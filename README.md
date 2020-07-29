# EtherPKI
This is a simple implementation of a blockchain-based PKI system that could be used to mitigate some of the issues with current public key encryption methods used on the Internet.

The basis for this project is using the Ethereum blockchain to utilize smart contracts which allow for users to validate individual attributes of what would be a certificate rather than the whole thing. More info to come later.

This project will be using *solidity* for the smart contract and *python* for the CLI interaction, as well as *Ethereum* for the storage of the contracts.

#### Installation Instructions
Complete all of the following steps in order to use EtherPKI on a local version of the Ethereum blockchain.

To install an Ethereum Test Network, follow [these instructions](https://medium.com/swlh/how-to-set-up-a-private-ethereum-blockchain-c0e74260492c).

To install EtherPKI:
```
$ git clone https://github.com/coleksmith9/EtherPKI.git
$ cd EtherPKI/EtherCLI/
$ pip3 install --user --editable .
```

Start your test network and run EtherPKI to add attributes to your entity. From here you need to add another address to your network to sign it or revoke it.
