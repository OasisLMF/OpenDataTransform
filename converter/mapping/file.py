import glob
import logging
import os
from collections import OrderedDict
from functools import reduce
from itertools import chain, product
from typing import Any, Dict, Iterable, List, Reversible, Set, TypedDict, Union

from ..data import get_data_path, hide_system_data_path
from ..errors import ConverterError
from ..files.yaml import read_yaml
from ..transformers import run
from .base import (
    BaseMapping,
    ColumnConversion,
    ColumnConversions,
    DirectionalMapping,
    MappingFormat,
    MappingSpec,
    TransformationEntry,
    TransformationSet,
)


def get_logger():  # pragma: no cover
    return logging.getLogger(__name__)


RawTransformConfig = TypedDict(
    "RawTransformConfig", {"transformation": str, "when": str}, total=False
)


RawColumnConversionConfig = TypedDict(
    "RawColumnConversionConfig",
    {"type": str, "nullable": bool, "null_values": List},
    total=False,
)


RawDirectionalConfig = TypedDict(
    "RawDirectionalConfig",
    {
        "transform": Dict[str, List[RawTransformConfig]],
        "types": Dict[str, RawColumnConversionConfig],
        "null_values": List,
    },
    total=False,
)


RawMappingFormat = TypedDict(
    "RawMappingFormat",
    {
        "name": str,
        "version": str,
    },
)


RawMappingConfig = TypedDict(
    "RawMappingConfig",
    {
        "bases": List[str],
        "file_type": str,
        "input_format": MappingFormat,
        "output_format": MappingFormat,
        "forward": RawDirectionalConfig,
        "reverse": RawDirectionalConfig,
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


class FileMappingSpec(MappingSpec):
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
    :param forward: The configuration for changing from the input format to
        output format (the current config is merged with the parents)
    :param reverse: The configuration for changing from the output format to
        input format (the current config is merged with the parents)
    """

    def __init__(
        self,
        path: str,
        config: RawMappingConfig,
        all_found_configs: Dict[
            str, Union["FileMappingSpec", RawMappingConfig]
        ],
        search_paths: List[str],
        redact_logs=False,
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
        :param redact_logs: Flag whether logs should be redacted, in this case
            paths are removed from metadata to prevent potential leaking of
            storage keys
        """
        self.path = path
        self.raw_config = config

        # load all the bases
        self.bases: List[FileMappingSpec] = [
            self._load_base(base_name, all_found_configs, search_paths)
            for base_name in config.get("bases", [])
        ]

        # get the file_type from the bases if not set on the current config
        file_type: Union[str, None] = self._resolve_property(
            *(b.file_type for b in self.bases),
            config.get("file_type"),
        )

        if not file_type:
            raise InvalidMappingFile(
                "file_type not found in the config file or its bases",
                self.path,
            )

        # get the input format from the bases if not set on the current config
        raw_input_format: Union[
            RawMappingFormat, MappingFormat, None
        ] = self._resolve_property(
            *(b.input_format for b in self.bases),
            config.get("input_format"),
        )

        if not raw_input_format:
            raise InvalidMappingFile(
                "input_format not found in the config file or its bases",
                self.path,
            )
        elif not isinstance(raw_input_format, MappingFormat):
            input_format = MappingFormat(**raw_input_format)
        else:
            input_format = raw_input_format

        # get the output format from the bases if not set on the current config
        raw_output_format: Union[
            RawMappingFormat, MappingFormat, None
        ] = self._resolve_property(
            *(b.output_format for b in self.bases),
            config.get("output_format"),
        )

        if not raw_output_format:
            raise InvalidMappingFile(
                "output_format not found in the config file or its bases",
                self.path,
            )
        elif not isinstance(raw_output_format, MappingFormat):
            output_format = MappingFormat(**raw_output_format)
        else:
            output_format = raw_output_format

        # merge the transforms from all the parents and the current config
        forward_transform: TransformationSet = self._reduce_transforms(
            *(b.forward.transformation_set for b in self.bases if b.forward),
            config.get("forward", {}).get("transform", {}),
        )

        reverse_transform: TransformationSet = self._reduce_transforms(
            *(b.reverse.transformation_set for b in self.bases if b.reverse),
            config.get("reverse", {}).get("transform", {}),
        )

        # merge all null values from format specific entries
        forward_null_values = self._parse_null_values(
            *chain(
                config.get("forward", {}).get("null_values", set()),
                *(b.forward.null_values for b in self.bases if b.forward),
            )
        )

        reverse_null_values = self._parse_null_values(
            *chain(
                config.get("reverse", {}).get("null_values", set()),
                *(b.reverse.null_values for b in self.bases if b.reverse),
            )
        )

        # merge the column conversions from all the parents and the current
        # config
        forward_types = self._reduce_types(
            *(b.forward.types for b in self.bases if b.forward),
            self._process_raw_types(
                config.get("forward", {}).get("types", {}),
                forward_null_values,
            ),
        )

        reverse_types = self._reduce_types(
            *(b.reverse.types for b in self.bases if b.reverse),
            self._process_raw_types(
                config.get("reverse", {}).get("types", {}),
                reverse_null_values,
            ),
        )

        super().__init__(
            file_type,
            input_format,
            output_format,
            forward=DirectionalMapping(
                input_format=input_format,
                output_format=output_format,
                transformation_set=forward_transform,
                types=forward_types,
                null_values=forward_null_values,
            ),
            reverse=DirectionalMapping(
                input_format=output_format,
                output_format=input_format,
                transformation_set=reverse_transform,
                types=reverse_types,
                null_values=reverse_null_values,
            ),
            metadata={
                "path": (
                    hide_system_data_path(path) if not redact_logs else "***"
                ),
            },
            redact_logs=redact_logs,
        )

        all_found_configs[self.path] = self

    @classmethod
    def _parse_null_values(cls, *raw) -> Set:
        return {run({}, v) for v in raw}

    @classmethod
    def _process_raw_types(cls, types, null_values):
        return {
            k: {
                **v,
                "null_values": cls._parse_null_values(
                    *v.get("null_values", [])
                )
                or null_values,
            }
            for k, v in types.items()
        }

    @classmethod
    def _resolve_property(cls, *values: Union[None, Any]) -> Union[None, Any]:
        """
        Finds the first non None value

        :param values: An iterable of all the values to test

        :return: THe first found non None value
        """
        return next(reversed([v for v in values if v]), None)

    @classmethod
    def _reduce_transforms(
        cls,
        *transform_configs: Union[
            TransformationSet, Dict[str, List[RawTransformConfig]]
        ],
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

    @classmethod
    def _reduce_types(
        cls,
        *transform_types: Union[
            ColumnConversions, Dict[str, RawColumnConversionConfig]
        ],
    ):
        return reduce(
            lambda types, current: {
                **types,
                **{
                    k: (
                        ColumnConversion(**v)  # type: ignore
                        if isinstance(v, dict)
                        else v
                    )
                    for k, v in current.items()
                },
            },
            transform_types,
            {},
        )

    def _load_base(
        self,
        base_name: str,
        all_found_configs: Dict[
            str, Union["FileMappingSpec", RawMappingConfig]
        ],
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
                f"Could not find base mapping file ({base_name})",
                self.path,
            )

        if not isinstance(config, FileMappingSpec):
            # if the found config is not yet hydrated store a hydrated version
            config = FileMappingSpec(
                config_path, config, all_found_configs, search_paths
            )
            all_found_configs[config_path] = config

        return config


class FileMapping(BaseMapping):
    """
    A mapping of all file mapping on the system in the search directories.

    :param config: The global config for the system
    :param search_paths: All the paths in the system to check for configs
    """

    def __init__(
        self,
        config,
        file_type: str,
        search_paths: List[str] = None,
        standard_search_path: str = get_data_path("mappings"),
        search_working_dir=True,
        file_override: str = None,
        **options,
    ):
        """
        :param search_paths: All the paths in the system to check for
            mapping configs. If set the path of the conversion config is
            prepended to this list.
        :param standard_search_path: The path to the standard library of
            mappings
        :param file_override: Specifies a specific file to use for the
            transformation rather interrogating teh mapping graph
        :param options: Ignored options
        """
        if config.path:
            search_paths = [os.path.dirname(config.path)] + (
                search_paths or []
            )

        super().__init__(
            config,
            file_type,
            search_paths=search_paths,
            standard_search_path=standard_search_path,
            search_working_dir=search_working_dir,
            **options,
        )

        self._raw_configs: Union[None, Dict[str, RawMappingConfig]] = None
        self._hydrated_configs: Union[None, Dict[str, FileMappingSpec]] = None
        self.search_paths = [
            *(os.path.abspath(p) for p in (search_paths or [])),
            os.path.abspath(standard_search_path),
        ]
        self.file_override = file_override

        if search_working_dir:
            self.search_paths.insert(0, os.path.abspath("."))

    def get_logger(self):
        return self.logger or get_logger()

    def _load_raw_configs(self) -> Dict[str, RawMappingConfig]:
        """
        Loads all the mappings in the search paths

        :return: The raw mapping configs keyed by their absolute paths.
        """
        if self.file_override:
            # for simplicity, if a file is specified we will still use
            # the normal graph mechanism but with only 1 candidate path
            candidate_paths: Iterable[str] = [self.file_override]
        else:
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
        cls,
        search_path: str,
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
                        "file_type",
                        "input_format",
                        "output_format",
                        "forward",
                        "reverse",
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
                yield k, FileMappingSpec(
                    k,
                    v,
                    self.raw_configs,
                    self.search_paths,
                    redact_logs=self.redact_logs,
                )
            except InvalidMappingFile as e:
                self.get_logger().warning(str(e))

    @property
    def mapping_specs(self) -> Reversible[FileMappingSpec]:
        """
        Gets all the hydrated mapping configs keyed by their absolute paths.
        If they have not already been loaded they are loaded here.
        """
        if self._hydrated_configs is None:
            self._hydrated_configs = OrderedDict(self._hydrate_raw_configs())

        return self._hydrated_configs.values()
