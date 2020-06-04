// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.4.16 <0.7.0;


contract EtherPKI {
    struct Attribute {
        address owner;
        string attributeType;
        bool hasProof;
        bytes32 identifier; // ethereum hash code
        string data;
        string dataHash;
    }

    struct Signature {
        address signer;
        uint256 attributeID;
        uint256 expiry;
    }

    struct Revocation {
        uint256 signatureID;
    }

    Attribute[] public attributes;
    Signature[] public signatures;
    Revocation[] public revocations;

    event AttributeAdded(uint indexed attributeID, address indexed owner,
        string attributeType, bool hasProof, bytes32 indexed identifier,
        string data, string dataHash);

    event AttributeSigned(uint indexed signatureID, address indexed signer,
        uint indexed attributeID, uint expiry);

    event SignatureRevoked(uint indexed revocationID, uint indexed signratureID);

    function addAttribute(string memory attributeType, bool hasProof, bytes32 identifier,
        string memory data, string memory dataHash) public
            returns (uint attributeID) {
                // store index in attributeID
                attributeID = attributes.length;

                // resize array
                attributes.push();

                // add element to array
                Attribute memory attribute = attributes[attributeID];

                attribute.owner = msg.sender;
                attribute.attributeType = attributeType;
                attribute.hasProof = hasProof;
                attribute.identifier = identifier;
                attribute.data = data;
                attribute.dataHash = dataHash;
                emit AttributeAdded(attributeID, msg.sender, attributeType, hasProof, identifier, data, dataHash);
    }

    function signAttribute(uint attributeID, uint expiry) public returns (uint signatureID) {
        // stores index in signatureID
        signatureID = signatures.length;

        // increases size of array
        signatures.push();

        // add element to array
        Signature memory signature = signatures[signatureID];

        signature.signer = msg.sender;
        signature.attributeID = attributeID;
        signature.expiry = expiry;
        emit AttributeSigned(signatureID, msg.sender, attributeID, expiry);
    }

    function revokeSignature(uint signatureID) public returns (uint revocationID) {
        if (signatures[signatureID].signer == msg.sender) {
            // stores index
            revocationID = revocations.length;

            // increases size of array
            revocations.push();

            // add element to array
            Revocation memory revocation = revocations[revocationID];

            revocation.signatureID = signatureID;
            emit SignatureRevoked(revocationID, signatureID);
        }
    }
}
