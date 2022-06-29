# coding=utf-8
"""CLI commands."""
import click

from bancor_simulator.archive.utils.logging_utils import print_info


@click.group()
def cli():
    """CLI command with no arguments. Does nothing."""
    pass


@click.command()
def info():
    """CLI command with `info` argument. Prints info about the system, bancor3, and dependencies of bancor3."""
    print_info()


cli.add_command(info)
