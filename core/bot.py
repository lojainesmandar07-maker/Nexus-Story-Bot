# core/bot.py - الكلاس الرئيسي للبوت
# هذا هو قلب المشروع - كل شيء يبدأ من هنا

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, Dict, Any, List, Set, Tuple
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
        
        # مزامنة الأوامر Global (المسار الأكثر ثباتاً)
        synced = await self.tree.sync()
        logger.info(f"✅ تم مزامنة {len(synced)} أمر سلاش (Global)")
        
        # تحديث إحصائيات المستخدمين
        await self.update_stats()
        
        # بدء مهمة الحفظ التلقائي
        self.loop.create_task(self.auto_save_task())
        
        # بدء مهمة النسخ الاحتياطي
        if config.get('backup.enabled', True):
            self.loop.create_task(self.auto_backup_task())
        
        logger.info("✅ البوت جاهز!")

    async def get_active_story_states(self) -> List[Dict[str, Any]]:
        """
        جمع كل الأجزاء النشطة المحتملة من أكثر من مصدر حالة.
        يعتمد على جدول sessions بالإضافة إلى حقول تقدم العوالم داخل players.
        """
        states: List[Dict[str, Any]] = []
        seen: Set[Tuple[int, str, str]] = set()

        if not self.db:
            return states

        world_ids = list(self.world_names.keys())

        # المصدر الأول: sessions (آخر جزء متفاعل عليه غالباً)
        sessions = await self.db.fetch_all("SELECT user_id, current_part FROM sessions")
        for session in sessions:
            user_id = session.get("user_id")
            current_part = session.get("current_part")
            if not user_id or not current_part:
                continue

            player = await self.db.get_player(user_id)
            if not player:
                continue

            resolved_world = player.get("current_world", "fantasy")
            if not self.story_loader.get_part(resolved_world, current_part):
                # fallback: اكتشف العالم الصحيح عبر مطابقة part لكل عالم
                for world_id in world_ids:
                    if self.story_loader.get_part(world_id, current_part):
                        resolved_world = world_id
                        break

            key = (user_id, resolved_world, current_part)
            if key not in seen:
                seen.add(key)
                states.append({"user_id": user_id, "world_id": resolved_world, "part_id": current_part})

        # المصدر الثاني: كل حقول *_part داخل players (يشمل تقدم عدة عوالم)
        part_fields = ", ".join([f"{world_id}_part" for world_id in world_ids])
        players = await self.db.fetch_all(f"SELECT user_id, {part_fields} FROM players")

        for player in players:
            user_id = player.get("user_id")
            if not user_id:
                continue

            for world_id in world_ids:
                part_id = player.get(f"{world_id}_part")
                if not part_id:
                    continue
                if not self.story_loader.get_part(world_id, part_id):
                    continue

                key = (user_id, world_id, part_id)
                if key in seen:
                    continue

                seen.add(key)
                states.append({"user_id": user_id, "world_id": world_id, "part_id": part_id})

        return states
        
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
        """نسخ أوامر الـ Global إلى كل Guild لمزامنة فورية (خصوصاً /ابدأ و/استمر)."""
        synced_count = 0
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                synced_count += 1
            except Exception as e:
                logger.warning(f"⚠️ فشل مزامنة أوامر السيرفر {guild.id}: {e}")
        if synced_count:
            logger.info(f"✅ تمت مزامنة أوامر Guild في {synced_count} سيرفر")

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
            logger.info(f"✅ تمت مزامنة أوامر Guild للسيرفر الجديد {guild.id}")
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
                    color=self.world_colors["general"]
                )
                
                # قائمة العوالم بشكل موحد وآمن
                canonical_worlds = ["fantasy", "retro", "future", "alternate"]
                worlds_text = ""
                for world_id in canonical_worlds:
                    emoji = self.world_emojis.get(world_id, "🌍")
                    name = self.world_names.get(world_id, world_id)
                    worlds_text += f"{emoji} {name}\n"

                embed.add_field(
                    name="🌍 العوالم المتاحة",
                    value=worlds_text,
                    inline=False
                )
                
                embed.set_image(url=self.world_dividers["general"])
                embed.set_footer(text="تم تطويره بـ ❤️ لخدمة مجتمعكم")
                
                await welcome_channel.send(embed=embed)
                logger.info(f"✅ تم إرسال رسالة الترحيب في {guild.name}")
        
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة الترحيب: {e}")
    
    async def on_command_error(self, ctx, error):
        """معالجة أخطاء الأوامر التقليدية"""
        logger.error(f"خطأ أمر: {error}")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """معالجة أخطاء أوامر السلاش"""
        try:
            if isinstance(error, app_commands.CommandOnCooldown):
                embed = discord.Embed(
                    title="⏳ انتظر قليلاً",
                    description=f"يمكنك استخدام هذا الأمر بعد {error.retry_after:.1f} ثانية",
                    color=self.world_colors["warning"]
                )
            elif isinstance(error, app_commands.MissingPermissions):
                embed = discord.Embed(
                    title="🚫 لا تملك الصلاحية",
                    description="ليس لديك صلاحية استخدام هذا الأمر",
                    color=self.world_colors["error"]
                )
            else:
                embed = discord.Embed(
                    title="❌ حدث خطأ",
                    description="حدث خطأ غير متوقع. حاول مرة أخرى لاحقاً",
                    color=self.world_colors["error"]
                )
                logger.error(f"App command error: {error}", exc_info=True)
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"خطأ في معالجة الخطأ: {e}")
    
    async def update_stats(self):
        """تحديث إحصائيات البوت"""
        try:
            if not self.db:
                return
            
            # إحصائيات المستخدمين
            users_stats = await self.db.get_users_count()
            self.stats["users_count"] = users_stats
            
            # إحصائيات إضافية من قاعدة البيانات
            db_stats = await self.db.get_bot_stats()
            if db_stats:
                self.stats.update(db_stats)
        
        except Exception as e:
            logger.error(f"خطأ تحديث الإحصائيات: {e}")
    
    async def auto_save_task(self):
        """مهمة الحفظ التلقائي كل 5 دقائق"""
        await self.wait_until_ready()
        
        while not self.is_closed():
            try:
                await asyncio.sleep(300)  # 5 دقائق
                
                # حفظ البيانات النشطة
                if self.db:
                    await self.db.commit()
                
                logger.debug("💾 تم الحفظ التلقائي")
            
            except Exception as e:
                logger.error(f"خطأ في الحفظ التلقائي: {e}")
    
    async def auto_backup_task(self):
        """مهمة النسخ الاحتياطي كل 24 ساعة"""
        await self.wait_until_ready()
        
        backup_interval = config.get('backup.interval_hours', 24) * 3600
        
        while not self.is_closed():
            try:
                await asyncio.sleep(backup_interval)
                
                if self.db:
                    backup_path = await self.db.create_backup()
                    logger.info(f"📦 تم إنشاء نسخة احتياطية: {backup_path}")
            
            except Exception as e:
                logger.error(f"خطأ في النسخ الاحتياطي: {e}")
    
    async def close(self):
        """إغلاق البوت بشكل آمن"""
        logger.info("🔄 جاري إغلاق البوت...")
        
        try:
            # حفظ نهائي للبيانات
            if self.db:
                await self.db.commit()
                await self.db.close()
                logger.info("✅ تم حفظ وإغلاق قاعدة البيانات")
            
            await super().close()
            logger.info("✅ تم إغلاق البوت بنجاح")
        
        except Exception as e:
            logger.error(f"❌ خطأ أثناء الإغلاق: {e}")
    
    # ============================================
    # دوال مساعدة للوصول السريع
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
