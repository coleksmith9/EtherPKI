"""IPFS Interface"""

import ipfsApi

# opens connection to ipfs on localhost on port 5001
ipfsclient = ipfsApi.Client('127.0.0.1', 5001)