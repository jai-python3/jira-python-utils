# -*- coding: utf-8 -*-
import click
import logging
import os
import pathlib
import sys
import yaml

from datetime import datetime
from typing import Any, Dict, List, Tuple

from .confluence.manager import Manager as ConfluenceManager
from .file_utils import check_infile_status
from .console_helper import print_red, print_yellow
from .helper import get_auth_jira, get_rest_url


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

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv('USER'),
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'conf/jira_weekly_updates_config.yaml'
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


def get_resolved_issues(start_date, end_date, assignee, auth_jira) -> List[Any]:
    query = f"""resolved >= {start_date} AND resolved <= {end_date}"""

    if assignee is not None:
        query = f"""{query} AND assignee in ({assignee})"""
        logging.info(f"Added assignee '{assignee}' to the query: {query}")

    return get_issues(query, auth_jira)


def get_in_development_issues(start_date, end_date, assignee, auth_jira) -> List[Any]:
    query = f"""status = 'In Development' AND updated>= {start_date} AND updated <= {end_date}"""

    if assignee is not None:
        query = f"""{query} AND assignee in ({assignee})"""
        logging.info(f"Added assignee '{assignee}' to the query: {query}")

    return get_issues(query, auth_jira)


def get_on_hold_issues(start_date, end_date, assignee, auth_jira) -> List[Any]:
    query = f"""status = 'On Hold' AND updated>= {start_date} AND updated <= {end_date}"""

    if assignee is not None:
        query = f"""{query} AND assignee in ({assignee})"""
        logging.info(f"Added assignee '{assignee}' to the query: {query}")

    return get_issues(query, auth_jira)


def get_issues(query, auth_jira) -> List[Any]:
    logging.info(f"Will attempt to retrieve issues with query '{query}'")

    try:
        issues = auth_jira.search_issues(query)

    except Exception as e:
        print_red(f"Encountered some exception while attempting to query with JQL '{query}' : '{e}'")
        sys.exit(1)
    else:
        print("Query was successful")
    return issues


def get_jira_issue_base_url(config) -> str:
    jira_issue_base_url = config['jira']['issue_base_url']
    if jira_issue_base_url is None or jira_issue_base_url == '':
        print_red("Could not find the JIRA issue base url in the configuration file")
        sys.exit(1)

    if jira_issue_base_url.endswith('/'):
        jira_issue_base_url = jira_issue_base_url.rstrip('/')

    return jira_issue_base_url


def get_weekly_ranges(config, config_file: str) -> List[Dict[str, str]]:

    if 'weekly' not in config['jira']:
        print_red(f"'weekly' section does not exist in configuration file '{config_file}'")
        sys.exit(1)

    return config['jira']['weekly']


def create_html_content(
    jira_issue_base_url: str,
    title: str,
    issues: List[Any],
    config: Dict[str, Any]) -> str:
    """Create the HTML table that will be inserted into the new Confluence
    page."""
    in_development_color = config['confluence']['status']['color_codes']['in_development']
    done_color = config['confluence']['status']['color_codes']['done']

    logging.info(f"Will add '{len(issues)}' issues to the HTML table for Confluence page with title '{title}'")

    content = []
    content.append(f"<html><body><h3>{title}</h3>")
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
        status = issue.fields.status.name
        if status.lower() == 'in development' or status.lower() == 'done' or status.lower() == 'on hold':
            content.append(f"<tr><td><a href='{jira_issue_base_url}/{issue}' target='_blank'>{issue}</a></td>")
            content.append(f"<td>{issue.fields.summary}</td>")
            content.append(f"<td>{issue.fields.issuetype.name}</td>")
            content.append(f"<td>{issue.fields.priority.name}</td>")
            if status.lower() == 'done':
                content.append(f"<td style='font-weight: bold; color: {done_color}'>{status}</td></tr>")
            elif status.lower() == 'in development':
                content.append(f"<td style='font-weight: bold; color: {in_development_color}'>{status}</td></tr>")
            elif status.lower() == 'on hold':
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

    rest_url_file = DEFAULT_URL_FILE
    check_infile_status(rest_url_file, "txt")

    url = get_rest_url(rest_url_file)

    if credential_file is None:
        credential_file = DEFAULT_CREDENTIAL_FILE

    check_infile_status(credential_file)

    error_ctr = 0

    if error_ctr > 0:
        print_red("Required parameter(s) not defined")
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

    week_ranges = get_weekly_ranges(config, config_file)

    logging.info(f"Found '{len(week_ranges)}' week ranges in the configuration file '{config_file}'")

    if assignee is None and 'assignee' in config['jira']:
        assignee = config['jira']['assignee']
        logging.info(f"Retrieved assignee '{assignee}' from the configuration file '{config_file}'")

    jira_issue_base_url = get_jira_issue_base_url(config)

    auth_jira, auth = get_auth_jira(credential_file, url)

    for week_range in week_ranges:

        start_date = week_range['start_date']
        end_date = week_range['end_date']
        print_yellow(f"{start_date=} {end_date=}")

        resolved_issues = get_resolved_issues(
            start_date,
            end_date,
            assignee,
            auth_jira
        )

        # in_development_issues = get_in_development_issues(
        #     start_date,
        #     end_date,
        #     assignee,
        #     auth_jira
        # )

        # on_hold_issues = get_on_hold_issues(
        #     start_date,
        #     end_date,
        #     assignee,
        #     auth_jira
        # )

        # issues = resolved_issues + in_development_issues + on_hold_issues
        # issues = on_hold_issues
        issues = resolved_issues

        confluence_page_name = f"Jay's Weekly Progress Report between '{start_date}' and '{end_date}'"

        html_content = create_html_content(
            jira_issue_base_url,
            confluence_page_name,
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
