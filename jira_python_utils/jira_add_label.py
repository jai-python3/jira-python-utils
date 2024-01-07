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

DEFAULT_LINK_TYPE = 'relates to'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--label', help='The child issue')
@click.option('--issue', help='The JIRA issue')
def main(credential_file: str, label: str, issue: str):

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

    if issue is None:
        error_console.print("--issue was not specified")
        error_ctr += 1

    if label is None:
        error_console.print("--label was not specified")
        error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    console.print(f"Will attempt to add label(s) '{label}' to JIRA issue '{issue}'")

    label_ctr = 0
    labels = label.split(',')

    try:

        i = auth_jira.issue(issue)

        if i is None:
            raise Exception(f"Could not retrieve issue object for issue '{issue}'")

        for label in labels:
            label_ctr += 1
            label = label.strip().replace(' ', '-')
            i.fields.labels.append(label)
        # i.fields.labels.append(u'change-control-form')
        i.update(fields={'labels': i.fields.labels})
        # i.update(labels=[label])

    except Error as e:
        if label_ctr == 1:
            error_console.print(f"Encountered some exception while attempting to add label '{label}' to issue '{issue}': {e}")
        else:
            error_console.print(f"Encountered some exception while attempting to add labels '{label}' to issue '{issue}': {e}")
        sys.exit(1)
    else:
        if label_ctr == 1:
            console.print(f"Added label '{label}' to issue '{issue}'")
        else:
            console.print(f"Added labels '{label}' to issue '{issue}'")


if __name__ == '__main__':
    main()
