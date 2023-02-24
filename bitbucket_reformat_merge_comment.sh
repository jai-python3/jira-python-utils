#!/usr/bin/env bash
source ${HOME}/.tools/jira-python-utils/venv/bin/activate
python ${HOME}/.tools/jira-python-utils/bitbucket_reformat_merge_comment.py "$@"