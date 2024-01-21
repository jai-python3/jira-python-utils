# -*- coding: utf-8 -*-
"""Retrieve issues from Jira using JQL."""
import click
import logging
import os
import pathlib
import sys
import yaml

from datetime import datetime
from jira import JIRA
from typing import Optional, Tuple


from file_utils import check_infile_status
from helper import get_rest_url, get_auth
from console_helper import print_yellow, print_red, print_green

# query = """"Epic Link" = RGCCIDM-118 AND assignee in (jaideep.sundaram)"""

DEFAULT_PROJECT = "jira-python-utils"

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
    '/tmp',
    os.getenv("USER"),
    DEFAULT_PROJECT,
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


@click.command()
@click.option('--assignee', help='The assignee')
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--query', help='The Jira jql query string')
def main(assignee: str, config_file: Optional[str], credential_file: Optional[str], logfile: Optional[str], outdir: Optional[str], query: str):
    """Retrieve issues from Jira using JQL.

    Args:
        assignee (str): The assignee.
        config_file (str): The configuration file.
        credential_file (str): The credential file.
        logfile (str): The log file.
        outdir (str): The output directory.
        query (str): The Jira jql query string.
    """

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file, "txt")

    url = get_rest_url(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

    # if not query:
    #     print("--query was not specified")
    #     error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        click.echo(click.get_current_context().get_help())
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

    check_infile_status(config_file, "yaml")

    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

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

    auth_jira = get_auth(credential_file, url)

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

        print_green(f"Found '{len(issues)}' issues")
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
