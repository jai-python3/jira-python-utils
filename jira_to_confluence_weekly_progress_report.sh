#!/usr/bin/env bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
. $SCRIPT_DIR/venv/bin/activate
python $SCRIPT_DIR/jira_to_confluence_weekly_progress_report.py "$@"
