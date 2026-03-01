# game/leveling.py - نظام المستويات والخبرة المتقدم

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math
import random


@dataclass
class LevelReward:
    """مكافأة عند الوصول لمستوى معين"""
    level: int
    title: Optional[str] = None  # لقب جديد
    items: List[Dict[str, Any]] = field(default_factory=list)  # عناصر
    xp_bonus: int = 0  # نقاط خبرة إضافية
    shards_bonus: int = 0  # شظايا إضافية
    unlock_world: Optional[str] = None  # عالم جديد يفتح
    unlock_feature: Optional[str] = None  # ميزة جديدة تفتح
    special: Optional[str] = None  # مكافأة خاصة


# ============================================
# إعدادات المستويات الأساسية
# ============================================

class LevelSystem:
    """
    نظام المستويات والخبرة
    يحسب المستوى بناءً على الخبرة ويدير المكافآت
    """
    
    # المعادلة: XP للمستوى n = BASE_XP * (MULTIPLIER ^ (n-1))
    BASE_XP = 100
    MULTIPLIER = 1.5
    MAX_LEVEL = 20
    
    # نقاط الخبرة من مصادر مختلفة
    XP_SOURCES = {
        "choice": 10,           # كل قرار في القصة
        "achievement": 50,      # كل إنجاز جديد
        "daily": 100,           # مكافأة يومية
        "first_daily": 150,     # أول مكافأة يومية في الأسبوع
        "streak_bonus": 20,     # مكافأة الاستمرارية لكل يوم
        "world_complete": 200,   # إكمال عالم
        "ending": 150,          # الوصول لنهاية
        "secret_ending": 300,   # نهاية سرية
        "item_use": 5,          # استخدام عنصر
        "craft": 25,            # صنع عنصر
        "explore": 8,           # استكشاف موقع جديد
        "talk": 5,              # التحدث مع شخصية
        "combat_win": 15,       # الفوز في معركة
        "combat_loss": 5        # الخسارة في معركة
    }
    
    # الألقاب حسب المستوى
    TITLES = {
        1: "مبتدئ",
        2: "مغامر",
        3: "مستكشف",
        4: "رحالة",
        5: "محارب",
        6: "بطل",
        7: "حكيم",
        8: "فيلسوف",
        9: "قائد",
        10: "أسطورة",
        11: "خالد",
        12: "ساحر",
        13: "تنين",
        14: "إله",
        15: "نيكسس"
    }
    
    # مكافآت المستويات
    LEVEL_REWARDS = {
        2: LevelReward(
            level=2,
            title="مغامر",
            items=[{"id": "potion", "quantity": 2}],
            xp_bonus=50
        ),
        3: LevelReward(
            level=3,
            title="مستكشف",
            items=[{"id": "crystal_heart", "quantity": 1}],
            shards_bonus=5
        ),
        4: LevelReward(
            level=4,
            title="رحالة",
            items=[{"id": "pure_shard", "quantity": 1}],
            xp_bonus=100
        ),
        5: LevelReward(
            level=5,
            title="محارب",
            items=[{"id": "greater_potion", "quantity": 2}],
            unlock_world="retro",
            shards_bonus=10
        ),
        6: LevelReward(
            level=6,
            title="بطل",
            items=[{"id": "magic_compass", "quantity": 1}],
            xp_bonus=150
        ),
        7: LevelReward(
            level=7,
            title="حكيم",
            items=[{"id": "memory_orb", "quantity": 1}],
            unlock_world="future",
            shards_bonus=15
        ),
        8: LevelReward(
            level=8,
            title="فيلسوف",
            items=[{"id": "ancient_scroll", "quantity": 2}],
            xp_bonus=200
        ),
        9: LevelReward(
            level=9,
            title="قائد",
            items=[{"id": "rebellion_badge", "quantity": 1}],
            shards_bonus=20
        ),
        10: LevelReward(
            level=10,
            title="أسطورة",
            items=[{"id": "truth_glass", "quantity": 1}],
            unlock_world="alternate",
            xp_bonus=300,
            shards_bonus=30
        ),
        11: LevelReward(
            level=11,
            title="خالد",
            items=[{"id": "pure_shard", "quantity": 3}],
            xp_bonus=350
        ),
        12: LevelReward(
            level=12,
            title="ساحر",
            items=[{"id": "dream_catcher", "quantity": 1}],
            shards_bonus=40
        ),
        13: LevelReward(
            level=13,
            title="تنين",
            items=[{"id": "cyber_implant", "quantity": 1}],
            xp_bonus=400
        ),
        14: LevelReward(
            level=14,
            title="إله",
            items=[{"id": "void_shard", "quantity": 2}],
            shards_bonus=50
        ),
        15: LevelReward(
            level=15,
            title="نيكسس",
            items=[{"id": "nexus_crystal", "quantity": 1}],
            xp_bonus=500,
            shards_bonus=100
        )
    }
    
    @classmethod
    def xp_for_level(cls, level: int) -> int:
        """
        حساب الخبرة المطلوبة لمستوى معين
        المستوى 1 يحتاج 0 XP
        """
        if level <= 1:
            return 0
        
        total = 0
        for i in range(1, level):
            total += int(cls.BASE_XP * (cls.MULTIPLIER ** (i - 1)))
        
        return total
    
    @classmethod
    def level_from_xp(cls, xp: int) -> int:
        """حساب المستوى بناءً على الخبرة"""
        level = 1
        while level < cls.MAX_LEVEL and xp >= cls.xp_for_level(level + 1):
            level += 1
        return level
    
    @classmethod
    def xp_for_next_level(cls, current_level: int) -> int:
        """الخبرة المطلوبة للمستوى التالي"""
        if current_level >= cls.MAX_LEVEL:
            return 0
        return cls.xp_for_level(current_level + 1)
    
    @classmethod
    def xp_progress(cls, current_xp: int) -> Tuple[int, int, float]:
        """
        حساب التقدم في المستوى الحالي
        يرجع: (xp_الحالي, xp_المطلوب, النسبة_المئوية)
        """
        current_level = cls.level_from_xp(current_xp)
        
        if current_level >= cls.MAX_LEVEL:
            return current_xp, 0, 100.0
        
        xp_for_current = cls.xp_for_level(current_level)
        xp_for_next = cls.xp_for_level(current_level + 1)
        
        xp_in_level = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        percentage = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 0
        
        return xp_in_level, xp_needed, percentage
    
    @classmethod
    def add_xp(cls, current_xp: int, source: str, multiplier: float = 1.0) -> Tuple[int, bool, Optional[int]]:
        """
        إضافة خبرة من مصدر معين
        يرجع: (xp_جديد, هل_زاد_المستوى, المستوى_الجديد)
        """
        base_xp = cls.XP_SOURCES.get(source, 10)
        xp_gain = int(base_xp * multiplier)
        
        new_xp = current_xp + xp_gain
        old_level = cls.level_from_xp(current_xp)
        new_level = cls.level_from_xp(new_xp)
        
        level_up = new_level > old_level
        
        return new_xp, level_up, new_level if level_up else None
    
    @classmethod
    def get_level_reward(cls, level: int) -> Optional[LevelReward]:
        """الحصول على مكافأة مستوى معين"""
        return cls.LEVEL_REWARDS.get(level)
    
    @classmethod
    def get_title(cls, level: int) -> str:
        """الحصول على اللقب المناسب للمستوى"""
        # البحث عن أقرب لقب
        best_title = "مبتدئ"
        for lvl, title in cls.TITLES.items():
            if level >= lvl:
                best_title = title
            else:
                break
        return best_title
    
    @classmethod
    def get_level_progress_bar(cls, current_xp: int, length: int = 10) -> str:
        """شريط تقدم المستوى"""
        xp_in_level, xp_needed, percentage = cls.xp_progress(current_xp)
        
        if xp_needed == 0:  # أقصى مستوى
            return "🟪" * length + " ✦ أقصى مستوى"
        
        filled = int(length * percentage / 100)
        empty = length - filled
        
        return "🟪" * filled + "⬜" * empty
    
    @classmethod
    def get_level_info(cls, current_xp: int) -> Dict[str, Any]:
        """الحصول على معلومات كاملة عن المستوى"""
        level = cls.level_from_xp(current_xp)
        xp_in_level, xp_needed, percentage = cls.xp_progress(current_xp)
        
        return {
            "level": level,
            "title": cls.get_title(level),
            "current_xp": current_xp,
            "xp_in_level": xp_in_level,
            "xp_needed": xp_needed,
            "percentage": percentage,
            "progress_bar": cls.get_level_progress_bar(current_xp),
            "next_level_xp": cls.xp_for_level(level + 1) if level < cls.MAX_LEVEL else None,
            "is_max": level >= cls.MAX_LEVEL
        }
    
    @classmethod
    def calculate_xp_multiplier(cls, player_data: Dict) -> float:
        """حساب مضاعف الخبرة بناءً على عوامل مختلفة"""
        multiplier = 1.0
        
        # مكافأة الاستمرارية اليومية
        streak = player_data.get("daily_streak", 0)
        if streak >= 7:
            multiplier += 0.2
        elif streak >= 30:
            multiplier += 0.5
        
        # مكافأة المستوى المنخفض (مساعدة اللاعبين الجدد)
        level = player_data.get("level", 1)
        if level < 5:
            multiplier += (5 - level) * 0.1
        
        # مكافأة إكمال العوالم
        worlds_completed = 0
        for world in ["fantasy", "retro", "future", "alternate"]:
            if player_data.get(f"{world}_ending"):
                worlds_completed += 1
        
        multiplier += worlds_completed * 0.1
        
        # عقوبة الفساد العالي
        corruption = player_data.get("corruption", 0)
        if corruption > 80:
            multiplier *= 0.8
        elif corruption > 60:
            multiplier *= 0.9
        
        return round(multiplier, 2)
    
    @classmethod
    def get_next_milestone(cls, current_xp: int) -> Dict[str, Any]:
        """المستوى التالي مع مكافأة خاصة"""
        level = cls.level_from_xp(current_xp)
        
        # البحث عن المستوى التالي الذي فيه مكافأة
        next_reward_level = None
        for lvl in sorted(cls.LEVEL_REWARDS.keys()):
            if lvl > level:
                next_reward_level = lvl
                break
        
        if next_reward_level:
            xp_needed = cls.xp_for_level(next_reward_level) - current_xp
            reward = cls.LEVEL_REWARDS[next_reward_level]
            
            return {
                "level": next_reward_level,
                "xp_needed": xp_needed,
                "reward": reward,
                "title": reward.title
            }
        
        return {"level": None, "xp_needed": 0}
    
    @classmethod
    def get_stats(cls, player_data: Dict) -> Dict[str, Any]:
        """إحصائيات كاملة عن تقدم اللاعب"""
        current_xp = player_data.get("xp", 0)
        level_info = cls.get_level_info(current_xp)
        
        # حساب الخبرة من مصادر مختلفة
        xp_breakdown = {}
        total_xp = current_xp
        remaining = total_xp
        
        for source, base_xp in sorted(cls.XP_SOURCES.items(), key=lambda x: -x[1]):
            if remaining <= 0:
                break
            # تقدير تقريبي
            xp_breakdown[source] = min(remaining, base_xp * 10)
            remaining -= xp_breakdown[source]
        
        return {
            **level_info,
            "xp_multiplier": cls.calculate_xp_multiplier(player_data),
            "next_milestone": cls.get_next_milestone(current_xp),
            "estimated_xp_breakdown": xp_breakdown,
            "total_xp_earned": current_xp
        }


# ============================================
# نظام السمعة (Reputation)
# ============================================

class ReputationSystem:
    """نظام السمعة - من -50 إلى 50"""
    
    MIN_REP = -50
    MAX_REP = 50
    NEUTRAL = 0
    
    # تأثيرات السمعة
    REPUTATION_EFFECTS = {
        # سمعة عالية (صديق)
        40: {
            "name": "محبوب",
            "discount": 0.8,  # خصم 20% عند الشراء
            "xp_multiplier": 1.2,
            "special_dialogues": True,
            "hidden_quests": True
        },
        20: {
            "name": "موثوق",
            "discount": 0.9,
            "xp_multiplier": 1.1,
            "special_dialogues": True
        },
        10: {
            "name": "معروف",
            "xp_multiplier": 1.05,
            "special_dialogues": True
        },
        
        # سمعة منخفضة (عدو)
        -20: {
            "name": "مشبوه",
            "tax": 1.1,  # ضريبة 10% إضافية
            "xp_multiplier": 0.9,
            "hostile": True
        },
        -40: {
            "name": "مكروه",
            "tax": 1.2,
            "xp_multiplier": 0.8,
            "hostile": True,
            "attack_chance": 0.3
        },
        -50: {
            "name": "عدو اللدود",
            "tax": 1.5,
            "xp_multiplier": 0.5,
            "hostile": True,
            "attack_chance": 0.8,
            "bounty": 1000
        }
    }
    
    @classmethod
    def get_level(cls, reputation: int) -> str:
        """مستوى السمعة (نص)"""
        if reputation >= 40:
            return "محبوب ⭐⭐⭐"
        elif reputation >= 20:
            return "موثوق ⭐⭐"
        elif reputation >= 10:
            return "معروف ⭐"
        elif reputation >= -10:
            return "محايد ⚪"
        elif reputation >= -30:
            return "مريب ⚠️"
        elif reputation >= -45:
            return "مكروه ❌"
        else:
            return "عدو اللدود 💢"
    
    @classmethod
    def get_effects(cls, reputation: int) -> Dict[str, Any]:
        """تأثيرات السمعة الحالية"""
        effects = {
            "name": cls.get_level(reputation),
            "discount": 1.0,
            "tax": 1.0,
            "xp_multiplier": 1.0,
            "special_dialogues": False,
            "hostile": False,
            "attack_chance": 0.0
        }
        
        # تطبيق التأثيرات حسب المستوى
        for threshold, level_effects in sorted(cls.REPUTATION_EFFECTS.items()):
            if (threshold > 0 and reputation >= threshold) or \
               (threshold < 0 and reputation <= threshold):
                effects.update(level_effects)
        
        return effects
    
    @classmethod
    def change_reputation(cls, current: int, change: int) -> int:
        """تغيير السمعة مع بقائها ضمن الحدود"""
        return max(cls.MIN_REP, min(cls.MAX_REP, current + change))
    
    @classmethod
    def get_reputation_bar(cls, reputation: int, length: int = 10) -> str:
        """شريط السمعة"""
        # تحويل من -50..50 إلى 0..100
        normalized = (reputation + 50) * 100 // 100
        
        filled = int(length * normalized / 100)
        empty = length - filled
        
        if reputation >= 0:
            return "🟩" * filled + "⬜" * empty + f" +{reputation}"
        else:
            return "⬜" * (length - filled) + "🟥" * filled + f" {reputation}"
    
    @classmethod
    def get_reaction(cls, reputation: int) -> str:
        """رد فعل الشخصيات حسب السمعة"""
        if reputation >= 40:
            return "يرحبون بك بحفاوة ويفتحون لك قلوبهم 🤗"
        elif reputation >= 20:
            return "يبتسمون لك ويثقون بك 😊"
        elif reputation >= 0:
            return "يتعاملون معك بشكل طبيعي 😐"
        elif reputation >= -30:
            return "ينظرون إليك بارتياب ويحافظون على مسافة 😒"
        elif reputation >= -45:
            return "يتجنبونك ويهمسون من وراء ظهرك 😠"
        else:
            return "يهربون منك أو يهاجمونك! 😱"


# ============================================
# دوال مساعدة
# ============================================

def calculate_level_up_rewards(old_level: int, new_level: int) -> List[LevelReward]:
    """المكافآت المستحقة عند القفز عدة مستويات"""
    rewards = []
    
    for level in range(old_level + 1, new_level + 1):
        reward = LevelSystem.get_level_reward(level)
        if reward:
            rewards.append(reward)
    
    return rewards


def get_xp_source_name(source: str) -> str:
    """اسم مصدر الخبرة بالعربية"""
    names = {
        "choice": "قرار في القصة",
        "achievement": "إنجاز جديد",
        "daily": "مكافأة يومية",
        "first_daily": "أول مكافأة في الأسبوع",
        "streak_bonus": "مكافأة الاستمرارية",
        "world_complete": "إكمال عالم",
        "ending": "الوصول لنهاية",
        "secret_ending": "نهاية سرية",
        "item_use": "استخدام عنصر",
        "craft": "صنع عنصر",
        "explore": "استكشاف موقع",
        "talk": "التحدث مع شخصية",
        "combat_win": "الفوز في معركة",
        "combat_loss": "الخسارة في معركة"
    }
    return names.get(source, source)


def get_level_color(level: int) -> int:
    """لون مناسب للمستوى"""
    if level >= 15:
        return 0xffd700  # ذهبي
    elif level >= 10:
        return 0x9b59b6  # بنفسجي
    elif level >= 7:
        return 0x3498db  # أزرق
    elif level >= 4:
        return 0x2ecc71  # أخضر
    else:
        return 0x95a5a6  # رمادي


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'LevelReward',
    'LevelSystem',
    'ReputationSystem',
    'calculate_level_up_rewards',
    'get_xp_source_name',
    'get_level_color'
]
