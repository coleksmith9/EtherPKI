"""Configuration management"""

import os

from appdirs import user_config_dir
from configobj import ConfigObj

try:
    os.makedirs(user_config_dir("etherpki"))
except OSError:
    if not os.path.isdir(user_config_dir("etherpki")):
        raise

configfile = os.path.join(user_config_dir("etherpki"), "config.ini")

config = ConfigObj(configfile)

if 'truststore' not in config:
    config['truststore'] = {}


def trust(address):
    """Adds an address to the truststore"""

    config['truststore'][address] = True

def untrust(address):
    """Removes an address from the truststore"""

    del config['truststore'][address]

def is_trusted(address):
    """Returns true if an address is in the truststore & is trusted"""

    return address in config['truststore'] and config['truststore'][address]

def get_trusted():
    """Returns a list of trusted Ethereum addresses"""
    return config['truststore'].keys()