# -*- coding: utf-8 -*-
"""Remove account from JIRA watchers."""
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
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--username', help='the username - default will be retrieve from the credential file')
@click.argument('issue')
def main(credential_file: str, username: str, issue: str):
    """Remove account from JIRA watchers.

    Args:
        credential_file (str): The credential file containing username and password.
        username (str): The username that should be removed from watchers - default will be retrieve from the credential file.
        issue (str): The Jira issue identifier e.g.: RA-478
    """

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    if issue is None:
        error_console.print("issue was not specified")
        sys.exit(1)

    if username is None:
        username = get_username(credential_file)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    console.print(f"Will attempt to remove username '{username}' from issue '{issue}'")

    auth_jira.remove_watcher(issue, username)

    console.print(f"Removed username '{username}' from watchers for issue '{issue}'")


if __name__ == '__main__':
    main()
