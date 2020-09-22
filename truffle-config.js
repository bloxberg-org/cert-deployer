module.exports = {
  networks: {
development: {
      provider: () =>
        new HDWalletProvider(mnemonic, 'https://core.bloxberg.org'),
      network_id: '8995',
      gas: 9000000,
      gasPrice: 400000000000000,
      from: '0xD748BF41264b906093460923169643f45BDbC32e'
    }
  },
  compilers: {
    solc: {
      version: "0.6.4",
      settings: {
        optimizer: {
            enabled: true,
            runs: 200
        },
       //evmVersion: "byzantium"
      }
    }
}
}
