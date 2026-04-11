import os
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum


class ChainType(Enum):
    EVM = "evm"
    SOLANA = "solana"
    SUI = "sui"


@dataclass
class ChainConfig:
    name: str
    chain_type: ChainType
    chain_id: int
    rpc_url: str
    explorer_url: str
    coin_symbol: str
    coin_decimals: int
    wrapped_token: str  # WETH, SOL, SUI
    default_gas_limit: int

    def __hash__(self):
        return hash(self.name)


CHAIN_CONFIGS: Dict[str, ChainConfig] = {
    "ethereum": ChainConfig(
        name="ethereum",
        chain_type=ChainType.EVM,
        chain_id=1,
        rpc_url=os.getenv("ETH_RPC_URL", "https://eth.llamarpc.com"),
        explorer_url="https://etherscan.io",
        coin_symbol="ETH",
        coin_decimals=18,
        wrapped_token="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        default_gas_limit=21000,
    ),
    "sepolia": ChainConfig(
        name="sepolia",
        chain_type=ChainType.EVM,
        chain_id=11155111,
        rpc_url=os.getenv("SEPOLIA_RPC_URL", "https://sepolia.llamarpc.com"),
        explorer_url="https://sepolia.etherscan.io",
        coin_symbol="ETH",
        coin_decimals=18,
        wrapped_token="0x7b79995e5f9A90051505805B6C05753d4f272aC6",
        default_gas_limit=21000,
    ),
    "arbitrum": ChainConfig(
        name="arbitrum",
        chain_type=ChainType.EVM,
        chain_id=42161,
        rpc_url=os.getenv("ARB_RPC_URL", "https://arb1.arbitrum.io/rpc"),
        explorer_url="https://arbiscan.io",
        coin_symbol="ETH",
        coin_decimals=18,
        wrapped_token="0x82aF49447d8a07e3bd95BD0d56f12c09F1C9e0c4",
        default_gas_limit=21000,
    ),
    "base": ChainConfig(
        name="base",
        chain_type=ChainType.EVM,
        chain_id=8453,
        rpc_url=os.getenv("BASE_RPC_URL", "https://mainnet.base.org"),
        explorer_url="https://basescan.org",
        coin_symbol="ETH",
        coin_decimals=18,
        wrapped_token="0x4200000000000000000000000000000000000006",
        default_gas_limit=21000,
    ),
    "solana": ChainConfig(
        name="solana",
        chain_type=ChainType.SOLANA,
        chain_id=101,
        rpc_url=os.getenv("SOL_RPC_URL", "https://api.mainnet-beta.solana.com"),
        explorer_url="https://solscan.io",
        coin_symbol="SOL",
        coin_decimals=9,
        wrapped_token="So11111111111111111111111111111111111111112",
        default_gas_limit=0,
    ),
    "sui": ChainConfig(
        name="sui",
        chain_type=ChainType.SUI,
        chain_id=0,
        rpc_url=os.getenv("SUI_RPC_URL", "https://fullnode.mainnet.sui.io"),
        explorer_url="https://suiscan.xyz",
        coin_symbol="SUI",
        coin_decimals=9,
        wrapped_token="0x0000000000000000000000000000000000000002::sui::SUI",
        default_gas_limit=0,
    ),
}


SUPPORTED_TOKENS = {
    "ethereum": {
        "ETH": {
            "address": "0xEeeeeEeeeEeEeeEdeEeEeeEEEeeeeEeeeeeeeEEeE",
            "decimals": 18,
            "symbol": "ETH",
        },
        "WETH": {
            "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "decimals": 18,
            "symbol": "WETH",
        },
        "USDC": {
            "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "decimals": 6,
            "symbol": "USDC",
        },
        "USDT": {
            "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "decimals": 6,
            "symbol": "USDT",
        },
        "PEPE": {
            "address": "0x6982508145454Ce6d2B9C7f54d1A3D7f1e4Aa98a",
            "decimals": 18,
            "symbol": "PEPE",
        },
        "SHIB": {
            "address": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
            "decimals": 18,
            "symbol": "SHIB",
        },
        "DOGE": {
            "address": "0xba2ae424d960c26247dd243c383b3b1c97cd02c7",
            "decimals": 8,
            "symbol": "DOGE",
        },
        "WIF": {
            "address": "0xDBC2D50f2C52F3eA4E1Cdb7f4C6b31A0F1C6aF9d",
            "decimals": 18,
            "symbol": "WIF",
        },
    },
    "solana": {
        "SOL": {
            "address": "So11111111111111111111111111111111111111112",
            "decimals": 9,
            "symbol": "SOL",
        },
        "USDC": {
            "address": "EPjFWdd5AufqSSLQub8SN2vU1j3mMqiZ2NPV2D2S1S6",
            "decimals": 6,
            "symbol": "USDC",
        },
        "USDT": {
            "address": "Es9vMFrzaCERkLgaT2t9RkDqEhWJBjkFH5UP5CQCx3kB",
            "decimals": 6,
            "symbol": "USDT",
        },
        "BONK": {
            "address": "DezXAZ8z7PnrnzjzjiXqeSq5sccEhHVJy8xwHqq3dY2c",
            "decimals": 5,
            "symbol": "BONK",
        },
        "WIF": {
            "address": "85VBFQZC9TZkfaptBWqv14ALD9fJNUKGZ33N5Wz3dD6C",
            "decimals": 6,
            "symbol": "WIF",
        },
        "POPCAT": {
            "address": "ASpT2hFLr4eSTsLryPpYK3gFK6B5F2CzvwuPJ4uVYqYp",
            "decimals": 9,
            "symbol": "POPCAT",
        },
    },
    "sui": {
        "SUI": {
            "address": "0x0000000000000000000000000000000000000002::sui::SUI",
            "decimals": 9,
            "symbol": "SUI",
        },
        "USDC": {
            "address": "0xa1f526d3a1f16c47e5e0e2f81a1f3f2e8d20c5d8::usdc::USDC",
            "decimals": 6,
            "symbol": "USDC",
        },
    },
}


def get_chain(chain_name: str) -> Optional[ChainConfig]:
    return CHAIN_CONFIGS.get(chain_name.lower())


def get_supported_chains() -> List[str]:
    return list(CHAIN_CONFIGS.keys())


def get_tokens_for_chain(chain: str) -> Dict:
    return SUPPORTED_TOKENS.get(chain.lower(), {})
