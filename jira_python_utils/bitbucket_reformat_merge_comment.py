# -*- coding: utf-8 -*-
import click
import logging
import os
import pathlib
import sys

from datetime import datetime


from .console_helper import print_red, print_yellow

DEFAULT_JIRA_ISSUE_PREFIXES = ['PTB', 'RGCCIDM']

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    '/tmp/',
    os.getenv('USER'),
    os.path.splitext(os.path.basename(__file__))[0],
    DEFAULT_TIMESTAMP
)

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


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
        click.echo(click.get_current_context().get_help())
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

    logging.basicConfig(
        filename=logfile,
        format=LOGGING_FORMAT,
        level=LOG_LEVEL
    )

    reformat_content(infile, logfile, outdir, outfile)


if __name__ == '__main__':
    main()
