# ui/views.py - الأزرار الدائمة والتفاعلية
# هذا أهم ملف في البوت! يضمن أن الأزرار تعمل للأبد

import discord
from discord.ui import View, Button
import logging
import asyncio
import sqlite3
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import random
import aiosqlite

from core.constants import BUTTON_STYLES, WORLD_EMOJIS, get_button_style
from utils.logger import logger_manager
from utils.helpers import parse_effects, summarize_effects, clamp
from utils.rate_limiter import ButtonRateLimit

logger = logging.getLogger(__name__)


def _classify_error(exc: Exception, source: str = "general") -> str:
    if isinstance(exc, (aiosqlite.Error, sqlite3.Error)):
        return "db_error"
    if isinstance(exc, discord.Forbidden):
        return "permissions_error"
    if source == "story_loader":
        return "story_loader_error"
    return "unexpected_error"


def _log_exception_with_context(
    *,
    error: Exception,
    event: str,
    source: str,
    interaction: Optional[discord.Interaction] = None,
    current_world: Optional[str] = None,
    current_part: Optional[str] = None,
    user_id: Optional[int] = None,
):
    logger.exception(
        "%s error_type=%s source=%s user_id=%s guild_id=%s channel_id=%s current_world=%s current_part=%s",
        event,
        _classify_error(error, source),
        source,
        user_id if user_id is not None else getattr(getattr(interaction, "user", None), "id", None),
        getattr(getattr(interaction, "guild", None), "id", None),
        getattr(getattr(interaction, "channel", None), "id", None),
        current_world,
        current_part,
        exc_info=error,
    )


class PersistentStoryView(View):
    """
    الأزرار الدائمة للقصة
    Timeout=None يعني الأزرار لا تنتهي أبداً!
    """
    
    def __init__(self, bot, user_id: int, world_id: str, part_data: Dict):
        # timeout=None هو السر! الأزرار تعمل للأبد
        super().__init__(timeout=None)
        
        self.bot = bot
        self.user_id = user_id
        self.world_id = world_id
        self.part_data = part_data
        self.part_id = part_data.get('id', 'unknown')
        
        # إحصائيات لهذا العرض
        self.clicks = 0
        self.created_at = datetime.now()
        
        # إنشاء الأزرار
        self._setup_buttons()
        
        logger.debug(f"✅ تم إنشاء أزرار دائمة لـ {user_id} في {world_id} - {self.part_id}")
    
    def _setup_buttons(self):
        """إنشاء الأزرار حسب الخيارات المتاحة"""
        choices = self.part_data.get('choices', [])
        
        for i, choice in enumerate(choices):
            # تحديد نمط الزر حسب نوع الخيار
            style = self._get_button_style(choice)
            
            # إنشاء custom_id فريد وثابت
            # هذا المفتاح يضمن بقاء الزر للأبد
            custom_id = f"nexus_{self.world_id}_{self.part_id}_{i}"
            
            # إنشاء الزر
            button = Button(
                label=choice.get('text', f'خيار {i+1}')[:80],  # حد 80 حرف
                emoji=choice.get('emoji'),
                style=style,
                custom_id=custom_id,
                row=i // 3  # كل 3 أزرار في سطر
            )
            
            # ربط callback
            button.callback = self._create_callback(choice, i)
            
            self.add_item(button)
    
    def _get_button_style(self, choice: Dict) -> discord.ButtonStyle:
        """تحديد لون الزر حسب نوع الخيار"""
        text = choice.get('text', '').lower()
        emoji = choice.get('emoji', '')
        
        # أنماط مختلفة
        if '⚔️' in emoji or 'قتال' in text or 'هاجم' in text:
            return BUTTON_STYLES['combat']  # أحمر
        elif '🔍' in emoji or 'استكشف' in text or 'بحث' in text:
            return BUTTON_STYLES['explore']  # أزرق
        elif '💬' in emoji or 'تحدث' in text or 'حوار' in text:
            return BUTTON_STYLES['talk']  # رمادي
        elif '🏃' in emoji or 'اهرب' in text or 'هروب' in text:
            return BUTTON_STYLES['flee']  # رمادي
        elif '💎' in emoji or 'شظية' in text or 'كنز' in text:
            return BUTTON_STYLES['shard']  # أخضر
        elif '💰' in emoji or 'مكافأة' in text:
            return BUTTON_STYLES['success']  # أخضر
        else:
            return BUTTON_STYLES['primary']  # أزرق عادي
    
    def _create_callback(self, choice: Dict, choice_index: int):
        """إنشاء دالة الاستدعاء للزر"""
        
        async def callback(interaction: discord.Interaction):
            # التحقق من أن المستخدم هو صاحب القصة
            if interaction.user.id != self.user_id:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description="هذه القصة ليست لك! ابدأ رحلتك الخاصة بـ `/ابدأ`",
                    color=self.bot.world_colors["error"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # إقرار التفاعل مباشرة لتجنب مهلة Discord عند بطء DB
            await interaction.response.defer()
            
            # التحقق من معدل الاستخدام (منع السبام)
            async with ButtonRateLimit(self.bot, self.user_id, f"{self.world_id}_{self.part_id}") as rate_limit:
                if not rate_limit.allowed:
                    if rate_limit.wait_time:
                        message = self.bot.rate_limiter.format_wait_message(rate_limit.wait_time)
                    else:
                        message = "⏳ انتظر قليلاً قبل استخدام الزر مرة أخرى"

                    await interaction.followup.send(message, ephemeral=True)
                    return
            
            try:
                # تسجيل النقر
                self.clicks += 1
                logger.info(f"👆 {interaction.user.name} اختار: {choice.get('text')}")
                
                # الحصول على بيانات اللاعب
                player = await self.bot.db.get_player(self.user_id)
                if not player:
                    # إذا لم يكن موجوداً، أنشئه
                    await self.bot.db.create_player(self.user_id, interaction.user.name)
                    player = await self.bot.db.get_player(self.user_id)
                
                # التحقق من الشروط (إن وجدت)
                requirements = choice.get('require', {})
                if not await self._check_requirements(interaction, requirements, player):
                    return
                
                # تطبيق التأثيرات
                effects = choice.get('effects', {})
                updates, impact_log, achievements = await self._apply_effects(
                    interaction, player, effects
                )
                
                # تحديد الجزء التالي
                next_part_id = choice.get('next')
                
                # احتمال الفشل (chance + fail_next)
                chance = choice.get('chance')
                fail_next = choice.get('fail_next')
                if chance is not None and fail_next:
                    roll = random.randint(1, 100)
                    if roll > int(chance):
                        next_part_id = fail_next
                        impact_log.append("🎲 الحظ لم يكن في صفك...")
                    else:
                        impact_log.append("🎲 الحظ حالفك!")
                
                if not next_part_id:
                    embed = discord.Embed(
                        title="❌ خطأ",
                        description="هذا الخيار لا يقود إلى جزء آخر",
                        color=self.bot.world_colors["error"]
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                # الحصول على الجزء التالي
                next_part = self.bot.story_loader.get_part(self.world_id, next_part_id)
                
                if not next_part:
                    embed = discord.Embed(
                        title="❌ خطأ في القصة",
                        description="عذراً، حدث خطأ في تحميل الجزء التالي. تم إبلاغ المطورين.",
                        color=self.bot.world_colors["error"]
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                # تحديث تقدم اللاعب في العالم
                world_part_field = f"{self.world_id}_part"
                updates[world_part_field] = next_part_id
                
                # إضافة نقاط خبرة بموازنة أعمق (تتأثر بالمخاطرة والتقدم)
                xp_gain = self._calculate_xp_gain(player, effects, next_part_id)
                updates["xp"] = player.get("xp", 0) + xp_gain
                impact_log.append(f"🌟 خبرة: +{xp_gain}")

                # إنجاز نادر مرتبط بالخيار (اختياري داخل JSON)
                rare_ach_id = choice.get("achievement_id")
                if rare_ach_id:
                    unlocked = await self.bot.db.unlock_achievement(self.user_id, rare_ach_id, self.world_id)
                    if unlocked:
                        rare_ach_name = choice.get("achievement_name", rare_ach_id)
                        impact_log.append(f"🏆 إنجاز نادر: {rare_ach_name}")
                
                # التحقق من زيادة المستوى
                level_up = False
                if updates["xp"] >= self.bot.get_xp_for_level(player.get("level", 1) + 1):
                    updates["level"] = player.get("level", 1) + 1
                    level_up = True
                    impact_log.append(f"⬆️ المستوى {updates['level']}!")
                
                # تحديث قاعدة البيانات
                await self.bot.db.update_player(self.user_id, updates)

                # حفظ الجلسة الحالية لاسترجاع الأزرار بعد إعادة التشغيل
                await self.bot.db.save_session(self.user_id, next_part_id)
                
                # تسجيل القرار في التاريخ
                impact_summary = summarize_effects(effects)
                await self.bot.db.add_history(
                    self.user_id,
                    self.world_id,
                    self.part_id,
                    choice.get('text'),
                    effects
                )
                
                # إنشاء الرسالة الجديدة
                updated_player = await self.bot.db.get_player(self.user_id)
                embed = self.bot.create_game_embed(self.world_id, next_part, updated_player)
                
                # إضافة ملخص التأثيرات
                if impact_log:
                    embed.add_field(
                        name="📊 نتيجة قرارك",
                        value="\n".join(impact_log[:5]),  # أول 5 تأثيرات فقط
                        inline=False
                    )
                
                # إضافة رسالة زيادة المستوى
                if level_up:
                    embed.add_field(
                        name="🎉 تهانينا!",
                        value=f"وصلت إلى المستوى {updates['level']}!",
                        inline=False
                    )
                
                # إرسال الإنجازات الجديدة
                for ach in achievements:
                    ach_embed = discord.Embed(
                        title=f"🏆 إنجاز جديد!",
                        description=f"{ach.get('emoji', '🏆')} **{ach.get('name')}**\n{ach.get('description', '')}",
                        color=0xffd700
                    )
                    await interaction.followup.send(embed=ach_embed, ephemeral=True)
                
                # تحديث الرسالة
                await interaction.message.edit(
                    embed=embed,
                    view=PersistentStoryView(self.bot, self.user_id, self.world_id, next_part)
                )
                
                # التحقق من النهاية
                if self.bot.story_loader.is_ending(self.world_id, next_part_id):
                    await self._handle_ending(interaction, next_part_id, updated_player)
                
            except Exception as e:
                _log_exception_with_context(
                    error=e,
                    event="persistent_story_choice_failed",
                    source="story_loader",
                    interaction=interaction,
                    current_world=self.world_id,
                    current_part=self.part_id,
                    user_id=self.user_id,
                )
                embed = discord.Embed(
                    title="❌ حدث خطأ",
                    description="حدث خطأ أثناء تنفيذ خيارك. حاول مرة أخرى.",
                    color=self.bot.world_colors["error"]
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        return callback
    
    async def _check_requirements(self, interaction: discord.Interaction, requirements: Dict, player: Dict) -> bool:
        """التحقق من شروط الخيار"""
        for req, value in requirements.items():
            if req == "flag":
                # التحقق من العلم
                flag_value = await self.bot.db.get_flag(self.user_id, value)
                if flag_value == 0:
                    embed = discord.Embed(
                        title="❌ متطلب غير مكتمل",
                        description=f"تحتاج إلى تفعيل `{value}` أولاً",
                        color=self.bot.world_colors["warning"]
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return False
            elif req == "item":
                # التحقق من العنصر
                if not await self.bot.db.has_item(self.user_id, value):
                    embed = discord.Embed(
                        title="❌ عنصر ناقص",
                        description=f"تحتاج إلى `{value}` في مخزونك",
                        color=self.bot.world_colors["warning"]
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return False
            else:
                # التحقق من متغيرات اللاعب
                player_value = player.get(req, 0)
                if player_value < value:
                    embed = discord.Embed(
                        title="❌ متطلب ناقص",
                        description=f"تحتاج إلى `{req}` بقيمة {value} على الأقل (لديك {player_value})",
                        color=self.bot.world_colors["warning"]
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return False
        
        return True
    
    def _calculate_xp_gain(self, player: Dict, effects: Dict, next_part_id: str) -> int:
        """حساب خبرة متوازنة حسب المخاطرة والتقدم"""
        base_xp = 10

        # مكافأة بسيطة للمخاطرة
        corruption_delta = int(effects.get("corruption", 0)) if isinstance(effects, dict) else 0
        reputation_delta = abs(int(effects.get("reputation", 0))) if isinstance(effects, dict) else 0
        mystery_delta = int(effects.get("mystery", 0)) if isinstance(effects, dict) else 0

        risk_bonus = max(0, corruption_delta) + (reputation_delta // 2) + (mystery_delta // 2)

        # مكافأة تقدم الجزء
        try:
            part_num = int(str(next_part_id).split('_')[-1])
        except Exception as e:
            _log_exception_with_context(
                error=e,
                event="calculate_xp_gain_parse_failed",
                source="story_loader",
                current_world=self.world_id,
                current_part=self.part_id,
                user_id=self.user_id,
            )
            part_num = 1
        progress_bonus = min(8, part_num // 4)

        # مكافأة اختيار مؤهل/نادر
        rare_bonus = 0
        if effects and any(k in effects for k in ["achievement", "flag"]):
            rare_bonus += 4

        xp_gain = base_xp + risk_bonus + progress_bonus + rare_bonus
        return max(8, min(32, xp_gain))

    async def _apply_effects(self, interaction: discord.Interaction, player: Dict, effects: Dict) -> tuple:
        """تطبيق تأثيرات الاختيار"""
        updates = {}
        impact_log = []
        new_achievements = []
        
        for key, value in effects.items():
            if key == "achievement":
                # فتح إنجاز
                success = await self.bot.db.unlock_achievement(
                    self.user_id, value, self.world_id
                )
                if success:
                    # الحصول على معلومات الإنجاز
                    # (سنضيفها لاحقاً من ملف achievements.py)
                    new_achievements.append({
                        "id": value,
                        "name": value.replace('_', ' ').title(),
                        "emoji": "🏆"
                    })
                    impact_log.append(f"🏆 إنجاز: {value}")
            
            elif key == "inventory_add":
                # إضافة عنصر للمخزون
                if isinstance(value, dict):
                    item_id = value.get("id", "unknown")
                    item_name = value.get("name", item_id)
                    qty = value.get("qty", 1)
                    await self.bot.db.add_to_inventory(self.user_id, item_id, item_name, qty)
                    impact_log.append(f"📦 +{qty} {item_name}")
                else:
                    await self.bot.db.add_to_inventory(self.user_id, value, value)
                    impact_log.append(f"📦 +{value}")
            
            elif key == "inventory_remove":
                # إزالة عنصر من المخزون
                if isinstance(value, dict):
                    item_id = value.get("id")
                    qty = value.get("qty", 1)
                    await self.bot.db.remove_from_inventory(self.user_id, item_id, qty)
                    impact_log.append(f"📦 -{qty} {item_id}")
                else:
                    await self.bot.db.remove_from_inventory(self.user_id, value)
                    impact_log.append(f"📦 -{value}")
            
            elif key == "flag":
                # تعيين علم
                await self.bot.db.set_flag(self.user_id, value, 1)
                impact_log.append(f"🚩 {value}")
            
            elif key == "alignment":
                # تغيير التوجه
                updates[key] = value
                impact_log.append(f"⚖️ توجه: {value}")
            
            else:
                # متغيرات رقمية
                current = player.get(key, 0)
                
                # حدود خاصة لكل متغير
                if key == "corruption":
                    new_val = clamp(current + value, 0, 100)
                elif key == "mystery":
                    new_val = clamp(current + value, 0, 100)
                elif key == "world_stability":
                    new_val = clamp(current + value, 0, 100)
                elif key == "reputation":
                    new_val = clamp(current + value, -50, 50)
                elif key in ["trust_aren", "fantasy_power", "memories", "tech_level", "identity"]:
                    new_val = clamp(current + value, 0, 100)
                elif key == "shards":
                    new_val = max(0, current + value)
                else:
                    new_val = max(0, current + value)
                
                updates[key] = new_val
                
                # إضافة للسجل مع رمز مناسب
                if value > 0:
                    impact_log.append(f"📈 {key}: +{value}")
                elif value < 0:
                    impact_log.append(f"📉 {key}: {value}")
        
        return updates, impact_log, new_achievements
    
    async def _handle_ending(self, interaction: discord.Interaction, part_id: str, player: Dict):
        """معالجة الوصول إلى نهاية"""
        
        # تحديد نوع النهاية
        ending_type = self.bot.story_loader.get_ending_type(self.world_id, part_id)
        
        # حفظ النهاية في قاعدة البيانات
        ending_field = f"{self.world_id}_ending"
        await self.bot.db.update_player(self.user_id, {ending_field: part_id})
        
        # تحديث إحصائيات العالم
        await self.bot.db.update_world_stats(self.world_id, 'complete')
        
        # رسالة خاصة حسب النوع
        ending_messages = {
            "light": "✨ لقد اخترت طريق النور...",
            "dark": "🌑 استسلمت للظلام...",
            "gray": "⚖️ حافظت على التوازن...",
            "secret": "🔮 لقد اكتشفت السر الأعظم!"
        }
        
        message = ending_messages.get(ending_type, "🏁 لقد وصلت إلى النهاية!")
        
        embed = discord.Embed(
            title=f"🎬 نهاية {self.bot.get_world_name(self.world_id)}",
            description=message,
            color=self.bot.get_world_color(self.world_id)
        )
        
        # هل يفتح عالماً جديداً؟
        if self.world_id == "fantasy" and ending_type in ["light", "secret"]:
            embed.add_field(
                name="🔓 عالم جديد مفتوح!",
                value=f"{WORLD_EMOJIS['retro']} **عالم الماضي** أصبح متاحاً الآن!\nاستخدم `/ابدأ retro` لبدء المغامرة.",
                inline=False
            )
        elif self.world_id == "retro" and ending_type in ["light", "secret"]:
            embed.add_field(
                name="🔓 عالم جديد مفتوح!",
                value=f"{WORLD_EMOJIS['future']} **عالم المستقبل** أصبح متاحاً الآن!",
                inline=False
            )
        elif self.world_id == "future" and ending_type in ["light", "secret"]:
            embed.add_field(
                name="🔓 عالم جديد مفتوح!",
                value=f"{WORLD_EMOJIS['alternate']} **الواقع البديل** أصبح متاحاً الآن!",
                inline=False
            )
        elif self.world_id == "alternate":
            embed.add_field(
                name="🏆 تهانينا!",
                value="لقد أكملت كل العوالم! أنت الآن أسطورة النيكسس.",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        
        # إضافة إنجاز خاص لإكمال العالم
        await self.bot.db.unlock_achievement(
            self.user_id,
            f"completed_{self.world_id}",
            self.world_id
        )
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        """معالجة الأخطاء"""
        _log_exception_with_context(
            error=error,
            event="persistent_story_view_on_error",
            source="general",
            interaction=interaction,
            current_world=self.world_id,
            current_part=self.part_id,
            user_id=self.user_id,
        )
        
        embed = discord.Embed(
            title="❌ حدث خطأ",
            description="عذراً، حدث خطأ غير متوقع. تم إبلاغ المطورين.",
            color=self.bot.world_colors["error"]
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            _log_exception_with_context(
                error=e,
                event="persistent_story_view_response_fallback",
                source="permissions",
                interaction=interaction,
                current_world=self.world_id,
                current_part=self.part_id,
                user_id=self.user_id,
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class PersistentViewManager:
    """
    مدير الأزرار الدائمة
    مسؤول عن تسجيل وتتبع كل الأزرار في البوت
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.active_views: Dict[str, PersistentStoryView] = {}
        self.view_count = 0
    
    async def register_all_views(self):
        """
        تسجيل كل الأزرار الدائمة
        مهم جداً! يضمن أن الأزرار تعمل حتى بعد إعادة التشغيل
        """
        try:
            active_states = await self.bot.get_active_story_states()
            restored = 0

            for state in active_states:
                user_id = state.get("user_id")
                world_id = state.get("world_id")
                current_part = state.get("part_id")
                if not user_id or not world_id or not current_part:
                    continue

                part_data = self.bot.story_loader.get_part(world_id, current_part)
                if not part_data:
                    continue

                view = PersistentStoryView(self.bot, user_id, world_id, part_data)
                self.bot.add_view(view)
                self.add_view(view, f"{user_id}:{world_id}:{current_part}")
                restored += 1

            logger.info(f"✅ تم تسجيل الأزرار الدائمة ({restored} حالة نشطة مستعادة)")

        except Exception as e:
            _log_exception_with_context(
                error=e,
                event="register_all_views_failed",
                source="story_loader",
            )
    
    def add_view(self, view: PersistentStoryView, view_id: str):
        """إضافة عرض جديد"""
        self.active_views[view_id] = view
        self.view_count += 1
    
    def remove_view(self, view_id: str):
        """إزالة عرض"""
        if view_id in self.active_views:
            del self.active_views[view_id]
    
    def get_view(self, view_id: str) -> Optional[PersistentStoryView]:
        """الحصول على عرض"""
        return self.active_views.get(view_id)
    
    def get_stats(self) -> Dict:
        """الحصول على إحصائيات الأزرار"""
        return {
            "active_views": len(self.active_views),
            "total_views_created": self.view_count,
            "views": {
                vid: {
                    "user_id": v.user_id,
                    "world": v.world_id,
                    "part": v.part_id,
                    "clicks": v.clicks,
                    "age": (datetime.now() - v.created_at).total_seconds()
                }
                for vid, v in self.active_views.items()
            }
        }


# ============================================
# أزرار مساعدة أخرى
# ============================================

class ConfirmView(View):
    """عرض تأكيد بسيط (نعم/لا)"""
    
    def __init__(self, user_id: int, confirm_callback: Callable, cancel_callback: Callable = None):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback
    
    @discord.ui.button(label="✅ نعم", style=discord.ButtonStyle.success, emoji="✅", row=0)
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس لك!", ephemeral=True)
            return
        
        await self.confirm_callback(interaction)
        self.stop()
    
    @discord.ui.button(label="❌ لا", style=discord.ButtonStyle.danger, emoji="❌", row=0)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس لك!", ephemeral=True)
            return
        
        if self.cancel_callback:
            await self.cancel_callback(interaction)
        else:
            await interaction.response.edit_message(content="✅ تم الإلغاء", view=None)
        self.stop()
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class PaginatedView(View):
    """عرض صفحات بسيط للتنقل بين عدة Embeds"""

    def __init__(self, user_id: int, pages: List[discord.Embed], timeout: int = 120):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.pages = pages
        self.current_page = 0

        # إذا صفحة واحدة فقط، لا حاجة لأزرار التنقل
        if len(self.pages) <= 1:
            for item in self.children:
                item.disabled = True
        else:
            self._update_buttons()

    def _update_buttons(self):
        if len(self.pages) <= 1:
            self.prev_button.disabled = True
            self.next_button.disabled = True
            return

        self.prev_button.disabled = self.current_page <= 0
        self.next_button.disabled = self.current_page >= len(self.pages) - 1

    @discord.ui.button(label="⬅️ السابق", style=discord.ButtonStyle.secondary, row=0)
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس لك!", ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1

        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="التالي ➡️", style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا ليس لك!", ephemeral=True)
            return

        if self.current_page < len(self.pages) - 1:
            self.current_page += 1

        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class WorldSelectView(View):
    """عرض اختيار العالم"""
    
    def __init__(self, bot, user_id: int, available_worlds: List[str]):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.selected_world = None
        
        # إنشاء زر لكل عالم متاح
        for i, world_id in enumerate(available_worlds):
            world_info = self.bot.story_loader.WORLDS.get(world_id, {})
            
            button = Button(
                label=world_info.get('name', world_id),
                emoji=world_info.get('emoji', '🌍'),
                style=discord.ButtonStyle.primary,
                custom_id=f"world_select_{world_id}",
                row=i // 2
            )
            button.callback = self._create_callback(world_id)
            self.add_item(button)
    
    def _create_callback(self, world_id: str):
        async def callback(interaction: discord.Interaction):
            try:
                if interaction.user.id != self.user_id:
                    await interaction.response.send_message("❌ هذا ليس لك!", ephemeral=True)
                    return

                # نغلق أزرار الاختيار ثم نبدأ العالم مباشرة (حل جذري بدل طلب /ابدأ مرة أخرى)
                self.selected_world = world_id
                self.stop()

                await interaction.response.defer(ephemeral=True)

                user_id = interaction.user.id
                username = interaction.user.name
                player = await self.bot.get_or_create_player(user_id, username)

                can_access, message = self.bot.can_access_world(player, world_id)
                if not can_access:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="🔒 عالم مقفل",
                            description=message,
                            color=self.bot.world_colors["warning"]
                        ),
                        ephemeral=True
                    )
                    return

                # تحديث بيانات بداية العالم
                await self.bot.db.update_player(user_id, {"current_world": world_id})
                start_part_id = self.bot.story_loader.get_start_part(world_id)
                part_data = self.bot.story_loader.get_part(world_id, start_part_id)

                if not part_data:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="❌ خطأ",
                            description="تعذر تحميل بداية العالم. حاول مرة أخرى.",
                            color=self.bot.world_colors["error"]
                        ),
                        ephemeral=True
                    )
                    return

                await self.bot.db.update_player(user_id, {f"{world_id}_part": start_part_id})
                await self.bot.db.save_session(user_id, start_part_id)

                updated_player = await self.bot.db.get_player(user_id)

                # Embed تمهيدي
                intro_embed = discord.Embed(
                    title=f"{self.bot.get_world_emoji(world_id)} تم اختيار {self.bot.get_world_name(world_id)}",
                    description="✅ تم بدء القصة تلقائياً.",
                    color=self.bot.get_world_color(world_id)
                )
                intro_embed.set_image(url=self.bot.get_world_divider(world_id))
                await interaction.followup.send(embed=intro_embed, ephemeral=True)

                # إرسال القصة مع الأزرار في القناة الحالية
                story_embed = self.bot.create_game_embed(world_id, part_data, updated_player)
                story_view = PersistentStoryView(self.bot, user_id, world_id, part_data)
                guild_id = interaction.guild.id if interaction.guild else None
                channel = interaction.channel
                channel_id = getattr(channel, "id", None)

                channel_failure_reason: Optional[str] = None
                if channel is None or not hasattr(channel, "send"):
                    channel_failure_reason = "channel_missing_or_not_sendable"
                elif interaction.guild:
                    me = interaction.guild.me or interaction.client.user
                    permissions = channel.permissions_for(me) if me else None
                    if permissions is None:
                        channel_failure_reason = "permissions_unavailable"
                    elif not permissions.send_messages:
                        channel_failure_reason = "missing_send_messages_permission"
                    elif not permissions.embed_links:
                        channel_failure_reason = "missing_embed_links_permission"

                if channel_failure_reason is None:
                    try:
                        await channel.send(embed=story_embed, view=story_view)
                    except Exception as send_error:
                        _log_exception_with_context(
                            error=send_error,
                            event="world_select_channel_send_failed",
                            source="permissions",
                            interaction=interaction,
                            current_world=world_id,
                            current_part=start_part_id,
                            user_id=user_id,
                        )
                        channel_failure_reason = f"send_failed:{type(send_error).__name__}:{send_error}"

                if channel_failure_reason:
                    logger.warning(
                        "⚠️ تعذر إرسال القصة في القناة الحالية (%s) guild_id=%s channel_id=%s user_id=%s",
                        channel_failure_reason,
                        guild_id,
                        channel_id,
                        interaction.user.id,
                    )
                    await interaction.followup.send(embed=story_embed, view=story_view, ephemeral=True)

                # تعطيل رسالة اختيار العالم القديمة
                try:
                    await interaction.message.edit(view=None)
                except Exception as e:
                    _log_exception_with_context(
                        error=e,
                        event="world_select_disable_old_view_failed",
                        source="permissions",
                        interaction=interaction,
                        current_world=world_id,
                        current_part=locals().get("start_part_id"),
                        user_id=self.user_id,
                    )

            except Exception as e:
                _log_exception_with_context(
                    error=e,
                    event="world_select_callback_failed",
                    source="story_loader",
                    interaction=interaction,
                    current_world=world_id,
                    current_part=locals().get("start_part_id"),
                    user_id=self.user_id,
                )
                err = "❌ حدث خطأ أثناء اختيار العالم، حاول مرة أخرى"
                if interaction.response.is_done():
                    await interaction.followup.send(err, ephemeral=True)
                else:
                    await interaction.response.send_message(err, ephemeral=True)

        return callback
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        message = getattr(self, "message", None)
        if not message:
            return

        timeout_notice = "⏰ انتهت صلاحية الاختيار، استخدم /ابدأ مجددًا"

        try:
            if message.embeds:
                embed = message.embeds[0].copy()
                embed.add_field(name="انتهى الوقت", value=timeout_notice, inline=False)
                await message.edit(embed=embed, view=self)
            else:
                await message.edit(content=timeout_notice, view=self)
        except Exception as e:
            _log_exception_with_context(
                error=e,
                event="world_select_timeout_update_failed",
                source="permissions",
                current_world=None,
                current_part=None,
                user_id=self.user_id,
            )

# ============================================
# تصدير الكلاسات
# ============================================

__all__ = [
    'PersistentStoryView',
    'PersistentViewManager',
    'ConfirmView',
    'PaginatedView',
    'WorldSelectView'
]
