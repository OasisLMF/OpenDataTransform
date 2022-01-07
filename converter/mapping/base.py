import logging
from typing import Dict, List, NamedTuple, Reversible, Set, Union

import networkx as nx
from lark import Tree

from converter.config import Config
from converter.config.errors import ConfigurationError
from converter.mapping.errors import NoConversionPathError
from converter.transformers.transform import parse


def get_logger():
    return logging.getLogger(__name__)


class TransformationEntry:
    def __init__(
        self,
        transformation: str,
        transformation_tree: Union[Tree, None] = None,
        when: str = "True",
        when_tree: Union[Tree, None] = None,
    ):
        self.transformation = transformation
        self.transformation_tree = transformation_tree
        self.when = when
        self.when_tree = when_tree

    def __eq__(self, other):
        return (
            self.transformation == other.transformation
            and self.when == other.when
        )

    def parse(self):
        self.when_tree = parse(self.when)
        self.transformation_tree = parse(self.transformation)


TransformationSet = Dict[str, List[TransformationEntry]]


class ColumnConversion(NamedTuple):
    type: str
    nullable: bool = True
    null_values: Set = set()


ColumnConversions = Dict[str, ColumnConversion]


class DirectionalMapping(NamedTuple):
    input_format: str
    output_format: str
    transformation_set: TransformationSet
    types: Dict[str, ColumnConversion] = dict()
    null_values: Set = set()


class MappingSpec:
    """
    Class holding information about a given mapping
    """

    def __init__(
        self,
        input_format,
        output_format,
        forward: DirectionalMapping = None,
        reverse: DirectionalMapping = None,
    ):
        self.input_format = input_format
        self.output_format = output_format
        self.forward = forward
        self.reverse = reverse

    @property
    def can_run_forwards(self):
        """
        Flag whether the mapping file can be applied forwards.

        :return: True is the mapping can be applied forwards, False otherwise
        """
        return (
            self.forward is not None
            and len(self.forward.transformation_set) > 0
        )

    @property
    def can_run_in_reverse(self):
        """
        Flag whether the mapping file can be applied in reverse.

        :return: True is the mapping can be applied in reverse, False otherwise
        """
        return (
            self.reverse is not None
            and len(self.reverse.transformation_set) > 0
        )


class BaseMapping:
    """
    Class describing the mapping from the input to the
    output formats.

    :param config: The global config for the system
    :param input_format: The start of the conversion path
    :param output_format: The end of the conversion path
    """

    def __init__(
        self,
        config: Config,
        input_format: str = None,
        output_format: str = None,
        **options,
    ):
        self._mapping_graph = None

        self.config = config
        self._options = {
            "input_format": input_format,
            "output_format": output_format,
            **options,
        }

        self.input_format = input_format
        if not self.input_format:
            raise ConfigurationError("input_format not set for the mapping.")

        self.output_format = output_format
        if not self.output_format:
            raise ConfigurationError("output_format not set for the mapping.")

    @property
    def mapping_specs(self) -> Reversible[MappingSpec]:
        """
        Returns a list of ``MappingSpec`` objects described by the mapping
        """
        raise NotImplementedError()

    def _build_mapping_graph(self) -> nx.DiGraph:
        """
        Creates a networkx graph to represent the relationships between
        formats in the system.

        :return: The built graph
        """
        g = nx.DiGraph()

        # the mapping config is in order from first search path to last
        # if we build it in reverse order we will store the most preferable
        # mapping on each edge
        for mapping in reversed(self.mapping_specs):
            if mapping.can_run_forwards:
                g.add_edge(
                    mapping.input_format,
                    mapping.output_format,
                    transform=mapping.forward,
                )

            if mapping.can_run_in_reverse:
                g.add_edge(
                    mapping.output_format,
                    mapping.input_format,
                    transform=mapping.reverse,
                )

        return g

    @property
    def mapping_graph(self) -> nx.DiGraph:
        """
        Creates the graph to represent the relationships between formats in
        the system. It it has not already been generated it is generated here.
        """
        if self._mapping_graph is None:
            self._mapping_graph = self._build_mapping_graph()

        return self._mapping_graph

    def get_transformations(self) -> List[DirectionalMapping]:
        """
        Gets a column transformations and full transformation set for the
        provided input and output paths.

        :return: The mappings along the conversion path.
        """
        try:
            path = nx.shortest_path(
                self.mapping_graph,
                self.input_format,
                self.output_format,
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            raise NoConversionPathError(self.input_format, self.output_format)

        get_logger().info(f"Path found {' -> '.join(path)}")
        edges = map(
            lambda in_out: self.mapping_graph[in_out[0]][in_out[1]],
            zip(path[:-1], path[1:]),
        )

        # parse the trees of the path so that is doesnt need
        # to be done for every row
        transformations = [edge["transform"] for edge in edges]
        for mapping in transformations:
            for transform in mapping.transformation_set.values():
                for case in transform:
                    case.parse()

        return transformations
