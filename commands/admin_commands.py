# commands/admin_commands.py - أوامر المشرفين
# /إحصاءات, /تحديث, /نسخ_احتياطي, /بث, /إرسال_للجميع, /إدارة_لاعب

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List
import asyncio
from datetime import datetime, timedelta
import os
import sys

from core.bot import NexusBot
from core.constants import WORLD_NAMES, WORLD_EMOJIS
from core.config import config
from database.db_manager import DatabaseManager
from game.achievements import ALL_ACHIEVEMENTS
from ui.views import ConfirmView
from utils.rate_limiter import rate_limit
from utils.helpers import format_time, format_number

logger = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """أوامر المشرفين (تتطلب صلاحيات)"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = bot.embeds
    
    # ============================================
    # التحقق من صلاحيات المشرف
    # ============================================
    
    def is_admin(self, interaction: discord.Interaction) -> bool:
        """التحقق من أن المستخدم مشرف"""
        # التحقق من صلاحيات المشرف في السيرفر
        if interaction.user.guild_permissions.administrator:
            return True
        
        # التحقق من قائمة المالكين في الإعدادات
        if interaction.user.id in config.get('bot.owner_ids', []):
            return True
        
        return False
    
    def is_owner(self, interaction: discord.Interaction) -> bool:
        """التحقق من أن المستخدم مالك البوت"""
        return interaction.user.id in config.get('bot.owner_ids', [])

    # ============================================
    # أمر /تعيين_عالم - تعيين قناة عالم
    # ============================================

    @app_commands.command(name="تعيين_عالم", description="⚙️ تعيين قناة قصة لعالم محدد")
    @app_commands.describe(
        world="العالم المطلوب",
        channel="القناة التي تريد إرسال قصة هذا العالم إليها"
    )
    @app_commands.choices(world=[
        app_commands.Choice(name="🌲 عالم الفانتازيا", value="fantasy"),
        app_commands.Choice(name="📜 عالم الماضي", value="retro"),
        app_commands.Choice(name="🤖 عالم المستقبل", value="future"),
        app_commands.Choice(name="🌀 الواقع البديل", value="alternate")
    ])
    @rate_limit("تعيين_عالم")
    async def setup_world_command(
        self,
        interaction: discord.Interaction,
        world: str,
        channel: discord.TextChannel
    ):
        """تعيين قناة قصة لعالم محدد في هذا السيرفر"""

        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if interaction.guild is None:
            await interaction.response.send_message("❌ هذا الأمر يعمل داخل السيرفر فقط", ephemeral=True)
            return

        saved = await self.bot.db.set_world_channel(
            interaction.guild.id,
            world,
            channel.id,
            interaction.user.id
        )

        if not saved:
            await interaction.response.send_message("❌ فشل حفظ الإعداد، حاول مرة أخرى", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ تم حفظ إعداد العالم",
            description=(
                f"{WORLD_EMOJIS[world]} **{WORLD_NAMES[world]}**\n"
                f"سيتم إرسال القصة في: {channel.mention}"
            ),
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="عرض_تعيين_العوالم", description="🗺️ عرض قنوات العوالم المضبوطة")
    @rate_limit("عرض_تعيين_العوالم")
    async def show_world_setup_command(self, interaction: discord.Interaction):
        """عرض إعدادات قنوات العوالم الحالية في السيرفر"""

        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if interaction.guild is None:
            await interaction.response.send_message("❌ هذا الأمر يعمل داخل السيرفر فقط", ephemeral=True)
            return

        mapping = await self.bot.db.get_guild_world_channels(interaction.guild.id)

        embed = discord.Embed(
            title="🗺️ إعدادات قنوات العوالم",
            description="خريطة العوالم الحالية في هذا السيرفر",
            color=0x3498db
        )

        for world_id in ["fantasy", "retro", "future", "alternate"]:
            channel_id = mapping.get(world_id)
            channel = interaction.guild.get_channel(channel_id) if channel_id else None
            channel_text = channel.mention if channel else "غير معيّنة"

            embed.add_field(
                name=f"{WORLD_EMOJIS[world_id]} {WORLD_NAMES[world_id]}",
                value=channel_text,
                inline=False
            )

        embed.set_footer(text="استخدم /تعيين_عالم لتعيين أو تعديل قناة أي عالم")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ============================================
    # أمر /إحصاءات - إحصاءات البوت
    # ============================================
    
    @app_commands.command(name="إحصاءات", description="📊 إحصاءات البوت العامة (للمشرفين)")
    @rate_limit("إحصاءات")
    async def stats_command(self, interaction: discord.Interaction):
        """عرض إحصاءات البوت"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # إحصائيات عامة
            total_players = await self.bot.db.get_total_players()
            active_players = await self.bot.db.get_active_players(60)  # آخر ساعة
            
            # إحصائيات العوالم
            worlds_stats = []
            for world_id in ["fantasy", "retro", "future", "alternate"]:
                stats = await self.bot.db.get_world_stats(world_id)
                worlds_stats.append(f"{WORLD_EMOJIS[world_id]} **{WORLD_NAMES[world_id]}**")
                worlds_stats.append(f"├ لاعبين: {stats.get('total_players', 0)}")
                worlds_stats.append(f"└ مكتمل: {stats.get('completed_players', 0)}")
            
            # إحصائيات إضافية
            total_achievements = len(ALL_ACHIEVEMENTS)
            total_commands = len(self.bot.tree.get_commands())
            
            # وقت التشغيل
            uptime = self.bot.uptime
            uptime_str = format_time((datetime.now() - uptime).total_seconds()) if uptime else "غير معروف"
            
            embed = discord.Embed(
                title="📊 إحصاءات البوت",
                color=0x3498db,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="🤖 معلومات البوت",
                value=(
                    f"**الاسم:** {self.bot.user.name}\n"
                    f"**الإصدار:** {self.bot.version}\n"
                    f"**وقت التشغيل:** {uptime_str}\n"
                    f"**السيرفرات:** {len(self.bot.guilds)}"
                ),
                inline=True
            )
            
            embed.add_field(
                name="👥 اللاعبين",
                value=(
                    f"**إجمالي:** {total_players}\n"
                    f"**نشطين (آخر ساعة):** {active_players}\n"
                    f"**الأوامر المنفذة:** {self.bot.stats.get('commands_used', 0)}"
                ),
                inline=True
            )
            
            embed.add_field(
                name="📊 النظام",
                value=(
                    f"**الأوامر:** {total_commands}\n"
                    f"**الإنجازات:** {total_achievements}\n"
                    f"**الأزرار النشطة:** {len(self.bot.view_manager.active_views) if self.bot.view_manager else 0}"
                ),
                inline=True
            )
            
            embed.add_field(
                name="🌍 العوالم",
                value="\n".join(worlds_stats),
                inline=False
            )
            
            embed.set_footer(text=f"الطلب من: {interaction.user.name}")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            logger.error(f"❌ خطأ في إحصاءات: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {e}", ephemeral=True)
    
    # ============================================
    # أمر /تحديث - تحديث القصة أو الأوامر
    # ============================================
    
    @app_commands.command(name="تحديث", description="🔄 تحديث القصة أو الأوامر (للمشرفين)")
    @app_commands.describe(
        النوع="ما الذي تريد تحديثه"
    )
    @app_commands.choices(النوع=[
        app_commands.Choice(name="📖 القصص", value="stories"),
        app_commands.Choice(name="🎮 الأوامر", value="commands"),
        app_commands.Choice(name="⚙️ الإعدادات", value="config"),
        app_commands.Choice(name="🔧 الكل", value="all")
    ])
    @rate_limit("تحديث")
    async def reload_command(
        self,
        interaction: discord.Interaction,
        النوع: str
    ):
        """تحديث القصة أو الأوامر"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        results = []
        
        if النوع in ["stories", "all"]:
            try:
                # إعادة تحميل القصص
                await self.bot.story_loader.load_all_stories()
                results.append("✅ تم تحديث القصص")
            except Exception as e:
                results.append(f"❌ فشل تحديث القصص: {e}")
        
        if النوع in ["commands", "all"]:
            try:
                # إعادة تحميل الأوامر
                await self.bot.tree.sync()
                results.append("✅ تم تحديث الأوامر")
            except Exception as e:
                results.append(f"❌ فشل تحديث الأوامر: {e}")
        
        if النوع in ["config", "all"]:
            try:
                # إعادة تحميل الإعدادات
                config.reload_config()
                results.append("✅ تم تحديث الإعدادات")
            except Exception as e:
                results.append(f"❌ فشل تحديث الإعدادات: {e}")
        
        embed = discord.Embed(
            title="🔄 نتائج التحديث",
            description="\n".join(results),
            color=0x2ecc71 if "❌" not in "\n".join(results) else 0xe74c3c
        )
        
        await interaction.followup.send(embed=embed)
    
    # ============================================
    # أمر /نسخ_احتياطي - إنشاء نسخة احتياطية
    # ============================================
    
    @app_commands.command(name="نسخ_احتياطي", description="💾 إنشاء نسخة احتياطية من قاعدة البيانات (للمشرفين)")
    @rate_limit("نسخ_احتياطي")
    async def backup_command(self, interaction: discord.Interaction):
        """إنشاء نسخة احتياطية"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # إنشاء النسخة
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/backup_{timestamp}.db"
            
            success = await self.bot.db.create_backup(backup_path)
            
            if success:
                # الحصول على حجم الملف
                size = os.path.getsize(backup_path)
                size_mb = size / (1024 * 1024)
                
                embed = discord.Embed(
                    title="✅ تم إنشاء النسخة الاحتياطية",
                    description=f"**الملف:** `{backup_path}`\n**الحجم:** {size_mb:.2f} MB",
                    color=0x2ecc71
                )
            else:
                embed = discord.Embed(
                    title="❌ فشل إنشاء النسخة",
                    description="حدث خطأ أثناء إنشاء النسخة الاحتياطية",
                    color=0xe74c3c
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            logger.error(f"❌ خطأ في النسخ الاحتياطي: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {e}", ephemeral=True)
    
    # ============================================
    # أمر /بث - إرسال رسالة لقناة معينة
    # ============================================
    
    @app_commands.command(name="بث", description="📢 إرسال رسالة إلى قناة معينة (للمشرفين)")
    @app_commands.describe(
        القناة="القناة المستهدفة",
        الرسالة="نص الرسالة"
    )
    @rate_limit("بث")
    async def announce_command(
        self,
        interaction: discord.Interaction,
        القناة: discord.TextChannel,
        الرسالة: str
    ):
        """إرسال إعلان إلى قناة"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📢 إعلان",
            description=الرسالة,
            color=0x9b59b6,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text=f"من: {interaction.user.name}")
        
        try:
            await القناة.send(embed=embed)
            
            embed = discord.Embed(
                title="✅ تم الإرسال",
                description=f"تم إرسال الرسالة إلى {القناة.mention}",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ فشل الإرسال",
                description=str(e),
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /إرسال_للجميع - رسالة لجميع اللاعبين (خاص)
    # ============================================
    
    @app_commands.command(name="إرسال_للجميع", description="📨 إرسال رسالة خاصة لجميع اللاعبين (للمالك)")
    @app_commands.describe(
        الرسالة="نص الرسالة"
    )
    @rate_limit("إرسال_للجميع")
    async def broadcast_command(
        self,
        interaction: discord.Interaction,
        الرسالة: str
    ):
        """إرسال رسالة خاص لجميع اللاعبين"""
        
        if not self.is_owner(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر لمالك البوت فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📨 رسالة من الإدارة",
            description=الرسالة,
            color=0x9b59b6,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="شكراً لكونك جزءاً من النيكسس!")
        
        # هذه الميزة تحتاج إلى قائمة بكل اللاعبين
        # للتبسيط، نرسل للسيرفرات فقط
        sent_count = 0
        failed_count = 0
        
        for guild in self.bot.guilds:
            try:
                # البحث عن قناة عامة
                channel = discord.utils.get(guild.channels, name="عام")
                if not channel:
                    channel = discord.utils.get(guild.channels, name="general")
                
                if channel and isinstance(channel, discord.TextChannel):
                    await channel.send(embed=embed)
                    sent_count += 1
                else:
                    failed_count += 1
            
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ فشل إرسال لـ {guild.name}: {e}")
        
        result_embed = discord.Embed(
            title="📨 نتائج الإرسال",
            description=f"✅ تم الإرسال: {sent_count}\n❌ فشل: {failed_count}",
            color=0x2ecc71 if failed_count == 0 else 0xf39c12
        )
        
        await interaction.followup.send(embed=result_embed)
    
    # ============================================
    # أمر /إدارة_لاعب - إدارة لاعب معين
    # ============================================
    
    @app_commands.command(name="إدارة_لاعب", description="👤 إدارة بيانات لاعب (للمشرفين)")
    @app_commands.describe(
        اللاعب="اللاعب المستهدف",
        الإجراء="الإجراء المطلوب",
        القيمة="القيمة (اختياري)"
    )
    @app_commands.choices(الإجراء=[
        app_commands.Choice(name="👀 عرض البيانات", value="view"),
        app_commands.Choice(name="💎 إضافة شظايا", value="add_shards"),
        app_commands.Choice(name="🌑 تعديل الفساد", value="set_corruption"),
        app_commands.Choice(name="🌟 تعديل المستوى", value="set_level"),
        app_commands.Choice(name="🗑️ حذف اللاعب", value="delete"),
        app_commands.Choice(name="🔓 فتح عالم", value="unlock_world")
    ])
    @rate_limit("إدارة_لاعب")
    async def manage_player_command(
        self,
        interaction: discord.Interaction,
        اللاعب: discord.User,
        الإجراء: str,
        القيمة: Optional[str] = None
    ):
        """إدارة بيانات لاعب"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_id = اللاعب.id
        player = await self.bot.db.get_player(user_id)
        
        if not player and الإجراء != "view":
            embed = discord.Embed(
                title="❌ لاعب غير موجود",
                description=f"لا يوجد لاعب باسم {اللاعب.mention}",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if الإجراء == "view":
            # عرض بيانات اللاعب
            embed = discord.Embed(
                title=f"👤 بيانات {اللاعب.name}",
                color=0x3498db
            )
            
            if player:
                stats = [
                    f"**المستوى:** {player.get('level', 1)}",
                    f"**الخبرة:** {player.get('xp', 0)}",
                    f"**الشظايا:** {player.get('shards', 0)}",
                    f"**الفساد:** {player.get('corruption', 0)}",
                    f"**السمعة:** {player.get('reputation', 0)}",
                    f"**التوجه:** {player.get('alignment', 'Gray')}",
                    f"**العالم الحالي:** {player.get('current_world', 'fantasy')}",
                ]
                
                # نهايات العوالم
                endings = []
                for world in ["fantasy", "retro", "future", "alternate"]:
                    if player.get(f"{world}_ending"):
                        endings.append(f"{WORLD_EMOJIS[world]} ✓")
                    else:
                        endings.append(f"{WORLD_EMOJIS[world]} ✗")
                
                stats.append(f"**النهايات:** {' '.join(endings)}")
                
                embed.description = "\n".join(stats)
                
                # آخر نشاط
                last = player.get('last_active', '')
                if last:
                    embed.set_footer(text=f"آخر نشاط: {last[:16]}")
            else:
                embed.description = "لم يبدأ هذا اللاعب اللعبة بعد."
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif الإجراء == "add_shards" and القيمة:
            try:
                amount = int(القيمة)
                new_shards = player.get("shards", 0) + amount
                await self.bot.db.update_player(user_id, {"shards": new_shards})
                
                embed = discord.Embed(
                    title="✅ تمت الإضافة",
                    description=f"تمت إضافة {amount} شظايا لـ {اللاعب.mention}\nالرصيد الجديد: {new_shards}",
                    color=0x2ecc71
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            except ValueError:
                embed = discord.Embed(
                    title="❌ قيمة غير صالحة",
                    description="الرجاء إدخال رقم صحيح",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif الإجراء == "set_corruption" and القيمة:
            try:
                value = max(0, min(100, int(القيمة)))
                await self.bot.db.update_player(user_id, {"corruption": value})
                
                embed = discord.Embed(
                    title="✅ تم التعديل",
                    description=f"تم تعديل فساد {اللاعب.mention} إلى {value}",
                    color=0x2ecc71
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            except ValueError:
                embed = discord.Embed(
                    title="❌ قيمة غير صالحة",
                    description="الرجاء إدخال رقم بين 0 و 100",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif الإجراء == "set_level" and القيمة:
            try:
                value = int(القيمة)
                # حساب الخبرة المناسبة للمستوى
                from game.leveling import LevelSystem
                xp = LevelSystem.xp_for_level(value)
                
                await self.bot.db.update_player(user_id, {"level": value, "xp": xp})
                
                embed = discord.Embed(
                    title="✅ تم التعديل",
                    description=f"تم تعديل مستوى {اللاعب.mention} إلى {value}",
                    color=0x2ecc71
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            except ValueError:
                embed = discord.Embed(
                    title="❌ قيمة غير صالحة",
                    description="الرجاء إدخال رقم صحيح",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif الإجراء == "delete":
            # طلب تأكيد للحذف
            embed = discord.Embed(
                title="⚠️ تحذير!",
                description=f"هل أنت متأكد من حذف جميع بيانات {اللاعب.mention}؟\n**لا يمكن التراجع عن هذا الإجراء!**",
                color=0xf39c12
            )
            
            async def confirm(interaction: discord.Interaction):
                await self.bot.db.delete_player(user_id)
                
                embed = discord.Embed(
                    title="✅ تم الحذف",
                    description=f"تم حذف جميع بيانات {اللاعب.mention}",
                    color=0x2ecc71
                )
                await interaction.response.edit_message(embed=embed, view=None)
            
            async def cancel(interaction: discord.Interaction):
                embed = discord.Embed(
                    title="❌ تم الإلغاء",
                    description="تم إلغاء عملية الحذف",
                    color=0x95a5a6
                )
                await interaction.response.edit_message(embed=embed, view=None)
            
            view = ConfirmView(interaction.user.id, confirm, cancel)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        elif الإجراء == "unlock_world" and القيمة:
            # فتح عالم للاعب
            valid_worlds = ["fantasy", "retro", "future", "alternate"]
            if القيمة not in valid_worlds:
                embed = discord.Embed(
                    title="❌ عالم غير صالح",
                    description=f"العوالم المتاحة: {', '.join(valid_worlds)}",
                    color=0xe74c3c
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # فتح العالم بوضع نهاية وهمية
            await self.bot.db.update_player(user_id, {f"{القيمة}_ending": "unlocked_by_admin"})
            
            embed = discord.Embed(
                title="✅ تم الفتح",
                description=f"تم فتح {WORLD_NAMES.get(القيمة, القيمة)} لـ {اللاعب.mention}",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /تنظيف - حذف رسائل البوت
    # ============================================
    
    @app_commands.command(name="تنظيف", description="🧹 حذف رسائل البوت (للمشرفين)")
    @app_commands.describe(
        العدد="عدد الرسائل المراد حذفها (1-100)"
    )
    @rate_limit("تنظيف")
    async def cleanup_command(
        self,
        interaction: discord.Interaction,
        العدد: Optional[int] = 10
    ):
        """حذف رسائل البوت"""
        
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر للمشرفين فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تحديد العدد بين 1 و 100
        limit = max(1, min(العدد, 100))
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            deleted = 0
            
            async for message in interaction.channel.history(limit=100):
                if message.author == self.bot.user:
                    await message.delete()
                    deleted += 1
                    if deleted >= limit:
                        break
                    
                    # تأخير بسيط
                    await asyncio.sleep(0.5)
            
            embed = discord.Embed(
                title="🧹 تم التنظيف",
                description=f"تم حذف {deleted} رسالة للبوت",
                color=0x2ecc71
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ فشل التنظيف",
                description=str(e),
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /إعادة_تشغيل - إعادة تشغيل البوت (للمالك)
    # ============================================
    
    @app_commands.command(name="إعادة_تشغيل", description="🔄 إعادة تشغيل البوت (للمالك)")
    @rate_limit("إعادة_تشغيل")
    async def restart_command(self, interaction: discord.Interaction):
        """إعادة تشغيل البوت"""
        
        if not self.is_owner(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر لمالك البوت فقط!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔄 إعادة تشغيل",
            description="جاري إعادة تشغيل البوت...",
            color=0xf39c12
        )
        
        await interaction.response.send_message(embed=embed)
        
        # إغلاق البوت
        await self.bot.close()
        
        # إعادة التشغيل (يحتاج إلى آلية خارجية)
        # في ريلت، يمكن استخدام os._exit(0) لإعادة التشغيل
        # لكن هذا يعتمد على المنصة


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(AdminCommands(bot))
    logger.info("✅ تم تحميل أوامر المشرفين")
