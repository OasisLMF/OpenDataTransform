from unittest import mock

import yaml
from click.testing import CliRunner
from hypothesis import given
from hypothesis.strategies import fixed_dictionaries, just, one_of, tuples

from converter.cli import cli
from converter.config import Config
from converter.mapping import BaseMapping
from converter.runner import BaseRunner
from tests.config.test_config import config_file


class FakeRunner(BaseRunner):
    def transform(self, extractor, mapping):
        return []


class FakeMapping(BaseMapping):
    def get_transformations(self):
        return []


def options():
    return tuples(
        one_of(fixed_dictionaries({"foo": just({"file": "bizz"})}), just({})),
        one_of(
            fixed_dictionaries({"converter_foo_env": just("fizz")}), just({}),
        ),
        one_of(tuples(just("foo.args"), just("fuzz")), just(())),
        just(
            {
                "runner": {"path": "tests.test_cli.FakeRunner"},
                "mapping": {
                    "path": "tests.test_cli.FakeMapping",
                    "options": {"input_format": "A", "output_format": "B"},
                },
                "extractor": {"path": "tests.connector.fakes.FakeConnector"},
                "loader": {"path": "tests.connector.fakes.FakeConnector"},
            },
        ),
    )


@given(opts=options())
def test_show_config(opts):
    conf, env, argv, ovr = opts
    argv_dict = dict([argv] if argv else [])
    argv = ["-o", *argv] if argv else []

    with config_file({**conf, **ovr}) as f, mock.patch("os.environ", env):
        expected_conf = Config(
            config_path=f, env=env, argv=argv_dict, overrides=ovr,
        )

        runner = CliRunner()

        result = runner.invoke(cli, [*argv, "--config", f, "show-config"])

        assert result.exit_code == 0
        assert yaml.load(result.output, yaml.SafeLoader) == expected_conf


@given(opts=options())
def test_run(opts):
    conf, env, argv, ovr = opts
    argv_dict = dict([argv] if argv else [])
    argv = ["-o", *argv] if argv else []

    with config_file({**conf, **ovr}) as f, mock.patch(
        "converter.cli.Controller"
    ) as mock_controller, mock.patch("os.environ", env):
        expected_conf = Config(
            config_path=f, env=env, argv=argv_dict, overrides=ovr,
        )

        runner = CliRunner()

        result = runner.invoke(cli, [*argv, "--config", f, "run"])

        assert result.exit_code == 0
        mock_controller.assert_called_once_with(expected_conf)


def test_run_raises___exception_is_logged():
    expected_exception = Exception("Some Error")

    with mock.patch("logging.exception") as mock_exception_logger, mock.patch(
        "converter.cli.Controller", side_effect=expected_exception
    ):
        runner = CliRunner()

        result = runner.invoke(cli, ["run"])

        mock_exception_logger.assert_called_once_with(expected_exception)
        assert result.exit_code == 1
