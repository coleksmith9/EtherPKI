"""Interface for accessing Ethereum client and EtherPKI contracts."""

import json
import os

import eth_rpc_client

import EtherCLI

# contract addresses
ETHERPKI_DEFAULT_ADDRESS = ''
ETHERPKI_ABI = json.load(open(os.path.join(os.path.dirname(EtherCLI.__file__), 'etherpki_abi.json')))

ethclient = eth_rpc_client.Client(host='127.0.0.1', port='8545')

def encode_api_data(data):
    """Prepares data to be sent to the Ethereum client."""

    if data is None:
        return None
    elif type(data) == str and data.startswith('0x'):
        # data is already hex encoded
        return data
    elif type(data) in [bool, int]:
        # use the native hex() function
        return hex(data)
    else:
        return '0x' + data.encode().hex() #TODO: verify its working
