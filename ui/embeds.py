# ui/embeds.py - تصميم الرسائل المدمجة (Embeds) الجميلة
# هذا الملف مسؤول عن شكل ومظهر كل رسائل البوت

import discord
from datetime import datetime
from typing import Dict, List, Any, Optional

from core.constants import (
    WORLD_COLORS, WORLD_DIVIDERS, WORLD_EMOJIS, WORLD_NAMES,
    WORLD_DESCRIPTIONS, WORLD_UNLOCK_RULES, create_progress_bar
)
from story.worlds import world_manager


class NexusEmbeds:
    """
    كلاس مسؤول عن إنشاء كل أنواع الرسائل المدمجة
    """
    
    def __init__(self, bot):
        self.bot = bot
    
    # ============================================
    # رسائل القصة الأساسية
    # ============================================
    
    def story_embed(self, world_id: str, part_data: Dict, player_data: Dict) -> discord.Embed:
        """
        إنشاء رسالة القصة الرئيسية
        هذه أهم رسالة - تظهر النص والخيارات
        """
        world_name = self.bot.get_world_name(world_id)
        world_emoji = self.bot.get_world_emoji(world_id)
        world_color = self.bot.get_world_color(world_id)
        
        # عنوان الجزء
        title = part_data.get('title', 'فصل جديد')
        location = part_data.get('location', '')
        
        if location:
            full_title = f"{world_emoji} {title} | 📍 {location}"
        else:
            full_title = f"{world_emoji} {title}"
        
        # نص القصة
        description = part_data.get('text', '')
        
        # إنشاء الـ Embed
        embed = discord.Embed(
            title=full_title,
            description=description,
            color=world_color,
            timestamp=datetime.now()
        )
        
        # إضافة الفاصل المناسب للعالم
        embed.set_image(url=self.bot.get_world_divider(world_id))
        
        # إضافة إحصائيات اللاعب
        stats = self._create_stats_field(world_id, player_data)
        embed.add_field(name="📊 حالتك", value=stats, inline=False)

        # معاينة الخيارات المتاحة (الاختيار الفعلي عبر الأزرار)
        choices = part_data.get('choices', [])
        if choices:
            preview = []
            for idx, choice in enumerate(choices[:4], 1):
                emoji = choice.get('emoji', '•')
                text = choice.get('text', 'خيار')
                preview.append(f"{idx}. {emoji} {text}")
            embed.add_field(name="🧭 الخيارات المتاحة", value="\n".join(preview), inline=False)
        
        # سطر سينمائي قصير يزيد الإحساس بالمشهد
        tone = self._get_scene_tone(part_data)
        embed.add_field(name="🎬 نبضة المشهد", value=tone, inline=False)

        # شريط التقدم داخل العالم
        part_id = part_data.get('id', 'unknown')
        part_number = self._extract_part_number(part_id)
        world_total = self.bot.story_loader.WORLDS.get(world_id, {}).get('total_parts', 1)
        progress_bar = create_progress_bar(part_number, world_total, 12)
        progress_percent = int((part_number / max(world_total, 1)) * 100)
        embed.add_field(
            name="🧭 تقدمك في العالم",
            value=f"{progress_bar} **{progress_percent}%** (الجزء {part_number}/{world_total})",
            inline=False
        )

        # إضافة تذييل
        embed.set_footer(text=f"{world_name} • {part_id} • اختر بحكمة")
        
        return embed
    
    def _create_stats_field(self, world_id: str, player: Dict) -> str:
        """إنشاء حقل الإحصائيات"""
        stats = []
        
        # إحصائيات أساسية
        stats.append(f"💎 **شظايا:** {player.get('shards', 0)}")
        
        # شريط الفساد
        corruption = player.get('corruption', 0)
        stats.append(f"🌑 **فساد:** {create_progress_bar(corruption, 100)} {corruption}%")
        
        # شريط الغموض
        mystery = player.get('mystery', 0)
        stats.append(f"🔮 **غموض:** {create_progress_bar(mystery, 100)} {mystery}%")
        
        # السمعة
        rep = player.get('reputation', 0)
        rep_emoji = "⭐" if rep >= 0 else "⚠️"
        stats.append(f"{rep_emoji} **سمعة:** {rep}")
        
        # التوجه
        alignment = player.get('alignment', 'Gray')
        align_emoji = {"Light": "✨", "Gray": "⚪", "Dark": "🌑"}.get(alignment, "⚪")
        stats.append(f"{align_emoji} **توجه:** {alignment}")
        
        # متغيرات خاصة بالعالم
        if world_id == "fantasy":
            power = player.get('fantasy_power', 0)
            stats.append(f"✨ **قوة فانتازيا:** {create_progress_bar(power, 100)} {power}%")
        elif world_id == "retro":
            memories = player.get('memories', 0)
            stats.append(f"📜 **ذكريات:** {create_progress_bar(memories, 100)} {memories}%")
        elif world_id == "future":
            tech = player.get('tech_level', 0)
            stats.append(f"⚙️ **تكنولوجيا:** {create_progress_bar(tech, 100)} {tech}%")
        elif world_id == "alternate":
            identity = player.get('identity', 0)
            stats.append(f"🌀 **هوية:** {create_progress_bar(identity, 100)} {identity}%")
        
        # المستوى والخبرة
        level = player.get('level', 1)
        xp = player.get('xp', 0)
        next_xp = self.bot.get_xp_for_level(level + 1)
        stats.append(f"📊 **مستوى {level}** ({xp}/{next_xp} XP)")
        
        return "\n".join(stats)
    
    # ============================================
    # رسائل العوالم
    # ============================================
    
    def world_intro_embed(self, world_id: str, player_level: int) -> discord.Embed:
        """رسالة تعريف بالعالم عند الدخول"""
        world_info = world_manager.get_world(world_id)
        
        embed = discord.Embed(
            title=f"{world_info.EMOJI} {world_info.NAME}",
            description=world_info.DESCRIPTION,
            color=world_info.COLOR
        )
        
        # معلومات إضافية
        embed.add_field(
            name="📖 عدد الأجزاء",
            value=f"{world_info.TOTAL_PARTS} جزء",
            inline=True
        )
        
        embed.add_field(
            name="🎬 النهايات",
            value=f"{len(world_info.ENDINGS)} نهايات مختلفة",
            inline=True
        )
        
        # متطلبات الدخول
        rules = WORLD_UNLOCK_RULES.get(world_id, {})
        req_level = rules.get('required_level', 1)
        
        if world_id == "fantasy":
            status = "✅ متاح للجميع"
        else:
            if player_level >= req_level:
                status = f"✅ متاح (مستوى {player_level} كافي)"
            else:
                status = f"🔒 يحتاج مستوى {req_level}"
        
        embed.add_field(name="🚪 حالة الدخول", value=status, inline=False)
        
        # الشخصيات الرئيسية
        chars = []
        for char_id, char in list(world_info.CHARACTERS.items())[:3]:
            chars.append(f"{char.emoji} **{char.name}** - {char.role}")
        
        if chars:
            embed.add_field(name="👥 شخصيات", value="\n".join(chars), inline=True)
        
        # المواقع الرئيسية
        locs = []
        for loc_id, loc in list(world_info.LOCATIONS.items())[:3]:
            locs.append(f"{loc.emoji} **{loc.name}**")
        
        if locs:
            embed.add_field(name="📍 مواقع", value="\n".join(locs), inline=True)
        
        embed.set_image(url=self.bot.get_world_divider(world_id))
        embed.set_footer(text="هل أنت مستعد لبدء المغامرة؟")
        
        return embed
    
    def worlds_list_embed(self, player_data: Dict) -> discord.Embed:
        """رسالة قائمة العوالم المتاحة"""
        embed = discord.Embed(
            title="🌍 رحلتك في النيكسس",
            description="اختر عالمك واستمر في المغامرة",
            color=WORLD_COLORS["general"]
        )
        
        worlds = world_manager.get_world_order()
        
        for world_id in worlds:
            world = world_manager.get_world(world_id)
            
            # حالة العالم
            if world_id == "fantasy":
                status = "✅ متاح"
                lock_text = ""
            else:
                # التحقق من فتح العالم
                prev_world = {"retro": "fantasy", "future": "retro", "alternate": "future"}.get(world_id)
                prev_ending = player_data.get(f"{prev_world}_ending")
                
                if prev_ending:
                    status = "✅ مفتوح"
                    lock_text = ""
                else:
                    status = "🔒 مقفل"
                    prev_name = world_manager.get_world(prev_world).NAME
                    lock_text = f"\n└ أكمل {prev_name} أولاً"
            
            # التقدم في العالم
            current_part = player_data.get(f"{world_id}_part", "لم يبدأ")
            ending = player_data.get(f"{world_id}_ending")
            
            if ending:
                progress = f"✅ مكتمل - {ending}"
            else:
                if current_part and current_part != "لم يبدأ":
                    progress = f"📖 في الجزء {current_part}"
                else:
                    progress = "⏳ لم يبدأ بعد"
            
            embed.add_field(
                name=f"{world.EMOJI} {world.NAME}",
                value=f"**الحالة:** {status}\n**التقدم:** {progress}{lock_text}",
                inline=False
            )
        
        embed.set_footer(text="استخدم /ابدأ [العالم] لبدء المغامرة")
        return embed
    
    # ============================================
    # رسائل اللاعب
    # ============================================
    
    def player_profile_embed(self, user: discord.User, player_data: Dict) -> discord.Embed:
        """ملف اللاعب الشخصي"""
        embed = discord.Embed(
            title=f"👤 ملف {user.name}",
            color=player_data.get('level', 1) * 1000  # لون حسب المستوى
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # إحصائيات أساسية
        stats = []
        stats.append(f"**المستوى:** {player_data.get('level', 1)}")
        stats.append(f"**الخبرة:** {player_data.get('xp', 0)} XP")
        stats.append(f"**الشظايا:** {player_data.get('shards', 0)} 💎")
        stats.append(f"**الفساد:** {player_data.get('corruption', 0)}% 🌑")
        stats.append(f"**السمعة:** {player_data.get('reputation', 0)} ⭐")
        
        embed.add_field(name="📊 إحصائيات", value="\n".join(stats), inline=True)
        
        # تقدم العوالم
        worlds_progress = []
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            world = world_manager.get_world(world_id)
            ending = player_data.get(f"{world_id}_ending")
            
            if ending:
                worlds_progress.append(f"{world.EMOJI} {world.NAME}: ✅ مكتمل")
            else:
                part = player_data.get(f"{world_id}_part", "لم يبدأ")
                if part and part != "لم يبدأ":
                    worlds_progress.append(f"{world.EMOJI} {world.NAME}: 📖 في التقدم")
                else:
                    worlds_progress.append(f"{world.EMOJI} {world.NAME}: ⏳ لم يبدأ")
        
        embed.add_field(name="🌍 العوالم", value="\n".join(worlds_progress), inline=False)
        
        # آخر نشاط
        last_active = player_data.get('last_active', '')
        if last_active:
            try:
                last = datetime.fromisoformat(last_active)
                now = datetime.now()
                diff = now - last
                hours = diff.total_seconds() / 3600
                
                if hours < 24:
                    activity = "اليوم"
                elif hours < 48:
                    activity = "أمس"
                else:
                    activity = f"منذ {int(hours/24)} أيام"
                
                embed.set_footer(text=f"آخر نشاط: {activity}")
            except:
                pass
        
        return embed
    
    # ============================================
    # رسائل الإنجازات
    # ============================================
    
    def achievement_unlock_embed(self, achievement_data: Dict) -> discord.Embed:
        """رسالة فتح إنجاز جديد"""
        embed = discord.Embed(
            title="🏆 إنجاز جديد!",
            description=f"{achievement_data.get('emoji', '🏆')} **{achievement_data.get('name', '')}**",
            color=0xffd700  # ذهبي
        )
        
        description = achievement_data.get('description', '')
        if description:
            embed.add_field(name="📝 وصف", value=description, inline=False)
        
        xp = achievement_data.get('xp_reward', 0)
        if xp:
            embed.add_field(name="🌟 مكافأة", value=f"{xp} XP", inline=True)
        
        return embed
    
    def achievements_list_embed(self, user: discord.User, achievements: List[Dict], total: int) -> discord.Embed:
        """قائمة الإنجازات"""
        embed = discord.Embed(
            title=f"🏆 إنجازات {user.name}",
            description=f"لديك **{len(achievements)}/{total}** إنجاز",
            color=0xffd700
        )
        
        if achievements:
            # تجميع الإنجازات حسب العالم
            by_world = {"fantasy": [], "retro": [], "future": [], "alternate": [], "general": []}
            
            for ach in achievements[:15]:  # حد أقصى 15
                world = ach.get('world', 'general')
                if world in by_world:
                    by_world[world].append(ach)
            
            for world_id, ach_list in by_world.items():
                if ach_list:
                    world_name = world_manager.get_world(world_id).NAME if world_id != 'general' else 'عام'
                    world_emoji = world_manager.get_world(world_id).EMOJI if world_id != 'general' else '🌟'
                    
                    value = "\n".join([
                        f"{a.get('emoji', '🏆')} {a.get('name', '')}"
                        for a in ach_list[:5]
                    ])
                    
                    if len(ach_list) > 5:
                        value += f"\n+ {len(ach_list)-5} أخرى..."
                    
                    embed.add_field(
                        name=f"{world_emoji} {world_name}",
                        value=value,
                        inline=True
                    )
        else:
            embed.description = "لا توجد إنجازات بعد. استمر في اللعب!"
        
        return embed
    
    # ============================================
    # رسائل المخزون
    # ============================================
    
    def inventory_embed(self, user: discord.User, items: List[Dict]) -> discord.Embed:
        """عرض المخزون"""
        embed = discord.Embed(
            title=f"🎒 مخزون {user.name}",
            color=0x2ecc71  # أخضر
        )
        
        if items:
            # تجميع العناصر حسب النوع
            consumables = []
            permanents = []
            crafting = []
            others = []
            
            for item in items:
                item_type = item.get('type', 'other')
                if item_type == 'consumable':
                    consumables.append(item)
                elif item_type == 'permanent':
                    permanents.append(item)
                elif item_type == 'crafting':
                    crafting.append(item)
                else:
                    others.append(item)
            
            if consumables:
                value = "\n".join([
                    f"{c.get('item_emoji', '📦')} **{c.get('item_name')}** x{c.get('quantity', 1)}"
                    for c in consumables[:8]
                ])
                embed.add_field(name="🧪 جرعات", value=value, inline=False)
            
            if permanents:
                value = "\n".join([
                    f"{p.get('item_emoji', '🔮')} **{p.get('item_name')}**"
                    for p in permanents[:5]
                ])
                embed.add_field(name="⚡ معدات", value=value, inline=False)
            
            if crafting:
                value = "\n".join([
                    f"{c.get('item_emoji', '🔨')} **{c.get('item_name')}** x{c.get('quantity', 1)}"
                    for c in crafting[:5]
                ])
                embed.add_field(name="🔨 مواد صياغة", value=value, inline=False)
            
            if others:
                value = "\n".join([
                    f"{o.get('item_emoji', '📦')} **{o.get('item_name')}** x{o.get('quantity', 1)}"
                    for o in others[:5]
                ])
                embed.add_field(name="📦 أخرى", value=value, inline=False)
            
            if len(items) > 20:
                embed.set_footer(text=f"وعناصر أخرى... إجمالي {len(items)} عنصر")
            else:
                embed.set_footer(text=f"إجمالي {len(items)} عنصر")
        else:
            embed.description = "مخزونك فارغ. العب أكثر لتحصل على عناصر!"
        
        return embed
    
    # ============================================
    # رسائل النظام
    # ============================================
    
    def error_embed(self, message: str, details: str = "") -> discord.Embed:
        """رسالة خطأ"""
        embed = discord.Embed(
            title="❌ خطأ",
            description=message,
            color=WORLD_COLORS["error"]
        )
        
        if details:
            embed.add_field(name="تفاصيل", value=f"```{details}```", inline=False)
        
        return embed
    
    def success_embed(self, message: str) -> discord.Embed:
        """رسالة نجاح"""
        return discord.Embed(
            title="✅ تم بنجاح",
            description=message,
            color=WORLD_COLORS["success"]
        )
    
    def warning_embed(self, message: str) -> discord.Embed:
        """رسالة تحذير"""
        return discord.Embed(
            title="⚠️ تحذير",
            description=message,
            color=WORLD_COLORS["warning"]
        )
    
    def info_embed(self, title: str, message: str) -> discord.Embed:
        """رسالة معلومات"""
        return discord.Embed(
            title=f"ℹ️ {title}",
            description=message,
            color=WORLD_COLORS["info"]
        )
    
    # ============================================
    # رسائل المساعدة
    # ============================================
    
    def help_embed(self) -> discord.Embed:
        """رسالة المساعدة الرئيسية"""
        embed = discord.Embed(
            title="📚 مساعدة بوت النيكسس",
            description=(
                "مرحباً بك في **بوت النيكسس** - راوي القصص التفاعلي!\n"
                "استكشف 4 عوالم مختلفة واتخذ قراراتك بنفسك.\n"
            ),
            color=WORLD_COLORS["general"]
        )
        
        # الأوامر الرئيسية
        commands = (
            "**/ابدأ [عالم]** - ابدأ رحلتك في عالم معين\n"
            "**/استمر** - استمر من آخر نقطة\n"
            "**/عوالمي** - اعرض تقدمك في كل عالم\n"
            "**/حالتي** - اعرض إحصائياتك\n"
            "**/مخزني** - اعرض عناصرك\n"
            "**/إنجازاتي** - اعرض إنجازاتك\n"
            "**/يومي** - خذ مكافأتك اليومية\n"
            "**/تاريخي** - اعرض قراراتك السابقة\n"
            "**/مساعدة** - عرض هذه المساعدة"
        )
        
        embed.add_field(name="🎮 الأوامر", value=commands, inline=False)
        
        # شرح العوالم
        worlds_text = ""
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            world = world_manager.get_world(world_id)
            worlds_text += f"{world.EMOJI} **{world.NAME}**: {world.DESCRIPTION[:50]}...\n"
        
        embed.add_field(name="🌍 العوالم", value=worlds_text, inline=False)
        
        embed.set_footer(text="تذكر: كل قرار يغير مصيرك في النيكسس")
        
        return embed
    
    def world_help_embed(self, world_id: str) -> discord.Embed:
        """مساعدة خاصة بعالم معين"""
        world = world_manager.get_world(world_id)
        
        embed = discord.Embed(
            title=f"{world.EMOJI} شرح {world.NAME}",
            description=world.DESCRIPTION,
            color=world.COLOR
        )
        
        # النهايات
        endings_text = ""
        for eid, ending in world.ENDINGS.items():
            endings_text += f"• **{ending.name}** - {ending.description}\n"
        
        embed.add_field(name="🎬 النهايات", value=endings_text, inline=False)
        
        # الشخصيات
        chars_text = ""
        for cid, char in list(world.CHARACTERS.items())[:5]:
            chars_text += f"{char.emoji} **{char.name}** - {char.role}\n"
        
        embed.add_field(name="👥 شخصيات", value=chars_text, inline=True)
        
        # المواقع
        locs_text = ""
        for lid, loc in list(world.LOCATIONS.items())[:5]:
            locs_text += f"{loc.emoji} **{loc.name}**\n"
        
        embed.add_field(name="📍 مواقع", value=locs_text, inline=True)
        
        # متغيرات خاصة
        if world.SPECIAL_VARS:
            embed.add_field(
                name="📊 متغيرات خاصة",
                value="\n".join([f"• {v}" for v in world.SPECIAL_VARS]),
                inline=False
            )
        
        embed.set_footer(text=f"عدد الأجزاء: {world.TOTAL_PARTS}")
        
        return embed
    
    # ============================================
    # رسائل النهايات
    # ============================================
    
    def ending_embed(self, world_id: str, ending_type: str, player_data: Dict) -> discord.Embed:
        """رسالة نهاية العالم"""
        world = world_manager.get_world(world_id)
        ending = world.ENDINGS.get(f"{world_id}_{ending_type}")
        
        if not ending:
            # إذا لم نجد النهاية المحددة، نستخدم نهاية افتراضية
            return self.info_embed(
                "🎬 نهاية الرحلة",
                f"لقد وصلت إلى نهاية {world.NAME}!"
            )
        
        # ألوان حسب نوع النهاية
        colors = {
            "light": 0xf1c40f,  # ذهبي
            "dark": 0x2c3e50,    # كحلي
            "gray": 0x95a5a6,    # رمادي
            "secret": 0x9b59b6   # بنفسجي
        }
        
        embed = discord.Embed(
            title=f"🎬 {ending.name}",
            description=ending.description,
            color=colors.get(ending_type, world.COLOR)
        )
        
        # إحصائيات النهاية
        stats = []
        stats.append(f"**المستوى النهائي:** {player_data.get('level', 1)}")
        stats.append(f"**الشظايا المجمعة:** {player_data.get('shards', 0)} 💎")
        stats.append(f"**الفساد النهائي:** {player_data.get('corruption', 0)}% 🌑")
        
        embed.add_field(name="📊 إحصائيات", value="\n".join(stats), inline=True)
        
        # المكافآت
        if ending.rewards:
            rewards = []
            if 'xp' in ending.rewards:
                rewards.append(f"🌟 {ending.rewards['xp']} XP")
            if 'items' in ending.rewards:
                for item in ending.rewards['items']:
                    rewards.append(f"📦 {item}")
            
            if rewards:
                embed.add_field(name="🎁 المكافآت", value="\n".join(rewards), inline=True)
        
        # العالم التالي
        if ending.next_world:
            next_world = world_manager.get_world(ending.next_world)
            embed.add_field(
                name="🔓 عالم جديد مفتوح",
                value=f"{next_world.EMOJI} **{next_world.NAME}** أصبح متاحاً!",
                inline=False
            )
        
        embed.set_image(url=WORLD_DIVIDERS["ending"])
        
        return embed
    
    # ============================================
    # رسائل المكافآت اليومية
    # ============================================
    
    def daily_reward_embed(self, day: int, rewards: Dict, streak: int) -> discord.Embed:
        """رسالة المكافأة اليومية"""
        embed = discord.Embed(
            title=f"🎁 اليوم {day} من المكافآت",
            description=f"استمراريتك: **{streak} أيام** 🔥",
            color=0xf1c40f
        )
        
        reward_text = []
        
        if 'shards' in rewards:
            reward_text.append(f"💎 **{rewards['shards']}** شظية")
        
        if 'xp' in rewards:
            reward_text.append(f"🌟 **{rewards['xp']}** XP")
        
        if 'items' in rewards:
            for item in rewards['items']:
                reward_text.append(f"📦 {item.get('name', 'عنصر')} x{item.get('quantity', 1)}")
        
        embed.add_field(name="📦 حصلت على:", value="\n".join(reward_text), inline=False)
        
        # المكافأة القادمة
        next_day = (day % 7) + 1
        embed.set_footer(text=f"غداً: اليوم {next_day} بمكافآت أكبر!")
        
        return embed
    
    # ============================================
    # رسالة الترحيب في السيرفر
    # ============================================
    
    def welcome_server_embed(self, guild_name: str, bot_stats: Dict) -> discord.Embed:
        """رسالة ترحيب عند دخول البوت سيرفر جديد"""
        embed = discord.Embed(
            title=f"✨ شكراً لاستضافتي في {guild_name} ✨",
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
            color=WORLD_COLORS["general"]
        )
        
        # إحصائيات البوت
        embed.add_field(
            name="📊 إحصائيات",
            value=(
                f"**السيرفرات:** {bot_stats.get('guilds', 0)}\n"
                f"**المستخدمين:** {bot_stats.get('users', 0)}\n"
                f"**الإصدار:** {bot_stats.get('version', '1.0.0')}"
            ),
            inline=True
        )
        
        # العوالم
        worlds_text = ""
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            world = world_manager.get_world(world_id)
            worlds_text += f"{world.EMOJI} {world.NAME}\n"
        
        embed.add_field(name="🌍 العوالم", value=worlds_text, inline=True)
        
        embed.set_image(url=WORLD_DIVIDERS["general"])
        embed.set_footer(text="نتمنى لك رحلة ممتعة في النيكسس!")
        
        return embed


    def _extract_part_number(self, part_id: str) -> int:
        """استخراج رقم الجزء من المعرف مثل FANTASY_12"""
        try:
            return int(str(part_id).split('_')[-1])
        except Exception:
            return 1

    def _get_scene_tone(self, part_data: Dict) -> str:
        """إضافة سطر نغمة سينمائية خفيف حسب محتوى الجزء"""
        text = f"{part_data.get('title','')} {part_data.get('text','')}"
        low = text.lower()

        if any(k in low for k in ['ظلام', 'خطر', 'دم', 'انقطاع', 'هاوي']):
            return "الهواء ثقيل... والقرار التالي قد يغيّر كل شيء."
        if any(k in low for k in ['نور', 'أمل', 'فجر', 'سلام', 'تعايش']):
            return "ومضة أمل تتسلل بين الشقوق... لكن الأمل وحده لا يكفي."
        if any(k in low for k in ['سر', 'مجهول', 'مرآة', 'ذاكرة', 'شيفرة']):
            return "كل إجابة هنا تفتح باب سؤال جديد."
        return "المشهد هادئ ظاهرياً... لكن العوالم تراقب اختيارك."



# ============================================
# تصدير الكلاس
# ============================================

__all__ = ['NexusEmbeds']
