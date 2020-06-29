import glob
import logging
import os
from functools import reduce
from itertools import chain, product
from typing import Any, Dict, List

import yaml

from .base import BaseMapping


logger = logging.getLogger(__name__)


class InvalidMappingFile(Exception):
    def __init__(self, reason, path):
        self.path = path
        self.reason = reason

        super().__init__(f"{path}: {reason}")


class MappingFile:
    def __init__(self, path, config, all_found_configs, search_paths):
        self.path = path

        # load all the bases
        self.bases: List[MappingFile] = [
            self._load_base(base_name, all_found_configs, search_paths)
            for base_name in config.get("bases", [])
        ]

        # get the input format from the bases if not set on the current config
        self.input_format = self._resolve_property(
            *(b.input_format for b in self.bases), config.get("input_format"),
        )

        if not self.input_format:
            raise InvalidMappingFile(
                "input_format not found in the config file or its bases",
                self.path,
            )

        # get the output format from the bases if not set on the current config
        self.output_format = self._resolve_property(
            *(b.output_format for b in self.bases),
            config.get("output_format"),
        )

        if not self.output_format:
            raise InvalidMappingFile(
                "output_format not found in the config file or its bases",
                self.path,
            )

        # merge the transforms from all the parents and the current config
        self.forward_transform = self._reduce_transforms(
            *(b.forward_transform for b in self.bases),
            config.get("forward_transform", {}),
        )

        self.reverse_transform = self._reduce_transforms(
            *(b.reverse_transform for b in self.bases),
            config.get("reverse_transform", {}),
        )

        all_found_configs[self.path] = self

    def _resolve_property(self, *values):
        return next(reversed([v for v in values if v]), None)

    def _reduce_transforms(self, *transform_configs):
        return reduce(
            lambda transforms, current: {**transforms, **current},
            transform_configs,
            {},
        )

    def _load_base(self, base_name, all_found_configs, search_paths):
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
                (None, None),
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
            all_found_configs[config] = config

        return config

    @property
    def can_run_forwards(self):
        return len(self.forward_transform) > 0

    @property
    def can_run_in_reverse(self):
        return len(self.reverse_transform) > 0


class FileMapping(BaseMapping):
    def __init__(
        self,
        search_paths=None,
        standard_search_path=os.path.join(
            os.path.dirname(__file__), "..", "_data", "mappings"
        ),
        **options,
    ):
        super().__init__(
            search_paths=search_paths,
            standard_search_path=standard_search_path,
            **options,
        )

        self._raw_configs = None
        self._hydrated_configs = None
        self.search_paths = [
            os.path.abspath("."),
            *(os.path.abspath(p) for p in (search_paths or [])),
            os.path.abspath(standard_search_path),
        ]

    def _load_raw_configs(self):
        candidate_paths = chain(
            *(
                self._get_candidate_paths_from_search_path(p)
                for p in self.search_paths
            )
        )

        path_wth_config = ((p, self._load_yaml(p)) for p in candidate_paths)

        # exclude any configs that dont pass the basic validation
        return {
            p: config
            for p, config in path_wth_config
            if self._validate_raw_config(config)
        }

    @property
    def raw_configs(self):
        if self._raw_configs is None:
            self._raw_configs = self._load_raw_configs()

        return self._raw_configs

    @classmethod
    def _load_yaml(cls, path):
        with open(path) as f:
            return yaml.load(f)

    @classmethod
    def _get_candidate_paths_from_search_path(cls, search_path):
        yield from glob.glob(
            os.path.abspath(os.path.join(search_path, "*.yml"))
        )
        yield from glob.glob(
            os.path.abspath(os.path.join(search_path, "*.yaml"))
        )

    @classmethod
    def _conf_has_unexpected_fields(cls, conf):
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
    def _validate_raw_config(cls, raw_config: Dict) -> bool:
        """
        Performs a small validation to make sure the candidate config is a
        dictionary and deosn't have any unexpected keys.

        :param raw_config: The config to check
        :return:
        """
        return isinstance(
            raw_config, dict
        ) and not cls._conf_has_unexpected_fields(raw_config)

    def _hydrate_raw_configs(self):
        for k, v in self.raw_configs.items():
            try:
                yield k, MappingFile(k, v, self.raw_configs, self.search_paths)
            except InvalidMappingFile as e:
                logger.warning(str(e))

    @property
    def mapping_configs(self):
        if self._hydrated_configs is None:
            self._hydrated_configs = dict(self._hydrate_raw_configs())

        return self._hydrated_configs

    def get_transformations(self) -> Dict[str, List[Any]]:
        return {}
