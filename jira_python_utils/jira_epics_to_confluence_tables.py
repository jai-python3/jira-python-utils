# -*- coding: utf-8 -*-
import click
import logging
import os
import pathlib
import sys
import yaml

from datetime import datetime
from typing import Any, Dict, List, Tuple

from .file_utils import check_infile_status
from .console_helper import print_red, print_yellow
from .helper import get_auth_jira, get_rest_url
from .confluence.manager import Manager as ConfluenceManager

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
    '/tmp/',
    os.getenv("USER"),
    DEFAULT_PROJECT,
    os.path.splitext(os.path.basename(__file__))[0],
    TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "conf",
    "jira_epics_config.yaml"
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


def get_jira_epic_links(config, config_file: str) -> List[Dict[str, str]]:
    """Get the JIRA epic links from the configuration file.

    Args:
        config (_type_): The configuration object.
        config_file (str): The configuration file.

    Returns:
        List[Dict[str, str]]: The list of epic links.
    """

    if 'epics' not in config['jira']:
        print_red(f"'epics' section does not exist in configuration file '{config_file}'")
        sys.exit(1)

    if 'links' not in config['jira']['epics']:
        print_red(f"'links' section does not exist in the 'epics' section in the configuration file '{config_file}'")
        sys.exit(1)

    links = config['jira']['epics']['links']
    if links is None or links == '' or len(links) == 0:
        print_red(f"Did not find any epic links in the configuration file '{config_file}'")
        sys.exit(1)

    return links


def create_html_content(
    jira_issue_base_url: str,
    epic_name: str,
    issues: List[Any],
    config: Dict[str, Any]) -> str:
    """Create the HTML content for the Confluence page.

    Args:
        jira_issue_base_url (str): The JIRA issue base url.
        epic_name (str): The epic name.
        issues (List[Any]): The list of issues.
        config (Dict[str, Any]): The configuration object.
    """
    in_development_color = config['confluence']['status']['color_codes']['in_development']
    done_color = config['confluence']['status']['color_codes']['done']

    logging.info(f"Will add '{len(issues)}' issues to the HTML table for Confluence page with title '{epic_name}'")

    content = []
    content.append(f"<html><body><h3>{epic_name}</h3>")
    content.append("""<table>
        <thead>
            <tr>
                <th>Issue</th>
                <th>Summary</th>
                <th>Type</th>
                <th>Priority</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>""")

    for issue in issues:
        content.append(f"<tr><td><a href='{jira_issue_base_url}/{issue}' target='_blank'>{issue}</a></td>")
        content.append(f"<td>{issue.fields.summary}</td>")
        content.append(f"<td>{issue.fields.issuetype.name}</td>")
        content.append(f"<td>{issue.fields.priority.name}</td>")
        status = issue.fields.status.name
        if status.lower() == 'done':
            content.append(f"<td style='font-weight: bold; color: {done_color}'>{status}</td></tr>")
        elif status.lower() == 'in development':
            content.append(f"<td style='font-weight: bold; color: {in_development_color}'>{status}</td></tr>")
        else:
            content.append(f"<td>{status}</td></tr>")

    content.append("</tbody></table></body></html>")
    return "\n".join(content)


@click.command()
@click.option('--assignee', help='The assignee')
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--credential_file', help='credential file containing username and password')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--query', help='The Jira jql query string')
def main(assignee: str, config_file: str, credential_file: str, logfile: str, outdir: str, query: str):
    """Retrieve JIRA issues for epics and create Confluence pages."""

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file, "txt")

    url = get_rest_url(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

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

    if 'jira' not in config:
        print_red(f"'jira' section does not exist in configuration file '{config_file}'")
        sys.exit(1)

    links = get_jira_epic_links(config, config_file)

    if assignee is None and 'assignee' in config:
        assignee = config['jira']['assignee']
        logging.info(f"Retrieved assignee '{assignee}' from the configuration file '{config_file}'")

    jira_issue_base_url = config['jira']['issue_base_url']
    if jira_issue_base_url is None or jira_issue_base_url == '':
        print_red("Could not find the JIRA issue base url in the configuration file")
        sys.exit(1)

    if jira_issue_base_url.endswith('/'):
        jira_issue_base_url = jira_issue_base_url.rstrip('/')

    logging.info(f"Found '{len(links)}' epic links in the configuration file '{config_file}'")

    auth_jira, auth = get_auth_jira(credential_file, url)

    for link in links:

        query = link['query']

        if assignee is not None:
            query = f"""{query} AND assignee in ({assignee})"""
            logging.info(f"Added assignee '{assignee}' to the query: {query}")

        epic_name = link['name']
        confluence_page_name = link['confluence_page_name']

        logging.info(f"Will attempt to retrieve issues for epic '{epic_name}' with query '{query}'")

        try:
            issues = auth_jira.search_issues(query)

        except Exception as e:
            print_red(f"Encountered some exception while attempting to query with JQL '{query}' : '{e}'")
            sys.exit(1)
        else:
            print("Query was successful")

        html_content = create_html_content(
            jira_issue_base_url,
            epic_name,
            issues,
            config,
        )


        manager = ConfluenceManager(
            outdir=outdir,
            config=config,
            config_file=config_file,
        )

        manager.create_page(
            auth=auth,
            title=confluence_page_name,
            html_content=html_content
        )

if __name__ == '__main__':
    main()
