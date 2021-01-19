# cert-deployer

This project deploys smart contracts to the Ethereum blockchain enabling the
cert-issuer to modify a certificates' or certificate batches' status respectively.

The related forked repositories of the original cert-issuer and cert-tools are linked
below.

https://github.com/bloxberg-org/cert-issuer

https://github.com/bloxberg-org/cert-tools

## How deploying smart contract works

After deploying the contract, the cert-deployer links the contract to the potential
issuer's ENS domain [(?)](https://decrypt.co/resources/ethereum-name-service-ens-explained-guide-learn) – more specific sets the contract's address as the ENS entry's
address attribute. This input, can, of course, be changed when deploying another
contract, but please note that addresses can only be overwritten, since the ENS
domain can point to only one (contract) address.

## Setting the cert-deployer up

The cert-deployer requires some preparation before it can be used. This preparation
includes certain administrative as well as technical steps to be fulfilled being
explained a bit more in detail below.

### Prerequisites

We highly recommend to use the cert-deployer within a virtual environment! See [recommendations](https://github.com/bloxberg-org/cert-issuer/blob/master/docs/virtualenv.md). After
activating the virtual environment, please execute:

`$ python setup.py install`

All necessary dependencies will be installed afterwards. Further required are also
the setups of an Ethereum wallet (the wallet has to be registered in the Ethereum
chain that being intended to be used later).

Our recommended tool for creating and managing the wallet is [Metamask](https://metamask.io).

### Configuring cert-deployer

The last step to be executed is completing the configuration inputs (optional:
adjusting the smart contract). The conf_template.ini file includes the following parameters:

```
deploying_address = <Your Ethereum address>

chain = <ethereum_ropsten|ethereum_mainnet|bloxberg>
node_url = <ethereum web3 public node url (e.g. infura)>

ens_name = <Your ENS name registered with your ethereum address>
overwrite_ens_link = <Do you want to overwrite a present link to a smart contract? True/False>

# usb_name is the folder where the private key is and key_file is the file name.
usb_name= <path-to-keyfile-folder>
key_file= <keyfile-file-name>
```

Notes:

1. The ethereum address corresponds to the respective wallet address.
1. The private key file [should be](https://eth-account.readthedocs.io/en/latest/eth_account.html#eth_account.account.Account.from_key) a raw private key: a hex str, bytes or int
1. Potential issuers can set up their own infura nodes or use publicly shared ones.
1. If a smart contract shall be deployed and used by an already to another contract
   linked ENS name, the `overwrite_ens_link` has to be set to `True` in order to prevent
   accidental overwriting.
1. The cert-deployer uses a separate class to access the wallet's private key which
   should be stored under the path provided. Ideally, that location is not permanently
   accessible (e.g. USB stick) improving security.

Rename the conf_template.ini to conf_eth.ini once filled with your parameters. You can find the existing bloxberg config in `conf_eth.ini` of this repository.

### Quick steps

Execute these instructions step-by-step:

1. ensure you have installed [solidity compiler (solc)](https://solidity.readthedocs.io/en/v0.5.3/installing-solidity.html)
1. clone github repo `$ git clone https://github.com/bloxberg-org/cert-deployer.git`
1. Activate virtual environment `$ virtualenv <virtual_env_name>/bin/activate`
1. install dependencies within virtualenv `$ python setup.py install`
1. add required information incl. paths and connection data into conf_eth.ini
1. deploy smart contract `$ python cert_deployer/deploy.py`

... install the forked cert-issuer- (and cert-tools) repositories for benefitting
from the whole framework (links above).
