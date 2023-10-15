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


#####################################################
start_block = 11504323 
end_block = 11506033
target_pair_address = 0xc5ed7350e0fb3f780c756ba7d5d8539dc242a414 # ETH-DUCK
stable_pair1_address = 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc # USDC/ETH
stable_pair0_address = 0xe93dc496dbc669d7ee4f03b0eb0a10bb13a4b2a4 # USDC/DUCK
target_pair_address_stable = 0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc # USDC/ETH

#####################################################
def get_decimals(token_address):
    token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
    return token_contract.functions.decimals().call()

############################################################
def get_token_addresses_v2(pair_address):
    # Create a contract instance
    pair_contract = w3.eth.contract(address=pair_address, abi=uniswap_v2_pair_abi)

    # Call the token0 and token1 functions
    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()

    return token0_address, token1_address


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

############################################################
def create_price_dataframe_v2(start_block, end_block, target_pair_address, stable_pair0_address, stable_pair1_address, file_name='your_file.csv'):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    # Get the token addresses for each pair
    target_token0_address, target_token1_address = get_token_addresses_v2(target_pair_address) # WBTC/ETH
    stable0_token0_address, stable0_token1_address = get_token_addresses_v2(stable_pair0_address) # USDC/WBTC
    stable1_token0_address, stable1_token1_address = get_token_addresses_v2(stable_pair1_address) # USDT/ETH
    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {'block_number': block_number}
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_v2_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token0')
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price token in term of stable coin(e.g., ETH)
        price_stable0_token1_in_stable = get_v2_price(stable0_token0_address, stable0_token1_address, stable_pair0_address, block_number, 'token1')
        price_stable1_token1_in_stable = get_v2_price(stable1_token0_address, stable1_token1_address, stable_pair1_address, block_number, 'token1')
        
        # Assuming the base token in both stablecoin pairs is the same (e.g., ETH)
        # Calculate and store the price in USD
        data['coin0_price_in_coin1'] = price_coin0_in_coin1
        data['coin1_price_in_coin0'] = price_coin1_in_coin0
        data['coin0_price_in_usd'] = price_stable0_token1_in_stable
        data['coin1_price_in_usd'] = price_stable1_token1_in_stable
        
        # Append the data to the DataFrame
        df = df.append(data, ignore_index=True)
    
    # Set the block_number column as the index of the DataFrame
    df.set_index('block_number', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv(file_name, index=True)
    
    return df

############################################################
def create_price_dataframe_stable_v2(start_block, end_block, target_pair_address_stable, file_name='your_file.csv'):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    # Get the token addresses for each pair
    target_token0_address, target_token1_address = get_token_addresses_v2(target_pair_address_stable)

    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        # Dictionary to hold data for this block number
        data = {
            'block_number': block_number,
            'coin0_price_in_coin1': None,
            'coin1_price_in_coin0': None,
            'coin0_price_in_usd': None,
            'coin1_price_in_usd': None
        }
        
        # Get the price of the tokens in the target pair
        price_coin1_in_coin0 = get_v2_price(target_token0_address, target_token1_address, target_pair_address_stable, block_number, 'token1')
        
        # Get the price of stablecoins in terms of the base token (e.g., ETH)

        
        # Assuming the base token in both stablecoin pairs is the same (e.g., ETH)
        # Calculate and store the price in USD
        data['coin0_price_in_coin1'] = 1
        data['coin1_price_in_coin0'] = price_coin1_in_coin0
        data['coin0_price_in_usd'] = 1
        data['coin1_price_in_usd'] = price_coin1_in_coin0
        
        # Append the data to the DataFrame
        df.loc[len(df)] = data  # This line replaces df = df.append(data, ignore_index=True)
    
    # Set the block_number column as the index of the DataFrame
    df.set_index('block_number', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv(file_name, index=True)
    
    return df

############################################################
def create_price_dataframe_ETH_DUCK_v2(start_block, end_block, target_pair_address, stable_pair0_address, file_name='your_file.csv'):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    # Get the token addresses for each pair
    target_token0_address, target_token1_address = get_token_addresses_v2(target_pair_address)
    stable0_token0_address, stable0_token1_address = get_token_addresses_v2(stable_pair0_address) 

    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {
            'block_number': block_number,
            'coin0_price_in_coin1': None,
            'coin1_price_in_coin0': None,
            'coin0_price_in_usd': None,
            'coin1_price_in_usd': None
        }
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_v2_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token0')
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price token in term of stable coin(e.g., ETH)
        price_stable0_token1_in_stable = get_v2_price(stable0_token0_address, stable0_token1_address, stable_pair0_address, block_number, 'token1')
    
        
        # Assuming the base token in both stablecoin pairs is the same (e.g., ETH)
        # Calculate and store the price in USD
        data['coin0_price_in_coin1'] = price_coin0_in_coin1
        data['coin1_price_in_coin0'] = price_coin1_in_coin0
        data['coin0_price_in_usd'] = price_stable0_token1_in_stable
        data['coin1_price_in_usd'] = price_coin1_in_coin0 * price_stable0_token1_in_stable
        
        # Append the data to the DataFrame
        df.loc[len(df)] = data  # This line replaces df = df.append(data, ignore_index=True)
    
    # Set the block_number column as the index of the DataFrame
    df.set_index('block_number', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv(file_name, index=True)
    
    return df

def create_price_dataframe_WBTC_ETH_v2(start_block, end_block, target_pair_address, stable_pair0_address, file_name='your_file.csv'):
    # Initialize an empty DataFrame
    columns = ['block_number', 'coin0_price_in_coin1', 'coin1_price_in_coin0', 'coin0_price_in_usd', 'coin1_price_in_usd']
    df = pd.DataFrame(columns=columns)
    
    # Get the token addresses for each pair
    target_token0_address, target_token1_address = get_token_addresses_v2(target_pair_address)
    stable0_token0_address, stable0_token1_address = get_token_addresses_v2(stable_pair0_address) 

    
    for block_number in range(start_block, end_block + 1):
        # Dictionary to hold data for this block number
        data = {
            'block_number': block_number,
            'coin0_price_in_coin1': None,
            'coin1_price_in_coin0': None,
            'coin0_price_in_usd': None,
            'coin1_price_in_usd': None
        }
        
        # Get the price of the tokens in the target pair
        price_coin0_in_coin1 = get_v2_price(target_token0_address, target_token1_address, target_pair_address, block_number, 'token0')
        price_coin1_in_coin0 = 1 / price_coin0_in_coin1 if price_coin0_in_coin1 else 0
        
        # Get the price token in term of stable coin(e.g., ETH)
        price_stable0_token1_in_stable = get_v2_price(stable0_token0_address, stable0_token1_address, stable_pair0_address, block_number, 'token1')
    
        # Assuming the base token in both stablecoin pairs is the same (e.g., ETH)
        # Calculate and store the price in USD
        data['coin0_price_in_coin1'] = price_coin0_in_coin1
        data['coin1_price_in_coin0'] = price_coin1_in_coin0
        data['coin0_price_in_usd'] = price_coin0_in_coin1 * price_stable0_token1_in_stable
        data['coin1_price_in_usd'] = price_stable0_token1_in_stable
        
        # Append the data to the DataFrame
        df.loc[len(df)] = data  # This line replaces df = df.append(data, ignore_index=True)
    
    # Set the block_number column as the index of the DataFrame
    df.set_index('block_number', inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv(file_name, index=True)
    
    return df
