# commands/achievement_commands.py - أوامر الإنجازات
# /إنجازاتي, /نهاياتي, /إنجاز_عشوائي, /إحصائيات_الإنجازات

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List
import random
from datetime import datetime

from core.bot import NexusBot
from core.constants import WORLD_EMOJIS, WORLD_NAMES
from game.achievements import (
    ALL_ACHIEVEMENTS,
    get_achievements_by_world,
    get_hidden_achievements,
    get_visible_achievements,
    calculate_achievement_progress,
    get_random_achievement,
    Achievement
)
from ui.views import PaginatedView
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit

logger = logging.getLogger(__name__)


class AchievementCommands(commands.Cog):
    """أوامر الإنجازات والنهايات"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /إنجازاتي - عرض الإنجازات
    # ============================================
    
    @app_commands.command(name="إنجازاتي", description="🏆 اعرض إنجازاتك التي حصلت عليها")
    @app_commands.describe(
        العالم="تصفية حسب العالم (اختياري)",
        الصفحة="رقم الصفحة"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate"),
        app_commands.Choice(name="🌟 عام", value="general"),
        app_commands.Choice(name="🔮 كل الإنجازات", value="all")
    ])
    @rate_limit("إنجازاتي")
    async def achievements_command(
        self,
        interaction: discord.Interaction,
        العالم: Optional[str] = "all",
        الصفحة: Optional[int] = 1
    ):
        """عرض الإنجازات التي حصل عليها اللاعب"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # الحصول على إنجازات اللاعب
        user_achievements = await self.bot.db.get_achievements(user_id)
        user_achievement_ids = {a['achievement_id'] for a in user_achievements}
        
        # تصفية حسب العالم
        if العالم != "all":
            all_world_achievements = get_achievements_by_world(العالم)
            achievement_list = [
                ach for ach in all_world_achievements
                if ach.id in user_achievement_ids
            ]
            title_suffix = f"في {WORLD_NAMES.get(العالم, 'العالم')}"
        else:
            # كل الإنجازات
            achievement_list = [
                ach for ach in ALL_ACHIEVEMENTS.values()
                if ach.id in user_achievement_ids
            ]
            title_suffix = ""
        
        # ترتيب حسب التاريخ (الأحدث أولاً)
        achievement_list.sort(
            key=lambda a: next(
                (ua['unlocked_at'] for ua in user_achievements if ua['achievement_id'] == a.id),
                ""
            ),
            reverse=True
        )
        
        if not achievement_list:
            embed = discord.Embed(
                title="🏆 لا توجد إنجازات",
                description="لم تحصل على أي إنجازات بعد. استمر في اللعب لفتح الإنجازات!",
                color=0xffd700
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تقسيم إلى صفحات
        items_per_page = 5
        pages = []
        
        for i in range(0, len(achievement_list), items_per_page):
            page_achievements = achievement_list[i:i + items_per_page]
            
            embed = discord.Embed(
                title=f"🏆 إنجازات {interaction.user.name} {title_suffix}",
                color=0xffd700
            )
            
            for ach in page_achievements:
                # البحث عن تاريخ الفتح
                unlock_info = next(
                    (ua for ua in user_achievements if ua['achievement_id'] == ach.id),
                    None
                )
                
                # تنسيق التاريخ
                date_str = ""
                if unlock_info and unlock_info.get('unlocked_at'):
                    try:
                        dt = datetime.fromisoformat(unlock_info['unlocked_at'])
                        date_str = f" *({dt.strftime('%Y/%m/%d')})*"
                    except:
                        pass
                
                # اسم الإنجاز مع لون حسب الندرة
                name = f"{ach.emoji} **{ach.name}**{date_str}"
                
                # إضافة كلمة "سري" إذا كان مخفياً
                if ach.hidden:
                    name = "🔮 " + name
                
                embed.add_field(
                    name=name,
                    value=f"└ {ach.description} (+{ach.xp_reward} XP)",
                    inline=False
                )
            
            # إحصائيات
            total = len(achievement_list)
            progress = calculate_achievement_progress(user_achievement_ids)
            
            embed.set_footer(
                text=f"صفحة {i//items_per_page + 1}/{(len(achievement_list)-1)//items_per_page + 1} • "
                     f"{len(achievement_list)}/{len(ALL_ACHIEVEMENTS)} إنجازات • {progress['percentage']:.1f}%"
            )
            
            pages.append(embed)
        
        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0])
        else:
            view = PaginatedView(interaction.user.id, pages, timeout=120)
            await interaction.response.send_message(
                embed=pages[الصفحة - 1] if 1 <= الصفحة <= len(pages) else pages[0],
                view=view
            )
    
    # ============================================
    # أمر /نهاياتي - عرض النهايات
    # ============================================
    
    @app_commands.command(name="نهاياتي", description="🎬 اعرض النهايات التي وصلت لها")
    @rate_limit("نهاياتي")
    async def endings_command(self, interaction: discord.Interaction):
        """عرض النهايات التي حصل عليها اللاعب"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        embed = discord.Embed(
            title=f"🎬 نهايات {interaction.user.name}",
            color=0x9b59b6
        )
        
        endings_found = False
        worlds_order = ["fantasy", "retro", "future", "alternate"]
        
        for world_id in worlds_order:
            ending = player.get(f"{world_id}_ending")
            world_name = WORLD_NAMES.get(world_id, world_id)
            world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
            
            if ending:
                endings_found = True
                # تحديد نوع النهاية
                ending_type = "غير معروف"
                type_emoji = "🎬"
                
                if "light" in ending.lower():
                    ending_type = "نور"
                    type_emoji = "✨"
                elif "dark" in ending.lower():
                    ending_type = "ظلام"
                    type_emoji = "🌑"
                elif "gray" in ending.lower() or "balance" in ending.lower():
                    ending_type = "توازن"
                    type_emoji = "⚖️"
                elif "secret" in ending.lower():
                    ending_type = "سرية"
                    type_emoji = "🔮"
                
                embed.add_field(
                    name=f"{world_emoji} {world_name}",
                    value=f"✅ **مكتمل** - {type_emoji} {ending_type}\n`{ending}`",
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"{world_emoji} {world_name}",
                    value="⏳ **لم يكتمل بعد**",
                    inline=True
                )
        
        if not endings_found:
            embed.description = "لم تصل إلى أي نهاية بعد. استمر في اللعب!"
        
        # إحصائيات
        completed_worlds = sum(1 for w in worlds_order if player.get(f"{w}_ending"))
        embed.set_footer(text=f"أكملت {completed_worlds}/4 عوالم")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /إنجاز_عشوائي - عرض إنجاز عشوائي
    # ============================================
    
    @app_commands.command(name="إنجاز_عشوائي", description="🎲 اعرض إنجازاً عشوائياً")
    @app_commands.describe(
        العالم="اختر عالم معين (اختياري)"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate"),
        app_commands.Choice(name="🌟 عام", value="general")
    ])
    @rate_limit("إنجاز_عشوائي")
    async def random_achievement_command(
        self,
        interaction: discord.Interaction,
        العالم: Optional[str] = None
    ):
        """عرض إنجاز عشوائي"""
        
        if العالم:
            achievements = get_achievements_by_world(العالم)
            if not achievements:
                embed = discord.Embed(
                    title="❌ لا توجد إنجازات",
                    description=f"لا توجد إنجازات في {WORLD_NAMES.get(العالم, 'هذا العالم')}",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            achievement = random.choice(achievements)
        else:
            achievement = get_random_achievement()
        
        embed = discord.Embed(
            title=f"🎲 إنجاز عشوائي",
            color=0xffd700
        )
        
        # اسم الإنجاز
        name = f"{achievement.emoji} **{achievement.name}**"
        if achievement.hidden:
            name = "🔮 " + name + " *(سري)*"
        
        embed.add_field(name=name, value=achievement.description, inline=False)
        
        # معلومات إضافية
        world_name = WORLD_NAMES.get(achievement.world, achievement.world)
        world_emoji = WORLD_EMOJIS.get(achievement.world, "🌍")
        
        embed.add_field(
            name="📋 معلومات",
            value=(
                f"**العالم:** {world_emoji} {world_name}\n"
                f"**مكافأة XP:** {achievement.xp_reward}"
            ),
            inline=False
        )
        
        if achievement.item_reward:
            item = achievement.item_reward
            embed.add_field(
                name="🎁 مكافأة خاصة",
                value=f"{item.get('emoji', '📦')} {item.get('name', '')} x{item.get('quantity', 1)}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /إحصائيات_الإنجازات - إحصائيات متقدمة
    # ============================================
    
    @app_commands.command(name="إحصائيات_الإنجازات", description="📊 اعرض إحصائيات الإنجازات")
    @rate_limit("إحصائيات_الإنجازات")
    async def achievement_stats_command(self, interaction: discord.Interaction):
        """عرض إحصائيات متقدمة عن الإنجازات"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # الحصول على إنجازات اللاعب
        user_achievements = await self.bot.db.get_achievements(user_id)
        user_ids = {a['achievement_id'] for a in user_achievements}
        
        # إحصائيات عامة
        progress = calculate_achievement_progress(user_ids)
        
        embed = discord.Embed(
            title=f"📊 إحصائيات إنجازات {interaction.user.name}",
            color=0x3498db
        )
        
        # إحصائيات أساسية
        embed.add_field(
            name="📋 عام",
            value=(
                f"**الإجمالي:** {progress['total']}\n"
                f"**المفتوح:** {progress['unlocked']}\n"
                f"**النسبة:** {progress['percentage']:.1f}%\n"
                f"**نقاط الإنجاز:** {progress['unlocked'] * 10}"
            ),
            inline=True
        )
        
        # الإنجازات المرئية
        embed.add_field(
            name="👁️ المرئية",
            value=(
                f"**الإجمالي:** {progress['visible_total']}\n"
                f"**المفتوح:** {progress['visible_unlocked']}\n"
                f"**النسبة:** {progress['visible_percentage']:.1f}%"
            ),
            inline=True
        )
        
        # الإنجازات السرية
        hidden_total = len(get_hidden_achievements())
        embed.add_field(
            name="🔮 السرية",
            value=(
                f"**الإجمالي:** {hidden_total}\n"
                f"**المفتوح:** {progress['hidden_unlocked']}\n"
                f"**النسبة:** {(progress['hidden_unlocked']/hidden_total*100) if hidden_total else 0:.1f}%"
            ),
            inline=True
        )
        
        # توزيع الإنجازات حسب العالم
        worlds_stats = []
        worlds_order = ["fantasy", "retro", "future", "alternate", "general"]
        
        for world_id in worlds_order:
            world_achievements = get_achievements_by_world(world_id)
            world_unlocked = len([a for a in world_achievements if a.id in user_ids])
            total = len(world_achievements)
            
            if total > 0:
                percentage = world_unlocked / total * 100
                bar_length = 10
                filled = int(bar_length * percentage / 100)
                bar = "🟪" * filled + "⬜" * (bar_length - filled)
                
                world_name = WORLD_NAMES.get(world_id, "عام")
                world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
                
                worlds_stats.append(
                    f"{world_emoji} **{world_name}:** {bar} {world_unlocked}/{total}"
                )
        
        if worlds_stats:
            embed.add_field(
                name="🌍 توزيع العوالم",
                value="\n".join(worlds_stats),
                inline=False
            )
        
        # أحدث 3 إنجازات
        if user_achievements:
            recent = sorted(user_achievements, key=lambda x: x['unlocked_at'], reverse=True)[:3]
            recent_text = []
            
            for r in recent:
                ach = ALL_ACHIEVEMENTS.get(r['achievement_id'])
                if ach:
                    try:
                        dt = datetime.fromisoformat(r['unlocked_at'])
                        date = dt.strftime('%Y/%m/%d')
                    except:
                        date = '?'
                    
                    recent_text.append(f"{ach.emoji} **{ach.name}** - {date}")
            
            if recent_text:
                embed.add_field(
                    name="🆕 أحدث الإنجازات",
                    value="\n".join(recent_text),
                    inline=False
                )
        
        # الإنجاز التالي (أعلى نسبة مئوية من الإنجازات غير المفتوحة)
        # هذه ميزة متقدمة تحتاج لحساب التقدم في كل إنجاز
        
        embed.set_footer(text="استمر في اللعب لفتح المزيد من الإنجازات!")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /إنجاز_تفصيلي - تفاصيل إنجاز معين
    # ============================================
    
    @app_commands.command(name="إنجاز_تفصيلي", description="🔍 اعرض تفاصيل إنجاز معين")
    @app_commands.describe(
        الإنجاز="معرف الإنجاز أو جزء من اسمه"
    )
    @rate_limit("إنجاز_تفصيلي")
    async def achievement_detail_command(
        self,
        interaction: discord.Interaction,
        الإنجاز: str
    ):
        """عرض تفاصيل إنجاز معين"""
        
        # البحث عن الإنجاز
        search = الإنجاز.lower()
        found = None
        
        # البحث بالمعرف أولاً
        if search in ALL_ACHIEVEMENTS:
            found = ALL_ACHIEVEMENTS[search]
        else:
            # البحث في الأسماء
            for ach in ALL_ACHIEVEMENTS.values():
                if search in ach.name.lower() or search in ach.description.lower():
                    found = ach
                    break
        
        if not found:
            embed = discord.Embed(
                title="❌ إنجاز غير موجود",
                description=f"لم أجد إنجازاً باسم '{الإنجاز}'",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق مما إذا كان اللاعب قد حصل عليه
        user_id = interaction.user.id
        has_achievement = await self.bot.db.has_achievement(user_id, found.id)
        
        embed = discord.Embed(
            title=f"{found.emoji} {found.name}",
            description=found.description,
            color=0xffd700 if has_achievement else 0x95a5a6
        )
        
        # معلومات إضافية
        world_name = WORLD_NAMES.get(found.world, found.world)
        world_emoji = WORLD_EMOJIS.get(found.world, "🌍")
        
        embed.add_field(
            name="📋 معلومات",
            value=(
                f"**العالم:** {world_emoji} {world_name}\n"
                f"**مكافأة XP:** {found.xp_reward}\n"
                f"**الحالة:** {'✅ مكتمل' if has_achievement else '⏳ غير مكتمل'}\n"
                f"**سري:** {'🔮 نعم' if found.hidden else '❌ لا'}"
            ),
            inline=False
        )
        
        if found.item_reward:
            item = found.item_reward
            embed.add_field(
                name="🎁 مكافأة خاصة",
                value=f"{item.get('emoji', '📦')} {item.get('name', '')} x{item.get('quantity', 1)}",
                inline=False
            )
        
        if found.requires_all_endings:
            embed.add_field(
                name="⚠️ متطلب خاص",
                value="يتطلب الحصول على كل النهايات في هذا العالم",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /أندر_الإنجازات - أندر الإنجازات
    # ============================================
    
    @app_commands.command(name="أندر_الإنجازات", description="🏆 اعرض أندر الإنجازات في السيرفر")
    @rate_limit("أندر_الإنجازات")
    async def rarest_achievements_command(self, interaction: discord.Interaction):
        """عرض أندر الإنجازات (الأقل حصولاً)"""
        
        # هذه ميزة متقدمة تحتاج إحصائيات من كل اللاعبين
        # للتبسيط، نعرض إنجازات عشوائية من الإنجازات السرية
        
        embed = discord.Embed(
            title="🏆 أندر الإنجازات",
            description="الإنجازات الأكثر ندرة في النيكسس",
            color=0x9b59b6
        )
        
        # اختيار 5 إنجازات سرية عشوائية
        hidden = get_hidden_achievements()
        random.shuffle(hidden)
        
        for ach in hidden[:5]:
            embed.add_field(
                name=f"{ach.emoji} **{ach.name}**",
                value=f"└ {ach.description}",
                inline=False
            )
        
        embed.set_footer(text="هذه الإنجازات نادرة جداً! هل تستطيع الحصول عليها؟")
        
        await interaction.response.send_message(embed=embed)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(AchievementCommands(bot))
    logger.info("✅ تم تحميل أوامر الإنجازات")
