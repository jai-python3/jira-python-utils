import logging
import os
import pathlib
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

import click
from colorama import Fore, Style

DEFAULT_JIRA_ISSUE_PREFIXES = ['PTB', 'RGCCIDM']

TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.path.splitext(os.path.basename(__file__))[0],
    TIMESTAMP
)


LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


def reformat_content_v1(infile: str, logfile: str, outdir: str, outfile: str) -> None:
    lookup = {}
    current_issue_id = None
    logging.info(f"Will read file '{infile}'")
    line_ctr = 0
    comments = []
    first_issue_found = False

    with open(infile, 'r') as f:
        for line in f:
            logging.info(f"{line=}")

            line_ctr += 1
            line = line.strip()
            if line == '':
                # issue_found = False
                continue
            elif line.startswith('PTB-') or line.startswith('RGCCIDM-'):
                if not first_issue_found:
                    first_issue_found = True
                    current_issue_id = line
                    logging.info(f"Found the first issue id '{line}'")
                    
                logging.info(f"Found issue id '{line}'")
                store_issue_comments(current_issue_id, comments, lookup)
                current_issue_id = line
                comments = []
                continue
            else:
                logging.info(f"appending comment '{line=}'")
                comments.append(line)
        if not (line.startswith('PTB-') or line.startswith('RGCCIDM-')):
            comments.append(line)
        store_issue_comments(current_issue_id, comments, lookup)
            # print(line)
    # print(f"{lookup=}")

    if line_ctr > 0:
        logging.info(f"Read '{line_ctr}' lines from file '{infile}'")
    else:
        logging.info(f"Did not read any lines from file '{infile}'")

    print("Here is the reformatted Bitbucket merge comment:")
    for issue_id in lookup:
        print(f"{issue_id}:")
        for comment in lookup[issue_id]:
            print(comment)


def reformat_content(infile: str, logfile: str, outdir: str, outfile: str) -> None:
    logging.info(f"Will read file '{infile}'")
    
    lines = None
    
    with open(infile, 'r') as f:
        lines = f.readlines()

    lines.reverse()
    logging.info(f"Read '{len(lines)}' from file '{infile}'")

    lookup = {}
    current_issue_id = None

    line_ctr = 0

    issue_id_list = []
    unique_issue_id_lookup = {}
    for line in lines:
        logging.info(f"{line=}")

        line_ctr += 1
        line = line.strip()
        if line == '':
            continue
        elif line.startswith('PTB-') or line.startswith('RGCCIDM-'):
            current_issue_id = line.strip()
            if current_issue_id not in unique_issue_id_lookup:
                issue_id_list.append(current_issue_id)
                unique_issue_id_lookup[current_issue_id] = True

            if current_issue_id not in lookup:
                lookup[current_issue_id] = []
            continue
        else:
            lookup[current_issue_id].append(line)

    issue_id_list.reverse()
    print("Here is the reformatted Bitbucket merge comment:")
    for issue_id in issue_id_list:
        print(f"\n{issue_id}:")
        comments = lookup[issue_id]
        comments.reverse()
        for comment in comments:
            print(comment)


def store_issue_comments(current_issue_id, comments, lookup) -> None:
    if current_issue_id is not None:
        if current_issue_id not in lookup:
            lookup[current_issue_id] = []

        if len(comments) > 0:
            logging.info(f"storing '{len(comments)}' comments for issue '{current_issue_id}'")
            for comment in comments:
                logging.info(f"storing comment '{comment}' for issue '{current_issue_id}'")

                lookup[current_issue_id].append(comment)
        else:
            logging.info(f"No comments to set for Jira issue '{current_issue_id}'")
    
        comments = []
    
    else:
        logging.info(f"Current Jira issue is not defined but have '{len(comments)}' comments:")
        for comment in comments:
            logging.info(comment)
    

def check_infile(infile: str) -> None:
    """Check the input file."""
    if not os.path.exists(infile):
        print_red(f"input file '{infile}' does not exist")
        sys.exit(1)

    if not os.path.isfile(infile):
        print_red(f"input file '{infile}' is not a regular file")
        sys.exit(1)

    if not infile.endswith(".txt"):
        print_red(
            f"input file '{infile}' does not have a .txt file extension"
        )
        sys.exit(1)

    if os.path.getsize(infile) == 0:
        print_red(f"input file'{infile}' has no content")
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
@click.option('--infile', help='The file containing the raw Bitbucket merge text')
@click.option('--logfile', help="The log file")
@click.option('--outdir', help=f"The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--outfile', help="The output file")
def main(infile: str, logfile: str, outdir: str, outfile: str):

    
    error_ctr = 0

    if infile is None:
        print_red("--infile was not specified")
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
            os.path.splitext(os.path.basename(__file__))[0] + '.txt'
        )
        print_yellow(f"--outfile was not specified and therefore was set to '{outfile}'")

    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    reformat_content(infile, logfile, outdir, outfile)


if __name__ == '__main__':
    main()
