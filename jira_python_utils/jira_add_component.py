# -*- coding: utf-8 -*-
import os
import sys
import click

from .helper import get_jira_url, get_auth
from .file_utils import check_infile_status

from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--issue', help='The JIRA issue')
@click.option('--comp', help='The JIRA component')
def main(credential_file, issue, comp):
    """Add component to JIRA issue."""

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE
    check_infile_status(credential_file)

    error_ctr = 0

    if issue is None:
        error_console.print("--issue was not specified")
        error_ctr += 1

    if comp is None:
        error_console.print("--comp was not specified")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    if auth_jira is None:
        error_console.print("Could not instantiate JIRA auth")
        sys.exit(1)

    console.print(f"Will attempt to add component '{comp}' to JIRA issue '{issue}'")

    try:

        i = auth_jira.issue(issue)
        if i is None:
            raise Exception(f"Could not retrieve issue object for issue '{issue}'")

        # comp = 'elio plasma resolve'
        i.fields.components.append({'name': comp})
        i.update(fields={'components': i.fields.components})

    except Error as e:
        error_console.print(f"Encountered some exception while attempting to add component '{comp}' to JIRA issue '{issue}': {e}")
        sys.exit(1)
    else:
        console.print("Added component '{comp}' to JIRA issue '{issue}'")


if __name__ == '__main__':
    main()
