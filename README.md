# EtherPKI
This is a simple implementation of a blockchain-based PKI system that could be used to mitigate some of the issues with current public key encryption methods used on the Internet.

The basis for this project is using the Ethereum blockchain to utilize smart contracts which allow for users to validate individual attributes of what would be a certificate rather than the whole thing. More info to come later.

This project will be using *solidity* for the smart contract and *python* for the CLI interaction, as well as *Ethereum* for the storage of the contracts.

#### To-Do
1. ~~Create a smart contract that can be added to the blockchain~~
2. ~~Create a testnet of the Ethereum blockchain to use as an example without requiring actual ETH~~
3. Add attributes to the test blockchain and sign them
3. Design a CLI application to interact with the blockchain to add, sign, and revoke attributes in Python
4. Implement a more efficient way (less [gas](https://www.investopedia.com/terms/g/gas-ethereum.asp)) to add and revoke attributes, possibly using [IPFS](https://ipfs.io/)
