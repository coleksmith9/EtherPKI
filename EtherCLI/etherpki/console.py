"""Console application for EtherPKI"""

import atexit
import logging
import time

import click

from etherpki.transactions import Transactions

@click.group()
def main():
    pass

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