# web/server.py - خادم ويب لإبقاء البوت نشطاً

from flask import Flask
from threading import Thread
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
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
            h1 { font-size: 3em; margin-bottom: 20px; }
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
            <div class="status">✅ البوت شغال!</div>
            <p>🌍 4 عوالم | 📖 150+ جزء | 🏆 30+ إنجاز</p>
            <hr>
            <p>استخدم <strong>/ابدأ</strong> في ديسكورد</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "alive"}

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    Thread(target=run, daemon=True).start()
    logger.info("🌐 خادم الويب شغال")
