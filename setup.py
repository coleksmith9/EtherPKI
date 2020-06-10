
from setuptools import setup

setup(
    name='etherpki',
    version='0.1',
    packages=['etherpki'],
    package_data={'etherpki': ['EtherCLI/etherpki_abi.json']},
    install_requires=[
        'click',
        'jsonrpc-requests',
        'ethereum',
        'rlp',
        'configobj',
        'appdirs',
        'ethereum-rpc-client',
        'python-gnupg',
        'ipfs-api'
    ],
    entry_points='''
        [console_scripts]
        etherpki=etherpki.console:cli
    ''',
)