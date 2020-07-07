import logging
import os
from datetime import datetime
from logging.config import dictConfig as loggingDictConfig

import click
import yaml

from converter.config import Config
from converter.controller import Controller


class ColorFormatter(logging.Formatter):
    colors = {
        logging.ERROR: "red",
        logging.CRITICAL: "red",
        logging.DEBUG: "blue",
        logging.WARNING: "yellow",
    }

    def format(self, record) -> str:
        return click.style(
            super().format(record), fg=self.colors.get(record.levelno),
        )


class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno <= logging.INFO


class ClickEchoHandler(logging.Handler):
    def emit(self, record):
        click.echo(
            self.format(record), err=record.levelno >= logging.WARNING,
        )


def init_logging(verbosity, no_color):
    filename_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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
                    "filename": f"{filename_time}-converter.log",
                    "level": logging.DEBUG,
                    "mode": "w",
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console", "log-file"]},
        }
    )
    logging.captureWarnings(True)


@click.group()
@click.option("--option", "-o", nargs=2, multiple=True)
@click.option(
    "--config", "-c", default="./config.yml", envvar="CONVERTER_CONFIG"
)
@click.option("--verbose", "-v", count=True)
@click.option("--no-color",)
@click.pass_context
def cli(ctx, config, verbose, no_color, option):
    ctx.ensure_object(dict)

    init_logging(verbose, no_color)

    options = dict(option)

    ctx.obj["config"] = Config(
        config_path=config,
        argv={k: yaml.load(v, yaml.SafeLoader) for k, v in options.items()},
        env=os.environ,
    )


@cli.command()
@click.pass_context
def show_config(ctx):
    click.echo(ctx.obj["config"].to_yaml())


@cli.command()
@click.pass_context
def run(ctx):
    try:
        logging.debug("Running with config:")
        logging.debug(ctx.obj["config"].to_yaml())
        Controller(ctx.obj["config"]).run()
    except Exception as e:
        logging.exception(e)
    else:
        logging.info("Transformation Complete")
