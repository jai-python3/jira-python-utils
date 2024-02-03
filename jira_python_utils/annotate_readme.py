# -*- coding: utf-8 -*-
"""Start a Jira task."""
import click
import logging
import os
import pathlib
import re
import sys

from datetime import datetime
from pathlib import Path
from rich.console import Console
from typing import Optional

from . import constants
from .file_utils import check_infile_status, backup_file
from .console_helper import print_yellow, print_red, print_green

error_console = Console(stderr=True, style="bold red")

console = Console()

DEFAULT_JIRA_BASE_URL = "https://jira.com/browse/"

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP
)

def get_date(date_type: str, current_date: str = "YYYY-MM-DD") -> str:
    ans = input(f"{date_type}? ({current_date}): ")
    if ans == "":
        return datetime.now().strftime("%Y-%m-%d")
    return ans


def get_status() -> str:
    status = input("Status? (e.g. In-Progress, Done, Pending, Blocked, etc.): ")
    if status == "":
        return "Pending"
    return status


def get_issue_type() -> str:
    issue_type = input("Issue-type? (e.g. new-feature, bugfix, data-management, config-management, etc.): ")
    if issue_type == "":
        return "TBD"
    return issue_type

def annotate_readme(
        jira_id: str,
        logfile : str,
        outdir: str,
        readme: str,
        jira_base_url: str = DEFAULT_JIRA_BASE_URL,
        verbose: bool = constants.DEFAULT_VERBOSE
    ) -> None:
    """Annotate the README.md file.

    Args:
        jira_id (str): The Jira ticket identifier.
        logfile (str): The log file.
        outdir (str): The output directory.
        readme (str): The README.md to be annotated/updated.
        verbose (bool): The verbose flag.
    """
    logging.info(f"Will backup '{readme}'")

    bakfile = backup_file(readme)
    # Read all lines in the file to an array
    lines = []

    logging.info(f"Will attempt to read lines from '{bakfile}'")
    with open(bakfile, 'r') as infile:
        lines = infile.readlines()

    outlines = []
    current_step = 0

    # Expected header information
    jira_id_encountered = False
    jira_url_reference_encountered = False
    keywords_encountered = False
    codebase_encountered = False
    date_created_encountered = False
    due_date_encountered = False
    date_completed_encountered = False
    status_encountered = False
    issue_type_encountered = False

    jira_id_line = None
    jira_url_reference_line = None
    keywords_line = None
    codebase_line = None
    date_created_line = None
    due_date_line = None
    date_completed_line = None
    status_line = None
    issue_type_line = None

    line_ctr = 0

    for line in lines:
        line_ctr += 1
        if line_ctr == 1:
            if line.startswith("# Jira ID: "): # This should appear on the first line
                logging.info(f"Jira ID encountered on line {line_ctr}")
                jira_id_encountered = True
                jira_id_line = line
                continue

        elif line.lower().startswith("reference: "):
            logging.info(f"Reference encountered on line {line_ctr}")
            jira_url_reference_encountered = True
            jira_url_reference_line = line
            continue

        elif line.lower().startswith("keywords: "):
            logging.info(f"Keywords encountered on line {line_ctr}")
            keywords_encountered = True
            keywords_line = line
            continue

        elif line.lower().startswith("codebase: "):
            logging.info(f"Codebase encountered on line {line_ctr}")
            codebase_encountered = True
            codebase_line = line
            continue

        elif line.lower().startswith("date-created: "):
            logging.info(f"Date-created encountered on line {line_ctr}")
            date_created_encountered = True
            date_created_line = line
            continue

        elif line.lower().startswith("date-completed: "):
            logging.info(f"Date-completed encountered on line {line_ctr}")
            date_completed_encountered = True
            date_completed_line = line
            continue

        elif line.lower().startswith("due-date: "):
            logging.info(f"Due-date encountered on line {line_ctr}")
            due_date_encountered = True
            due_date_line = line
            continue

        elif line.lower().startswith("status: "):
            logging.info(f"Status encountered on line {line_ctr}")
            status_encountered = True
            status_line = line
            continue

        elif line.lower().startswith("issue-type: "):
            logging.info(f"Issue-type encountered on line {line_ctr}")
            issue_type_encountered = True
            issue_type_line = line
            continue

        # Use regex to check if line starts with ## Step and then a number
        elif re.match(r"## Step \d+", line):
            current_step += 1
            # Use regex to replace the step number with the Jira ID
            outline = re.sub(r"## Step \d+", f"## Step {current_step}", line)
            outlines.append(outline)

        elif line.startswith("## "):
            current_step += 1
            outline = line.replace("## ", f"## Step {current_step} - ")
            outlines.append(outline)
            continue
        else:
            outlines.append(line)
            continue

    logging.info(f"Will attempt to write annotated '{readme}'")

    with open(readme, 'w') as outfile:
        if not jira_id_encountered:
            outfile.write(f"# Jira ID: {jira_id}\n\n")
        else:
            outfile.write(f"{jira_id_line}")

        if not jira_url_reference_encountered:
            outfile.write(f"Reference: {jira_base_url}{jira_id}\n\n")
        else:
            outfile.write(f"{jira_url_reference_line}")

        if not keywords_encountered:
            keywords = get_keywords()
            keywords_str = ', '.join(keywords)
            outfile.write(f"Keywords: {keywords_str}\n\n")
        else:
            outfile.write(f"{keywords_line}")

        if not codebase_encountered:
            codebase = get_codebase()
            outfile.write(f"Codebase: {codebase}\n\n")
        else:
            outfile.write(f"{codebase_line}")

        current_date = None
        if not date_created_encountered:
            dt = get_date("date-created", current_date=current_date)
            outfile.write(f"date-created: {dt}\n\n")
            current_date = dt
        else:
            outfile.write(f"{date_created_line}")

        if not due_date_encountered:
            dt = get_date("due-date", current_date=current_date)
            outfile.write(f"due-date: {dt}\n\n")
            current_date = dt
        else:
            outfile.write(f"{due_date_line}")

        if not date_completed_encountered:
            dt = get_date("date-completed", current_date=current_date)
            outfile.write(f"date-completed: {dt}\n\n")
        else:
            outfile.write(f"{date_completed_line}")


        if not status_encountered:
            status = get_status()
            outfile.write(f"status: {status}\n\n")
        else:
            outfile.write(f"{status_line}")

        if not issue_type_encountered:
            issue_type = get_issue_type()
            outfile.write(f"issue-type: {issue_type}\n\n")
        else:
            outfile.write(f"{issue_type_line}")


        for line in outlines:
            outfile.write(line)

    if verbose:
        console.print(f"Wrote annotated '{readme}'")
        logging.info(f"Wrote annotated '{readme}'")


def get_keywords() -> list:
    """Prompt the user for the keywords.

    Returns:
        List[str]: The list of keywords.
    """
    keywords = []
    while True:
        keyword = click.prompt("Enter a keyword (or press Enter to end)", default="")
        if keyword == "":
            break
        keywords.append(keyword)
    return keywords


def get_codebase() -> str:
    """Prompt the user for the name of the codebase.

    Returns:
        str: Name of the codebase.
    """
    codebase = click.prompt("Enter the name of the codebase", default="")
    return codebase


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
@click.option('--jira_id', help='Required: The Jira ticket identifier')
@click.option('--logfile', help="Optional: The log file")
@click.option('--outdir', help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--readme', help='Required: The README.md to be annotated/updated')
@click.option('--verbose', is_flag=True, help=f"Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.", callback=validate_verbose)
def main(
    jira_id: str,
    logfile: Optional[str],
    outdir: Optional[str],
    readme: str,
    verbose: Optional[bool]
    ):
    """Annotate/update the README.md file."""

    error_ctr = 0

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if readme is None:
        print_red("--readme was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print_red("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    check_infile_status(readme, "md")

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

    annotate_readme(
        jira_id,
        logfile,
        outdir,
        readme,
        jira_base_url=DEFAULT_JIRA_BASE_URL,
        verbose=constants.DEFAULT_VERBOSE
    )

    if verbose:
        console.print(f"The log file is '{logfile}'.")
        print_green(f"Execution of '{os.path.abspath(__file__)}' completed.")

if __name__ == '__main__':
    main()
