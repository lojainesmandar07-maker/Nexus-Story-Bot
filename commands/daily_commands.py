# commands/daily_commands.py - أوامر المكافآت اليومية
# /يومي, /استمرارية, /مكافآتي

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime, timedelta
import random
from typing import Optional, Dict, Any

from core.bot import NexusBot
from core.constants import WORLD_EMOJIS
from game.items import get_item, ALL_ITEMS
from game.leveling import LevelSystem
from ui.views import ConfirmView
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit
from utils.helpers import format_time

logger = logging.getLogger(__name__)


class DailyCommands(commands.Cog):
    """أوامر المكافآت اليومية"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # المكافآت اليومية حسب اليوم
    # ============================================
    
    DAILY_REWARDS = {
        1: {
            "name": "اليوم الأول",
            "emoji": "1️⃣",
            "shards": 5,
            "xp": 50,
            "items": [{"id": "potion", "quantity": 2}],
            "description": "بداية جيدة!"
        },
        2: {
            "name": "اليوم الثاني",
            "emoji": "2️⃣",
            "shards": 5,
            "xp": 75,
            "items": [{"id": "crystal_heart", "quantity": 1}],
            "description": "استمر في المجيء!"
        },
        3: {
            "name": "اليوم الثالث",
            "emoji": "3️⃣",
            "shards": 10,
            "xp": 100,
            "items": [{"id": "potion", "quantity": 3}],
            "description": "أنت ملتزم!"
        },
        4: {
            "name": "اليوم الرابع",
            "emoji": "4️⃣",
            "shards": 10,
            "xp": 125,
            "items": [{"id": "pure_shard", "quantity": 1}],
            "description": "رائع!"
        },
        5: {
            "name": "اليوم الخامس",
            "emoji": "5️⃣",
            "shards": 15,
            "xp": 150,
            "items": [
                {"id": "potion", "quantity": 5},
                {"id": "crystal_heart", "quantity": 1}
            ],
            "description": "مذهل!"
        },
        6: {
            "name": "اليوم السادس",
            "emoji": "6️⃣",
            "shards": 15,
            "xp": 175,
            "items": [{"id": "dark_core", "quantity": 1}],
            "description": "تقترب من الإنجاز!"
        },
        7: {
            "name": "اليوم السابع",
            "emoji": "7️⃣",
            "shards": 25,
            "xp": 200,
            "items": [
                {"id": "pure_shard", "quantity": 2},
                {"id": "crystal_heart", "quantity": 2},
                {"id": "mystery_box", "quantity": 1}
            ],
            "description": "🌟 أسبوع كامل! مكافأة خاصة!"
        }
    }
    
    # مكافآت إضافية للاستمرارية الطويلة
    STREAK_BONUSES = {
        7: {"shards": 10, "items": [{"id": "mystery_box", "quantity": 1}]},
        14: {"shards": 20, "items": [{"id": "pure_shard", "quantity": 2}]},
        21: {"shards": 30, "items": [{"id": "crystal_heart", "quantity": 3}]},
        28: {"shards": 50, "items": [{"id": "mystery_box", "quantity": 3}]},
        30: {"shards": 100, "items": [{"id": "nexus_crystal", "quantity": 1}]}
    }
    
    # ============================================
    # أمر /يومي - المكافأة اليومية
    # ============================================
    
    @app_commands.command(name="يومي", description="🎁 احصل على مكافأتك اليومية")
    @rate_limit("يومي")
    async def daily_command(self, interaction: discord.Interaction):
        """الحصول على المكافأة اليومية"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # التحقق من آخر مكافأة
        last_daily = player.get("last_daily")
        now = datetime.now()
        
        # حساب الاستمرارية الحالية
        current_streak = player.get("daily_streak", 0)
        
        if last_daily:
            try:
                last = datetime.fromisoformat(last_daily)
                next_daily = last + timedelta(days=1)
                
                # إذا كان لا يزال في نفس اليوم
                if now.date() == last.date():
                    next_time = next_daily
                    wait_seconds = (next_time - now).total_seconds()
                    
                    if wait_seconds > 0:
                        hours = int(wait_seconds // 3600)
                        minutes = int((wait_seconds % 3600) // 60)
                        
                        embed = discord.Embed(
                            title="⏳ مكافأة اليوم التالي",
                            description=f"يمكنك الحصول على مكافأتك التالية بعد **{hours} ساعة و {minutes} دقيقة**",
                            color=0xf39c12
                        )
                        
                        # عرض استمراريتك
                        if current_streak > 0:
                            embed.add_field(
                                name="🔥 استمراريتك",
                                value=f"{current_streak} يوم متتالي",
                                inline=False
                            )
                        
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                
                # التحقق من كسر الاستمرارية
                if (now - last).days > 1:
                    # تم كسر الاستمرارية
                    current_streak = 0
                    logger.info(f"👤 {interaction.user.name} كسر استمراريته")
            
            except Exception as e:
                logger.error(f"خطأ في تاريخ المكافأة: {e}")
        
        # حساب يوم الاستمرارية الجديد
        current_streak += 1
        day_in_cycle = ((current_streak - 1) % 7) + 1
        
        # الحصول على مكافأة اليوم
        daily_reward = self.DAILY_REWARDS[day_in_cycle].copy()
        
        # تطبيق مكافأة الاستمرارية الطويلة
        streak_bonus = {}
        for streak_day, bonus in self.STREAK_BONUSES.items():
            if current_streak >= streak_day:
                streak_bonus = bonus
        
        # تجهيز المكافآت
        shards_gain = daily_reward.get("shards", 0) + streak_bonus.get("shards", 0)
        xp_gain = daily_reward.get("xp", 0)
        
        # تحديث اللاعب
        updates = {
            "shards": player.get("shards", 0) + shards_gain,
            "last_daily": now.isoformat(),
            "daily_streak": current_streak
        }
        
        # إضافة الخبرة
        new_xp = player.get("xp", 0) + xp_gain
        old_level = player.get("level", 1)
        new_level = LevelSystem.level_from_xp(new_xp)
        updates["xp"] = new_xp
        
        if new_level > old_level:
            updates["level"] = new_level
        
        await self.bot.db.update_player(user_id, updates)
        
        # إضافة العناصر
        items_gained = []
        
        # عناصر اليوم
        for item in daily_reward.get("items", []):
            item_id = item["id"]
            quantity = item["quantity"]
            item_data = get_item(item_id)
            
            if item_data:
                await self.bot.db.add_to_inventory(
                    user_id,
                    item_id,
                    item_data.name,
                    quantity
                )
                items_gained.append(f"{item_data.emoji} **{item_data.name}** x{quantity}")
        
        # عناصر مكافأة الاستمرارية
        for item in streak_bonus.get("items", []):
            item_id = item["id"]
            quantity = item["quantity"]
            item_data = get_item(item_id)
            
            if item_data:
                await self.bot.db.add_to_inventory(
                    user_id,
                    item_id,
                    item_data.name,
                    quantity
                )
                items_gained.append(f"{item_data.emoji} **{item_data.name}** x{quantity}")
        
        # إنشاء رسالة المكافأة
        embed = discord.Embed(
            title=f"🎁 مكافأة اليوم {day_in_cycle} {daily_reward['emoji']}",
            description=daily_reward["description"],
            color=0xf1c40f
        )
        
        # المكافآت
        rewards_text = []
        
        if shards_gain > 0:
            rewards_text.append(f"💎 **{shards_gain}** شظية")
        
        if xp_gain > 0:
            rewards_text.append(f"🌟 **{xp_gain}** XP")
        
        if items_gained:
            rewards_text.extend(items_gained)
        
        embed.add_field(
            name="📦 حصلت على:",
            value="\n".join(rewards_text) if rewards_text else "لا توجد مكافآت",
            inline=False
        )
        
        # معلومات الاستمرارية
        streak_text = f"🔥 **{current_streak}** يوم متتالي"
        
        # المكافأة القادمة
        next_day = (day_in_cycle % 7) + 1
        next_reward = self.DAILY_REWARDS[next_day]
        
        streak_text += f"\n⏩ غداً: اليوم {next_day} {next_reward['emoji']}"
        
        # المكافأة الخاصة القادمة
        for milestone in [7, 14, 21, 28, 30]:
            if current_streak < milestone:
                days_left = milestone - current_streak
                streak_text += f"\n🎯 بعد {days_left} أيام: مكافأة خاصة للمداومة!"
                break
        
        embed.add_field(name="🔥 استمراريتك", value=streak_text, inline=False)
        
        # زيادة المستوى
        if new_level > old_level:
            embed.add_field(
                name="⬆️ زيادة مستوى!",
                value=f"وصلت إلى المستوى **{new_level}**!",
                inline=False
            )
        
        # إنجاز خاص للمداومة
        if current_streak == 7:
            await self.bot.db.unlock_achievement(
                user_id,
                "daily_devoted",
                "general"
            )
            embed.add_field(
                name="🏆 إنجاز جديد!",
                value="حصلت على إنجاز **المخلص اليومي**!",
                inline=False
            )
        elif current_streak == 30:
            await self.bot.db.unlock_achievement(
                user_id,
                "daily_legend",
                "general"
            )
            embed.add_field(
                name="🏆 إنجاز أسطوري!",
                value="حصلت على إنجاز **أسطورة الاستمرارية**!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /استمرارية - عرض الاستمرارية
    # ============================================
    
    @app_commands.command(name="استمرارية", description="🔥 اعرض استمراريتك اليومية")
    @rate_limit("استمرارية")
    async def streak_command(self, interaction: discord.Interaction):
        """عرض معلومات الاستمرارية"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        current_streak = player.get("daily_streak", 0)
        last_daily = player.get("last_daily")
        
        embed = discord.Embed(
            title=f"🔥 استمرارية {interaction.user.name}",
            color=0xe67e22
        )
        
        # شريط الاستمرارية
        if current_streak > 0:
            # حساب اليوم في الدورة
            day_in_cycle = ((current_streak - 1) % 7) + 1
            
            # إنشاء شريط الأيام السبعة
            streak_bar = ""
            for i in range(1, 8):
                if i < day_in_cycle:
                    streak_bar += "✅"
                elif i == day_in_cycle:
                    streak_bar += "🎁"
                else:
                    streak_bar += "⬜"
            
            embed.add_field(
                name="📅 الأسبوع الحالي",
                value=f"{streak_bar}\nاليوم {day_in_cycle} من 7",
                inline=False
            )
            
            embed.add_field(
                name="🔥 الاستمرارية",
                value=f"**{current_streak}** يوم متتالي",
                inline=True
            )
        else:
            embed.add_field(
                name="📅 لا توجد استمرارية",
                value="لم تحصل على مكافأتك اليومية بعد. استخدم `/يومي` للبدء!",
                inline=False
            )
        
        # آخر مكافأة
        if last_daily:
            try:
                last = datetime.fromisoformat(last_daily)
                next_daily = last + timedelta(days=1)
                now = datetime.now()
                
                if now < next_daily:
                    wait = next_daily - now
                    hours = wait.seconds // 3600
                    minutes = (wait.seconds % 3600) // 60
                    
                    embed.add_field(
                        name="⏳ المكافأة التالية",
                        value=f"بعد {hours} ساعة و {minutes} دقيقة",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🎁 المكافأة التالية",
                        value="متاحة الآن! استخدم `/يومي`",
                        inline=True
                    )
            except:
                pass
        
        # المكافآت القادمة
        if current_streak > 0:
            next_milestones = []
            
            for milestone in [7, 14, 21, 28, 30]:
                if current_streak < milestone:
                    days_left = milestone - current_streak
                    bonus = self.STREAK_BONUSES.get(milestone, {})
                    
                    rewards = []
                    if bonus.get("shards"):
                        rewards.append(f"{bonus['shards']} شظية")
                    if bonus.get("items"):
                        for item in bonus["items"]:
                            item_data = get_item(item["id"])
                            if item_data:
                                rewards.append(f"{item_data.emoji} {item_data.name}")
                    
                    if rewards:
                        next_milestones.append(
                            f"• بعد {days_left} أيام: " + "، ".join(rewards)
                        )
            
            if next_milestones:
                embed.add_field(
                    name="🎯 المكافآت القادمة",
                    value="\n".join(next_milestones),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /مكافآتي - عرض سجل المكافآت
    # ============================================
    
    @app_commands.command(name="مكافآتي", description="📜 اعرض سجل مكافآتك اليومية")
    @rate_limit("مكافآتي")
    async def rewards_history_command(self, interaction: discord.Interaction):
        """عرض سجل المكافآت اليومية"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # هذه ميزة متقدمة تتطلب جدولاً خاصاً للمكافآت
        # للتبسيط، سنعرض آخر 7 أيام من الاستمرارية
        
        current_streak = player.get("daily_streak", 0)
        
        embed = discord.Embed(
            title=f"📜 سجل مكافآت {interaction.user.name}",
            color=0x3498db
        )
        
        if current_streak == 0:
            embed.description = "لم تحصل على أي مكافآت بعد. استخدم `/يومي` للبدء!"
        else:
            # عرض آخر 7 أيام
            history = []
            for i in range(min(7, current_streak)):
                day_num = current_streak - i
                day_in_cycle = ((day_num - 1) % 7) + 1
                reward = self.DAILY_REWARDS[day_in_cycle]
                
                status = "✅" if i == 0 else "✓"
                history.append(f"{status} اليوم {day_num}: {reward['emoji']} {reward['name']}")
            
            embed.add_field(
                name="📆 آخر المكافآت",
                value="\n".join(history),
                inline=False
            )
            
            # إحصائيات
            total_shards = current_streak * 5  # تقريبي
            total_xp = current_streak * 75  # تقريبي
            
            embed.add_field(
                name="📊 إجمالي تقريبي",
                value=(
                    f"**المجموع:** {current_streak} يوم\n"
                    f"**شظايا:** ~{total_shards}\n"
                    f"**خبرة:** ~{total_xp} XP"
                ),
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /تذكير_يومي - تفعيل تذكير يومي
    # ============================================
    
    @app_commands.command(name="تذكير_يومي", description="⏰ فعّل أو عطّل التذكير اليومي")
    @app_commands.describe(
        الحالة="تشغيل أو إيقاف التذكير"
    )
    @app_commands.choices(الحالة=[
        app_commands.Choice(name="✅ تشغيل", value="on"),
        app_commands.Choice(name="❌ إيقاف", value="off")
    ])
    @rate_limit("تذكير_يومي")
    async def daily_reminder_command(
        self,
        interaction: discord.Interaction,
        الحالة: str
    ):
        """تفعيل أو إيقاف التذكير اليومي"""
        
        user_id = interaction.user.id
        
        if الحالة == "on":
            await self.bot.db.set_flag(user_id, "daily_reminder", 1)
            embed = discord.Embed(
                title="✅ تم التفعيل",
                description="سيتم تذكيرك يومياً بالمكافأة!",
                color=0x2ecc71
            )
        else:
            await self.bot.db.set_flag(user_id, "daily_reminder", 0)
            embed = discord.Embed(
                title="❌ تم الإيقاف",
                description="لن يتم تذكيرك بعد الآن",
                color=0xe74c3c
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # مهمة التذكير اليومي (تعمل في الخلفية)
    # ============================================
    
    async def send_daily_reminders(self):
        """إرسال تذكيرات يومية للاعبين"""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            try:
                # التحقق كل ساعة
                await asyncio.sleep(3600)
                
                now = datetime.now()
                # نرسل التذكير في الساعة 12 ظهراً فقط
                if now.hour != 12:
                    continue
                
                logger.info("🔔 جاري إرسال التذكيرات اليومية...")
                
                # هذه الميزة تحتاج إلى قائمة بكل اللاعبين النشطين
                # للتبسيط، لن ننفذها الآن
                
            except Exception as e:
                logger.error(f"❌ خطأ في إرسال التذكيرات: {e}")
    
    # ============================================
    # أمر /إعادة_تعيين_يومي - إعادة تعيين (للمشرفين)
    # ============================================
    
    @app_commands.command(name="إعادة_تعيين_يومي", description="🔄 إعادة تعيين مكافأة لاعب (للمشرفين)")
    @app_commands.describe(
        اللاعب="اللاعب المراد إعادة تعيين مكافأته"
    )
    @rate_limit("إعادة_تعيين_يومي")
    async def reset_daily_command(
        self,
        interaction: discord.Interaction,
        اللاعب: discord.User
    ):
        """إعادة تعيين المكافأة اليومية للاعب (للمشرفين فقط)"""
        
        # التحقق من صلاحيات المشرف
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_id = اللاعب.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            embed = discord.Embed(
                title="❌ لاعب غير موجود",
                description=f"لا يوجد لاعب باسم {اللاعب.mention}",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # طلب تأكيد
        embed = discord.Embed(
            title="⚠️ تأكيد إعادة التعيين",
            description=f"هل تريد إعادة تعيين المكافأة اليومية لـ {اللاعب.mention}؟",
            color=0xf39c12
        )
        
        embed.add_field(
            name="📊 المعلومات الحالية",
            value=(
                f"**الاستمرارية:** {player.get('daily_streak', 0)} يوم\n"
                f"**آخر مكافأة:** {player.get('last_daily', 'لا توجد')[:10] if player.get('last_daily') else 'لا توجد'}"
            ),
            inline=False
        )
        
        async def confirm(interaction: discord.Interaction):
            await self.bot.db.update_player(user_id, {
                "last_daily": None,
                "daily_streak": 0
            })
            
            embed = discord.Embed(
                title="✅ تمت إعادة التعيين",
                description=f"تم إعادة تعيين المكافأة اليومية لـ {اللاعب.mention}",
                color=0x2ecc71
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        async def cancel(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ تم الإلغاء",
                description="تم إلغاء عملية إعادة التعيين",
                color=0x95a5a6
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        view = ConfirmView(interaction.user.id, confirm, cancel)
        await interaction.response.send_message(embed=embed, view=view)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(DailyCommands(bot))
    logger.info("✅ تم تحميل أوامر المكافآت اليومية")
