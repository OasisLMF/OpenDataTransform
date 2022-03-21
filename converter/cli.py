import logging
import os
import sys
from datetime import datetime
from importlib import reload
from logging.config import dictConfig as loggingDictConfig

import click
import yaml
from PySide6.QtWidgets import QApplication

from converter.config import Config
from converter.controller import Controller
from converter.ui.main_window import MainWindow


class ColorFormatter(logging.Formatter):
    """
    Changes the color of the log message based on the log level. Errors are
    red, warnings are yellow and debug messages are blue.

    :param colors: Mapping of log level to colors
    """

    colors = {
        logging.ERROR: "red",
        logging.CRITICAL: "red",
        logging.DEBUG: "blue",
        logging.WARNING: "yellow",
    }

    def format(self, record) -> str:
        """
        Adds the color to the log message.

        :param record: The record to format

        :return: The formatted message
        """
        return click.style(
            super().format(record),
            fg=self.colors.get(record.levelno),
        )


class ClickEchoHandler(logging.Handler):
    """
    Sends the log message onto `click.echo`
    """

    def emit(self, record):
        click.echo(
            self.format(record),
            err=record.levelno >= logging.WARNING,
        )


def init_logging(verbosity, no_color, config):
    """
    Sets up the logging config for the console and files

    :param verbosity: The verbosity level
        0 - errors and warnings only
        1 - info
        2 - debug
    :param no_color: Don't add the color to the output
    :param config: The path to the config file
    """
    logging.shutdown()
    reload(logging)

    config_dir = os.path.abspath(os.path.dirname(config))
    time_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_dir = os.path.join(config_dir, "runs", time_string)
    os.makedirs(log_dir, exist_ok=True)

    console_log_level = [logging.WARNING, logging.INFO, logging.DEBUG][
        min(2, verbosity)  # max verbosity level is 2
    ]

    loggingDictConfig(
        {
            "version": 1,
            "formatters": {
                "console": {
                    "class": (
                        "logging.Formatter"
                        if no_color
                        else "converter.cli.ColorFormatter"
                    ),
                },
                "file": {"format": "%(asctime)s %(levelname)-7s: %(message)s"},
                "yaml": {"format": "%(message)s"},
            },
            "filters": {"info_only": {"class": "converter.cli.InfoFilter"}},
            "handlers": {
                "console": {
                    "class": "converter.cli.ClickEchoHandler",
                    "formatter": "console",
                    "level": console_log_level,
                },
                "log-file": {
                    "class": "logging.FileHandler",
                    "formatter": "file",
                    "filename": os.path.join(log_dir, "converter.log"),
                    "level": logging.DEBUG,
                    "mode": "w",
                },
                "validation-log-yaml": {
                    "class": "logging.FileHandler",
                    "formatter": "yaml",
                    "filename": os.path.join(log_dir, "validation.yaml"),
                    "level": logging.INFO,
                    "mode": "w",
                },
                "metadata-log-yaml": {
                    "class": "logging.FileHandler",
                    "formatter": "yaml",
                    "filename": os.path.join(log_dir, "metadata.yaml"),
                    "level": logging.INFO,
                    "mode": "w",
                },
            },
            "loggers": {
                "converter.validator": {
                    "level": logging.INFO,
                    "handlers": ["validation-log-yaml"],
                    "propagate": True,
                },
                "converter.metadata": {
                    "level": logging.INFO,
                    "handlers": ["metadata-log-yaml"],
                    "propagate": True,
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console", "log-file"]},
        }
    )
    logging.captureWarnings(True)


@click.group(invoke_without_command=True)
@click.option(
    "--option",
    "-o",
    nargs=2,
    multiple=True,
    help=(
        "Sets a configuration option, a path and value are required "
        "eg -o extractor.options.foo.bar bash"
    ),
)
@click.option(
    "--config",
    "-c",
    default="./config.yml",
    envvar="CONVERTER_CONFIG",
    help="Path to the configuration file.",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help=(
        "Specifies the verbosity level, if used multiple "
        "times the verbosity is increased further"
    ),
)
@click.option(
    "--no-color",
    help="Disables colorised output.",
    is_flag=True,
    flag_value=False,
)
@click.pass_context
def cli(ctx, config, verbose, no_color, option):
    """
    Initialises the cli grouping with default options.
    """
    ctx.ensure_object(dict)

    init_logging(verbose, no_color, config)

    options = dict(option)

    ctx.obj["config"] = Config(
        config_path=config,
        argv={k: yaml.load(v, yaml.SafeLoader) for k, v in options.items()},
        env=os.environ,
    )

    if ctx.invoked_subcommand is None:
        app = QApplication(sys.argv)

        if not ctx.obj["config"].path:
            # if there is no config path add blank template, acc, loc and ri
            # entries so that all tabs are open
            ctx.obj["config"] = Config(
                config_path=config,
                argv={k: yaml.load(v, yaml.SafeLoader) for k, v in options.items()},
                env=os.environ,
                overrides={
                    Config.TEMPLATE_TRANSFORMATION_PATH: {},
                    Config.TRANSFORMATIONS_PATH: {
                        Config.ACC_TRANSFORMATION_LABEL: {},
                        Config.LOC_TRANSFORMATION_LABEL: {},
                        Config.RI_TRANSFORMATION_LABEL: {},
                    }
                }
            )

        widget = MainWindow(
            ctx.obj["config"],
            lambda p: init_logging(verbose, no_color, p),
        )
        widget.show()

        sys.exit(app.exec_())


@cli.command()
@click.pass_context
def show_config(ctx):
    """
    Prints the resolved config to the console
    """
    click.echo(ctx.obj["config"].to_yaml())


@cli.command()
@click.pass_context
def run(ctx):
    """
    Runs the data conversion
    """
    try:
        logging.debug(f"Running with config:\n{ctx.obj['config'].to_yaml()}")
        Controller(ctx.obj["config"]).run()
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
    else:
        logging.info("Transformation Complete")
