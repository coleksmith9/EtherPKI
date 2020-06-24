"""API for EtherPKI events"""

import time

from ethereum import abi
from ethereum import processblock
from ethereum.utils import big_endian_to_int
from ethereum.utils import decode_hex

import ipfshttpclient
from gpgapi import process_proof
from ethapi import ETHERPKI_ABI
from ethapi import ETHERPKI_DEFAULT_ADDRESS
from ethapi import ethclient
from ethapi import encode_api_data

class Events(object):
    def __init__(self, address=ETHERPKI_DEFAULT_ADDRESS):
        """
        Initialization of the event retreiver.

        address: the Ethereum address of the contract
        """
        self.address = address

        self._contracttranslator = abi.ContractTranslator(ETHERPKI_ABI)

    def _get_event_id_by_name(self, event_name):
        """
        Get the name of the event based on its name.

        event_name: the event's name
        """
        for event_id, event in self._contracttranslator.event_data.items():
            if event['name'] == event_name:
                return event_id

    def _get_logs(self, topics, event_name=None):
        """
        Get logs of the events that occur.

        topics:     a list of topics to search based on
        event_name: the name of the event
        """

        # set topic to the ID if the name is specified
        if event_name == None:
            event_topic = None
        else:
            event_topic = self._get_event_id_by_name(event_name)

        # add the event type to the topics
        topics = [event_topic] + topics

        # encode topics to be sent to the eth client
        topics = [encode_api_data(topic) for topic in topics]

        # gets logs from eth client
        logs = ethclient.get_logs(
            from_block='earliest',
            address=self.address,
            topics=topics,
        )
        

        # decode logs using the ABI
        decoded_logs = []
        for log in logs:
            logobj = processblock.Log(
                log['address'][2:],
                [big_endian_to_int(decode_hex(topic[2:])) for topic in log['topics']],
                decode_hex(log['data'][2:])
            )
            decoded_log = self._contracttranslator.listen(logobj, noprint=True)
            decoded_logs.append(decoded_log)

        return decoded_logs

    def filter_attributes(self, attributeID=None, owner=None, identifier=None):
        """
        Filter and get attributes.

        attributeID: the ID of the attribute
        owner: the Ethereum address that owns the attribute
        identifier: the identifier of the attribute
        """
        return self._get_logs([attributeID, owner, identifier], event_name='AttributeAdded')

    def filter_signatures(self, signatureID=None, signer=None, attributeID=None):
        """
        Filter and get signatures.

        signatureID: the ID of the signature
        signer: the Ethereum address that owns the signature
        attributeID: the ID of the attribute
        """
        return self._get_logs([signatureID, signer, attributeID], event_name='AttributeSigned')

    def filter_revocations(self, revocationID=None, signatureID=None):
        """
        Filter and get revocations

        revocationID: the ID of the revocation
        signatureID: the ID of the signature
        """
        return self._get_logs([revocationID, signatureID], event_name='SignatureRevoked')

    def get_attribute_signatures_status(self, attributeID):
        """
        Get all of the signatures of an attribute and check their expiration.

        attributeID: the ID of the attribute

        returns a dictionary representing the signatures' status
        """
        signatures = []
        status = {
            'valid': 0,
            'invalid': 0
        }

        signatures_status = {
            'status': status,
            'signatures': signatures
        }

        # filter signatures for a specified attribute
        rawsignatures = self.filter_signatures(attributeID=attributeID)

        # process the signatures
        for rawsignature in rawsignatures:
            signature = {}

            # add signature properties to the dictionary
            signature.update(rawsignature)

            # check if expired
            signature['expired'] = time.time() > signature['expiry']

            # check if revoked
            rawrevocations = self.filter_revocations(signatureID=signature['signatureID'])

            if len(rawrevocations) > 0:
                signature['revocation'] = rawrevocations
            else:
                signature['revocation'] = False
            # check if valid
            if not signature['expired'] and not signature['revocation']:
                signature['valid'] = True
                status['valid'] += 1
            else:
                signature['valid'] = False
                status['invalid'] += 1

            signatures.append(signature)

        return signatures_status

    def retreive_attributes(self, attributeID):
        """
        Get an attribute, its status, signatures status. Downloads from blockchain if needed.

        attributeID: the ID of the attribute

        returns a dictionary representing the properties of the attribute
        """
        rawattributes = self.filter_attributes(attributeID=attributeID)

        if not rawattributes:
            return None

        attribute = rawattributes[0]
        attribute['signatures_status'] = self.get_attribute_signatures_status(attributeID)

        # download ipfs data if needed
        if attribute['data'].startswith('ipfs-block://'):
            ipfs_key = attribute['data'][len('ipfs-block://'):]
            ipfshttpclient.Client.get(ipfs_key)

        # verify PGP proof
        if attribute['attributeType'] == 'pgp-key':
            attribute['proof_valid'] = self.verify_attribute_pgp_proof(attribute)

        # set proof validity to unknown if the attribute has proof but unable to be processed
        if attribute['has_proof'] and 'proof_valid' not in attribute:
            attribute['proof_valid'] = None

        return attribute

    def verify_attribute_pgp_proof(self, attribute):
        """
        Verify the PGP proof of an attribute.

        Return True if valid, False if invalid, or None if the proof is unspecified.

        attribute: the attribute to be checked.
        """

        # case for unspecified proof
        if not attribute['has_proof']:
            return None

        proof = process_proof(attribute['data'])

        if not proof:
            return False

        (proof_address, proof_fingerprint) = proof

        if (
            # check that the fingerprints match
            proof_fingerprint.decode('hex') == attribute['identifier'].rstrip('\x00')
            # check that the ethereum addresses match
            and proof_address == '0x' + attribute['owner']
            ):
            return True

        return False