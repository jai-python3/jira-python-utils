# -*- coding: utf-8 -*-
"""Get the JIRA issue details."""
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
@click.option('--credential_file', help='credential file containing username and password (default is $HOME/.jira/credentials.txt)')
@click.argument('issue')
def main(credential_file: str, issue: str):
    """ISSUE : string - the JIRA issue identifier e.g.: RA-478"""

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    if issue is None:
        error_console.print("issue was not specified")
        sys.exit(1)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    jira_issue = auth_jira.issue(issue)
    summary = jira_issue.fields.summary
    desc = jira_issue.fields.description
    issue_type = jira_issue.fields.issuetype.name
    assignee = jira_issue.fields.assignee.name
    priority = jira_issue.fields.priority.name
    status = jira_issue.fields.status.name

    console.print(f"summary '{summary}'")
    console.print(f"description'{desc}'")
    console.print(f"type '{issue_type}'")
    console.print(f"assignee '{assignee}'")
    console.print(f"status '{status}'")
    console.print(f"priority '{priority}'")


if __name__ == '__main__':
    main()
