# main.py - ملف التشغيل الرئيسي

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# تحميل التوكن
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# إضافة المجلدات إلى المسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.bot import NexusBot
from web.server import keep_alive

async def main():
    TOKEN = os.getenv('TOKEN')
    
    if not TOKEN:
        logger.critical("❌ التوكن غير موجود! أضفه كـ Secret في Replit")
        return
    
    try:
        bot = NexusBot()
        keep_alive()
        logger.info("✅ بدء تشغيل البوت...")
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.info("👋 تم إيقاف البوت")
    except Exception as e:
        logger.critical(f"💥 خطأ: {e}")
    finally:
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
