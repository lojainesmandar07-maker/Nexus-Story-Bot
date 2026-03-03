# game/achievements.py - نظام الإنجازات والمكافآت
# أكثر من 40 إنجاز مختلف في 4 عوالم

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class Achievement:
    """كلاس أساسي للإنجازات"""
    
    id: str
    name: str
    description: str
    emoji: str
    world: str  # fantasy, retro, future, alternate, general
    xp_reward: int = 50
    item_reward: Optional[Dict[str, Any]] = None
    hidden: bool = False  # إنجاز سري
    secret_condition: Optional[str] = None
    requires_all_endings: bool = False
    order: int = 0  # ترتيب الظهور
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس للتخزين"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "world": self.world,
            "xp_reward": self.xp_reward,
            "item_reward": self.item_reward,
            "hidden": self.hidden,
            "order": self.order
        }


# ============================================
# إنجازات عالم الفانتازيا 🌲
# ============================================

FANTASY_ACHIEVEMENTS = [
    Achievement(
        id="fantasy_explorer",
        name="مستكشف الفانتازيا",
        description="اكتشفت 5 أماكن سرية في عالم الفانتازيا",
        emoji="🗺️",
        world="fantasy",
        xp_reward=100,
        item_reward={"id": "magic_compass", "name": "🧭 بوصلة سحرية", "quantity": 1},
        order=1
    ),
    
    Achievement(
        id="fantasy_master",
        name="سيد الفانتازيا",
        description="أكملت عالم الفانتازيا بكل نهاياته الثلاث",
        emoji="👑",
        world="fantasy",
        xp_reward=300,
        item_reward={"id": "dream_catcher", "name": "🪶 صائدة الأحلام", "quantity": 1},
        requires_all_endings=True,
        order=10
    ),
    
    Achievement(
        id="dream_walker",
        name="سائر الأحلام",
        description="زرت كل المواقع في عالم الفانتازيا",
        emoji="🌙",
        world="fantasy",
        xp_reward=150,
        order=5
    ),
    
    Achievement(
        id="fairy_friend",
        name="صديق الجن",
        description="ساعدت مخلوقات الغابة المسحورة",
        emoji="🧚",
        world="fantasy",
        xp_reward=75,
        order=3
    ),
    
    Achievement(
        id="shadow_defeater",
        name="قاهر الظل",
        description="هزمت ملك الظل في معركة شريفة",
        emoji="⚔️",
        world="fantasy",
        xp_reward=200,
        item_reward={"id": "moon_stone", "name": "🌕 حجر القمر", "quantity": 1},
        order=8
    ),
    
    Achievement(
        id="pure_heart_fantasy",
        name="قلب نقي في الفانتازيا",
        description="أكملت عالم الفانتازيا بنقاء (فساد أقل من 20)",
        emoji="❤️",
        world="fantasy",
        xp_reward=150,
        order=7,
        hidden=True
    ),
    
    Achievement(
        id="corrupted_fantasy",
        name="فاسد في الأحلام",
        description="أكملت عالم الفانتازيا بفساد عالٍ (أكثر من 80)",
        emoji="🖤",
        world="fantasy",
        xp_reward=150,
        order=7,
        hidden=True
    ),
    
    Achievement(
        id="fantasy_speedrunner",
        name="عداء الفانتازيا",
        description="أكملت عالم الفانتازيا في أقل من 30 دقيقة",
        emoji="⚡",
        world="fantasy",
        xp_reward=200,
        order=9,
        hidden=True
    )
]

# ============================================
# إنجازات عالم الماضي 📜
# ============================================

RETRO_ACHIEVEMENTS = [
    Achievement(
        id="memory_keeper",
        name="حارس الذكريات",
        description="استعدت 10 ذكريات من الماضي",
        emoji="📻",
        world="retro",
        xp_reward=100,
        item_reward={"id": "memory_orb", "name": "🔮 كرة الذكريات", "quantity": 1},
        order=1
    ),
    
    Achievement(
        id="time_traveler",
        name="مسافر عبر الزمن",
        description="غيرت حدثاً مصيرياً في الماضي",
        emoji="⏳",
        world="retro",
        xp_reward=200,
        item_reward={"id": "time_sand", "name": "⏳ رمال الزمن", "quantity": 3},
        order=5
    ),
    
    Achievement(
        id="past_master",
        name="حكيم الماضي",
        description="أكملت عالم الماضي بكل نهاياته",
        emoji="👴",
        world="retro",
        xp_reward=300,
        requires_all_endings=True,
        order=10
    ),
    
    Achievement(
        id="forgiveness",
        name="التسامح",
        description="سامحت شخصاً من الماضي وتركت الأحقاد",
        emoji="🕊️",
        world="retro",
        xp_reward=150,
        order=6
    ),
    
    Achievement(
        id="childhood_return",
        name="العودة إلى الطفولة",
        description="زرت كل الأماكن من طفولتك",
        emoji="🏠",
        world="retro",
        xp_reward=75,
        order=3
    ),
    
    Achievement(
        id="regret_free",
        name="بلا ندم",
        description="لم تندم على أي قرار في عالم الماضي",
        emoji="😌",
        world="retro",
        xp_reward=150,
        order=8,
        hidden=True
    ),
    
    Achievement(
        id="ancestor_talk",
        name="حديث الأجداد",
        description="تحدثت مع كل شخصيات الماضي",
        emoji="👥",
        world="retro",
        xp_reward=125,
        order=4
    ),
    
    Achievement(
        id="past_changer",
        name="مغير الزمن",
        description="غيرت 3 أحداث مختلفة في الماضي",
        emoji="🔄",
        world="retro",
        xp_reward=250,
        order=9,
        hidden=True
    )
]

# ============================================
# إنجازات عالم المستقبل 🤖
# ============================================

FUTURE_ACHIEVEMENTS = [
    Achievement(
        id="tech_pioneer",
        name="رائد التكنولوجيا",
        description="طورت التكنولوجيا إلى أقصى حد (مستوى 100)",
        emoji="⚡",
        world="future",
        xp_reward=150,
        item_reward={"id": "cyber_implant", "name": "🦾 زرع إلكتروني", "quantity": 1},
        order=2
    ),
    
    Achievement(
        id="rebellion_leader",
        name="قائد التمرد",
        description="قادت ثورة ناجحة ضد النظام",
        emoji="⚔️",
        world="future",
        xp_reward=200,
        item_reward={"id": "rebellion_badge", "name": "⭐ شارة التمرد", "quantity": 1},
        order=5
    ),
    
    Achievement(
        id="future_master",
        name="سيد المستقبل",
        description="أكملت عالم المستقبل بكل نهاياته",
        emoji="🤖",
        world="future",
        xp_reward=300,
        requires_all_endings=True,
        order=10
    ),
    
    Achievement(
        id="ai_negotiator",
        name="مفاوض الآلات",
        description="توصلت لاتفاق سلمي مع الذكاء الاصطناعي",
        emoji="🤝",
        world="future",
        xp_reward=150,
        order=7
    ),
    
    Achievement(
        id="humanity_saver",
        name="منقذ الإنسانية",
        description="أنقذت آخر بقايا البشر",
        emoji="👨‍👩‍👧",
        world="future",
        xp_reward=250,
        order=8
    ),
    
    Achievement(
        id="cyber_warrior",
        name="محارب إلكتروني",
        description="انتصرت في 10 معارك ضد الآلات",
        emoji="🦾",
        world="future",
        xp_reward=125,
        order=3
    ),
    
    Achievement(
        id="machine_understanding",
        name="فهم الآلات",
        description="فهمت دوافع الذكاء الاصطناعي وتعاطفت معه",
        emoji="💭",
        world="future",
        xp_reward=100,
        order=6,
        hidden=True
    ),
    
    Achievement(
        id="future_destroyer",
        name="مدمر المستقبل",
        description="دمرت عالم المستقبل بالكامل",
        emoji="💥",
        world="future",
        xp_reward=200,
        order=9,
        hidden=True
    )
]

# ============================================
# إنجازات الواقع البديل 🌀
# ============================================

ALTERNATE_ACHIEVEMENTS = [
    Achievement(
        id="truth_seeker",
        name="باحث عن الحقيقة",
        description="اكتشفت الحقيقة المطلقة عن النيكسس",
        emoji="🔍",
        world="alternate",
        xp_reward=200,
        item_reward={"id": "truth_glass", "name": "🥃 كأس الحقيقة", "quantity": 1},
        order=3
    ),
    
    Achievement(
        id="reality_shaper",
        name="مُشكل الواقع",
        description="أعدت تشكيل واقعك بنفسك",
        emoji="🌀",
        world="alternate",
        xp_reward=300,
        order=7
    ),
    
    Achievement(
        id="alternate_master",
        name="حكيم الواقع",
        description="أكملت الواقع البديل بكل نهاياته الأربع",
        emoji="🌟",
        world="alternate",
        xp_reward=400,
        requires_all_endings=True,
        order=10
    ),
    
    Achievement(
        id="self_discovery",
        name="اكتشاف الذات",
        description="عرفت من أنت حقاً",
        emoji="👤",
        world="alternate",
        xp_reward=150,
        order=2
    ),
    
    Achievement(
        id="nexus_guardian",
        name="حارس النيكسس",
        description="حافظت على التوازن بين كل العوالم",
        emoji="⚖️",
        world="alternate",
        xp_reward=350,
        item_reward={"id": "nexus_crystal", "name": "💠 كريستال النيكسس", "quantity": 1},
        order=9
    ),
    
    Achievement(
        id="void_walker",
        name="سائر الفراغ",
        description="نجوت من السقوط في الفراغ",
        emoji="⬛",
        world="alternate",
        xp_reward=100,
        order=4,
        hidden=True
    ),
    
    Achievement(
        id="infinite_possibilities",
        name="احتمالات لا نهائية",
        description="رأيت 10 نسخ مختلفة من نفسك",
        emoji="∞",
        world="alternate",
        xp_reward=180,
        order=5
    ),
    
    Achievement(
        id="reality_breaker",
        name="كاسر الواقع",
        description="كسرت حاجز الواقع ودخلت البعد الرابع",
        emoji="🔓",
        world="alternate",
        xp_reward=250,
        order=8,
        hidden=True
    )
]

# ============================================
# إنجازات عامة 🌟
# ============================================

GENERAL_ACHIEVEMENTS = [
    Achievement(
        id="first_choice",
        name="أول قرار",
        description="اتخذت أول قرار في رحلتك",
        emoji="🎯",
        world="general",
        xp_reward=10,
        order=1
    ),
    
    Achievement(
        id="shard_collector",
        name="جامع الشظايا",
        description="جمعت 50 شظية",
        emoji="💎",
        world="general",
        xp_reward=150,
        item_reward={"id": "greater_shard", "name": "💎✨ شظية كبرى", "quantity": 1},
        order=20
    ),
    
    Achievement(
        id="shard_master",
        name="سيد الشظايا",
        description="جمعت 200 شظية",
        emoji="💎👑",
        world="general",
        xp_reward=300,
        item_reward={"id": "pure_shard", "name": "✨ شظية نقية", "quantity": 5},
        order=30
    ),
    
    Achievement(
        id="pure_heart",
        name="قلب نقي",
        description="حافظت على نقائك رغم الفساد (فساد أقل من 10 بعد المستوى 5)",
        emoji="😇",
        world="general",
        xp_reward=200,
        item_reward={"id": "potion", "name": "🧪 جرعة نقاء", "quantity": 10},
        order=25
    ),
    
    Achievement(
        id="corrupted_soul",
        name="روح مظلمة",
        description="استسلمت للفساد تماماً (فساد 100)",
        emoji="👿",
        world="general",
        xp_reward=200,
        item_reward={"id": "dark_core", "name": "🖤 نواة الظلام", "quantity": 3},
        order=25
    ),
    
    Achievement(
        id="balanced_one",
        name="المتوازن",
        description="حافظت على توازن تام بين النور والظلام",
        emoji="⚖️",
        world="general",
        xp_reward=250,
        order=28
    ),
    
    Achievement(
        id="high_level",
        name="مستوى عالٍ",
        description="وصلت إلى المستوى 10",
        emoji="📈",
        world="general",
        xp_reward=200,
        order=15
    ),
    
    Achievement(
        id="legendary_level",
        name="مستوى أسطوري",
        description="وصلت إلى المستوى 20",
        emoji="🌟",
        world="general",
        xp_reward=500,
        item_reward={"id": "mystery_box", "name": "🎁 صندوق غامض", "quantity": 3},
        order=35
    ),
    
    Achievement(
        id="daily_devoted",
        name="المخلص اليومي",
        description="حصلت على مكافأتك اليومية 7 أيام متتالية",
        emoji="📆",
        world="general",
        xp_reward=150,
        item_reward={"id": "crystal_heart", "name": "💖 قلب الكريستال", "quantity": 1},
        order=12
    ),
    
    Achievement(
        id="daily_legend",
        name="أسطورة الاستمرارية",
        description="حصلت على مكافأتك اليومية 30 يوماً",
        emoji="🔥",
        world="general",
        xp_reward=500,
        item_reward={"id": "mystery_box", "name": "🎁 صندوق غامض", "quantity": 5},
        order=40,
        hidden=True
    ),
    
    Achievement(
        id="choice_maker",
        name="صانع القرارات",
        description="اتخذت 100 قرار في اللعبة",
        emoji="🤔",
        world="general",
        xp_reward=200,
        order=18
    ),
    
    Achievement(
        id="choice_master",
        name="سيد القرارات",
        description="اتخذت 500 قرار في اللعبة",
        emoji="👑",
        world="general",
        xp_reward=500,
        order=38
    ),
    
    Achievement(
        id="explorer",
        name="المستكشف",
        description="زرت 20 موقعاً مختلفاً",
        emoji="🧭",
        world="general",
        xp_reward=150,
        order=14
    ),
    
    Achievement(
        id="world_traveler",
        name="مسافر العوالم",
        description="زرت كل العوالم الأربعة",
        emoji="🌍",
        world="general",
        xp_reward=300,
        order=22
    ),
    
    Achievement(
        id="collector",
        name="جامع",
        description="اقتنيت 20 عنصراً مختلفاً",
        emoji="📦",
        world="general",
        xp_reward=100,
        order=8
    ),
    
    Achievement(
        id="hoarder",
        name="مكتنز",
        description="اقتنيت 50 عنصراً مختلفاً",
        emoji="🏦",
        world="general",
        xp_reward=250,
        order=32
    ),
    
    Achievement(
        id="crafter",
        name="صانع",
        description="صنعت أول عنصر لك",
        emoji="🔨",
        world="general",
        xp_reward=50,
        order=5
    ),
    
    Achievement(
        id="master_crafter",
        name="صانع ماهر",
        description="صنعت 10 عناصر مختلفة",
        emoji="⚒️",
        world="general",
        xp_reward=200,
        item_reward={"id": "gold_coin", "name": "🪙 عملة ذهبية", "quantity": 50},
        order=27
    ),
    
    Achievement(
        id="wealthy",
        name="ثري",
        description="جمعت 1000 قطعة ذهبية",
        emoji="💰",
        world="general",
        xp_reward=250,
        order=33
    ),
    
    Achievement(
        id="billionaire",
        name="ملياردير",
        description="جمعت 10000 قطعة ذهبية",
        emoji="💵",
        world="general",
        xp_reward=500,
        item_reward={"id": "mystery_box", "name": "🎁 صندوق غامض", "quantity": 10},
        order=45,
        hidden=True
    )
]

# ============================================
# إنجازات نهايات العوالم
# ============================================

ENDING_ACHIEVEMENTS = [
    # فانتازيا
    Achievement(
        id="fantasy_light_ending",
        name="نور الفانتازيا",
        description="حصلت على نهاية النور في عالم الفانتازيا",
        emoji="✨",
        world="fantasy",
        xp_reward=100,
        order=11
    ),
    
    Achievement(
        id="fantasy_dark_ending",
        name="ظلام الفانتازيا",
        description="حصلت على نهاية الظلام في عالم الفانتازيا",
        emoji="🌑",
        world="fantasy",
        xp_reward=100,
        order=12
    ),
    
    Achievement(
        id="fantasy_gray_ending",
        name="توازن الفانتازيا",
        description="حصلت على نهاية التوازن في عالم الفانتازيا",
        emoji="⚖️",
        world="fantasy",
        xp_reward=100,
        order=13
    ),
    
    # ماضي
    Achievement(
        id="retro_light_ending",
        name="نور الماضي",
        description="حصلت على نهاية النور في عالم الماضي",
        emoji="✨",
        world="retro",
        xp_reward=100,
        order=14
    ),
    
    Achievement(
        id="retro_dark_ending",
        name="ظلام الماضي",
        description="حصلت على نهاية الظلام في عالم الماضي",
        emoji="🌑",
        world="retro",
        xp_reward=100,
        order=15
    ),
    
    Achievement(
        id="retro_gray_ending",
        name="توازن الماضي",
        description="حصلت على نهاية التوازن في عالم الماضي",
        emoji="⚖️",
        world="retro",
        xp_reward=100,
        order=16
    ),
    
    # مستقبل
    Achievement(
        id="future_light_ending",
        name="نور المستقبل",
        description="حصلت على نهاية النور في عالم المستقبل",
        emoji="✨",
        world="future",
        xp_reward=100,
        order=17
    ),
    
    Achievement(
        id="future_dark_ending",
        name="ظلام المستقبل",
        description="حصلت على نهاية الظلام في عالم المستقبل",
        emoji="🌑",
        world="future",
        xp_reward=100,
        order=18
    ),
    
    Achievement(
        id="future_gray_ending",
        name="توازن المستقبل",
        description="حصلت على نهاية التوازن في عالم المستقبل",
        emoji="⚖️",
        world="future",
        xp_reward=100,
        order=19
    ),
    
    # واقع بديل
    Achievement(
        id="alternate_light_ending",
        name="نور الحقيقة",
        description="حصلت على نهاية النور في الواقع البديل",
        emoji="✨",
        world="alternate",
        xp_reward=150,
        order=20
    ),
    
    Achievement(
        id="alternate_dark_ending",
        name="ظلام الحقيقة",
        description="حصلت على نهاية الظلام في الواقع البديل",
        emoji="🌑",
        world="alternate",
        xp_reward=150,
        order=21
    ),
    
    Achievement(
        id="alternate_gray_ending",
        name="توازن الحقيقة",
        description="حصلت على نهاية التوازن في الواقع البديل",
        emoji="⚖️",
        world="alternate",
        xp_reward=150,
        order=22
    ),
    
    Achievement(
        id="alternate_secret_ending",
        name="سر النيكسس",
        description="اكتشفت النهاية السرية في الواقع البديل",
        emoji="🔮",
        world="alternate",
        xp_reward=300,
        item_reward={"id": "nexus_crystal", "name": "💠 كريستال النيكسس", "quantity": 1},
        order=23,
        hidden=True
    )
]

# ============================================
# إنجازات الخيارات النادرة 🌟
# ============================================

RARE_CHOICE_ACHIEVEMENTS = [
    Achievement(
        id="rare_fantasy_oath",
        name="قسم الحارس الأول",
        description="اخترت طريق الوعد منذ أول مفترق في الفانتازيا",
        emoji="🛡️",
        world="fantasy",
        xp_reward=120,
        hidden=True,
        order=40
    ),
    Achievement(
        id="rare_retro_truth",
        name="اعتراف بلا أقنعة",
        description="واجهت حقيقة الماضي في لحظة نادرة",
        emoji="🕯️",
        world="retro",
        xp_reward=120,
        hidden=True,
        order=41
    ),
    Achievement(
        id="rare_future_pulse",
        name="نبض المدينة",
        description="سمعت نبض المستقبل واخترت الرحمة تحت الضغط",
        emoji="💓",
        world="future",
        xp_reward=120,
        hidden=True,
        order=42
    ),
    Achievement(
        id="rare_alternate_self",
        name="مرآة الذات الكاملة",
        description="اتخذت خياراً نادراً في مواجهة ذاتك البديلة",
        emoji="🪞",
        world="alternate",
        xp_reward=120,
        hidden=True,
        order=43
    )
]

# ============================================
# إنجازات سرية خاصة
# ============================================

SECRET_ACHIEVEMENTS = [
    Achievement(
        id="easter_egg_hunter",
        name="صياد البيض",
        description="وجدت 5 بيضات عيد الفصح مخبأة في القصة",
        emoji="🥚",
        world="general",
        xp_reward=300,
        item_reward={"id": "mystery_box", "name": "🎁 صندوق غامض", "quantity": 2},
        hidden=True,
        order=50
    ),
    
    Achievement(
        id="dev_speaker",
        name="متحدث مع المطور",
        description="وجدت رسالة سرية من مطوري اللعبة",
        emoji="👨‍💻",
        world="general",
        xp_reward=500,
        hidden=True,
        order=51
    ),
    
    Achievement(
        id="perfect_game",
        name="لعبة مثالية",
        description="أنهيت كل العوالم بدون أي فساد",
        emoji="🏆",
        world="general",
        xp_reward=1000,
        item_reward={"id": "truth_glass", "name": "🥃 كأس الحقيقة", "quantity": 1},
        hidden=True,
        order=52
    ),
    
    Achievement(
        id="time_paradox",
        name="مفارقة زمنية",
        description="قابلت نفسك من الماضي والمستقبل في نفس الوقت",
        emoji="⏰",
        world="alternate",
        xp_reward=400,
        hidden=True,
        order=53
    ),
    
    Achievement(
        id="nexus_legend",
        name="أسطورة النيكسس",
        description="أكملت كل العوالم وحصلت على كل النهايات وكل الإنجازات",
        emoji="🌟",
        world="general",
        xp_reward=2000,
        item_reward={"id": "nexus_crystal", "name": "💠 كريستال النيكسس", "quantity": 5},
        hidden=True,
        order=99
    )
]

# ============================================
# تجميع كل الإنجازات
# ============================================

ALL_ACHIEVEMENTS = {}

# إضافة إنجازات الفانتازيا
for ach in FANTASY_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات الماضي
for ach in RETRO_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات المستقبل
for ach in FUTURE_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات الواقع البديل
for ach in ALTERNATE_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات عامة
for ach in GENERAL_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

for ach in RARE_CHOICE_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات النهايات
for ach in ENDING_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach

# إضافة إنجازات سرية
for ach in SECRET_ACHIEVEMENTS:
    ALL_ACHIEVEMENTS[ach.id] = ach


# ============================================
# دوال مساعدة للإنجازات
# ============================================

def get_achievement(achievement_id: str) -> Optional[Achievement]:
    """الحصول على إنجاز بمعرفه"""
    return ALL_ACHIEVEMENTS.get(achievement_id)


def get_achievements_by_world(world_id: str) -> List[Achievement]:
    """الحصول على إنجازات عالم معين"""
    achievements = [ach for ach in ALL_ACHIEVEMENTS.values() if ach.world == world_id]
    return sorted(achievements, key=lambda x: x.order)


def get_hidden_achievements() -> List[Achievement]:
    """الحصول على الإنجازات السرية"""
    return [ach for ach in ALL_ACHIEVEMENTS.values() if ach.hidden]


def get_visible_achievements() -> List[Achievement]:
    """الحصول على الإنجازات غير السرية"""
    return [ach for ach in ALL_ACHIEVEMENTS.values() if not ach.hidden]


def check_ending_achievements(world_id: str, endings: List[str]) -> List[Achievement]:
    """التحقق من إنجازات النهايات"""
    unlocked = []
    
    for ending in endings:
        ach_id = f"{world_id}_{ending}_ending"
        if ach_id in ALL_ACHIEVEMENTS:
            unlocked.append(ALL_ACHIEVEMENTS[ach_id])
    
    return unlocked


def check_world_completion(world_id: str, completed_endings: List[str]) -> List[Achievement]:
    """التحقق من إكمال عالم"""
    unlocked = []
    
    # إنجاز إكمال العالم
    if len(completed_endings) >= 3:  # على الأقل 3 نهايات
        master_ach_id = {
            "fantasy": "fantasy_master",
            "retro": "past_master",
            "future": "future_master",
            "alternate": "alternate_master"
        }.get(world_id)
        
        if master_ach_id and master_ach_id in ALL_ACHIEVEMENTS:
            unlocked.append(ALL_ACHIEVEMENTS[master_ach_id])
    
    return unlocked


def calculate_achievement_progress(user_achievements: List[str]) -> Dict:
    """حساب تقدم الإنجازات"""
    total = len(ALL_ACHIEVEMENTS)
    unlocked = len(user_achievements)
    visible_total = len(get_visible_achievements())
    visible_unlocked = len([a for a in user_achievements if a in ALL_ACHIEVEMENTS and not ALL_ACHIEVEMENTS[a].hidden])
    
    return {
        "total": total,
        "unlocked": unlocked,
        "percentage": (unlocked / total * 100) if total > 0 else 0,
        "visible_total": visible_total,
        "visible_unlocked": visible_unlocked,
        "visible_percentage": (visible_unlocked / visible_total * 100) if visible_total > 0 else 0,
        "hidden_unlocked": unlocked - visible_unlocked
    }


def get_random_achievement() -> Achievement:
    """الحصول على إنجاز عشوائي"""
    return random.choice(list(ALL_ACHIEVEMENTS.values()))


def get_rarest_achievements(user_achievements: List[str], limit: int = 5) -> List[Achievement]:
    """الحصول على أندر الإنجازات (الأقل فتحاً)"""
    # هنا نحتاج إحصائيات من قاعدة البيانات
    # للتبسيط، نرجع إنجازات عشوائية
    all_ach = list(ALL_ACHIEVEMENTS.values())
    random.shuffle(all_ach)
    return all_ach[:limit]


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'Achievement',
    'ALL_ACHIEVEMENTS',
    'FANTASY_ACHIEVEMENTS',
    'RETRO_ACHIEVEMENTS',
    'FUTURE_ACHIEVEMENTS',
    'ALTERNATE_ACHIEVEMENTS',
    'GENERAL_ACHIEVEMENTS',
    'ENDING_ACHIEVEMENTS',
    'SECRET_ACHIEVEMENTS',
    'get_achievement',
    'get_achievements_by_world',
    'get_hidden_achievements',
    'get_visible_achievements',
    'check_ending_achievements',
    'check_world_completion',
    'calculate_achievement_progress',
    'get_random_achievement'
]
