# -*- coding: utf-8 -*-
"""Add a comment to a JIRA issue with the change control information."""
import os
import sys
import click
import json

from typing import Optional


from .helper import get_jira_url, get_auth
from .file_utils import check_infile_status

from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()


DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

DEFAULT_CONFIG_FILE = os.environ['HOME'] + '/.jira/change_control_config.json'

DEFAULT_INTERACTIVE_MODE = False


@click.command()
@click.option('--change_control_id', help='The change control identifier')
@click.option('--credential_file', help=f"The credential file containing username and password - default is '{DEFAULT_CREDENTIAL_FILE}'")
@click.option('--config_file', help=f"The config ini file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--compliance123_base_url', help='The 123Compliance URL base for change control')
@click.option('--docusign_base_url', help='The DocuSign URL base for the change control')
@click.option('--issue', help='The JIRA issue identifier e.g.: JP-478')
@click.option('--interactive', is_flag=True, help='Run in interactive mode')
def main(change_control_id: str, credential_file: Optional[str], config_file: Optional[str], compliance123_base_url: str, docusign_base_url: str, issue: str, interactive: Optional[bool]):
    """Add change control content to a Jira ticket.

    Args:
        change_control_id (str): The change control identifier.
        credential_file (Optional[str]): The credential file containing username and password.
        config_file (Optional[str]): The config ini file.
        compliance123_base_url (str): The 123Compliance URL base for change control.
        docusign_base_url (str): The DocuSign URL base for the change control.
        issue (str): The JIRA issue identifier e.g.: JP-478.
        interactive (Optional[bool]): Run in interactive mode.

    This will insert a comment in the specified JIRA issue like this:
    Change control [CR-01958|123Compliance_root_URL/base_URL_for_this_change_control/]
    has been prepared in 123Compliance.

    Change control has been prepared in DocuSign and sent to the following individuals for signatures:

    * [~person1_jira_alias]
    * [~person2_jira_alias]
    * [~person3_jira_alias]

    Reference:
    DocuSign_root_URL/base_URL_for_this_change_control
    """

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file)

    docusign_root_url = None
    compliance123_root_url = None
    signers_list = []

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        console.print(f"[bold yellow]--config_file was not specified and therefore was set to '{config_file}'[/]")

    check_infile_status(config_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE
        console.print("[bold yellow]--credential_file was not specified and therefore was set to '{credential_file}'[/]")

    check_infile_status(credential_file)

    if interactive is None:
        interactive = DEFAULT_INTERACTIVE_MODE
        console.print("[bold yellow]--interactive was not specified and therefore was set to '{interactive}'[/]")

    error_ctr = 0

    if issue is None:
        if not interactive:
            error_console.print("--issue was not specified")
            error_ctr += 1

    if change_control_id is None:
        if not interactive:
            error_console.print("--change_control_id was not specified")
            error_ctr += 1

    if compliance123_base_url is None:
        if not interactive:
            error_console.print("--compliance123_base_url was not specified")
            error_ctr += 1

    if docusign_base_url is None:
        if not interactive:
            error_console.print("--docusign_base_url was not specified")
            error_ctr += 1

    if error_ctr > 0:
        error_console.print("Required command-line parameters were not specified")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)


    with open(config_file, 'r') as json_file:
        text = json_file.read()
        json_data = json.loads(text)

        for key in json_data:
            val = json_data[key]
            if key == '123compliance_root_url':
                compliance123_root_url = val
            elif key == 'docusign_root_url':
                docusign_root_url = val
            elif key == 'signers_list':
                signers_list = val

    if change_control_id is None:
        change_control_id = input("What is the change control ID? ")
        if change_control_id is None or change_control_id == '':
            error_console.print("Invalid value")
            sys.exit(1)

    if compliance123_base_url is None:
        compliance123_base_url = input("What is the 123Compliance base URL? ")
        if compliance123_base_url is None or compliance123_base_url == '':
            error_console.print("Invalid value")
            sys.exit(1)

    if docusign_base_url is None:
        docusign_base_url = input("What is the DocuSign base URL? ")
        if docusign_base_url is None or docusign_base_url == '':
            error_console.print("Invalid value")
            sys.exit(1)

    if compliance123_base_url.startswith('http'):
        compliance123_full_url = compliance123_base_url
    else:
        compliance123_full_url = compliance123_root_url + '/' + compliance123_base_url

    if docusign_base_url.startswith('http'):
        docusign_full_url = docusign_base_url
    else:
        docusign_full_url = docusign_root_url + '/' + docusign_base_url

    comment = f"Change control [{change_control_id}|{compliance123_full_url}] has been prepared in 123Compliance.\n\n"
    comment += "The change control has been prepared in DocuSign and sent to the following individuals for signatures:\n"
    for signer in signers_list:
        comment += f"* [~{signer}]\n"
    comment += f"\nReference:\n{docusign_full_url}"

    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))

    console.print(f"Will attempt to add the following to issue '{issue}':\n\n{comment}")

    auth_jira.add_comment(issue, comment)

    console.print("\n[bold green]Done[/]")


if __name__ == '__main__':
    main()
