# -*- coding: utf-8 -*-
"""Add a comment to the Jira issue."""
import os
import sys

import click

from .helper import get_jira_url, get_auth
from .file_utils import check_infile_status

from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_URL_FILE = os.environ['HOME'] + '/.jira/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'


@click.command()
@click.option('--credential_file', help=f"credential file containing username and password - default is '{DEFAULT_CREDENTIAL_FILE}'")
@click.option('--comment', help='text to be added as a comment to the specified issue')
@click.option('--comment_file', help='file containing the text to be added as a comment to the specified issue')
@click.argument('issue')
def main(credential_file: str, comment: str, comment_file: str, issue: str):
    """Add a comment to the Jira issue.

    Args:
        credential_file (str): credential file containing username and password - default is '~/.jira/credentials.txt'
        comment (str): text to be added as a comment to the specified issue
        comment_file (str): file containing the text to be added as a comment to the specified issue
        issue (str): the issue id
    """

    error_ctr = 0

    if issue is None:
        error_console.print("issue was not specified")
        error_ctr += 1

    if comment is None and comment_file is None:
        error_console.print("--comment and --comment_file were not specified")
        error_ctr += 1

    if comment == '':
        error_console.print("You must provide some text for the comment")
        error_ctr += 1

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    url = get_jira_url(DEFAULT_URL_FILE)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    if comment_file is not None:
        check_infile_status(comment_file)
        with open(comment_file, 'r') as cf:
            comment = cf.read()

    auth_jira = get_auth(credential_file, url)

    if auth_jira is None:
        error_console.print("Could not instantiate JIRA for url '{}'".format(url))
        sys.exit(1)

    console.print(f"Will attempt to add comment '{comment}' to issue '{issue}'")

    auth_jira.add_comment(issue, comment)

    console.print(f"Added comment '{comment}' to issue '{issue}'")


if __name__ == '__main__':
    main()
