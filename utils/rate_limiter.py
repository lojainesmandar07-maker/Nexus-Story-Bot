# utils/rate_limiter.py - نظام منع السبام وتحديد السرعة

import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """هيكل بيانات لتحديد السرعة"""
    max_requests: int  # أقصى عدد من الطلبات
    time_window: int   # الإطار الزمني بالثواني
    requests: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_request(self):
        """إضافة طلب جديد"""
        now = time.time()
        self.requests.append(now)
        # إزالة الطلبات القديمة
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
    
    def is_limited(self) -> bool:
        """التحقق مما إذا كان التحديد مفعل"""
        return len(self.requests) >= self.max_requests
    
    def remaining(self) -> int:
        """العدد المتبقي من الطلبات"""
        return max(0, self.max_requests - len(self.requests))
    
    def reset_time(self) -> float:
        """الوقت المتبقي لإعادة التعيين"""
        if not self.requests:
            return 0
        oldest = self.requests[0]
        return max(0, (oldest + self.time_window) - time.time())


@dataclass
class UserRateLimit:
    """تحديد السرعة لمستخدم معين"""
    user_id: int
    commands: Dict[str, RateLimit] = field(default_factory=dict)
    buttons: Dict[str, RateLimit] = field(default_factory=dict)
    last_reset: float = field(default_factory=time.time)
    warnings: int = 0
    blocked_until: float = 0.0
    
    def is_blocked(self) -> bool:
        """التحقق مما إذا كان المستخدم محظوراً مؤقتاً"""
        if self.blocked_until > time.time():
            return True
        return False
    
    def add_warning(self):
        """إضافة تحذير"""
        self.warnings += 1
        if self.warnings >= 3:
            # حظر لمدة 5 دقائق بعد 3 تحذيرات
            self.blocked_until = time.time() + 300
            self.warnings = 0
            logger.warning(f"🚫 تم حظر المستخدم {self.user_id} مؤقتاً بسبب السبام")
    
    def reset(self):
        """إعادة تعيين كل الحدود"""
        self.commands.clear()
        self.buttons.clear()
        self.last_reset = time.time()
        self.warnings = 0
        self.blocked_until = 0.0


class RateLimiter:
    """
    مدير تحديد السرعة المتقدم
    يمنع المستخدمين من إرسال أوامر كثيرة في وقت قصير
    """
    
    def __init__(self):
        # تخزين حدود المستخدمين
        self.users: Dict[int, UserRateLimit] = defaultdict(UserRateLimit)
        
        # حدود عامة للبوت
        self.global_commands = RateLimit(max_requests=100, time_window=60)   # 100 أمر في الدقيقة
        self.global_buttons = RateLimit(max_requests=200, time_window=60)    # 200 زر في الدقيقة
        
        # إعدادات افتراضية
        self.default_command_limit = 10    # 10 أوامر في الدقيقة
        self.default_button_limit = 20     # 20 زر في الدقيقة
        self.default_window = 60           # دقيقة واحدة
        
        # تخزين حدود مخصصة لكل أمر
        self.command_limits: Dict[str, Tuple[int, int]] = {}
        
        # إحصائيات
        self.stats = {
            "total_commands": 0,
            "total_buttons": 0,
            "blocked_commands": 0,
            "blocked_buttons": 0,
            "warnings_issued": 0
        }
    
    def set_command_limit(self, command: str, max_requests: int, time_window: int = 60):
        """تحديد حد مخصص لأمر معين"""
        self.command_limits[command] = (max_requests, time_window)
    
    def _get_user(self, user_id: int) -> UserRateLimit:
        """الحصول على كائن المستخدم (مع تحديث المعرف)"""
        if user_id not in self.users:
            self.users[user_id] = UserRateLimit(user_id=user_id)
        return self.users[user_id]
    
    def _get_command_limit(self, command: str) -> Tuple[int, int]:
        """الحصول على الحد المخصص لأمر معين"""
        return self.command_limits.get(command, (self.default_command_limit, self.default_window))
    
    def check_command(self, user_id: int, command: str) -> Tuple[bool, Optional[float]]:
        """
        التحقق من أمر
        يرجع: (مسموح, وقت الانتظار المتبقي)
        """
        user = self._get_user(user_id)
        
        # التحقق من الحظر
        if user.is_blocked():
            wait_time = user.blocked_until - time.time()
            return False, wait_time
        
        # التحقق من الحد العام
        if self.global_commands.is_limited():
            self.stats["blocked_commands"] += 1
            return False, self.global_commands.reset_time()
        
        # الحصول على الحد المخصص للأمر
        max_req, window = self._get_command_limit(command)
        
        # إنشاء حد للأمر إذا لم يكن موجوداً
        if command not in user.commands:
            user.commands[command] = RateLimit(max_requests=max_req, time_window=window)
        
        command_limit = user.commands[command]
        
        # التحقق من الحد
        if command_limit.is_limited():
            self.stats["blocked_commands"] += 1
            user.add_warning()
            return False, command_limit.reset_time()
        
        # تسجيل الأمر
        command_limit.add_request()
        self.global_commands.add_request()
        self.stats["total_commands"] += 1
        
        return True, 0
    
    def check_button(self, user_id: int, button_id: str) -> Tuple[bool, Optional[float]]:
        """
        التحقق من زر
        يرجع: (مسموح, وقت الانتظار المتبقي)
        """
        user = self._get_user(user_id)
        
        # التحقق من الحظر
        if user.is_blocked():
            wait_time = user.blocked_until - time.time()
            return False, wait_time
        
        # التحقق من الحد العام
        if self.global_buttons.is_limited():
            self.stats["blocked_buttons"] += 1
            return False, self.global_buttons.reset_time()
        
        # إنشاء حد للزر إذا لم يكن موجوداً
        if button_id not in user.buttons:
            user.buttons[button_id] = RateLimit(
                max_requests=self.default_button_limit,
                time_window=self.default_window
            )
        
        button_limit = user.buttons[button_id]
        
        # التحقق من الحد
        if button_limit.is_limited():
            self.stats["blocked_buttons"] += 1
            user.add_warning()
            return False, button_limit.reset_time()
        
        # تسجيل الزر
        button_limit.add_request()
        self.global_buttons.add_request()
        self.stats["total_buttons"] += 1
        
        return True, 0
    
    def check_daily(self, user_id: int, last_claim: Optional[str]) -> Tuple[bool, Optional[float]]:
        """
        التحقق من المكافأة اليومية
        يرجع: (مسموح, وقت الانتظار المتبقي)
        """
        if not last_claim:
            return True, 0
        
        try:
            last = datetime.fromisoformat(last_claim)
            next_claim = last + timedelta(days=1)
            now = datetime.now()
            
            if now < next_claim:
                wait_time = (next_claim - now).total_seconds()
                return False, wait_time
            
            return True, 0
        except:
            return True, 0
    
    def reset_user(self, user_id: int):
        """إعادة تعيين حدود مستخدم"""
        if user_id in self.users:
            self.users[user_id].reset()
            logger.info(f"🔄 تم إعادة تعيين حدود المستخدم {user_id}")
    
    def reset_all(self):
        """إعادة تعيين كل الحدود"""
        self.users.clear()
        self.global_commands.requests.clear()
        self.global_buttons.requests.clear()
        self.stats = {
            "total_commands": 0,
            "total_buttons": 0,
            "blocked_commands": 0,
            "blocked_buttons": 0,
            "warnings_issued": 0
        }
        logger.info("🔄 تم إعادة تعيين كل الحدود")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إحصائيات مستخدم"""
        user = self._get_user(user_id)
        
        return {
            "user_id": user_id,
            "is_blocked": user.is_blocked(),
            "blocked_until": user.blocked_until,
            "warnings": user.warnings,
            "commands_count": sum(len(limit.requests) for limit in user.commands.values()),
            "buttons_count": sum(len(limit.requests) for limit in user.buttons.values()),
            "commands": {
                cmd: {
                    "count": len(limit.requests),
                    "remaining": limit.remaining(),
                    "reset_in": limit.reset_time()
                }
                for cmd, limit in user.commands.items()
            }
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات عامة"""
        return {
            "total_commands": self.stats["total_commands"],
            "total_buttons": self.stats["total_buttons"],
            "blocked_commands": self.stats["blocked_commands"],
            "blocked_buttons": self.stats["blocked_buttons"],
            "warnings_issued": self.stats["warnings_issued"],
            "active_users": len(self.users),
            "global_commands": {
                "count": len(self.global_commands.requests),
                "remaining": self.global_commands.remaining(),
                "reset_in": self.global_commands.reset_time()
            },
            "global_buttons": {
                "count": len(self.global_buttons.requests),
                "remaining": self.global_buttons.remaining(),
                "reset_in": self.global_buttons.reset_time()
            }
        }
    
    def cleanup_old_users(self, max_age: int = 3600):
        """تنظيف المستخدمين القدامى (أكبر من ساعة)"""
        now = time.time()
        to_delete = []
        
        for user_id, user in self.users.items():
            if now - user.last_reset > max_age:
                to_delete.append(user_id)
        
        for user_id in to_delete:
            del self.users[user_id]
        
        if to_delete:
            logger.info(f"🧹 تم تنظيف {len(to_delete)} مستخدم قديم")
    
    def format_wait_message(self, seconds: float) -> str:
        """تنسيق رسالة الانتظار"""
        if seconds < 60:
            return f"⏳ انتظر {int(seconds)} ثانية"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"⏳ انتظر {minutes} دقيقة"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"⏳ انتظر {hours} ساعة و {minutes} دقيقة"


# ============================================
# Decorators للتحقق من السرعة
# ============================================

def rate_limit(command_name: str = None):
    """
    Decorator لتحديد سرعة الأوامر
    مثال: @rate_limit("ابدأ")
    """
    def decorator(func):
        async def wrapper(self, interaction, *args, **kwargs):
            user_id = interaction.user.id
            cmd = command_name or func.__name__
            
            # التحقق من الحد
            allowed, wait_time = self.bot.rate_limiter.check_command(user_id, cmd)
            
            if not allowed:
                if wait_time:
                    message = self.bot.rate_limiter.format_wait_message(wait_time)
                else:
                    message = "⏳ انتظر قليلاً قبل استخدام الأمر مرة أخرى"
                
                await interaction.response.send_message(message, ephemeral=True)
                return
            
            # تنفيذ الأمر
            return await func(self, interaction, *args, **kwargs)
        
        return wrapper
    return decorator


class ButtonRateLimit:
    """Context manager للتحقق من سرعة الأزرار"""
    
    def __init__(self, bot, user_id: int, button_id: str):
        self.bot = bot
        self.user_id = user_id
        self.button_id = button_id
        self.allowed = False
        self.wait_time = 0
    
    async def __aenter__(self):
        self.allowed, self.wait_time = self.bot.rate_limiter.check_button(
            self.user_id, self.button_id
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def send_wait_message(self, interaction):
        """إرسال رسالة انتظار"""
        if self.wait_time:
            message = self.bot.rate_limiter.format_wait_message(self.wait_time)
        else:
            message = "⏳ انتظر قليلاً قبل استخدام الزر مرة أخرى"
        
        await interaction.response.send_message(message, ephemeral=True)


# ============================================
# مهمة التنظيف الدورية
# ============================================

async def cleanup_task(rate_limiter: RateLimiter, interval: int = 300):
    """
    مهمة تنظيف دورية
    تعمل كل 5 دقائق لتنظيف المستخدمين القدامى
    """
    while True:
        await asyncio.sleep(interval)
        rate_limiter.cleanup_old_users()
        logger.debug("🧹 تم تشغيل مهمة تنظيف rate limiter")


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'RateLimiter',
    'rate_limit',
    'ButtonRateLimit',
    'cleanup_task'
]
