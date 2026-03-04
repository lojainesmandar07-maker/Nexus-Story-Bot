# core/bot.py - الكلاس الرئيسي للبوت
# هذا هو قلب المشروع - كل شيء يبدأ من هنا

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

# استيراد الإعدادات والثوابت
from core.constants import (
    WORLD_COLORS, WORLD_DIVIDERS, WORLD_EMOJIS, WORLD_NAMES,
    WORLD_DESCRIPTIONS, WORLD_UNLOCK_RULES, SYSTEM_MESSAGES,
    get_world_color, get_world_divider, get_world_emoji,
    get_world_name, get_world_description, create_progress_bar
)
from core.config import config, paths, env

# استيراد قاعدة البيانات
from database.db_manager import DatabaseManager

# استيراد محمل القصة
from story.loader import StoryLoader

# استيراد مدير الأزرار الدائمة
from ui.views import PersistentViewManager

# استيراد أدوات مساعدة
from utils.logger import setup_logger
from utils.helpers import format_time, parse_effects
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class NexusBot(commands.Bot):
    """
    الكلاس الرئيسي للبوت - يرث من commands.Bot
    يحتوي على كل الإعدادات والوظائف الأساسية
    """
    
    def __init__(self):
        # إعداد الصلاحيات (Intents)
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        # الحصول على البادئة من الإعدادات
        command_prefix = config.get('bot.command_prefix', '/')
        
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None,  # سنستخدم أوامر سلاش للمساعدة
            case_insensitive=True
        )
        
        # معلومات البوت الأساسية
        self.version = config.get('bot.version', '1.0.0')
        self.bot_name = config.get('bot.name', 'Nexus Bot')
        self.owner_ids = config.get('bot.owner_ids', [])
        
        # الثوابت من core.constants
        self.world_colors = WORLD_COLORS
        self.world_dividers = WORLD_DIVIDERS
        self.world_emojis = WORLD_EMOJIS
        self.world_names = WORLD_NAMES
        self.world_descriptions = WORLD_DESCRIPTIONS
        self.world_unlock_rules = WORLD_UNLOCK_RULES
        self.system_messages = SYSTEM_MESSAGES
        
        # مدير قاعدة البيانات
        self.db: Optional[DatabaseManager] = None
        
        # محمل القصة
        self.story_loader: Optional[StoryLoader] = None
        
        # مدير الأزرار الدائمة
        self.view_manager: Optional[PersistentViewManager] = None
        
        # محدد السرعة
        self.rate_limiter = RateLimiter()
        
        # قاموس لتخزين الجلسات النشطة
        self.active_sessions: Dict[int, Dict] = {}
        
        # إحصائيات البوت
        self.stats = {
            "start_time": None,
            "commands_used": 0,
            "buttons_clicked": 0,
            "users_count": 0,
            "worlds_completed": 0,
            "total_choices": 0,
            "total_achievements": 0
        }
        
        # قائمة الإضافات (Cogs) التي سيتم تحميلها
        self.initial_extensions = [
            'commands.story_commands',
            'commands.world_commands',
            'commands.player_commands',
            'commands.inventory_commands',
            'commands.achievement_commands',
            'commands.daily_commands',
            'commands.help_commands',
            'commands.admin_commands'
        ]
        
        logger.info(f"✅ تم إنشاء كائن البوت (الإصدار {self.version})")
        logger.info(f"📌 البادئة: {command_prefix}")
    
    async def setup_hook(self):
        """
        يتم استدعاؤها قبل تشغيل البوت
        هنا نحمّل كل الإضافات ونسجل الأزرار الدائمة
        """
        logger.info("🔄 جاري تجهيز البوت...")
        
        # بدء计时
        self.stats["start_time"] = discord.utils.utcnow()
        
        # تهيئة قاعدة البيانات
        self.db = DatabaseManager()
        await self.db.initialize()
        logger.info("✅ قاعدة البيانات جاهزة")
        
        # تهيئة محمل القصة
        self.story_loader = StoryLoader(self.db)
        await self.story_loader.load_all_stories()
        logger.info("✅ محمل القصة جاهز")
        
        # تهيئة مدير الأزرار الدائمة
        self.view_manager = PersistentViewManager(self)
        logger.info("✅ مدير الأزرار جاهز")
        
        # تحميل الإضافات (Cogs)
        await self.load_extensions()
        
        # تسجيل الأزرار الدائمة (مهم جداً!)
        await self.view_manager.register_all_views()
        
        # مزامنة أوامر السلاش
        synced = await self.tree.sync()
        logger.info(f"✅ تم مزامنة {len(synced)} أمر سلاش")
        
        # تحديث إحصائيات المستخدمين
        await self.update_stats()
        
        # بدء مهمة الحفظ التلقائي
        self.loop.create_task(self.auto_save_task())
        
        # بدء مهمة النسخ الاحتياطي
        if config.get('backup.enabled', True):
            self.loop.create_task(self.auto_backup_task())
        
        logger.info("✅ البوت جاهز!")
    
    async def load_extensions(self):
        """تحميل كل الإضافات من مجلد commands"""
        loaded = 0
        failed = []
        
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                loaded += 1
                logger.info(f"✅ تم تحميل {extension}")
            except Exception as e:
                failed.append(extension)
                logger.error(f"❌ فشل تحميل {extension}: {e}")
        
        if failed:
            logger.warning(f"⚠️ {len(failed)} إضافة فشلت: {', '.join(failed)}")
        logger.info(f"✅ تم تحميل {loaded}/{len(self.initial_extensions)} إضافة")

    async def sync_guild_commands(self):
        """مزامنة أوامر السلاش لكل سيرفر لتظهر فوراً (Guild Sync)."""
        synced_count = 0
        for guild in self.guilds:
            try:
                # انسخ الأوامر العالمية إلى السيرفر ثم مزامنة فورية
                # هذا يقلل تأخر ظهور الأوامر العالمية مثل /ابدأ و /استمر
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                synced_count += 1
            except Exception as e:
                logger.warning(f"⚠️ فشل مزامنة أوامر السيرفر {guild.id}: {e}")
        if synced_count:
            logger.info(f"✅ تمت مزامنة أوامر السلاش في {synced_count} سيرفر")

    async def on_ready(self):
        """يتم استدعاؤها عندما يكون البو جاهزاً"""
        logger.info(f"✅ {self.user} متصل وجاهز!")
        logger.info(f"🆔 ID: {self.user.id}")
        logger.info(f"🌐 في {len(self.guilds)} سيرفر")
        
        # تحديث الحالة
        activity_text = config.get('bot.activity_status', '🌍 النيكسس ينتظرك | /ابدأ')
        await self.change_presence(
            activity=discord.Game(name=activity_text)
        )
        
        # تحديث إحصائيات المستخدمين
        await self.update_stats()

        # مزامنة سريعة لكل سيرفر (تجعل الأوامر تظهر فوراً مثل /ابدأ و/استمر)
        await self.sync_guild_commands()
        
        # إرسال رسالة إلى قنوات الترحيب
        for guild in self.guilds:
            await self.send_welcome_message(guild)
        
        logger.info(f"👥 إجمالي المستخدمين: {self.stats['users_count']}")
    
    async def on_guild_join(self, guild: discord.Guild):
        """عند دخول البوت إلى سيرفر جديد"""
        logger.info(f"✅ انضممت إلى سيرفر جديد: {guild.name} (ID: {guild.id})")
        try:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"✅ تمت مزامنة أوامر السلاش للسيرفر الجديد {guild.id}")
        except Exception as e:
            logger.warning(f"⚠️ فشل مزامنة السيرفر الجديد {guild.id}: {e}")
        await self.send_welcome_message(guild)
    
    async def send_welcome_message(self, guild: discord.Guild):
        """إرسال رسالة ترحيب في السيرفر"""
        try:
            # البحث عن قناة الترحيب المناسبة
            welcome_channel = None
            channel_names = ["✦-الترحيب", "welcome", "ترحيب", "general", "عام"]
            
            for name in channel_names:
                welcome_channel = discord.utils.get(guild.channels, name=name)
                if welcome_channel:
                    break
            
            if not welcome_channel:
                # إذا لم يجد، استخدم أول قناة نصية
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        welcome_channel = channel
                        break
            
            if welcome_channel:
                embed = discord.Embed(
                    title=f"✨ شكراً لاستضافتي في {guild.name} ✨",
                    description=(
                        "أنا **بوت النيكسس**، راوي القصص التفاعلي!\n\n"
                        "**📖 ماذا أقدم؟**\n"
                        "• 4 عوالم مختلفة للاستكشاف\n"
                        "• أكثر من 160 جزء قصة\n"
                        "• 30+ إنجاز ومكافأة\n"
                        "• عناصر قابلة للاستخدام والدمج\n"
                        "• أزرار دائمة تعمل للأبد\n\n"
                        "**🎮 للبدء:** استخدم `/ابدأ`\n"
                        "**📚 للمساعدة:** استخدم `/مساعدة`"
                    ),
                    color=self.world_colors["general"],
                    timestamp=datetime.now()
                )
                
                # إضافة حقول للعوالم (المفاتيح الأساسية فقط بدون المرادفات)
                worlds_text = ""
                canonical_worlds = ["fantasy", "retro", "future", "alternate"]
                for world_id in canonical_worlds:
                    world_name = self.world_names.get(world_id, world_id)
                    world_emoji = self.world_emojis.get(world_id, "🌍")
                    worlds_text += f"{world_emoji} **{world_name}**\n"
                
                embed.add_field(
                    name="🌍 العوالم المتاحة",
                    value=worlds_text,
                    inline=True
                )
                
                embed.add_field(
                    name="📊 إحصائيات سريعة",
                    value=(
                        f"**السيرفرات:** {len(self.guilds)}\n"
                        f"**المستخدمين:** {self.stats['users_count']}\n"
                        f"**الإصدار:** {self.version}"
                    ),
                    inline=True
                )
                
                embed.set_image(url=self.world_dividers["general"])
                embed.set_footer(text="نتمنى لك رحلة ممتعة في النيكسس!")
                
                await welcome_channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة الترحيب لـ {guild.name}: {e}")
    
    async def on_message(self, message: discord.Message):
        """معالجة الرسائل"""
        # تجاهل رسائل البوت نفسه
        if message.author.bot:
            return
        
        # معالجة الأوامر النصية (احتياطي)
        await self.process_commands(message)
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """معالجة أخطاء الأوامر النصية"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        logger.error(f"❌ خطأ في أمر {ctx.command}: {error}")
        
        embed = discord.Embed(
            title="❌ حدث خطأ",
            description=f"```{error}```",
            color=self.world_colors["error"]
        )
        await ctx.send(embed=embed, delete_after=10)
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """معالجة أخطاء أوامر السلاش"""
        logger.error(f"❌ خطأ في أمر سلاش: {error}")
        
        embed = discord.Embed(
            title="❌ حدث خطأ",
            description=f"```{error}```",
            color=self.world_colors["error"]
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def on_interaction(self, interaction: discord.Interaction):
        """تسجيل التفاعلات (للإحصائيات)"""
        if interaction.type == discord.InteractionType.component:
            self.stats["buttons_clicked"] += 1
    
    async def close(self):
        """إغلاق البوت بشكل آمن"""
        logger.info("🔄 جاري إغلاق البوت...")
        
        # حفظ البيانات
        if self.db:
            await self.db.close()
        
        # إلغاء المهام
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        
        await super().close()
        logger.info("✅ تم إغلاق البوت")
    
    async def update_stats(self):
        """تحديث إحصائيات البوت"""
        total_users = 0
        for guild in self.guilds:
            total_users += guild.member_count
        
        self.stats["users_count"] = total_users
        
        if self.db:
            # الحصول على إحصائيات من قاعدة البيانات
            self.stats["worlds_completed"] = await self.db.get_total_completions()
            self.stats["total_achievements"] = await self.db.get_total_achievements()
    
    async def auto_save_task(self):
        """مهمة الحفظ التلقائي"""
        await self.wait_until_ready()
        interval = config.get('story.save_interval', 300)
        
        while not self.is_closed():
            try:
                await asyncio.sleep(interval)
                
                if self.db:
                    await self.db.save_all()
                    logger.debug("✅ تم الحفظ التلقائي")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ خطأ في الحفظ التلقائي: {e}")
    
    async def auto_backup_task(self):
        """مهمة النسخ الاحتياطي التلقائي"""
        await self.wait_until_ready()
        interval = config.get('backup.interval', 86400)
        
        while not self.is_closed():
            try:
                await asyncio.sleep(interval)
                
                if self.db:
                    backup_path = paths.get_backup_file()
                    await self.db.create_backup(backup_path)
                    logger.info(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ خطأ في النسخ الاحتياطي: {e}")
    
    # ============================================
    # دوال مساعدة للعوالم
    # ============================================
    
    def get_world_color(self, world_id: str) -> int:
        """الحصول على لون عالم معين"""
        return self.world_colors.get(world_id, self.world_colors["general"])
    
    def get_world_divider(self, world_id: str) -> str:
        """الحصول على فاصل عالم معين"""
        return self.world_dividers.get(world_id, self.world_dividers["general"])
    
    def get_world_emoji(self, world_id: str) -> str:
        """الحصول على إيموجي عالم معين"""
        return self.world_emojis.get(world_id, self.world_emojis["general"])
    
    def get_world_name(self, world_id: str) -> str:
        """الحصول على اسم عالم معين"""
        return self.world_names.get(world_id, world_id)
    
    def get_world_description(self, world_id: str) -> str:
        """الحصول على وصف عالم معين"""
        return self.world_descriptions.get(world_id, "")
    
    def can_access_world(self, player_data: Dict, world_id: str) -> tuple[bool, str]:
        """التحقق من إمكانية دخول عالم معين"""
        rules = self.world_unlock_rules.get(world_id)
        
        if not rules:
            return False, "عالم غير موجود"
        
        # العالم الأول متاح دائماً
        if world_id == "fantasy":
            return True, "✓ متاح"
        
        # التحقق من المستوى
        required_level = rules.get("required_level", 1)
        player_level = player_data.get("level", 1)
        
        if player_level < required_level:
            return False, f"❌ يحتاج مستوى {required_level}"
        
        # التحقق من النهاية المطلوبة
        required_ending = rules.get("required_ending")
        if required_ending:
            if not player_data.get(required_ending):
                prev_world = world_id
                if world_id == "retro":
                    prev_world = "fantasy"
                elif world_id == "future":
                    prev_world = "retro"
                elif world_id == "alternate":
                    prev_world = "future"
                
                prev_name = self.get_world_name(prev_world)
                return False, f"❌ أكمل {prev_name} أولاً"
        
        return True, "✓ متاح"
    
    # ============================================
    # دوال مساعدة للاعبين
    # ============================================
    
    async def get_or_create_player(self, user_id: int, username: str) -> Dict:
        """الحصول على بيانات اللاعب أو إنشائها"""
        player = await self.db.get_player(user_id)
        
        if not player:
            await self.db.create_player(user_id, username)
            player = await self.db.get_player(user_id)
            logger.info(f"👤 لاعب جديد: {username} (ID: {user_id})")
        
        return player
    
    async def add_xp(self, user_id: int, amount: int) -> tuple[int, bool]:
        """إضافة نقاط خبرة والتحقق من زيادة المستوى"""
        player = await self.db.get_player(user_id)
        if not player:
            return 0, False
        
        current_xp = player.get("xp", 0)
        current_level = player.get("level", 1)
        
        new_xp = current_xp + amount
        new_level = current_level
        
        # التحقق من زيادة المستوى
        level_up = False
        while new_level < config.get('game.max_level', 20):
            required = self.get_xp_for_level(new_level + 1)
            if new_xp >= required:
                new_level += 1
                level_up = True
            else:
                break
        
        # تحديث البيانات
        updates = {"xp": new_xp}
        if level_up:
            updates["level"] = new_level
        
        await self.db.update_player(user_id, updates)
        
        return new_xp, level_up
    
    def get_xp_for_level(self, level: int) -> int:
        """حساب الخبرة المطلوبة لمستوى معين"""
        base = config.get('game.base_xp', 100)
        multiplier = config.get('game.xp_multiplier', 1.5)
        
        return int(base * (multiplier ** (level - 1)))
    
    # ============================================
    # دوال مساعدة للرسائل
    # ============================================
    
    def create_progress_bar(self, current: int, maximum: int, length: int = 10) -> str:
        """إنشاء شريط تقدم"""
        return create_progress_bar(current, maximum, length)
    
    def get_system_message(self, category: str, key: str, **kwargs) -> str:
        """الحصول على رسالة نظام"""
        message = self.system_messages.get(category, {}).get(key, "")
        if kwargs:
            message = message.format(**kwargs)
        return message
    
    # ============================================
    # خصائص (Properties)
    # ============================================
    
    @property
    def uptime(self) -> Optional[datetime]:
        """مدة تشغيل البوت"""
        return self.stats["start_time"]
    
    @property
    def uptime_str(self) -> str:
        """مدة التشغيل كنص"""
        if not self.stats["start_time"]:
            return "غير معروف"
        
        delta = discord.utils.utcnow() - self.stats["start_time"]
        return format_time(delta.total_seconds())
    
    @property
    def is_ready(self) -> bool:
        """التحقق من جاهزية البوت"""
        return self.db is not None and self.story_loader is not None


# ============================================
# دالة للحصول على كائن البوت
# ============================================
async def get_bot() -> NexusBot:
    """الحصول على كائن البوت (للاستخدام في أماكن أخرى)"""
    return NexusBot()


# ============================================
# تصدير الكلاس
# ============================================
__all__ = ['NexusBot', 'get_bot']
