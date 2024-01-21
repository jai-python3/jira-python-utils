# -*- coding: utf-8 -*-
import click
import logging
import json
import os
import pathlib
import sys

from pathlib import Path
from datetime import datetime
from rich.console import Console
from typing import Optional

from .file_utils import check_infile_status, check_indir_status
from .console_helper import print_yellow, print_red

error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv("USER"),
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = False


def get_file_list(indir: str = None, extension: str = None) -> list:
    """Get the list of files in the specified directory.

    Args:
        indir (str): The directory to search for files.
        extension (str): The file extension to filter on.

    Returns:
        List[str]: The list of files found in the directory.
    """
    if extension is None:
        logging.info(f"Going to search for files in directory '{indir}'")
    else:
        logging.info(f"Going to search for files with extension '{extension}' in directory '{indir}'")

    file_list = []
    for dirpath, dirnames, filenames in os.walk(indir):
        if 'venv' in dirpath:
            logging.info(f"Going to ignore files in directory '{dirpath}'")
            continue
        for name in filenames:
            path = os.path.normpath(os.path.join(dirpath, name))
            if os.path.isfile(path):
                if extension is not None:
                    if os.path.endswith('.{extension}'):
                        file_list.append(path)
                else:
                    file_list.append(path)

    return file_list


def scan_jira_dir(jira_root_dir: str, verbose: bool = DEFAULT_VERBOSE) -> None:
    """Scan the Jira directory and print the metadata for each Jira issue.

    Args:
        jira_root_dir (str): The root directory where your Jira issue-specific subdirectories are created.
        verbose (bool, optional): If true, print more info to STDOUT. Defaults to DEFAULT_VERBOSE.
    """

    check_indir_status(jira_root_dir, "metadata.json")

    file_list = get_file_list(jira_root_dir, verbose)
    for f in file_list:
        check_infile_status(f)

        with open(f, 'r') as jf:
            jira_dict = json.load(jf)
            jira_id = jira_dict['jira_id']
            url = jira_dict['url']
            title = jira_dict['title']
            date = jira_dict['date']
            print(f"\n\nJira ID: {jira_id}")
            print(f"Title: {title}")
            print(f"Date: {date}")
            print(f"URL: {url}")
            print(f"File: {f}")


@click.command()
@click.option('--jira_root_dir', help='Optional: The root directory where your Jira issue-specific subdirectories are created')
@click.option('--logfile', help="Optional: The log file")
@click.option('--outdir', help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{DEFAULT_VERBOSE}'")
def main(jira_root_dir: Optional[str], logfile: Optional[str], outdir: Optional[str], verbose: Optional[bool]):
    """Scan the Jira directory and print the metadata for each Jira issue.

    Args:
        jira_root_dir (Optional[str]): The root directory where your Jira issue-specific subdirectories are created.
        logfile (Optional[str]): The log file.
        outdir (Optional[str]): The default is the current working directory - default is '{DEFAULT_OUTDIR}'.
        verbose (Optional[bool]): If true, print more info to STDOUT - default is '{DEFAULT_VERBOSE}'.
    """

    error_ctr = 0

    if jira_root_dir is None:
        print_red("--jira_root_dir was not specified")
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

    if verbose is None:
        verbose = DEFAULT_VERBOSE
        print_yellow(f"--verbose was not specified and therefore was set to '{verbose}'")

    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

    scan_jira_dir(jira_root_dir, verbose)

if __name__ == '__main__':
    main()
