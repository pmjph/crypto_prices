from web3 import Web3
import json
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Access the INFURA_API_KEY environment variable
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_API_KEY}'))

# Load Uniswap V3 Pool ABI
with open('abiContracts/erc20_abi.json', 'r') as f:
    erc20_abi = json.load(f)

# Load Uniswap V2 Pair ABI
with open('abiContracts/uniswap_v2_pool_abi.json', 'r') as f:
    uniswap_v2_pair_abi = json.load(f)

token0_address = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 # USDC
token1_address = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 # ETH
pair_address = 0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc # USDC/ETH

# Create contract instances
token0_contract = w3.eth.contract(address=token0_address, abi=erc20_abi)
token1_contract = w3.eth.contract(address=token1_address, abi=erc20_abi)
pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)

# Get token decimals
token0_decimals = token0_contract.functions.decimals().call()
token1_decimals = token1_contract.functions.decimals().call()

# Get reserves at a specific block
block_number = 12345678
reserves = pair_contract.functions.getReserves().call(block_identifier=block_number)

# Calculate the price
reserve0 = reserves[0] / (10 ** token0_decimals)
reserve1 = reserves[1] / (10 ** token1_decimals)

price_token0_in_token1 = reserve0 / reserve1

price_token1_in_token0 = reserve1 / reserve0


#####################################################
def get_decimals(token_address):
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    return token_contract.functions.decimals().call()

####################################################
def get_token0_price(token0_address, token1_address, pair_address, block_number):
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)
    reserves = pair_contract.functions.getReserves().call(block_identifier=block_number)

    token0_decimals = get_decimals(token0_address)
    token1_decimals = get_decimals(token1_address)

    reserve0 = reserves[0] / (10 ** token0_decimals)
    reserve1 = reserves[1] / (10 ** token1_decimals)

    price_token0_in_token1 = reserve1 / reserve0
    return price_token0_in_token1
####################################################
def get_token1_price(token0_address, token1_address, pair_address, block_number):
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)
    reserves = pair_contract.functions.getReserves().call(block_identifier=block_number)

    token0_decimals = get_decimals(token0_address)
    token1_decimals = get_decimals(token1_address)

    reserve0 = reserves[0] / (10 ** token0_decimals)
    reserve1 = reserves[1] / (10 ** token1_decimals)

    price_token1_in_token0 = reserve0 / reserve1
    return price_token1_in_token0


####################################################

def get_price_data(token0_address, token1_address, pair_address, start_block, end_block):
    # Create an empty DataFrame
    price_data = pd.DataFrame(columns=['block_number', 'price_token0_in_token1', 'price_token1_in_token0'])

    # Loop through the block range
    for block_number in range(start_block, end_block + 1):
        # Get the prices at the current block
        price_token0_in_token1 = get_token0_price(token0_address, token1_address, pair_address, block_number)
        price_token1_in_token0 = get_token1_price(token0_address, token1_address, pair_address, block_number)

        # Append the prices and block number to the DataFrame
        price_data = price_data.append({
            'block_number': block_number,
            'price_token0_in_token1': price_token0_in_token1,
            'price_token1_in_token0': price_token1_in_token0
        }, ignore_index=True)

    # Set the block_number column as the index of the DataFrame
    price_data.set_index('block_number', inplace=True)

    return price_data

# Usage:
# Replace the following values with the actual addresses and block numbers
token0_address = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'  # USDC
token1_address = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'  # ETH
pair_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # USDC/ETH
start_block = 12345678
end_block = 12345778

# Get the price data
price_data_df = get_price_data(token0_address, token1_address, pair_address, start_block, end_block)
print(price_data_df)
####################################################

def get_price_data(token0_address, token1_address, pair_address, start_block, end_block):
    # Create an empty DataFrame
    price_data = pd.DataFrame(columns=['block_number', 'price_token0_in_token1', 'price_token1_in_token0'])

    # Loop through the block range
    for block_number in range(start_block, end_block + 1):
        # Get the prices at the current block
        price_token0_in_token1 = get_token0_price(token0_address, token1_address, pair_address, block_number)
        price_token1_in_token0 = get_token1_price(token0_address, token1_address, pair_address, block_number)

        # Append the prices and block number to the DataFrame
        price_data = price_data.append({
            'block_number': block_number,
            'price_token0_in_token1': price_token0_in_token1,
            'price_token1_in_token0': price_token1_in_token0
        }, ignore_index=True)

    # Set the block_number column as the index of the DataFrame
    price_data.set_index('block_number', inplace=True)

    return price_data

############################################################

def create_price_dataframe(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {'block_number': block_number}
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_price(target_pair_address, block_number)
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price of stablecoins in terms of the base token (e.g., ETH)
        price_stable0_in_base = get_price(stable_pair0_address, block_number)
        price_stable1_in_base = get_price(stable_pair1_address, block_number)
        
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
    
    return df

# Define the addresses of the pairs
target_pair_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # coin0_coin1
stable_pair0_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # stable_coin0
stable_pair1_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # stable_coin1

# Call the function to create the DataFrame
start_block = 12345678
end_block = 12345778
price_df = create_price_dataframe(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address)

# Now price_df contains the pricing data for each block number in the specified range

############################################################
def get_v2_price(token0_address, token1_address, pair_address, block_number, token_to_price):
    """
    Get the price of the specified token at a particular block number.

    Parameters:
    - token0_address (str): The contract address of token0.
    - token1_address (str): The contract address of token1.
    - pair_address (str): The contract address of the Uniswap V2 pair.
    - block_number (int): The block number at which to get the price.
    - token_to_price (str): Specify which token's price to get ('token0' or 'token1').

    Returns:
    - float: The price of the specified token.
    """
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)
    reserves = pair_contract.functions.getReserves().call(block_identifier=block_number)

    token0_decimals = get_decimals(token0_address)
    token1_decimals = get_decimals(token1_address)

    reserve0 = reserves[0] / (10 ** token0_decimals)
    reserve1 = reserves[1] / (10 ** token1_decimals)

    if token_to_price == 'token0':
        return reserve1 / reserve0
    elif token_to_price == 'token1':
        return reserve0 / reserve1
    else:
        raise ValueError("Invalid token_to_price argument. Must be 'token0' or 'token1'.")

# Example usage:
# Get the price of token0 in terms of token1
price_token0_in_token1 = get_v2_price(token0_address, token1_address, pair_address, block_number, 'token0')

# Get the price of token1 in terms of token0
price_token1_in_token0 = get_v2_price(token0_address, token1_address, pair_address, block_number, 'token1')

############################################################

def create_price_dataframe(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {'block_number': block_number}
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_price(target_pair_address, block_number)
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price of stablecoins in terms of the base token (e.g., ETH)
        price_stable0_in_base = get_price(stable_pair0_address, block_number)
        price_stable1_in_base = get_price(stable_pair1_address, block_number)
        
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
    
    return df

# Define the addresses of the pairs
target_pair_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # coin0_coin1
stable_pair0_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # stable_coin0
stable_pair1_address = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'  # stable_coin1

# Call the function to create the DataFrame
start_block = 12345678
end_block = 12345778
price_df = create_price_dataframe(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address)


############################################################
def get_token_addresses_v2(pair_address):
    # Create a contract instance
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)

    # Call the token0 and token1 functions
    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()

    return token0_address, token1_address

############################################################
def create_price_dataframe_v2(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    # Get the token addresses for each pair
    target_token0_address, target_token1_address = get_token_addresses_v2(target_pair_address)
    stable0_token0_address, stable0_token1_address = get_token_addresses_v2(stable_pair0_address)
    stable1_token0_address, stable1_token1_address = get_token_addresses_v2(stable_pair1_address)
    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {'block_number': block_number}
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_v2_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token0')
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price of stablecoins in terms of the base token (e.g., ETH)
        price_stable0_in_base = get_v2_price(stable0_token0_address, stable0_token1_address, stable_pair0_address, block_number, 'token0')
        price_stable1_in_base = get_v2_price(stable1_token0_address, stable1_token1_address, stable_pair1_address, block_number, 'token0')
        
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

