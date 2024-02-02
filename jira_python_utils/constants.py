import logging
import os
from datetime import datetime


DEFAULT_PROJECT = "jira-python-utils"

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_URL_FILE = os.path.join(
    os.getenv("HOME"),
    '.jira',
    'jira_rest_url.txt'
)

DEFAULT_CREDENTIAL_FILE = os.path.join(
    os.getenv('HOME'),
    ".jira",
    "credentials.txt"
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'conf',
    'config.yaml'
)

DEFAULT_OUTDIR_BASE = os.path.join(
    '/tmp/',
    os.getenv("USER"),
    DEFAULT_PROJECT,
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO

DEFAULT_VERBOSE = False

