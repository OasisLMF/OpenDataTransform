from functools import reduce
from itertools import chain
from typing import Any, Dict, Iterable, Tuple, TypeVar

import yaml


T = TypeVar("T")
ConfigSource = Dict[str, Any]


class NotFoundType:
    pass


NotFound = NotFoundType()


class Config:
    """
    Configuration class that loads the config file, environment (TODO),
    command line (TODO) and overrides and merges them into a single map.
    """
    def __init__(
        self, config_path: str = None, overrides: Dict[str, Any] = None
    ):
        self.config = self.merge_config_sources(
            *self.get_config_sources(config_path, overrides)
        )

    def get_config_sources(
        self, config_path: str = None, overrides: ConfigSource = None,
    ) -> Iterable[ConfigSource]:
        """
        Returns all the provided config sources in order of increasing
        precedence, the order is:

        1. Config file
        2. Environment (TODO)
        3. Command line (TODO)
        4. Hard coded overrides

        :param config_path: The path to the config file
        :param overrides: hard coded override values for the config

        :return: An iterable of normalised configs from the various sources
        """
        if config_path:
            with open(config_path) as f:
                yield self.normalise_property_names(yaml.load(f))

        if overrides:
            yield self.normalise_property_names(overrides)

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
