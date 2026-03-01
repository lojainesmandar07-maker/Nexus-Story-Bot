# utils/helpers.py - دوال مساعدة عامة

import random
import re
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import math

# ============================================
# دوال الوقت والتاريخ
# ============================================

def format_time(seconds: Union[int, float]) -> str:
    """
    تحويل الثواني إلى نص مفهوم
    مثال: 3661 ثانية -> "1 ساعة و 1 دقيقة و 1 ثانية"
    """
    if seconds < 0:
        seconds = 0
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} ساعة" + ("" if hours == 1 else ""))
    if minutes > 0:
        parts.append(f"{minutes} دقيقة" + ("" if minutes == 1 else ""))
    if secs > 0 or not parts:
        parts.append(f"{secs} ثانية" + ("" if secs == 1 else ""))
    
    return " و ".join(parts)

def format_datetime(dt: datetime) -> str:
    """تنسيق التاريخ والوقت"""
    return dt.strftime("%Y/%m/%d %H:%M:%S")

def parse_duration(duration_str: str) -> Optional[int]:
    """
    تحويل نص مدة إلى ثواني
    مثال: "1h30m" -> 5400
    """
    pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        return None
    
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    
    return hours * 3600 + minutes * 60 + seconds

def time_until(target_time: datetime) -> timedelta:
    """الوقت المتبقي حتى وقت معين"""
    return target_time - datetime.now()

def is_expired(timestamp: Optional[str], max_age: int) -> bool:
    """التحقق مما إذا كان طابع زمني قد انتهى"""
    if not timestamp:
        return True
    
    try:
        dt = datetime.fromisoformat(timestamp)
        age = (datetime.now() - dt).total_seconds()
        return age > max_age
    except:
        return True


# ============================================
# دوال الأرقام والإحصائيات
# ============================================

def clamp(value: Union[int, float], minimum: Union[int, float], maximum: Union[int, float]) -> Union[int, float]:
    """تقييد قيمة بين حدين"""
    return max(minimum, min(maximum, value))

def percentage(part: Union[int, float], whole: Union[int, float]) -> float:
    """حساب النسبة المئوية"""
    if whole == 0:
        return 0
    return (part / whole) * 100

def weighted_choice(choices: List[Dict[str, Any]]) -> Any:
    """
    اختيار عشوائي مع أوزان
    choices = [{"value": "a", "weight": 5}, {"value": "b", "weight": 1}]
    """
    total = sum(choice.get("weight", 1) for choice in choices)
    r = random.uniform(0, total)
    upto = 0
    
    for choice in choices:
        weight = choice.get("weight", 1)
        if upto + weight >= r:
            return choice.get("value")
        upto += weight
    
    return choices[-1].get("value") if choices else None

def format_number(num: Union[int, float]) -> str:
    """تنسيق الأرقام (مثال: 1000 -> 1,000)"""
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"

def calculate_level(xp: int, base_xp: int = 100, multiplier: float = 1.5) -> int:
    """حساب المستوى بناءً على الخبرة"""
    level = 1
    xp_needed = base_xp
    
    while xp >= xp_needed and level < 100:
        xp -= xp_needed
        level += 1
        xp_needed = int(base_xp * (multiplier ** (level - 1)))
    
    return level

def xp_for_level(level: int, base_xp: int = 100, multiplier: float = 1.5) -> int:
    """حساب الخبرة المطلوبة لمستوى معين"""
    if level <= 1:
        return 0
    
    total = 0
    for i in range(1, level):
        total += int(base_xp * (multiplier ** (i - 1)))
    
    return total


# ============================================
# دوال النصوص
# ============================================

def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """قص النص إذا كان طويلاً"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """تنظيف النص من الرموز غير المرغوب فيها"""
    # إزالة Markdown
    text = re.sub(r'[*_`~>|]', '', text)
    # إزالة الروابط
    text = re.sub(r'https?://\S+', '[رابط]', text)
    return text.strip()

def extract_mentions(text: str) -> List[int]:
    """استخراج منشنات من النص"""
    pattern = r'<@!?(\d+)>'
    return [int(id) for id in re.findall(pattern, text)]

def format_list(items: List[str], style: str = "bullet") -> str:
    """تنسيق قائمة"""
    if style == "bullet":
        return "\n".join(f"• {item}" for item in items)
    elif style == "number":
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    elif style == "arrow":
        return "\n".join(f"→ {item}" for item in items)
    return "\n".join(items)

def pluralize(count: int, singular: str, plural: str = None) -> str:
    """جمع الكلمات حسب العدد"""
    if count == 1:
        return f"{count} {singular}"
    return f"{count} {plural or singular + 'ات'}"

def create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """إنشاء شريط تقدم"""
    percent = clamp(current / maximum, 0, 1)
    filled = int(length * percent)
    empty = length - filled
    
    return "🟩" * filled + "⬜" * empty


# ============================================
# دوال عشوائية
# ============================================

def random_id(length: int = 8) -> str:
    """إنشاء ID عشوائي"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(length))

def random_color() -> int:
    """لون عشوائي لـ Discord"""
    return random.randint(0, 0xFFFFFF)

def random_chance(percent: float) -> bool:
    """فرصة عشوائية بنسبة مئوية"""
    return random.random() < (percent / 100)

def random_from_weighted(weights: Dict[str, float]) -> str:
    """اختيار عشوائي من قاموس الأوزان"""
    total = sum(weights.values())
    r = random.uniform(0, total)
    upto = 0
    
    for key, weight in weights.items():
        if upto + weight >= r:
            return key
        upto += weight
    
    return list(weights.keys())[-1]


# ============================================
# دوال JSON والبيانات
# ============================================

def safe_json_loads(text: str, default: Any = None) -> Any:
    """تحميل JSON بأمان"""
    try:
        return json.loads(text)
    except:
        return default

def safe_json_dumps(data: Any, **kwargs) -> str:
    """تحويل إلى JSON بأمان"""
    try:
        return json.dumps(data, ensure_ascii=False, **kwargs)
    except:
        return "{}"

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """دمج قاموسين (عميق)"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def deep_get(obj: Dict, path: str, default: Any = None) -> Any:
    """الحصول على قيمة من قاموس عميق"""
    keys = path.split('.')
    value = obj
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value


# ============================================
# دوال التشفير والأمان
# ============================================

def hash_string(text: str) -> str:
    """تشفير نص"""
    return hashlib.sha256(text.encode()).hexdigest()

def generate_token() -> str:
    """توليد رمز عشوائي"""
    return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:32]

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ============================================
# دوال Discord
# ============================================

def discord_timestamp(dt: datetime, style: str = "f") -> str:
    """
    إنشاء طابع زمني لـ Discord
    الأنماط: f (تاريخ ووقت), R (وقت نسبي), d (تاريخ), t (وقت)
    """
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:{style}>"

def format_discord_time(seconds: int, style: str = "R") -> str:
    """تنسيق وقت لـ Discord"""
    return f"<t:{seconds}:{style}>"

def create_command_mention(command_name: str) -> str:
    """إنشاء منشن لأمر سلاش"""
    return f"</{command_name}:0>"


# ============================================
# دوال ألعاب
# ============================================

def calculate_damage(attack: int, defense: int) -> int:
    """حساب الضرر في المعارك"""
    base = attack - defense // 2
    variance = random.randint(-base // 5, base // 5)
    return max(1, base + variance)

def calculate_crit_chance(luck: int) -> float:
    """حساب فرصة الضربة القاضية"""
    return clamp(luck / 100, 0.05, 0.3)

def calculate_xp_reward(level: int, difficulty: float = 1.0) -> int:
    """حساب مكافأة الخبرة"""
    base = 10 * level
    multiplier = clamp(difficulty, 0.5, 2.0)
    return int(base * multiplier)

def calculate_gold_reward(level: int, luck: int) -> int:
    """حساب مكافأة العملة"""
    base = random.randint(level * 5, level * 15)
    bonus = random.randint(0, luck)
    return base + bonus


# ============================================
# دوال تحليل القرارات
# ============================================

def parse_effects(effects: Dict[str, Any]) -> List[str]:
    """تحويل التأثيرات إلى نص مفهوم"""
    result = []
    
    for key, value in effects.items():
        if key == "achievement":
            result.append(f"🏆 إنجاز: {value}")
        elif key == "inventory_add":
            if isinstance(value, dict):
                name = value.get("name", value.get("id", "عنصر"))
                qty = value.get("qty", 1)
                result.append(f"📦 +{qty} {name}")
            else:
                result.append(f"📦 +{value}")
        elif key == "inventory_remove":
            if isinstance(value, dict):
                name = value.get("name", value.get("id", "عنصر"))
                qty = value.get("qty", 1)
                result.append(f"📦 -{qty} {name}")
            else:
                result.append(f"📦 -{value}")
        elif key == "flag":
            result.append(f"🚩 {value}")
        elif key == "relationship":
            if ':' in value:
                char, change = value.split(':', 1)
                result.append(f"❤️ {char}: {change:+}")
        elif isinstance(value, (int, float)):
            if value > 0:
                result.append(f"📈 {key}: +{value}")
            elif value < 0:
                result.append(f"📉 {key}: {value}")
    
    return result

def summarize_effects(effects: Dict[str, Any]) -> str:
    """تلخيص التأثيرات في جملة واحدة"""
    parsed = parse_effects(effects)
    if not parsed:
        return "لا تأثير"
    return " | ".join(parsed[:3]) + ("..." if len(parsed) > 3 else "")


# ============================================
# دوال المهام غير المتزامنة
# ============================================

async def run_in_executor(func, *args):
    """تشغيل دالة في منفذ منفصل"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

async def wait_with_condition(condition_func, timeout: float = 30.0, interval: float = 0.1):
    """الانتظار حتى تتحقق حالة معينة"""
    start = datetime.now()
    while (datetime.now() - start).total_seconds() < timeout:
        if condition_func():
            return True
        await asyncio.sleep(interval)
    return False

def create_task(coro):
    """إنشاء مهمة غير متزامنة"""
    return asyncio.create_task(coro)


# ============================================
# دوال تحقق
# ============================================

def is_valid_world(world_id: str) -> bool:
    """التحقق من صحة معرف العالم"""
    valid_worlds = ["fantasy", "retro", "future", "alternate", "past", "alt"]
    return world_id.lower() in valid_worlds

def normalize_world_id(world_id: str) -> str:
    """تطبيع معرف العالم"""
    mapping = {
        "past": "retro",
        "alt": "alternate"
    }
    return mapping.get(world_id.lower(), world_id.lower())

def is_valid_choice(choice: Dict) -> bool:
    """التحقق من صحة كائن الخيار"""
    required = ["text", "next"]
    return all(key in choice for key in required)


# ============================================
# دوال النظام
# ============================================

def get_system_info() -> Dict[str, Any]:
    """الحصول على معلومات النظام"""
    import platform
    import psutil
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(),
        "memory": psutil.virtual_memory().total // (1024 ** 2),  # MB
        "disk": psutil.disk_usage('/').free // (1024 ** 3)  # GB
    }

def get_memory_usage() -> float:
    """الحصول على استخدام الذاكرة بالميجابايت"""
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB


# ============================================
# تصدير الدوال
# ============================================

__all__ = [
    # الوقت
    'format_time', 'format_datetime', 'parse_duration',
    'time_until', 'is_expired',
    
    # الأرقام
    'clamp', 'percentage', 'weighted_choice',
    'format_number', 'calculate_level', 'xp_for_level',
    
    # النصوص
    'truncate', 'clean_text', 'extract_mentions',
    'format_list', 'pluralize', 'create_progress_bar',
    
    # عشوائية
    'random_id', 'random_color', 'random_chance',
    'random_from_weighted',
    
    # JSON
    'safe_json_loads', 'safe_json_dumps',
    'merge_dicts', 'deep_get',
    
    # التشفير
    'hash_string', 'generate_token', 'validate_email',
    
    # Discord
    'discord_timestamp', 'format_discord_time', 'create_command_mention',
    
    # ألعاب
    'calculate_damage', 'calculate_crit_chance',
    'calculate_xp_reward', 'calculate_gold_reward',
    
    # تحليل القرارات
    'parse_effects', 'summarize_effects',
    
    # مهام غير متزامنة
    'run_in_executor', 'wait_with_condition', 'create_task',
    
    # تحقق
    'is_valid_world', 'normalize_world_id', 'is_valid_choice',
    
    # النظام
    'get_system_info', 'get_memory_usage'
]
