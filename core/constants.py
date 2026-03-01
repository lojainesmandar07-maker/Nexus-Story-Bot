# core/constants.py - كل الثوابت والألوان والإعدادات الثابتة

import discord

# ============================================
# ألوان العوالم (للاستخدام في Embeds)
# ============================================
WORLD_COLORS = {
    "fantasy": 0x9b59b6,      # بنفسجي - عالم الفانتازيا
    "retro": 0x3498db,        # أزرق - عالم الماضي
    "future": 0xe74c3c,       # أحمر - عالم المستقبل
    "alternate": 0x2ecc71,    # أخضر - الواقع البديل
    "general": 0xf1c40f,      # ذهبي - عام
    "error": 0xe74c3c,        # أحمر - للأخطاء
    "success": 0x2ecc71,      # أخضر - للنجاح
    "warning": 0xf39c12,      # برتقالي - للتحذيرات
    "info": 0x3498db          # أزرق - للمعلومات
}

# ============================================
# روابط الفواصل (الـ Dividers) - حسب الصور الجديدة
# ============================================
WORLD_DIVIDERS = {
    "fantasy": "https://media.discordapp.net/attachments/1475249056036032554/1477783191111864470/fantasy_copy.png?ex=69a60458&is=69a4b2d8&hm=1edb25b0145af29a3dcd648c53c3cd976b42559b83da95d7d397dd3c9db9f648&=&format=webp&quality=lossless&width=600&height=120",
    
    "retro": "https://media.discordapp.net/attachments/1475249056036032554/1477783192307240990/past_copy.png?ex=69a60458&is=69a4b2d8&hm=77b26cde5fca36c5883021c69024aee428381fd32f7efabb9425755533da7711&=&format=webp&quality=lossless&width=600&height=120",
    
    "future": "https://media.discordapp.net/attachments/1475249056036032554/1477783191736553693/future_copy.png?ex=69a60458&is=69a4b2d8&hm=a65d179b9f006b63dde885383d63ebd6541982ff538bfd2bfd9ef7375e92af22&=&format=webp&quality=lossless&width=600&height=120",
    
    "alternate": "https://media.discordapp.net/attachments/1475249056036032554/1477783190474194946/aternatve_copy.png?ex=69a60458&is=69a4b2d8&hm=dc9a1080252efc0651106bc24e8a9550664322601e81beb29f689654130f2e39&=&format=webp&quality=lossless&width=600&height=120",
    
    "general": "https://media.discordapp.net/attachments/1472302270770053120/1472303048943468695/IMG_3554.gif?ex=699f4390&is=699df210&hm=f8f917593e7434a346a8f09afa943fedbafbda9fd7c979334a3b09fc53ac4a3a&=&width=675&height=36"
}

# ============================================
# الإيموجيات الخاصة بكل عالم
# ============================================
WORLD_EMOJIS = {
    "fantasy": "🌲",
    "retro": "📜",
    "future": "🤖",
    "alternate": "🌀",
    "general": "🌟"
}

# ============================================
# أسماء العوالم (للرسائل)
# ============================================
WORLD_NAMES = {
    "fantasy": "عالم الفانتازيا",
    "retro": "عالم الماضي",
    "future": "عالم المستقبل",
    "alternate": "الواقع البديل"
}

# ============================================
# إعدادات قاعدة البيانات
# ============================================
DATABASE_CONFIG = {
    "path": "data/database/nexus.db",
    "timeout": 10,  # ثواني
    "backup_interval": 86400  # 24 ساعة بالثواني
}

# ============================================
# إعدادات البوت
# ============================================
BOT_CONFIG = {
    "command_prefix": "!",  # احتياطي (لكننا سنستخدم / بشكل أساسي)
    "default_world": "fantasy",
    "max_history": 50,  # أقصى عدد للقرارات المحفوظة
    "daily_cooldown": 86400,  # 24 ساعة بالثواني
    "rate_limit": {
        "commands_per_minute": 10,
        "buttons_per_minute": 20
    }
}

# ============================================
# إعدادات المستويات والخبرة
# ============================================
LEVEL_CONFIG = {
    "base_xp": 100,  # XP للمستوى الأول
    "xp_multiplier": 1.5,  # مضاعف كل مستوى
    "max_level": 20,
    "xp_per_choice": 10,  # XP لكل قرار
    "xp_per_achievement": 50  # XP إضافي لكل إنجاز
}

# ============================================
# المتغيرات الأساسية في اللعبة
# ============================================
GAME_VARIABLES = {
    "shards": {"min": 0, "max": 999, "default": 0, "emoji": "💎"},
    "corruption": {"min": 0, "max": 100, "default": 0, "emoji": "🌑"},
    "mystery": {"min": 0, "max": 100, "default": 0, "emoji": "🔮"},
    "reputation": {"min": -50, "max": 50, "default": 0, "emoji": "⭐"},
    "alignment": {"options": ["Light", "Gray", "Dark"], "default": "Gray", "emoji": "⚖️"},
    "fantasy_power": {"min": 0, "max": 100, "default": 0, "emoji": "✨"},
    "memories": {"min": 0, "max": 100, "default": 0, "emoji": "📜"},
    "tech_level": {"min": 0, "max": 100, "default": 0, "emoji": "⚙️"},
    "identity": {"min": 0, "max": 100, "default": 0, "emoji": "🌀"}
}

# ============================================
# رسائل النظام
# ============================================
SYSTEM_MESSAGES = {
    "error": {
        "not_started": "❌ لم تبدأ رحلتك بعد! استخدم `/ابدأ` أولاً",
        "wrong_user": "❌ هذه القصة ليست لك! ابدأ رحلتك الخاصة بـ `/ابدأ`",
        "invalid_choice": "❌ هذا الخيار غير متاح حالياً",
        "world_locked": "❌ هذا العالم مقفل! أكمل العالم السابق أولاً",
        "no_item": "❌ ليس لديك هذا العنصر في مخزونك",
        "daily_cooldown": "⌛ انتظر {hours} ساعة و {minutes} دقيقة للمكافأة التالية"
    },
    "success": {
        "game_started": "✅ بدأت رحلتك في عالم {world}!",
        "choice_made": "✅ تم تسجيل قرارك",
        "daily_claimed": "🎁 حصلت على مكافأتك اليومية!"
    }
}

# ============================================
# قنوات السيرفر (حسب الصورة)
# ============================================
SERVER_CHANNELS = {
    "fantasy": {
        "records": "« • الجيل.سجلات",
        "posts": "« • الجيل.ستايالات",
        "chat": "« • الجيل.دردشة"
    },
    "retro": {
        "records": "« • الريترو.سجلات",
        "posts": "« • الريترو.ستايالات",
        "chat": "« • الريترو.دردشة"
    },
    "future": {
        "records": "« • المستقبل.سجلات",
        "posts": "« • المستقبل.ستايالات",
        "chat": "« • المستقبل.دردشة"
    },
    "alternate": {
        "records": "« • البديل.السجلات.الواقع",
        "posts": "« • البديل.ستايالات.الواقع",
        "chat": "« • البديل.دردشة.الواقع"
    }
}
