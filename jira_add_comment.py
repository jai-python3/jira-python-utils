# -*- coding: utf-8 -*-
import os
import sys

import click
from jira import JIRA

DEFAULT_URL_FILE = os.environ['HOME'] + '/.jira/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'



def get_jira_url() -> str:
    rest_url_file = DEFAULT_URL_FILE
    if not os.path.exists(rest_url_file):
        print("JIRA REST URL file '{}' does not exist".format(rest_url_file))
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            url = url.strip()
            print("read the REST URL from file '{}'".format(rest_url_file))
    print(f"Retrieved URL '{url}' from '{rest_url_file}'")
    return url


@click.command()
@click.option('--credential_file', help='credential file containing username and password (default is $HOME/.jira/credentials.txt)')
@click.option('--comment', help='text to be added as a comment to the specified issue')
@click.option('--comment_file', help='file containing the text to be added as a comment to the specified issue')
@click.argument('issue')
def main(credential_file, comment, comment_file, issue):
    """ISSUE : string - the JIRA issue identifier e.g.: RA-478
    """

    if comment is None and comment_file is None:
        print("--comment and --comment_file were not specified")
        sys.exit(1)

    if comment == '':
        print("You must provide some test for the comment")
        sys.exit(1)

    url = get_jira_url()

    if comment_file is not None:
        with open(comment_file, 'r') as cf:
            comment = cf.read()

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
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file")

    options = {
        'server': url,
        'verify': False
    }

    auth_jira = JIRA(options=options, basic_auth=(username, password))
    if auth_jira is None:
        print("Could not instantiate JIRA for url '{}'".format(url))
        sys.exit(1)

    if auth_jira is not None:
        print("Will attempt to add comment '{}' to issue '{}'".format(comment, issue))
        auth_jira.add_comment(issue, comment)
        print("Added comment '{}' to issue '{}'".format(comment, issue))

    else:
        print("Could not instantiate JIRA for url '{}'".format(url))


if __name__ == '__main__':
    main()
