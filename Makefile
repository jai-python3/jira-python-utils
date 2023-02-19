# .PHONY init

.DEFAULT_GOAL = help

help:
	@echo "  The following options are available:"
	@echo ""
	@echo "  make init"
	@echo ""
	@echo "       Initialize this jira-python-utils project"
	@echo ""
	@echo "       - create a virtual environment using virtualenv"
	@echo "       - run pip install -r requirements-dev.txt"
	@echo "       - append the aliases.txt to the ~/.zshrc"
	@echo ""

init:
	virtualenv venv -p python3.8 && . venv/bin/activate && pip install --upgrade pip && pip install -r requirements-dev.txt
	echo "source ${HOME}/jira-python-utils/aliases.sh" >> ${HOME}/.zshrc
	. ${HOME}/.zshrc
