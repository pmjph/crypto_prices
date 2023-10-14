import pandas as pd
from web3 import Web3
import json
import os

# Load the .env file
from dotenv import load_dotenv
load_dotenv()

# Access the INFURA_API_KEY environment variable
INFURA_API_KEY = os.getenv('INFURA_API_KEY')
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_API_KEY}'))

# Load Uniswap V3 Pool ABI
with open('abiContracts/erc20_abi.json', 'r') as f:
    erc20_abi = json.load(f)

# Load Uniswap V3 Pool ABI
with open('abiContracts/uniswap_v3_pool_abi.json', 'r') as f:
    uniswap_v3_pool_abi = json.load(f)

def get_tick(pool_address, block_number):
    pool_contract = w3.eth.contract(address=pool_address, abi=uniswap_v3_pool_abi)
    slot0_data = pool_contract.functions.slot0().call(block_identifier=block_number)
    return slot0_data[1]  # Assuming the tick is the second element in the slot0 data tuple

def get_v3_price_data(token0_address, token1_address, pool_address, start_block, end_block):
    price_data = pd.DataFrame(columns=['block_number', 'price_token0_in_token1', 'price_token1_in_token0'])

    for block_number in range(start_block, end_block + 1):
        tick = get_tick(pool_address, block_number)
        price_token1_in_token0 = 1.0001 ** tick
        price_token0_in_token1 = 1 / price_token1_in_token0

        price_data = price_data.append({
            'block_number': block_number,
            'price_token0_in_token1': price_token0_in_token1,
            'price_token1_in_token0': price_token1_in_token0
        }, ignore_index=True)

    price_data.set_index('block_number', inplace=True)
    return price_data

# Usage:
token0_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # USDC
token1_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'  # ETH
pool_address = '0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8'  # USDC/ETH pool on Uniswap V3
start_block = 12345678
end_block = 12345778

price_data_df = get_v3_price_data(token0_address, token1_address, pool_address, start_block, end_block)
print(price_data_df)


################################################
def get_v3_price_data(token0_address, token1_address, pool_address, start_block, end_block):
    # Create contract instances
    token0_contract = w3.eth.contract(address=token0_address, abi=erc20_abi)
    token1_contract = w3.eth.contract(address=token1_address, abi=erc20_abi)
    
    # Get token decimals
    token0_decimals = token0_contract.functions.decimals().call()
    token1_decimals = token1_contract.functions.decimals().call()
    
    price_data = pd.DataFrame(columns=['block_number', 'price_token0_in_token1', 'price_token1_in_token0'])

    for block_number in range(start_block, end_block + 1):
        tick = get_tick(pool_address, block_number)
        price_token1_in_token0 = (1.0001 ** tick) * (10 ** (token0_decimals - token1_decimals))
        price_token0_in_token1 = 1 / price_token1_in_token0

        price_data = price_data.append({
            'block_number': block_number,
            'price_token0_in_token1': price_token0_in_token1,
            'price_token1_in_token0': price_token1_in_token0
        }, ignore_index=True)

    price_data.set_index('block_number', inplace=True)
    return price_data

#################################################################

def get_v3_price(token0_address, token1_address, pool_address, block_number, token_to_price):
    """
    Get the price of the specified token at a particular block number on Uniswap V3.

    Parameters:
    - token0_address (str): The contract address of token0.
    - token1_address (str): The contract address of token1.
    - pool_address (str): The contract address of the Uniswap V3 pool.
    - block_number (int): The block number at which to get the price.
    - token_to_price (str): Specify which token's price to get ('token0' or 'token1').

    Returns:
    - float: The price of the specified token.
    """
    # Create contract instances
    token0_contract = w3.eth.contract(address=token0_address, abi=erc20_abi)
    token1_contract = w3.eth.contract(address=token1_address, abi=erc20_abi)
    
    # Get token decimals
    token0_decimals = token0_contract.functions.decimals().call()
    token1_decimals = token1_contract.functions.decimals().call()
    
    tick = get_tick(pool_address, block_number)
    price_token1_in_token0 = (1.0001 ** tick) * (10 ** (token0_decimals - token1_decimals))
    price_token0_in_token1 = 1 / price_token1_in_token0
    
    if token_to_price == 'token0':
        return price_token0_in_token1
    elif token_to_price == 'token1':
        return price_token1_in_token0
    else:
        raise ValueError("Invalid token_to_price argument. Must be 'token0' or 'token1'.")

# Example usage:
# Get the price of token0 in terms of token1
price_token0_in_token1 = get_v3_price(token0_address, token1_address, pool_address, block_number, 'token0')

# Get the price of token1 in terms of token0
price_token1_in_token0 = get_v3_price(token0_address, token1_address, pool_address, block_number, 'token1')

###############################################
def create_price_dataframe(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address):
    # Token addresses need to be known or retrieved
    # Assuming you have functions to get the addresses based on pair addresses
    target_token0_address, target_token1_address = get_token_addresses(target_pair_address)
    stable0_token0_address, stable0_token1_address = get_token_addresses(stable_pair0_address)
    stable1_token0_address, stable1_token1_address = get_token_addresses(stable_pair1_address)

    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {'block_number': block_number}
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_v3_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token0')
        price_coin1_in_coin0 = get_v3_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token1')
        
        # Get the price of stablecoins in terms of the base token (e.g., ETH)
        price_stable0_in_base = get_v3_price(stable0_token0_address, stable0_token1_address, stable_pair0_address, block_number, 'token0')
        price_stable1_in_base = get_v3_price(stable1_token0_address, stable1_token1_address, stable_pair1_address, block_number, 'token0')
        
        # Assuming the base token in both stablecoin pairs is the same (e.g., ETH)
        # Calculate and store the price in USD
        data['coin0_price_in_coin1'] = price_coin0_in_coin1
        data['coin1_price_in_coin0'] = price_coin1_in_coin0
        data['coin0_price_in_usd'] = price_coin0_in_coin1 * price_stable0_in_base
        data['coin1_price_in_usd'] = price_coin1_in_coin0 * price_stable1_in_base
        
        # Append the data to the DataFrame
        df = df.append(data, ignore_index=True)
    
    # Set the block_number column as the index of the DataFrame
    df.set_index('block_number', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv('your_file.csv', index=True)
    
    return df

# Assuming get_token_addresses is a function that returns the addresses of token0 and token1 of a pair
def get_token_addresses(pair_address):
    # Create a contract instance
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v3_pool_abi)

    # Call the token0 and token1 functions
    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()

    return token0_address, token1_address


