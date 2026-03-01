# main.py - ملف التشغيل الرئيسي

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# تحميل التوكن من ملف .env
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

# إضافة المجلدات إلى مسار البحث
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.bot import NexusBot
from web.server import keep_alive
from utils.logger import setup_logger

async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    
    # الحصول على التوكن
    TOKEN = os.getenv('TOKEN')
    
    if not TOKEN:
        logger.critical("❌ التوكن غير موجود! أضف TOKEN في متغيرات البيئة")
        logger.critical("📝 في Replit: اذهب إلى Secrets وأضف TOKEN = توكنك")
        return
    
    try:
        # إعداد السجلات المتقدمة
        setup_logger()
        
        # إنشاء البوت
        bot = NexusBot()
        
        # تشغيل خادم الويب (للبقاء حياً)
        keep_alive()
        
        logger.info("✅ بدء تشغيل البوت...")
        
        # تشغيل البوت
        await bot.start(TOKEN)
        
    except KeyboardInterrupt:
        logger.info("👋 تم إيقاف البوت يدوياً")
    except Exception as e:
        logger.critical(f"💥 خطأ غير متوقع: {e}", exc_info=True)
    finally:
        # إغلاق البوت بشكل آمن
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
