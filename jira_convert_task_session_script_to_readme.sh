#!/usr/bin/env bash
source ${HOME}/.tools/jira-python-utils/venv/bin/activate
python ${HOME}/.tools/jira-python-utils/jira_convert_task_session_script_to_readme.py "$@"
