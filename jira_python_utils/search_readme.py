# -*- coding: utf-8 -*-
"""Search for Jira README.md, parse the file and output summary details."""
import click
import logging
import os
import pathlib
import sys

from rich.console import Console
from typing import Dict, Optional

from . import constants
from .file_utils import check_infile_status
from .console_helper import print_yellow, print_red, print_green

error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_ORDER = [
    "jira_id",
    "reference",
    "keywords",
    "codebase",
    "date_created",
    "date_completed",
    "due_date",
    "status",
    "issue_type",
]

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP
)

def process_readme(
    exclude: str,
    infile: str,
    logfile: str,
    outdir: str,
    verbose: bool = constants.DEFAULT_VERBOSE
    ) -> None:
    """Parse the README.md and output the summary details.

    Args:
        exclude (str): Comma-separated list fields to exclude from the summary details.
        infile (str): The README.md file to be analyzed.
        logfile (str): The log file.
        outdir (str): The output directory.
        verbose (bool, optional): If True, more details to STDOUT. Defaults to constants.DEFAULT_VERBOSE.
    """
    logging.info(f"Will read file '{infile}'")
    line_ctr = 0
    lookup = {}
    with open(infile, 'r') as f:
        for line in f:
            line_ctr += 1
            line = line.strip()


            if line.lower().startswith("# jira id:") or line.lower().startswith("# jira:"):
                jira_id = line.split(":")[1].strip()
                lookup["jira_id"] = jira_id
                logging.info(f"Found Jira ID '{jira_id}' at line '{line_ctr}'")
            elif line.lower().startswith("# jira "):
                jira_id = line.replace("# Jira", "").strip()
                lookup["jira_id"] = jira_id
                logging.info(f"Found Jira ID '{jira_id}' at line '{line_ctr}'")
            elif line.lower().startswith("keywords:"):
                keywords = line.split(":")[1].strip()
                lookup["keywords"] = keywords
                logging.info(f"Found keywords '{keywords}' at line '{line_ctr}'")
            elif line.lower().startswith("codebase:"):
                codebase = line.split(":")[1].strip()
                lookup["codebase"] = codebase
                logging.info(f"Found codebase '{codebase}' at line '{line_ctr}'")
            elif line.lower().startswith("date-created:"):
                date_created = line.split(":")[1].strip()
                lookup["date_created"] = date_created
                logging.info(f"Found date_created '{date_created}' at line '{line_ctr}'")
            elif line.lower().startswith("date-completed:"):
                date_completed = line.split(":")[1].strip()
                lookup["date_completed"] = date_completed
                logging.info(f"Found date_completed '{date_completed}' at line '{line_ctr}'")
            elif line.lower().startswith("due-date:"):
                due_date = line.split(":")[1].strip()
                lookup["due_date"] = due_date
                logging.info(f"Found due_date '{due_date}' at line '{line_ctr}'")
            elif line.lower().startswith("status:"):
                status = line.split(":")[1].strip()
                lookup["status"] = status
                logging.info(f"Found status '{status}' at line '{line_ctr}'")
            elif line.lower().startswith("issue-type:"):
                issue_type = line.split(":")[1].strip()
                lookup["issue_type"] = issue_type
                logging.info(f"Found issue_type '{issue_type}' at line '{line_ctr}'")
            elif line.lower().startswith("reference: https://"):
                reference = line.replace("Reference: ", "").strip()
                lookup["reference"] = reference
                logging.info(f"Found reference '{reference}' at line '{line_ctr}'")


    if line_ctr > 0:
        logging.info(f"Read '{line_ctr}' lines from file '{infile}'")
    else:
        logging.info("Did not read any lines from file '{infile}'")

    display_summary_details(exclude, lookup, infile, verbose)

def display_summary_details(
    exclude: str,
    lookup: Dict[str, str],
    infile: str,
    verbose: bool = constants.DEFAULT_VERBOSE
    ) -> None:
    """Display the summary details.

    Args:
        exclude (str): Comma-separated list fields to exclude from the summary details.
        lookup (Dict[str, str]): The lookup dictionary containing the field and value.
        infile (str): The README.md file to be analyzed.
        verbose (bool, optional): If True, more details to STDOUT. Defaults to constants.DEFAULT_VERBOSE.
    """
    exclude_list = None
    if exclude:
        exclude_list = [e.strip() for e in exclude.split(",")]

    for field in DEFAULT_ORDER:
        if exclude_list and field in exclude_list:
            logging.info(f"Excluding field '{field}'")
            continue
        if field in lookup:
            console.print(f"{field}: {lookup[field]}")
        else:
            if verbose:
                console.print(f"{field}: Not found")


def validate_verbose(ctx, param, value):
    """Validate the validate option.

    Args:
        ctx (Context): The click context.
        param (str): The parameter.
        value (bool): The value.

    Returns:
        bool: The value.
    """

    if value is None:
        click.secho("--verbose was not specified and therefore was set to 'True'", fg='yellow')
        return constants.DEFAULT_VERBOSE
    return value


@click.command()
@click.option('--exclude', help='Optional: Comma-separated list fields to exclude from the summary details.')
@click.option('--infile', help='Required: The README.md file to be analyzed.')
@click.option('--logfile', help="Optional: The log file.")
@click.option('--outdir', help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'.")
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.", callback=validate_verbose)
def main(
    exclude: str,
    infile: str,
    logfile: Optional[str],
    outdir: Optional[str],
    verbose: Optional[bool]
    ):
    """Search for Jira README.md, parse the file and output summary details."""


    error_ctr = 0

    if infile is None:
        print_red("--infile was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print_red("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    check_infile_status(infile, "md")

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
        verbose = constants.DEFAULT_VERBOSE
        print_yellow(f"--verbose was not specified and therefore was set to '{verbose}'")


    logging.basicConfig(
        filename=logfile,
        format=constants.LOGGING_FORMAT,
        level=constants.LOG_LEVEL
    )

    process_readme(
        exclude,
        infile,
        logfile,
        outdir,
        verbose=constants.DEFAULT_VERBOSE
    )

    if verbose:
        console.print(f"The log file is '{logfile}'.")
        print_green(f"Execution of '{os.path.abspath(__file__)}' completed.")

if __name__ == '__main__':
    main()
