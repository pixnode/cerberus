#!/usr/bin/env python3
"""
api.py — Polymarket V2 API Key Generator & Collateral Utility

This script connects to the Polymarket CTF Exchange V2.
It derives your L2 API credentials from your L1 Private Key.
You can then paste these credentials into your .env file.
"""

import os
import sys
from dotenv import load_dotenv

# We must load env vars before importing config if we are running standalone
load_dotenv()

try:
    from py_clob_client_v2 import ClobClient, ApiCreds
    from py_clob_client_v2.constants import POLYGON
except ImportError:
    print("ERROR: py-clob-client-v2 is not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

def main():
    print("=" * 60)
    print("  CERBERUS — Polymarket V2 API Key Generator")
    print("=" * 60)
    
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
    host = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
    
    if not private_key:
        print("ERROR: POLYMARKET_PRIVATE_KEY is missing in your .env file.")
        print("Please add your Polygon wallet private key to .env first.")
        sys.exit(1)

    print(f"[*] Host: {host}")
    print("[*] Deriving API Key from Private Key...")
    
    try:
        # Step 1: Initialize raw client with just the private key
        client = ClobClient(
            host=host,
            chain_id=POLYGON,
            key=private_key
        )
        
        # Step 2: Request or derive API credentials (L2 Signature)
        creds = client.create_or_derive_api_key()
        
        print("\n[+] SUCCESS! API Credentials Derived.")
        print("-" * 60)
        print("Please COPY AND PASTE the following into your .env file:\n")
        
        print(f"POLYMARKET_API_KEY={creds.api_key}")
        print(f"POLYMARKET_API_SECRET={creds.api_secret}")
        print(f"POLYMARKET_API_PASSPHRASE={creds.api_passphrase}")
        
        print("-" * 60)
        
        # Step 3: Check collateral allowance
        print("\n[*] Initializing fully authenticated V2 client...")
        auth_client = ClobClient(
            host=host,
            chain_id=POLYGON,
            key=private_key,
            creds=creds
        )
        
        try:
            print("[*] Checking pUSD balance and allowance...")
            auth_client.update_balance_allowance()
            print("[+] Balance/allowance state synchronized locally.")
        except Exception as e:
            print(f"[-] Warning: Failed to sync balance/allowance: {e}")
            print("    (You may need to deposit/wrap USDC.e to pUSD via the Polymarket UI first)")
            
    except Exception as e:
        print(f"\n[-] ERROR deriving API Key: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
