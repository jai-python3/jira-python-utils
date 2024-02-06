#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import click
import pathlib
import logging
import pathlib

from rich.console import Console
from datetime import datetime
from typing import List

DEFAULT_PROJECT = "jira-python-utils"

EXECUTABLES = [
    "annotate-readme",
    "bitbucket-reformat-merge-comment",
    "jira-add-change-control-comment",
    "jira-add-comment",
    "jira-add-component",
    "jira-add-label",
    "jira-assign-issue",
    "jira-convert-task-session-script-to-readme",
    "jira-create-issue",
    "jira-create-release-software-issues",
    "jira-epics-to-confluence-tables",
    "jira-get-issue-details",
    "jira-initiate-workspace",
    "jira-link-issues",
    "jira-remove-watcher",
    "jira-search-issues",
    "jira-start-task",
    "jira-sync-workspace",
    "jira-to-confluence-weekly-progress-report",
    "jira-scan-jira-dirs",
    "search-readme"
]

DEFAULT_ALIAS_PREFIX = "jj"

DEFAULT_TIMESTAMP = str(datetime.today().strftime("%Y-%m-%d-%H%M%S"))

DEFAULT_OUTDIR = os.path.join(
    "/tmp/",
    os.getenv("USER"),
    DEFAULT_PROJECT,
    os.path.basename(__file__),
    DEFAULT_TIMESTAMP,
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = True


error_console = Console(stderr=True, style="bold red")

console = Console()


def create_aliases_file(wrapper_scripts: List[str], outdir: str, prefix: str = DEFAULT_ALIAS_PREFIX) -> None:
    """Create a file with aliases for the wrapper scripts.

    Args:
        wrapper_scripts (List[str]): list of wrapper scripts
        outdir (str): output directory
    """
    outfile = os.path.join(outdir, f"{DEFAULT_PROJECT}-aliases.txt")

    with open(outfile, 'w') as of:
        of.write(f"## method-created: {os.path.abspath(__file__)}\n")
        of.write(f"## date-created: {str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))}\n")
        of.write(f"## created-by: {os.environ.get('USER')}\n")
        for wrapper_script in wrapper_scripts:
            alias = os.path.basename(wrapper_script).replace(".sh", "")
            line = f"alias {prefix}-{alias}='bash {wrapper_script}'"
            of.write(f"{line}\n")

    logging.info(f"Wrote file '{outfile}'")
    print(f"Wrote file '{outfile}'")


def create_wrapper_script(infile: str, outdir: str) -> str:

    outfile = None
    if not infile.endswith(".sh"):
        outfile = os.path.join(outdir, os.path.basename(infile) + ".sh")

    with open(outfile, "w") as of:
        of.write("#!/bin/bash\n")
        # of.write(
        #     'SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"\n'
        # )

        bin_dir = os.path.dirname(__file__)
        activate_script = os.path.join(bin_dir, "activate")
        of.write(f"source {activate_script}\n")

        of.write(f"python {bin_dir}/{os.path.basename(infile)} \"$@\"")

    logging.info(f"Wrote wrapper shell script '{outfile}'")
    return outfile



@click.command()
@click.option(
    "--outdir",
    type=str,
    help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'",
)
@click.option(
    "--alias-prefix",
    type=str,
    help=f"Optional: The prefix to be applied to the aliases - default is '{DEFAULT_ALIAS_PREFIX}'",
)
def main(outdir: str, alias_prefix: str):
    """Create wrapper shell scripts and aliases."""
    error_ctr = 0

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if outdir is None:
        outdir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        console.print(f"[bold yellow]--outdir was not specified and therefore was set to '{outdir}'[/]")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        console.print(f"[bold yellow]Created output directory '{outdir}'[/]")

    if alias_prefix is None:
        alias_prefix = DEFAULT_ALIAS_PREFIX
        console.print(f"[bold yellow]--alias-prefix was not specified and therefore was set to '{alias_prefix}'[/]")

    wrapper_scripts = []

    for executable in EXECUTABLES:
        console_script = os.path.join(os.path.dirname(__file__), executable)
        if not os.path.exists(console_script):
            raise Exception(f"Console script '{console_script}' does not exist")
        wrapper_script = create_wrapper_script(console_script, outdir)
        wrapper_scripts.append(wrapper_script)

    create_aliases_file(wrapper_scripts, outdir, alias_prefix)

    console.print(f"[bold green]Execution of {os.path.abspath(__file__)} completed[/]")


if __name__ == "__main__":
    main()
