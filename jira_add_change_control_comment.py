# -*- coding: utf-8 -*-
import os
import sys
import click
import json

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

DEFAULT_CONFIG_FILE = os.environ['HOME'] + '/.jira/change_control_config.json'

DEFAULT_INTERACTIVE_MODE = False


@click.command()
@click.option('--change_control_id', help='The change control identifier')
@click.option('--credential_file', help='The credential file containing username and password (default is $HOME/.jira/credentials.txt)')
@click.option('--config_file', help='The config ini file (default is $HOME/.jira/change_control_config.json)')
@click.option('--compliance123_base_url', help='The 123Compliance URL base for change control')
@click.option('--docusign_base_url', help='The DocuSign URL base for the change control')
@click.option('--issue', help='The JIRA issue identifier e.g.: JP-478')
@click.option('--interactive', is_flag=True, help='Run in interactive mode')
def main(change_control_id, credential_file, config_file, compliance123_base_url, docusign_base_url, issue, interactive):
    """Will insert a comment in the specified JIRA issue like this: Change
    control [CR-01958|123Compliance_root_URL/base_URL_for_this_change_control/]
    has been prepared in 123Compliance.

    Change control has been prepared in DocuSign and sent to the following individuals for signatures:

    * [~person1_jira_alias]
    * [~person2_jira_alias]
    * [~person3_jira_alias]

    Reference:
    DocuSign_root_URL/base_URL_for_this_change_control
    """

    rest_url_file = DEFAULT_URL_FILE

    docusign_root_url = None
    compliance123_root_url = None
    signers_list = []

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        print("--config_file was not specified and therefore was set to '{}'".format(config_file))

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE
        print("--credential_file was not specified and therefore was set to '{}'".format(credential_file))

    if interactive is None:
        interactive = DEFAULT_INTERACTIVE_MODE
        print("--interactive was not specified and therefore was set to '{}'".format(interactive))

    error_ctr = 0

    if issue is None:
        if not interactive:
            print("--issue was not specified")
            error_ctr += 1

    if change_control_id is None:
        if not interactive:
            print("--change_control_id was not specified")
            error_ctr += 1

    if compliance123_base_url is None:
        if not interactive:
            print("--compliance123_base_url was not specified")
            error_ctr += 1

    if docusign_base_url is None:
        if not interactive:
            print("--docusign_base_url was not specified")
            error_ctr += 1

    if error_ctr > 0:
        print("Required command-line parameters were not specified")
        sys.exit(1)

    if not os.path.exists(rest_url_file):
        print("JIRA REST URL file '{}' does not exist".format(rest_url_file))
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            url = url.strip()
            print("read the REST URL from file '{}'".format(rest_url_file))

    if not os.path.exists(credential_file):
        print("JIRA credential file '{}' does not exist".format(credential_file))
        sys.exit(1)

    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file")

    if not os.path.exists(config_file):
        raise Exception("config file '{}' does not exist".format(config_file))

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
            print("Invalid value")
            sys.exit(1)

    if compliance123_base_url is None:
        compliance123_base_url = input("What is the 123Compliance base URL? ")
        if compliance123_base_url is None or compliance123_base_url == '':
            print("Invalid value")
            sys.exit(1)

    if docusign_base_url is None:
        docusign_base_url = input("What is the DocuSign base URL? ")
        if docusign_base_url is None or docusign_base_url == '':
            print("Invalid value")
            sys.exit(1)

    if compliance123_base_url.startswith('http'):
        compliance123_full_url = compliance123_base_url
    else:
        compliance123_full_url = compliance123_root_url + '/' + compliance123_base_url

    if docusign_base_url.startswith('http'):
        docusign_full_url = docusign_base_url
    else:
        docusign_full_url = docusign_root_url + '/' + docusign_base_url

    comment = "Change control [{}|{}] has been prepared in 123Compliance.\n\n".format(change_control_id, compliance123_full_url)
    comment += "The change control has been prepared in DocuSign and sent to the following individuals for signatures:\n"
    for signer in signers_list:
        comment += "* [~{}]\n".format(signer)
    comment += "\nReference:\n{}".format(docusign_full_url)

    print("\nWill attempt to authenticate with JIRA")
    auth_jira = JIRA(url, basic_auth=(username, password))

    if auth_jira is not None:
        print("Will attempt to add the following to issue '{}':\n\n{}".format(issue, comment))
        auth_jira.add_comment(issue, comment)
        print("\nDone")

    else:
        print("Could not instantiate JIRA for url '{}'".format(url))


if __name__ == '__main__':
    main()
