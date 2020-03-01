import os
import sys
import click

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--issue', help='The JIRA issue')
@click.option('--comp', help='The JIRA component')
def main(credential_file, issue, comp):
    """Add component to JIRA issue
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

    if issue is None:
        print("--issue was not specified")
        error_ctr += 1

    if comp is None:
        print("--comp was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        sys.exit(1)


    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file '{}'".format(credential_file))

    auth_jira = JIRA(url, basic_auth=(username, password))

    if auth_jira is None:
        print("Could not instantiate JIRA for url '{}'".format(url))
        sys.exit(1)


    print("Will attempt to add component '{}' to JIRA issue '{}'".format(comp, issue))

    try:

        i = auth_jira.issue(issue)
        if i is None:
            raise Exception("Could not retrieve issue object for issue '{}'".format(issue))

        # comp = 'elio plasma resolve'
        i.fields.components.append({'name': comp})
        i.update(fields={'components': i.fields.components})

    except Error as e:
        print("Encountered some exception while attempting to add component '{}' to JIRA issue '{}': {}".format(comp, issue, e))
        sys.exit(1)
    else:
        print("Added component '{}' to JIRA issue '{}'".format(comp, issue))


if __name__ == '__main__':
    main()
