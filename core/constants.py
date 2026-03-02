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
    "info": 0x3498db,         # أزرق - للمعلومات
    "dark": 0x2c3e50,         # كحلي - للظلام
    "light": 0xf1c40f         # ذهبي - للنور
}

# ============================================
# روابط الفواصل (الـ Dividers) - صورك الجديدة
# ============================================
WORLD_DIVIDERS = {
    "fantasy": "https://media.discordapp.net/attachments/1475249056036032554/1477783191111864470/fantasy_copy.png?ex=69a60458&is=69a4b2d8&hm=1edb25b0145af29a3dcd648c53c3cd976b42559b83da95d7d397dd3c9db9f648&=&format=webp&quality=lossless&width=600&height=120",
    
    "retro": "https://media.discordapp.net/attachments/1475249056036032554/1477783192307240990/past_copy.png?ex=69a60458&is=69a4b2d8&hm=77b26cde5fca36c5883021c69024aee428381fd32f7efabb9425755533da7711&=&format=webp&quality=lossless&width=600&height=120",
    
    "future": "https://media.discordapp.net/attachments/1475249056036032554/1477783191736553693/future_copy.png?ex=69a60458&is=69a4b2d8&hm=a65d179b9f006b63dde885383d63ebd6541982ff538bfd2bfd9ef7375e92af22&=&format=webp&quality=lossless&width=600&height=120",
    
    "alternate": "https://media.discordapp.net/attachments/1475249056036032554/1477783190474194946/aternatve_copy.png?ex=69a60458&is=69a4b2d8&hm=dc9a1080252efc0651106bc24e8a9550664322601e81beb29f689654130f2e39&=&format=webp&quality=lossless&width=600&height=120",
    
    "general": "https://media.discordapp.net/attachments/1472302270770053120/1472303048943468695/IMG_3554.gif?ex=699f4390&is=699df210&hm=f8f917593e7434a346a8f09afa943fedbafbda9fd7c979334a3b09fc53ac4a3a&=&width=675&height=36",
    
    "combat": "https://media.discordapp.net/attachments/1475249056036032555/1475949842902683710/IMG_7045.png?ex=699f58e8&is=699e0768&hm=815d85803ff82737a7db1eb8cc4046c609038ee3d6bb6c520a83b323661196ee&=&format=webp&quality=lossless&width=600&height=90",
    
    "city": "https://media.discordapp.net/attachments/1475249056036032555/1475949756751679488/IMG_9090.png?ex=699f58d3&is=699e0753&hm=715e9b08ccceda4c2db76f2b6f698ec94487482ee2caa44ca4ed7c18b59edcbe&=&format=webp&quality=lossless&width=315&height=48",
    
    "nature": "https://media.discordapp.net/attachments/1475249056036032555/1475949815392243762/IMG_9160.gif?ex=699f58e1&is=699e0761&hm=e8ed0637453557bdb5ba5a051197e7fe4b5a3c9e0233eb797e94bfe08a7888a6&=&width=260&height=96",
    
    "dark": "https://media.discordapp.net/attachments/1475249056036032555/1475949841241866302/IMG_9464.gif?ex=699f58e7&is=699e0767&hm=23c42d53be60e6efb6a9fc8c8188798237b431157a6f116995d864a29f2e7d46&=&width=600&height=168",
    
    "shard": "https://media.discordapp.net/attachments/1475249056036032555/1475949754281234564/IMG_8722.gif?ex=699f58d3&is=699e0753&hm=e4ec64a8dd5dad334f8ebda6c756c1fb822d79b2d9829567fd1f93c2a861caaf&=&width=902&height=32",
    
    "ending": "https://media.discordapp.net/attachments/1475249056036032555/1475949741681541204/t3oosp.png?ex=699f58d0&is=699e0750&hm=bc244db5574d6188a1d50c707f2b02edf9b3cc4653ddf92f4b654cc23b2b7a86&=&format=webp&quality=lossless&width=1500&height=627"
}

# ============================================
# الإيموجيات الخاصة بكل عالم
# ============================================
WORLD_EMOJIS = {
    "fantasy": "🌲",
    "retro": "📜",
    "past": "📜",  # مرادف
    "future": "🤖",
    "alternate": "🌀",
    "alt": "🌀",  # مرادف
    "general": "🌟",
    "light": "✨",
    "dark": "🌑",
    "gray": "⚪",
    "shard": "💎",
    "combat": "⚔️",
    "explore": "🔍",
    "talk": "💬",
    "flee": "🏃"
}

# ============================================
# أسماء العوالم (للاستخدام في الرسائل)
# ============================================
WORLD_NAMES = {
    "fantasy": "عالم الفانتازيا",
    "retro": "عالم الماضي",
    "past": "عالم الماضي",  # مرادف
    "future": "عالم المستقبل",
    "alternate": "الواقع البديل",
    "alt": "الواقع البديل",  # مرادف
    "general": "العالم العام"
}

# ============================================
# أوصاف العوالم
# ============================================
WORLD_DESCRIPTIONS = {
    "fantasy": (
        "أول نقطة استقرار بعد الضياع. الزمن هنا لا يسير للأمام ولا يعود للخلف... "
        "بل يقف منتظراً. السما صافية، البحر هادئ، لكن العالم يراقب... لأنه ما زال يتكون."
    ),
    "retro": (
        "عالم الماضي ليس مكاناً... بل حالة. الزمن هنا متسق، يدور في حلقات متكررة. "
        "أمكنة مألوفة، وجوه تعرفها لكنها لا تعرفك. كل شيء يتظفرك، ليس للترحيب بل للمحاسبة."
    ),
    "future": (
        "في هذا العالم... لم يأت المستقبل كعلم، بل حكم نهائي. المدن ارتفعت، الآلات تطورت، "
        "والعقل انسحب. كل شيء فعال، كل شيء صامت. لكن في هذا الصمت، هناك نبض خافت..."
    ),
    "alternate": (
        "هنا لا توجد حدود. لا زمن ثابت، لا شكل دائم. في الواقع البديل لم ينته الوجود، "
        "بل فقد معناه. لم يعد هناك خطر زمني واضح، بل انكسر العالم إلى احتمالات. "
        "ومن بين هذا الكسر ولد عالم لم يكن يجب أن يوجد."
    )
}

# ============================================
# قواعد فتح العوالم (Unlock Rules)
# ============================================
WORLD_UNLOCK_RULES = {
    "fantasy": {
        "required_ending": None,          # متاح من البداية
        "required_level": 1,
        "description": "✓ متاح للجميع",
        "order": 1
    },
    "retro": {
        "required_ending": "fantasy_ending",  # يحتاج نهاية من عالم الفانتازيا
        "required_level": 3,
        "description": "🔓 يفتح بعد إكمال عالم الفانتازيا",
        "order": 2
    },
    "future": {
        "required_ending": "retro_ending",
        "required_level": 5,
        "description": "🔓 يفتح بعد إكمال عالم الماضي",
        "order": 3
    },
    "alternate": {
        "required_ending": "future_ending",
        "required_level": 7,
        "description": "🔓 يفتح بعد إكمال عالم المستقبل",
        "order": 4
    }
}

# ============================================
# إعدادات البوت
# ============================================
BOT_CONFIG = {
    "name": "نيكسس بوت",
    "command_prefix": "/",  # ✅ البادئة المطلوبة
    "default_world": "fantasy",
    "max_history": 50,          # أقصى عدد للقرارات المحفوظة
    "daily_cooldown": 86400,    # 24 ساعة بالثواني
    "version": "1.0.0"
}

# ============================================
# إعدادات تحديد السرعة (Rate Limiting)
# ============================================
RATE_LIMITS = {
    "commands_per_minute": 10,
    "buttons_per_minute": 20,
    "daily_limit": 1,
    "cooldown_message": "⏳ انتظر قليلاً قبل استخدام الأمر مرة أخرى"
}

# ============================================
# إعدادات قاعدة البيانات
# ============================================
DATABASE_CONFIG = {
    "path": "data/database/nexus.db",
    "timeout": 10,               # ثواني
    "backup_interval": 86400,    # 24 ساعة
    "auto_backup": True,
    "max_backups": 7              # احتفظ بآخر 7 نسخ
}

# ============================================
# إعدادات المستويات والخبرة
# ============================================
LEVEL_CONFIG = {
    "base_xp": 100,              # XP للمستوى الأول
    "xp_multiplier": 1.5,         # مضاعف كل مستوى
    "max_level": 20,
    "xp_per_choice": 10,          # XP لكل قرار
    "xp_per_achievement": 50,      # XP إضافي لكل إنجاز
    "xp_per_daily": 100            # XP للمكافأة اليومية
}

# ============================================
# المتغيرات الأساسية في اللعبة
# ============================================
GAME_VARIABLES = {
    # متغيرات عامة
    "shards": {
        "min": 0, "max": 999, "default": 0, 
        "emoji": "💎", "name": "الشظايا",
        "description": "قطع من طاقة النيكسس، تمنحك قوة"
    },
    "corruption": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "🌑", "name": "الفساد",
        "description": "كلما زاد، اقتربت من الظلام"
    },
    "mystery": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "🔮", "name": "الغموض",
        "description": "معرفتك بأسرار النيكسس"
    },
    "reputation": {
        "min": -50, "max": 50, "default": 0, 
        "emoji": "⭐", "name": "السمعة",
        "description": "سمعتك بين سكان العوالم"
    },
    "alignment": {
        "options": ["Light", "Gray", "Dark"], 
        "default": "Gray", 
        "emoji": "⚖️", "name": "التوجه",
        "description": "نور - رمادي - ظلام"
    },
    "world_stability": {
        "min": 0, "max": 100, "default": 100, 
        "emoji": "🌍", "name": "استقرار العالم",
        "description": "كلما انخفض، اقتربت النهاية"
    },
    
    # متغيرات خاصة بكل عالم
    "fantasy_power": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "✨", "name": "قوة الفانتازيا",
        "description": "قوتك في عالم الأحلام"
    },
    "memories": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "📜", "name": "الذكريات",
        "description": "ذكريات مستعادة من الماضي"
    },
    "tech_level": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "⚙️", "name": "مستوى التكنولوجيا",
        "description": "تطورك التقني في المستقبل"
    },
    "identity": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "🌀", "name": "الهوية",
        "description": "فهمك لحقيقتك في الواقع البديل"
    },
    
    # متغيرات العلاقات
    "trust_aren": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "🤝", "name": "ثقة أرين",
        "description": "مدى ثقة رفيقك بك"
    },
    
    # متغيرات تطورية
    "xp": {
        "min": 0, "max": 10000, "default": 0, 
        "emoji": "🌟", "name": "خبرة",
        "description": "نقاط الخبرة"
    },
    "level": {
        "min": 1, "max": 20, "default": 1, 
        "emoji": "📊", "name": "المستوى",
        "description": "مستوى المغامر"
    },
    "knowledge_path": {
        "min": 0, "max": 100, "default": 0, 
        "emoji": "📚", "name": "طريق المعرفة",
        "description": "معرفتك العميقة بالشظايا"
    }
}

# ============================================
# رسائل النظام
# ============================================
SYSTEM_MESSAGES = {
    # رسائل الأخطاء
    "error": {
        "not_started": "❌ لم تبدأ رحلتك بعد! استخدم `/ابدأ` أولاً",
        "wrong_user": "❌ هذه القصة ليست لك! ابدأ رحلتك الخاصة بـ `/ابدأ`",
        "invalid_choice": "❌ هذا الخيار غير متاح حالياً",
        "world_locked": "❌ هذا العالم مقفل! أكمل العالم السابق أولاً",
        "no_item": "❌ ليس لديك هذا العنصر في مخزونك",
        "daily_cooldown": "⌛ انتظر {hours} ساعة و {minutes} دقيقة للمكافأة التالية",
        "invalid_world": "❌ عالم غير موجود",
        "no_progress": "❌ لا يوجد تقدم في هذا العالم",
        "command_cooldown": "⏳ استخدم الأمر بعد {seconds} ثانية"
    },
    
    # رسائل النجاح
    "success": {
        "game_started": "✅ بدأت رحلتك في {world}!",
        "choice_made": "✅ تم تسجيل قرارك",
        "daily_claimed": "🎁 حصلت على مكافأتك اليومية: {rewards}",
        "item_used": "✅ تم استخدام {item} بنجاح",
        "achievement_unlocked": "🏆 إنجاز جديد: {achievement}",
        "world_unlocked": "🔓 تم فتح {world}!",
        "level_up": "⬆️ وصلت إلى المستوى {level}!"
    },
    
    # رسائل تحذيرية
    "warning": {
        "high_corruption": "⚠️ الفساد مرتفع! احذر من الظلام",
        "low_stability": "⚠️ استقرار العالم منخفض!",
        "danger": "⚠️ خطر! فكر جيداً قبل الاختيار"
    },
    
    # رسائل معلومات
    "info": {
        "welcome": "✨ مرحباً بك في النيكسس! ابدأ رحلتك بـ `/ابدأ`",
        "help": "📚 استخدم `/مساعدة` لعرض كل الأوامر",
        "worlds": "🌍 لديك {count} عوالم متاحة"
    }
}

# ============================================
# قنوات السيرفر (حسب صورتك)
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
    },
    "general": {
        "welcome": "✦-الترحيب",
        "commands": "✦-الأوامر",
        "announcements": "✦-الإعلانات"
    }
}

# ============================================
# أنماط الأزرار (Button Styles)
# ============================================
BUTTON_STYLES = {
    "primary": discord.ButtonStyle.primary,     # أزرق
    "secondary": discord.ButtonStyle.secondary, # رمادي
    "success": discord.ButtonStyle.success,     # أخضر
    "danger": discord.ButtonStyle.danger,       # أحمر
    "combat": discord.ButtonStyle.danger,       # قتال
    "explore": discord.ButtonStyle.primary,     # استكشاف
    "talk": discord.ButtonStyle.secondary,      # حوار
    "flee": discord.ButtonStyle.secondary,      # هروب
    "item": discord.ButtonStyle.success,        # عنصر
    "shard": discord.ButtonStyle.success,       # شظية
    "confirm": discord.ButtonStyle.success,     # تأكيد
    "cancel": discord.ButtonStyle.danger,       # إلغاء
    "back": discord.ButtonStyle.secondary,      # رجوع
    "next": discord.ButtonStyle.primary         # تالي
}

# ============================================
# أنواع النهايات
# ============================================
ENDING_TYPES = {
    "light": {
        "name": "نهاية النور",
        "emoji": "✨",
        "color": 0xf1c40f,
        "description": "حافظت على نورك وأنقذت العالم"
    },
    "dark": {
        "name": "نهاية الظلام",
        "emoji": "🌑",
        "color": 0x2c3e50,
        "description": "استسلمت للفساد وأصبحت سيد الظل"
    },
    "gray": {
        "name": "نهاية التوازن",
        "emoji": "⚖️",
        "color": 0x95a5a6,
        "description": "وازنت بين النور والظلام"
    },
    "secret": {
        "name": "نهاية سرية",
        "emoji": "🔮",
        "color": 0x9b59b6,
        "description": "اكتشفت حقيقة النيكسس"
    }
}

# ============================================
# دوال مساعدة للثوابت
# ============================================
def get_world_color(world_id: str) -> int:
    """الحصول على لون العالم"""
    return WORLD_COLORS.get(world_id, WORLD_COLORS["general"])

def get_world_divider(world_id: str) -> str:
    """الحصول على فاصل العالم"""
    return WORLD_DIVIDERS.get(world_id, WORLD_DIVIDERS["general"])

def get_world_emoji(world_id: str) -> str:
    """الحصول على إيموجي العالم"""
    return WORLD_EMOJIS.get(world_id, WORLD_EMOJIS["general"])

def get_world_name(world_id: str) -> str:
    """الحصول على اسم العالم"""
    return WORLD_NAMES.get(world_id, world_id)

def get_world_description(world_id: str) -> str:
    """الحصول على وصف العالم"""
    return WORLD_DESCRIPTIONS.get(world_id, "")

def get_button_style(style_name: str) -> discord.ButtonStyle:
    """الحصول على نمط الزر"""
    return BUTTON_STYLES.get(style_name, discord.ButtonStyle.secondary)

def create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """إنشاء شريط تقدم"""
    percent = max(0, min(current / maximum, 1.0))
    filled = int(length * percent)
    empty = length - filled
    return "🟪" * filled + "⬜" * empty

def clamp(value: int, min_val: int, max_val: int) -> int:
    """تقييد قيمة بين حدين"""
    return max(min_val, min(max_val, value))
