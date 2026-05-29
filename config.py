"""
config.py — Cerberus V3.2 Central Configuration Loader
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Loads all parameters from the .env file.
Provides typed helper functions used by every module.

All modules MUST import from here — never call os.getenv() directly.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


# ─── Typed Helpers ─────────────────────────────────────────────────────────────
def _str(key: str, default: str = "") -> str:
    return os.getenv(key, default)

def _int(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default

def _float(key: str, default: float = 0.0) -> float:
    try:
        return float(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default

def _bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).strip().lower()
    return val in ("true", "1", "yes")


# ─── Mode ──────────────────────────────────────────────────────────────────────
DRY_RUN: bool = _bool("DRY_RUN", True)

# ─── API Credentials ───────────────────────────────────────────────────────────
POLYMARKET_PRIVATE_KEY: str   = _str("POLYMARKET_WALLET_PRIVATE_KEY")
POLYMARKET_API_KEY: str       = _str("POLYMARKET_API_KEY")
POLYMARKET_API_SECRET: str    = _str("POLYMARKET_API_SECRET")
POLYMARKET_API_PASSPHRASE: str = _str("POLYMARKET_API_PASSPHRASE")
POLYMARKET_HOST: str          = _str("POLYMARKET_HOST", "https://clob.polymarket.com")

BINANCE_WS_URL: str = _str("BINANCE_WS_URL", "wss://stream.binance.com:9443/ws")
RTDS_WS_URL: str    = _str("RTDS_WS_URL",    "wss://ws-live-data.polymarket.com")

TELEGRAM_BOT_TOKEN: str = _str("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str   = _str("TELEGRAM_CHAT_ID")

# ─── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL: str = _str("LOG_LEVEL", "INFO")
LOG_FILE: str  = _str("LOG_FILE", "logs/cerberus.log")

# ─── 6-Layer Sanitizer ─────────────────────────────────────────────────────────
SANITIZER_PARALLEL_CONNECTIONS: int   = _int("SANITIZER_PARALLEL_CONNECTIONS", 150)
SANITIZER_PRUNE_INTERVAL_SECONDS: int = _int("SANITIZER_PRUNE_INTERVAL_SECONDS", 4)
SANITIZER_PRUNE_PERCENT: int          = _int("SANITIZER_PRUNE_PERCENT", 10)
SANITIZER_STAGGER_SPREAD_MS: int      = _int("SANITIZER_STAGGER_SPREAD_MS", 1000)
SANITIZER_WARMUP_SECONDS: int         = _int("SANITIZER_WARMUP_SECONDS", 15)
SANITIZER_MIN_TICKS_PER_TOKEN: int    = _int("SANITIZER_MIN_TICKS_PER_TOKEN", 3)
SANITIZER_MAX_JUMP_DOLLAR: float      = _float("SANITIZER_MAX_JUMP_DOLLAR", 15.0)
SANITIZER_STALE_THRESHOLD_DOLLAR: float = _float("SANITIZER_STALE_THRESHOLD_DOLLAR", 15.0)
SANITIZER_GRACE_PERIOD_SECONDS: int   = _int("SANITIZER_GRACE_PERIOD_SECONDS", 8)
SANITIZER_MAX_KILLS_PER_MINUTE: int   = _int("SANITIZER_MAX_KILLS_PER_MINUTE", 20)
SANITIZER_MAX_KILLS_PER_CYCLE: int    = _int("SANITIZER_MAX_KILLS_PER_CYCLE", 2)
SANITIZER_JITTER_EMA_ALPHA: float     = _float("SANITIZER_JITTER_EMA_ALPHA", 0.2)

# ─── Model Paths ───────────────────────────────────────────────────────────────
BTC_MODEL_PATH: str = _str("BTC_MODEL_PATH", "data/betas_btc.npy")
ETH_MODEL_PATH: str = _str("ETH_MODEL_PATH", "data/betas_eth.npy")
MODEL_BRIER_EXCELLENT:  float = _float("MODEL_BRIER_EXCELLENT",  0.15)
MODEL_BRIER_ACCEPTABLE: float = _float("MODEL_BRIER_ACCEPTABLE", 0.20)
MODEL_BRIER_PAUSE:      float = _float("MODEL_BRIER_PAUSE",      0.20)  # LIVE strict threshold
MODEL_BRIER_WARMUP:     float = _float("MODEL_BRIER_WARMUP",     0.22)  # WARMUP/TRANSITION (week 1)
# NOTE: Use MODEL_BRIER_WARMUP for <5000 real samples (synthetic labels lack microstructure noise)
# Tighten to MODEL_BRIER_PAUSE after 5000 real outcomes. See training/blended_trainer.py.

# ─── Risk Management ───────────────────────────────────────────────────────────
TOTAL_CAPITAL_PUSD: float          = _float("TOTAL_CAPITAL_PUSD", 200.0)
DAILY_LOSS_LIMIT_USDC: float       = _float("DAILY_LOSS_LIMIT_USDC", 5.0)
CONSECUTIVE_LOSS_LIMIT: int        = _int("CONSECUTIVE_LOSS_LIMIT", 3)
ADVERSE_SELECTION_WINDOW: int      = _int("ADVERSE_SELECTION_WINDOW", 10)
ADVERSE_SELECTION_THRESHOLD: float = _float("ADVERSE_SELECTION_THRESHOLD", 0.45)
BTC_HOURLY_LOSS_LIMIT_USDC: float  = _float("BTC_HOURLY_LOSS_LIMIT_USDC", 150.0)
ETH_HOURLY_LOSS_LIMIT_USDC: float  = _float("ETH_HOURLY_LOSS_LIMIT_USDC", 100.0)
GLOBAL_MAX_DRAWDOWN_USDC: float    = _float("GLOBAL_MAX_DRAWDOWN_USDC", 50.0)

# ─── GhostShield ───────────────────────────────────────────────────────────────
GHOST_VERIFY_TIMEOUT_MS: int         = _int("GHOST_VERIFY_TIMEOUT_MS", 2000)
GHOST_MAX_RETRIES: int               = _int("GHOST_MAX_RETRIES", 3)
GHOST_DECLARE_TIMEOUT_MS: int        = _int("GHOST_DECLARE_TIMEOUT_MS", 5000)
GHOST_RECONCILIATION_INTERVAL_S: int = _int("GHOST_RECONCILIATION_INTERVAL_S", 60)
GHOST_MAX_PENDING_FILLS: int         = _int("GHOST_MAX_PENDING_FILLS", 10)
GHOST_SPIKE_THRESHOLD_PCT: float     = _float("GHOST_SPIKE_THRESHOLD_PCT", 0.05)

# ─── Order Management ──────────────────────────────────────────────────────────
ORDER_RATE_LIMIT_COUNT: int   = _int("ORDER_RATE_LIMIT_COUNT", 8)
ORDER_RATE_LIMIT_WINDOW_S: int = _int("ORDER_RATE_LIMIT_WINDOW_S", 10)
ORDER_MAKER_TTL_S: int        = _int("ORDER_MAKER_TTL_S", 3)

# ─── Position / Time Stops (SRE: no hardcoded values) ─────────────────────────
HARD_TIME_STOP_S: int = _int("HARD_TIME_STOP_S", 120)
SOFT_TIME_STOP_S: int = _int("SOFT_TIME_STOP_S", 30)

# ─── Dead Man's Switch ─────────────────────────────────────────────────────────
DMS_STALE_THRESHOLD_S: int  = _int("DMS_STALE_THRESHOLD_S", 120)
HEARTBEAT_INTERVAL_S: int   = _int("HEARTBEAT_INTERVAL_S", 10)

# ─── Training Pipeline ─────────────────────────────────────────────────────────
TRAINING_DECAY_FACTOR: float    = _float("TRAINING_DECAY_FACTOR", 0.95)
TRAINING_MIN_SAMPLES: int       = _int("TRAINING_MIN_SAMPLES", 5000)
TRAINING_RETRAIN_HOUR_UTC: int  = _int("TRAINING_RETRAIN_HOUR_UTC", 2)

# ─── Spread & Volatility ───────────────────────────────────────────────────────
BTC_VOL_REFERENCE: float         = _float("BTC_VOL_REFERENCE", 0.02)
ETH_VOL_REFERENCE: float         = _float("ETH_VOL_REFERENCE", 0.03)
SPREAD_TIME_MULT_FINAL_60S: float  = _float("SPREAD_TIME_MULT_FINAL_60S", 2.0)
SPREAD_TIME_MULT_FINAL_120S: float = _float("SPREAD_TIME_MULT_FINAL_120S", 1.5)

# ─── Latency & Infrastructure ──────────────────────────────────────────────────
LATENCY_P50_TARGET_MS: int = _int("LATENCY_P50_TARGET_MS", 110)
LATENCY_P99_TARGET_MS: int = _int("LATENCY_P99_TARGET_MS", 300)
PAPER_TRADING_LOG: str     = _str("PAPER_TRADING_LOG", "logs/paper_trades.csv")


# ─── Market Config Dataclass ───────────────────────────────────────────────────
@dataclass
class MarketConfig:
    label:                   str
    asset:                   str
    timeframe:               str
    enabled:                 bool
    maker_edge_min:          float
    taker_net_edge_min:      float
    spread_base:             float
    max_hold_seconds:        int
    time_stop_seconds:       int
    taker_disable_seconds:   int
    force_flat_seconds:      int
    position_reduce_seconds: int
    trade_size_usdc:         float
    market_slug:             str
    # Fee-aware spread (spread_threshold.py integration)
    category:            str   = "crypto"
    min_offset:          float = 0.010
    base_spread_target:  float = 0.005
    vol_reference:       float = 0.02


@dataclass
class RiskConfig:
    total_capital:          float = TOTAL_CAPITAL_PUSD
    daily_loss_limit:       float = DAILY_LOSS_LIMIT_USDC
    consecutive_loss_limit: int   = CONSECUTIVE_LOSS_LIMIT
    adverse_window:         int   = ADVERSE_SELECTION_WINDOW
    adverse_threshold:      float = ADVERSE_SELECTION_THRESHOLD
    global_max_drawdown:    float = GLOBAL_MAX_DRAWDOWN_USDC


RISK_CONFIG = RiskConfig()


def _build_market(asset: str, tf: str) -> Optional[MarketConfig]:
    key = f"{asset}_{tf}"          # e.g. "BTC_5M"
    env = f"ENABLE_{key}"
    if not _bool(env, False):
        return None
    return MarketConfig(
        label                  = f"{asset}-{tf}",
        asset                  = asset,
        timeframe              = tf,
        enabled                = True,
        maker_edge_min         = _float(f"{key}_MAKER_EDGE_MIN", 0.025),
        taker_net_edge_min     = _float(f"{key}_TAKER_NET_EDGE_MIN", 0.030),
        spread_base            = _float(f"{key}_SPREAD_BASE", 0.005),
        max_hold_seconds       = _int(f"{key}_MAX_HOLD_SECONDS", 30),
        time_stop_seconds      = _int(f"{key}_TIME_STOP_SECONDS", 10),
        taker_disable_seconds  = _int(f"{key}_TAKER_DISABLE_SECONDS", 60),
        force_flat_seconds     = _int(f"{key}_FORCE_FLAT_SECONDS", 5),
        position_reduce_seconds = _int(f"{key}_POSITION_REDUCE_SECONDS", 10),
        trade_size_usdc        = _float(f"{key}_TRADE_SIZE_USDC", 2.50),
        market_slug            = _str(f"{asset}_{tf}_MARKET_SLUG", ""),
        # Fee-aware spread
        category           = "crypto",
        min_offset         = _float(f"{key}_MIN_OFFSET", 0.010),
        base_spread_target = _float(f"{key}_BASE_SPREAD_TARGET", 0.005),
        vol_reference      = BTC_VOL_REFERENCE if asset == "BTC" else ETH_VOL_REFERENCE,
    )


# Build active markets dict at import time
ACTIVE_MARKETS: Dict[str, MarketConfig] = {}
for _asset in ("BTC", "ETH"):
    for _tf in ("5M", "15M", "1H"):
        _mc = _build_market(_asset, _tf)
        if _mc:
            ACTIVE_MARKETS[_mc.label] = _mc
