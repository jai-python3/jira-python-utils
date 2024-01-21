import logging
import os
import sys

from jira import JIRA
from rich.console import Console
from typing import Tuple

error_console = Console(stderr=True, style="bold red")

console = Console()


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

    logging.info(f"options: {options}")

    auth_jira = JIRA(
        options=options,
        basic_auth=(username, password)
    )

    if auth_jira is None:
        error_console.print(f"Could not instantiate JIRA for url '{url}'")
        sys.exit(1)

    auth = (username, password)

    return auth_jira, auth


def get_username_password(credential_file: str) -> Tuple[str,str]:
    """Parse the credential file and retrieve the username and password."""
    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()
        (username, password) = line.split(':')
        console.print(f"read username and password from credentials file '{credential_file}'")
        return username, password


def get_rest_url(rest_url_file: str) -> str:
    """Get the REST URL from the file.

    Args:
        rest_url_file (str): The path to the file containing the REST URL.

    Returns:
        str: The REST URL.
    """
    with open(rest_url_file, 'r') as f:
        url = f.readline()
        url = url.strip()
        console.print(f"Retrieved the REST URL from file '{rest_url_file}'")
    return url


def get_jira_url(rest_url_file: str) -> str:
    if not os.path.exists(rest_url_file):
        error_console.print(f"JIRA REST URL file '{rest_url_file}' does not exist")
        sys.exit(1)
    else:
        with open(rest_url_file, 'r') as f:
            url = f.readline()
            url = url.strip()
            logging.info(f"read the REST URL from file '{rest_url_file}'")
    return url


def get_credentials(credential_file: str) -> (str, str):
    """Parse the credential file and retrieve the username and password.

    Args:
        credential_file (str): The credential file.

    Returns:
        Tuple[str,str]: The username and password.
    """
    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()

        (username, password) = line.split(':')

        if username is None or username == "":
            raise Exception(f"username is empty in file '{credential_file}'")

        if password is None or password == "":
            raise Exception(f"password is empty in file '{credential_file}'")

        console.print("read username and password from credentials file")
    return (username, password)


def get_username(credential_file: str) -> str:
    with open(credential_file, 'r') as f:
        line = f.readline()
        line = line.strip()

        (username, _) = line.split(':')

        if username is None or username == "":
            raise Exception(f"username is empty in file '{credential_file}'")

    return username


def get_auth(credential_file: str, url: str):
    """Instantiate the JIRA object.

    Args:
        credential_file (str): the credentials file
        url: the REST URL

    Returns:
        JIRA: The JIRA class instance
    """
    username, password = get_credentials(credential_file)

    options = {
        'server': url,
        'verify': False
    }

    auth_jira = JIRA(options=options, basic_auth=(username, password))

    if auth_jira is None:
        error_console.print(f"Could not instantiate JIRA for url '{url}'")
        sys.exit(1)

    return auth_jira

def get_summary(issue_id: str, credential_file: str, rest_url_file: str) -> str:
    auth_jira = get_auth(credential_file, get_jira_url(rest_url_file))
    jira_issue = auth_jira.issue(issue_id)
    return jira_issue.fields.summary
