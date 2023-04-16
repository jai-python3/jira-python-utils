# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

import click
import yaml
from colorama import Fore, Style
from jira import JIRA

TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))


DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
)


DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.path.splitext(os.path.basename(__file__))[0],
    TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'conf/jira_weekly_updates_config.yaml'
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = False



def echo_script(jira_id: str, jira_dir: str) -> None:
    print("Execute this when ready to start:")
    outfile = os.path.join(jira_dir, f"script_{TIMESTAMP}.txt")
    print_yellow(f"script -q {outfile}")
    print_yellow(f"echo 'Starting task {jira_id}'")


def create_symlink_directory(jira_dir: str, verbose: bool = DEFAULT_VERBOSE) -> None:

    target_dir = os.path.join(os.getenv("HOME"), "JIRA", os.path.basename(jira_dir))

    # create the symlink
    os.symlink(jira_dir, target_dir)

    # verify the symlink was created successfully
    if os.path.islink(target_dir):
        logging.info(f"Symlink created: {target_dir} -> {jira_dir}")
        if verbose:
            print(f"Symlink created: {target_dir} -> {jira_dir}")
    else:
        print_red(f"Could not create symlink '{target_dir}'")
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
            print(f"Wrote file '{outfile}'")
    print(f"README file is ready: '{outfile}'")


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
            print(f"Created directory '{jira_dir}'")
    else:
        logging.info(f"'{jira_dir}' already exists")
        if verbose:
            print(f"'{jira_dir}' already exists")

    return jira_dir


def check_config_file(config_file: str) -> None:
    """Check the configuration file."""
    if not os.path.exists(config_file):
        print_red(f"configuration file '{config_file}' does not exist")
        sys.exit(1)

    if not os.path.isfile(config_file):
        print_red(f"configuration file '{config_file}' is not a regular file")
        sys.exit(1)

    if not config_file.endswith(".yaml"):
        print_red(
            f"configuration file '{config_file}' does not have a .yaml file extension"
        )
        sys.exit(1)

    if os.path.getsize(config_file) == 0:
        print_red(f"configuration file'{config_file}' has no content")
        sys.exit(1)


def print_red(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.RED + msg + Style.RESET_ALL)


def print_green(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.GREEN + msg + Style.RESET_ALL)


def print_yellow(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.YELLOW + msg + Style.RESET_ALL)


@click.command()
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--jira_id', help='The Jira ticket identifier')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{DEFAULT_VERBOSE}'")
def main(config_file: str, jira_id: str, logfile: str, outdir: str, verbose: bool):

    error_ctr = 0

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
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

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        print_yellow(f"--config_file was not specified and therefore was set to '{config_file}'")

    check_config_file(config_file)

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print_yellow(f"--verbose was not specified and therefore was set to '{verbose}'")

    rest_url_file = DEFAULT_URL_FILE
    if not os.path.exists(rest_url_file):
        print("JIRA REST URL file '{}' does not exist".format(rest_url_file))
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            url = url.strip()
            print("read the REST URL from file '{}'".format(rest_url_file))

    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    logging.info(f"Loading configuration from '{config_file}'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    url = f"{url}/browse/{jira_id}"
    logging.info(f"{url=}")
    jira_dir = initialize_jira_directory(jira_id, verbose)
    create_symlink_directory(jira_dir, verbose)
    create_readme_file(jira_dir, jira_id, url, verbose)
    echo_script(jira_id, jira_dir)


if __name__ == '__main__':

    main()
