"""Console application for EtherPKI"""

import atexit
import logging
import time

import click

from etherpki.transactions import Transactions
from etherpki.events import Events
from etherpki import userconfig

# helper method for later
def echo_attribute_block(attribute, signatures_status=None):
    """Echo a console block representing basic data about the attribute."""
    if signatures_status is None and 'signatures_status' in attribute:
        signatures_status = attribute['signatures_status']

    # Encode attribute identifier as hex if it contains non-ASCII characters.
    if not all(ord(c) < 128 for c in attribute['identifier']):
        attribute['identifier'] = '0x' + attribute['identifier'].rstrip('\x00').encode('hex')

    click.echo("Attribute ID #" + str(attribute['attributeID']) + ':')
    click.echo("\tType: " + attribute['attributeType'])
    click.echo("\tOwner: " + attribute['owner']
        + (" [trusted]" if userconfig.is_trusted(attribute['owner']) else " [untrusted]"))
    click.echo("\tIdentifier: " + attribute['identifier'])

    if signatures_status is not None:
        valid_signatures = signatures_status['status']['valid']
        click.echo("\t[" + str(valid_signatures) + " valid signature"
            + ("]" if valid_signatures == 1 else "s]"))

@click.group()
def main():
    # Prevent the requests module from printing INFO logs to the console.
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Save the configuration on exit.
    atexit.register(userconfig.config.write)

@click.command()
@click.option('--attributetype', prompt=True, type=str)
@click.option('--has_proof', prompt=True, type=bool)
@click.option('--identifier', prompt=True, type=str)
@click.option('--data', prompt=True, type=str)
@click.option('--datahash', prompt=True, type=str)
def rawaddattribute(attributetype, has_proof, identifier, data, datahash):
    """(Advanced) Manually add an attribute to your identity."""
    transactions = Transactions()
    transactions.add_attribute(attributetype, has_proof, identifier, data, datahash)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--attributeid', prompt=True, type=int)
@click.option('--expiry', prompt=True, type=str)
def rawsignattribute(attributeid, expiry):
    """(Advanced) Manually sign an attribute about an identity."""
    transactions = Transactions()
    transactions.sign_attribute(attributeid, expiry)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--signatureid', prompt=True, type=str)
def rawrevokeattribute(signatureid):
    """(Advanced) Manaully revoke your signature of an attribute."""
    transactions = Transactions()
    transactions.revoke_signature(signatureid)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--attributetype', prompt='Attribute type', help='Attribute type', type=str)
@click.option('--identifier', prompt='Attribute identifier', help='Attribute identifier', type=str)
@click.option('--data', prompt='Attribute data', default='', help='Attribute data', type=str)
def add(attributetype, identifier, data):
    """Add an attribute to your identity."""
    transactions = Transactions()
    transactions.add_attribute_with_hash(attributetype, False, identifier, data)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--attributetype', prompt='Attribute type', help='Attribute type', type=str)
@click.option('--identifier', prompt='Attribute identifier', help='Attribute identifier', type=str)
@click.option('--data', prompt='Attribute data', default='', help='Attribute data', type=str)
def ipfsadd(attributetype, identifier, data):
    """Add an attribute to your identity over IPFS."""
    transactions = Transactions()
    transactions.add_attribute_over_ipfs(attributetype, False, identifier, data)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--attributeid', prompt='Attribute ID', help='Attribute ID', type=int)
@click.option('--expires', prompt='Signature days to expire', default=365, help='Signature days to expire', type=int)
def sign(attributeid, expires):
    """Sign an attribute."""
    transactions = Transactions()

    expiry = int(time.time()) + expires * 60 * 60 * 24
    transactions.sign_attribute(attributeid, expiry)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--signatureid', prompt='Signature ID', help='Signature ID', type=int)
def revoke(signatureid):
    """Revoke one of your signatures."""
    transactions = Transactions()
    transactions.revoke_signature(signatureid)

    click.echo()
    click.echo("Transaction sent.")


@click.command()
@click.option('--address', prompt='Ethereum address', help='Ethereum address', type=str)
def trust(address):
    """Trust an Ethereum address."""
    click.echo()

    if userconfig.is_trusted(address):
        click.echo("Address " + address + " is already trusted.")
    else:
        userconfig.trust(address)
        click.echo("Address " + address + " trusted.")


@click.command()
@click.option('--address', prompt='Ethereum address', help='Ethereum address', type=str)
def untrust(address):
    """Untrust an Ethereum address."""
    click.echo()

    if not userconfig.is_trusted(address):
        click.echo("Address " + address + " is already not trusted.")
    else:
        userconfig.untrust(address)
        click.echo("Address " + address + " untrusted.")


@click.command()
def trusted():
    """View the list of trusted Ethereum addresses."""
    for address in userconfig.get_trusted():
        click.echo(address)


@click.command()
@click.option('--attributeid', prompt='Attribute ID', help='Attribute ID', type=int)
def retrieve(attributeid):
    """Retrieve an attribute."""
    events = Events()
    attribute = events.retrieve_attribute(attributeid)

    if attribute is None:
        click.echo("No such attribute.")
        return

    click.echo()

    echo_attribute_block(attribute)
    click.echo()

    if 'proof_valid' in attribute:
        click.echo("Proof status for attribute ID #" + str(attribute['attributeID']) + ':')
        if attribute['proof_valid'] is None:
            click.echo("\tUnknown")
        elif attribute['proof_valid']:
            click.echo("\tValid")
        else:
            click.echo("\tINVALID")

        click.echo()

    click.echo("Signatures for attribute ID #" + str(attribute['attributeID']) + ':')
    for signature in attribute['signatures_status']['signatures']:
        sig_line = "\t#" + str(signature['signatureID'])

        if signature['revocation']:
            sig_line += " [revoked]"
        elif signature['expired']:
            sig_line += " [expired]"
        elif signature['valid']:
            sig_line += " [valid]"

        sig_line += " by " + signature['signer']
        sig_line += (" [trusted]" if userconfig.is_trusted(attribute['owner']) else " [untrusted]")
        click.echo(sig_line)

    click.echo()
    click.echo("--ATTRIBUTE DATA:")
    click.echo(attribute['data'])


@click.command()
@click.option('--attributetype', help='Attribute type', type=str)
@click.option('--identifier', help='Attribute identifier', type=str)
@click.option('--owner', help='Attribute owner', type=str)
def search(attributetype, identifier, owner):
    """Search for attributes."""
    # Pad identifiers with zeros.
    if identifier is not None:
        if identifier.startswith('0x'): # Hex data.
            identifier = identifier.ljust(66, '0')
        else:
            identifier = identifier.ljust(32, '\x00')

    events = Events()
    attributes = events.filter_attributes(None, owner, identifier)

    for attribute in attributes:
        if attributetype is not None and attributetype != attribute['attributeType']:
            continue

        signatures_status = events.get_attribute_signatures_status(attribute['attributeID'])

        echo_attribute_block(attribute, signatures_status)
        click.echo()


@click.command()
@click.option('--keyid', prompt='Key ID', help='Key ID', type=str)
def ipfsaddpgp(keyid):
    """Add a PGP key attribute to your identity over IPFS."""
    transactions = Transactions()
    click.echo()

    try:
        transactions.add_pgp_attribute_over_ipfs(keyid)
    except ValueError as e:
        click.echo("Error: " + str(e))
        return

    click.echo("Transaction sent.")