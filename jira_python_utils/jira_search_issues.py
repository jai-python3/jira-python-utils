# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import sys
from datetime import datetime
from typing import Tuple

import click
import yaml
from colorama import Fore, Style
from jira import JIRA

# query = """"Epic Link" = RGCCIDM-118 AND assignee in (jaideep.sundaram)"""

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

TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.path.splitext(os.path.basename(__file__))[0],
    TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'conf/config.yaml'
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

# DEFAULT_ASSIGNEE = 'jaideep.sundaram'


def get_auth_jira(credential_file: str, url: str):
    """Instantiate the JIRA object.

    Args:
        credential_file (str): the credentials file
        url: the REST URL

    Returns:
        JIRA: The JIRA class instance
    """
    username, password = get_username_password(credential_file)

    options = {
        'server': url,
        'verify': False
    }

    print(f"options: {options}")

    auth_jira = JIRA(
        options=options,
        basic_auth=(username, password)
    )

    if auth_jira is None:
        print_red(f"Could not instantiate JIRA for url '{url}'")
        sys.exit(1)
    print("AAA")
    return auth_jira


def get_username_password(credential_file: str) -> Tuple[str,str]:
    """Parse the credential file and retrieve the username and password."""
    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        print("read username and password from credentials file '{}'".format(credential_file))
        return username, password


def get_rest_url(rest_url_file: str) -> str:
    with open(rest_url_file, 'r') as f:
        url = f.readline()
        url = url.strip()
        print("read the REST URL from file '{}'".format(rest_url_file))
    return url


def check_rest_url_file(rest_url_file: str) -> None:
    """Check the JIRA REST URL file."""
    if not os.path.exists(rest_url_file):
        print_red(f"JIRA REST URL file '{rest_url_file}' does not exist")
        sys.exit(1)

    if not os.path.isfile(rest_url_file):
        print_red(f"JIRA REST URLfile '{rest_url_file}' is not a regular file")
        sys.exit(1)

    if not rest_url_file.endswith(".txt"):
        print_red(
            f"JIRA REST URLfile '{rest_url_file}' does not have a .txt file extension"
        )
        sys.exit(1)
    if os.path.getsize(rest_url_file) == 0:
        print_red(f"JIRA REST URL file '{rest_url_file}' has no content")
        sys.exit(1)

        print("read the REST URL from file '{}'".format(rest_url_file))


def check_credential_file(credential_file: str) -> None:
    """Check the JIRA credential file.

    The file should contain a single line:
    username:password

    Args:
        credential_file (str): the path to the credential file
    """
    if not os.path.exists(credential_file):
        print_red(f"credential file '{credential_file}' does not exist")
        sys.exit(1)

    if not os.path.isfile(credential_file):
        print_red(f"credentialfile '{credential_file}' is not a regular file")
        sys.exit(1)

    if os.path.getsize(credential_file) == 0:
        print_red(f"credential file '{credential_file}' has no content")
        sys.exit(1)


def check_config_file(config_file: str) -> None:
    """Check the configuration file."""
    if not os.path.exists(config_file):
        print_red(f"configuration file '{config_file}' does not exist")
        sys.exit(1)

    if not os.path.isfile(config_file):
        print_red(f"configuration file '{config_file}' is not a regular file")
        sys.exit(1)

    if not config_file.endswith(".yaml"):
        print_red(
            f"configuration file '{config_file}' does not have a .yaml file extension"
        )
        sys.exit(1)

    if os.path.getsize(config_file) == 0:
        print_red(f"configuration file'{config_file}' has no content")
        sys.exit(1)


def print_red(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.RED + msg + Style.RESET_ALL)


def print_green(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.GREEN + msg + Style.RESET_ALL)


def print_yellow(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.

    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.YELLOW + msg + Style.RESET_ALL)


@click.command()
@click.option('--assignee', help='The assignee')
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--query', help='The Jira jql query string')
def main(assignee: str, config_file: str, credential_file: str, logfile: str, outdir: str, query: str):

    rest_url_file = DEFAULT_URL_FILE
    check_rest_url_file(rest_url_file)

    url = get_rest_url(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_credential_file(credential_file)

    error_ctr = 0

    # if not query:
    #     print("--query was not specified")
    #     error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        sys.exit(1)

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print_yellow(f"--outdir was not specified and therefore was set to '{outdir}'")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

        print_yellow(f"Created output directory '{outdir}'")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        print_yellow(f"--logfile was not specified and therefore was set to '{logfile}'")

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        print_yellow(f"--config_file was not specified and therefore was set to '{config_file}'")

    check_config_file(config_file)

    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    logging.info(f"Loading configuration from '{config_file}'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    if 'epics' not in config:
        print_red(f"'epics' section does not exist in configuration file '{config_file}'")
        sys.exit(1)

    if 'links' not in config['epics']:
        print_red(f"'links' section does not exist in the 'epics' section in the configuration file '{config_file}'")
        sys.exit(1)

    if assignee is None and 'assignee' in config:
        assignee = config['assignee']
        logging.info(f"Retrieved assignee '{assignee}' from the configuration file '{config_file}'")

    links = config['epics']['links']
    if links is None or links == '' or len(links) == 0:
        print_red(f"Did not find any epic links in the configuration file '{config_file}'")
        sys.exit(1)

    logging.info(f"Found '{len(links)}' epic links in the configuration file '{config_file}'")

    auth_jira = get_auth_jira(credential_file, url)

    for link in links:

        query = link['query']

        if assignee is not None:
            query = f"""{query} AND assignee in ({assignee})"""
            logging.info(f"Added assignee '{assignee}' to the query: {query}")

        name = link['name']
        logging.info(f"Will attempt to retrieve issues for epic '{name}' with query '{query}'")
        print(f"\n##Will attempt to retrieve issues for epic '{name}' with query '{query}'")
        # continue

        try:
            issues = auth_jira.search_issues(query)

        except Exception as e:
            print_red(f"Encountered some exception while attempting to query with JQL '{query}' : '{e}'")
            sys.exit(1)
        else:
            print("Query was successful")

        print(f"Found '{len(issues)}' issues")
        for issue in issues:
            print(issue)
            # assignee = jira_issue.fields.assignee.name
            print(f"summary '{issue.fields.summary}'")
            print(f"description '{issue.fields.description}'")
            print(f"issue_type '{issue.fields.issuetype.name}'")
            print(f"priority '{issue.fields.priority.name}'")
            print(f"status '{issue.fields.status.name}'")




if __name__ == '__main__':
    main()
