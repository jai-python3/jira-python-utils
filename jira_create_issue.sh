#!/usr/bin/env bash
source ${HOME}/jira-python-utils/venv/bin/activate
python ~/jira-python-utils/jira_create_issue.py "$@"
