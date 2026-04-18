import json
import os
import requests
from tools.registry import registry

HELIUS_RPC = os.getenv("HELIUS_RPC_URL", os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com"))
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")


def check_requirements() -> bool:
    """Check if Helius/Solana RPC is accessible"""
    try:
        response = requests.post(HELIUS_RPC, 
            json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
            timeout=5)
        return response.status_code == 200
    except:
        return False


def get_transaction_details(tx_signature: str) -> str:
    """Get parsed transaction details from Helius"""
    try:
        url = HELIUS_RPC
        if HELIUS_API_KEY:
            url = "https://api.mainnet-beta.solana.com"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [tx_signature, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
        }
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "result" in data and data["result"]:
            tx = data["result"]
            return json.dumps({
                "signature": tx_signature,
                "slot": tx.get("slot"),
                "block_time": tx.get("blockTime"),
                "fee": tx.get("fee"),
                "status": tx.get("meta", {}).get("status", {}),
                "instructions": len(tx.get("transaction", {}).get("message", {}).get("instructions", []))
            })
        return json.dumps({"error": "Transaction not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_signatures_for_address(wallet: str, limit: int = 10) -> str:
    """Get transaction signatures for a wallet"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [wallet, {"limit": limit}]
        }
        
        response = requests.post(HELIUS_RPC, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        signatures = []
        if "result" in data:
            for sig in data["result"]:
                signatures.append({
                    "signature": sig.get("signature"),
                    "slot": sig.get("slot"),
                    "block_time": sig.get("blockTime"),
                    "status": sig.get("status", {})
                })
        
        return json.dumps({"wallet": wallet, "signatures": signatures})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_accounts(wallet: str) -> str:
    """Get all token accounts for a wallet"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet,
                {"program": "TokenkegQFEYz5ymGmcEtjuF4i7"},  # SPL Token program
                {"encoding": "jsonParsed"}
            ]
        }
        
        response = requests.post(HELIUS_RPC, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        accounts = []
        if "result" in data:
            for acc in data["result"]["value"]:
                info = acc["account"]["data"]["parsed"]["info"]
                accounts.append({
                    "mint": info.get("mint"),
                    "amount": info.get("amount"),
                    "decimals": info.get("decimals")
                })
        
        return json.dumps({"wallet": wallet, "token_accounts": accounts})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_cluster_nodes() -> str:
    """Get cluster nodes (for network info)"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getClusterNodes",
            "params": []
        }
        
        response = requests.post(HELIUS_RPC, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        nodes = []
        if "result" in data:
            for node in data["result"][:10]:
                nodes.append({
                    "pubkey": node.get("pubkey"),
                    "gossip": node.get("gossip"),
                    "version": node.get("version"),
                    "feature_set": node.get("featureSet")
                })
        
        return json.dumps({"nodes": nodes})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_slot_leader() -> str:
    """Get current slot leader"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSlotLeader",
            "params": []
        }
        
        response = requests.post(HELIUS_RPC, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return json.dumps({"slot_leader": data.get("result")})
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="helius_tx_details",
    toolset="onchain",
    schema={
        "name": "helius_tx_details",
        "description": "Get parsed transaction details from Solana",
        "parameters": {
            "type": "object",
            "properties": {
                "tx_signature": {"type": "string", "description": "Transaction signature"}
            },
            "required": ["tx_signature"]
        }
    },
    handler=lambda args, **kw: get_transaction_details(args.get("tx_signature", "")),
    check_fn=check_requirements
)

registry.register(
    name="helius_signatures",
    toolset="onchain",
    schema={
        "name": "helius_signatures",
        "description": "Get transaction signatures for a wallet",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet": {"type": "string", "description": "Wallet address"},
                "limit": {"type": "integer", "description": "Max signatures", "default": 10}
            },
            "required": ["wallet"]
        }
    },
    handler=lambda args, **kw: get_signatures_for_address(
        args.get("wallet", ""),
        args.get("limit", 10)
    ),
    check_fn=check_requirements
)

registry.register(
    name="helius_token_accounts",
    toolset="onchain",
    schema={
        "name": "helius_token_accounts",
        "description": "Get all SPL token accounts for a wallet",
        "parameters": {
            "type": "object",
            "properties": {
                "wallet": {"type": "string", "description": "Wallet address"}
            },
            "required": ["wallet"]
        }
    },
    handler=lambda args, **kw: get_token_accounts(args.get("wallet", "")),
    check_fn=check_requirements
)

registry.register(
    name="helius_cluster_nodes",
    toolset="onchain",
    schema={
        "name": "helius_cluster_nodes",
        "description": "Get Solana network cluster nodes",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_cluster_nodes(),
    check_fn=check_requirements
)