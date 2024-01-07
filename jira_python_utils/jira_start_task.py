# -*- coding: utf-8 -*-
import click
import logging
import os
import pathlib
import sys

from datetime import datetime
from rich.console import Console

from .helper import get_jira_url
from .file_utils import check_infile_status


error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
)


DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv("USER"),
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = False



def echo_script(jira_id: str, jira_dir: str) -> None:
    console.print("Execute this when ready to start:")
    outfile = os.path.join(jira_dir, f"script_{DEFAULT_TIMESTAMP}.txt")
    console.print(f"[bold yellow]script -q {outfile}[/]")
    console.print(f"[bold yellow]echo 'Starting task {jira_id}'[/]")


def create_symlink_directory(jira_dir: str, verbose: bool = DEFAULT_VERBOSE) -> None:

    target_dir = os.path.join(os.getenv("HOME"), "JIRA", os.path.basename(jira_dir))

    # create the symlink
    os.symlink(jira_dir, target_dir)

    # verify the symlink was created successfully
    if os.path.islink(target_dir):
        logging.info(f"Symlink created: {target_dir} -> {jira_dir}")
        if verbose:
            console.print(f"Symlink created: {target_dir} -> {jira_dir}")
    else:
        error_console.print(f"Could not create symlink '{target_dir}'")
        sys.exit(1)


def create_readme_file(jira_dir: str, jira_id: str, url: str, verbose: bool = DEFAULT_VERBOSE) -> None:
    outfile = os.path.join(jira_dir, "README.md")
    if not os.path.exists(outfile):
        with open(outfile, 'w') as of:
            of.write(f"# Jira ID: {jira_id}\n")
            of.write(f"URL: {url}\n<br>\n")
            of.write(f"Date: {str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))}\n<br>\n")

        logging.info(f"Wrote file '{outfile}'")
        if verbose:
            console.print(f"Wrote file '{outfile}'")
    console.print(f"README file is ready: '{outfile}'")


def initialize_jira_directory(jira_id: str, verbose: bool = DEFAULT_VERBOSE) -> str:
    """Create the Jira id directory and return the that path.

    Args:
        jira_id (str): The Jira issue id

    Returns:
        dir (str): The absolute path to the Jira issue directory created
    """
    jira_dir = os.path.join(os.getenv("HOME"), "vboxshare", "JIRA", jira_id)
    if not os.path.exists(jira_dir):
        pathlib.Path(jira_dir).mkdir(parents=True, exist_ok=True)

        logging.info(f"Created directory '{jira_dir}'")
        if verbose:
            console.print(f"Created directory '{jira_dir}'")
    else:
        logging.info(f"'{jira_dir}' already exists")
        if verbose:
            console.print(f"'{jira_dir}' already exists")

    return jira_dir


@click.command()
@click.option('--jira_id', help='The Jira ticket identifier')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{DEFAULT_VERBOSE}'")
def main(jira_id: str, logfile: str, outdir: str, verbose: bool):

    error_ctr = 0

    if jira_id is None:
        error_console.print("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        console.print(f"[bold yellow]--outdir was not specified and therefore was set to '{outdir}'[/]")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        console.print(f"[bold yellow]Created output directory '{outdir}'[/]")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        console.print(f"[bold yellow]--logfile was not specified and therefore was set to '{logfile}'[/]")

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        console.print(f"[bold yellow]--verbose was not specified and therefore was set to '{verbose}'[/]")

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

    url = get_jira_url(rest_url_file)

    url = f"{url}/browse/{jira_id}"
    logging.info(f"{url=}")
    jira_dir = initialize_jira_directory(jira_id, verbose)
    create_symlink_directory(jira_dir, verbose)
    create_readme_file(jira_dir, jira_id, url, verbose)
    echo_script(jira_id, jira_dir)


if __name__ == '__main__':
    main()
