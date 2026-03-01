# web/server.py - خادم ويب بسيط باستخدام Flask
# هذا المهم لإبقاء البوت نشطاً على منصات مثل Replit

from flask import Flask
from threading import Thread
import logging

logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

@app.route('/')
def home():
    """الصفحة الرئيسية - تعرض حالة البوت"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>نيكسس بوت</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
                direction: rtl;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 30px;
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                font-size: 3em;
                margin-bottom: 20px;
            }
            .status {
                background: #27ae60;
                display: inline-block;
                padding: 10px 20px;
                border-radius: 50px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ بوت النيكسس ✨</h1>
            <div class="status">✅ البوت شغال ومتصل!</div>
            <p>🌍 4 عوالم في انتظارك</p>
            <p>📖 أكثر من 150 جزء قصة</p>
            <p>🏆 30+ إنجاز</p>
            <hr>
            <p>استخدم /ابدأ في ديسكورد لبدء المغامرة</p>
            <small>آخر تحديث: 2024</small>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """صفحة فحص الصحة - ترجع حالة البوت"""
    return {"status": "alive", "timestamp": __import__('datetime').datetime.now().isoformat()}

def run():
    """تشغيل خادم Flask"""
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل خادم الويب: {e}")

def keep_alive():
    """تشغيل الخادم في خيط منفصل"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    logger.info("🌐 خادم الويب شغال على port 8080")
