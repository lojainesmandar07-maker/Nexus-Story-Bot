# main.py - نقطة تشغيل البوت

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# تحميل .env
load_dotenv()

# لضمان الاستيراد من جذر المشروع
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.bot import NexusBot
from core.config import config
from web.server import keep_alive
from utils.logger import setup_logger


def bootstrap_logging():
    """تهيئة سجل بسيط قبل setup_logger المتقدم."""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/bootstrap.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


async def main():
    bootstrap_logging()
    logger = logging.getLogger("main")

    token = os.getenv("TOKEN")
    if not token:
        logger.critical("❌ TOKEN غير موجود. أضفه في متغيرات البيئة.")
        return

    # ملاحظة تنظيمية: تسجيل PersistentViewManager و register_all_views
    # يتم حصرياً داخل NexusBot.setup_hook في core/bot.py لتجنب أي تكرار مستقبلي.
    bot = NexusBot()

    try:
        setup_logger()
        logger.info("🚀 بدء تشغيل البوت...")

        if config.get("web.enabled", True):
            keep_alive()

        await bot.start(token)

    except KeyboardInterrupt:
        logger.warning("🛑 تم إيقاف البوت يدويًا.")

    except Exception as exc:
        logger.exception(f"💥 خطأ غير متوقع أثناء تشغيل البوت: {exc}")

    finally:
        await bot.close()
        logger.info("✅ تم إغلاق البوت بأمان.")


if __name__ == "__main__":
    asyncio.run(main())
