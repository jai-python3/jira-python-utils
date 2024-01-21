# -*- coding: utf-8 -*-
"""Initiate the JIRA workspace."""
import click
import logging
import os
import pathlib
import sys

from datetime import datetime
from rich.console import Console

console = Console()

from console_helper import print_red, print_yellow

DEFAULT_PROJECT = "jira-python-utils"

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv("USER"),
    DEFAULT_PROJECT,
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


def create_jira_directory(jira_dir: str) -> None:
    """Create the JIRA directory if it does not exist.

    Args:
        jira_dir (str): The JIRA directory.
    """
    if not os.path.exists(jira_dir):
        pathlib.Path(jira_dir).mkdir(parents=True, exist_ok=True)

        console.print(f"Created directory '{jira_dir}'")
    else:
        console.print(f"'{jira_dir}' already exists")


@click.command()
@click.option('--jira_id', help='The Jira ticket identifier')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
def main(jira_id: str, logfile: str, outdir: str):
    """Initiate the JIRA workspace.

    Args:
        jira_id (str): The JIRA ticket identifier.
        logfile (str): The log file.
        outdir (str): The output directory.
    """
    error_ctr = 0

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print_red("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print_yellow(f"--outdir was not specified and therefore was set to '{outdir}'")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        print_yellow(f"Created output directory '{outdir}'")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        print_yellow(f"--logfile was not specified and therefore was set to '{logfile}'")


    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

    jira_dir = os.path.join(os.getenv("HOME"), "JIRA", jira_id)
    create_jira_directory(jira_dir)

    shared_jira_dir = os.path.join(os.getenv("HOME"), "vboxshare", "JIRA", jira_id)
    create_jira_directory(shared_jira_dir)


if __name__ == '__main__':

    main()
