# game/items.py - تعريف كل العناصر في اللعبة
# جرعات، شظايا، معدات، مواد صياغة، إلخ.

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ItemRarity(Enum):
    """ندرة العنصر"""
    COMMON = "شائع"
    UNCOMMON = "نادر"
    RARE = "نادر جداً"
    EPIC = "أسطوري"
    LEGENDARY = "خرافي"


class ItemType(Enum):
    """نوع العنصر"""
    CONSUMABLE = "قابل للاستخدام"
    PERMANENT = "دائم"
    CRAFTING = "مادة صياغة"
    QUEST = "مهمة"
    KEY = "مفتاح"
    SHARD = "شظية"


@dataclass
class GameItem:
    """كلاس أساسي للعناصر"""
    
    id: str
    name: str
    description: str
    emoji: str
    type: ItemType
    rarity: ItemRarity
    value: int = 0  # قيمة البيع
    max_stack: int = 99
    usable: bool = True
    tradeable: bool = True
    craftable: bool = False
    world: str = "general"  # العالم الذي ينتمي إليه
    effects: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس للتخزين"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "type": self.type.value,
            "rarity": self.rarity.value,
            "value": self.value,
            "max_stack": self.max_stack,
            "usable": self.usable,
            "tradeable": self.tradeable,
            "craftable": self.craftable,
            "world": self.world,
            "effects": self.effects,
            "requirements": self.requirements
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GameItem':
        """إنشاء عنصر من قاموس"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            emoji=data["emoji"],
            type=ItemType(data["type"]) if "type" in data else ItemType.CONSUMABLE,
            rarity=ItemRarity(data["rarity"]) if "rarity" in data else ItemRarity.COMMON,
            value=data.get("value", 0),
            max_stack=data.get("max_stack", 99),
            usable=data.get("usable", True),
            tradeable=data.get("tradeable", True),
            craftable=data.get("craftable", False),
            world=data.get("world", "general"),
            effects=data.get("effects", {}),
            requirements=data.get("requirements", {})
        )


# ============================================
# العناصر الأساسية
# ============================================

# جرعات وعلاجات
POTION = GameItem(
    id="potion",
    name="🧪 جرعة نقاء",
    description="تقلل الفساد بمقدار 10 نقاط. جرعة أساسية لكل مغامر.",
    emoji="🧪",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.COMMON,
    value=5,
    max_stack=99,
    effects={"corruption": -10}
)

GREATER_POTION = GameItem(
    id="greater_potion",
    name="🧪✨ جرعة نقاء كبرى",
    description="تقلل الفساد بمقدار 25 نقطة. فعالة جداً في الأوقات الصعبة.",
    emoji="🧪✨",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.UNCOMMON,
    value=15,
    max_stack=50,
    effects={"corruption": -25}
)

PURE_SHARD = GameItem(
    id="pure_shard",
    name="✨ شظية نقية",
    description="شظية غير ملوثة تقلل الفساد بمقدار 15 وتوجهك نحو النور.",
    emoji="✨",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.RARE,
    value=20,
    max_stack=10,
    effects={"corruption": -15, "alignment": "Light"}
)

DARK_CORE = GameItem(
    id="dark_core",
    name="🖤 نواة الظلام",
    description="جوهر مظلم يزيد الفساد بمقدار 20 ويوجهك نحو الظلام.",
    emoji="🖤",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.RARE,
    value=20,
    max_stack=10,
    effects={"corruption": 20, "alignment": "Dark"}
)

CRYSTAL_HEART = GameItem(
    id="crystal_heart",
    name="💖 قلب الكريستال",
    description="بلورة نادرة تزيد استقرار العالم بمقدار 10.",
    emoji="💖",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.EPIC,
    value=30,
    max_stack=5,
    effects={"world_stability": 10}
)

# ============================================
# شظايا (المتغير الأساسي في اللعبة)
# ============================================

SHARD_FRAGMENT = GameItem(
    id="shard_fragment",
    name="💎 شظية صغيرة",
    description="جزء من شظية أكبر. يمكن دمج 10 منها لصنع شظية نقية.",
    emoji="💎",
    type=ItemType.CRAFTING,
    rarity=ItemRarity.COMMON,
    value=1,
    max_stack=999,
    usable=False,
    craftable=True
)

SHARD = GameItem(
    id="shard",
    name="💎 شظية",
    description="شظية طاقة نقية. تستخدم في العديد من الوصفات.",
    emoji="💎",
    type=ItemType.CRAFTING,
    rarity=ItemRarity.UNCOMMON,
    value=5,
    max_stack=999,
    usable=False,
    craftable=True
)

GREATER_SHARD = GameItem(
    id="greater_shard",
    name="💎✨ شظية كبرى",
    description="شظية قوية جداً. يمكن استخدامها لتعزيز القدرات.",
    emoji="💎✨",
    type=ItemType.CRAFTING,
    rarity=ItemRarity.RARE,
    value=25,
    max_stack=100,
    usable=True,
    effects={"shards": 5, "mystery": 5}
)

# ============================================
# عناصر عالم الفانتازيا
# ============================================

DREAM_CATCHER = GameItem(
    id="dream_catcher",
    name="🪶 صائدة الأحلام",
    description="تسمح لك برؤية أحلام الآخرين وتكشف الأسرار الخفية.",
    emoji="🪶",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.RARE,
    value=50,
    max_stack=1,
    world="fantasy",
    effects={"mystery": 5, "fantasy_power": 10}
)

FAIRY_DUST = GameItem(
    id="fairy_dust",
    name="✨ غبار الجن",
    description="غبار سحري يجعلك تطير لفترة قصيرة ويكشف الأماكن المخفية.",
    emoji="✨",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.UNCOMMON,
    value=15,
    max_stack=20,
    world="fantasy",
    effects={"fantasy_power": 10, "mystery": 5}
)

MOON_STONE = GameItem(
    id="moon_stone",
    name="🌕 حجر القمر",
    description="يضيء في الظلام ويكشف الأسرار. يزيد من قوتك في الليل.",
    emoji="🌕",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.RARE,
    value=40,
    max_stack=1,
    world="fantasy",
    effects={"mystery": 10, "corruption": -5}
)

ELVEN_BREAD = GameItem(
    id="elven_bread",
    name="🍞 خبز الجن",
    description="لقمة واحدة تكفي ليوم كامل من المغامرات. يعيد طاقتك.",
    emoji="🍞",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.COMMON,
    value=3,
    max_stack=50,
    world="fantasy",
    effects={"xp": 25}
)

MAGIC_COMPASS = GameItem(
    id="magic_compass",
    name="🧭 بوصلة سحرية",
    description="تظهر لك الاتجاه الصحيح في الخيارات الصعبة.",
    emoji="🧭",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.EPIC,
    value=100,
    max_stack=1,
    world="fantasy",
    effects={"reveal_hidden_choices": True}
)

# ============================================
# عناصر عالم الماضي
# ============================================

MEMORY_ORB = GameItem(
    id="memory_orb",
    name="🔮 كرة الذكريات",
    description="تسمح لك برؤية ذكريات منسية واستعادة لحظات من الماضي.",
    emoji="🔮",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.RARE,
    value=50,
    max_stack=1,
    world="retro",
    effects={"memories": 10, "mystery": 5}
)

TIME_SAND = GameItem(
    id="time_sand",
    name="⏳ رمال الزمن",
    description="حبيبات من الزمن نفسه. تسمح لك برؤية لحظة من الماضي.",
    emoji="⏳",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.RARE,
    value=30,
    max_stack=10,
    world="retro",
    effects={"memories": 15, "knowledge_path": 5}
)

REGRET_TEAR = GameItem(
    id="regret_tear",
    name="💧 دمعة الندم",
    description="دمعة صادقة تساعدك على تصحيح خطأ من الماضي.",
    emoji="💧",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.EPIC,
    value=50,
    max_stack=5,
    world="retro",
    effects={"corruption": -10, "memories": 5}
)

OLD_PHOTO = GameItem(
    id="old_photo",
    name="📸 صورة قديمة",
    description="صورة من الماضي. تحمل ذكريات جميلة.",
    emoji="📸",
    type=ItemType.QUEST,
    rarity=ItemRarity.UNCOMMON,
    value=10,
    max_stack=1,
    world="retro",
    usable=False
)

CHILDHOOD_TOY = GameItem(
    id="childhood_toy",
    name="🧸 لعبة الطفولة",
    description="لعبة قديمة تذكرك بأيام الطفولة البريئة.",
    emoji="🧸",
    type=ItemType.QUEST,
    rarity=ItemRarity.COMMON,
    value=5,
    max_stack=1,
    world="retro",
    usable=False
)

# ============================================
# عناصر عالم المستقبل
# ============================================

CYBER_IMPLANT = GameItem(
    id="cyber_implant",
    name="🦾 زرع إلكتروني",
    description="يعزز قدراتك التكنولوجية ويوصلك بشبكة المعلومات.",
    emoji="🦾",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.EPIC,
    value=80,
    max_stack=1,
    world="future",
    effects={"tech_level": 15, "mystery": 5}
)

NEURAL_LINK = GameItem(
    id="neural_link",
    name="🧠 رابط عصبي",
    description="يوصلك مباشرة بشبكة الآلات. يزيد من قوتك لكنه يرفع الفساد.",
    emoji="🧠",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.RARE,
    value=60,
    max_stack=1,
    world="future",
    effects={"tech_level": 20, "corruption": 10}
)

REBELLION_BADGE = GameItem(
    id="rebellion_badge",
    name="⭐ شارة التمرد",
    description="رمز المقاومة. يزيد سمعتك بين البشر ويحترمك المتمردون.",
    emoji="⭐",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.UNCOMMON,
    value=25,
    max_stack=1,
    world="future",
    effects={"reputation": 15}
)

ENERGY_CELL = GameItem(
    id="energy_cell",
    name="🔋 خلية طاقة",
    description="مصدر طاقة محمول. يشغل الأجهزة ويعزز التكنولوجيا.",
    emoji="🔋",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.COMMON,
    value=8,
    max_stack=50,
    world="future",
    effects={"tech_level": 5}
)

HOLOGRAM_DEVICE = GameItem(
    id="hologram_device",
    name="📽️ جهاز هولوغرام",
    description="يخلق نسخة ثلاثية الأبعاد منك لتخدع الأعداء.",
    emoji="📽️",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.RARE,
    value=40,
    max_stack=5,
    world="future",
    effects={"flee_chance": 50}  # فرصة الهروب من المعركة
)

# ============================================
# عناصر الواقع البديل
# ============================================

TRUTH_GLASS = GameItem(
    id="truth_glass",
    name="🥃 كأس الحقيقة",
    description="يكشف لك الخيارات المخفية ويظهر لك الحقيقة المطلقة.",
    emoji="🥃",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.LEGENDARY,
    value=200,
    max_stack=1,
    world="alternate",
    effects={"mystery": 20, "knowledge_path": 15, "see_all_outcomes": True}
)

NEXUS_CRYSTAL = GameItem(
    id="nexus_crystal",
    name="💠 كريستال النيكسس",
    description="عنصر أسطوري، يمكنه فتح أي بوابة والتنقل بين كل العوالم.",
    emoji="💠",
    type=ItemType.KEY,
    rarity=ItemRarity.LEGENDARY,
    value=500,
    max_stack=1,
    world="alternate",
    usable=False,
    tradeable=False
)

VOID_SHARD = GameItem(
    id="void_shard",
    name="⚫ شظية الفراغ",
    description="قطعة من العدم نفسه. تحمل طاقة هائلة لكنها خطيرة.",
    emoji="⚫",
    type=ItemType.SHARD,
    rarity=ItemRarity.EPIC,
    value=100,
    max_stack=5,
    world="alternate",
    effects={"corruption": 20, "mystery": 20, "identity": 10}
)

REALITY_FRAGMENT = GameItem(
    id="reality_fragment",
    name="🧩 شظية واقع",
    description="جزء من واقع بديل. تجميعها يكشف حقائق مذهلة.",
    emoji="🧩",
    type=ItemType.CRAFTING,
    rarity=ItemRarity.RARE,
    value=30,
    max_stack=99,
    world="alternate",
    usable=False,
    craftable=True
)

MIRROR_OF_SOULS = GameItem(
    id="mirror_of_souls",
    name="🪞 مرآة الأرواح",
    description="تظهر لك حقيقتك الداخلية. تزيد من فهمك لهويتك.",
    emoji="🪞",
    type=ItemType.PERMANENT,
    rarity=ItemRarity.EPIC,
    value=150,
    max_stack=1,
    world="alternate",
    effects={"identity": 20, "knowledge_path": 10}
)

# ============================================
# عناصر عامة
# ============================================

MYSTERY_BOX = GameItem(
    id="mystery_box",
    name="🎁 صندوق غامض",
    description="صندوق مجهول المحتوى. يمكن أن يحتوي على أي شيء!",
    emoji="🎁",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.EPIC,
    value=50,
    max_stack=10,
    world="general",
    effects={"random_reward": True}
)

GOLD_COIN = GameItem(
    id="gold_coin",
    name="🪙 عملة ذهبية",
    description="عملة قديمة تستخدم في التجارة بين العوالم.",
    emoji="🪙",
    type=ItemType.CRAFTING,
    rarity=ItemRarity.COMMON,
    value=1,
    max_stack=999,
    world="general",
    usable=False
)

KEY_TO_NOWHERE = GameItem(
    id="key_to_nowhere",
    name="🗝️ مفتاح اللامكان",
    description="مفتاح غامض. لا أحد يعلم أي باب يفتح.",
    emoji="🗝️",
    type=ItemType.KEY,
    rarity=ItemRarity.EPIC,
    value=100,
    max_stack=1,
    world="general",
    usable=False
)

ANCIENT_SCROLL = GameItem(
    id="ancient_scroll",
    name="📜 لفافة قديمة",
    description="تحتوي على معرفة منسية عن الشظايا.",
    emoji="📜",
    type=ItemType.CONSUMABLE,
    rarity=ItemRarity.RARE,
    value=40,
    max_stack=5,
    world="general",
    effects={"knowledge_path": 10, "mystery": 5}
)

# ============================================
# قاموس بكل العناصر
# ============================================

ALL_ITEMS = {
    # أساسيات
    "potion": POTION,
    "greater_potion": GREATER_POTION,
    "pure_shard": PURE_SHARD,
    "dark_core": DARK_CORE,
    "crystal_heart": CRYSTAL_HEART,
    
    # شظايا
    "shard_fragment": SHARD_FRAGMENT,
    "shard": SHARD,
    "greater_shard": GREATER_SHARD,
    
    # فانتازيا
    "dream_catcher": DREAM_CATCHER,
    "fairy_dust": FAIRY_DUST,
    "moon_stone": MOON_STONE,
    "elven_bread": ELVEN_BREAD,
    "magic_compass": MAGIC_COMPASS,
    
    # ماضي
    "memory_orb": MEMORY_ORB,
    "time_sand": TIME_SAND,
    "regret_tear": REGRET_TEAR,
    "old_photo": OLD_PHOTO,
    "childhood_toy": CHILDHOOD_TOY,
    
    # مستقبل
    "cyber_implant": CYBER_IMPLANT,
    "neural_link": NEURAL_LINK,
    "rebellion_badge": REBELLION_BADGE,
    "energy_cell": ENERGY_CELL,
    "hologram_device": HOLOGRAM_DEVICE,
    
    # واقع بديل
    "truth_glass": TRUTH_GLASS,
    "nexus_crystal": NEXUS_CRYSTAL,
    "void_shard": VOID_SHARD,
    "reality_fragment": REALITY_FRAGMENT,
    "mirror_of_souls": MIRROR_OF_SOULS,
    
    # عام
    "mystery_box": MYSTERY_BOX,
    "gold_coin": GOLD_COIN,
    "key_to_nowhere": KEY_TO_NOWHERE,
    "ancient_scroll": ANCIENT_SCROLL
}


# ============================================
# دوال مساعدة للعناصر
# ============================================

def get_item(item_id: str) -> Optional[GameItem]:
    """الحصول على عنصر بمعرفه"""
    return ALL_ITEMS.get(item_id)


def get_items_by_world(world_id: str) -> List[GameItem]:
    """الحصول على عناصر عالم معين"""
    return [item for item in ALL_ITEMS.values() if item.world == world_id]


def get_items_by_type(item_type: ItemType) -> List[GameItem]:
    """الحصول على عناصر من نوع معين"""
    return [item for item in ALL_ITEMS.values() if item.type == item_type]


def get_items_by_rarity(rarity: ItemRarity) -> List[GameItem]:
    """الحصول على عناصر بندرة معينة"""
    return [item for item in ALL_ITEMS.values() if item.rarity == rarity]


def get_random_item(world_id: Optional[str] = None, rarity: Optional[ItemRarity] = None) -> Optional[GameItem]:
    """الحصول على عنصر عشوائي"""
    import random
    
    items = list(ALL_ITEMS.values())
    
    if world_id:
        items = [i for i in items if i.world == world_id]
    
    if rarity:
        items = [i for i in items if i.rarity == rarity]
    
    return random.choice(items) if items else None


def calculate_item_value(item: GameItem, quantity: int = 1) -> int:
    """حساب قيمة عنصر أو مجموعة عناصر"""
    return item.value * quantity


def can_use_item(item: GameItem, player_data: Dict) -> bool:
    """التحقق مما إذا كان اللاعب يمكنه استخدام العنصر"""
    if not item.usable:
        return False
    
    # التحقق من المتطلبات
    for req, value in item.requirements.items():
        if req == "level":
            if player_data.get("level", 1) < value:
                return False
        elif req == "world":
            if player_data.get("current_world") != value:
                return False
        elif req == "alignment":
            if player_data.get("alignment") != value:
                return False
    
    return True


def apply_item_effects(item: GameItem, player_data: Dict) -> Dict:
    """تطبيق تأثيرات العنصر على اللاعب"""
    updates = {}
    
    for effect, value in item.effects.items():
        if effect == "corruption":
            current = player_data.get("corruption", 0)
            updates["corruption"] = max(0, min(100, current + value))
        
        elif effect == "mystery":
            current = player_data.get("mystery", 0)
            updates["mystery"] = max(0, min(100, current + value))
        
        elif effect == "reputation":
            current = player_data.get("reputation", 0)
            updates["reputation"] = max(-50, min(50, current + value))
        
        elif effect == "world_stability":
            current = player_data.get("world_stability", 100)
            updates["world_stability"] = max(0, min(100, current + value))
        
        elif effect == "shards":
            current = player_data.get("shards", 0)
            updates["shards"] = max(0, current + value)
        
        elif effect == "xp":
            current = player_data.get("xp", 0)
            updates["xp"] = current + value
        
        elif effect == "alignment":
            updates["alignment"] = value
        
        elif effect in ["fantasy_power", "memories", "tech_level", "identity", "knowledge_path"]:
            current = player_data.get(effect, 0)
            updates[effect] = max(0, min(100, current + value))
    
    return updates


# ============================================
# وصفات الصياغة (Crafting Recipes)
# ============================================

CRAFTING_RECIPES = {
    "pure_shard": {
        "name": "شظية نقية",
        "result": "pure_shard",
        "quantity": 1,
        "ingredients": {
            "shard_fragment": 10,
            "crystal_heart": 1
        },
        "description": "دمج 10 شظايا صغيرة مع قلب كريستال",
        "world": "fantasy",
        "level_required": 3
    },
    
    "greater_shard": {
        "name": "شظية كبرى",
        "result": "greater_shard",
        "quantity": 1,
        "ingredients": {
            "shard": 5,
            "pure_shard": 2
        },
        "description": "دمج 5 شظايا عادية مع 2 شظية نقية",
        "world": "general",
        "level_required": 5
    },
    
    "nexus_crystal": {
        "name": "كريستال النيكسس",
        "result": "nexus_crystal",
        "quantity": 1,
        "ingredients": {
            "pure_shard": 5,
            "dark_core": 5,
            "void_shard": 3,
            "reality_fragment": 10
        },
        "description": "عنصر أسطوري - دمج قوى النور والظلام والفراغ",
        "world": "alternate",
        "level_required": 10,
        "secret": True
    },
    
    "truth_glass": {
        "name": "كأس الحقيقة",
        "result": "truth_glass",
        "quantity": 1,
        "ingredients": {
            "crystal_heart": 3,
            "memory_orb": 1,
            "ancient_scroll": 2,
            "void_shard": 1
        },
        "description": "يكشف الحقيقة المطلقة",
        "world": "alternate",
        "level_required": 8
    },
    
    "magic_compass": {
        "name": "بوصلة سحرية",
        "result": "magic_compass",
        "quantity": 1,
        "ingredients": {
            "shard": 10,
            "moon_stone": 1,
            "gold_coin": 20
        },
        "description": "تظهر لك الاتجاه الصحيح",
        "world": "fantasy",
        "level_required": 4
    },
    
    "cyber_implant": {
        "name": "زرع إلكتروني",
        "result": "cyber_implant",
        "quantity": 1,
        "ingredients": {
            "energy_cell": 5,
            "shard": 15,
            "gold_coin": 30
        },
        "description": "يعزز قدراتك التكنولوجية",
        "world": "future",
        "level_required": 5
    },
    
    "memory_orb": {
        "name": "كرة الذكريات",
        "result": "memory_orb",
        "quantity": 1,
        "ingredients": {
            "old_photo": 3,
            "childhood_toy": 1,
            "time_sand": 2,
            "shard": 10
        },
        "description": "تسترجع ذكريات منسية",
        "world": "retro",
        "level_required": 4
    },
    
    "greater_potion": {
        "name": "جرعة نقاء كبرى",
        "result": "greater_potion",
        "quantity": 1,
        "ingredients": {
            "potion": 3,
            "crystal_heart": 1
        },
        "description": "جرعة أقوى من العادية",
        "world": "general",
        "level_required": 2
    }
}


def can_craft(recipe_id: str, inventory: Dict[str, int], player_level: int) -> bool:
    """التحقق مما إذا كان اللاعب يمكنه صنع عنصر"""
    recipe = CRAFTING_RECIPES.get(recipe_id)
    if not recipe:
        return False
    
    # التحقق من المستوى
    if player_level < recipe.get("level_required", 1):
        return False
    
    # التحقق من المواد
    for ingredient, required_qty in recipe["ingredients"].items():
        if inventory.get(ingredient, 0) < required_qty:
            return False
    
    return True


def craft_item(recipe_id: str, inventory: Dict[str, int]) -> Optional[str]:
    """صنع عنصر واستهلاك المواد"""
    recipe = CRAFTING_RECIPES.get(recipe_id)
    if not recipe:
        return None
    
    # استهلاك المواد
    for ingredient, required_qty in recipe["ingredients"].items():
        inventory[ingredient] -= required_qty
        if inventory[ingredient] <= 0:
            del inventory[ingredient]
    
    return recipe["result"]


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'ItemRarity',
    'ItemType',
    'GameItem',
    'ALL_ITEMS',
    'CRAFTING_RECIPES',
    'get_item',
    'get_items_by_world',
    'get_items_by_type',
    'get_items_by_rarity',
    'get_random_item',
    'calculate_item_value',
    'can_use_item',
    'apply_item_effects',
    'can_craft',
    'craft_item'
]
