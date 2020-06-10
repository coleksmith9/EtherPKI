"""Console application for EtherPKI"""

import atexit
import logging
import time

import click

from etherpki.transactions import Transactions
# from etherpki.events import Events TODO: implement events and uncomment
from etherpki import userconfig

@click.group()
def main():
    # Prevent the requests module from printing INFO logs to the console.
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Save the configuration on exit.
    atexit.register(userconfig.config.write)

@click.command()
@click.option("--attributetype", prompt="Attribute Type", type=str)
@click.option("--identifier", prompt="Attribute Identifier", type=str)
@click.option("--data", prompt="Data", help="Data", type=str)
def add(attributetype, identifier, data):
    """ADDs attributes to the network"""
    click.echo("Adding! %s %s %s" % (attributetype, identifier, data))

main.add_command(add)

if __name__ == "__main__":
    main()