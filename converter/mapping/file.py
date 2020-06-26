import glob
import logging
import os
from functools import reduce
from itertools import chain, product
from typing import Any, Dict, List

import yaml

from .base import BaseMapping

logger = logging.getLogger(__name__)


def _load_yaml(path):
    with open(path) as f:
        return yaml.load(f)


def _get_candidate_paths_from_search_path(search_path):
    yield from glob.glob(os.path.abspath(os.path.join(search_path, "*.yml")))
    yield from glob.glob(os.path.abspath(os.path.join(search_path, "*.yaml")))


def _validate_raw_config(raw_config: Dict) -> bool:
    """
    Performs a small validation to make sure the candidate config is a
    dictionary and deosn't have any unexpected keys.

    :param raw_config: The config to check
    :return:
    """
    return (
        # make sure we haven't loaded a yaml list
        isinstance(raw_config, dict) and
        # make sure the config doesnt have any unexpected keys
        len(raw_config.keys() ^ {
            "bases", "input_format", "output_format",
            "forward_transform", "reverse_transform",
        }) == 0
    )


def _load_raw_configs(search_paths):
    candidate_paths = chain(*(
        _get_candidate_paths_from_search_path(p) for p in search_paths
    ))

    path_wth_config = ((p, _load_yaml(p)) for p in candidate_paths)

    # exclude any configs that dont pass the basic validation
    return {
        p: config
        for p, config in path_wth_config
        if _validate_raw_config(config)
    }


def _hydreate_configs(raw_configs, search_paths):
    for k, v in raw_configs:
        try:
            yield k, MappingFile(k, v, raw_configs, search_paths)
        except InvalidMappingFile as e:
            logger.warning(e)


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
            for base_name in config.get('bases', [])
        ]

        # get the input format from the bases if not set on the current config
        self.input_format = self._resolve_property(
            config.get('input_format'), *(b.input_format for b in self.bases)
        )

        if not self.input_format:
            raise InvalidMappingFile(
                "input_format not found in the config file or its bases",
                self.path,
            )

        # get the output format from the bases if not set on the current config
        self.output_format = self._resolve_property(
            config.get('output_format'), *(b.output_format for b in self.bases)
        )

        if not self.output_format:
            raise InvalidMappingFile(
                "output_format not found in the config file or its bases",
                self.path,
            )

        # merge the transforms from all the parents and the current config
        self.forward_transform = self._reduce_transforms(
            config.get('forward_transform', {}),
            *(b.forward_transform for b in self.bases),
        )

        self.reverse_transform = self._reduce_transforms(
            config.get('reverse_transform', {}),
            *(b.reverse_transform for b in self.bases),
        )


    def _resolve_property(self, *values):
        return next(reversed([v for v in values if v]), None)

    def _reduce_transforms(self, *transform_configs):
        return reduce(
            lambda transforms, current: {**transforms, **current},
            reversed(transform_configs),
            {},
        )

    def _load_base(self, base_name, all_found_configs, search_paths):
        if os.path.splitext(base_name)[1] in ["yml", "yaml"]:
            # if the base has a yaml extension treat it as an relative
            # path so we dont need to lookup the parents
            config_path = os.path.join(self.path, base_name)
            config = all_found_configs.get(config_path)
        else:
            # if we aren't dealing with a relative path find the config in
            # the search paths

            # get all paths matching the name in each search path for
            # yml and yaml extansions
            possible_paths = map(
                lambda tpl: os.path.join(tpl[0], f"{base_name}.{tpl[1]}"),
                product(search_paths, ("yml", "yaml"))
            )

            # get the config path and config for the first match
            config_path, config = next(
                ((p, all_found_configs.get(p)) for p in possible_paths),
                None
            )

        if not config:
            raise InvalidMappingFile(
                f"Could not find base mapping file ({base_name})",
                self.path,
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
    def __init__(self, **options):
        super().__init__(**options)

        self.search_paths = [
            *options.get('search_paths', []),
            os.path.join(os.path.dirname(__file__), '..', '_data', 'mappings'),
        ]

        self._raw_configs = _load_raw_configs(self.search_paths)
        self._mapping_configs = dict(
            _hydreate_configs(self._raw_configs, self.search_paths)
        )

    def get_transformations(self) -> Dict[str, List[Any]]:
        return {}
