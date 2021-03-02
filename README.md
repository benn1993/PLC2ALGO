# PLC2ALGO
 Connection of a S7 PLC to the algorand blockchain

## Requirements

1. A PureStake Account and the corresponding API key

2. An Algorand wallet for the TESTNet

3. Siemens Simatic S7 PLC

   This example is tested with an SIMATIC S7-300, more specific a CPU315-2-PN/DP. The is not spedific for this type of S7 and should work with any S7 PLC.

4. A PC. Note that the Siemens Software is only available for windows

5. Siemens Simatic Manager and python 3.6+

6. At least three TestNet Accounts. A tutorial for the generation can be found [here](https://developer.algorand.org/tutorials/create-account-testnet-python/#1-generate-an-algorand-key-pair).

7. A PureStake API key. For more details visit this [tutorial](https://developer.algorand.org/tutorials/getting-started-purestake-api-service/). For this solution the code for the transaction was adapted from this [tutorial](https://developer.algorand.org/tutorials/creating-python-transaction-purestake-api/).

## Description

A detailed description of all the tools and how to set up this solution can be found in `PLC_Solution.pdf`.