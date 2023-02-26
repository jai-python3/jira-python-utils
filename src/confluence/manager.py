import json
import logging
import os
from typing import Dict, List, Tuple, Union

import requests
from rich import print as rprint

DEFAULT_VERBOSE = False

DEFAULT_CONTENT_TYPE = 'page'


class Manager:
    """Class for working with Confluence REST API."""


    def __init__(self, **kwargs):
        """Constructor for class for working with Confluence REST API."""
        self.outdir = kwargs.get('outdir', None)
        self.outfile = kwargs.get('outfile', None)
        self.logfile = kwargs.get('logfile', None)
        self.config = kwargs.get('config', None)
        self.config_file = kwargs.get('config_file', None)
        self.space_key = kwargs.get('space_key', None)

        self.rest_api_url = kwargs.get('rest_api_url', None)
        if self.rest_api_url is None:
            self._derive_rest_api_url()

        self.parent_page_id = kwargs.get('parent_page_id', None)
        if self.parent_page_id is None:
            self._derive_parent_page_id()

        self.space_key = kwargs.get('space_key', None)
        if self.space_key is None:
            self._derive_space_key()


        logging.info(f"Instantiated Manager in '{os.path.abspath(__file__)}'")

    def _derive_rest_api_url(self) -> None:
        if 'confluence' not in self.config:
            raise Exception(f"Did not find 'confluence' section in the configuration file '{self.config_file}'")

        if 'rest_api_url' not in self.config['confluence']:
            raise Exception(f"Did not find 'rest_api_url' in the 'confluence' section in the configuration file '{self.config_file}'")
        self.rest_api_url = self.config['confluence']['rest_api_url']

    def _derive_parent_page_id(self) -> None:
        if 'confluence' not in self.config:
            raise Exception(f"Did not find 'confluence' section in the configuration file '{self.config_file}'")

        if 'parent_page_id' not in self.config['confluence']:
            raise Exception(f"Did not find 'parent_page_id' in the 'confluence' section in the configuration file '{self.config_file}'")
        self.parent_page_id = self.config['confluence']['parent_page_id']

    def _derive_space_key(self) -> None:
        if 'confluence' not in self.config:
            raise Exception(f"Did not find 'confluence' section in the configuration file '{self.config_file}'")

        if 'space_key' not in self.config['confluence']:
            raise Exception(f"Did not find 'space_key' in the 'confluence' section in the configuration file '{self.config_file}'")
        self.space_key = self.config['confluence']['space_key']

    def create_page(
        self, 
        auth: Union[Tuple[str, str], None] = None, 
        parent_page_id: int = None, 
        content_type: str = DEFAULT_CONTENT_TYPE, 
        title: str = None, 
        html_content: str = None) -> List[str]:
        """Create the Confluence page for the Jira epic."""
        if parent_page_id is None:
            parent_page_id = self.parent_page_id
        if title is None:
            raise Exception("title was not define")
        if html_content is None:
            raise Exception("html_content was not define")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        params = {
            'spaceKey': self.space_key, 
            'title': title
        }

        result = requests.get(
            self.rest_api_url,
            headers=headers, 
            auth=auth, 
            params=params,
            verify=False
        )

        json_output = json.loads(result.text)
        logging.info(f"json_output: {json_output}")
        if json_output['results']:
            pid = json_output['results'][0]['id']
            print(f"Page with title '{title}' in home space '{self.config['confluence']['home_space']}' already exists so will update it")
            logging.info(f"Page with title '{title}' in home space '{self.config['confluence']['home_space']}' already exists so will update it")
        else:
            self._create_page(headers, auth, parent_page_id, title, content_type)

        self.update_page(pid, headers, auth, title, html_content)

    def _create_page(self, 
    headers, 
    auth, 
    parent_page_id: int, 
    title: str, 
    content_type: str) -> int:
        print(f"Page with title '{title}' in home space '{self.config['confluence']['home_space']}' does not exist, so will create it now")
        logging.info(f"Page with title '{title}' in home space '{self.config['confluence']['home_space']}' does not exist, so will create it now")

        data = {
            'title': title,
            'type': content_type,
            'space': {'key': self.space_key}, 
            'ancestors': [{'id': parent_page_id}] # ID of the parent page
        }

        result = requests.post(
            self.rest_api_url,
            headers=headers, 
            auth=auth, 
            json=data,
            verify=False
        )

        json_output = json.loads(result.text)

        logging.info(f"{json_output=}")

        if 'id' not in json_output:
            raise Exception("did not find id in the json_output!")

        pid = json_output['id']

        logging.info(f"Page with title '{title}' has created and assigned pagd ID '{pid}'")
        print(f"Page with title '{title}' has created and assigned pagd ID '{pid}'")
            
        return pid

    def update_page(self, 
    pid: int, headers: Dict[str,str], 
    auth, 
    title: str, 
    html_content: str) -> None:

        logging.info(f"Will attempt to retrieve content for page with ID '{pid}'")
        result = requests.get(
            f"{self.rest_api_url}/{pid}",
            headers=headers,
            auth=auth,
            verify=False
        )

        json_output = json.loads(result.text)

        version = int(json_output['version']['number']) + 1

        logging.info(f"Will attempt to update the page content - new version will be '{version}'")

        data = {
                'type': 'page',
                'title': title,
                'body': {
                    'storage': {
                        'value': html_content,
                        'representation': 'storage',
                    }
                },
                'version': {
                    'number': version,
                }
        }

        logging.info(f"{data=}")
        result = requests.put(
            f"{self.rest_api_url}/{pid}",
            headers=headers,
            auth=auth,
            json=data,
            verify=False
        )

        json_output = json.loads(result.text)
        logging.info(f"{json_output=}")

        if 'statusCode' in json_output and int(json_output['statusCode']) != 200:
            rprint(f"[bold red]Encountered some error while attempting to update content of page '{title}'.  Please see the log file.[/]")
            logging.error(f"Encountered some error while attempting to update content of page '{title}'.  Please see the log file.")
        else:
            logging.info(f"Updated the Confluence page '{title}'")
            rprint(f"[green]Updated the Confluence page '{title}'[/]")
