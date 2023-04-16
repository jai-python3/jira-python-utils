#!/usr/bin/env bash
source ${HOME}/.tools/jira-python-utils/venv/bin/activate
python ${HOME}/.tools/jira-python-utils/jira_sync_workspace.py "$@"
