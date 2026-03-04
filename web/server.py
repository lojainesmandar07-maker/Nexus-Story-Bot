# web/server.py - خادم ويب لإبقاء البوت نشطاً

from flask import Flask, jsonify
from threading import Thread
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نيكسس بوت - راوي القصص</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 30px;
                padding: 40px;
                max-width: 800px;
                margin: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            h1 {
                font-size: 3.5em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .status {
                background: #27ae60;
                display: inline-block;
                padding: 15px 30px;
                border-radius: 50px;
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 30px;
                box-shadow: 0 5px 15px rgba(39, 174, 96, 0.4);
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 20px;
                text-align: center;
                transition: transform 0.3s;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.25);
            }
            
            .stat-emoji {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .stat-label {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .stat-value {
                font-size: 1.8em;
                font-weight: bold;
            }
            
            .divider {
                height: 2px;
                background: linear-gradient(to right, transparent, white, transparent);
                margin: 30px 0;
            }
            
            .command {
                background: rgba(0, 0, 0, 0.2);
                padding: 10px 20px;
                border-radius: 10px;
                display: inline-block;
                font-family: monospace;
                font-size: 1.2em;
                margin: 5px;
            }
            
            .footer {
                margin-top: 30px;
                font-size: 0.9em;
                opacity: 0.7;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ بوت النيكسس ✨</h1>
            <div class="status">✅ البوت شغال ومتصل!</div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-emoji">🌍</div>
                    <div class="stat-label">العوالم</div>
                    <div class="stat-value">4</div>
                </div>
                <div class="stat-card">
                    <div class="stat-emoji">📖</div>
                    <div class="stat-label">أجزاء القصة</div>
                    <div class="stat-value">160+</div>
                </div>
                <div class="stat-card">
                    <div class="stat-emoji">🏆</div>
                    <div class="stat-label">إنجازات</div>
                    <div class="stat-value">30+</div>
                </div>
                <div class="stat-card">
                    <div class="stat-emoji">🎁</div>
                    <div class="stat-label">عناصر</div>
                    <div class="stat-value">20+</div>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <h2>🎮 الأوامر الرئيسية</h2>
            <div>
                <span class="command">/ابدأ</span>
                <span class="command">/استمر</span>
                <span class="command">/عوالمي</span>
                <span class="command">/حالتي</span>
                <span class="command">/مخزني</span>
                <span class="command">/إنجازاتي</span>
                <span class="command">/يومي</span>
                <span class="command">/مساعدة</span>
            </div>
            
            <div class="footer">
                <p>آخر تحديث: 2024 | الإصدار 1.0.0</p>
                <p>استخدم الأوامر في ديسكورد لبدء مغامرتك!</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """فحص صحة البوت"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/stats')
def stats():
    """إحصائيات سريعة"""
    return jsonify({
        "worlds": 4,
        "total_parts": 160,
        "achievements": 30,
        "items": 20
    })

def run():
    """تشغيل الخادم"""
    try:
        # Render يمرر المنفذ عبر PORT، مع fallback إلى 8080
        port = int(os.getenv("PORT", "8080"))
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"❌ خطأ في خادم الويب: {e}")

def keep_alive():
    """تشغيل الخادم في خيط منفصل"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    logger.info(f"🌐 خادم الويب شغال على port {os.getenv('PORT', '8080')}")
