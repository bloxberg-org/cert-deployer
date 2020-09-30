import os
import json
import logging

from web3 import Web3, HTTPProvider

import config
import blockchain_handlers.path_tools as tools
import blockchain_handlers.signer as signer

ENS_CONTRACTS = {
    'ethereum_mainnet': {
        'ens_registry': '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e',
        'ens_resolver': '0xDaaF96c344f63131acadD0Ea35170E7892d3dfBA'
        },
    'ethereum_ropsten': {
        'ens_registry': '0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e',
        'ens_resolver': '0x42D63ae25990889E35F215bC95884039Ba354115'
        },
    'bloxberg': {
	'ens_registry': '0xb9F5cd1e334aCEd748bA1422b8a08c548ddBc73D',
        'ens_resolver': '0x56D608448b20DB47559b3aD76ef18c5Bdac4d50D',
        'ens_registrar': '0x1C242FE4Dc151aB4e5932fc82e50c9a8E749ebEF'
	}
    }


class MakeW3(object):
    '''
    Defines an ethereum node that will be used for communication with the
    ethereum blockchain and initializes the account data
    '''
    def __init__(self, app_config):
        self.url = app_config.node_url
        self.w3 = self._create_w3_obj()
        self.account = app_config.deploying_address
        self.w3.eth.defaultAccount = self.account

    def _create_w3_obj(self):
        '''
        Instantiates a web3 connection with ethereum node
        '''
        return Web3(HTTPProvider(self.url))


class ContractConnection(object):
    '''
    Collects abi, address, contract data and instantiates a contract object
    '''
    def __init__(self, contract_name, app_config):
        self.current_chain = app_config.chain
        self.contract_name = contract_name
        self.w3Factory = MakeW3(app_config)
        self.w3 = self.w3Factory.w3
        self.contract_obj = self._create_contract_object()
        self.functions = self.ContractFunctions(self.w3Factory, self.contract_obj, app_config)

    def _create_contract_object(self):
        '''
        Returns contract address and abi
        '''
        address = self._get_address()
        address = self.w3.toChecksumAddress(address)
        abi = self._get_abi()
        return self.w3.eth.contract(address=address, abi=abi)

    def _get_abi(self):
        '''
        Returns smart contract abi stored in data directory
        '''
        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, f"data/{self.contract_name}_abi.json")

        with open(path, "r") as f:
            raw = f.read()
        abi = json.loads(raw)

        return abi

    def _get_address(self):
        '''
        Returns transaction address
        '''
        return ENS_CONTRACTS[self.current_chain][self.contract_name]

    def get_ens_address(chain, contract_name):
        '''
        Returns transaction address
        '''
        return ENS_CONTRACTS[chain][contract_name]


    class ContractFunctions(object):
        '''
        Prepares and executes transactions and calls
        '''
        def __init__(self, w3Factory, contract_obj, app_config):
            self.app_config = app_config
            self.w3Factory = w3Factory
            self.w3 = self.w3Factory.w3
            self._contract_obj = contract_obj
            self._acct = self.w3Factory.account

        def _get_tx_options(self, estimated_gas):
            '''
            Returns raw transaction
            '''
            return {
                'nonce': self.w3.eth.getTransactionCount(self._acct),
                'gas': estimated_gas*2
            }

        def transact(self, method, *argv):
            '''
            Sends a signed transaction on the blockchain and waits for a response
            '''
            # gas estimation
            estimated_gas = self._contract_obj.functions[method](*argv).estimateGas()

            # preparing transaction
            tx_options = self._get_tx_options(estimated_gas)
            construct_txn = self._contract_obj.functions[method](*argv).buildTransaction(tx_options)
            signed = signer.sign_transaction(self.app_config, construct_txn)

            # sending transaction
            logging.info("Transaction %s pending...", str(method))
            tx_hash = self.w3.eth.sendRawTransaction(signed.rawTransaction)
            tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
            logging.info("Executed transaction: %s, using the following amount of gas: %s", str(method), str(tx_receipt.gasUsed))

        def call(self, method, *argv):
            '''
            Calls data
            '''
            return self._contract_obj.functions[method](*argv).call()
