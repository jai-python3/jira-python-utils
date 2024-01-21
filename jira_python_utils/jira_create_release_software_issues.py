# -*- coding: utf-8 -*-
"""Create a set of JIRA issues for a software release.

Raises:
    Exception: Raise if there is a problem emitted by the API.
"""
import os
import sys
import click

from jira import JIRA
from typing import List


DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

DEFAULT_ASSIGNEE = 'jsundaram'

DEFAULT_LINK_ISSUES = True

DEFAULT_PROJECT = 'RA'

g_url = None
g_auth_jira = None
g_project = None
g_assignee = None
g_codebase = None
g_version = None
g_server = None
g_component = None
g_parent_issue_id = None
g_issue_type = 'Task'
g_link_type = 'relates to'

g_issues = []


def create_issue_software_release():
    """Create a new JIRA issue for the 'software release'."""
    summary = f"software release for {g_codebase} {g_version} on {g_server}"
    description = f"Need to install software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['software-release', 'install-server:' + g_server, g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_test_cases_software():
    """Create a new JIRA issue for the 'test cases'."""
    summary = f"test cases for {g_codebase} {g_version}"
    description = f"Identify and collect test cases.\ncode-base: {g_codebase}\nversion: {g_version}"
    labels = ['test-cases', g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_install_software():
    """Create a new JIRA issue for the 'install software'."""
    summary = f"install software release for {g_codebase} {g_version} on {g_server}"
    description = f"Need to install software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['software-release', 'install-server:' + g_server, g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_establish_release_candidate():
    """Create a new JIRA issue for the 'establish release candidate'."""
    summary = f"establish next software release candidate for {g_codebase} {g_version}"
    description = f"Need to establish the next software release candidate.\ncode-base: {g_codebase}\nversion: {g_version}"
    labels = ['establish-release-candidate', g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_prepare_change_control():
    """Create a new JIRA issue for 'prepare change control'."""
    summary = f"prepare change control to install {g_codebase} {g_version} on {g_server}"
    description = f"Need to prepare a change control in 123Compliance and DocuSign to install a software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['prepare-change-control', 'install-server:' + g_server, g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def  create_issue_prepare_validation_docs():
    """Create a new JIRA issue for 'prepare validation documents'."""
    summary = f"prepare validation documents for {g_codebase} {g_version} on {g_server}"
    description = f"Need to prepare validation documents for a software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['prepare-validation-documents', g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_execute_validation_checks():
    """Create a new JIRA issue for 'execute validation checks'."""
    summary = f"execution validation checks for {g_codebase} {g_version} on {g_server}"
    description = f"Need to execute validation checks for a software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['execute-validation-checks', 'install-server:' + g_server, g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)


def create_issue_collect_release_documents():
    """Create a new JIRA issue for 'collect release documents'."""
    summary = f"collect release documents for {g_codebase} {g_version} on {g_server}"
    description = f"Need to prepare the binder coverpage and collect all release documents (change control and validation documents) for the software release.\ncode-base: {g_codebase}\nversion: {g_version}\nserver(s): {g_server}"
    labels = ['collect-release-documents', 'install-server:' + g_server, g_codebase + '-' + g_version, g_codebase]
    return create_issue(summary, description, labels)

# def create_issue(summary, desc, labels=None):
#     print("summary '{}'".format(summary))
#     print("description '{}'\n\n".format(desc))
#     if labels is not None:
#         print("Here are the labels:")
#         for label in labels:
#             print(label)
#     print("\n")
#     return 'ID1'


def create_issue(summary: str, description: str, labels: List[str] = None) -> None:
    """Create a new JIRA issue.

    Args:
        summary (str): The JIRA issue summary.
        description (str): The new JIRA issue description.
        labels (list): The labels that should be applied to the new JIRA issue.
    """
    if g_parent_issue_id is not None:
        description += "\nReference: " + g_parent_issue_id

    print(f"Will attempt to create a JIRA issue for project '{g_project}' summary '{summary}' type '{g_issue_type}' assignee '{g_assignee}' and description:\n{description}")

    try:
        new_issue = g_auth_jira.create_issue(
            project=g_project,
            summary=summary,
            issuetype={'name':g_issue_type},
            description=description,
            assignee={'name':g_assignee}
            )

    except Error as e:
        print(f"Encountered some exception while attempting to create a new JIRA issue: '{e}'")
        sys.exit(1)

    new_issue_id = new_issue.key
    new_issue_url = g_url + '/browse/' + new_issue_id
    print(f"\nCreated new issue with ID '{new_issue_id}'\n{new_issue_url}")

    if DEFAULT_LINK_ISSUES:

        if g_parent_issue_id is not None:

            print(f"Will attempt to link parent issue '{g_parent_issue_id}' to this issue '{new_issue_id}' with link type '{g_link_type}'")

            try:
                g_auth_jira.create_issue_link(
                    type=g_link_type,
                    inwardIssue=new_issue_id,
                    outwardIssue=g_parent_issue_id,
                    comment={
                        "body": f"Linking {new_issue_id} to {g_parent_issue_id}"
                    }
                )

            except Error as e:
                print(f"Encountered some exception while attempting to link this issue '{new_issue_id}' to parent issue '{g_parent_issue_id}' with link type '{g_link_type}': {e}")
                sys.exit(1)
            else:
                print(f"Linked this issue '{new_issue_id}' to parent issue '{g_parent_issue_id}' with link type '{g_link_type}'")

    if g_component is not None:

        try:

            i = g_auth_jira.issue(new_issue_id)
            if i is None:
                raise Exception(f"Could not retrieve issue object for issue '{new_issue_id}'")

            i.fields.components.append({'name': g_component})
            i.update(fields={'components': i.fields.components})

        except Error as e:
            print(f"Encountered some exception while attempting to add component '{g_component}' to JIRA issue '{new_issue_id}': {e}")
            sys.exit(1)
        else:
            print(f"Added component '{g_component}' to JIRA issue '{new_issue_id}'")

    if labels is not None:

        label_ctr = 0
        label_str = ",".join(labels)

        for label in labels:
            label_ctr += 1
            label = label.strip()
            label = label.replace(' ', '-')
            new_issue.fields.labels.append(label)

        try:
            new_issue.update(fields={'labels': new_issue.fields.labels})
        except Error as e:
            if label_ctr == 1:
                print(f"Encountered some exception while attempting to add label '{label_str}' to JIRA issue '{new_issue_id}': {e}")
            else:
                print(f"Encountered some exception while attempting to add labels '{label_str}' to JIRA issue '{new_issue_id}': {e}")

            sys.exit(1)
        else:
            if label_ctr == 1:
                print(f"Added label '{label_str}' to JIRA issue '{new_issue_id}'")
            else:
                print(f"Added labels '{label_str}' to JIRA issue '{new_issue_id}'")

    global g_issues
    g_issues.append(new_issue_id)

    return new_issue_id


@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--project', help='The JIRA project key')
@click.option('--codebase', help='The code-base')
@click.option('--version', help='The version of the code-base')
@click.option('--server', help='The server the code will be installed on')
@click.option('--assignee', help='The assignee')
@click.option('--component', help='The component')
@click.option('--all', is_flag=True, default=False)
def main(credential_file, project, codebase, version, server, assignee, component, all):
    """Create the standard set of JIRA issues.

    If executed with --all option, will create issues for all of the following:

        establish release candidate

        prepare change control

        install software

        prepare validation documents

        execute validation checks

        prepare test cases

        collect release documents
    """

    rest_url_file = DEFAULT_URL_FILE
    if not os.path.exists(rest_url_file):
        print("JIRA REST URL file '{}' does not exist".format(rest_url_file))
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            url = url.strip()
            print("read the REST URL from file '{}'".format(rest_url_file))

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    if not os.path.exists(credential_file):
        print("JIRA credential file '{}' does not exist".format(credential_file))
        sys.exit(1)

    error_ctr = 0

    if codebase is None:
        print("--codebase was not specified")
        error_ctr += 1

    if version is None:
        print("--version was not specified")
        error_ctr += 1

    if server is None:
        print("--server was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if project is None:
        project = DEFAULT_PROJECT
        print(f"--project was not specified and therefore was set to default '{project}'")

    if assignee is None:
        assignee = DEFAULT_ASSIGNEE
        print(f"--assignee was not specified and therefore was set to default '{assignee}'")

    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print(f"read username and password from credentials file default '{credential_file}'")

    auth_jira = JIRA(url, basic_auth=(username, password))
    if auth_jira is None:
        print(f"Could not instantiate JIRA for url '{url}'")
        sys.exit(1)

    global g_url
    g_url = url

    global g_auth_jira
    g_auth_jira = auth_jira

    global g_project
    g_project = project

    global g_assignee
    g_assignee = assignee

    global g_codebase
    g_codebase = codebase

    global g_version
    g_version = version

    global g_server
    g_server = server

    global g_component
    g_component = component

    parent_issue_id = create_issue_software_release()

    global g_parent_issue_id
    g_parent_issue_id = parent_issue_id

    if all:
        yes_or_no_all = None
        while yes_or_no_all is None or yes_or_no_all == "":
            print("\nWill create new JIRA issues ALL of the following?")
            print(" establish release candidate")
            print(" prepare change control")
            print(" install software")
            print(" prepare validation documents")
            print(" execute validation checks")
            print(" prepare test cases")
            print(" collect release documents")
            yes_or_no_all = input("\nCreate new JIRA issues ALL of those? [Y/n] ")

            if yes_or_no_all is None or yes_or_no_all == "":
                yes_or_no_all = 'Y'
            if yes_or_no_all == 'Y' or yes_or_no_all == 'y':
                create_issue_establish_release_candidate()
                create_issue_prepare_change_control()
                create_issue_install_software()
                create_issue_prepare_validation_docs()
                create_issue_execute_validation_checks()
                create_issue_test_cases_software()
                create_issue_collect_release_documents()

            else:
                print("Will not create new JIRA issues for ALL of those.")
    else:
        yes_or_no_1 = None
        while yes_or_no_1 is None or yes_or_no_1 == '':
            yes_or_no_1 = input("\nCreate new JIRA issue for 'establish release candidate'? [Y/n] ")
            if yes_or_no_1 is None or yes_or_no_1 == '':
                yes_or_no_1 = 'Y'
            if yes_or_no_1 == 'Y' or yes_or_no_1 == 'y':
                create_issue_establish_release_candidate()
            else:
                print("Will not create new JIRA issue for 'establish release candidate'")

        yes_or_no_2 = None
        while yes_or_no_2 is None or yes_or_no_2 == '':
            yes_or_no_2 = input("\nCreate new JIRA issue for 'prepare change control'? [Y/n] ")
            if yes_or_no_2 is None or yes_or_no_2 == '':
                yes_or_no_2 = 'Y'
            if yes_or_no_2 == 'Y' or yes_or_no_2 == 'y':
                create_issue_prepare_change_control()
            else:
                print("Will not create new JIRA issue for 'prepare change control'")

        yes_or_no_3 = None
        while yes_or_no_3 is None or yes_or_no_3 == '':
            yes_or_no_3 = input("\nCreate new JIRA issue for 'prepare validation documents'? [Y/n] ")
            if yes_or_no_3 is None or yes_or_no_3 == '':
                yes_or_no_3 = 'Y'
            if yes_or_no_3 == 'Y' or yes_or_no_3 == 'y':
                create_issue_prepare_validation_docs()
            else:
                print("Will not create new JIRA issue 'prepare validation documents'")

        yes_or_no_4 = None
        while yes_or_no_4 is None or yes_or_no_4 == '':
            yes_or_no_4 = input("\nCreate 'execute validation checks' JIRA issue? [Y/n] ")
            if yes_or_no_4 is None or yes_or_no_4 == '':
                yes_or_no_4 = 'Y'
            if yes_or_no_4 == 'Y' or yes_or_no_4 == 'y':
                create_issue_execute_validation_checks()
            else:
                print("Will not create 'execute validation checks' JIRA issue")

        yes_or_no_5 = None
        while yes_or_no_5 is None or yes_or_no_5 == '':
            yes_or_no_5 = input("\nCreate 'test cases' JIRA issue? [Y/n] ")
            if yes_or_no_5 is None or yes_or_no_5 == '':
                yes_or_no_5 = 'Y'
            if yes_or_no_5 == 'Y' or yes_or_no_5 == 'y':
                create_issue_test_cases_software()
            else:
                print("Will not create 'test cases' JIRA issue")

        yes_or_no_6 = None
        while yes_or_no_6 is None or yes_or_no_6 == '':
            yes_or_no_6 = input("\nCreate 'collect release documents' JIRA issue? [Y/n] ")
            if yes_or_no_6 is None or yes_or_no_6 == '':
                yes_or_no_6 = 'Y'
            if yes_or_no_6 == 'Y' or yes_or_no_6 == 'y':
                create_issue_collect_release_documents()
            else:
                print("Will not create 'collect release documents' JIRA issue")

    print("Remember to assign the epic link for these new JIRA issues:")
    for issue in g_issues:
        print(f"{issue}")


if __name__ == '__main__':
    main()
