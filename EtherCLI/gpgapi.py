"""API for interacting with GPG."""

import shutil
import tempfile

import gnupg

gpgclient = gnupg.GPG()

class tempGPG(object):
    """a class for creating a temporary GPG instance separate from the user's GPG directory."""

    def __init__(self):
        # create the temporary directory
        self.tempdir = tempfile.mkdtemp()

        # initialize the interface
        self.gpgclient = gnupg.GPG(gnupghome=self.tempdir)

    def destroy(self):
        shutil.rmtree(self.tempdir)

def generate_pgp_attribute_data(keyid, address):
    """Generates the public key and cryptographic proof for a PGP attribute.

    returns a tuple of (fingerprint, data).

    keyid:      the ID of the PGP key.
    address:    Ethereum address to generate cryptographic proof for.
    """

    # export the public key
    public_key = gpgclient.export_keys(keyid, minimal=True)

    # use the temporary GPG interface to key that only one key has been exported and get its fingerprint
    tempgpg = tempGPG()
    try:
        import_results = tempgpg.gpgclient.import_keys(public_key)

        # check that only 1 key was imported
        if import_results.counts != 1: #TODO: verify that it should be 'counts'
            raise ValueError("Invalid PGP key ID specified")

        fingerprint = str(import_results.fingerprints[0])
    finally:
        tempgpg.destroy()

    # generate the proof signature
    proof = gpgclient.sign('Ethereum addres: ' + address, keyid=fingerprint)


    if not proof:
        raise ValueError("A PGP key was specified that does not have a cooresponding secret key")

    # concatenate public key & proof
    data = public_key + '\n' + proof

    return (fingerprint, data)

def process_proof(data):
    """Process the cryptographic proof of PGP attribute data.

    returns a tuple of (Ethereum address, PGP key fingerprint) if the proof is valid, otherwise False
    
    data:   the PGP attribute data.
    """

    key = ''
    signature = ''
    address = ''
    key_mode = False
    signature_mode = False

    # extract key, signature, and address
    for line in data.split('\n'):
        line = line.strip()
        if line == '-----END PGP PUBLIC KEY BLOCK-----':
            key_mode = False
            key += line + '\n'
        elif line == '-----BEGIN PGP PUBLIC KEY BLOCK-----' or key_mode:
            if not key_mode:
                key_mode = True
            key += line + '\n'
        elif line == '-----END PGP SIGNATURE-----':
            signature_mode = False
            signature += line + '\n'
        elif line == '-----BEGIN PGP SIGNED MESSAGE-----' or signature_mode:
            if not signature_mode:
                signature_mode = True
            if line.startswith('Ethereum address: '):
                address = line[len('Ethereum address: '):]
            signature += line + '\n'

    # create a temporary keychain and import the key
    tempgpg = tempGPG()
    tempgpg.gpgclient.import_keys(key)

    verified = tempgpg.gpgclient.verify(signature)

    tempgpg.destroy()

    if not verified:
        return False

    return (address, verified.fingerprint)
