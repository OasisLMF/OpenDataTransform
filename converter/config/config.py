import os
from functools import reduce
from itertools import chain
from typing import Any, Dict, Iterable, Tuple, TypeVar

import yaml

from converter.files.yaml import read_yaml


T = TypeVar("T")
ConfigSource = Dict[str, Any]


class NotFoundType:
    def get(self, *args, **kwargs):
        return self


NotFound = NotFoundType()


class Config:
    """
    Configuration class that loads the config file, environment,
    command line and overrides and merges them into a single map.
    """

    def __init__(
        self,
        argv: Dict[str, Any] = None,
        config_path: str = None,
        overrides: Dict[str, Any] = None,
        env: Dict[str, str] = None,
    ):
        self.path = os.path.abspath(config_path) if config_path else None
        self.config = self.merge_config_sources(
            *self.get_config_sources(
                config_path=config_path,
                env=env,
                argv=argv,
                overrides=overrides,
            )
        )

    def __eq__(self, other):
        return self.config in [other, getattr(other, "config", {})]

    def get_config_sources(
        self,
        config_path: str = None,
        env: Dict[str, str] = None,
        argv: Dict[str, Any] = None,
        overrides: ConfigSource = None,
    ) -> Iterable[ConfigSource]:
        """
        Returns all the provided config sources in order of increasing
        precedence, the order is:

        1. Config file
        2. Environment
        3. Command line
        4. Hard coded overrides

        :param config_path: The path to the config file
        :param env: The systems environment dict
        :param argv: Dict of config paths to values
        :param overrides: hard coded override values for the config

        :return: An iterable of normalised configs from the various sources
        """
        if config_path and os.path.exists(config_path):
            yield self.normalise_property_names(read_yaml(config_path))

        if env:
            yield self.normalise_property_names(self.process_env_options(env))

        if argv:
            yield self.normalise_property_names(self.process_cli_options(argv))

        if overrides:
            yield self.normalise_property_names(overrides)

    def _get_config_dict_from_path_value_pairs(
        self, paths_and_values, separator,
    ):
        conf = {}
        for path, value in paths_and_values:
            *parts, final = path.lower().split(separator)
            reduce(lambda c, part: c.setdefault(part, {}), parts, conf)[
                final
            ] = value

        return conf

    def process_cli_options(self, argv):
        return self._get_config_dict_from_path_value_pairs(argv.items(), ".")

    def process_env_options(self, env):
        env_search = "CONVERTER_".lower()

        return self._get_config_dict_from_path_value_pairs(
            (
                (
                    k.lower().replace(env_search, ""),
                    yaml.load(v, yaml.SafeLoader),
                )
                for k, v in env.items()
                if k.lower().startswith(env_search)
            ),
            "_",
        )

    def merge_config_sources(
        self,
        first: ConfigSource = None,
        second: ConfigSource = None,
        *others: ConfigSource,
    ) -> ConfigSource:
        """
        Merges any number of config sources the later sources taking precedence
        over the former.

        :param first: The first source
        :param second: The second source
        :param others: The other sources

        :return: The merged config source
        """
        first = first or {}
        second = second or {}

        merged = self.deep_merge_dictionary_items(first, second)

        if others:
            return self.merge_config_sources(merged, *others)

        return merged

    def deep_merge_dictionary_items(
        self, first: Any, second: Any
    ) -> ConfigSource:
        """
        Merges the 2 dictionary entries, the process is as follows:

        1. If the element from the first dictionary is not found use the
           element from the second independent from type
        2. If the element in the second dictionary is not a dictionary and has
           been found stop here and use it
        3. If the second element isn't found and the first has use the first
           value
        4. If both elements have been found then use the merge of the 2

        :param first: The first dict or the value from the first dict to try
            to merge
        :param second: The second dict or the value from the second dict to
            try to merge

        :return: The merged result
        """
        if first is NotFound or (
            second is not NotFound and not isinstance(second, dict)
        ):
            # if the first value was not found or the second value has been
            # found and is not a dictionary, use it
            return second
        elif first is not NotFound and second is NotFound:
            # else if we have no value from second and first is found use it
            return first
        else:
            # otherwise, continue merging deeper
            return {
                key: self.deep_merge_dictionary_items(
                    first.get(key, NotFound), second.get(key, NotFound)
                )
                for key in chain(first.keys(), second.keys())
            }

    def normalise_property_names(self, d: ConfigSource) -> ConfigSource:
        """
        Converts all names in all levels of the dictionary to lowercase

        :param d: The dictionary to normalise

        :return: The normalised dictionary
        """
        return dict(map(lambda kv: self.normalise_property(*kv), d.items()))

    def normalise_property(self, key: str, value: Any) -> Tuple[str, Any]:
        """
        Gets the normalised (lowercase) name with the normalised value.
        If the value is a dictionary it is normalised otherwise the value
        is returned unchanged.

        :param key: The key name for the entry
        :param value: The value for the entry

        :return: A 2-tuple of the normalised key and value of the entry
        """
        if isinstance(value, dict):
            return key.lower(), self.normalise_property_names(value)
        else:
            return key.lower(), value

    def get(self, path: str, fallback: Any = NotFound) -> Any:
        """
        Gets a property from the configuration from it's path in the config.
        The path should be dotted path into the config. For example, with the
        config::

             {
                "foo": {
                    "bar": "baz"
                }
             }

        The path `"foo.bar"` would return `"baz"` and the path `"foo"` would
        return `{"bar": "baz"}`.

        If the path isn't found in the config the `fallback` value is used if
        one is provided, if no fallback is provided a `KeyError` is raised.

        :param path: The path of the requested value into the config.
        :param fallback: The value to use if the path isn't found.

        :return: The found path ot fallback if provided
        """
        res = reduce(
            lambda conf, path_part: conf.get(path_part, NotFound),
            path.lower().split("."),
            self.config,
        )

        if res is not NotFound:
            return res

        if fallback is not NotFound:
            return fallback

        raise KeyError(path)

    def to_yaml(self):
        """
        Generates a yaml string  representation of the normalised config

        :return: The yaml representation
        """
        return yaml.safe_dump(self.config)

    def absolute_path(self, p):
        """
        Gets the absolute path relative to the config files directory.

        :param p: The path relative to the config file

        :return: The absolute path if both the config path and `p` are set,
            if `p` is `None`, `None` is returned. If the config path is `None`,
            `p` is returned without modification
        """
        if p is not None:
            return os.path.abspath(
                os.path.join(os.path.dirname(self.path or "."), p)
            )

        return p
