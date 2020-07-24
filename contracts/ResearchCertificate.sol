pragma solidity ^0.6.0;

import "/home/james/bloxberg-certs/cert-deployer/contracts/ERC721Full.sol";
import "/home/james/bloxberg-certs/cert-deployer/contracts/Counters.sol";

contract ResearchCertificate is ERC721Full {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    constructor() ERC721Full("DigitalLabs", "SARI") public {
    }

    function createCertificate(address recipient, string memory tokenURI, string memory tokenHash) public returns (uint256) {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);
        _setTokenHash(newItemId, tokenHash);

        return newItemId;
    }
}
