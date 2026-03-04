# story/loader.py - محمل القصص المتقدم
# يدعم 4 عوالم مع تحميل ذكي وتخزين مؤقت

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

from core.config import paths, config
from utils.helpers import safe_json_loads, safe_json_dumps, deep_get
from utils.logger import logger_manager

logger = logging.getLogger(__name__)


class StoryLoader:
    """
    محمل القصص المتقدم
    يدعم 4 عوالم مع تخزين مؤقت وتحقق من الصحة
    """
    
    # داخل class StoryLoader

WORLDS = {
    "fantasy": {
        "name": "عالم الفانتازيا",
        "file": paths.FANTASY_STORY,
        "start_part": "FANTASY_001",
        "total_parts": 50,
        "endings": 3,
        "color": 0x9b59b6,
        "emoji": "🌲"
    },
    "retro": {
        "name": "عالم الماضي",
        "file": paths.RETRO_STORY,
        "start_part": "RETRO_01",
        "total_parts": 100,
        "endings": 5,
        "color": 0x3498db,
        "emoji": "📜"
    },
    "future": {
        "name": "عالم المستقبل",
        "file": paths.FUTURE_STORY,
        "start_part": "FUTURE_001",
        "total_parts": 32,
        "endings": 4,
        "color": 0xe74c3c,
        "emoji": "🤖"
    },
    "alternate": {
        "name": "الواقع البديل",
        "file": paths.ALTERNATE_STORY,
        "start_part": "ALTER_001",
        "total_parts": 36,
        "endings": 5,
        "color": 0x2ecc71,
        "emoji": "🌀"
    }
}

def get_start_part(self, world_id: str) -> str:
    """الحصول على جزء البداية لعالم معين مع توافق أسماء الأجزاء المختلفة"""
    world_info = self.WORLDS.get(world_id, {})
    configured_start = world_info.get("start_part", f"{world_id.upper()}_01")

    story = self.stories.get(world_id, {})
    parts = story.get("parts", {})

    if configured_start in parts:
        return configured_start

    if parts:
        # fallback مرن: خذ أقل جزء حسب الرقم النهائي (يدعم _01 و _001)
        def _part_sort_key(part_id: str):
            try:
                return int(part_id.split("_")[-1])
            except (ValueError, TypeError):
                return float("inf")

        return min(parts.keys(), key=_part_sort_key)

    return configured_start
        }
    }
    
    def __init__(self, db):
        self.db = db
        self.stories = {}
        self.cache = {}
        self.cache_timeout = 300  # 5 دقائق
        self.logger = logger_manager.get_logger('story')
        
        # إحصائيات التحميل
        self.stats = {
            "total_parts": 0,
            "loaded_worlds": 0,
            "last_load": None
        }
    
    async def load_all_stories(self):
        """تحميل كل قصص العوالم"""
        loaded = 0
        failed = []
        
        for world_id, world_info in self.WORLDS.items():
            try:
                success = await self.load_story(world_id)
                if success:
                    loaded += 1
                    self.stats["loaded_worlds"] += 1
                else:
                    failed.append(world_id)
            except Exception as e:
                self.logger.error(f"❌ خطأ في تحميل {world_id}: {e}")
                failed.append(world_id)
        
        self.stats["last_load"] = datetime.now().isoformat()
        
        if failed:
            self.logger.warning(f"⚠️ فشل تحميل: {', '.join(failed)}")
        self.logger.info(f"✅ تم تحميل {loaded}/{len(self.WORLDS)} عوالم")
        
        # حساب إجمالي الأجزاء
        self._update_total_parts()

        # التحقق من الوصلات بعد تحميل كل العوالم
        self.validate_all_parts()
    
    async def load_story(self, world_id: str) -> bool:
        """تحميل قصة عالم معين"""
        world_info = self.WORLDS.get(world_id)
        if not world_info:
            self.logger.error(f"❌ عالم غير معروف: {world_id}")
            return False
        
        file_path = world_info["file"]
        
        try:
            # التحقق من وجود الملف
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # التحقق من صحة البيانات
                    if not self._validate_story_data(data, world_id):
                        self.logger.warning(f"⚠️ بيانات {world_id} غير صالحة، استخدام افتراضية")
                        data = self._create_default_story(world_id)
            else:
                self.logger.warning(f"⚠️ ملف {world_id} غير موجود، إنشاء قصة افتراضية")
                data = self._create_default_story(world_id)
                
                # حفظ القصة الافتراضية
                self._save_default_story(world_id, data)
            
            # إضافة معلومات إضافية
            data['world_id'] = world_id
            data['world_name'] = world_info['name']
            data['loaded_at'] = datetime.now().isoformat()
            
            self.stories[world_id] = data
            self.logger.info(f"✅ تم تحميل {world_info['name']}: {self._count_parts(data)} أجزاء")
            
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ خطأ في JSON لـ {world_id}: {e}")
            # استخدام القصة الافتراضية
            self.stories[world_id] = self._create_default_story(world_id)
            return False
        except Exception as e:
            self.logger.error(f"❌ خطأ غير متوقع في {world_id}: {e}")
            return False
    
    def _validate_story_data(self, data: Dict, world_id: str) -> bool:
        """التحقق من صحة بيانات القصة"""
        required_fields = ['metadata', 'parts']
        
        for field in required_fields:
            if field not in data:
                self.logger.error(f"❌ {world_id}: حقل {field} مفقود")
                return False
        
        # التحقق من وجود أجزاء
        parts = data.get('parts')
        if not parts:
            self.logger.error(f"❌ {world_id}: لا توجد أجزاء")
            return False

        # التحقق من تطابق metadata.total_parts مع العدد الفعلي
        metadata_total = data.get('metadata', {}).get('total_parts')
        actual_total = len(parts)
        if isinstance(metadata_total, int) and metadata_total != actual_total:
            self.logger.error(f"❌ {world_id}: metadata.total_parts={metadata_total} لا يطابق العدد الفعلي={actual_total}")
            return False

        # التحقق من كل جزء
        for part_id, part in parts.items():
            if not self._validate_part(part, part_id, world_id):
                return False
        
        return True
    
    def _validate_part(self, part: Dict, part_id: str, world_id: str) -> bool:
        """التحقق من صحة جزء معين"""
        required_fields = ['title', 'text', 'choices']
        
        for field in required_fields:
            if field not in part:
                self.logger.error(f"❌ {world_id} - {part_id}: حقل {field} مفقود")
                return False
        
        # التحقق من الخيارات
        choices = part['choices']
        if not choices:
            self.logger.error(f"❌ {world_id} - {part_id}: لا توجد خيارات")
            return False

        if not (2 <= len(choices) <= 4):
            self.logger.error(f"❌ {world_id} - {part_id}: عدد الخيارات يجب أن يكون بين 2 و4")
            return False
        
        for i, choice in enumerate(choices):
            if 'text' not in choice or 'next' not in choice:
                self.logger.error(f"❌ {world_id} - {part_id}: خيار {i} غير صالح")
                return False

            chance = choice.get('chance')
            if chance is not None and (not isinstance(chance, int) or chance < 1 or chance > 100):
                self.logger.error(f"❌ {world_id} - {part_id}: chance غير صالح في الخيار {i}")
                return False

            if chance is not None and 'fail_next' not in choice:
                self.logger.error(f"❌ {world_id} - {part_id}: fail_next مفقود للخيار {i}")
                return False
        
        return True
    
    def _create_default_story(self, world_id: str) -> Dict:
        """إنشاء قصة افتراضية لعالم معين"""
        world_info = self.WORLDS.get(world_id, {})
        
        stories = {
            "fantasy": {
                "metadata": {
                    "name": "عالم الفانتازيا",
                    "version": "1.0",
                    "total_parts": 10,
                    "endings": 3,
                    "variables": ["shards", "corruption", "fantasy_power"]
                },
                "parts": {
                    "FANTASY_01": {
                        "title": "صحوة التائه",
                        "location": "الساحة الغريبة",
                        "text": "استيقظت في ساحة غريبة. السماء بنفسجية والأشجار تلمع بضوء غريب. لا تذكر كيف وصلت إلى هنا. آخر شيء تتذكره هو وميض أزرق... ثم لا شيء.",
                        "choices": [
                            {
                                "text": "🔍 استكشاف المكان",
                                "emoji": "🔍",
                                "next": "FANTASY_02",
                                "effects": {"fantasy_power": 5, "mystery": 2}
                            },
                            {
                                "text": "⏳ انتظار المساعدة",
                                "emoji": "⏳",
                                "next": "FANTASY_03",
                                "effects": {"shards": 1, "corruption": 1}
                            },
                            {
                                "text": "🧘 التأمل ومحاولة التذكر",
                                "emoji": "🧘",
                                "next": "FANTASY_04",
                                "effects": {"mystery": 5, "knowledge_path": 2}
                            }
                        ]
                    },
                    "FANTASY_02": {
                        "title": "بوابة النور",
                        "location": "الساحة الغريبة",
                        "text": "تتجول في الساحة، فتكتشف بوابة من نور تتلألأ. تشعر بدفء غريب ينبعث منها. هل تدخل؟",
                        "choices": [
                            {
                                "text": "🚪 الدخول",
                                "emoji": "🚪",
                                "next": "FANTASY_05",
                                "effects": {"fantasy_power": 10, "mystery": 5}
                            },
                            {
                                "text": "👁️ التجول حولها",
                                "emoji": "👁️",
                                "next": "FANTASY_06",
                                "effects": {"knowledge_path": 3}
                            }
                        ]
                    },
                    "FANTASY_03": {
                        "title": "ظل يتحرك",
                        "location": "الساحة الغريبة",
                        "text": "بينما تنتظر، ترى ظلاً يتحرك بين الأشجار. يقترب ببطء...",
                        "choices": [
                            {
                                "text": "🗡️ مواجهته",
                                "emoji": "🗡️",
                                "next": "FANTASY_07",
                                "effects": {"corruption": 5, "shards": 2}
                            },
                            {
                                "text": "💬 التحدث معه",
                                "emoji": "💬",
                                "next": "FANTASY_08",
                                "effects": {"mystery": 5, "trust_aren": 5}
                            }
                        ]
                    }
                }
            },
            "retro": {
                "metadata": {
                    "name": "عالم الماضي",
                    "version": "1.0",
                    "total_parts": 8,
                    "endings": 3,
                    "variables": ["shards", "corruption", "memories"]
                },
                "parts": {
                    "RETRO_01": {
                        "title": "العودة إلى الطفولة",
                        "location": "المنزل القديم",
                        "text": "تجد نفسك في منزل طفولتك. كل شيء كما كان... الأثاث، الرائحة، حتى الضوء. لكن شيئاً واحداً مختلف: أنت هنا الآن، وهناك شخص آخر في الغرفة المجاورة.",
                        "choices": [
                            {
                                "text": "🔍 استكشاف المنزل",
                                "emoji": "🔍",
                                "next": "RETRO_02",
                                "effects": {"memories": 5, "mystery": 2}
                            },
                            {
                                "text": "🚪 فتح باب الغرفة",
                                "emoji": "🚪",
                                "next": "RETRO_03",
                                "effects": {"memories": 10, "corruption": 2}
                            }
                        ]
                    }
                }
            },
            "future": {
                "metadata": {
                    "name": "عالم المستقبل",
                    "version": "1.0",
                    "total_parts": 8,
                    "endings": 3,
                    "variables": ["shards", "corruption", "tech_level"]
                },
                "parts": {
                    "FUTURE_01": {
                        "title": "مدينة الضوء",
                        "location": "المدينة المستقبلية",
                        "text": "تهبط في مدينة مستقبلية. المباني تلامس السحاب، والسيارات تطير في السماء. لكن هناك شيء غريب... لا يوجد بشر في الشوارع. فقط آلات.",
                        "choices": [
                            {
                                "text": "🤖 متابعة الآلات",
                                "emoji": "🤖",
                                "next": "FUTURE_02",
                                "effects": {"tech_level": 5, "mystery": 3}
                            },
                            {
                                "text": "🔍 البحث عن بشر",
                                "emoji": "🔍",
                                "next": "FUTURE_03",
                                "effects": {"reputation": 5}
                            }
                        ]
                    }
                }
            },
            "alternate": {
                "metadata": {
                    "name": "الواقع البديل",
                    "version": "1.0",
                    "total_parts": 6,
                    "endings": 4,
                    "variables": ["shards", "corruption", "identity"]
                },
                "parts": {
                    "ALT_01": {
                        "title": "كل الاحتمالات",
                        "location": "بين العوالم",
                        "text": "تقف في فضاء لا نهائي. حولك، ترى نسخاً متعددة من نفسك من عوالم مختلفة. كل واحدة تروي قصة مختلفة. من أنت حقاً؟",
                        "choices": [
                            {
                                "text": "💬 التحدث معهم",
                                "emoji": "💬",
                                "next": "ALT_02",
                                "effects": {"identity": 5, "knowledge_path": 5}
                            },
                            {
                                "text": "🌀 الاندماج معهم",
                                "emoji": "🌀",
                                "next": "ALT_03",
                                "effects": {"identity": 15, "corruption": 10}
                            }
                        ]
                    }
                }
            }
        }
        
        return stories.get(world_id, {"metadata": {}, "parts": {}})
    
    def _save_default_story(self, world_id: str, data: Dict):
        """حفظ القصة الافتراضية في ملف"""
        try:
            file_path = self.WORLDS[world_id]["file"]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ تم حفظ قصة افتراضية لـ {world_id}")
        except Exception as e:
            self.logger.error(f"❌ خطأ في حفظ القصة الافتراضية: {e}")
    
    def _count_parts(self, story: Dict) -> int:
        """حساب عدد الأجزاء في القصة"""
        return len(story.get('parts', {}))
    
    def _update_total_parts(self):
        """تحديث إجمالي عدد الأجزاء"""
        total = 0
        for world_id, story in self.stories.items():
            total += self._count_parts(story)
        self.stats["total_parts"] = total
    
    def get_part(self, world_id: str, part_id: str) -> Optional[Dict]:
        """الحصول على جزء من قصة عالم معين"""
        # التحقق من التخزين المؤقت
        cache_key = f"{world_id}_{part_id}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.cache_timeout:
                return data.copy() if data else None
        
        world_story = self.stories.get(world_id)
        if not world_story:
            self.logger.error(f"❌ عالم غير موجود: {world_id}")
            return None
        
        part = world_story.get('parts', {}).get(part_id)
        if part:
            # إضافة معلومات إضافية
            part = part.copy()
            part['id'] = part_id
            part['world'] = world_id
            part['world_name'] = self.WORLDS[world_id]['name']
            
            # تخزين في الكاش
            self.cache[cache_key] = (datetime.now(), part)
            
            return part
        
        self.logger.warning(f"⚠️ جزء غير موجود: {world_id} - {part_id}")
        return None
    
    def get_start_part(self, world_id: str) -> str:
        """الحصول على جزء البداية عالم معين"""
        world_info = self.WORLDS.get(world_id, {})
        return world_info.get("start_part", f"{world_id.upper()}_01")
    
    def get_next_part(self, world_id: str, current_part: str, choice_index: int) -> Optional[str]:
        """الحصول على الجزء التالي بناءً على اختيار"""
        part = self.get_part(world_id, current_part)
        if not part:
            return None
        
        choices = part.get('choices', [])
        if choice_index < 0 or choice_index >= len(choices):
            return None
        
        return choices[choice_index].get('next')
    
    def get_ending(self, world_id: str, ending_id: str) -> Optional[Dict]:
        """الحصول على نهاية معينة"""
        world_story = self.stories.get(world_id)
        if not world_story:
            return None
        
        endings = world_story.get('endings', {})
        return endings.get(ending_id)
    
    def get_metadata(self, world_id: str) -> Dict:
        """الحصول على بيانات تعريفية لعالم"""
        world_story = self.stories.get(world_id, {})
        return world_story.get('metadata', {})
    
    def get_variables(self, world_id: str) -> List[str]:
        """الحصول على قائمة المتغيرات الخاصة بعالم"""
        metadata = self.get_metadata(world_id)
        return metadata.get('variables', [])
    
    def get_all_parts(self, world_id: str) -> Dict[str, Dict]:
        """الحصول على كل أجزاء عالم (للاستخدام الداخلي)"""
        world_story = self.stories.get(world_id, {})
        return world_story.get('parts', {})
    
    def part_exists(self, world_id: str, part_id: str) -> bool:
        """التحقق من وجود جزء"""
        return self.get_part(world_id, part_id) is not None
    
    def is_ending(self, world_id: str, part_id: str) -> bool:
        """التحقق مما إذا كان الجزء نهاية"""
        part = self.get_part(world_id, part_id)
        if not part:
            return False
        
        # التحقق من وجود خيارات (النهايات ليس لها خيارات أو خيار واحد فقط)
        choices = part.get('choices', [])
        return len(choices) <= 1
    
    def get_ending_type(self, world_id: str, part_id: str) -> str:
        """الحصول على نوع النهاية"""
        part = self.get_part(world_id, part_id)
        if not part:
            return "unknown"
        
        return part.get('ending_type', 'normal')
    
    def get_world_progress(self, world_id: str, current_part: str) -> Dict:
        """الحصول على تقدم اللاعب في العالم"""
        all_parts = self.get_all_parts(world_id)
        total = len(all_parts)
        
        # البحث عن مؤشر الجزء الحالي
        current_index = 0
        part_ids = list(all_parts.keys())
        
        if current_part in part_ids:
            current_index = part_ids.index(current_part) + 1
        
        return {
            "total": total,
            "current": current_index,
            "percentage": (current_index / total * 100) if total > 0 else 0,
            "is_ending": self.is_ending(world_id, current_part)
        }
    
    def get_available_choices(self, world_id: str, part_id: str, player_data: Dict) -> List[Dict]:
        """الحصول على الخيارات المتاحة بناءً على شروط اللاعب"""
        part = self.get_part(world_id, part_id)
        if not part:
            return []
        
        choices = []
        for choice in part.get('choices', []):
            # التحقق من الشروط
            requirements = choice.get('require', {})
            if self._check_requirements(requirements, player_data):
                choices.append(choice)
        
        return choices
    
    def _check_requirements(self, requirements: Dict, player_data: Dict) -> bool:
        """التحقق من شروط الخيار"""
        for key, value in requirements.items():
            if key == "flag":
                # التحقق من العلم
                # هذه الدالة تحتاج للاعب من قاعدة البيانات
                pass
            else:
                player_value = player_data.get(key, 0)
                if player_value < value:
                    return False
        return True
    
    def get_choice_effects(self, world_id: str, part_id: str, choice_index: int) -> Dict:
        """الحصول على تأثيرات اختيار معين"""
        part = self.get_part(world_id, part_id)
        if not part:
            return {}
        
        choices = part.get('choices', [])
        if choice_index < 0 or choice_index >= len(choices):
            return {}
        
        return choices[choice_index].get('effects', {})
    
    def clear_cache(self):
        """مسح التخزين المؤقت"""
        self.cache.clear()
        self.logger.info("🧹 تم مسح التخزين المؤقت للقصص")
    
    async def reload_world(self, world_id: str) -> bool:
        """إعادة تحميل عالم معين"""
        # مسح الكاش لهذا العالم
        keys_to_delete = [k for k in self.cache if k.startswith(f"{world_id}_")]
        for key in keys_to_delete:
            del self.cache[key]
        
        # إعادة التحميل
        return await self.load_story(world_id)
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات المحمل"""
        stats = self.stats.copy()
        stats["worlds"] = {}
        
        for world_id, story in self.stories.items():
            stats["worlds"][world_id] = {
                "name": self.WORLDS[world_id]["name"],
                "parts": self._count_parts(story),
                "loaded_at": story.get('loaded_at', 'unknown')
            }
        
        return stats
    
    def validate_all_parts(self) -> List[str]:
        """التحقق من صحة كل الأجزاء (للتأكد من عدم وجود وصلات مقطوعة)"""
        errors = []
        
        for world_id, story in self.stories.items():
            parts = story.get('parts', {})
            
            for part_id, part in parts.items():
                for i, choice in enumerate(part.get('choices', [])):
                    valid_endings = set(story.get('endings', {}).keys())

                    next_part = choice.get('next')
                    if next_part and next_part not in parts and next_part not in valid_endings:
                        errors.append(f"{world_id} - {part_id} -> {next_part} (غير موجود)")

                    fail_next = choice.get('fail_next')
                    if fail_next and fail_next not in parts and fail_next not in valid_endings:
                        errors.append(f"{world_id} - {part_id} -> fail_next:{fail_next} (غير موجود)")
        
        if errors:
            self.logger.warning(f"⚠️ {len(errors)} خطأ في وصلات القصة")
        else:
            self.logger.info("✅ جميع وصلات القصة سليمة")
        
        return errors
