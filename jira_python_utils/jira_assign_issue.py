# -*- coding: utf-8 -*-
"""Assign a JIRA issue to a user."""
import os
import sys
import click

from .helper import get_jira_url, get_auth, get_username
from .file_utils import check_infile_status

from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'


@click.command()
@click.option('--credential_file', help=f"credential file containing username and password - default is '{DEFAULT_CREDENTIAL_FILE}")
@click.option('--assignee', help='username to be assigned to issue (default will be username specified in credential file)')
@click.argument('issue')
def main(credential_file: str, assignee: str, issue: str):
    """Assign a JIRA issue to a user.

    Args:
        credential_file (str): The credential file containing username and password.
        assignee (str): The Jira username to be assigned to the issue.
        issue (str): The Jira issue identifier e.g.: JP-478.
    """
    if issue is None:
        error_console.print("issue was not specified")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    if assignee is None:
        assignee = get_username(credential_file)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    if auth_jira is None:
        error_console.print("Could not instantiate JIRA auth for url")
        sys.exit(1)

    console.print(f"Will attempt to assign issue '{issue}' to username '{assignee}'")

    auth_jira.assign_issue(issue, assignee)

    console.print(f"Assigned issue '{issue}' to username '{assignee}'")


if __name__ == '__main__':
    main()
