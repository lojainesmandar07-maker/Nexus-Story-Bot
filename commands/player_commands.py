# commands/player_commands.py - أوامر اللاعب الشخصية
# /حالتي, /مستواي, /سمعتي, /إحصائياتي

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
from datetime import datetime

from core.bot import NexusBot
from core.constants import WORLD_EMOJIS, WORLD_NAMES, create_progress_bar
from game.leveling import LevelSystem, ReputationSystem, get_level_color
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit
from utils.helpers import format_time

logger = logging.getLogger(__name__)


class PlayerCommands(commands.Cog):
    """أوامر اللاعب الشخصية"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /حالتي - عرض حالة اللاعب
    # ============================================
    
    @app_commands.command(name="حالتي", description="📊 اعرض حالة مغامرك وإحصائياته")
    @rate_limit("حالتي")
    async def profile_command(self, interaction: discord.Interaction):
        """عرض ملف اللاعب الشخصي"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            # إنشاء لاعب جديد
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # إنشاء ملف اللاعب
        embed = discord.Embed(
            title=f"👤 ملف {interaction.user.name}",
            color=get_level_color(player.get("level", 1))
        )
        
        # صورة اللاعب
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        # معلومات أساسية
        current_world = player.get("current_world", "fantasy")
        
        embed.add_field(
            name="📋 معلومات أساسية",
            value=(
                f"**المستوى:** {player.get('level', 1)} - {LevelSystem.get_title(player.get('level', 1))}\n"
                f"**الخبرة:** {player.get('xp', 0)} XP\n"
                f"**العالم الحالي:** {WORLD_EMOJIS[current_world]} {WORLD_NAMES[current_world]}\n"
                f"**عدد القرارات:** {player.get('choices_count', 0)}"
            ),
            inline=False
        )
        
        # شريط تقدم المستوى
        level_info = LevelSystem.get_level_info(player.get("xp", 0))
        if not level_info["is_max"]:
            progress_bar = level_info["progress_bar"]
            embed.add_field(
                name="📈 تقدم المستوى",
                value=f"{progress_bar} {level_info['xp_in_level']}/{level_info['xp_needed']} XP",
                inline=False
            )
        
        # المتغيرات الأساسية
        embed.add_field(
            name="💎 المتغيرات الأساسية",
            value=(
                f"**الشظايا:** {player.get('shards', 0)} 💎\n"
                f"**الفساد:** {player.get('corruption', 0)}/100 {create_progress_bar(player.get('corruption', 0), 100, 5)}\n"
                f"**الغموض:** {player.get('mystery', 0)}/100 🔮\n"
                f"**السمعة:** {player.get('reputation', 0)} ⭐"
            ),
            inline=True
        )
        
        # المتغيرات الخاصة بالعالم الحالي
        special_vars = []
        if current_world == "fantasy":
            special_vars.append(f"**قوة فانتازيا:** {player.get('fantasy_power', 0)}/100 ✨")
        elif current_world == "retro":
            special_vars.append(f"**الذكريات:** {player.get('memories', 0)}/100 📜")
        elif current_world == "future":
            special_vars.append(f"**مستوى التكنولوجيا:** {player.get('tech_level', 0)}/100 ⚙️")
        elif current_world == "alternate":
            special_vars.append(f"**الهوية:** {player.get('identity', 0)}/100 🌀")
        
        special_vars.append(f"**ثقة أرين:** {player.get('trust_aren', 0)}/100 🤝")
        
        embed.add_field(
            name="✨ متغيرات خاصة",
            value="\n".join(special_vars),
            inline=True
        )
        
        # استقرار العالم
        stability = player.get("world_stability", 100)
        stability_bar = create_progress_bar(stability, 100, 5)
        embed.add_field(
            name="🌍 استقرار العالم",
            value=f"{stability_bar} {stability}%",
            inline=False
        )
        
        # التوجه
        alignment = player.get("alignment", "Gray")
        align_emoji = {"Light": "✨", "Gray": "⚪", "Dark": "🌑"}.get(alignment, "⚪")
        embed.add_field(name="⚖️ التوجه", value=f"{align_emoji} {alignment}", inline=True)
        
        # آخر نشاط
        last_active = player.get("last_active", "")
        if last_active:
            try:
                last = datetime.fromisoformat(last_active)
                now = datetime.now()
                diff = now - last
                
                if diff.days > 0:
                    activity = f"منذ {diff.days} يوم"
                elif diff.seconds > 3600:
                    activity = f"منذ {diff.seconds // 3600} ساعة"
                else:
                    activity = f"منذ {diff.seconds // 60} دقيقة"
                
                embed.set_footer(text=f"آخر نشاط: {activity}")
            except:
                pass
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /مستواي - عرض تفاصيل المستوى
    # ============================================
    
    @app_commands.command(name="مستواي", description="📈 اعرض تفاصيل مستواك وتقدمك")
    @rate_limit("مستواي")
    async def level_command(self, interaction: discord.Interaction):
        """عرض معلومات المستوى بالتفصيل"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # الحصول على معلومات المستوى
        level_info = LevelSystem.get_stats(player)
        
        embed = discord.Embed(
            title=f"📈 مستوى {interaction.user.name}",
            color=get_level_color(level_info["level"])
        )
        
        # معلومات المستوى الحالي
        embed.add_field(
            name="🎯 المستوى الحالي",
            value=(
                f"**المستوى:** {level_info['level']}\n"
                f"**اللقب:** {level_info['title']}\n"
                f"**إجمالي الخبرة:** {level_info['current_xp']} XP"
            ),
            inline=True
        )
        
        # التقدم
        if not level_info["is_max"]:
            embed.add_field(
                name="📊 التقدم",
                value=(
                    f"{level_info['progress_bar']}\n"
                    f"**في المستوى:** {level_info['xp_in_level']} / {level_info['xp_needed']} XP\n"
                    f"**النسبة:** {level_info['percentage']:.1f}%"
                ),
                inline=True
            )
        else:
            embed.add_field(
                name="🌟 أقصى مستوى",
                value="وصلت إلى أعلى مستوى! تهانينا!",
                inline=True
            )
        
        # مضاعف الخبرة
        multiplier = level_info["xp_multiplier"]
        embed.add_field(
            name="⚡ مضاعف الخبرة",
            value=f"x{multiplier}",
            inline=False
        )
        
        # المستوى التالي مع مكافأة
        next_milestone = level_info["next_milestone"]
        if next_milestone["level"]:
            reward = next_milestone["reward"]
            reward_text = []
            
            if reward.title:
                reward_text.append(f"• لقب: {reward.title}")
            if reward.items:
                for item in reward.items:
                    reward_text.append(f"• عنصر: {item.get('name', '')} x{item.get('quantity', 1)}")
            if reward.shards_bonus:
                reward_text.append(f"• شظايا: +{reward.shards_bonus}")
            if reward.xp_bonus:
                reward_text.append(f"• خبرة: +{reward.xp_bonus}")
            if reward.unlock_world:
                world_name = WORLD_NAMES.get(reward.unlock_world, reward.unlock_world)
                reward_text.append(f"• فتح عالم: {world_name}")
            
            embed.add_field(
                name=f"🎁 المستوى {next_milestone['level']} - {next_milestone['title']}",
                value="\n".join(reward_text) or "مكافأة غامضة",
                inline=False
            )
        
        # مكافآت المستويات القادمة
        future_rewards = []
        for level in range(level_info["level"] + 1, min(level_info["level"] + 4, 16)):
            reward = LevelSystem.get_level_reward(level)
            if reward:
                future_rewards.append(f"المستوى {level}: {reward.title or 'مكافأة'}")
        
        if future_rewards:
            embed.add_field(
                name="🔜 المكافآت القادمة",
                value="\n".join(future_rewards),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /سمعتي - عرض سمعة اللاعب
    # ============================================
    
    @app_commands.command(name="سمعتي", description="⭐ اعرض سمعتك وتأثيرها")
    @rate_limit("سمعتي")
    async def reputation_command(self, interaction: discord.Interaction):
        """عرض معلومات السمعة"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        reputation = player.get("reputation", 0)
        effects = ReputationSystem.get_effects(reputation)
        
        embed = discord.Embed(
            title=f"⭐ سمعة {interaction.user.name}",
            color=0xf1c40f if reputation >= 0 else 0xe74c3c
        )
        
        # شريط السمعة
        rep_bar = ReputationSystem.get_reputation_bar(reputation, 15)
        embed.add_field(
            name="📊 مستوى السمعة",
            value=f"{rep_bar}\n**{effects['name']}**",
            inline=False
        )
        
        # التأثيرات
        effects_text = []
        
        if "discount" in effects and effects["discount"] < 1.0:
            discount = int((1 - effects["discount"]) * 100)
            effects_text.append(f"✅ خصم {discount}% عند الشراء")
        
        if "tax" in effects and effects["tax"] > 1.0:
            tax = int((effects["tax"] - 1) * 100)
            effects_text.append(f"❌ ضريبة إضافية {tax}%")
        
        if "xp_multiplier" in effects:
            if effects["xp_multiplier"] > 1.0:
                effects_text.append(f"⚡ مضاعف خبرة x{effects['xp_multiplier']}")
            elif effects["xp_multiplier"] < 1.0:
                effects_text.append(f"⚠️ خبرة مخفضة x{effects['xp_multiplier']}")
        
        if effects.get("special_dialogues"):
            effects_text.append("💬 حوارات خاصة متاحة")
        
        if effects.get("hostile"):
            effects_text.append("⚔️ الشخصيات قد تهاجمك")
        
        if effects.get("attack_chance"):
            chance = int(effects["attack_chance"] * 100)
            effects_text.append(f"⚠️ فرصة هجوم {chance}%")
        
        if effects.get("bounty"):
            effects_text.append(f"💰 مكافأة على رأسك: {effects['bounty']} قطعة")
        
        if effects.get("hidden_quests"):
            effects_text.append("🔍 مهام سرية متاحة")
        
        embed.add_field(
            name="✨ التأثيرات",
            value="\n".join(effects_text) or "لا توجد تأثيرات خاصة",
            inline=False
        )
        
        # رد فعل الشخصيات
        embed.add_field(
            name="👥 رد فعل الشخصيات",
            value=ReputationSystem.get_reaction(reputation),
            inline=False
        )
        
        # كيفية تحسين السمعة
        if reputation < 50:
            tips = []
            if reputation < 0:
                tips.append("• ساعد المحتاجين لتحسين سمعتك")
                tips.append("• تجنب الهجوم على الأبرياء")
            else:
                tips.append("• أكمل المهام الجانبية")
                tips.append("• ساعد الشخصيات الرئيسية")
            
            embed.add_field(
                name="💡 نصائح لتحسين السمعة",
                value="\n".join(tips),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /إحصائياتي - إحصائيات متقدمة
    # ============================================
    
    @app_commands.command(name="إحصائياتي", description="📊 إحصائيات متقدمة عن رحلتك")
    @rate_limit("إحصائياتي")
    async def stats_command(self, interaction: discord.Interaction):
        """عرض إحصائيات متقدمة"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        embed = discord.Embed(
            title=f"📊 إحصائيات {interaction.user.name}",
            color=0x3498db
        )
        
        # إحصائيات عامة
        embed.add_field(
            name="📋 عام",
            value=(
                f"**تاريخ الانضمام:** {player.get('created_at', 'غير معروف')[:10]}\n"
                f"**وقت اللعب:** {player.get('play_time', 0)} دقيقة\n"
                f"**القرارات:** {player.get('choices_count', 0)}\n"
                f"**الجلسات:** {player.get('sessions_count', 1)}"
            ),
            inline=True
        )
        
        # إحصائيات العوالم
        worlds_completed = 0
        worlds_text = []
        
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            ending = player.get(f"{world_id}_ending")
            if ending:
                worlds_completed += 1
                worlds_text.append(f"{WORLD_EMOJIS[world_id]} ✓")
            else:
                worlds_text.append(f"{WORLD_EMOJIS[world_id]} ○")
        
        embed.add_field(
            name="🌍 العوالم",
            value=f"{' '.join(worlds_text)}\n**المكتملة:** {worlds_completed}/4",
            inline=True
        )
        
        # الحصول على الإنجازات
        achievements = await self.bot.db.get_achievements(user_id)
        
        embed.add_field(
            name="🏆 الإنجازات",
            value=f"**المفتوحة:** {len(achievements)}\n**النقاط:** {len(achievements) * 10}",
            inline=True
        )
        
        # الحصول على المخزون
        inventory = await self.bot.db.get_inventory(user_id)
        total_items = sum(item.get('quantity', 0) for item in inventory)
        
        embed.add_field(
            name="🎒 المخزون",
            value=f"**عناصر فريدة:** {len(inventory)}\n**إجمالي العناصر:** {total_items}",
            inline=True
        )
        
        # التوزيع الزمني (إذا كان متاحاً)
        history = await self.bot.db.get_history(user_id, 50)
        if history:
            # آخر نشاط
            last = history[0].get('timestamp', '')
            if last:
                try:
                    last_dt = datetime.fromisoformat(last)
                    now = datetime.now()
                    diff = now - last_dt
                    
                    if diff.days == 0:
                        last_activity = "اليوم"
                    elif diff.days == 1:
                        last_activity = "أمس"
                    else:
                        last_activity = f"منذ {diff.days} أيام"
                    
                    embed.add_field(
                        name="⏰ آخر نشاط",
                        value=f"{last_activity} في {history[0].get('world', 'غير معروف')}",
                        inline=False
                    )
                except:
                    pass
        
        # أفضل الإنجازات (أعلى XP)
        embed.add_field(
            name="💡 حقائق عن رحلتك",
            value=(
                f"• أكثر عالم لعبت فيه: {self._get_most_played_world(history)}\n"
                f"• متوسط الفساد: {player.get('corruption', 0)}%\n"
                f"• أعلى سمعة وصلت لها: {max(player.get('reputation', 0), 0)}"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /أين_أنا - موقعي الحالي
    # ============================================
    
    @app_commands.command(name="أين_أنا", description="📍 اعرف أين أنت الآن في القصة")
    @rate_limit("أين_أنا")
    async def whereami_command(self, interaction: discord.Interaction):
        """عرض الموقع الحالي في القصة"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            embed = discord.Embed(
                title="❌ لا يوجد تقدم",
                description="لم تبدأ رحلتك بعد! استخدم `/ابدأ` أولاً",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        current_world = player.get("current_world", "fantasy")
        current_part = player.get(f"{current_world}_part", "لم يبدأ")
        
        # الحصول على معلومات الجزء
        part_data = None
        if current_part != "لم يبدأ":
            part_data = self.bot.story_loader.get_part(current_world, current_part)
        
        embed = discord.Embed(
            title=f"📍 موقعك الحالي",
            color=self.bot.get_world_color(current_world)
        )
        
        # معلومات العالم
        world_info = f"{WORLD_EMOJIS[current_world]} **{WORLD_NAMES[current_world]}**"
        
        if part_data:
            title = part_data.get('title', 'جزء غير معروف')
            location = part_data.get('location', 'موقع غير معروف')
            
            embed.add_field(
                name="📖 القصة",
                value=(
                    f"**العالم:** {world_info}\n"
                    f"**الجزء:** {current_part}\n"
                    f"**العنوان:** {title}\n"
                    f"**الموقع:** {location}"
                ),
                inline=False
            )
            
            # وصف مختصر
            desc = part_data.get('text', '')[:200]
            if desc:
                embed.add_field(name="📝 وصف", value=desc + "...", inline=False)
            
            # الخيارات المتاحة
            choices = part_data.get('choices', [])
            if choices:
                choices_text = "\n".join([f"{c.get('emoji', '•')} {c.get('text', '')}" for c in choices[:3]])
                if len(choices) > 3:
                    choices_text += f"\n... و {len(choices)-3} خيارات أخرى"
                
                embed.add_field(name="🔮 خياراتك المتاحة", value=choices_text, inline=False)
        else:
            embed.add_field(
                name="🌍 أنت في",
                value=world_info,
                inline=False
            )
            
            if current_part == "لم يبدأ":
                embed.add_field(
                    name="⚠️ ملاحظة",
                    value="لم تبدأ هذا العالم بعد. استخدم `/استمر` للبدء!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚠️ خطأ",
                    value=f"لم يتم العثور على الجزء {current_part}",
                    inline=False
                )
        
        # شريط التقدم
        if current_part != "لم يبدأ":
            progress = self.bot.story_loader.get_world_progress(current_world, current_part)
            bar = create_progress_bar(int(progress["percentage"]), 100, 12)
            embed.add_field(
                name="📊 تقدمك في العالم",
                value=f"{bar} {progress['percentage']:.1f}% ({progress['current']}/{progress['total']})",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # دوال مساعدة
    # ============================================
    
    def _get_most_played_world(self, history: list) -> str:
        """الحصول على أكثر عالم لعب فيه"""
        if not history:
            return "غير معروف"
        
        world_counts = {}
        for h in history:
            world = h.get('world', 'general')
            world_counts[world] = world_counts.get(world, 0) + 1
        
        if not world_counts:
            return "غير معروف"
        
        most_played = max(world_counts.items(), key=lambda x: x[1])
        world_id = most_played[0]
        
        return WORLD_NAMES.get(world_id, world_id)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(PlayerCommands(bot))
    logger.info("✅ تم تحميل أوامر اللاعب")
