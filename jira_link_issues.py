import os
import sys
import click

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

DEFAULT_LINK_TYPE = 'relates to'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--child_issue', help='The child issue')
@click.option('--parent_issue', help='The parent issue')
@click.option('--link_type', help='The type of link')
def main(credential_file, child_issue, parent_issue, link_type):

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

    if child_issue is None:
        print("--child_issue was not specified")
        error_ctr += 1

    if parent_issue is None:
        print("--parent_issue was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        sys.exit(1)

    if link_type is None:
        link_type = DEFAULT_LINK_TYPE
        print("--link_type was not specified and therefore was set to default '{}'".format(link_type))

    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file '{}'".format(credential_file))

    auth_jira = JIRA(url, basic_auth=(username, password))

    if auth_jira is None:
        print("Could not instantiate JIRA for url '{}'".format(url))
        sys.exit(1)

    print("Will attempt to link JIRA issue '{}' to '{}' with link type '{}'".format(child_issue, parent_issue, link_type))

    try:

        auth_jira.create_issue_link(
            type=link_type,
            inwardIssue=child_issue,
            outwardIssue=parent_issue,
            comment={
                "body": "Linking {} to {}".format(child_issue, parent_issue)
            }
        )

    except Error as e:
        print("Encountered some exception while attempting to link '{}' to '{}' with link type '{}': {}".format(child_issue, parent_issue, link_type, e))
        sys.exit(1)
    else:
        print("Linked '{}' to '{}' with link type '{}'".format(child_issue, parent_issue, link_type))



if __name__ == '__main__':
    main()
