import filecmp
import logging
import os
import pathlib
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

import click
import yaml
from colorama import Fore, Style


TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.path.splitext(os.path.basename(__file__))[0],
    TIMESTAMP
)

DEFAULT_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'conf/jira_workspace_config.yaml'
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO
    

import logging
import os

def get_file_list(indir: str = None, extension: str = None) -> list:
    """Get the list of files in the specified directory
    :param indir: {str} - the directory to search for files
    :param extension: {str} - the file extension to filter on
    :returns file_list: {list} - the list of files found in the directory
    """
    if extension is None:
        logging.info(f"Going to search for files in directory '{indir}'")
    else:
        logging.info(f"Going to search for files with extension '{extension}' in directory '{indir}'")

    file_list = []
    for dirpath, dirnames, filenames in os.walk(indir):
        if 'venv' in dirpath:
            logging.info(f"Going to ignore files in directory '{dirpath}'")
            continue
        for name in filenames:
            path = os.path.normpath(os.path.join(dirpath, name))
            if os.path.isfile(path):
                if extension is not None:
                    if os.path.endswith('.{extension}'):
                        file_list.append(path)
                else:
                    file_list.append(path)

    return file_list


def get_files_lookup(indir: str) -> Dict[str, str]:
    file_list = get_file_list(indir)
    lookup = {}
    for f in file_list:
        key = f.replace(indir, "")
        if key.startswith("/"):
            key = key.lstrip("/")

        lookup[key] = f
    return lookup

def sync_directories(shared_jira_dir, jira_dir, config, config_file, logfile, outfile) -> None:
    jira_dir_lookup = get_files_lookup(jira_dir)
    logging.info(f"{jira_dir_lookup=}")

    shared_jira_dir_lookup = get_files_lookup(shared_jira_dir)
    logging.info(f"{shared_jira_dir_lookup=}")

    cmds = []
    
    prepare_commands(
        source_lookup=jira_dir_lookup, 
        target_lookup=shared_jira_dir_lookup, 
        source_dir=jira_dir, 
        target_dir=shared_jira_dir, 
        cmds=cmds
    )

    prepare_commands(
        source_lookup=shared_jira_dir_lookup,
        target_lookup=jira_dir_lookup,
        source_dir=shared_jira_dir,
        target_dir=jira_dir,
        cmds=cmds
    )

    if len(cmds) > 0:

        user = os.environ.get('USER')
        cmd = f"sudo chown -R {user}.{user} {jira_dir}"
        cmds.append(cmd)
        
        cmd = f"sudo chown -R {user}.{user} {shared_jira_dir}"
        cmds.append(cmd)

        with open(outfile, 'w') as of:
            of.write("#!/usr/bin/bash\n")
            of.write(f"## method-created: {os.path.abspath(__file__)}\n")
            of.write(f"## date-created: {str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))}\n")
            of.write(f"## created-by: {user}\n")
            of.write(f"## logfile: {logfile}\n")
            of.write(f"## config_file: {config_file}\n")

            for cmd in cmds:    
                of.write(f"{cmd}\n")
        
        logging.info(f"Wrote file '{outfile}'")
        print(f"Wrote file '{outfile}'")
    else:
        print_green(f"Both directories are already synced!")


def prepare_commands(source_lookup: Dict[str, str], target_lookup: Dict[str, str], source_dir: str, target_dir: str, cmds: List[str]) -> List[str]:
    for filekey, filepath in source_lookup.items():
        if filekey not in target_lookup:
            logging.info(f"Will copy '{filepath}' to '{target_dir}'")
            target_file = f"{target_dir}/{filekey}"
            dirname = os.path.dirname(target_file)
            if not os.path.exists(dirname):
                cmd = f"sudo mkdir -p {dirname}"
                cmds.append(cmd)
            cmd = f"sudo cp {filepath} {target_file}"
            cmds.append(cmd)
        else:
            target_file = target_lookup[filekey]
            if not filecmp.cmp(filepath, target_file):
                print(f"{target_file=} {filepath=} are different")
                logging.info(f"File '{filekey}' already exists in '{target_dir}' - you will need to determine which is most up-to-date and copy that one to the destination")
            else:
                logging.info(f"No action required since these two files are the same: {target_file=} {filepath=}")

    return cmds

    # for filekey, filepath in shared_jira_dir_lookup.items():
    #     if filekey not in jira_dir_lookup:
    #         logging.info(f"Will copy '{filepath}' to '{jira_dir}'")
    #         cmd = f"sudo cp {filepath} {jira_dir}/{filekey}"
    #         cmds.append(cmd)

    #     else:
    #         logging.info(f"File '{filekey}' already exists in '{jira_dir}'")


def check_config_file(config_file: str) -> None:
    """Check the configuration file."""
    if not os.path.exists(config_file):
        print_red(f"configuration file '{config_file}' does not exist")
        sys.exit(1)

    if not os.path.isfile(config_file):
        print_red(f"configuration file '{config_file}' is not a regular file")
        sys.exit(1)

    if not config_file.endswith(".yaml"):
        print_red(
            f"configuration file '{config_file}' does not have a .yaml file extension"
        )
        sys.exit(1)

    if os.path.getsize(config_file) == 0:
        print_red(f"configuration file'{config_file}' has no content")
        sys.exit(1)


def print_red(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.
    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.RED + msg + Style.RESET_ALL)


def print_green(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.
    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.GREEN + msg + Style.RESET_ALL)


def print_yellow(msg: str = None) -> None:
    """Print message to STDOUT in yellow text.
    :param msg: {str} - the message to be printed
    """
    if msg is None:
        raise Exception("msg was not defined")

    print(Fore.YELLOW + msg + Style.RESET_ALL)


@click.command()
@click.option('--config_file', type=click.Path(exists=True), help=f"The configuration file - default is '{DEFAULT_CONFIG_FILE}'")
@click.option('--jira_id', help='The Jira ticket identifier')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--outfile', help="The output file")
def main(config_file: str, jira_id: str, logfile: str, outdir: str, outfile: str):
    
    error_ctr = 0

    if jira_id is None:
        print_red("--jira_id was not specified")
        error_ctr += 1

    if error_ctr > 0:
        print("Required parameter(s) not defined")
        sys.exit(1)

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print_yellow(f"--outdir was not specified and therefore was set to '{outdir}'")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

        print_yellow(f"Created output directory '{outdir}'")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        print_yellow(f"--logfile was not specified and therefore was set to '{logfile}'")

    if outfile is None:
        outfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.sh'
        )
        print_yellow(f"--outfile was not specified and therefore was set to '{outfile}'")

    if config_file is None:
        config_file = DEFAULT_CONFIG_FILE
        print_yellow(f"--config_file was not specified and therefore was set to '{config_file}'")
    
    check_config_file(config_file)

    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    logging.info(f"Loading configuration from '{config_file}'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    jira_dir = os.path.join(config["main_jira_work_dir"], jira_id)
    if jira_dir.endswith("/"):
        jira_dir.rstrip("/")

    jira_dir_exists = False
    if not os.path.exists(jira_dir):
        pathlib.Path(jira_dir).mkdir(parents=True, exist_ok=True)

        print(f"Created directory '{jira_dir}'")
    else:
        jira_dir_exists = True
        logging.info(f"'{jira_dir}' exists")

    shared_jira_dir = os.path.join(config["shared_jira_work_dir"], jira_id)
    if shared_jira_dir.endswith("/"):
        shared_jira_dir.rstrip("/")
    shared_jira_dir_exists = False

    if not os.path.exists(shared_jira_dir):
        print_red(f"Please execute the following:\n")

        pathlib.Path(shared_jira_dir).mkdir(parents=True, exist_ok=True)

        print_red(f"sudo mkdir -p {shared_jira_dir}")
        print("And then rerun this program.")
        sys.exit(1)
    else:
        logging.info(f"'{shared_jira_dir}' exists")
        shared_jira_dir_exists = True

    if shared_jira_dir_exists and jira_dir_exists:
        sync_directories(
            shared_jira_dir, 
            jira_dir, 
            config, 
            config_file, 
            logfile, 
            outfile
        )


if __name__ == '__main__':
    main()
