import os
import sys

import click
from jira import JIRA

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
def main(credential_file, project, summary, desc, issue_type, assignee):

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

    if project is None:
        print("--project was not specified")
        error_ctr += 1

    if summary is None:
        print("--summary was not specified")
        error_ctr += 1

    if issue_type is None:
        print("--issue_type was not specified")
        error_ctr += 1

    if desc is None:
        desc = summary
        print("--desc was not specified and therefore was set to '{}'".format(desc))

    if assignee is None:
        assignee = DEFAULT_ASSIGNEE
        print("--assignee was not specified and therefore was set to '{}'".format(assignee))


    if error_ctr > 0:
        print("Required parameter(s) not defined")
        sys.exit(1)

    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file '{}'".format(credential_file))

    if issue_type.lower() == 'task':
        issue_type = 'Task'
    elif issue_type.lower() == 'bug':
        issue_type = 'Bug'
    elif issue_type.lower() == 'story':
        issue_type = 'Story'
    else:
        print(f"issue type '{issue_type}' is not supported")
        sys.exit(1)

    options = {
        'server': url, 
        'verify': False
    }

    auth_jira = JIRA(options=options, basic_auth=(username, password))
    if auth_jira is None:
        print("Could not instantiate JIRA for url '{}'".format(url))
        sys.exit(1)

    print("Will attempt to create a JIRA issue for project '{}' summary '{}' type '{}' assignee '{}' description '{}'".format(project, summary, issue_type, assignee, desc))

    try:
        new_issue = auth_jira.create_issue(
            project={'key':project}, 
            summary=summary, 
            issuetype={'name':issue_type}, 
            description=desc, 
            assignee={'name':assignee}
        )

    except Error as e:
        print("Encountered some exception while attempting to create a new JIRA issue: '{}'".format(e))
        sys.exit(1)
    else:
        print("Created new issue")
        print(new_issue)



if __name__ == '__main__':
    main()
