import os
import sys
import click

from jira import JIRA

DEFAULT_URL_FILE = os.path.dirname(__file__) + '/conf/jira_rest_url.txt'

DEFAULT_CREDENTIAL_FILE = os.environ['HOME'] + '/.jira/credentials.txt'

DEFAULT_LINK_TYPE = 'relates to'

@click.command()
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--label', help='The child issue')
@click.option('--issue', help='The JIRA issue')
def main(credential_file, label, issue):

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

    if label is None:
        print("--label was not specified")
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

    print("Will attempt to add label(s) '{}' to JIRA issue '{}'".format(label, issue))

    label_ctr = 0
    labels = label.split(',')

    try:

        i = auth_jira.issue(issue)

        if i is None:
            raise Exception("Could not retrieve issue object for issue '{}'".format(issue))

        for l in labels:
            label_ctr += 1
            l = l.strip()
            l = l.replace(' ', '-')
            i.fields.labels.append(l)
        # i.fields.labels.append(u'change-control-form')
        i.update(fields={'labels': i.fields.labels})
        # i.update(labels=[label])

    except Error as e:
        if label_ctr == 1:
            print("Encountered some exception while attempting to add label '{}' to issue '{}': {}".format(label, issue, e))
        else:
            print("Encountered some exception while attempting to add labels '{}' to issue '{}': {}".format(label, issue, e))

        sys.exit(1)
    else:
        if label_ctr == 1:
            print("Added label '{}' to issue '{}'".format(label, issue))
        else:
            print("Added labels '{}' to issue '{}'".format(label, issue))




if __name__ == '__main__':
    main()
