import json
import os
import requests
from tools.registry import registry
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.system_program import TransferParams, transfer
from solders.hash import Hash

JUPITER_API_URL = "https://api.jup.ag/swap/v1"
JUPITER_API_URL_V2 = "https://api.jup.ag/swap/v2"
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


def _execute_swap_impl(quote_response: str, private_key_b58: str) -> str:
    """Execute a token swap on Solana DEX using Jupiter
    
    Args:
        quote_response: JSON string from dex_swap_quote
        private_key_b58: Base58 encoded private key for signing
    
    Returns:
        JSON string with transaction signature or error
    """
    try:
        import base58
        
        quote_data = json.loads(quote_response)
        
        if "error" in quote_data:
            return json.dumps({"error": "Invalid quote response"})
        
        user_public_key = quote_data.get("user_public_key")
        if not user_public_key:
            return json.dumps({"error": "Missing user_public_key in quote"})
        
        swap_request = {
            "quoteResponse": quote_data,
            "userPublicKey": user_public_key,
            "prioritizationFeeLamports": "auto"
        }
        
        swap_response = requests.post(
            f"{JUPITER_API_URL_V2}/swap",
            json=swap_request,
            timeout=15
        )
        swap_response.raise_for_status()
        swap_data = swap_response.json()
        
        if "swapTransaction" not in swap_data:
            return json.dumps({"error": "No swap transaction returned"})
        
        blockhash, err = get_latest_blockhash()
        if err:
            return json.dumps({"error": f"Blockhash error: {err}"})
        
        try:
            tx_bytes = base58.b58decode(swap_data["swapTransaction"])
            versioned_tx = VersionedTransaction.from_bytes(tx_bytes)
        except Exception as e:
            return json.dumps({"error": f"Failed to parse transaction: {str(e)}"})
        
        private_key_bytes = base58.b58decode(private_key_b58)
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
                "input_token": quote_data.get("input_mint"),
                "output_token": quote_data.get("output_mint"),
                "input_amount": quote_data.get("input_amount"),
                "output_amount": quote_data.get("output_amount"),
                "explorer_url": f"https://solscan.io/tx/{send_data['result']}?cluster=devnet"
            })
        elif "error" in send_data:
            return json.dumps({"error": send_data["error"]})
        
        return json.dumps({"error": "Unknown error"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_swap_quote(input_mint: str, output_mint: str, amount: int, slippage: float = 0.5, user_public_key: str = None) -> str:
    """Get swap quote from Jupiter aggregator
    
    Args:
        input_mint: Input token mint address
        output_mint: Output token mint address
        amount: Amount in lamports (smallest unit)
        slippage: Maximum slippage tolerance (0.5 = 0.5%)
        user_public_key: The wallet address that will execute the swap (required for execution)
    """
    try:
        url = f"{JUPITER_API_URL}/quote"
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": int(slippage * 100)
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = {
            "input_mint": input_mint,
            "output_mint": output_mint,
            "input_amount": amount,
            "output_amount": data.get("outAmount"),
            "price_impact": data.get("priceImpactPct"),
            "route": data.get("routePlan", [])
        }
        
        if user_public_key:
            result["user_public_key"] = user_public_key
        else:
            result["user_public_key"] = ""
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_token_list(chain: str = "solana") -> str:
    """Get available tokens for swap"""
    try:
        url = f"{JUPITER_API_URL}/tokens"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        tokens = []
        for token in data.get("tokens", [])[:50]:
            tokens.append({
                "address": token.get("address"),
                "symbol": token.get("symbol"),
                "name": token.get("name"),
                "decimals": token.get("decimals"),
                "liquidity": token.get("liquidity")
            })
        
        return json.dumps({"tokens": tokens})
    except Exception as e:
        return json.dumps({"error": str(e)})


def execute_swap(quote_response: str, private_key: str) -> str:
    """Execute a token swap on Solana DEX using Jupiter
    
    Args:
        quote_response: JSON string from dex_swap_quote
        private_key: Base58 encoded private key for signing
    
    Returns:
        JSON string with transaction signature or error
    """
    return _execute_swap_impl(quote_response, private_key)


registry.register(
    name="dex_swap_quote",
    toolset="dex",
    schema={
        "name": "dex_swap_quote",
        "description": "Get a swap quote from Jupiter DEX aggregator for Solana. Returns quote with user_public_key needed for execution.",
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
                "slippage": {
                    "type": "number",
                    "description": "Maximum slippage tolerance (0.5 = 0.5%)",
                    "default": 0.5
                },
                "user_public_key": {
                    "type": "string",
                    "description": "Your wallet address (required for swap execution)"
                }
            },
            "required": ["input_mint", "output_mint", "amount", "user_public_key"]
        }
    },
    handler=lambda args, **kw: get_swap_quote(
        args.get("input_mint", ""),
        args.get("output_mint", ""),
        args.get("amount", 0),
        args.get("slippage", 0.5),
        args.get("user_public_key", "")
    ),
    check_fn=check_requirements
)

registry.register(
    name="dex_token_list",
    toolset="dex",
    schema={
        "name": "dex_token_list",
        "description": "Get list of available tokens for swap on Solana DEX",
        "parameters": {
            "type": "object",
            "properties": {
                "chain": {
                    "type": "string",
                    "description": "Blockchain chain (default: solana)",
                    "default": "solana"
                }
            }
        }
    },
    handler=lambda args, **kw: get_token_list(args.get("chain", "solana")),
    check_fn=check_requirements
)

registry.register(
    name="dex_execute_swap",
    toolset="dex",
    schema={
        "name": "dex_execute_swap",
        "description": "Execute a token swap on Solana DEX using Jupiter aggregator. First call dex_swap_quote to get a quote, then pass that quote_response along with your private_key to execute the swap.",
        "parameters": {
            "type": "object",
            "properties": {
                "quote_response": {
                    "type": "string",
                    "description": "Quote response JSON from dex_swap_quote tool"
                },
                "private_key": {
                    "type": "string",
                    "description": "Base58 encoded Solana private key for signing the transaction"
                }
            },
            "required": ["quote_response", "private_key"]
        }
    },
    handler=lambda args, **kw: execute_swap(
        args.get("quote_response", ""),
        args.get("private_key", "")
    ),
    check_fn=check_requirements
)