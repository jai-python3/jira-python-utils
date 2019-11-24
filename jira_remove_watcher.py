import os
import sys
import click

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'


@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.argument('issue')
def main(credential_file, issue):

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

    auth_jira = JIRA(url, basic_auth=(username, password))

    if auth_jira is not None:
        print("Will attempt to remove username '{}' from issue '{}'".format(username, issue))
        auth_jira.remove_watcher(issue, username)
        print("Removed username '{}' from watchers for issue '{}'".format(username, issue))
    
    else:
        print("Could not instantiate JIRA for url '{}'".format(url))


if __name__ == '__main__':
    main()
