# ⚡ Cerberus V3.2
**Multi-Asset, Multi-Timeframe Directional Maker-First Probability Arbitrage Engine**

Cerberus V3.2 is an ultra-low latency trading engine built to exploit probabilistic mispricing on Polymarket's Binary Options (Crypto Markets) using a Numba-JIT Logistic Regression engine and a highly asynchronous 6-Layer WebSocket Sanitizer.

---

## ⚙️ System Architecture

* **6-Layer WebSocket Sanitizer:** Multiplexes 150+ parallel WebSockets across Binance and Polymarket to ensure jitter-free, ultra-low latency data feeds.
* **Dual-Threat Execution:** 
  * *Ambusher (Maker-First):* Automatically posts liquidity at `best_bid + 0.01` to capture spreads and avoid taker fees.
  * *Directional Sniper (Taker Fallback):* Sweeps the orderbook aggressively using VWAP slippage curves when extreme mispricing is detected.
* **GhostShield:** 3-Phase verification system to prevent API state desynchronization (Ghost Fills).
* **Dead Man's Switch & Risk Brain:** Centralized risk unit to enforce global max drawdowns and automatic emergency liquidations.

---

## 🛠️ Installation Tutorial

### 1. Requirements
* Python 3.10+
* Node.js & npm (For the Mission Control Dashboard)
* A Polymarket Account (with Polygon USDC.e deposited)

### 2. Setup Environment
Clone or navigate to the Cerberus workspace, then install the Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure `.env`
Copy the example environment file:
```bash
cp .env.example .env
```
Inside `.env`, you must provide:
* `POLYMARKET_PRIVATE_KEY` (Your Polygon Wallet Private Key)
* `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` (For Telegram alerts)

### 4. Generate Polymarket V2 API Credentials
Polymarket V2 uses L2 Signature API Keys. We provide a utility script to generate these safely from your private key.
Run the script:
```bash
python api.py
```
*Copy the generated `API_KEY`, `API_SECRET`, and `API_PASSPHRASE` and paste them into your `.env` file.*

---

## 🚀 How to Run

### Step 1: Model Bootstrap (Synthetic Warmup)
Before the bot can calculate fair value probabilities, you must train the logistic regression coefficients (`betas`).
Run the synthetic data generator:
```bash
python training/synthetic_labels.py
```
*Wait for this script to successfully generate `data/betas_btc.npy` and `data/betas_eth.npy`.*

### Step 2: Start the Engine (Dry Run)
By default, `.env` should have `DRY_RUN=true`. This allows the engine to connect to all WebSockets, run the ML models, and log decisions *without* placing real money orders.
```bash
python main.py
```
Verify that the logs show healthy connections and no fatal errors.

### Step 3: Go Live
Once you are confident in the system's stability, edit `.env`:
```env
DRY_RUN=false
```
Then restart the engine:
```bash
python main.py
```

---

## 📊 Monitoring System

Cerberus V3.2 features a 3-Level Reporting architecture to keep you informed 24/7.

### Level 1: Mission Control Dashboard (React)
A real-time, highly visual web dashboard showing live PnL, latency metrics, WebSocket health, and GhostShield status.
To run the dashboard:
```bash
cd reporting/dashboard
npm install
npm run dev
```
Then open `http://localhost:5173` in your browser.

### Level 2: Per-Session JSONL Dumps
Every market window (5M, 15M, 1H), the bot automatically dumps a full state snapshot to `logs/sessions/`. This data can be used for deep retrospective analysis and model recalibration.

### Level 3: Daily Telegram Digest
Cerberus will automatically push a daily summary to your Telegram at 00:00 UTC containing Gross PnL, Win Rate, and Total Orders.
To test this notification manually at any time, run:
```bash
python reporting/daily_digest.py --test
```

---
*Developed for elite probabilistic arbitrage. May the odds be overwhelmingly in your favor.*
