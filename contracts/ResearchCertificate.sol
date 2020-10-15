pragma solidity ^0.6.0;

import "contracts/ERC721Full.sol";
import "contracts/Counters.sol";
import "contracts/Ownable.sol";

contract ResearchCertificate is ERC721Full, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    constructor() ERC721Full("ResearchObjectCertification", "ROC") public {
    }

    function createCertificate(address recipient, string memory tokenURI, string memory tokenHash) onlyOwner public returns (uint256) {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);
        _setTokenHash(newItemId, tokenHash);

        return newItemId;
    }

    function updateTokenURI(uint256 tokenID, string memory tokenURI) onlyOwner public returns (string memory) { 

	_setTokenURI(tokenID, tokenURI);
	return tokenURI;
    }
}
