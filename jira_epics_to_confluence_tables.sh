#!/usr/bin/env bash
source ${HOME}/.tools/jira-python-utils/venv/bin/activate
python ${HOME}/.tools/jira-python-utils/jira_epics_to_confluence_tables.py "$@"
