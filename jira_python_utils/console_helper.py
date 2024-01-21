"""The console helper module provides functions for printing colored messages to the console.

    Raises:
        Exception: If the message is not defined.
"""
from rich.console import Console

error_console = Console(stderr=True, style="bold red")

console = Console()


def print_red(msg: str) -> None:
    """Print the message in red.

    Args:
        msg (str): The message to be printed to STDERR.

    Raises:
        Exception: If the message is not defined.
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")
    error_console.print(msg)


def print_green(msg: str) -> None:
    """Print the message in green.

    Args:
        msg (str): The message to be printed to STDOUT.

    Raises:
        Exception: If the message is not defined.
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")

    console.print(f"[bold green]{msg}[/]")

def print_yellow(msg: str = None) -> None:
    """Print the message in yellow.

    Args:
        msg (str): The message to be printed to STDOUT.

    Raises:
        Exception: If the message is not defined.
    """
    if msg is None or msg == "":
        raise Exception("msg was not defined")

    console.print(f"[bold yellow]{msg}[/]")
