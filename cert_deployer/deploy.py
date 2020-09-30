import json
import logging
import config
import re
from solcx import get_solc_version, set_solc_version, compile_standard, compile_files, install_solc, compile_source
#from solc import compile_standard, compile_files
from ens import ENS
from blockchain_handlers.connectors import MakeW3, ContractConnection
import blockchain_handlers.signer as signer
import blockchain_handlers.path_tools as tools


class ContractDeployer(object):
    '''
    Compiles, signes and deploys a smart contract on the ethereum blockchain
    '''
    def __init__(self):
        '''
        Defines blockchain, initializes ethereum wallet, calls out compilation
        and deployment functions
        '''
        self.app_config = config.get_config()
        w3Factory = MakeW3(self.app_config)
        self._w3 = w3Factory.w3
        self._acct = w3Factory.account
        self._ens_name = self.app_config.ens_name

    def check_balance(self):
        estimated_required_gas = 500000
        gas_price = self._w3.eth.gasPrice

        gas_balance = self._w3.eth.getBalance(self._acct)
        if gas_balance < estimated_required_gas * gas_price:
            logging.error("Your account balance is not sufficient to perform all transactions.")
            exit()

    def do_deploy(self):
        '''
        Leads the deployment process step-by-step
        '''
        self.check_balance()
        self._security_check()
        self._compile_contract()
        self._deploy()
        self._assign_name()
        self._assign_ens()

    def _security_check(self):
        '''
        Makes sure that an existing contract does not get overwritten unintensionally
        '''
        # connect to public resolver
        ens_resolver = ContractConnection("ens_resolver", self.app_config)
        node = ENS.namehash(self._ens_name)
        temp = ens_resolver.functions.call("addr", node)

        # check if ens address is already linked to a contract and potential overwriting intended
        if temp != "0x0000000000000000000000000000000000000000" and self.app_config.overwrite_ens_link is not True:
            logging.error("A smart Contract already deployed on this domain and overwrite_ens_link is not True.")
            exit("Stopping process.")

    def _compile_contract(self):
        install_solc('v0.6.2')
        set_solc_version('v0.6.2')
        '''
        Compiles smart contract, creates bytecode and abi
        '''
        # loading contract file data
        with open(tools.get_contr_path(), "r") as source_file:
            source_raw = source_file.read()
 
        # loading configuration data
        with open(tools.get_compile_data_path()) as opt_file:
            raw_opt = opt_file.read()
            opt = json.loads(raw_opt)
        #opt["sources"]["ResearchCertificate.sol"]["content"] = source_raw
        compiled_sol = compile_source(source_raw)
        contract_interface = compiled_sol['<stdin>:' + 'ResearchCertificate']
        self.bytecode = contract_interface['bin']
        self.abi = contract_interface['abi']

        logging.info("Succesfully compiled contract")

    def _deploy(self):
        '''
        Signs raw transaction and deploys contract on the blockchain
        '''
        # building raw transaction
        contract = self._w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        estimated_gas = contract.constructor().estimateGas()
        construct_txn = contract.constructor().buildTransaction({
            'nonce': self._w3.eth.getTransactionCount(self._acct),
            'gas': estimated_gas*2
        })

        # signing and sending transaction
        signed = signer.sign_transaction(self.app_config, construct_txn)
        logging.info("Transaction deployment pending...")

        tx_hash = self._w3.eth.sendRawTransaction(signed.rawTransaction)
        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        self.contr_address = tx_receipt.contractAddress

        logging.info("Deployed the contract at address %s,  using the following amount of gas: %s", self.contr_address, tx_receipt.gasUsed)
        
    def _assign_name(self):
    
        # prepare domain
        

        url = self.app_config.ens_name
        url = re.sub('\.berg$', '', url)
        
        
        labelhash = self._w3.sha3(text=url);
        ens_registrar = ContractConnection("ens_registrar", self.app_config)
        print(ens_registrar)
 
	# set subdomain
        tx_hash = ens_registrar.functions.transact("register", labelhash, self.app_config.deploying_address)
        print(tx_hash)
        

        

    def _assign_ens(self):
        '''
        Updates ENS entries
        '''
        # prepare domain
        ens_domain = self._ens_name
        node = ENS.namehash(ens_domain)

        # connect to registry and resolver
        ens_registry = ContractConnection("ens_registry", self.app_config)
        ens_resolver = ContractConnection("ens_resolver", self.app_config)

        
        # set resolver
        curr_resolver = ens_registry.functions.call("resolver", node)
        if curr_resolver == "0x0000000000000000000000000000000000000000":
            resolver_address = ContractConnection.get_ens_address(self.app_config.chain, "ens_resolver")
            ens_registry.functions.transact("setResolver", node, resolver_address)
        else:
            logging.info("Resolver already set for %s", ens_domain)

        # set ABI
        ens_resolver.functions.transact("setABI", node, 1, json.dumps(self.abi).encode())

        # set address
        self.contr_address = self._w3.toChecksumAddress(self.contr_address)
        ens_resolver.functions.transact("setAddr", node, self.contr_address)
        ens_resolver.functions.transact("setName", node, ens_domain)

        # get data for output
        addr = ens_resolver.functions.call("addr", node)
        name = ens_resolver.functions.call("name", node)

        logging.info("SUCCESS – Set contract with address %s to name %s", addr, name)
        

if __name__ == '__main__':
    '''
    Calls respective functionatilites
    '''
    ContractDeployer().do_deploy()
