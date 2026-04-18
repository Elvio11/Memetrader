import json
import os
import requests
from tools.registry import registry
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
import base58

JUPITER_LIMIT_ORDER_API_URL = "https://jup.ag/api/limit/v1"
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")


def check_requirements() -> bool:
    """Check if Solana devnet is accessible"""
    try:
        response = requests.get(SOLANA_RPC, 
            json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
            timeout=5)
        return response.status_code == 200
    except:
        return False


def get_latest_blockhash() -> tuple:
    """Get latest blockhash for transaction signing"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLatestBlockhash",
            "params": []
        }
        response = requests.post(SOLANA_RPC, json=payload, timeout=10)
        data = response.json()
        if "result" in data:
            blockhash = data["result"]["value"]["blockhash"]
            return Hash.from_string(blockhash), None
        return None, "Failed to get blockhash"
    except Exception as e:
        return None, str(e)


def _sign_and_send_transaction(tx_bytes: str, private_key_b58: str) -> str:
    """Sign and send a transaction"""
    try:
        # Decode the transaction
        tx_raw = base58.b58decode(tx_bytes)
        versioned_tx = VersionedTransaction.from_bytes(tx_raw)
        
        # Load keypair from private key
        private_key_bytes = base58.b58decode(private_key_b58)
        keypair = Keypair.from_bytes(private_key_bytes)
        
        # Sign the transaction
        signed_tx = VersionedTransaction(versioned_tx.message, [keypair])
        
        # Send the transaction
        send_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [
                base58.b58encode(bytes(signed_tx)).decode(),
                {"encoding": "base64", "maxSupportedTransactionVersion": 0}
            ]
        }
        
        send_response = requests.post(SOLANA_RPC, json=send_payload, timeout=30)
        send_data = send_response.json()
        
        if "result" in send_data:
            return json.dumps({
                "success": True,
                "signature": send_data["result"],
                "explorer_url": f"https://solscan.io/tx/{send_data['result']}?cluster=devnet"
            })
        elif "error" in send_data:
            return json.dumps({"error": send_data["error"]})
        else:
            return json.dumps({"error": "Unknown error"})
            
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_limit_order(input_mint: str, output_mint: str, in_amount: int, out_amount: int, 
                      user_public_key: str, private_key_b58: str, expired_at: int = None) -> str:
    """Create a Jupiter limit order
    
    Args:
        input_mint: Input token mint address
        output_mint: Output token mint address
        in_amount: Amount of input token to sell (in smallest unit)
        out_amount: Minimum amount of output token to receive (in smallest unit)
        user_public_key: Wallet address that will create the order
        private_key_b58: Base58 encoded private key for signing
        expired_at: Unix timestamp for order expiration (optional)
    
    Returns:
        JSON string with transaction signature or error
    """
    try:
        # Prepare the request for creating a limit order
        payload = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "inAmount": str(in_amount),
            "outAmount": str(out_amount),
            "maker": user_public_key
        }
        
        if expired_at is not None:
            payload["expiredAt"] = str(expired_at)
        
        # Call Jupiter Limit Order API to create the order
        response = requests.post(
            f"{JUPITER_LIMIT_ORDER_API_URL}/createOrder",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        order_data = response.json()
        
        if "error" in order_data:
            return json.dumps({"error": order_data["error"]})
        
        # Extract the unsigned transaction
        if "transaction" not in order_data:
            return json.dumps({"error": "No transaction returned from API"})
        
        tx_bytes = order_data["transaction"]
        
        # Sign and send the transaction
        return _sign_and_send_transaction(tx_bytes, private_key_b58)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def query_open_orders(wallet: str) -> str:
    """Query open limit orders for a wallet
    
    Args:
        wallet: Wallet address to query orders for
    
    Returns:
        JSON string with open orders or error
    """
    try:
        response = requests.get(
            f"{JUPITER_LIMIT_ORDER_API_URL}/openOrders",
            params={"wallet": wallet},
            timeout=10
        )
        response.raise_for_status()
        return response.text()
    except Exception as e:
        return json.dumps({"error": str(e)})


def cancel_limit_order(order_public_key: str, user_public_key: str, private_key_b58: str) -> str:
    """Cancel a Jupiter limit order
    
    Args:
        order_public_key: Public key of the order to cancel
        user_public_key: Wallet address that owns the order
        private_key_b58: Base58 encoded private key for signing
    
    Returns:
        JSON string with transaction signature or error
    """
    try:
        # Prepare the request for canceling a limit order
        payload = {
            "orderPubKey": order_public_key,
            "maker": user_public_key
        }
        
        # Call Jupiter Limit Order API to cancel the order
        response = requests.post(
            f"{JUPITER_LIMIT_ORDER_API_URL}/cancelOrders",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        cancel_data = response.json()
        
        if "error" in cancel_data:
            return json.dumps({"error": cancel_data["error"]})
        
        # Extract the unsigned transaction
        if "transaction" not in cancel_data:
            return json.dumps({"error": "No transaction returned from API"})
        
        tx_bytes = cancel_data["transaction"]
        
        # Sign and send the transaction
        return _sign_and_send_transaction(tx_bytes, private_key_b58)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


# Register the tools
registry.register(
    name="jupiter_limit_create",
    toolset="dex",
    schema={
        "name": "jupiter_limit_create",
        "description": "Create a Jupiter limit order. Returns a transaction that needs to be signed and sent.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_mint": {
                    "type": "string",
                    "description": "Input token mint address"
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token mint address"
                },
                "in_amount": {
                    "type": "integer",
                    "description": "Amount of input token to sell (in smallest unit)"
                },
                "out_amount": {
                    "type": "integer",
                    "description": "Minimum amount of output token to receive (in smallest unit)"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Wallet address that will create the order"
                },
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded Solana private key for signing the transaction"
                },
                "expired_at": {
                    "type": "integer",
                    "description": "Unix timestamp for order expiration (optional)"
                }
            },
            "required": ["input_mint", "output_mint", "in_amount", "out_amount", "user_public_key", "private_key"]
        }
    },
    handler=lambda args, **kw: create_limit_order(
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("in_amount", 0),
        args.get("out_amount", 0),
        args.get("user_public_key", ""),
        args.get("private_key", ""),
        args.get("expired_at")
    ),
    check_fn=check_requirements
)

registry.register(
    name="jupiter_limit_query",
    toolset="dex",
    schema={
        "name": "jupiter_limit_query",
        "description": "Query open Jupiter limit orders for a wallet",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet": {
                    "type": "string",
                    "description": "Wallet address to query orders for"
                }
            },
            "required": ["wallet"]
        }
    },
    handler=lambda args, **kw: query_open_orders(args.get("wallet", "")),
    check_fn=check_requirements
)

registry.register(
    name="jupiter_limit_cancel",
    toolset="dex",
    schema={
        "name": "jupiter_limit_cancel",
        "description": "Cancel a Jupiter limit order. Returns a transaction that needs to be signed and sent.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_public_key": {
                    "type": "string",
                    "description": "Public key of the order to cancel"
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Wallet address that owns the order"
                },
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded Solana private key for signing the transaction"
                }
            },
            "required": ["order_public_key", "user_public_key", "private_key"]
        }
    },
    handler=lambda args, **kw: cancel_limit_order(
        args.get("order_public_key", ""),
        args.get("user_public_key", ""),
        args.get("private_key", "")
    ),
    check_fn=check_requirements
)