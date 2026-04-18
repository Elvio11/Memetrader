import json
import os
import requests
from tools.registry import registry
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
import base58

RAYDIUM_API_URL = "https://transaction-v1.raydium.io"
SOLANA_RPC = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")


def check_requirements() -> bool:
    """Check if Solana RPC and Raydium API are accessible"""
    try:
        response = requests.get(SOLANA_RPC, 
            json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
            timeout=5)
        if response.status_code != 200:
            return False
        response = requests.get(f"{RAYDIUM_API_URL}/compute/swap-base-in?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=100000000&slippageBps=50&txVersion=V0", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_swap_quote(input_mint: str, output_mint: str, amount: int, slippage_bps: int = 50, tx_version: str = "V0") -> str:
    """Get swap quote from Raydium DEX
    
    Args:
        input_mint: Input token mint address
        output_mint: Output token mint address
        amount: Amount in lamports (smallest unit)
        slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
        tx_version: Transaction version - "V0" or "LEGACY"
    
    Returns:
        JSON string with quote data
    """
    try:
        url = f"{RAYDIUM_API_URL}/compute/swap-base-in"
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount),
            "slippageBps": slippage_bps,
            "txVersion": tx_version
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return json.dumps({"error": data.get("msg", "Quote failed")})
        
        swap_data = data.get("data", {})
        return json.dumps({
            "input_mint": input_mint,
            "output_mint": output_mint,
            "input_amount": amount,
            "output_amount": swap_data.get("outputAmount"),
            "other_amount_threshold": swap_data.get("otherAmountThreshold"),
            "slippage_bps": swap_data.get("slippageBps"),
            "price_impact_pct": swap_data.get("priceImpactPct"),
            "route_plan": swap_data.get("routePlan", []),
            "swap_type": swap_data.get("swapType"),
            "version": data.get("version")
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def build_transaction(swap_response: str, wallet_address: str, tx_version: str = "V0", wrap_sol: bool = True, priority_fee_micro_lamports: int = None) -> str:
    """Build swap transaction from quote response
    
    Args:
        swap_response: JSON string from get_swap_quote
        wallet_address: User's wallet public key
        tx_version: Transaction version - "V0" or "LEGACY"
        wrap_sol: Whether to wrap SOL for input (if input is SOL)
        priority_fee_micro_lamports: Optional priority fee
    
    Returns:
        JSON string with unsigned transaction
    """
    try:
        swap_data = json.loads(swap_response)
        if "error" in swap_data:
            return json.dumps({"error": "Invalid swap response"})
        
        url = f"{RAYDIUM_API_URL}/transaction/swap-base-in"
        
        payload = {
            "swapResponse": swap_data,
            "wallet": wallet_address,
            "txVersion": tx_version,
            "wrapSol": wrap_sol
        }
        
        if priority_fee_micro_lamports:
            payload["computeUnitPriceMicroLamports"] = str(priority_fee_micro_lamports)
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return json.dumps({"error": data.get("msg", "Transaction build failed")})
        
        tx_data = data.get("data", [])
        if not tx_data or len(tx_data) == 0:
            return json.dumps({"error": "No transaction returned"})
        
        return json.dumps({
            "transactions": [tx.get("transaction") for tx in tx_data],
            "version": data.get("version"),
            "wallet": wallet_address
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_swap(quote_response: str, private_key: str, wallet_address: str = None, tx_version: str = "V0", priority_fee: int = None) -> str:
    """Execute a Raydium swap
    
    Args:
        quote_response: JSON string from get_swap_quote
        private_key: Base58 encoded private key for signing
        wallet_address: User's wallet public key (required for building tx)
        tx_version: Transaction version - "V0" or "LEGACY"
        priority_fee: Optional priority fee in micro-lamports
    
    Returns:
        JSON string with transaction signature or error
    """
    try:
        swap_data = json.loads(quote_response)
        if "error" in swap_data:
            return json.dumps({"error": "Invalid quote response"})
        
        if not wallet_address:
            return json.dumps({"error": "wallet_address required for execution"})
        
        build_result = build_transaction(quote_response, wallet_address, tx_version, True, priority_fee)
        build_data = json.loads(build_result)
        
        if "error" in build_data:
            return json.dumps({"error": f"Transaction build error: {build_data['error']}"})
        
        if "transactions" not in build_data or not build_data["transactions"]:
            return json.dumps({"error": "No transactions to sign"})
        
        tx_bytes = build_data["transactions"][0]
        tx_raw = base58.b58decode(tx_bytes)
        versioned_tx = VersionedTransaction.from_bytes(tx_raw)
        
        private_key_bytes = base58.b58decode(private_key)
        keypair = Keypair.from_bytes(private_key_bytes)
        
        signed_tx = VersionedTransaction(versioned_tx.message, [keypair])
        
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
                "input_mint": swap_data.get("input_mint"),
                "output_mint": swap_data.get("output_mint"),
                "input_amount": swap_data.get("input_amount"),
                "output_amount": swap_data.get("output_amount"),
                "explorer_url": f"https://solscan.io/tx/{send_data['result']}?cluster=devnet"
            })
        elif "error" in send_data:
            return json.dumps({"error": send_data["error"]})
        
        return json.dumps({"error": "Unknown error"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_list() -> str:
    """Get list of popular tokens on Raydium"""
    try:
        url = "https://api-v3.raydium.io/main/token/list"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        tokens = []
        for token in data.get("data", [])[:50]:
            tokens.append({
                "address": token.get("address"),
                "symbol": token.get("symbol"),
                "name": token.get("name"),
                "decimals": token.get("decimals")
            })
        
        return json.dumps({"tokens": tokens})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_pool_info(token_a: str = None, token_b: str = None) -> str:
    """Get liquidity pools from Raydium
    
    Args:
        token_a: Optional first token mint to filter pools
        token_b: Optional second token mint to filter pools
    """
    try:
        url = "https://api-v3.raydium.io/main/pool/list"
        params = {}
        if token_a:
            params["token1"] = token_a
        if token_b:
            params["token2"] = token_b
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pools = data.get("data", [])[:20]
        return json.dumps({
            "pools": [{
                "pool_id": p.get("poolId"),
                "token_a": p.get("token1"),
                "token_b": p.get("token2"),
                "liquidity": p.get("liquidity"),
                "volume_24h": p.get("volume24h")
            } for p in pools],
            "count": len(pools)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


registry.register(
    name="raydium_quote",
    toolset="dex",
    schema={
        "name": "raydium_quote",
        "description": "Get a swap quote from Raydium DEX on Solana. Raydium provides liquidity from both AMM pools and Central Limit Order Book (CLOB).",
        "parameters": {
            "type": "object",
            "properties": {
                "input_mint": {
                    "type": "string",
                    "description": "Input token mint address (e.g., So11111111111111111111111111111111111111112 for SOL)"
                },
                "output_mint": {
                    "type": "string",
                    "description": "Output token mint address"
                },
                "amount": {
                    "type": "integer",
                    "description": "Amount in lamports (smallest unit)"
                },
                "slippage_bps": {
                    "type": "integer",
                    "description": "Slippage tolerance in basis points (50 = 0.5%)",
                    "default": 50
                },
                "tx_version": {
                    "type": "string",
                    "description": "Transaction version: V0 or LEGACY",
                    "default": "V0"
                }
            },
            "required": ["input_mint", "output_mint", "amount"]
        }
    },
    handler=lambda args, **kw: get_swap_quote(
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("amount", 0),
        args.get("slippage_bps", 50),
        args.get("tx_version", "V0")
    ),
    check_fn=check_requirements
)

registry.register(
    name="raydium_execute",
    toolset="dex",
    schema={
        "name": "raydium_execute",
        "description": "Execute a token swap on Raydium DEX. First call raydium_quote to get a quote, then pass that quote_response along with your private_key and wallet_address to execute the swap.",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_response": {
                    "type": "string",
                    "description": "Quote response JSON from raydium_quote tool"
                },
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded Solana private key for signing the transaction"
                },
                "wallet_address": {
                    "type": "string",
                    "description": "Your wallet address (public key)"
                },
                "tx_version": {
                    "type": "string",
                    "description": "Transaction version: V0 or LEGACY",
                    "default": "V0"
                },
                "priority_fee": {
                    "type": "integer",
                    "description": "Optional priority fee in micro-lamports"
                }
            },
            "required": ["quote_response", "private_key", "wallet_address"]
        }
    },
    handler=lambda args, **kw: execute_swap(
        args.get("quote_response", ""),
        args.get("private_key", ""),
        args.get("wallet_address", ""),
        args.get("tx_version", "V0"),
        args.get("priority_fee")
    ),
    check_fn=check_requirements
)

registry.register(
    name="raydium_tokens",
    toolset="dex",
    schema={
        "name": "raydium_tokens",
        "description": "Get list of popular tokens available on Raydium",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda args, **kw: get_token_list(),
    check_fn=check_requirements
)

registry.register(
    name="raydium_pools",
    toolset="dex",
    schema={
        "name": "raydium_pools",
        "description": "Get liquidity pools from Raydium",
        "parameters": {
            "type": "object",
            "properties": {
                "token_a": {
                    "type": "string",
                    "description": "Optional first token mint to filter pools"
                },
                "token_b": {
                    "type": "string",
                    "description": "Optional second token mint to filter pools"
                }
            }
        }
    },
    handler=lambda args, **kw: get_pool_info(
        args.get("token_a"),
        args.get("token_b")
    ),
    check_fn=check_requirements
)