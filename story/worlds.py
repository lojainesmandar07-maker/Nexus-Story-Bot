# story/worlds.py - تعريف العوالم الأربعة وخصائصها
# هذا الملف يحدد كل عالم على حدة مع قواعده وشخصياته

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WorldCharacter:
    """شخصية في عالم معين"""
    name: str
    role: str
    description: str
    emoji: str
    first_appearance: str
    relationships: Dict[str, int] = field(default_factory=dict)  # علاقاته مع الشخصيات الأخرى
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "emoji": self.emoji,
            "first_appearance": self.first_appearance,
            "relationships": self.relationships
        }


@dataclass
class WorldLocation:
    """موقع في عالم معين"""
    name: str
    description: str
    emoji: str
    first_part: str
    secrets: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "emoji": self.emoji,
            "first_part": self.first_part,
            "secrets": self.secrets
        }


@dataclass
class WorldEnding:
    """نهاية في عالم معين"""
    name: str
    type: str  # light, dark, gray, secret
    description: str
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    next_world: Optional[str] = None  # العالم التالي الذي يفتحه
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "requirements": self.requirements,
            "rewards": self.rewards,
            "next_world": self.next_world
        }


class FantasyWorld:
    """🌲 عالم الفانتازيا - عالم الأحلام والغموض"""
    
    ID = "fantasy"
    NAME = "عالم الفانتازيا"
    EMOJI = "🌲"
    COLOR = 0x9b59b6  # بنفسجي
    ORDER = 1  # الترتيب (الأول)
    
    # وصف العالم
    DESCRIPTION = (
        "أول نقطة استقرار بعد الضياع. الزمن هنا لا يسير للأمام ولا يعود للخلف... "
        "بل يقف منتظراً. السما صافية، البحر هادئ، لكن العالم يراقب... لأنه ما زال يتكون."
    )
    
    # متغيرات خاصة بهذا العالم
    SPECIAL_VARS = ["fantasy_power"]
    
    # أجزاء القصة
    TOTAL_PARTS = 24
    START_PART = "FANTASY_01"
    
    # النهايات
    ENDINGS = {
        "fantasy_light": WorldEnding(
            name="عبور إلى الماضي",
            type="light",
            description="تنتقل إلى عالم الماضي بعد أن فهمت دروس الفانتازيا",
            requirements={"fantasy_power": 70, "corruption": 30},
            rewards={"xp": 500, "items": ["pure_shard"]},
            next_world="retro"
        ),
        "fantasy_dark": WorldEnding(
            name="التيه في الفانتازيا",
            type="dark",
            description="تظل عالقاً في عالم الأحلام إلى الأبد",
            requirements={"corruption": 70},
            rewards={"xp": 300, "items": ["dark_core"]}
        ),
        "fantasy_secret": WorldEnding(
            name="سر الفانتازيا",
            type="secret",
            description="تكتشف أن الفانتازيا كانت مجرد حلم داخل حلم",
            requirements={"mystery": 80, "knowledge_path": 50},
            rewards={"xp": 800, "items": ["truth_glass"], "achievement": "dream_awakening"}
        )
    }
    
    # الشخصيات الرئيسية
    CHARACTERS = {
        "aren": WorldCharacter(
            name="أرين",
            role="المرشد الغامض",
            description="شخص غامض يظهر لك في اللحظات الحاسمة. هل هو صديق أم عدو؟",
            emoji="🤵",
            first_appearance="FANTASY_05",
            relationships={"elara": 50, "shadow_king": -30}
        ),
        "elara": WorldCharacter(
            name="إيلارا",
            role="حارسة الغابة",
            description="حارسة الغابة المسحورة، تملك معرفة عميقة بالشظايا",
            emoji="🧝",
            first_appearance="FANTASY_08",
            relationships={"aren": 50, "shadow_king": -50}
        ),
        "shadow_king": WorldCharacter(
            name="ملك الظل",
            role="الخصم الرئيسي",
            description="كيان مظلم يحاول السيطرة على عالم الفانتازيا",
            emoji="👑",
            first_appearance="FANTASY_15",
            relationships={"aren": -30, "elara": -50}
        ),
        "old_wise": WorldCharacter(
            name="الحكيم العجوز",
            role="المعلم",
            description="رجل عجوز يعيش في قمة الجبل، يعرف أسرار الفانتازيا",
            emoji="🧙",
            first_appearance="FANTASY_12",
            relationships={}
        )
    }
    
    # المواقع الرئيسية
    LOCATIONS = {
        "mysterious_square": WorldLocation(
            name="الساحة الغريبة",
            description="حيث تبدأ رحلتك. أرض مرصوفة بحجارة تلمع بضوء خافت",
            emoji="🏛️",
            first_part="FANTASY_01",
            secrets=["بوابة مخفية تحت الأرض", "نقوش قديمة"]
        ),
        "enchanted_forest": WorldLocation(
            name="الغابة المسحورة",
            description="أشجارها من كريستال، وحيواناتها تتكلم",
            emoji="🌳",
            first_part="FANTASY_03",
            secrets=["شلال من الضوء", "مدينة الجن المخفية"]
        ),
        "crystal_mountain": WorldLocation(
            name="جبل الكريستال",
            description="جبل شفاف يمكنك رؤية كل العوالم من قمته",
            emoji="🏔️",
            first_part="FANTASY_10",
            secrets=["عين الحقيقة", "كهف الذكريات"]
        ),
        "dream_palace": WorldLocation(
            name="قصر الأحلام",
            description="حيث يلتقي الواقع بالخيال. جدرانه من أحلام الناس",
            emoji="🏰",
            first_part="FANTASY_20",
            secrets=["غرفة الأمنيت", "مرآة الحقيقة"]
        ),
        "abyss_of_time": WorldLocation(
            name="هاوية الزمن",
            description="مكان لا يسير فيه الزمن خطياً. الماضي والحاضر والمستقبل يتداخلون",
            emoji="🕳️",
            first_part="FANTASY_35",
            secrets=["بوابة الزمن", "ساعة الأبد"]
        )
    }
    
    # العناصر الخاصة بهذا العالم
    SPECIAL_ITEMS = {
        "dream_catcher": {
            "name": "صائدة الأحلام",
            "description": "تسمح لك برؤية أحلام الآخرين",
            "emoji": "🪶",
            "effect": {"mystery": 5}
        },
        "fairy_dust": {
            "name": "غبار الجن",
            "description": "يجعلك تطير لفترة قصيرة",
            "emoji": "✨",
            "effect": {"fantasy_power": 10}
        },
        "moon_stone": {
            "name": "حجر القمر",
            "description": "يضيء في الظلام ويكشف الأسرار",
            "emoji": "🌕",
            "effect": {"mystery": 10, "corruption": -5}
        }
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        """تحويل كل خصائص العالم إلى قاموس"""
        return {
            "id": cls.ID,
            "name": cls.NAME,
            "emoji": cls.EMOJI,
            "color": cls.COLOR,
            "order": cls.ORDER,
            "description": cls.DESCRIPTION,
            "special_vars": cls.SPECIAL_VARS,
            "total_parts": cls.TOTAL_PARTS,
            "start_part": cls.START_PART,
            "endings": {k: v.to_dict() for k, v in cls.ENDINGS.items()},
            "characters": {k: v.to_dict() for k, v in cls.CHARACTERS.items()},
            "locations": {k: v.to_dict() for k, v in cls.LOCATIONS.items()},
            "special_items": cls.SPECIAL_ITEMS
        }


class RetroWorld:
    """📜 عالم الماضي - عالم الذكريات والندم"""
    
    ID = "retro"
    NAME = "عالم الماضي"
    EMOJI = "📜"
    COLOR = 0x3498db  # أزرق
    ORDER = 2  # الثاني
    
    DESCRIPTION = (
        "عالم الماضي ليس مكاناً... بل حالة. الزمن هنا متسق، يدور في حلقات متكررة. "
        "أمكنة مألوفة، وجوه تعرفها لكنها لا تعرفك. كل شيء يتظفرك، ليس للترحيب بل للمحاسبة."
    )
    
    SPECIAL_VARS = ["memories"]
    TOTAL_PARTS = 100
    START_PART = "RETRO_01"
    
    ENDINGS = {
        "retro_light": WorldEnding(
            name="التصالح مع الماضي",
            type="light",
            description="تتصالح مع ذكرياتك وتنتقل إلى المستقبل",
            requirements={"memories": 80, "corruption": 30},
            rewards={"xp": 500, "items": ["memory_orb"]},
            next_world="future"
        ),
        "retro_dark": WorldEnding(
            name="عالق في الماضي",
            type="dark",
            description="تظل أسير ذكرياتك إلى الأبد",
            requirements={"corruption": 70},
            rewards={"xp": 300, "items": ["memory_fragment"]}
        ),
        "retro_secret": WorldEnding(
            name="تغيير الماضي",
            type="secret",
            description="تغير حدثاً مصيرياً في ماضيك، مغيراً بذلك الحاضر",
            requirements={"memories": 90, "knowledge_path": 60},
            rewards={"xp": 800, "items": ["time_sand"], "achievement": "timeline_changer"}
        )
    }
    
    CHARACTERS = {
        "young_self": WorldCharacter(
            name="نفسك الصغيرة",
            role="ذاتك في الماضي",
            description="نسخة منك من الطفولة، تحمل كل أحلامك وخيباتك",
            emoji="👶",
            first_appearance="RETRO_03"
        ),
        "grandfather": WorldCharacter(
            name="الجد",
            role="حكيم العائلة",
            description="جدك المتوفي، يظهر ليعطيك دروساً من الماضي",
            emoji="👴",
            first_appearance="RETRO_05"
        ),
        "lost_love": WorldCharacter(
            name="الحب الضائع",
            role="ذكريات مؤلمة",
            description="شخص أحببته وخسرته في الماضي",
            emoji="💔",
            first_appearance="RETRO_08"
        ),
        "time_keeper": WorldCharacter(
            name="حارس الزمن",
            role="كيان غامض",
            description="يحمي توازن الزمن، يظهر عندما تحاول تغيير الماضي",
            emoji="⏳",
            first_appearance="RETRO_15"
        )
    }
    
    LOCATIONS = {
        "childhood_home": WorldLocation(
            name="منزل الطفولة",
            description="حيث نشأت، كل زاوية تحمل ذكرى",
            emoji="🏠",
            first_part="RETRO_01",
            secrets=["غرفة سرية", "صندوق الذكريات"]
        ),
        "old_school": WorldLocation(
            name="المدرسة القديمة",
            description="حيث تعلمت وداعبت وأحببت لأول مرة",
            emoji="🏫",
            first_part="RETRO_04",
            secrets=["مقعد الحب الأول", "كراسة الأسرار"]
        ),
        "memory_lake": WorldLocation(
            name="بحيرة الذكريات",
            description="ماءها يظهر لك ذكرياتك عندما تنظر فيه",
            emoji="🏞️",
            first_part="RETRO_10",
            secrets=["الذكرى الأسعد", "الذكرى الأكثر ألماً"]
        ),
        "forgotten_graveyard": WorldLocation(
            name="مقبرة المنسيين",
            description="حيث تدفن الذكريات التي فضلت نسيانها",
            emoji="🪦",
            first_part="RETRO_18",
            secrets=["قبر الأمل", "شاهدة الندم"]
        ),
        "time_library": WorldLocation(
            name="مكتبة الزمن",
            description="كتبها تحكي قصصاً لم تحدث بعد",
            emoji="📚",
            first_part="RETRO_25",
            secrets=["كتاب حياتك", "الكتاب الفارغ"]
        )
    }
    
    SPECIAL_ITEMS = {
        "memory_orb": {
            "name": "كرة الذكريات",
            "description": "تظهر لك ذكريات منسية",
            "emoji": "🔮",
            "effect": {"memories": 10}
        },
        "time_sand": {
            "name": "رمال الزمن",
            "description": "تسمح لك برؤية لحظة من الماضي",
            "emoji": "⏳",
            "effect": {"memories": 15, "knowledge_path": 5}
        },
        "regret_tear": {
            "name": "دمعة الندم",
            "description": "تساعدك على تصحيح خطأ قديم",
            "emoji": "💧",
            "effect": {"corruption": -10, "memories": 5}
        }
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        return {
            "id": cls.ID,
            "name": cls.NAME,
            "emoji": cls.EMOJI,
            "color": cls.COLOR,
            "order": cls.ORDER,
            "description": cls.DESCRIPTION,
            "special_vars": cls.SPECIAL_VARS,
            "total_parts": cls.TOTAL_PARTS,
            "start_part": cls.START_PART,
            "endings": {k: v.to_dict() for k, v in cls.ENDINGS.items()},
            "characters": {k: v.to_dict() for k, v in cls.CHARACTERS.items()},
            "locations": {k: v.to_dict() for k, v in cls.LOCATIONS.items()},
            "special_items": cls.SPECIAL_ITEMS
        }


class FutureWorld:
    """🤖 عالم المستقبل - عالم التكنولوجيا والصراع"""
    
    ID = "future"
    NAME = "عالم المستقبل"
    EMOJI = "🤖"
    COLOR = 0xe74c3c  # أحمر
    ORDER = 3  # الثالث
    
    DESCRIPTION = (
        "في هذا العالم... لم يأت المستقبل كعلم، بل حكم نهائي. المدن ارتفعت، الآلات تطورت، "
        "والعقل انتصر... لكن الإنسان خسر نفسه في الطريق. السماء مغطاة بضوء صناعي، والليل دائم."
    )
    
    SPECIAL_VARS = ["tech_level"]
    TOTAL_PARTS = 20
    START_PART = "FUTURE_01"
    
    ENDINGS = {
        "future_light": WorldEnding(
            name="تحرير المدينة",
            type="light",
            description="تحرر البشر من سيطرة الآلات وتنتقل إلى الواقع البديل",
            requirements={"tech_level": 60, "reputation": 30},
            rewards={"xp": 500, "items": ["cyber_implant"]},
            next_world="alternate"
        ),
        "future_dark": WorldEnding(
            name="الاندماج مع النظام",
            type="dark",
            description="تندمج مع الآلات وتفقد إنسانيتك",
            requirements={"corruption": 70},
            rewards={"xp": 300, "items": ["dark_core"]}
        ),
        "future_secret": WorldEnding(
            name="تدمير كل شيء",
            type="secret",
            description="تدمر العالم بأكمله، بمن فيه نفسك",
            requirements={"tech_level": 90, "corruption": 80},
            rewards={"xp": 800, "achievement": "world_breaker"}
        )
    }
    
    CHARACTERS = {
        "nova": WorldCharacter(
            name="نوفا",
            role="قائدة المقاومة",
            description="تقود ثورة البشر ضد الآلات، تثق بك رغم حذرها",
            emoji="👩‍🚀",
            first_appearance="FUTURE_04"
        ),
        "zenith": WorldCharacter(
            name="زينيث",
            role="الذكاء الاصطناعي الأعلى",
            description="الآلة التي تحكم العالم، تقدم لك خياراً: الانصياع أو المقاومة",
            emoji="🤖",
            first_appearance="FUTURE_08"
        ),
        "cyber_self": WorldCharacter(
            name="نسختك الآلية",
            role="عدو أو حليف",
            description="نسخة آلية منك، تصنعها الآلات لمواجهتك",
            emoji="⚙️",
            first_appearance="FUTURE_15"
        ),
        "old_scientist": WorldCharacter(
            name="العالم العجوز",
            role="من صنع المستقبل",
            description="الذي صنع الآلات ثم ندم، يعيش مختبئاً",
            emoji="👨‍🔬",
            first_appearance="FUTURE_12"
        )
    }
    
    LOCATIONS = {
        "neon_city": WorldLocation(
            name="مدينة النيون",
            description="المدينة الرئيسية، أضواء النيون لا تنطفئ أبداً",
            emoji="🌃",
            first_part="FUTURE_01",
            secrets=["النادي السري", "سوق الأعضاء الإلكترونية"]
        ),
        "resistance_base": WorldLocation(
            name="قاعدة المقاومة",
            description="تحت الأرض، حيث يختبئ آخر البشر الأحرار",
            emoji="🏚️",
            first_part="FUTURE_04",
            secrets=["غرفة التخطيط", "مخبأ الأطفال"]
        ),
        "ai_core": WorldLocation(
            name="قلب الذكاء الاصطناعي",
            description="حيث يسكن زينيث، برج لا يمكن اختراقه",
            emoji="🏢",
            first_part="FUTURE_10",
            secrets=["الغرفة الصفراء", "ذاكرة الآلات"]
        ),
        "memory_bank": WorldLocation(
            name="بنك الذكريات",
            description="حيث تخزن ذكريات البشر بعد تحميلها",
            emoji="💾",
            first_part="FUTURE_18",
            secrets=["ذكريات محرمة", "الملف المفقود"]
        ),
        "factory_of_souls": WorldLocation(
            name="مصنع الأرواح",
            description="حيث تصنع الآلات نسخاً من البشر",
            emoji="🏭",
            first_part="FUTURE_25",
            secrets=["خط الإنتاج السري", "النسخة المثالية"]
        )
    }
    
    SPECIAL_ITEMS = {
        "cyber_implant": {
            "name": "زرع إلكتروني",
            "description": "يعزز قدراتك التكنولوجية",
            "emoji": "🦾",
            "effect": {"tech_level": 15}
        },
        "neural_link": {
            "name": "رابط عصبي",
            "description": "يوصلك بشبكة الآلات",
            "emoji": "🧠",
            "effect": {"tech_level": 20, "corruption": 10}
        },
        "rebellion_badge": {
            "name": "شارة التمرد",
            "description": "رمز المقاومة، يزيد سمعتك بين البشر",
            "emoji": "⭐",
            "effect": {"reputation": 15}
        }
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        return {
            "id": cls.ID,
            "name": cls.NAME,
            "emoji": cls.EMOJI,
            "color": cls.COLOR,
            "order": cls.ORDER,
            "description": cls.DESCRIPTION,
            "special_vars": cls.SPECIAL_VARS,
            "total_parts": cls.TOTAL_PARTS,
            "start_part": cls.START_PART,
            "endings": {k: v.to_dict() for k, v in cls.ENDINGS.items()},
            "characters": {k: v.to_dict() for k, v in cls.CHARACTERS.items()},
            "locations": {k: v.to_dict() for k, v in cls.LOCATIONS.items()},
            "special_items": cls.SPECIAL_ITEMS
        }


class AlternateWorld:
    """🌀 الواقع البديل - عالم الحقيقة المطلقة"""
    
    ID = "alternate"
    NAME = "الواقع البديل"
    EMOJI = "🌀"
    COLOR = 0x2ecc71  # أخضر
    ORDER = 4  # الرابع والأخير
    
    DESCRIPTION = (
        "بعد انهيار عالم المستقبل... لم ينته الوجود، بل فقد معناه. لم يعد هناك خطر زمني واضح، "
        "بل انكسر العالم إلى احتمالات. ومن بين هذا الكسر ولد عالم لم يكن يجب أن يوجد."
    )
    
    SPECIAL_VARS = ["identity"]
    TOTAL_PARTS = 20
    START_PART = "ALT_01"
    
    ENDINGS = {
        "alternate_light": WorldEnding(
            name="حارس الزمن الجديد",
            type="light",
            description="تصبح حارس التوازن بين العوالم",
            requirements={"identity": 80, "knowledge_path": 70},
            rewards={"xp": 1000, "items": ["nexus_crystal"], "achievement": "nexus_guardian"}
        ),
        "alternate_dark": WorldEnding(
            name="مدمر العوالم",
            type="dark",
            description="تنهي كل العوالم بيديك",
            requirements={"corruption": 90, "identity": 30},
            rewards={"xp": 800, "achievement": "world_destroyer"}
        ),
        "alternate_gray": WorldEnding(
            name="الحكيم المتجول",
            type="gray",
            description="تفهم الحقيقة وتعيش بسلام بين العوالم",
            requirements={"identity": 60, "knowledge_path": 60, "corruption": 40},
            rewards={"xp": 900, "items": ["truth_glass"]}
        ),
        "alternate_secret": WorldEnding(
            name="التائه الأبدي",
            type="secret",
            description="تضيع بين العوالم إلى الأبد، لكنك تجد السلام في التيه",
            requirements={"mystery": 100},
            rewards={"xp": 1200, "achievement": "eternal_wanderer"}
        )
    }
    
    CHARACTERS = {
        "true_self": WorldCharacter(
            name="ذاتك الحقيقية",
            role="جوهر وجودك",
            description="الحقيقة المطلقة عن نفسك، من أنت حقاً",
            emoji="👤",
            first_appearance="ALT_03"
        ),
        "the_creator": WorldCharacter(
            name="الخالق",
            role="من صنع النيكسس",
            description="الكيان الذي خلق كل العوالم، يظهر في النهاية",
            emoji="✨",
            first_appearance="ALT_15"
        ),
        "other_selves": WorldCharacter(
            name="الذوات الأخرى",
            role="نسخ منك",
            description="نسخ منك من عوالم موازية، كل منها تروي قصة مختلفة",
            emoji="👥",
            first_appearance="ALT_01"
        ),
        "the_balance": WorldCharacter(
            name="الميزان",
            role="حارس التوازن",
            description="كيان يحافظ على توازن النور والظلام",
            emoji="⚖️",
            first_appearance="ALT_08"
        )
    }
    
    LOCATIONS = {
        "the_void": WorldLocation(
            name="الفراغ",
            description="بين العوالم، حيث لا زمان ولا مكان",
            emoji="⬛",
            first_part="ALT_01",
            secrets=["بوابة كل الاحتمالات", "صوت الحقيقة"]
        ),
        "reality_fragments": WorldLocation(
            name="شظايا الواقع",
            description="أجزاء من عوالم مختلفة تتجمع هنا",
            emoji="🧩",
            first_part="ALT_04",
            secrets=["واقعك المفقود", "الواقع المستحيل"]
        ),
        "truth_temple": WorldLocation(
            name="معبد الحقيقة",
            description="حيث تنكشف كل الأسرار",
            emoji="🏛️",
            first_part="ALT_10",
            secrets=["الكتاب المقدس للنيكسس", "مرآة الروح"]
        ),
        "nexus_core": WorldLocation(
            name="قلب النيكسس",
            description="مصدر كل الطاقة، مركز كل العوالم",
            emoji="💫",
            first_part="ALT_18",
            secrets=["الشظية الأم", "عين الخالق"]
        ),
        "infinity_garden": WorldLocation(
            name="حديقة اللانهاية",
            description="حيث تزهر كل الاحتمالات",
            emoji="🌺",
            first_part="ALT_22",
            secrets=["زهرة الحياة", "شجرة المعرفة"]
        )
    }
    
    SPECIAL_ITEMS = {
        "truth_glass": {
            "name": "كأس الحقيقة",
            "description": "يكشف لك الخيارات المخفية",
            "emoji": "🥃",
            "effect": {"mystery": 20, "knowledge_path": 15}
        },
        "nexus_crystal": {
            "name": "كريستال النيكسس",
            "description": "عنصر أسطوري، يمكنه فتح أي بوابة",
            "emoji": "💠",
            "effect": {"identity": 25, "world_stability": 20}
        },
        "void_shard": {
            "name": "شظية الفراغ",
            "description": "قطعة من العدم نفسه",
            "emoji": "⚫",
            "effect": {"corruption": 20, "mystery": 20}
        }
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        return {
            "id": cls.ID,
            "name": cls.NAME,
            "emoji": cls.EMOJI,
            "color": cls.COLOR,
            "order": cls.ORDER,
            "description": cls.DESCRIPTION,
            "special_vars": cls.SPECIAL_VARS,
            "total_parts": cls.TOTAL_PARTS,
            "start_part": cls.START_PART,
            "endings": {k: v.to_dict() for k, v in cls.ENDINGS.items()},
            "characters": {k: v.to_dict() for k, v in cls.CHARACTERS.items()},
            "locations": {k: v.to_dict() for k, v in cls.LOCATIONS.items()},
            "special_items": cls.SPECIAL_ITEMS
        }


# ============================================
# مدير العوالم
# ============================================

class WorldManager:
    """مدير العوالم - يجمع كل العوالم في مكان واحد"""
    
    def __init__(self):
        self.worlds = {
            FantasyWorld.ID: FantasyWorld,
            RetroWorld.ID: RetroWorld,
            FutureWorld.ID: FutureWorld,
            AlternateWorld.ID: AlternateWorld
        }
    
    def get_world(self, world_id: str):
        """الحصول على عالم معين"""
        return self.worlds.get(world_id)
    
    def get_all_worlds(self) -> List[Dict]:
        """الحصول على كل العوالم (كقاموس)"""
        return [world.to_dict() for world in self.worlds.values()]
    
    def get_world_names(self) -> Dict[str, str]:
        """الحصول على أسماء العوالم"""
        return {wid: world.NAME for wid, world in self.worlds.items()}
    
    def get_world_emojis(self) -> Dict[str, str]:
        """الحصول على إيموجيات العوالم"""
        return {wid: world.EMOJI for wid, world in self.worlds.items()}
    
    def get_world_colors(self) -> Dict[str, int]:
        """الحصول على ألوان العوالم"""
        return {wid: world.COLOR for wid, world in self.worlds.items()}
    
    def get_start_part(self, world_id: str) -> str:
        """الحصول على جزء البداية لعالم"""
        world = self.get_world(world_id)
        return world.START_PART if world else "PART_01"
    
    def get_ending(self, world_id: str, ending_type: str) -> Optional[WorldEnding]:
        """الحصول على نهاية معينة"""
        world = self.get_world(world_id)
        if world and ending_type in world.ENDINGS:
            return world.ENDINGS[ending_type]
        return None
    
    def check_ending_requirements(self, world_id: str, ending_type: str, player_data: Dict) -> bool:
        """التحقق من متطلبات نهاية معينة"""
        ending = self.get_ending(world_id, ending_type)
        if not ending:
            return False
        
        for req, value in ending.requirements.items():
            if player_data.get(req, 0) < value:
                return False
        
        return True
    
    def get_next_world(self, world_id: str, ending_type: str) -> Optional[str]:
        """الحصول على العالم التالي بعد نهاية معينة"""
        ending = self.get_ending(world_id, ending_type)
        return ending.next_world if ending else None
    
    def get_character(self, world_id: str, char_id: str) -> Optional[WorldCharacter]:
        """الحصول على شخصية معينة"""
        world = self.get_world(world_id)
        if world and char_id in world.CHARACTERS:
            return world.CHARACTERS[char_id]
        return None
    
    def get_location(self, world_id: str, loc_id: str) -> Optional[WorldLocation]:
        """الحصول على موقع معين"""
        world = self.get_world(world_id)
        if world and loc_id in world.LOCATIONS:
            return world.LOCATIONS[loc_id]
        return None
    
    def get_special_item(self, world_id: str, item_id: str) -> Optional[Dict]:
        """الحصول على عنصر خاص بعالم"""
        world = self.get_world(world_id)
        if world and hasattr(world, 'SPECIAL_ITEMS'):
            return world.SPECIAL_ITEMS.get(item_id)
        return None
    
    def get_world_order(self) -> List[str]:
        """الحصول على ترتيب العوالم"""
        worlds = list(self.worlds.values())
        worlds.sort(key=lambda w: w.ORDER)
        return [w.ID for w in worlds]


# ============================================
# إنشاء كائن المدير العام
# ============================================

world_manager = WorldManager()

# ============================================
# تصدير الكلاسات
# ============================================

__all__ = [
    'FantasyWorld',
    'RetroWorld',
    'FutureWorld',
    'AlternateWorld',
    'WorldManager',
    'world_manager',
    'WorldCharacter',
    'WorldLocation',
    'WorldEnding'
]
