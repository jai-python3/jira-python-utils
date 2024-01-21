# -*- coding: utf-8 -*-
"""Start a Jira task."""
import click
import logging
import json
import os
import pathlib
import sys
import yaml

from datetime import datetime
from pathlib import Path
from rich.console import Console
from typing import Optional

from .helper import get_jira_url, get_summary
from .file_utils import check_infile_status
from .console_helper import print_yellow, print_red

error_console = Console(stderr=True, style="bold red")

console = Console()

DEFAULT_PROJECT = "jira-python-utils"

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
)

DEFAULT_CREDENTIAL_FILE = os.path.join(
    os.getenv('HOME'),
    ".jira",
    "credentials.txt"
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'conf',
    'config.yaml'
)

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv("USER"),
    DEFAULT_PROJECT,
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = False


def echo_script(jira_id: str, jira_dir: str) -> None:
    """Echo the script command to execute when ready to start.

    Args:
        jira_id (str): The Jira issue identifier.
        jira_dir (str): The Jira issue-specific directory.
    """
    console.print("Execute this when ready to start:")
    outfile = os.path.join(jira_dir, f"script_{DEFAULT_TIMESTAMP}.txt")
    console.print(f"script -q {outfile}[/]")
    console.print(f"echo 'Starting task {jira_id}'[/]")


def get_home_jira_dir() -> str:
    """Derive the Jira directory in the user's home directory.

    Returns:
        str: The Jira directory in the user's home directory.
    """
    home_jira_dir = os.path.join(os.getenv("HOME"), "JIRA")
    if not os.path.exists(home_jira_dir):
        pathlib.Path(home_jira_dir).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory '{home_jira_dir}'")
    return home_jira_dir

def create_symlink_directory(jira_dir: str, verbose: bool = DEFAULT_VERBOSE) -> None:
    """Create a symlink to the Jira issue-specific directory in the user's home directory.

    Args:
        jira_dir (str): The Jira issue-specific directory.
        verbose (bool, optional): If true print more info to STDOUT. Defaults to DEFAULT_VERBOSE.
    """

    home_jira_dir = get_home_jira_dir()
    target_dir = os.path.join(home_jira_dir, os.path.basename(jira_dir))

    print_yellow(f"Creating symlink '{target_dir}' -> '{jira_dir}'")

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


def create_readme_file(jira_dir: str, jira_id: str, url: str, title: str, verbose: bool = DEFAULT_VERBOSE) -> None:
    """Create a README.md file in the Jira issue directory.

    Args:
        jira_dir (str): The Jira issue-specific directory.
        jira_id (str): The Jira issue identifier.
        url (str): The Jira issue-specific URL.
        title (str): The summary of the Jira issue.
        verbose (bool, optional): If True, print more details to STDOUT. Defaults to DEFAULT_VERBOSE.
    """
    outfile = os.path.join(jira_dir, "README.md")
    if not os.path.exists(outfile):
        with open(outfile, 'w') as of:
            of.write(f"# Jira ID: {jira_id}\n")
            of.write(f"URL: {url}\n<br>\n")
            of.write(f"Date: {str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))}\n<br>\n")
            if title is not None:
                of.write(f"Title: {title}\n<br>\n")

        logging.info(f"Wrote file '{outfile}'")
        if verbose:
            console.print(f"Wrote file '{outfile}'")
    console.print(f"README file is ready: '{outfile}'")


def create_metadata_file(jira_dir: str, jira_id: str, url: str, title: str) -> None:
    """Create a [jira_id].metadata.json file.

    This will contain information about the Jira issue
    that can be parsed by other scripts for report generation.

    Args:
        jira_dir (str): The Jira issue-specific directory.
        jira_id (str): The Jira issue identifier.
        url (str): The Jira issue-specific URL.
        title (str): The summary of the Jira issue.
    """
    outfile = os.path.join(jira_dir, f"{jira_id}.metadata.json")
    lookup = {
        "jira_id": jira_id,
        "url": url,
        "title": title,
        "date": str(datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))
    }

    # Write lookup to JSON file
    with open(outfile, 'w') as of:
        json.dump(lookup, of)

    logging.info(f"Wrote metadata file '{outfile}'")
    console.print(f"Wrote metadata file '{outfile}'")


def initialize_jira_directory(jira_root_dir: str, jira_id: str, verbose: bool = DEFAULT_VERBOSE) -> str:
    """Create the Jira id directory and return the that path.

    Args:
        jira_root_dir (str): The root directory where the Jira issue-specific directory will be created
        jira_id (str): The Jira issue id

    Returns:
        dir (str): The absolute path to the Jira issue directory created
    """
    jira_dir = os.path.join(jira_root_dir, jira_id)
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
@click.option('--config_file', help=f"Optional: The configuration YAML file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--crdential_file', help=f"Optional: The file containing the username and password for logging into Jira - default is '{DEFAULT_CREDENTIAL_FILE}'")
@click.option('--jira_id', help='Required: The Jira ticket identifier')
@click.option('--jira_root_dir', help='Optional: The root directory where your Jira issue-specific subdirectories are created')
@click.option('--logfile', help="Optional: The log file")
@click.option('--outdir', help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{DEFAULT_VERBOSE}'")
def main(config_file: Optional[str], credential_file: Optional[str], jira_id: str, jira_root_dir: str, logfile: Optional[str], outdir: Optional[str], verbose: Optional[bool]):
    """Start a Jira task.

    Args:
        config_file (Optional[str]): The configuration YAML file.
        credential_file (Optional[str]): The file containing the username and password for logging into Jira.
        jira_id (str): The Jira ticket identifier.
        jira_root_dir (str): The root directory where your Jira issue-specific subdirectories are created.
        logfile (Optional[str]): The log file.
        outdir (Optional[str]): The default is the current working directory - default is '{DEFAULT_OUTDIR}'.
        verbose (Optional[bool]): If true, print more info to STDOUT - default is '{DEFAULT_VERBOSE}'.
    """

    error_ctr = 0

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print_red("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        print_yellow(f"--config_file was not specified and therefore was set to '{config_file}'")

    check_infile_status(config_file, "yaml")

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

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print_yellow(f"--verbose was not specified and therefore was set to '{verbose}'")

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)
    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )


    logging.info(f"Will load contents of config file '{config_file}'")
    config = yaml.safe_load(Path(config_file).read_text())

    if jira_root_dir is None:
        if "jira_root_dir" not in config:
            print_red(f"Could not find jira_root_dir in the configuration file '{config_file}'")
            sys.exit(1)

    jira_root_dir = config['jira_root_dir']
    if jira_root_dir is None or jira_root_dir == "":
        print_red(f"jira_root_dir could not be derived from the configuration file '{config_file}' and so was set to default '{jira_root_dir}'")
        sys.exit(1)
    print_yellow(f"The jira_root_dir was read from the configuration file '{config_file}' and set to '{jira_root_dir}'")

    jira_base_url = get_jira_url(rest_url_file)

    url = f"{jira_base_url}/browse/{jira_id}"

    logging.info(f"{url=}")

    jira_dir = initialize_jira_directory(jira_root_dir, jira_id, verbose)

    create_symlink_directory(jira_dir, verbose)

    summary = get_summary(jira_id, credential_file, rest_url_file)

    create_readme_file(jira_dir, jira_id, url, summary, verbose)

    create_metadata_file(jira_dir, jira_id, url, summary)

    echo_script(jira_id, jira_dir)



if __name__ == '__main__':
    main()
