"""
main.py — Cerberus V3.2 Async Hub
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Entry point for the Multi-Asset Async Arbitrage Engine.

PRD §3.2: Single asyncio process with per-market worker coroutines.
Spawns exactly 1 worker per active market in ACTIVE_MARKETS config.
"""

import asyncio
import signal
import sys
import traceback

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from loguru import logger
import config

# ── Feeds ──────────────────────────────────────────────────────────────────────
from feeds.binance_ws import create_binance_sanitizer, binance_state
from exchange.orderbook_ws import create_polymarket_sanitizer, poly_states

# ── Market Infrastructure ──────────────────────────────────────────────────────
from markets.market_worker import MarketWorker, binance_state as worker_btc_state
from markets.rtds_client import RTDSClient

# ── Exchange ───────────────────────────────────────────────────────────────────
from exchange.polymarket_client import PolymarketRESTClient

# ── Safety & Execution ────────────────────────────────────────────────────────
from safety.ghostshield import GhostShield
from execution.order_manager import OrderManager
from safety.adverse_selection import AdverseSelectionMonitor
from execution.position_manager import PositionTracker
from risk.risk_brain import RiskBrain

# ── Reporting ─────────────────────────────────────────────────────────────────
from reporting.telegram_notifier import TelegramNotifier
from reporting.session_logger import SessionLogger
from model.fair_value import load_models
from training.blended_trainer import start_scheduler

# ─── System Shutdown Event ─────────────────────────────────────────────────────
_shutdown_event = asyncio.Event()


def _handle_signal(sig: signal.Signals) -> None:
    logger.warning(f"[MAIN] Received signal {sig.name}. Initiating graceful shutdown...")
    _shutdown_event.set()


# ─── V3.2 Async Hub ───────────────────────────────────────────────────────────
async def main() -> None:
    logger.info("=" * 72)
    logger.info("  CERBERUS V3.2 — Asymmetric Probability Arbitrage Engine")
    logger.info(f"  MODE: {'DRY RUN ⚠️ ' if config.DRY_RUN else '🔴 LIVE TRADING'}")
    logger.info(f"  Active Markets: {list(config.ACTIVE_MARKETS.keys())}")
    logger.info("=" * 72)

    # Register OS signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: _handle_signal(s))
        except NotImplementedError:
            signal.signal(sig, lambda s, f: _handle_signal(signal.Signals(s)))

    if not config.ACTIVE_MARKETS:
        logger.error("[MAIN] No active markets in .env — set ENABLE_BTC_5M=true etc. Exiting.")
        return

    # ── Load ML Models ────────────────────────────────────────────────────────
    load_models()

    # ── 1. Core Services ──────────────────────────────────────────────────────
    telegram       = TelegramNotifier()
    session_logger = SessionLogger()
    rest_client    = PolymarketRESTClient()

    # ── 2. Safety & Risk ──────────────────────────────────────────────────────
    ghost_shield   = GhostShield(rest_client)
    order_manager  = OrderManager(rest_client, ghost_shield)
    adverse_sel    = AdverseSelectionMonitor()
    risk_brain     = RiskBrain(PositionTracker(order_manager, adverse_sel), order_manager)

    # ── 3. Data Feeds ─────────────────────────────────────────────────────────
    binance_sanitizer = create_binance_sanitizer()
    poly_sanitizer    = create_polymarket_sanitizer()
    rtds_client       = RTDSClient()

    # ── 4. Market Workers (PRD §3.2: 1 per active market) ────────────────────
    workers: list[MarketWorker] = []
    for label, mkt_cfg in config.ACTIVE_MARKETS.items():
        worker = MarketWorker(
            market_config     = mkt_cfg,
            order_manager     = order_manager,
            ghostshield       = ghost_shield,
            adverse_selection = adverse_sel,
            session_logger    = session_logger,
            risk_brain        = risk_brain,
        )
        workers.append(worker)
        logger.info(f"[MAIN] Worker registered: {label}")

    # ── 5. Daily Retrain Scheduler (PRD §7.1 Phase 2/3) ─────────────────────
    scheduler = start_scheduler()  # Fires at 02:00 UTC daily

    # ── 6. Task Dispatch ──────────────────────────────────────────────────────
    tasks: list[asyncio.Task] = []

    # Shared feeds
    tasks.append(asyncio.create_task(binance_sanitizer.start(), name="binance_ws"))
    tasks.append(asyncio.create_task(poly_sanitizer.start(),    name="poly_ws"))
    tasks.append(asyncio.create_task(rtds_client.run(),         name="rtds_ws"))

    # Safety & execution
    tasks.append(asyncio.create_task(ghost_shield.start_monitor(),  name="ghostshield"))
    tasks.append(asyncio.create_task(order_manager.process_queue(), name="order_manager"))
    tasks.append(asyncio.create_task(risk_brain.start_monitor(),    name="risk_brain"))
    tasks.append(asyncio.create_task(telegram.start(),              name="telegram"))

    # Per-market worker coroutines (PRD §3.2 — this is the KEY change from before)
    for worker in workers:
        tasks.append(asyncio.create_task(worker.run(), name=f"worker_{worker.label}"))

    # ── 6. Startup Alert ─────────────────────────────────────────────────────
    await telegram.send_message(
        f"🚀 <b>CERBERUS V3.2 Started</b>\n"
        f"Mode: {'DRY_RUN' if config.DRY_RUN else 'LIVE'}\n"
        f"Markets: {', '.join(config.ACTIVE_MARKETS.keys())}\n"
        f"Workers: {len(workers)}"
    )
    logger.info(f"[MAIN] All systems nominal. {len(workers)} market workers running.")

    # ── 7. Graceful Shutdown ──────────────────────────────────────────────────
    try:
        await _shutdown_event.wait()
        logger.warning("[MAIN] Shutdown initiated. Stopping all components...")

        for worker in workers:
            worker.stop()

        risk_brain.stop()
        order_manager.stop()
        ghost_shield.stop()
        rtds_client.stop()
        poly_sanitizer.stop()
        binance_sanitizer.stop()

        await telegram.send_message(
            f"🛑 <b>CERBERUS V3.2 Stopped</b>\n"
            f"Markets traded: {', '.join(config.ACTIVE_MARKETS.keys())}"
        )
        telegram.stop()

        await asyncio.sleep(2)

        for task in tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("[MAIN] Cerberus shut down cleanly.")

    except Exception as e:
        logger.critical(f"[MAIN] Fatal exception: {e}\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[MAIN] KeyboardInterrupt — exiting.")
    except SystemExit as e:
        sys.exit(e.code)
