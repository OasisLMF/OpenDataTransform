import os
import re
from functools import reduce
from itertools import chain
from typing import Any, Dict, Iterable, List, Tuple, TypeVar, Union

import yaml

from converter.config.errors import ConfigurationError
from converter.files.yaml import read_yaml


T = TypeVar("T")
ConfigSource = Dict[str, Any]


class NotFoundType:
    def get(self, *args, **kwargs):
        return self


NotFound = NotFoundType()


def deep_merge_dictionary_items(
    first: Union[Dict, "Config"], second: Union[Dict, "Config"]
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
    if isinstance(first, Config):
        first = first.config

    if isinstance(second, Config):
        second = second.config

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
            key: deep_merge_dictionary_items(
                first.get(key, NotFound), second.get(key, NotFound)
            )
            for key in chain(first.keys(), second.keys())
        }


def get_json_path(
    config: Dict[str, Any], path: str, fallback: Any = NotFound
) -> Any:
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
        config,
    )

    if res is not NotFound:
        return res

    if fallback is not NotFound:
        return fallback

    raise KeyError(path)


class Config:
    """
    Configuration class that loads the config file, environment,
    command line and overrides and merges them into a single map.
    """

    TEMPLATE_TRANSFORMATION_PATH = "template_transformation"
    TRANSFORMATIONS_PATH = "transformations"
    ACC_TRANSFORMATION_LABEL = "acc"
    ACC_TRANSFORMATION_PATH = (
        f"{TRANSFORMATIONS_PATH}.{ACC_TRANSFORMATION_LABEL}"
    )
    LOC_TRANSFORMATION_LABEL = "loc"
    LOC_TRANSFORMATION_PATH = (
        f"{TRANSFORMATIONS_PATH}.{LOC_TRANSFORMATION_LABEL}"
    )
    RI_TRANSFORMATION_LABEL = "ri"
    RI_TRANSFORMATION_PATH = (
        f"{TRANSFORMATIONS_PATH}.{RI_TRANSFORMATION_LABEL}"
    )

    TRANSFORMATION_PATH_SUB = re.compile(r"^transformations\.[^.]+")

    def __init__(
        self,
        argv: Dict[str, Any] = None,
        config_path: str = None,
        overrides: Dict[str, Any] = None,
        env: Dict[str, str] = None,
    ):
        self.path = (
            os.path.abspath(config_path)
            if config_path and os.path.exists(config_path)
            else None
        )
        self.argv = argv
        self.env = env
        self.overrides = overrides
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

    def __bool__(self):
        return bool(self.config)

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
        self,
        paths_and_values,
        separator,
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

    @classmethod
    def validate(cls, config_path: str):
        """
        Basic validation check of the config file.
        """
        config = read_yaml(config_path)
        # If transformations key not in yaml file flag as invalid.
        if "transformations" not in config:
            raise ConfigurationError(
                "Invalid config file - transformation key required"
            )

    @classmethod
    def merge_config_sources(
        cls,
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

        merged = deep_merge_dictionary_items(first, second)

        if others:
            return cls.merge_config_sources(merged, *others)

        return merged

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
        return get_json_path(self.config, path, fallback=fallback)

    def get_template_resolved_value(self, path: str, fallback: Any = NotFound):
        """
        Gets the value for a given path reverting to the transformation
        template if the value is not found.

        :param path: The path of the requested value into the config.
        :param fallback: The value to use if the path isn't found.

        :return: The found path ot fallback if provided
        """

        try:
            return self.get(path)
        except KeyError:
            pass

        try:
            template_property_path = self.TRANSFORMATION_PATH_SUB.sub(
                self.TEMPLATE_TRANSFORMATION_PATH,
                path,
            )
            return self.get(template_property_path)
        except KeyError:
            pass

        if fallback is not NotFound:
            return fallback

        raise KeyError(path)

    def set(self, path: str, value: Any):
        """
        Sets a property in the configuration by it's path in the config.
        The path should be dotted path into the config. For example, setting
        the path `"foo.bar"` to `"baz"` the following config will be created::

             {
                "foo": {
                    "bar": "baz"
                }
             }

        :param path: The path of the value to set.
        :param value: The value to set.
        """
        block = self.config

        path_parts = path.lower().split(".")
        for path_part in path_parts[:-1]:
            block = block.setdefault(path_part, {})

        block[path_parts[-1]] = value

    def delete(self, path):
        """
        Removes a specific path from the config

        :param path: The path to remove.
        """
        block = self.config

        path_parts = path.lower().split(".")
        for path_part in path_parts[:-1]:
            if path_part not in block:
                return
            block = block[path_part]

        if path_parts[-1] in block:
            del block[path_parts[-1]]

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

    def save(self, new_filename=None):
        """
        Writes the configuration to a yaml file.

        :param new_filename: The filename to use. If not set the current
            filename in the configuration is used.
        """
        with open(new_filename or self.path, "w") as f:
            f.write(self.to_yaml())

    def keys(self):
        """
        Gets an iterable keys.
        """
        return self.config.keys()

    def items(self):
        """
        Gets an iterable of (key, value) tuples.
        """
        return self.config.items()

    def get_transformation_configs(self) -> List["TransformationConfig"]:
        """
        Generates all the configs for running specific transformations
        resolved with the template transformation

        :return: A list of transformation configs
        """
        return [
            TransformationConfig(self, file_type)
            for file_type in self.get(
                self.TRANSFORMATIONS_PATH, fallback={}
            ).keys()
        ]

    @property
    def has_template(self) -> bool:
        """
        Checks if the config has a template transformation
        """
        return self.TEMPLATE_TRANSFORMATION_PATH in self

    @property
    def has_acc(self):
        """
        Checks if the config has an account transformation
        """
        return self.ACC_TRANSFORMATION_PATH in self

    @property
    def has_loc(self):
        """
        Checks if the config has a location transformation
        """
        return self.LOC_TRANSFORMATION_PATH in self

    @property
    def has_ri(self):
        """
        Checks if the config has a reinsurance transformation
        """
        return self.RI_TRANSFORMATION_PATH in self

    def uses_template_value(self, property_path):
        """
        Checks if a given path uses the value from the template transformation.
        """
        template_property_path = self.TRANSFORMATION_PATH_SUB.sub(
            self.TEMPLATE_TRANSFORMATION_PATH,
            property_path,
        )
        try:
            template_value = self.get(template_property_path)
        except KeyError:
            # if the property isn't in the template then we cant be
            # using the template value
            return False

        try:
            config_value = self.get(property_path)
        except KeyError:
            # if the property is in the template but not in the config
            # we must be using the template path
            return True

        # if it is set in both specify we are using the template if
        # the 2 values are the same
        return template_value == config_value

    def __contains__(self, item):
        try:
            self.get(item)
            return True
        except KeyError:
            return False


class TransformationConfig:
    def __init__(self, config: Config, file_type: str):
        self.root_config = config
        self.file_type = file_type

        # merge the template transformation with the overrides
        self.config = deep_merge_dictionary_items(
            self.root_config.get(
                self.root_config.TEMPLATE_TRANSFORMATION_PATH, fallback={}
            ),
            self.root_config.get(
                f"{self.root_config.TRANSFORMATIONS_PATH}.{file_type}",
                fallback={},
            ),
        )

    def absolute_path(self, p):
        """
        Gets the absolute path relative to the config files directory.

        :param p: The path relative to the config file

        :return: The absolute path if both the config path and `p` are set,
            if `p` is `None`, `None` is returned. If the config path is `None`,
            `p` is returned without modification
        """
        return self.root_config.absolute_path(p)

    def keys(self):
        """
        Gets an iterable keys.
        """
        return self.config.keys()

    def items(self):
        """
        Gets an iterable of (key, value) tuples.
        """
        return self.config.items()

    @property
    def path(self):
        """
        Returns the path of the root config
        """
        return self.root_config.path

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
        return get_json_path(self.config, path, fallback=fallback)

    def __eq__(self, other):
        return self.config == other.config
