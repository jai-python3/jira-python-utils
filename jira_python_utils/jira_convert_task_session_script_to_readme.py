# -*- coding: utf-8 -*-
"""Convert a script session file to a README file."""
import click
import logging
import os
import pathlib
import sys

from datetime import datetime
from typing import List

from .console_helper import print_red, print_yellow
from .file_utils import check_infile_status

DEFAULT_PROJECT = "jira-python-utils"

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_COMMAND_PROMPT = "➜"

DEFAULT_COMMAND_START = "✗"

DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
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


def get_file_content(infile: str, command_prompt: str = DEFAULT_COMMAND_PROMPT, command_start: str = DEFAULT_COMMAND_START) -> List[str]:
    """Read the file and return the content as a list of lists.

    Args:
        infile (str): The input file absolute path.
        command_prompt (str, optional): The command prompt string. Defaults to DEFAULT_COMMAND_PROMPT.
        command_start (str, optional): The command start string. Defaults to DEFAULT_COMMAND_START.

    Returns:
        List[str]: The content of the file as a list of lists.
    """
    command_prompt = command_prompt.lstrip()
    command_start = command_start.lstrip()

    logging.info(f"{command_prompt=} {command_start=}")

    logging.info(f"Will read file '{infile}'")
    line_ctr = 0
    content = []
    current_command = None
    command_ctr = 0
    current_command_output = []

    with open(infile, 'r') as f:
        for line in f:
            line_ctr += 1
            print(f"{line}")
            if line.startswith(command_prompt):
                command_ctr += 1
                content.append([current_command, current_command_output])
                current_command = line.split(command_start)[1]
                current_command_output = []

        # Store the last line in the file
        content.append([current_command, current_command_output])

    if line_ctr > 0:
        logging.info(f"Read '{line_ctr}' lines from file '{infile}'")
        logging.info(f"Found '{command_ctr}' commands in file '{infile}'")
    else:
        logging.info(f"Did not read any lines from file '{infile}'")

    return content


def include() -> bool:
    """Prompt the user to include the command in the README.

    Returns:
        bool: True if the user wants to include the command in the README, False otherwise.
    """
    ans = input("Include this command in the README? [Y/n] ")
    ans = ans.strip()
    if ans == '' or ans.lower() == 'y':
        return True
    return False

def get_description() -> str:
    """Prompt the user for a description of the command."""
    desc = None
    while desc is None or desc == '':
        desc = input("What is the description? ")
        desc = desc.strip()
    return desc

def convert_file(infile: str, outfile: str, jira_id: str, verbose: bool = DEFAULT_VERBOSE, command_prompt: str = DEFAULT_COMMAND_PROMPT, command_start: str = DEFAULT_COMMAND_START) -> None:
    """Convert the input file to a README file.

    Args:
        infile (str): The input file absolute path.
        outfile (str): The output file absolute path.
        jira_id (str): The Jira issue id.
        verbose (bool, optional): Will print more info to STDOUT. Defaults to DEFAULT_VERBOSE.
        command_prompt (str, optional): The command prompt string. Defaults to DEFAULT_COMMAND_PROMPT.
        command_start (str, optional): The command start string. Defaults to DEFAULT_COMMAND_START.
    """
    content = get_file_content(infile, command_prompt, command_start)

    with open(outfile, 'w') as of:
        for i, command_set in enumerate(content, start=1):
            command = command_set[0]
            command_output = command_set[1]
            print(f"Here is command '{i}': {command}")
            print(f"{command_output}\n")
            if not include():
                continue

            desc = get_description()
            of.write(f"## Step {i} {desc}\n")
            of.write('"""shell\n')
            of.write(f"{command_output}")
            of.write('"""\n')

    logging.info(f"Wrote file '{outfile}'")
    if verbose:
        print(f"Wrote file '{outfile}'")


def echo_script(jira_id: str, jira_dir: str) -> None:
    """Start the script command.

    Args:
        jira_id (str): The Jira issue id.
        jira_dir (str): The directory where the script file will be written.
    """
    print("Execute this when ready to start:")
    outfile = os.path.join(jira_dir, f"script_{DEFAULT_TIMESTAMP}.txt")
    print_yellow(f"script -q {outfile}")
    print_yellow(f"echo 'Starting task {jira_id}'")


def create_symlink_directory(jira_dir: str, verbose: bool = DEFAULT_VERBOSE) -> None:
    """Create the symlink to the Jira issue directory.

    Args:
        jira_dir (str): The Jira issue directory.
        verbose (bool, optional): If True print info to STDOUT. Defaults to DEFAULT_VERBOSE.
    """

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
    """Create the README file.

    Args:
        jira_dir (str): The Jira issue directory.
        jira_id (str): The Jira issue id.
        url (str): The Jira issue URL.
        verbose (bool, optional): If true print more info to STDOUT. Defaults to DEFAULT_VERBOSE.
    """
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



@click.command()
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--infile', help='The input script session file')
@click.option('--jira_id', help='The Jira ticket identifier')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--outfile', help="The output README file")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{DEFAULT_VERBOSE}'")
def main(config_file: str, infile: str, jira_id: str, logfile: str, outdir: str, outfile: str, verbose: bool):
    """Convert a script session file to a README file.

    Args:
        config_file (str): The configuration file.
        infile (str): The input script session file.
        jira_id (str): The Jira ticket identifier.
        logfile (str): The log file.
        outdir (str): The output directory.
        outfile (str): The output README file.
        verbose (bool): The verbose flag.
    """

    error_ctr = 0

    if infile is None:
        print_red("--infile was not specified")
        error_ctr += 1

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    check_infile_status(infile)

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

    if outfile is None:
        outfile = os.path.join(os.getenv("HOME"), "JIRA", "README.md")
        print_yellow(f"--outfile was not specified and therefore was set to '{outfile}'")

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print_yellow(f"--verbose was not specified and therefore was set to '{verbose}'")

    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

    convert_file(infile, outfile, jira_id, verbose)


if __name__ == '__main__':

    main()
