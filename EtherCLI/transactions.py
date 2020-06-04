"""API for adding transactions to the EtherPKI network"""

import io

from ethereum import abi
from ethapi import ETHERPKI_ABI
from ethapi import ETHERPKI_DEFAULT_ADDRESS
from ethapi import ethclient
from ethapi import encode_api_data


class Transactions(object):
    def __init__(self, from_address=None, to_address=ETHERPKI_DEFAULT_ADDRESS):
        """Initialize transactions.

        from_address: the Ethereum address transactions should come from
        to_address: the Ethereum EtherPKI contract address.
        """
        if from_address is None:
            # Uses the first Ethereum account address if none is specified.
            self.from_address = ethclient.get_accounts()[0]
        else:
            self.from_address = from_address
        
        self.to_address = to_address

        # initialize contract ABI
        self._contracttranslator = abi.ContractTranslator(ETHERPKI_ABI)