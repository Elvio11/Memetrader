import json
import base58
from solders.keypair import Keypair
from tools.registry import registry


def check_requirements() -> bool:
    """Check if Solana wallet libraries are available"""
    try:
        from solders.keypair import Keypair
        import base58
        return True
    except:
        return False


def load_wallet_from_private_key(private_key_b58: str) -> str:
    """Load wallet from base58 encoded private key
    
    Returns wallet address and status.
    """
    try:
        private_key_bytes = base58.b58decode(private_key_b58)
        keypair = Keypair.from_bytes(private_key_bytes)
        return json.dumps({
            "success": True,
            "wallet_address": str(keypair.pubkey()),
            "message": "Wallet loaded successfully"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Invalid private key: {str(e)}"
        })


def get_wallet_address(private_key_b58: str) -> str:
    """Get wallet address from private key (without loading full keypair)
    
    Useful for displaying address without holding private key in memory.
    """
    try:
        private_key_bytes = base58.b58decode(private_key_b58)
        keypair = Keypair.from_bytes(private_key_bytes)
        return json.dumps({
            "wallet_address": str(keypair.pubkey())
        })
    except Exception as e:
        return json.dumps({
            "error": str(e)
        })


def validate_private_key(private_key_b58: str) -> str:
    """Validate if a private key is valid base58 encoded Solana key
    
    Returns validation result.
    """
    try:
        private_key_bytes = base58.b58decode(private_key_b58)
        if len(private_key_bytes) != 64:
            return json.dumps({
                "valid": False,
                "error": "Private key must be 64 bytes (32 byte seed)"
            })
        keypair = Keypair.from_bytes(private_key_bytes)
        return json.dumps({
            "valid": True,
            "wallet_address": str(keypair.pubkey())
        })
    except Exception as e:
        return json.dumps({
            "valid": False,
            "error": str(e)
        })


def get_token_balance(wallet_address: str, token_mint: str = None) -> str:
    """Get token balance for a wallet
    
    If token_mint is None, returns SOL balance.
    Otherwise returns specific token balance.
    """
    try:
        import os
        import requests
        
        rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        
        if token_mint is None:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
        else:
            payload = {
                "jsonrpc": "2.0", 
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"mint": token_mint},
                    {"encoding": "jsonParsed"}
                ]
            }
        
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        if "result" in data:
            if token_mint is None:
                lamports = data["result"].get("value", {}).get("lamports", 0)
                sol_balance = lamports / 1e9
                return json.dumps({
                    "wallet": wallet_address,
                    "sol_balance": sol_balance,
                    "lamports": lamports
                })
            else:
                accounts = data["result"].get("value", [])
                if accounts:
                    amount = accounts[0].get("account", {}).get("data", {}).get("parsed", {}).get("info", {}).get("amount", "0")
                    return json.dumps({
                        "wallet": wallet_address,
                        "token_mint": token_mint,
                        "amount": int(amount)
                    })
                return json.dumps({
                    "wallet": wallet_address,
                    "token_mint": token_mint,
                    "amount": 0
                })
        return json.dumps({"error": "RPC call failed"})
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="solana_load_wallet",
    toolset="dex",
    schema={
        "name": "solana_load_wallet",
        "description": "Load Solana wallet from base58 private key",
        "parameters": {
            "type": "object",
            "properties": {
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded private key"
                }
            },
            "required": ["private_key"]
        }
    },
    handler=lambda args, **kw: load_wallet_from_private_key(args.get("private_key", "")),
    check_fn=check_requirements
)

registry.register(
    name="solana_get_address",
    toolset="dex",
    schema={
        "name": "solana_get_address",
        "description": "Get Solana wallet address from private key",
        "parameters": {
            "type": "object",
            "properties": {
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded private key"
                }
            },
            "required": ["private_key"]
        }
    },
    handler=lambda args, **kw: get_wallet_address(args.get("private_key", "")),
    check_fn=check_requirements
)

registry.register(
    name="solana_validate_key",
    toolset="dex",
    schema={
        "name": "solana_validate_key",
        "description": "Validate Solana private key format",
        "parameters": {
            "type": "object",
            "properties": {
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded private key to validate"
                }
            },
            "required": ["private_key"]
        }
    },
    handler=lambda args, **kw: validate_private_key(args.get("private_key", "")),
    check_fn=check_requirements
)

registry.register(
    name="solana_get_balance",
    toolset="dex",
    schema={
        "name": "solana_get_balance",
        "description": "Get Solana token balance for a wallet",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet_address": {
                    "type": "string",
                    "description": "Solana wallet address"
                },
                "token_mint": {
                    "type": "string",
                    "description": "Token mint address (optional, defaults to SOL)"
                }
            },
            "required": ["wallet_address"]
        }
    },
    handler=lambda args, **kw: get_token_balance(
        args.get("wallet_address", ""),
        args.get("token_mint")
    ),
    check_fn=check_requirements
)