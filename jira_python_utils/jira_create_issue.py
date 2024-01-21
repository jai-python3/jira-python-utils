# -*- coding: utf-8 -*-
"""Create a JIRA issue."""
import os
import sys
import click

from .helper import get_jira_url, get_auth, get_username
from .file_utils import check_infile_status

from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()

DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
)

DEFAULT_CREDENTIAL_FILE = os.path.join(
    os.getenv('HOME'),
    '.jira',
    'credentials.txt'
)

DEFAULT_ASSIGNEE = 'jsundaram'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--project', help='The JIRA project key')
@click.option('--summary', help='The summary i.e.: the title of the issue')
@click.option('--desc', help='The description of the issue')
@click.option('--issue_type', help='The issue type e.g.: bug')
@click.option('--assignee', help='The assignee')
def main(credential_file: str, project: str, summary: str, desc: str, issue_type: str, assignee: str):
    """Create a JIRA issue.

    Args:
        credential_file (str): The credential file containing username and password.
        project (str): The JIRA project key.
        summary (str): The summary i.e.: the title of the issue.
        desc (str): The description of the issue.
        issue_type (str): The issue type e.g.: bug.
        assignee (str): The assignee.
    """

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

    if project is None:
        error_console.print("--project was not specified")
        error_ctr += 1

    if summary is None:
        error_console.print("--summary was not specified")
        error_ctr += 1

    if issue_type is None:
        error_console.print("--issue_type was not specified")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if desc is None:
        desc = summary
        console.print(f"[bold yellow]--desc was not specified and therefore was set to '{desc}'[/]")

    if assignee is None:
        assignee = get_username(credential_file)
        console.print(f"[bold yellow]--assignee was not specified and therefore was set to '{assignee}'[/]")


    if issue_type.lower() == 'task':
        issue_type = 'Task'
    elif issue_type.lower() == 'bug':
        issue_type = 'Bug'
    elif issue_type.lower() == 'story':
        issue_type = 'Story'
    else:
        error_console.print(f"issue type '{issue_type}' is not supported")
        sys.exit(1)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    console.print(f"Will attempt to create a JIRA issue for project '{project}' summary '{summary}' type '{issue_type}' assignee '{assignee}' description '{desc}'")

    try:
        new_issue = auth_jira.create_issue(
            project={'key':project},
            summary=summary,
            issuetype={'name':issue_type},
            description=desc,
            assignee={'name':assignee}
        )

    except Error as e:
        error_console.print(f"Encountered some exception while attempting to create a new JIRA issue: '{e}'")
        sys.exit(1)
    else:
        console.print("Created new issue")
        console.print(new_issue)



if __name__ == '__main__':
    main()
