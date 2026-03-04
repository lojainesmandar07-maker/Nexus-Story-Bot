# commands/world_commands.py - أوامر العوالم
# /عوالمي, /تبديل_عالم, /شرح_عالم, /خريطة

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

from core.bot import NexusBot
from core.constants import WORLD_NAMES, WORLD_EMOJIS, WORLD_DESCRIPTIONS, WORLD_UNLOCK_RULES
from story.worlds import world_manager
from ui.embeds import NexusEmbeds
from ui.views import ConfirmView
from utils.rate_limiter import rate_limit

logger = logging.getLogger(__name__)


class WorldCommands(commands.Cog):
    """أوامر العوالم والتنقل بينها"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /عوالمي - عرض العوالم المتاحة
    # ============================================
    
    @app_commands.command(name="عوالمي", description="🌍 اعرض العوالم المتاحة وتقدمك فيها")
    @rate_limit("عوالمي")
    async def worlds_command(self, interaction: discord.Interaction):
        """عرض كل العوالم وتقدم اللاعب فيها"""

        # منع خطأ: The application did not respond للأوامر التي قد تتأخر
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            # إذا كان اللاعب جديداً، أنشئ له ملف
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # إنشاء رسالة العوالم
        embed = discord.Embed(
            title="🌍 رحلتك في النيكسس",
            description="اختر عالمك واستمر في المغامرة",
            color=self.bot.world_colors["general"]
        )
        
        # ترتيب العوالم
        worlds_order = ["fantasy", "retro", "future", "alternate"]
        
        for world_id in worlds_order:
            world_name = WORLD_NAMES.get(world_id, world_id)
            world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
            
            # التحقق من حالة العالم
            can_access, message = self.bot.can_access_world(player, world_id)
            
            # التقدم في العالم
            current_part = player.get(f"{world_id}_part")
            ending = player.get(f"{world_id}_ending")
            
            if ending:
                progress = f"✅ **مكتمل** - النهاية: {ending}"
                status_emoji = "✅"
            elif current_part and current_part != "لم يبدأ" and current_part != f"{world_id.upper()}_01":
                # حساب التقدم التقريبي
                progress_info = self.bot.story_loader.get_world_progress(world_id, current_part)
                percentage = progress_info["percentage"]
                
                # شريط تقدم بسيط
                bar_length = 10
                filled = int(bar_length * percentage / 100)
                bar = "🟪" * filled + "⬜" * (bar_length - filled)
                
                progress = f"📖 **في التقدم**\n{bar} {percentage:.1f}%"
                status_emoji = "📖"
            elif current_part == f"{world_id.upper()}_01" or current_part == "لم يبدأ":
                progress = "⏳ **لم يبدأ**"
                status_emoji = "⏳"
            else:
                progress = "❓ **غير معروف**"
                status_emoji = "❓"
            
            # حالة القفل
            if world_id == "fantasy":
                lock_status = "✅ متاح للجميع"
            else:
                if can_access:
                    lock_status = "✅ **مفتوح** - يمكنك الدخول"
                else:
                    lock_status = f"🔒 **مقفل** - {message}"
            
            # إضافة إلى الرسالة
            embed.add_field(
                name=f"{status_emoji} {world_emoji} **{world_name}**",
                value=f"{progress}\n{lock_status}",
                inline=False
            )
        
        # إحصائيات عامة
        worlds_completed = 0
        for world_id in worlds_order:
            if player.get(f"{world_id}_ending"):
                worlds_completed += 1
        
        embed.set_footer(text=f"أكملت {worlds_completed}/4 عوالم • استخدم /تبديل_عالم للتنقل")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /تبديل_عالم - تغيير العالم الحالي
    # ============================================
    
    @app_commands.command(name="تبديل_عالم", description="🔄 بدّل بين العوالم المتاحة")
    @app_commands.describe(
        العالم="اختر العالم الذي تريد التبديل إليه"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate")
    ])
    @rate_limit("تبديل_عالم")
    async def switch_world_command(
        self,
        interaction: discord.Interaction,
        العالم: str
    ):
        """التبديل بين العوالم"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            embed = discord.Embed(
                title="❌ لا يوجد تقدم",
                description="لم تبدأ رحلتك بعد! استخدم `/ابدأ` أولاً",
                color=self.bot.world_colors["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        world_id = العالم
        current_world = player.get("current_world", "fantasy")
        
        # إذا كان نفس العالم الحالي
        if world_id == current_world:
            embed = discord.Embed(
                title="ℹ️ نفس العالم",
                description=f"أنت بالفعل في {WORLD_EMOJIS[world_id]} **{WORLD_NAMES[world_id]}**",
                color=self.bot.world_colors["info"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من إمكانية الدخول
        can_access, message = self.bot.can_access_world(player, world_id)
        
        if not can_access:
            embed = discord.Embed(
                title="🔒 عالم مقفل",
                description=message,
                color=self.bot.world_colors["warning"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تحديث العالم الحالي
        await self.bot.db.update_player(user_id, {"current_world": world_id})
        
        embed = discord.Embed(
            title="✅ تم التبديل",
            description=f"أنت الآن في {WORLD_EMOJIS[world_id]} **{WORLD_NAMES[world_id]}**\nاستخدم `/استمر` لمتابعة رحلتك",
            color=self.bot.get_world_color(world_id)
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /شرح_عالم - شرح مفصل لعالم معين
    # ============================================
    
    @app_commands.command(name="شرح_عالم", description="📚 شرح مفصل لعالم معين")
    @app_commands.describe(
        العالم="اختر العالم الذي تريد شرحه"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate")
    ])
    @rate_limit("شرح_عالم")
    async def world_info_command(
        self,
        interaction: discord.Interaction,
        العالم: str
    ):
        """شرح مفصل لعالم معين"""
        
        world_id = العالم
        
        # الحصول على معلومات العالم
        world_class = world_manager.get_world(world_id)
        
        if not world_class:
            embed = discord.Embed(
                title="❌ خطأ",
                description="عالم غير موجود",
                color=self.bot.world_colors["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # إنشاء رسالة الشرح
        embed = discord.Embed(
            title=f"{world_class.EMOJI} {world_class.NAME}",
            description=world_class.DESCRIPTION,
            color=world_class.COLOR
        )
        
        # معلومات أساسية
        embed.add_field(
            name="📊 معلومات أساسية",
            value=(
                f"**عدد الأجزاء:** {world_class.TOTAL_PARTS}\n"
                f"**عدد النهايات:** {len(world_class.ENDINGS)}\n"
                f"**متغيرات خاصة:** {', '.join(world_class.SPECIAL_VARS)}"
            ),
            inline=False
        )
        
        # النهايات
        endings_text = ""
        for ending_id, ending in world_class.ENDINGS.items():
            ending_type = ending.type
            type_emoji = {
                "light": "✨", 
                "dark": "🌑", 
                "gray": "⚖️", 
                "secret": "🔮"
            }.get(ending_type, "🎬")
            
            endings_text += f"{type_emoji} **{ending.name}** - {ending.description}\n"
        
        embed.add_field(name="🎬 النهايات", value=endings_text or "لا توجد", inline=False)
        
        # الشخصيات الرئيسية (أول 5)
        chars_text = ""
        for i, (char_id, char) in enumerate(list(world_class.CHARACTERS.items())[:5]):
            chars_text += f"{char.emoji} **{char.name}** - {char.role}\n"
        
        if chars_text:
            embed.add_field(name="👥 شخصيات رئيسية", value=chars_text, inline=True)
        
        # المواقع الرئيسية (أول 5)
        locs_text = ""
        for i, (loc_id, loc) in enumerate(list(world_class.LOCATIONS.items())[:5]):
            locs_text += f"{loc.emoji} **{loc.name}**\n"
        
        if locs_text:
            embed.add_field(name="📍 مواقع رئيسية", value=locs_text, inline=True)
        
        # متطلبات الدخول
        rules = WORLD_UNLOCK_RULES.get(world_id, {})
        if world_id == "fantasy":
            req_text = "✅ متاح للجميع"
        else:
            prev_world = {
                "retro": "عالم الفانتازيا",
                "future": "عالم الماضي",
                "alternate": "عالم المستقبل"
            }.get(world_id, "غير معروف")
            
            req_level = rules.get("required_level", 1)
            req_text = f"🔓 يتطلب:\n• إكمال {prev_world}\n• المستوى {req_level}"
        
        embed.add_field(name="🚪 متطلبات الدخول", value=req_text, inline=False)
        
        # عناصر خاصة بالعالم
        if hasattr(world_class, 'SPECIAL_ITEMS') and world_class.SPECIAL_ITEMS:
            items_text = ""
            for item_id, item in list(world_class.SPECIAL_ITEMS.items())[:3]:
                items_text += f"{item.get('emoji', '📦')} **{item.get('name', item_id)}**\n"
            
            if items_text:
                embed.add_field(name="🎁 عناصر خاصة", value=items_text, inline=True)
        
        embed.set_image(url=self.bot.get_world_divider(world_id))
        embed.set_footer(text=f"الترتيب: {world_class.ORDER} • استخدم /ابدأ {world_id} لبدء المغامرة")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /خريطة - عرض خريطة العالم
    # ============================================
    
    @app_commands.command(name="خريطة", description="🗺️ اعرض خريطة العوالم ومواقعك")
    @rate_limit("خريطة")
    async def map_command(self, interaction: discord.Interaction):
        """عرض خريطة العوالم"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        current_world = player.get("current_world", "fantasy")
        
        # إنشاء خريطة نصية
        map_lines = []
        map_lines.append("```")
        map_lines.append("            🌌 فضاء النيكسس 🌌")
        map_lines.append("")
        map_lines.append("        [🌀] ← [🤖] ← [📜] ← [🌲]")
        map_lines.append("         الواقع    المستقبل   الماضي   الفانتازيا")
        map_lines.append("           البديل")
        map_lines.append("")
        map_lines.append("              ↓         ↓         ↓         ↓")
        map_lines.append("           [🔮]      [⚡]      [⏳]      [✨]")
        map_lines.append("          نهايات    نهايات    نهايات    نهايات")
        map_lines.append("            4         3         3         3")
        map_lines.append("```")
        
        # خريطة مواقع العالم الحالي
        world_class = world_manager.get_world(current_world)
        current_part = player.get(f"{current_world}_part", "لم يبدأ")
        
        map_lines.append(f"\n**📍 موقعك الحالي:** {WORLD_EMOJIS[current_world]} {WORLD_NAMES[current_world]}")
        
        if current_part != "لم يبدأ" and world_class:
            # البحث عن الموقع التقريبي
            map_lines.append(f"📖 **الجزء:** {current_part}")
            
            # عرض بعض المواقع في هذا العالم
            map_lines.append("\n**🗺️ أبرز المواقع في هذا العالم:**")
            for i, (loc_id, loc) in enumerate(list(world_class.LOCATIONS.items())[:5]):
                marker = "📍" if i == 0 else "   "
                map_lines.append(f"{marker} {loc.emoji} **{loc.name}**")
        
        # معلومات إضافية
        embed = discord.Embed(
            title="🗺️ خريطة النيكسس",
            description="\n".join(map_lines),
            color=self.bot.get_world_color(current_world)
        )
        
        # إحصائيات سريعة
        worlds_completed = 0
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            if player.get(f"{world_id}_ending"):
                worlds_completed += 1
        
        embed.add_field(
            name="📊 إحصائيات رحلتك",
            value=(
                f"**العوالم المكتملة:** {worlds_completed}/4\n"
                f"**العالم الحالي:** {WORLD_EMOJIS[current_world]} {WORLD_NAMES[current_world]}\n"
                f"**المستوى:** {player.get('level', 1)}"
            ),
            inline=False
        )
        
        embed.set_footer(text="السهم يشير إلى ترتيب فتح العوالم")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /ترتيب_العوالم - عرض ترتيب فتح العوالم
    # ============================================
    
    @app_commands.command(name="ترتيب_العوالم", description="🔓 اعرض ترتيب فتح العوالم")
    @rate_limit("ترتيب_العوالم")
    async def world_order_command(self, interaction: discord.Interaction):
        """عرض ترتيب فتح العوالم"""
        
        embed = discord.Embed(
            title="🔓 ترتيب فتح العوالم",
            description="لكل عالم متطلباته الخاصة لفتحه",
            color=self.bot.world_colors["general"]
        )
        
        worlds_order = ["fantasy", "retro", "future", "alternate"]
        
        for i, world_id in enumerate(worlds_order, 1):
            world_name = WORLD_NAMES.get(world_id, world_id)
            world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
            rules = WORLD_UNLOCK_RULES.get(world_id, {})
            
            if world_id == "fantasy":
                requirement = "✅ متاح من البداية"
            else:
                prev_world = {
                    "retro": "عالم الفانتازيا",
                    "future": "عالم الماضي",
                    "alternate": "عالم المستقبل"
                }.get(world_id, "")
                
                req_level = rules.get("required_level", 1)
                requirement = f"• أكمل {prev_world}\n• المستوى {req_level}"
            
            embed.add_field(
                name=f"{i}. {world_emoji} {world_name}",
                value=requirement,
                inline=False
            )
        
        # إضافة معلومات عن النهايات
        endings_info = (
            "✨ **نهاية النور** - توجه نحو الخير والسلام\n"
            "🌑 **نهاية الظلام** - استسلم للفساد\n"
            "⚖️ **نهاية التوازن** - حافظ على الوسطية\n"
            "🔮 **نهاية سرية** - اكتشف أسرار النيكسس"
        )
        embed.add_field(name="🎬 أنواع النهايات", value=endings_info, inline=False)
        
        embed.set_footer(text="كلما تقدمت، تفتح عوالم أكثر!")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /إحصائيات_العالم - إحصائيات عن عالم معين
    # ============================================
    
    @app_commands.command(name="إحصائيات_العالم", description="📊 اعرض إحصائيات عن عالم معين")
    @app_commands.describe(
        العالم="اختر العالم الذي تريد إحصائياته"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate")
    ])
    @rate_limit("إحصائيات_العالم")
    async def world_stats_command(
        self,
        interaction: discord.Interaction,
        العالم: str
    ):
        """عرض إحصائيات عن عالم معين"""
        
        world_id = العالم
        
        # الحصول على إحصائيات من قاعدة البيانات
        stats = await self.bot.db.get_world_stats(world_id)
        
        world_class = world_manager.get_world(world_id)
        
        embed = discord.Embed(
            title=f"{world_class.EMOJI} إحصائيات {world_class.NAME}",
            color=world_class.COLOR
        )
        
        # إحصائيات أساسية
        embed.add_field(
            name="👥 اللاعبين",
            value=(
                f"**دخلوا العالم:** {stats.get('total_players', 0)}\n"
                f"**أكملوه:** {stats.get('completed_players', 0)}"
            ),
            inline=True
        )
        
        # متوسط الفساد
        avg_corruption = stats.get('average_corruption', 0)
        embed.add_field(
            name="🌑 متوسط الفساد",
            value=f"{avg_corruption:.1f}%",
            inline=True
        )
        
        # معلومات القصة
        embed.add_field(
            name="📖 القصة",
            value=(
                f"**الأجزاء:** {world_class.TOTAL_PARTS}\n"
                f"**النهايات:** {len(world_class.ENDINGS)}"
            ),
            inline=True
        )
        
        # الشخصيات
        embed.add_field(
            name="👥 الشخصيات",
            value=str(len(world_class.CHARACTERS)),
            inline=True
        )
        
        # المواقع
        embed.add_field(
            name="📍 المواقع",
            value=str(len(world_class.LOCATIONS)),
            inline=True
        )
        
        # العناصر الخاصة
        if hasattr(world_class, 'SPECIAL_ITEMS'):
            embed.add_field(
                name="🎁 العناصر الخاصة",
                value=str(len(world_class.SPECIAL_ITEMS)),
                inline=True
            )
        
        # الخيارات الشائعة (إذا كانت متوفرة)
        popular = stats.get('popular_choices', {})
        if popular:
            choices_text = ""
            for choice, count in list(popular.items())[:3]:
                choices_text += f"• {choice}: {count}\n"
            
            embed.add_field(name="📊 الخيارات الشائعة", value=choices_text, inline=False)
        
        embed.set_footer(text=f"آخر تحديث: {stats.get('updated_at', 'غير معروف')[:10]}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(WorldCommands(bot))
    logger.info("✅ تم تحميل أوامر العوالم")
