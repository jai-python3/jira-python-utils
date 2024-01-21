# -*- coding: utf-8 -*-
"""Link two JIRA issues together."""
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

DEFAULT_LINK_TYPE = 'relates to'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--child_issue', help='The child issue')
@click.option('--parent_issue', help='The parent issue')
@click.option('--link_type', help='The type of link')
def main(credential_file: str, child_issue: str, parent_issue: str, link_type: str):
    """Link two JIRA issues together.

    Args:
        credential_file (str): The credential file containing username and password.
        child_issue (str): The child issue.
        parent_issue (str): The parent issue.
        link_type (str): The type of link.
    """

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

    if child_issue is None:
        error_console.print("--child_issue was not specified")
        error_ctr += 1

    if parent_issue is None:
        error_console.print("--parent_issue was not specified")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if link_type is None:
        link_type = DEFAULT_LINK_TYPE
        console.print(f"--link_type was not specified and therefore was set to default '{link_type}'")

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    console.print(f"Will attempt to link JIRA issue '{child_issue}' to '{parent_issue}' with link type '{link_type}'")

    try:

        auth_jira.create_issue_link(
            type=link_type,
            inwardIssue=child_issue,
            outwardIssue=parent_issue,
            comment={
                "body": f"Linking {child_issue} to {parent_issue}"
            }
        )

    except Error as e:
        error_console.print(f"Encountered some exception while attempting to link '{child_issue}' to '{parent_issue}' with link type '{link_type}': {e}")
        sys.exit(1)
    else:
        console.print(f"Linked '{child_issue}' to '{parent_issue}' with link type '{link_type}'")


if __name__ == '__main__':
    main()
