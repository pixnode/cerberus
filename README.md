# ⚡ Cerberus V3.2
**Multi-Asset, Multi-Timeframe Directional Maker-First Probability Arbitrage Engine**

Cerberus V3.2 is an ultra-low latency, production-grade SRE trading engine built to exploit probabilistic mispricing on Polymarket's Binary Options (Crypto Markets) using a Logistic Regression engine and a highly asynchronous 6-Layer WebSocket Sanitizer.

---

## ⚙️ System Architecture

* **Market Workers:** 6 isolated asynchronous coroutines (BTC/ETH across 5M, 15M, 1H) ensuring one market's network failure does not crash the engine.
* **Strike Discovery (Gamma API):** Automatically parses strike prices from question text using live Polymarket slugs (`btc-updown-5m-{ts}`, etc).
* **Dual-Threat Execution:** 
  * *Ambusher (Maker-First):* Automatically posts liquidity at `best_bid + 0.01` to capture spreads and avoid taker fees. Uses **fee-aware dynamic spread thresholds** (`C_CRYPTO=0.9984`).
  * *Directional Sniper (Taker Fallback):* Sweeps the orderbook aggressively when extreme mispricing is detected.
* **GhostShield:** 3-Phase verification system (WS → REST → Reconciliation) to prevent API state desynchronization (Ghost Fills) with UNVERIFIED state tracking.
* **Dead Man's Switch & Risk Brain:** Centralized risk unit enforcing global max drawdowns, per-asset hourly loss limits, consecutive loss limits, and 30-second post-fill **Adverse Selection** checks.

---

## 🚀 Deployment (VPS / Production)

Cerberus is designed to be deployed to a Linux VPS (Ubuntu/Debian) directly from your Windows machine using the provided 1-click deployment script.

### 1. Deploy to VPS
From your local Windows machine, double-click the deployment script:
```cmd
deploy_to_vps.bat
```
*(Script ini akan memaketkan kode (tanpa .env/.git/logs), mengirimnya via `scp` ke `root@204.168.229.145`, mengekstraknya, dan menjalankan `vps_setup.sh` secara otomatis).*

### 2. Konfigurasi Kredensial (.env)
Setelah deploy selesai, masuk ke VPS via SSH:
```bash
ssh root@204.168.229.145
cd /root/cerberus
nano .env
```
Isi konfigurasi wajib:
* `POLYMARKET_WALLET_PRIVATE_KEY`
* `POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`
* `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
* **Pastikan `DRY_RUN=true` untuk testing awal.**

### 3. Start Engine (Systemd)
Deployment script sudah membuat systemd service `cerberus`. Anda tinggal menyalakannya:
```bash
systemctl start cerberus
systemctl enable cerberus
```

---

## 🧠 ML Training Pipeline (Phase 1, 2, 3)

Cerberus menggunakan model *Logistic Regression* yang dilatih menggunakan data Binance (OHLCV) dan Polymarket.

Proses **Setup Awal (Otomatis dilakukan oleh `vps_setup.sh`)**:
```bash
# 1. Download 90 hari data OHLCV dari Binance (Tanpa API Key)
python3 training/historical_downloader.py --days 90 --asset BTC
python3 training/historical_downloader.py --days 90 --asset ETH

# 2. Train Model dengan Synthetic Labels
python3 training/train_model.py --asset BTC
python3 training/train_model.py --asset ETH

# 3. Validasi Brier Score
python3 training/model_validator.py --mode model_performance --asset BTC
```

**Brier Score Thresholds:**
* **WARMUP Phase (< 5000 real samples):** Target `< 0.22` (Sedikit lebih longgar karena label sintetis tidak mengandung microstructure noise seperti spread dan slippage).
* **LIVE Phase (≥ 5000 real samples):** Target ketat `< 0.20`.
* Jadwal Retrain: Berjalan otomatis setiap jam 02:00 UTC melalui `training/blended_trainer.py`.

---

## 📊 Monitoring System

Cerberus V3.2 memiliki 3-Level Reporting architecture kelas SRE.

### Level 1: TUI Mission Control (Terminal Dashboard)
Dashboard *real-time* berbasis terminal yang menampilkan live PnL, latency metrics, WebSocket health, Risk Brain, dan GhostShield.
**Cara akses di VPS:**
```bash
cd /root/cerberus
source .venv/bin/activate
python3 reporting/dashboard.py
```
*(Tersedia juga `python3 reporting/dashboard.py --demo` untuk melihat UI menggunakan data mock).*

### Level 2: Per-Session JSONL Dumps
Setiap market window selesai, bot membuang snapshot state (PnL, Brier score, fill rates) ke `logs/sessions/` dengan format JSON yang strict untuk keperluan *post-mortem analysis*.

### Level 3: Daily Telegram Digest
Bot mengirimkan rekap harian ke Telegram (Total Trades, Win Rate, Ghost Rate, Brier Score OOS) setiap jam 00:00 UTC.
Untuk mengetes pengiriman report kapan saja:
```bash
python3 reporting/daily_digest.py --preview
```

---
### ⚠️ PRE-FLIGHT CHECKLIST (Sebelum DRY_RUN=false)
1. Brier Score OOS harus `< 0.20` selama 3 hari berturut-turut.
2. Hit endpoint `GET https://clob.polymarket.com/fee-config` secara manual untuk memverifikasi bahwa konstanta fee `C_CRYPTO` benar-benar `0.9984` (1.56%).
3. Ghost Rate harian konsisten di bawah 3%.

*Developed for elite probabilistic arbitrage. May the odds be overwhelmingly in your favor.*
