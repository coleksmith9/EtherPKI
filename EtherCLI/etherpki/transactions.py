"""API for adding transactions to the EtherPKI network"""

import io

from ethereum import abi
from ethapi import ETHERPKI_ABI
from ethapi import ETHERPKI_DEFAULT_ADDRESS
from ethapi import ethclient
from ethapi import encode_api_data
from gpgapi import generate_pgp_attribute_data
import ipfshttpclient


class Transactions(object):
    def __init__(self, from_address=None, to_address=ETHERPKI_DEFAULT_ADDRESS):
        """Initialize transactions.

        from_address:   the Ethereum address transactions should come from
        to_address:     the Ethereum EtherPKI contract address.
        """
        if from_address is None:
            # Uses the first Ethereum account address if none is specified.
            self.from_address = ethclient.get_accounts()[0]
        else:
            self.from_address = from_address
        
        self.to_address = to_address

        # initialize contract ABI
        self._contracttranslator = abi.ContractTranslator(ETHERPKI_ABI)

    def _send_transaction(self, data):
        """ Sends a transaction to the Ethereum client.

        data:   the data to be sent.
        """
        return ethclient.send_transaction(
            _from=self.from_address,
            to=self.to_address,
            data=encode_api_data(data),
            gas=100 # TODO: modify?
        )

    def add_attribute(self, attributetype, has_proof, identifier, data, datahash):
        """Sends a transaction to add an attribute.

        attributetype:  the type of attribute.
        has_proof:      True if the attribute has proof, otherwise false.
        identifier:     the indexable identifier of the attribute.
        data:           the data of the attribute.
        datahash:       the hash of the data if it is stored off of the blockchain.
        """
        args = [attributetype, has_proof, identifier, data, datahash]
        data = self._contracttranslator.encode('addAttribute', args)
        return self._send_transaction(data)

    def add_attribute_with_hash(self, attributetype, has_proof, identifier, data):
        """Sends a transaction to add an attribute, but it calculates the datahash automatically.

        attributetype:  the type of attribute.
        has_proof:      True if the attribute has proof, otherwise false.
        identifier:     the indexable identifier of the attribute.
        data:           the data of the attribute.
        """
        datahash = '' # TODO: calculate hash
        return self.add_attribute(attributetype, has_proof, identifier, data, datahash)

    def add_attribute_over_ipfs(self, attributetype, has_proof, identifier, data):
        """Sends a transaction to add an attribute & stores the data on IPFS.

        attributetype:  the type of attribute.
        has_proof:      True if the attribute has proof, otherwise false.
        identifier:     the indexable identifier of the attribute.
        data:           the data of the attribute.
        """

        # stores the data as an IPFS block and gets the key.
        with ipfshttpclient.connect() as client:
            ipfs_key = client.block.put(io.StringIO(data))['Key']

        # generates the EtherPKI-specific URI for the IPFS block
        ipfs_uri = 'ipfs-block://' + ipfs_key

        # adds the attribute by automatically calculating the hash
        self.add_attribute_with_hash(attributetype, has_proof, identifier, ipfs_uri)

    def add_pgp_attribute_over_ipfs(self, keyid):
        """Send a transaction to add an identity PGP attribute, storing the data on IPFS.

        keyid:  the ID of the PGP key.
        """
        # generate PGP attribute data and get identifier
        (fingerprint, data) = generate_pgp_attribute_data(keyid, self.from_address)

        # express identifier as fingerprint in binary format
        identifier = fingerprint.decode('hex')

        self.add_attribute_over_ipfs(
            attributetype='pgp-key',
            has_proof=True,
            identifier=identifier,
            data=data,
        )


    def sign_attribute(self, attributeID, expiry):
        """Send a transaction to sign an attribute.

        attributeID:    the ID of the attribute.
        expiry:         the expiry time of the attribute in unix time.
        """

        args = [attributeID, expiry]
        data = self._contracttranslator.encode('signAttribute', args)
        return self._send_transaction(data)

    def revoke_signature(self, signatureID):
        """Sends a transaction to revoke a signature.

        signatureID:    the ID of the signature.
        """

        args = [signatureID]
        data = self._contracttranslator.encode('revokeSignature', args)
        return self._send_transaction(data)