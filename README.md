# jira-python-utils
Collection of Python utility scripts interacting with Jira issue tracking system instance.

- [jira-python-utils](#jira-python-utils)
  - [Motivation](#motivation)
  - [Improvements](#improvements)
  - [Installation](#installation)
  - [Generate shell wrapper scripts](#generate-shell-wrapper-scripts)
  - [Exported scripts](#exported-scripts)
  - [Contributing](#contributing)
  - [To-Do/Coming Next](#to-docoming-next)
  - [CHANGELOG](#changelog)
  - [License](#license)



## Motivation

The collection of Python scripts allows uses to quickly and easily interact with Jira via command-line terminal.


## Improvements

Please see the [TODO](TODO.md) for a list of upcoming improvements.


## Installation

Please see the [INSTALL](docs/INSTALL.md) guide for instructions.


## Generate shell wrapper scripts

After executing `pip install jira-python-utils`, execute this exported script: `make_executables_and_aliases.py`.<br>
This will create the wrapper shell scripts and a file containing aliases named `jira-python-utils-aliases.txt` in the current directory.<br><br>
You can then add this line to your `.bashrc` or `.zshrc`:<br>
`source dir/jira-python-utils-aliases.txt`<br>
where dir is the directory that contains the aliases file.


## Exported scripts

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

Note that these will only be available after the Python virtual environment is activated.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## To-Do/Coming Next

Please view the listing of planned improvements [here](TODO.md).

## CHANGELOG

Please view the CHANGELOG [here](CHANGELOG.md).

## License

[GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE)
