# main.py - ملف التشغيل الرئيسي للبوت
# هذا الملف هو نقطة البداية، يربط كل المكونات مع بعضها

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env (التوكن)
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

# استيراد البوت من core
from core.bot import NexusBot
from web.server import keep_alive

async def main():
    """الدالة الرئيسية لتشغيل البوت"""
    
    # الحصول على التوكن من المتغيرات البيئية
    TOKEN = os.getenv('TOKEN')
    
    if not TOKEN:
        logger.critical("❌ لم يتم العثور على التوكن! تأكد من وجود متغير TOKEN في ملف .env")
        logger.critical("📝 طريقة الإصلاح: أنشئ ملف .env وأضف فيه TOKEN=توكن_البوت_هنا")
        return
    
    try:
        # إنشاء البوت
        bot = NexusBot()
        
        # بدء خادم الويب (للبقاء حياً على ريلت)
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
    # تشغيل الدالة الرئيسية
    asyncio.run(main())
