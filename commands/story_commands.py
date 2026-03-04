# commands/story_commands.py - أوامر القصة الرئيسية
# /ابدأ, /استمر, /قراراتي, /تاريخي

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
import random

from core.bot import NexusBot
from core.constants import WORLD_NAMES, WORLD_EMOJIS, SYSTEM_MESSAGES
from ui.views import PersistentStoryView, WorldSelectView, ConfirmView
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit
from utils.helpers import format_time

logger = logging.getLogger(__name__)


class StoryCommands(commands.Cog):
    """أوامر القصة الرئيسية"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /ابدأ - بدء رحلة جديدة
    # ============================================
    
    @app_commands.command(name="ابدأ", description="🚀 ابدأ رحلتك في عالم النيكسس")
    @app_commands.describe(
        العالم="اختر العالم الذي تريد البدء فيه (اختياري)"
    )
    @app_commands.choices(العالم=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate")
    ])
    @rate_limit("ابدأ")
    async def start_command(
        self,
        interaction: discord.Interaction,
        العالم: Optional[str] = None
    ):
        """بدء رحلة جديدة في عالم معين"""

        # منع خطأ: The application did not respond
        await interaction.response.defer(ephemeral=True)

        try:
            # التحقق من القناة المناسبة
            if not await self._check_channel(interaction):
                return

            user_id = interaction.user.id
            username = interaction.user.name

            # الحصول على بيانات اللاعب
            player = await self.bot.db.get_player(user_id)

            # إذا كان اللاعب جديداً
            if not player:
                await self.bot.db.create_player(user_id, username)
                player = await self.bot.db.get_player(user_id)

                embed = discord.Embed(
                    title="✨ مرحباً بك في النيكسس!",
                    description=(
                        "أهلاً بك أيها المغامر الجديد!\n\n"
                        "**📖 ما هو النيكسس؟**\n"
                        "هو عالم من 4 عوالم مترابطة، كل عالم له قصته وشخصياته ونهاياته.\n\n"
                        "**🎮 كيف تلعب؟**\n"
                        "• ستظهر لك أزرار تمثل الخيارات المتاحة\n"
                        "• كل قرار يغير مسار القصة ويؤثر على شخصيتك\n"
                        "• راقب الفساد - لا تدعه يسيطر عليك\n"
                        "• اجمع الشظايا والإنجازات لتصبح أقوى\n\n"
                        "**🌍 ابدأ الآن باختيار عالمك الأول!**"
                    ),
                    color=self.bot.world_colors["general"]
                )
                embed.set_image(url=self.bot.world_dividers["general"])
                await interaction.followup.send(embed=embed, ephemeral=True)

                # عرض اختيار العوالم
                await self._show_world_selection(interaction, player)
                return

            # إذا كان لديه تقدم سابق وعين عالماً محدداً
            if العالم:
                await self._start_world(interaction, العالم, player)
            else:
                # عرض العوالم المتاحة
                await self._show_world_selection(interaction, player)

        except Exception as e:
            logger.error(f"Error in start_command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ حدث خطأ تقني أثناء بدء الرحلة، يرجى المحاولة لاحقاً.",
                ephemeral=True
            )

    async def _send_interaction_message(
        self,
        interaction: discord.Interaction,
        *,
        content: Optional[str] = None,
        embed: Optional[discord.Embed] = None,
        view: Optional[discord.ui.View] = None,
        ephemeral: bool = False
    ):
        """إرسال رسالة للتفاعل سواء كان response أو followup بحسب حالة التفاعل"""
        if interaction.response.is_done():
            return await interaction.followup.send(content=content, embed=embed, view=view, ephemeral=ephemeral)
        return await interaction.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)

    async def _show_world_selection(self, interaction: discord.Interaction, player: dict):
        """عرض أزرار اختيار العالم"""
        
        # تحديد العوالم المتاحة
        available_worlds = []
        
        # عالم الفانتازيا متاح دائماً
        available_worlds.append("fantasy")
        
        # التحقق من فتح العوالم الأخرى
        if player.get("fantasy_ending"):
            available_worlds.append("retro")
        if player.get("retro_ending"):
            available_worlds.append("future")
        if player.get("future_ending"):
            available_worlds.append("alternate")
        
        # إنشاء أزرار اختيار العالم
        view = WorldSelectView(self.bot, interaction.user.id, available_worlds)
        
        embed = discord.Embed(
            title="🌍 اختر عالمك",
            description="اختر العالم الذي تريد المغامرة فيه:",
            color=self.bot.world_colors["general"]
        )
        
        for world_id in available_worlds:
            status = "✅ متاح"
            if world_id == "fantasy":
                status = "✅ متاح للجميع"
            elif world_id == "retro" and player.get("fantasy_ending"):
                status = f"✅ مفتوح (أكملت الفانتازيا)"
            elif world_id == "future" and player.get("retro_ending"):
                status = f"✅ مفتوح (أكملت الماضي)"
            elif world_id == "alternate" and player.get("future_ending"):
                status = f"✅ مفتوح (أكملت المستقبل)"
            
            embed.add_field(
                name=f"{WORLD_EMOJIS[world_id]} {WORLD_NAMES[world_id]}",
                value=status,
                inline=False
            )
        
        await self._send_interaction_message(interaction, embed=embed, view=view)
    
    async def _start_world(self, interaction: discord.Interaction, world_id: str, player: dict):
        """بدء عالم معين"""
        
        # التحقق من إمكانية دخول العالم
        can_access, message = self.bot.can_access_world(player, world_id)
        
        if not can_access:
            embed = discord.Embed(
                title="🔒 عالم مقفل",
                description=message,
                color=self.bot.world_colors["warning"]
            )
            await self._send_interaction_message(interaction, embed=embed, ephemeral=True)
            return
        
        # تحديث العالم الحالي
        await self.bot.db.update_player(interaction.user.id, {"current_world": world_id})
        
        # الحصول على جزء البداية
        start_part_id = self.bot.story_loader.get_start_part(world_id)
        part_data = self.bot.story_loader.get_part(world_id, start_part_id)
        
        if not part_data:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"لم يتم العثور على بداية {WORLD_NAMES[world_id]}",
                color=self.bot.world_colors["error"]
            )
            await self._send_interaction_message(interaction, embed=embed, ephemeral=True)
            return
        
        # تحديث تقدم اللاعب في العالم
        await self.bot.db.update_player(interaction.user.id, {f"{world_id}_part": start_part_id})
        await self.bot.db.save_session(interaction.user.id, start_part_id)
        
        # إنشاء رسالة تعريف بالعالم
        intro_embed = self.embeds.world_intro_embed(world_id, player.get("level", 1))
        await self._send_interaction_message(interaction, embed=intro_embed, ephemeral=True)
        
        # الحصول على بيانات اللاعب المحدثة
        updated_player = await self.bot.db.get_player(interaction.user.id)
        
        # إنشاء رسالة القصة
        story_embed = self.bot.create_game_embed(world_id, part_data, updated_player)
        
        # إنشاء الأزرار الدائمة
        view = PersistentStoryView(self.bot, interaction.user.id, world_id, part_data)
        
        # تحديد القناة المناسبة للعالم
        channel = await self._get_world_channel(interaction, world_id)
        
        if channel:
            await channel.send(
                content=f"**{interaction.user.mention} بدأ رحلته في {WORLD_NAMES[world_id]}**",
                embed=story_embed,
                view=view
            )
            await self._send_interaction_message(interaction, content=f"✅ تم إرسال القصة في {channel.mention}", ephemeral=True)
        else:
            # إذا لم توجد القناة المناسبة، أرسل في نفس القناة
            await self._send_interaction_message(interaction, embed=story_embed, view=view)
    
    # ============================================
    # أمر /استمر - متابعة الرحلة
    # ============================================
        @app_commands.command(name="استمر", description="⏩ استمر في رحلتك من آخر نقطة")
    @rate_limit("استمر")
    async def continue_command(self, interaction: discord.Interaction):
        """متابعة الرحلة من آخر نقطة"""

        # منع خطأ: The application did not respond
        await interaction.response.defer(ephemeral=True)

        try:
            # التحقق من القناة المناسبة
            if not await self._check_channel(interaction):
                return

            user_id = interaction.user.id
            player = await self.bot.db.get_player(user_id)

            if not player or not player.get("current_world"):
                await interaction.followup.send(
                    "❌ لا يوجد تقدم سابق. استخدم `/ابدأ` أولاً.",
                    ephemeral=True
                )
                return

            current_world = player.get("current_world", "fantasy")
            current_part = player.get(f"{current_world}_part")

            if not current_part or current_part == "لم يبدأ":
                await interaction.followup.send(
                    f"❌ لم تبدأ {WORLD_NAMES.get(current_world, current_world)} بعد!",
                    ephemeral=True
                )
                return

            part_data = self.bot.story_loader.get_part(current_world, current_part)
            if not part_data:
                await interaction.followup.send(
                    "❌ عذراً، تعذر تحميل بيانات القصة الحالية.",
                    ephemeral=True
                )
                return

            # إنشاء رسالة القصة
            story_embed = self.bot.create_game_embed(current_world, part_data, player)

            # إنشاء الأزرار الدائمة
            view = PersistentStoryView(self.bot, user_id, current_world, part_data)
            await self.bot.db.save_session(user_id, current_part)

            # تحديد القناة المناسبة
            channel = await self._get_world_channel(interaction, current_world)

            if channel:
                await channel.send(
                    content=f"**{interaction.user.mention} يستمر في {WORLD_NAMES[current_world]}**",
                    embed=story_embed,
                    view=view
                )
                await interaction.followup.send(
                    f"✅ تم متابعة القصة في {channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(embed=story_embed, view=view, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in continue_command: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ حدث خطأ أثناء محاولة استكمال القصة.",
                ephemeral=True
            )
    
    # ============================================
    # أمر /قراراتي - عرض آخر القرارات
    # ============================================
    
    @app_commands.command(name="قراراتي", description="📜 اعرض آخر قراراتك في القصة")
    @app_commands.describe(
        العدد="عدد لقرارات (1-20, افتراضي 10)"
    )
    @rate_limit("قراراتي")
    async def history_command(
        self,
        interaction: discord.Interaction,
        العدد: Optional[int] = 10
    ):
        """عرض تاريخ القرارات"""
        
        # تحديد العدد (بين 1 و 20)
        limit = max(1, min(العدد, 20))
        
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
        
        # الحصول على تاريخ القرارات
        history = await self.bot.db.get_history(user_id, limit)
        
        if not history:
            embed = discord.Embed(
                title="📜 تاريخ القرارات",
                description="لا توجد قرارات مسجلة بعد. ابدأ اللعب لتظهر قراراتك!",
                color=self.bot.world_colors["info"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # إنشاء رسالة التاريخ
        embed = discord.Embed(
            title=f"📜 آخر {len(history)} قرارات",
            color=self.bot.world_colors["general"]
        )
        
        for i, h in enumerate(history, 1):
            world_emoji = WORLD_EMOJIS.get(h.get('world', 'general'), '🌍')
            timestamp = h.get('timestamp', '')
            time_str = ""
            
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    now = datetime.now()
                    diff = now - dt
                    
                    if diff.days > 0:
                        time_str = f"منذ {diff.days} يوم"
                    elif diff.seconds > 3600:
                        time_str = f"منذ {diff.seconds // 3600} ساعة"
                    else:
                        time_str = f"منذ {diff.seconds // 60} دقيقة"
                except:
                    pass
            
            value = f"{h.get('choice_text', '')[:100]}"
            if h.get('effects'):
                value += f"\n`{h.get('effects')}`"
            
            embed.add_field(
                name=f"{i}. {world_emoji} {h.get('part_id', '')} {time_str}",
                value=value or "قرار غير معروف",
                inline=False
            )
        
        embed.set_footer(text=f"إجمالي القرارات: {player.get('choices_count', 0)}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /تاريخي - عرض تقدمي في العالم
    # ============================================
    
    @app_commands.command(name="تاريخي", description="📊 اعرض تقدمك في العالم الحالي")
    @rate_limit("تاريخي")
    async def progress_command(self, interaction: discord.Interaction):
        """عرض التقدم في العالم الحالي"""
        
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
        
        current_world = player.get("current_world", "fantasy")
        
        # الحصول على تقدم العالم
        current_part = player.get(f"{current_world}_part", "لم يبدأ")
        
        if current_part == "لم يبدأ":
            progress_text = "لم تبدأ هذا العالم بعد"
            percentage = 0
        else:
            world_progress = self.bot.story_loader.get_world_progress(current_world, current_part)
            total = world_progress["total"]
            current = world_progress["current"]
            percentage = world_progress["percentage"]
            
            progress_text = f"الجزء {current} من {total} ({percentage:.1f}%)"
        
        embed = discord.Embed(
            title=f"{WORLD_EMOJIS[current_world]} تقدمك في {WORLD_NAMES[current_world]}",
            color=self.bot.get_world_color(current_world)
        )
        
        # شريط التقدم
        progress_bar = self.bot.create_progress_bar(int(percentage), 100, 15)
        embed.add_field(
            name="📊 التقدم",
            value=f"{progress_bar}\n{progress_text}",
            inline=False
        )
        
        # معلومات إضافية
        if player.get(f"{current_world}_ending"):
            embed.add_field(
                name="✅ الحالة",
                value=f"مكتمل! النهاية: {player[f'{current_world}_ending']}",
                inline=False
            )
                    
        # متغيرات خاصة بالعالم
        if current_world == "fantasy":
            embed.add_field(
                name="✨ قوة الفانتازيا",
                value=f"{player.get('fantasy_power', 0)}/100",
                inline=True
            )
        elif current_world == "retro":
            embed.add_field(
                name="📜 الذكريات",
                value=f"{player.get('memories', 0)}/100",
                inline=True
            )
        elif current_world == "future":
            embed.add_field(
                name="⚙️ مستوى التكنولوجيا",
                value=f"{player.get('tech_level', 0)}/100",
                inline=True
            )
        elif current_world == "alternate":
            embed.add_field(
                name="🌀 الهوية",
                value=f"{player.get('identity', 0)}/100",
                inline=True
            )
        
        embed.add_field(
            name="🌑 الفساد",
            value=f"{player.get('corruption', 0)}/100",
            inline=True
        )
        
        embed.add_field(
            name="💎 الشظايا",
            value=str(player.get('shards', 0)),
            inline=True
        )
        
        embed.set_footer(text=f"المستوى {player.get('level', 1)} • {player.get('xp', 0)} XP")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /إعادة - إعادة تعيين التقدم
    # ============================================
    
    @app_commands.command(name="إعادة", description="🔄 إعادة تعيين تقدمك (احذر! لا يمكن التراجع)")
    @rate_limit("إعادة")
    async def reset_command(self, interaction: discord.Interaction):
        """إعادة تعيين تقدم اللاعب"""
        
        # طلب تأكيد
        embed = discord.Embed(
            title="⚠️ تحذير!",
            description=(
                "هل أنت متأكد من إعادة تعيين تقدمك؟\n\n"
                "**سيتم حذف:**\n"
                "• كل تقدمك في جميع العوالم\n"
                "• جميع الإنجازات\n"
                "• جميع العناصر في مخزونك\n"
                "• تاريخ قراراتك\n\n"
                "**لا يمكن التراجع عن هذا الإجراء!**"
            ),
            color=self.bot.world_colors["warning"]
        )
        
        async def confirm(interaction: discord.Interaction):
            user_id = interaction.user.id
            
            # حذف اللاعب
            await self.bot.db.delete_player(user_id)
            
            embed = discord.Embed(
                title="✅ تم إعادة التعيين",
                description="تم حذف تقدمك بالكامل. استخدم `/ابدأ` لبدء رحلة جديدة!",
                color=self.bot.world_colors["success"]
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        async def cancel(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ تم الإلغاء",
                description="تم إلغاء عملية إعادة التعيين.",
                color=self.bot.world_colors["info"]
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        view = ConfirmView(interaction.user.id, confirm, cancel)
        await interaction.response.send_message(embed=embed, view=view)
    
    # ============================================
    # دوال مساعدة
    # ============================================
    
    async def _check_channel(self, interaction: discord.Interaction) -> bool:
        """التحقق من أن القناة مناسبة للأمر"""
        # هذه دالة اختيارية - يمكن تعطيلها إذا أردت السماح بأي قناة
        return True
    
    async def _get_world_channel(self, interaction: discord.Interaction, world_id: str) -> Optional[discord.TextChannel]:
        """الحصول على القناة المناسبة للعالم"""
        guild = interaction.guild
        if not guild:
            return None

        # 1) أولوية لإعدادات السيرفر عبر أمر setup
        configured_channel_id = await self.bot.db.get_world_channel(guild.id, world_id)
        if configured_channel_id:
            configured_channel = guild.get_channel(configured_channel_id)
            if isinstance(configured_channel, discord.TextChannel):
                perms = configured_channel.permissions_for(guild.me)
                if perms.send_messages and perms.embed_links:
                    return configured_channel

        # 2) fallback على الأسماء الافتراضية من الثوابت
        from core.constants import SERVER_CHANNELS
        channel_name = SERVER_CHANNELS.get(world_id, {}).get("records")
        if channel_name:
            for channel in guild.channels:
                if channel.name == channel_name and isinstance(channel, discord.TextChannel):
                    perms = channel.permissions_for(guild.me)
                    if perms.send_messages and perms.embed_links:
                        return channel

        # 3) لا ننشئ قناة تلقائياً: نعيد None ليتم الإرسال في نفس القناة
        return None


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(StoryCommands(bot))
    logger.info("✅ تم تحميل أوامر القصة")
