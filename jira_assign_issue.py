import os
import sys
import click

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'


@click.command()
@click.option('--credential_file', help='credential file containing username and password (default is $HOME/.jira/credentials.txt)')
@click.option('--assignee', help='username to be assigned to issue (default will be username specified in credential file)')
@click.argument('issue')
def main(credential_file, assignee, issue):
    """ISSUE : string - the JIRA issue identifier e.g.: RA-478
    """

    rest_url_file = DEFAULT_URL_FILE
    if not os.path.exists(rest_url_file):
        print("JIRA REST URL file '{}' does not exist".format(rest_url_file))
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            print("read the REST URL from file '{}'".format(rest_url_file))

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    if not os.path.exists(credential_file):
        print("JIRA credential file '{}' does not exist".format(credential_file))
        sys.exit(1)

    if issue is None:
        print("issue was not specified")
        sys.exit(1)

    with open(credential_file, 'r') as f:
        line = f.readline()
        (username, password) = line.split(':')
        print("read username and password from credentials file")

    if assignee is None:
        assignee = username

    auth_jira = JIRA(url, basic_auth=(username, password))

    if auth_jira is not None:
        print("Will attempt to assign issue '{}' to username '{}'".format(issue, assignee))
        auth_jira.assign_issue(issue, assignee)
        print("Assigned issue '{}' to username '{}'".format(issue, assignee))

    else:
        print("Could not instantiate JIRA for url '{}'".format(url))


if __name__ == '__main__':
    main()
