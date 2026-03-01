# commands/help_commands.py - أوامر المساعدة
# /مساعدة, /شرح, /أسئلة, /روابط

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

from core.bot import NexusBot
from core.constants import WORLD_NAMES, WORLD_EMOJIS, WORLD_DESCRIPTIONS
from story.worlds import world_manager
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit

logger = logging.getLogger(__name__)


class HelpCommands(commands.Cog):
    """أوامر المساعدة والتوجيه"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /مساعدة - المساعدة الرئيسية
    # ============================================
    
    @app_commands.command(name="مساعدة", description="📚 اعرض قائمة الأوامر والمساعدة")
    @app_commands.describe(
        القسم="اختر القسم الذي تريد مساعدة عنه"
    )
    @app_commands.choices(القسم=[
        app_commands.Choice(name="🎮 أساسيات اللعبة", value="basics"),
        app_commands.Choice(name="🌍 العوالم", value="worlds"),
        app_commands.Choice(name="📖 القصة", value="story"),
        app_commands.Choice(name="👤 اللاعب", value="player"),
        app_commands.Choice(name="🎒 المخزون", value="inventory"),
        app_commands.Choice(name="🏆 الإنجازات", value="achievements"),
        app_commands.Choice(name="🎁 المكافآت اليومية", value="daily"),
        app_commands.Choice(name="❓ جميع الأوامر", value="all")
    ])
    @rate_limit("مساعدة")
    async def help_command(
        self,
        interaction: discord.Interaction,
        القسم: Optional[str] = None
    ):
        """عرض المساعدة حسب القسم"""
        
        if not القسم or القسم == "all":
            await self._show_all_commands(interaction)
        elif القسم == "basics":
            await self._show_basics(interaction)
        elif القسم == "worlds":
            await self._show_worlds_help(interaction)
        elif القسم == "story":
            await self._show_story_help(interaction)
        elif القسم == "player":
            await self._show_player_help(interaction)
        elif القسم == "inventory":
            await self._show_inventory_help(interaction)
        elif القسم == "achievements":
            await self._show_achievements_help(interaction)
        elif القسم == "daily":
            await self._show_daily_help(interaction)
    
    async def _show_all_commands(self, interaction: discord.Interaction):
        """عرض كل الأوامر"""
        
        embed = discord.Embed(
            title="📚 جميع أوامر بوت النيكسس",
            description=(
                "مرحباً بك في عالم النيكسس! هنا جميع الأوامر المتاحة:\n\n"
                "**📝 ملاحظة:** جميع الأوامر تبدأ بـ `/`"
            ),
            color=self.bot.world_colors["general"]
        )
        
        # أوامر القصة
        story_commands = (
            "`/ابدأ [عالم]` - ابدأ رحلتك في عالم معين\n"
            "`/استمر` - استمر من آخر نقطة\n"
            "`/قراراتي` - اعرض آخر قراراتك\n"
            "`/تاريخي` - اعرض تقدمك في العالم الحالي\n"
            "`/إعادة` - إعادة تعيين تقدمك (احذر!)"
        )
        embed.add_field(name="📖 أوامر القصة", value=story_commands, inline=False)
        
        # أوامر العوالم
        world_commands = (
            "`/عوالمي` - اعرض العوالم المتاحة\n"
            "`/تبديل_عالم` - بدّل بين العوالم\n"
            "`/شرح_عالم` - شرح مفصل لعالم\n"
            "`/خريطة` - اعرض خريطة العوالم\n"
            "`/ترتيب_العوالم` - ترتيب فتح العوالم\n"
            "`/إحصائيات_العالم` - إحصائيات عن عالم"
        )
        embed.add_field(name="🌍 أوامر العوالم", value=world_commands, inline=False)
        
        # أوامر اللاعب
        player_commands = (
            "`/حالتي` - اعرض ملفك الشخصي\n"
            "`/مستواي` - تفاصيل مستواك\n"
            "`/سمعتي` - معلومات سمعتك\n"
            "`/إحصائياتي` - إحصائيات متقدمة\n"
            "`/أين_أنا` - موقعك الحالي"
        )
        embed.add_field(name="👤 أوامر اللاعب", value=player_commands, inline=False)
        
        # أوامر المخزون
        inventory_commands = (
            "`/مخزني` - اعرض مخزونك\n"
            "`/استخدم` - استخدم عنصراً\n"
            "`/دمج` - ادمج عناصر لصنع عناصر أقوى\n"
            "`/بيع` - بع عنصراً\n"
            "`/هدية` - أهدِ عنصراً للاعب آخر"
        )
        embed.add_field(name="🎒 أوامر المخزون", value=inventory_commands, inline=False)
        
        # أوامر الإنجازات
        achievement_commands = (
            "`/إنجازاتي` - اعرض إنجازاتك\n"
            "`/نهاياتي` - اعرض النهايات\n"
            "`/إنجاز_عشوائي` - إنجاز عشوائي\n"
            "`/إحصائيات_الإنجازات` - إحصائيات\n"
            "`/إنجاز_تفصيلي` - تفاصيل إنجاز\n"
            "`/أندر_الإنجازات` - أندر الإنجازات"
        )
        embed.add_field(name="🏆 أوامر الإنجازات", value=achievement_commands, inline=False)
        
        # أوامر المكافآت اليومية
        daily_commands = (
            "`/يومي` - احصل على مكافأتك اليومية\n"
            "`/استمرارية` - اعرض استمراريتك\n"
            "`/مكافآتي` - سجل المكافآت\n"
            "`/تذكير_يومي` - فعّل التذكير"
        )
        embed.add_field(name="🎁 أوامر المكافآت", value=daily_commands, inline=False)
        
        # أوامر المساعدة
        help_commands = (
            "`/مساعدة` - عرض هذه المساعدة\n"
            "`/شرح` - شرح نظام معين\n"
            "`/أسئلة` - أسئلة شائعة\n"
            "`/روابط` - روابط مفيدة"
        )
        embed.add_field(name="📚 أوامر المساعدة", value=help_commands, inline=False)
        
        embed.set_footer(text="استخدم /مساعدة [قسم] لتفاصيل أكثر")
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_basics(self, interaction: discord.Interaction):
        """عرض أساسيات اللعبة"""
        
        embed = discord.Embed(
            title="🎮 أساسيات لعبة النيكسس",
            description="كل ما تحتاج معرفته للبدء",
            color=0x3498db
        )
        
        embed.add_field(
            name="❓ ما هو النيكسس؟",
            value=(
                "النيكسس هو عالم من 4 عوالم مترابطة، كل عالم له قصته وشخصياته ونهاياته.\n"
                "أنت كلاعب تختار مسارك بنفسك عبر القرارات التي تتخذها."
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎮 كيف ألعب؟",
            value=(
                "1️⃣ استخدم `/ابدأ` لبدء رحلتك في عالم الفانتازيا\n"
                "2️⃣ ستظهر لك رسالة قصة مع أزرار تمثل الخيارات\n"
                "3️⃣ اختر خيارك بحكمة - كل قرار يغير مسار القصة\n"
                "4️⃣ تابع تقدمك بـ `/استمر` أو `/حالتي`\n"
                "5️⃣ اجمع الشظايا والإنجازات لتصبح أقوى"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 المتغيرات الرئيسية",
            value=(
                "**💎 الشظايا:** عملة اللعبة الأساسية\n"
                "**🌑 الفساد:** كلما زاد، اقتربت من الظلام\n"
                "**🔮 الغموض:** معرفتك بأسرار النيكسس\n"
                "**⭐ السمعة:** سمعتك بين سكان العوالم\n"
                "**⚖️ التوجه:** نور - رمادي - ظلام"
            ),
            inline=False
        )
        
        embed.set_footer(text="ابدأ الآن بـ /ابدأ")
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_worlds_help(self, interaction: discord.Interaction):
        """عرض مساعدة العوالم"""
        
        embed = discord.Embed(
            title="🌍 شرح العوالم",
            description="النيكسس يتكون من 4 عوالم مترابطة",
            color=0x9b59b6
        )
        
        for world_id in ["fantasy", "retro", "future", "alternate"]:
            world_name = WORLD_NAMES.get(world_id, world_id)
            world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
            world_desc = WORLD_DESCRIPTIONS.get(world_id, "")
            
            embed.add_field(
                name=f"{world_emoji} {world_name}",
                value=f"{world_desc[:100]}...\n`/شرح_عالم {world_id}` للمزيد",
                inline=False
            )
        
        embed.add_field(
            name="🔓 ترتيب فتح العوالم",
            value=(
                "1️⃣ عالم الفانتازيا (متاح للجميع)\n"
                "2️⃣ عالم الماضي (بعد إكمال الفانتازيا)\n"
                "3️⃣ عالم المستقبل (بعد إكمال الماضي)\n"
                "4️⃣ الواقع البديل (بعد إكمال المستقبل)"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_story_help(self, interaction: discord.Interaction):
        """عرض مساعدة القصة"""
        
        embed = discord.Embed(
            title="📖 نظام القصة",
            description="كيف تعمل القصة التفاعلية",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="🔄 تدفق القصة",
            value=(
                "1️⃣ كل قرار تختاره يأخذك لمسار مختلف\n"
                "2️⃣ بعض الخيارات لها متطلبات (مستوى معين، عنصر...)\n"
                "3️⃣ القرارات تؤثر على المتغيرات (فساد، غموض، سمعة...)\n"
                "4️⃣ في النهاية، تصل إلى إحدى النهايات المتعددة"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎬 النهايات",
            value=(
                "✨ **نهاية النور** - توجه نحو الخير والسلام\n"
                "🌑 **نهاية الظلام** - استسلم للفساد\n"
                "⚖️ **نهاية التوازن** - حافظ على الوسطية\n"
                "🔮 **نهاية سرية** - اكتشف أسرار النيكسس"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 نصائح",
            value=(
                "• فكر قبل أن تختار - بعض القرارات لا رجعة فيها\n"
                "• راقب الفساد - لا تدعه يصل إلى 100\n"
                "• اجمع الشظايا - ستساعدك في اللحظات الحرجة\n"
                "• العب كل النهايات - هناك أسرار تنتظرك"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_player_help(self, interaction: discord.Interaction):
        """عرض مساعدة اللاعب"""
        
        embed = discord.Embed(
            title="👤 نظام اللاعب",
            description="كل ما يتعلق بشخصيتك",
            color=0xf1c40f
        )
        
        embed.add_field(
            name="📈 المستويات",
            value=(
                "كل قرار تاخذه يمنحك خبرة (XP)\n"
                "عند وصولك لكمية كافية، يرتفع مستواك\n"
                "المستوى الأعلى يمنحك ألقاباً ومكافآت"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⭐ السمعة",
            value=(
                "سمعتك تؤثر على تعامل الشخصيات معك\n"
                "سمعة عالية = خصومات وحوارات خاصة\n"
                "سمعة منخفضة = ضرائب وهجمات"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🌑 الفساد",
            value=(
                "الفساد يزداد مع اختيارات الظلام\n"
                "فساد عالٍ = قوة أكبر لكن عواقب وخيمة\n"
                "يمكنك تقليل الفساد بجرعات النقاء"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_inventory_help(self, interaction: discord.Interaction):
        """عرض مساعدة المخزون"""
        
        embed = discord.Embed(
            title="🎒 نظام المخزون",
            description="العناصر وكيفية استخدامها",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="🧪 أنواع العناصر",
            value=(
                "• **قابل للاستخدام**: جرعات، شظايا (تستهلك)\n"
                "• **دائم**: معدات، أدوات (تبقى معك)\n"
                "• **مواد صياغة**: تستخدم لصنع عناصر أقوى\n"
                "• **مفاتيح**: لفتح مناطق خاصة"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔨 الصياغة (Crafting)",
            value=(
                "اجمع المواد لتصنع عناصر أقوى\n"
                "استخدم `/دمج` لرؤية الوصفات المتاحة\n"
                "كلما ارتفع مستواك، تفتح وصفات جديدة"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💰 التجارة",
            value=(
                "يمكنك بيع العناصر بـ `/بيع`\n"
                "وإهدائها للآخرين بـ `/هدية`\n"
                "بعض العناصر النادرة لا تباع!"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_achievements_help(self, interaction: discord.Interaction):
        """عرض مساعدة الإنجازات"""
        
        embed = discord.Embed(
            title="🏆 نظام الإنجازات",
            description="كيف تحصل على الإنجازات",
            color=0xffd700
        )
        
        embed.add_field(
            name="📋 أنواع الإنجازات",
            value=(
                "• **إنجازات عادية**: تظهر للجميع\n"
                "• **إنجازات سرية 🔮**: تظهر فقط بعد الحصول عليها\n"
                "• **إنجازات نهايات**: تحصل عليها بإنهاء العوالم\n"
                "• **إنجازات خاصة**: لأمور نادرة"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎁 مكافآت الإنجازات",
            value=(
                "كل إنجاز يمنحك:\n"
                "• نقاط خبرة (XP)\n"
                "• عناصر خاصة أحياناً\n"
                "• فتح محتوى سري"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔍 كيف تكتشف الإنجازات السرية؟",
            value=(
                "• جرب خيارات غير متوقعة\n"
                "• تفاعل مع كل الشخصيات\n"
                "• ابحث في الأماكن الغريبة\n"
                "• العب بطرق مختلفة"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_daily_help(self, interaction: discord.Interaction):
        """عرض مساعدة المكافآت اليومية"""
        
        embed = discord.Embed(
            title="🎁 نظام المكافآت اليومية",
            description="لا تنس مكافأتك كل يوم!",
            color=0xf1c40f
        )
        
        embed.add_field(
            name="📅 كيف تعمل؟",
            value=(
                "• استخدم `/يومي` كل 24 ساعة\n"
                "• المكافآت تزداد مع الاستمرارية\n"
                "• كل 7 أيام تحصل على مكافأة خاصة\n"
                "• إذا فاتك يوم، تعود للبداية"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔥 مكافآت الاستمرارية",
            value=(
                "**7 أيام:** صندوق غامض\n"
                "**14 يوم:** شظايا نقية\n"
                "**21 يوم:** قلوب كريستال\n"
                "**30 يوم:** كريستال نيكسس 🏆"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⏰ التذكير",
            value=(
                "فعّل التذكير بـ `/تذكير_يومي تشغيل`\n"
                "سيتم تذكيرك يومياً في الساعة 12 ظهراً"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /شرح - شرح نظام معين
    # ============================================
    
    @app_commands.command(name="شرح", description="📖 شرح مفصل لنظام معين")
    @app_commands.describe(
        الموضوع="اختر الموضوع الذي تريد شرحه"
    )
    @app_commands.choices(الموضوع=[
        app_commands.Choice(name="💎 الشظايا", value="shards"),
        app_commands.Choice(name="🌑 الفساد", value="corruption"),
        app_commands.Choice(name="🔮 الغموض", value="mystery"),
        app_commands.Choice(name="⭐ السمعة", value="reputation"),
        app_commands.Choice(name="⚖️ التوجه", value="alignment"),
        app_commands.Choice(name="🤝 الثقة", value="trust"),
        app_commands.Choice(name="🔨 الصياغة", value="crafting"),
        app_commands.Choice(name="🎲 الاحتمالات", value="chance")
    ])
    @rate_limit("شرح")
    async def explain_command(
        self,
        interaction: discord.Interaction,
        الموضوع: str
    ):
        """شرح نظام معين بالتفصيل"""
        
        explanations = {
            "shards": {
                "title": "💎 الشظايا",
                "description": (
                    "الشظايا هي العملة الأساسية في النيكسس.\n\n"
                    "**كيف تحصل عليها؟**\n"
                    "• اختيارات معينة في القصة\n"
                    "• المكافآت اليومية\n"
                    "• فتح الصناديق\n"
                    "• إكمال الإنجازات\n\n"
                    "**لماذا تحتاجها؟**\n"
                    "• شراء عناصر من المتجر\n"
                    "• فتح مسارات خاصة في القصة\n"
                    "• الصياغة (Crafting)\n"
                    "• فتح إنجازات خاصة"
                )
            },
            "corruption": {
                "title": "🌑 الفساد",
                "description": (
                    "الفساد يقيس مدى تأثرك بالظلام.\n\n"
                    "**كيف يزيد؟**\n"
                    "• اختيارات أنانية\n"
                    "• استخدام عناصر مظلمة\n"
                    "• الهجوم على الأبرياء\n"
                    "• نهايات الظلام\n\n"
                    "**تأثيراته:**\n"
                    "• فساد > 70: مظهر متغير، حوارات مختلفة\n"
                    "• فساد > 90: بعض الشخصيات تهاجمك\n"
                    "• فساد 100: نهاية الظلام\n\n"
                    "**كيف تخفضه؟**\n"
                    "• جرعات النقاء\n"
                    "• اختيارات نبيلة\n"
                    "• مساعدة المحتاجين"
                )
            },
            "mystery": {
                "title": "🔮 الغموض",
                "description": (
                    "الغموض يمثل معرفتك بأسرار النيكسس.\n\n"
                    "**كيف يزيد؟**\n"
                    "• استكشاف أماكن جديدة\n"
                    "• قراءة كتب وألواح قديمة\n"
                    "• التحدث مع شخصيات غامضة\n"
                    "• اكتشاف أسرار\n\n"
                    "**فوائده:**\n"
                    "• فتح خيارات مخفية\n"
                    "• اكتشاف نهايات سرية\n"
                    "• فهم حبكة القصة بشكل أعمق\n"
                    "• إنجازات خاصة"
                )
            },
            "reputation": {
                "title": "⭐ السمعة",
                "description": (
                    "السمعة تعكس رأي سكان العوالم بك.\n\n"
                    "**من -50 إلى +50**\n\n"
                    "**سمعة عالية (+20 فأكثر):**\n"
                    "• خصومات عند الشراء\n"
                    "• حوارات خاصة\n"
                    "• مهام حصرية\n"
                    "• معاملة محترمة\n\n"
                    "**سمعة منخفضة (-20 فأقل):**\n"
                    "• ضرائب إضافية\n"
                    "• نظرات ريبة\n"
                    "• هجمات محتملة\n"
                    "• مكافأة على رأسك"
                )
            },
            "alignment": {
                "title": "⚖️ التوجه",
                "description": (
                    "التوجه يمثل ميولك الأخلاقي.\n\n"
                    "**✨ نور**\n"
                    "• اختيارات نبيلة\n"
                    "• مساعدة الآخرين\n"
                    "• نهايات مشرقة\n\n"
                    "**⚪ رمادي**\n"
                    "• توازن بين الخير والشر\n"
                    "• اختيارات عملية\n"
                    "• نهايات متوازنة\n\n"
                    "**🌑 ظلام**\n"
                    "• اختيارات أنانية\n"
                    "• استخدام القوة\n"
                    "• نهايات مظلمة"
                )
            },
            "trust": {
                "title": "🤝 الثقة",
                "description": (
                    "الثقة تمثل علاقتك بالشخصيات الرئيسية.\n\n"
                    "**أهم الشخصيات:**\n"
                    "• أرين - رفيقك في الرحلة\n"
                    "• إيلارا - حارسة الغابة\n"
                    "• نوفا - قائدة المقاومة\n\n"
                    "**كيف تزيد الثقة؟**\n"
                    "• مساعدتهم في الأزمات\n"
                    "• اختيارات تدعمهم\n"
                    "• الصدق معهم\n\n"
                    "**فوائد الثقة العالية:**\n"
                    "• مساعدتهم في المعارك\n"
                    "• معلومات سرية\n"
                    "• نهايات أفضل"
                )
            },
            "crafting": {
                "title": "🔨 الصياغة (Crafting)",
                "description": (
                    "اصنع عناصر أقوى بدمج المواد.\n\n"
                    "**كيف تعمل؟**\n"
                    "1️⃣ اجمع المواد (شظايا، بلورات...)\n"
                    "2️⃣ استخدم `/دمج` لرؤية الوصفات\n"
                    "3️⃣ اختر الوصفة التي تريد\n"
                    "4️⃣ أكد الصياغة\n\n"
                    "**وصفات مهمة:**\n"
                    "• شظية نقية: 10 شظايا صغيرة + قلب كريستال\n"
                    "• كريستال نيكسس: 5 شظايا نقية + 5 نواة ظلام\n"
                    "• كأس الحقيقة: 3 قلوب كريستال + كرة ذكريات\n\n"
                    "**نصائح:**\n"
                    "• بعض الوصفات تحتاج مستوى معين\n"
                    "• وصفات نادرة تفتح فقط في نهايات معينة"
                )
            },
            "chance": {
                "title": "🎲 نظام الاحتمالات",
                "description": (
                    "بعض الخيارات تعتمد على الحظ.\n\n"
                    "**كيف يعمل؟**\n"
                    "• كل خيار له نسبة نجاح (مثلاً 70%)\n"
                    "• إذا نجحت، تسلك مساراً\n"
                    "• إذا فشلت، تسلك مساراً آخر\n\n"
                    "**العوامل المؤثرة:**\n"
                    "• مستوى الشخصية\n"
                    "• سمعة اللاعب\n"
                    "• عناصر خاصة (مثل بوصلة سحرية)\n"
                    "• توجه (نور/ظلام)\n\n"
                    "**نصائح:**\n"
                    "• فكر قبل المخاطرة\n"
                    "• استخدم عناصر تزيد فرص النجاح\n"
                    "• بعض الفشل يقود لمغامرات جديدة!"
                )
            }
        }
        
        exp = explanations.get(الموضوع)
        if not exp:
            embed = discord.Embed(
                title="❌ موضوع غير معروف",
                description="استخدم `/مساعدة` لرؤية المواضيع المتاحة",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=exp["title"],
            description=exp["description"],
            color=self.bot.world_colors["info"]
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /أسئلة - أسئلة شائعة
    # ============================================
    
    @app_commands.command(name="أسئلة", description="❓ أسئلة شائعة عن اللعبة")
    @rate_limit("أسئلة")
    async def faq_command(self, interaction: discord.Interaction):
        """عرض الأسئلة الشائعة"""
        
        embed = discord.Embed(
            title="❓ أسئلة شائعة",
            description="أجوبة لأكثر الأسئلة تكراراً",
            color=0x3498db
        )
        
        faqs = [
            ("❔ كيف أبدأ اللعب؟", "استخدم `/ابدأ` واختر عالم الفانتازيا للبدء."),
            ("❔ ماذا أفعل إذا علقت في القصة؟", "استخدم `/استمر` لمتابعة آخر نقطة."),
            ("❔ كيف أزيد مستواي؟", "كل قرار تاخذه يمنحك خبرة. المهام الجانبية تعطي خبرة إضافية."),
            ("❔ كيف أفتح العوالم الأخرى؟", "أكمل عالم الفانتازيا لفتح الماضي، وهكذا."),
            ("❔ ماذا يحدث إذا وصل الفساد 100؟", "تصل إلى نهاية الظلام في عالمك الحالي."),
            ("❔ كيف أحصل على عناصر نادرة؟", "المكافآت اليومية، الإنجازات، الصياغة، الاستكشاف."),
            ("❔ هل يمكنني اللعب مع أصدقائي؟", "لكل لاعب قصته المستقلة، لكن يمكنكم تبادل العناصر."),
            ("❔ ماذا لو أخطأت في اختيار؟", "كل اختيار جزء من رحلتك. جرب مسارات مختلفة في المرات القادمة!")
        ]
        
        for q, a in faqs:
            embed.add_field(name=q, value=a, inline=False)
        
        embed.set_footer(text="أسئلة أخرى؟ استخدم /مساعدة")
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /روابط - روابط مفيدة
    # ============================================
    
    @app_commands.command(name="روابط", description="🔗 روابط مفيدة")
    @rate_limit("روابط")
    async def links_command(self, interaction: discord.Interaction):
        """عرض روابط مفيدة"""
        
        embed = discord.Embed(
            title="🔗 روابط مفيدة",
            description="روابط قد تهمك",
            color=0x9b59b6
        )
        
        embed.add_field(
            name="📚 دليل اللعبة",
            value=(
                "• استخدم `/مساعدة` لعرض الأوامر\n"
                "• استخدم `/شرح` لشرح أنظمة معينة\n"
                "• استخدم `/أسئلة` للأسئلة الشائعة"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💬 مجتمع النيكسس",
            value=(
                "• شارك نظرياتك في قناة `الدردشة`\n"
                "• اعرض إنجازاتك في `الستايالات`\n"
                "• ناقش مع الآخرين"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🐛 الإبلاغ عن أخطاء",
            value=(
                "إذا وجدت خطأ في القصة:\n"
                "• راسل المطورين\n"
                "• استخدم `/تقرير` (قريباً)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💡 اقتراحات",
            value=(
                "لديك فكرة لتطوير اللعبة؟\n"
                "شاركها معنا!"
            ),
            inline=False
        )
        
        embed.set_footer(text="شكراً لكونك جزءاً من النيكسس!")
        
        await interaction.response.send_message(embed=embed)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(HelpCommands(bot))
    logger.info("✅ تم تحميل أوامر المساعدة")
