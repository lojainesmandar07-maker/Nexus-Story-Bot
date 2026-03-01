# core/config.py - إعدادات البوت المتقدمة
# هذا الملف يدير كل الإعدادات من ملف JSON والمتغيرات البيئية

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Config:
    """
    كلاس الإعدادات الرئيسي - نمط Singleton
    يدير كل إعدادات البوت من ملف JSON
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """نمط Singleton - نسخة واحدة فقط من الإعدادات"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """تحميل الإعدادات من ملف JSON"""
        config_file = "config.json"
        
        # الإعدادات الافتراضية الكاملة
        default_config = {
            "bot": {
                "name": "Nexus Story Bot",
                "version": "1.0.0",
                "command_prefix": "/",
                "default_world": "fantasy",
                "max_history": 50,
                "activity_status": "🌍 النيكسس ينتظرك | /ابدأ",
                "owner_ids": [],  # IDs المشرفين
                "testing_mode": False,
                "debug_mode": False
            },
            
            "database": {
                "path": "data/database/nexus.db",
                "backup_interval": 86400,  # 24 ساعة
                "auto_backup": True,
                "max_backups": 7,
                "timeout": 10,
                "wal_mode": True  # Write-Ahead Logging للسرعة
            },
            
            "game": {
                "daily_cooldown": 86400,
                "max_level": 20,
                "base_xp": 100,
                "xp_multiplier": 1.5,
                "xp_per_choice": 10,
                "xp_per_achievement": 50,
                "xp_per_daily": 100,
                "starting_shards": 0,
                "starting_items": ["potion"],
                "max_inventory_slots": 50,
                "enable_crafting": True,
                "enable_trading": False
            },
            
            "rate_limits": {
                "commands_per_minute": 10,
                "buttons_per_minute": 20,
                "daily_limit": 1,
                "cooldown_message": True,
                "enable_global_limits": True
            },
            
            "worlds": {
                "fantasy": {
                    "enabled": True,
                    "start_part": "FANTASY_01",
                    "required_level": 1,
                    "required_ending": None
                },
                "retro": {
                    "enabled": True,
                    "start_part": "RETRO_01",
                    "required_level": 3,
                    "required_ending": "fantasy_ending"
                },
                "future": {
                    "enabled": True,
                    "start_part": "FUTURE_01",
                    "required_level": 5,
                    "required_ending": "retro_ending"
                },
                "alternate": {
                    "enabled": True,
                    "start_part": "ALT_01",
                    "required_level": 7,
                    "required_ending": "future_ending"
                }
            },
            
            "story": {
                "auto_save": True,
                "save_interval": 300,  # 5 دقائق
                "max_choice_time": 300,  # 5 دقائق للأزرار
                "enable_choice_analysis": True,
                "default_choice_timeout": 60
            },
            
            "economy": {
                "enabled": True,
                "currency_name": "شظية",
                "currency_emoji": "💎",
                "starting_balance": 0,
                "max_balance": 999999
            },
            
            "logging": {
                "level": "INFO",
                "save_to_file": True,
                "save_commands": True,
                "save_errors": True,
                "log_channel_id": None,  # قناة ديسكورد للسجلات
                "webhook_url": None
            },
            
            "backup": {
                "enabled": True,
                "interval": 86400,
                "max_backups": 7,
                "backup_path": "data/backups",
                "compress": True
            },
            
            "web": {
                "enabled": True,
                "port": 8080,
                "host": "0.0.0.0",
                "debug": False
            },
            
            "features": {
                "achievements": True,
                "inventory": True,
                "daily_rewards": True,
                "crafting": True,
                "trading": False,
                "leaderboard": True,
                "voice_acting": False
            }
        }
        
        try:
            # محاولة تحميل ملف الإعدادات
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # دمج الإعدادات
                    self._config = self._deep_merge(default_config, user_config)
                logger.info(f"✅ تم تحميل الإعدادات من {config_file}")
            else:
                # استخدام الإعدادات الافتراضية
                self._config = default_config
                # حفظ الإعدادات الافتراضية للمستخدم
                self.save_config()
                logger.info("✅ تم إنشاء ملف إعدادات افتراضي")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ خطأ في ملف JSON: {e}")
            self._config = default_config
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل الإعدادات: {e}")
            self._config = default_config
    
    def _deep_merge(self, default: Dict, user: Dict) -> Dict:
        """دمج عميق بين إعدادات المستخدم والإعدادات الافتراضية"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """الحصول على قيمة إعداد معين (مثال: get('bot.name'))"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """تغيير قيمة إعداد معين"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return self.save_config()
    
    def get_bot_config(self) -> Dict:
        """الحصول على كل إعدادات البوت"""
        return self._config.get("bot", {})
    
    def get_database_config(self) -> Dict:
        """الحصول على إعدادات قاعدة البيانات"""
        return self._config.get("database", {})
    
    def get_game_config(self) -> Dict:
        """الحصول على إعدادات اللعبة"""
        return self._config.get("game", {})
    
    def get_rate_limits(self) -> Dict:
        """الحصول على إعدادات تحديد السرعة"""
        return self._config.get("rate_limits", {})
    
    def get_world_config(self, world_id: str) -> Dict:
        """الحصول على إعدادات عالم معين"""
        worlds = self._config.get("worlds", {})
        return worlds.get(world_id, {})
    
    def get_story_config(self) -> Dict:
        """الحصول على إعدادات القصة"""
        return self._config.get("story", {})
    
    def get_economy_config(self) -> Dict:
        """الحصول على إعدادات الاقتصاد"""
        return self._config.get("economy", {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """التحقق إذا كانت ميزة معينة مفعلة"""
        features = self._config.get("features", {})
        return features.get(feature, False)
    
    def save_config(self) -> bool:
        """حفظ الإعدادات الحالية إلى ملف"""
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
            logger.info("✅ تم حفظ الإعدادات")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ الإعدادات: {e}")
            return False
    
    def reload_config(self) -> bool:
        """إعادة تحميل الإعدادات من الملف"""
        try:
            self._load_config()
            logger.info("✅ تم إعادة تحميل الإعدادات")
            return True
        except Exception as e:
            logger.error(f"❌ خطأ في إعادة تحميل الإعدادات: {e}")
            return False
    
    def is_admin(self, user_id: int) -> bool:
        """التحقق إذا كان المستخدم أدمن"""
        owner_ids = self.get('bot.owner_ids', [])
        return user_id in owner_ids
    
    def is_testing_mode(self) -> bool:
        """التحقق من وضع الاختبار"""
        return self.get('bot.testing_mode', False)
    
    def is_debug_mode(self) -> bool:
        """التحقق من وضع التصحيح"""
        return self.get('bot.debug_mode', False)


# ============================================
# إعدادات المسارات (Paths)
# ============================================
class Paths:
    """كلاس المسارات - لإدارة مسارات الملفات والمجلدات"""
    
    # المسار الأساسي للمشروع
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # مجلدات رئيسية
    CORE_DIR = os.path.join(BASE_DIR, "core")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    BACKUPS_DIR = os.path.join(DATA_DIR, "backups")
    DATABASE_DIR = os.path.join(DATA_DIR, "database")
    STORIES_DIR = os.path.join(DATA_DIR, "stories")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    COMMANDS_DIR = os.path.join(BASE_DIR, "commands")
    GAME_DIR = os.path.join(BASE_DIR, "game")
    UI_DIR = os.path.join(BASE_DIR, "ui")
    UTILS_DIR = os.path.join(BASE_DIR, "utils")
    WEB_DIR = os.path.join(BASE_DIR, "web")
    
    # ملفات
    DATABASE_FILE = os.path.join(DATABASE_DIR, "nexus.db")
    MAIN_LOG = os.path.join(LOGS_DIR, "bot.log")
    ERROR_LOG = os.path.join(LOGS_DIR, "errors.log")
    COMMANDS_LOG = os.path.join(LOGS_DIR, "commands.log")
    
    # ملفات القصص
    FANTASY_STORY = os.path.join(STORIES_DIR, "fantasy_story.json")
    RETRO_STORY = os.path.join(STORIES_DIR, "retro_story.json")
    FUTURE_STORY = os.path.join(STORIES_DIR, "future_story.json")
    ALTERNATE_STORY = os.path.join(STORIES_DIR, "alternate_story.json")
    
    @classmethod
    def ensure_directories(cls):
        """التأكد من وجود كل المجلدات المطلوبة"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.BACKUPS_DIR,
            cls.DATABASE_DIR,
            cls.STORIES_DIR,
            cls.ASSETS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("✅ تم التأكد من وجود كل المجلدات")
    
    @classmethod
    def get_story_file(cls, world_id: str) -> str:
        """الحصول على ملف قصة عالم معين"""
        files = {
            "fantasy": cls.FANTASY_STORY,
            "retro": cls.RETRO_STORY,
            "future": cls.FUTURE_STORY,
            "alternate": cls.ALTERNATE_STORY
        }
        return files.get(world_id, "")
    
    @classmethod
    def get_backup_file(cls, suffix: str = "") -> str:
        """الحصول على مسار ملف النسخ الاحتياطي"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if suffix:
            filename = f"backup_{timestamp}_{suffix}.json"
        else:
            filename = f"backup_{timestamp}.json"
        return os.path.join(cls.BACKUPS_DIR, filename)


# ============================================
# إعدادات البيئة (Environment)
# ============================================
class Environment:
    """إعدادات البيئة والمتغيرات"""
    
    @staticmethod
    def get_token() -> Optional[str]:
        """الحصول على التوكن من المتغيرات البيئية"""
        token = os.getenv('TOKEN')
        if not token:
            logger.warning("⚠️ لم يتم العثور على TOKEN في المتغيرات البيئية")
        return token
    
    @staticmethod
    def is_production() -> bool:
        """التحقق من بيئة الإنتاج"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    @staticmethod
    def is_development() -> bool:
        """التحقق من بيئة التطوير"""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    @staticmethod
    def get_environment() -> str:
        """الحصول على اسم البيئة الحالية"""
        return os.getenv('ENVIRONMENT', 'development')
    
    @staticmethod
    def get_database_url() -> str:
        """الحصول على رابط قاعدة البيانات"""
        return os.getenv('DATABASE_URL', '')
    
    @staticmethod
    def get_webhook_url() -> Optional[str]:
        """الحصول على رابط Webhook"""
        return os.getenv('WEBHOOK_URL')
    
    @staticmethod
    def get_redis_url() -> Optional[str]:
        """الحصول على رابط Redis (للتخزين المؤقت)"""
        return os.getenv('REDIS_URL')


# ============================================
# إنشاء كائنات الإعدادات العامة
# ============================================

# إنشاء كائن الإعدادات الرئيسي
config = Config()

# إنشاء كائن المسارات
paths = Paths()

# إنشاء كائن البيئة
env = Environment()

# التأكد من وجود المجلدات
paths.ensure_directories()

# ============================================
# تصدير الكائنات للاستخدام في باقي الملفات
# ============================================
__all__ = ['config', 'paths', 'env', 'Config', 'Paths', 'Environment']
