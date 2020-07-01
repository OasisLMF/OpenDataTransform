import glob
import logging
import os
from collections import OrderedDict
from functools import reduce
from itertools import chain, product
from typing import Dict, Iterable, List, TypedDict, Union

import networkx as nx

from ..errors import ConverterError
from ..files import read_yaml
from .base import BaseMapping, TransformationEntry, TransformationSet


logger = logging.getLogger(__name__)


RawTransformConfig = TypedDict(
    "RawTransformConfig", {"transformation": str, "when": str}, total=False
)


RawMappingConfig = TypedDict(
    "RawMappingConfig",
    {
        "bases": List[str],
        "input_format": str,
        "output_format": str,
        "forward_transform": Dict[str, List[RawTransformConfig]],
        "reverse_transform": Dict[str, List[RawTransformConfig]],
    },
    total=False,
)


class InvalidMappingFile(ConverterError):
    """
    Error raised when a mapping file fails validation

    :param reason: String representing the reason for the failure.
    :param path: Path to the failing file.
    """

    def __init__(self, reason: str, path: str):
        self.path: str = path
        self.reason: str = reason

        super().__init__(f"{path}: {reason}.")


class NoConversionPathError(ConverterError):
    """
    Error raised there is no valid format map between 2 formats

    :param input_format: The start path in the requested path.
    :param output_format: The end path in the requested path.
    """

    def __init__(self, input_format, output_format):
        self.input_format = input_format
        self.output_format = output_format

        super().__init__(
            f"No conversion path from {input_format} to {output_format}."
        )


class MappingFile:
    """
    A file representing a conversion mapping between 2 formats.

    This class will also load any base configs represented by the config.

    The final result is added to `all_found_configs` so that further mappings
    can use this to lookup parents rather than processing the raw config again.

    :param path: Absolute path to the mapping file.
    :param raw_config: The raw config data from the mapping file.
    :param bases: A list of `MappingFile` objects to use as the base files
    :param input_format: The input format resolved from the parent and current
        configs.
    :param output_format: The output format resolved from the parent and
        current configs.
    :param forward_transform: The transforms from changing from the input
        format to output format (the current config is merged with the parents)
    :param reverse_transform: The transforms from changing from the ouptut
        format to input format (the current config is merged with the parents)
    """

    def __init__(
        self,
        path: str,
        config: RawMappingConfig,
        all_found_configs: Dict[str, Union["MappingFile", RawMappingConfig]],
        search_paths: List[str],
    ):
        """
        :param path: Absolute path to the mapping file.
        :param config: The raw config for read from the mapping file.
        :param all_found_configs: A dictionary mapping absolute paths to raw
            configs and hydrated `MappingFile` objects.
        :param search_paths: The paths used to search for parents (these files
            aren't read here but the search paths are used to find parents
            in `all_found_configs`). Parents in the former search paths will
            be used in preference to the later.
        """
        self.path = path
        self.raw_config = config

        # load all the bases
        self.bases: List[MappingFile] = [
            self._load_base(base_name, all_found_configs, search_paths)
            for base_name in config.get("bases", [])
        ]

        # get the input format from the bases if not set on the current config
        self.input_format: Union[str, None] = self._resolve_property(
            *(b.input_format for b in self.bases), config.get("input_format"),
        )

        if not self.input_format:
            raise InvalidMappingFile(
                "input_format not found in the config file or its bases",
                self.path,
            )

        # get the output format from the bases if not set on the current config
        self.output_format: Union[str, None] = self._resolve_property(
            *(b.output_format for b in self.bases),
            config.get("output_format"),
        )

        if not self.output_format:
            raise InvalidMappingFile(
                "output_format not found in the config file or its bases",
                self.path,
            )

        # merge the transforms from all the parents and the current config
        self.forward_transform: TransformationSet = self._reduce_transforms(
            *(b.forward_transform for b in self.bases),
            config.get("forward_transform", {}),
        )

        self.reverse_transform: TransformationSet = self._reduce_transforms(
            *(b.reverse_transform for b in self.bases),
            config.get("reverse_transform", {}),
        )

        all_found_configs[self.path] = self

    @staticmethod
    def _resolve_property(*values: Union[None, str]) -> Union[None, str]:
        """
        Finds the first non None value

        :param values: An iterable of all the values to test

        :return: THe first found non None value
        """
        return next(reversed([v for v in values if v]), None)

    @staticmethod
    def _reduce_transforms(
        *transform_configs: Union[TransformationSet, Dict]
    ) -> TransformationSet:
        """
        Merges the current configs transforms with all the parents.

        :param transform_configs: An iterable containing the transforms to
            merge

        :return: The merged transformation set
        """
        return reduce(
            lambda transforms, current: {
                **transforms,
                **{
                    k: [
                        TransformationEntry(**t) if isinstance(t, dict) else t
                        for t in v
                    ]
                    for k, v in current.items()
                },
            },
            transform_configs,
            {},
        )

    def _load_base(
        self,
        base_name: str,
        all_found_configs: Dict[str, Union["MappingFile", RawMappingConfig]],
        search_paths: List[str],
    ):
        """
        Processes the base hydrating it if it has not yet been hydrated.

        :param base_name:
        :param all_found_configs:
        :param search_paths:

        :return: The hydrated `MappingFile` object for the base
        """
        if os.path.splitext(base_name)[1] in [".yml", ".yaml"]:
            # if the base has a yaml extension treat it as an relative
            # path so we dont need to lookup the parents
            config_path = os.path.join(os.path.dirname(self.path), base_name)
            config = all_found_configs.get(config_path)
        else:
            # if we aren't dealing with a relative path find the config in
            # the search paths

            # get all paths matching the name in each search path for
            # yml and yaml extansions
            possible_paths = map(
                lambda tpl: os.path.join(tpl[0], f"{base_name}.{tpl[1]}"),
                product(search_paths, ("yml", "yaml")),
            )

            # get the config path and config for the first match
            config_path, config = next(
                (
                    (p, all_found_configs.get(p))
                    for p in possible_paths
                    if p in all_found_configs
                ),
                ("", None),
            )

        if not config:
            raise InvalidMappingFile(
                f"Could not find base mapping file ({base_name})", self.path,
            )

        if not isinstance(config, MappingFile):
            # if the found config is not yet hydrated store a hydrated version
            config = MappingFile(
                config_path, config, all_found_configs, search_paths
            )
            all_found_configs[config_path] = config

        return config

    @property
    def can_run_forwards(self):
        """
        Flag whether the mapping file can be applied forwards.

        :return: True is the mapping can be applied forwards, False otherwise
        """
        return len(self.forward_transform) > 0

    @property
    def can_run_in_reverse(self):
        """
        Flag whether the mapping file can be applied in reverse.

        :return: True is the mapping can be applied in reverse, False otherwise
        """
        return len(self.reverse_transform) > 0


class FileMapping(BaseMapping):
    """
    A mapping of all file mapping on the system in the search directories.

    :param search_paths: All the paths in the system to check for configs
    """

    def __init__(
        self,
        search_paths: List[str] = None,
        standard_search_path: str = os.path.join(
            os.path.dirname(__file__), "..", "_data", "mappings"
        ),
        **options,
    ):
        """
        :param search_paths: All the paths in the system to check for configs
        :param standard_search_path: The path to the standard library of
            mappings
        :param options: Ignored options
        """
        super().__init__(
            search_paths=search_paths,
            standard_search_path=standard_search_path,
            **options,
        )

        self._raw_configs: Union[None, Dict[str, RawMappingConfig]] = None
        self._hydrated_configs: Union[None, Dict[str, MappingFile]] = None
        self.search_paths = [
            os.path.abspath("."),
            *(os.path.abspath(p) for p in (search_paths or [])),
            os.path.abspath(standard_search_path),
        ]

        self._mapping_graph = None

    def _load_raw_configs(self) -> Dict[str, RawMappingConfig]:
        """
        Loads all the mappings in the search paths

        :return: The raw mapping configs keyed by their absolute paths.
        """
        candidate_paths = chain(
            *(
                self._get_candidate_paths_from_search_path(p)
                for p in self.search_paths
            )
        )

        path_wth_config = ((p, self._load_yaml(p)) for p in candidate_paths)

        # exclude any configs that dont pass the basic validation
        return OrderedDict(
            (p, config)
            for p, config in path_wth_config
            if self._validate_raw_config(config)
        )

    @property
    def raw_configs(self) -> Dict[str, RawMappingConfig]:
        """
        Gets the raw configs from teh system. If they have not yet been loaded
        they are loaded here.
        """
        if self._raw_configs is None:
            self._raw_configs = self._load_raw_configs()

        return self._raw_configs

    @classmethod
    def _load_yaml(cls, path) -> RawMappingConfig:
        """
        Gets the yaml content from a file.

        :param path: Path to the yaml file.

        :return: The parsed yaml content
        """
        return read_yaml(path)

    @classmethod
    def _get_candidate_paths_from_search_path(
        cls, search_path: str,
    ) -> Iterable[str]:
        """
        Gets all the possible yaml files from the search path.

        :param search_path:
        :return:
        """
        yield from glob.glob(
            os.path.abspath(os.path.join(search_path, "*.yml"))
        )
        yield from glob.glob(
            os.path.abspath(os.path.join(search_path, "*.yaml"))
        )

    @classmethod
    def _conf_has_unexpected_fields(cls, conf: RawMappingConfig) -> bool:
        """
        Checks if the config has any unexpected fields

        :param conf: The conf to check

        :return: True if there are any extra fields or if its not a dict,
            otherwise False
        """
        return (
            len(
                conf.keys()
                & (
                    conf.keys()
                    ^ {
                        "bases",
                        "input_format",
                        "output_format",
                        "forward_transform",
                        "reverse_transform",
                    }
                )
            )
            != 0
        )

    @classmethod
    def _validate_raw_config(cls, raw_config: RawMappingConfig) -> bool:
        """
        Performs a small validation to make sure the candidate config is a
        dictionary and doesn't have any unexpected keys.

        :param raw_config: The config to check

        :return: True if the config is valid, otherwise False
        """
        return isinstance(
            raw_config, dict
        ) and not cls._conf_has_unexpected_fields(raw_config)

    def _hydrate_raw_configs(self):
        """
        Converts all raw configs to `MappingFile` objects.

        :return: The hydrated configs keyed by their absolute paths.
        """
        for k, v in self.raw_configs.items():
            try:
                yield k, MappingFile(k, v, self.raw_configs, self.search_paths)
            except InvalidMappingFile as e:
                logger.warning(str(e))

    @property
    def mapping_configs(self):
        """
        Gets all the hydrated mapping configs keyed by their absolute paths.
        If they have not already been loaded they are loaded here.
        """
        if self._hydrated_configs is None:
            self._hydrated_configs = OrderedDict(self._hydrate_raw_configs())

        return self._hydrated_configs

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
        for mapping in reversed(self.mapping_configs.values()):
            if mapping.can_run_forwards:
                g.add_edge(
                    mapping.input_format,
                    mapping.output_format,
                    transform_set=mapping.forward_transform,
                    filename=mapping.path,
                )

            if mapping.can_run_in_reverse:
                g.add_edge(
                    mapping.output_format,
                    mapping.input_format,
                    transform_set=mapping.reverse_transform,
                    filename=mapping.path,
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

    def get_transformations(self) -> List[TransformationSet]:
        """
        Gets a full transformation set for the provided input and output paths.

        :return: The transformation set for the conversion path.
        """
        try:
            path = nx.shortest_path(
                self.mapping_graph, self.input_format, self.output_format,
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            raise NoConversionPathError(self.input_format, self.output_format)

        logger.info(f"Path found {' -> '.join(path)}")
        edges = map(
            lambda in_out: self.mapping_graph[in_out[0]][in_out[1]],
            zip(path[:-1], path[1:]),
        )

        return [edge["transform_set"] for edge in edges]
