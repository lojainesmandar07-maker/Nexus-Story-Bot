# utils/logger.py - نظام تسجيل الأخطاء المتقدم

import logging
import sys
import os
from datetime import datetime
from typing import Optional
import traceback
import json

# ألوان للطرفية (Terminal)
class Colors:
    """ألوان للطباعة في الطرفية"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'

class ColoredFormatter(logging.Formatter):
    """تنسيق السجلات مع ألوان"""
    
    COLORS = {
        logging.DEBUG: Colors.GRAY,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelno, Colors.WHITE)
        
        # تنسيق الوقت
        record.asctime = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        
        # تنسيق الرسالة مع اللون
        message = super().format(record)
        
        # إضافة لون للمستوى
        levelname = f"{log_color}{record.levelname}{Colors.RESET}"
        
        return message.replace(record.levelname, levelname)

class LoggerManager:
    """
    مدير السجلات المتقدم
    يدير عدة ملفات للسجلات ومستويات مختلفة
    """
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = "logs"
        self._ensure_log_directory()
        
        # إعداد السجلات الأساسية
        self.setup_bot_logger()
        self.setup_error_logger()
        self.setup_command_logger()
        self.setup_database_logger()
        
        # سجل الأحداث المهمة
        self.event_logger = self.setup_file_logger(
            'events', 
            'events.log',
            logging.INFO
        )
        
        # سجل أداء البوت
        self.performance_logger = self.setup_file_logger(
            'performance',
            'performance.log',
            logging.DEBUG
        )
    
    def _ensure_log_directory(self):
        """التأكد من وجود مجلد السجلات"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def setup_file_logger(self, name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
        """إعداد سجل لملف معين"""
        logger = logging.getLogger(name)
        
        if logger.handlers:
            return logger
        
        logger.setLevel(level)
        
        # معالج للملف
        file_path = os.path.join(self.log_dir, filename)
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(level)
        
        # تنسيق للملف (بدون ألوان)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # معالج للطرفية (مع ألوان)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        self._loggers[name] = logger
        return logger
    
    def setup_bot_logger(self):
        """إعداد سجل البوت الرئيسي"""
        self.bot_logger = self.setup_file_logger(
            'bot',
            'bot.log',
            logging.INFO
        )
    
    def setup_error_logger(self):
        """إعداد سجل الأخطاء"""
        self.error_logger = self.setup_file_logger(
            'error',
            'error.log',
            logging.ERROR
        )
    
    def setup_command_logger(self):
        """إعداد سجل الأوامر"""
        self.command_logger = self.setup_file_logger(
            'command',
            'commands.log',
            logging.INFO
        )
    
    def setup_database_logger(self):
        """إعداد سجل قاعدة البيانات"""
        self.db_logger = self.setup_file_logger(
            'database',
            'database.log',
            logging.INFO
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """الحصول على سجل معين"""
        return self._loggers.get(name, logging.getLogger(name))
    
    def log_command(self, user_id: int, username: str, command: str, args: str = ""):
        """تسجيل استخدام أمر"""
        self.command_logger.info(
            f"CMD | User: {username} ({user_id}) | Command: {command} | Args: {args}"
        )
    
    def log_error(self, error: Exception, context: str = ""):
        """تسجيل خطأ مع تفاصيل كاملة"""
        error_trace = traceback.format_exc()
        self.error_logger.error(
            f"ERROR | Context: {context}\n"
            f"Type: {type(error).__name__}\n"
            f"Message: {str(error)}\n"
            f"Traceback:\n{error_trace}"
        )
    
    def log_event(self, event_type: str, data: dict):
        """تسجيل حدث مهم"""
        self.event_logger.info(
            f"EVENT | Type: {event_type} | Data: {json.dumps(data, ensure_ascii=False)}"
        )
    
    def log_performance(self, operation: str, duration: float):
        """تسجيل أداء عملية معينة"""
        self.performance_logger.debug(
            f"PERF | Operation: {operation} | Duration: {duration:.3f}s"
        )
    
    def log_database_query(self, query: str, params: tuple, duration: float):
        """تسجيل استعلام قاعدة البيانات"""
        self.db_logger.debug(
            f"DB | Query: {query} | Params: {params} | Duration: {duration:.3f}s"
        )
    
    def log_user_action(self, user_id: int, action: str, details: str = ""):
        """تسجيل إجراء قام به مستخدم"""
        self.bot_logger.info(
            f"USER | ID: {user_id} | Action: {action} | Details: {details}"
        )
    
    def log_world_progress(self, user_id: int, world: str, part: str):
        """تسجيل تقدم لاعب في عالم معين"""
        self.bot_logger.info(
            f"PROGRESS | User: {user_id} | World: {world} | Part: {part}"
        )


# ============================================
# دوال مساعدة للاستخدام السريع
# ============================================

# إنشاء مدير السجلات العام
logger_manager = LoggerManager()

def setup_logger():
    """إعداد السجلات (للاستخدام من main.py)"""
    return logger_manager

def get_logger(name: str) -> logging.Logger:
    """الحصول على سجل معين"""
    return logger_manager.get_logger(name)

def log_command(user_id: int, username: str, command: str, args: str = ""):
    """تسجيل أمر"""
    logger_manager.log_command(user_id, username, command, args)

def log_error(error: Exception, context: str = ""):
    """تسجيل خطأ"""
    logger_manager.log_error(error, context)

def log_event(event_type: str, data: dict):
    """تسجيل حدث"""
    logger_manager.log_event(event_type, data)

def log_performance(operation: str, duration: float):
    """تسجيل أداء"""
    logger_manager.log_performance(operation, duration)

def log_user_action(user_id: int, action: str, details: str = ""):
    """تسجيل إجراء مستخدم"""
    logger_manager.log_user_action(user_id, action, details)


# ============================================
# كلاس مخصص للـ Context Manager
# ============================================

class LogPerformance:
    """Context manager لقياس أداء كتلة من الكود"""
    
    def __init__(self, operation: str):
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        log_performance(self.operation, duration)
        
        if exc_type:
            log_error(exc_val, f"في {self.operation}")


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'logger_manager',
    'setup_logger',
    'get_logger',
    'log_command',
    'log_error',
    'log_event',
    'log_performance',
    'log_user_action',
    'LogPerformance'
]
