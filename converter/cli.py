import os

import click
import yaml

from converter.config import Config
from converter.controller import Controller


def init_logging(verbosity, no_color):
    pass


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
    Controller(ctx.obj["config"]).run()
