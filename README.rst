=================
JIRA Python Utils
=================

Collection of Python utils for interacting with JIRA from the command line.


Features
--------

Insert the URL for your instance of Jira in the ``conf/jira_rest_url.txt`` file.

.. code-block:: bash

    https://jira.your-domain.com

Insert your Jira username in the ``~/.jira/credentials.txt file``.
Remember to set permissions ``chmod 600 ~/.jira/credentials.txt``.

Note: The password might not be necessary depending on your Jira configuration.

.. code-block:: bash

    someusername:somepassword


The following exported scripts are available:

- annotate-readme
- bitbucket-reformat-merge-comment
- jira-add-change-control-comment
- jira-add-comment
- jira-add-component
- jira-add-label
- jira-assign-issue
- jira-convert-task-session-script-to-readme
- jira-create-issue
- jira-create-release-software-issues
- jira-epics-to-confluence-tables
- jira-get-issue-details
- jira-initiate-workspace
- jira-link-issues
- jira-remove-watcher
- jira-search-issues
- jira-start-task
- jira-sync-workspace
- jira-to-confluence-weekly-progress-report
- search-readme
