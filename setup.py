#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0',
    "Rich",
    "jira"
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Jai Python3",
    author_email='jai.python3@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Collection of Python utils for interacting with JIRA",
    entry_points={
        'console_scripts': [
            "annotate-readme=jira_python_utils.annotate_readme:main",
            "bitbucket-reformat-merge-comment=jira_python_utils.bitbucket_reformat_merge_comment:main",
            "jira-add-change-control-comment=jira_python_utils.jira_add_change_control_comment:main",
            "jira-add-comment=jira_python_utils.jira_add_comment:main",
            "jira-add-component=jira_python_utils.jira_add_component:main",
            "jira-add-label=jira_python_utils.jira_add_label:main",
            "jira-assign-issue=jira_python_utils.jira_assign_issue:main",
            "jira-convert-task-session-script-to-readme=jira_python_utils.jira_convert_task_session_script_to_readme:main",
            "jira-create-issue=jira_python_utils.jira_create_issue:main",
            "jira-create-release-software-issues=jira_python_utils.jira_create_release_software_issues:main",
            "jira-epics-to-confluence-tables=jira_python_utils.jira_epics_to_confluence_tables:main",
            "jira-get-issue-details=jira_python_utils.jira_get_issue_details:main",
            "jira-initiate-workspace=jira_python_utils.jira_initiate_workspace:main",
            "jira-link-issues=jira_python_utils.jira_link_issues:main",
            "jira-remove-watcher=jira_python_utils.jira_remove_watcher:main",
            "jira-search-issues=jira_python_utils.jira_search_issues:main",
            "jira-start-task=jira_python_utils.jira_start_task:main",
            "jira-sync-workspace=jira_python_utils.jira_sync_workspace:main",
            "jira-to-confluence-weekly-progress-report=jira_python_utils.jira_to_confluence_weekly_progress_report:main",
            "jira-scan-jira-dirs=jira_python_utils.scan_jira_dirs:main",
            "jira-annotate-readme=jira_python_utils.annotate_readme:main",
            "search-readme=jira_python_utils.search_readme:main",
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='jira_python_utils',
    name='jira_python_utils',
    packages=find_packages(include=['jira_python_utils', 'jira_python_utils.*']),
    scripts=["scripts/make_executables_and_aliases.py"],
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jai-python3/jira-python-utils',
    version='0.6.0',
    zip_safe=False,
)
