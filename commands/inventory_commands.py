# commands/inventory_commands.py - أوامر المخزون والعناصر
# /مخزني, /استخدم, /دمج, /بيع, /هدية

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional, List
import random

from core.bot import NexusBot
from core.constants import WORLD_EMOJIS, WORLD_NAMES
from game.items import (
    ALL_ITEMS, CRAFTING_RECIPES, get_item, get_items_by_world,
    can_use_item, apply_item_effects, can_craft, craft_item,
    ItemRarity, ItemType
)
from game.leveling import LevelSystem
from ui.views import ConfirmView, PaginatedView
from ui.embeds import NexusEmbeds
from utils.rate_limiter import rate_limit
from utils.helpers import format_number

logger = logging.getLogger(__name__)


class InventoryCommands(commands.Cog):
    """أوامر المخزون والعناصر"""
    
    def __init__(self, bot: NexusBot):
        self.bot = bot
        self.embeds = NexusEmbeds(bot)
    
    # ============================================
    # أمر /مخزني - عرض المخزون
    # ============================================
    
    @app_commands.command(name="مخزني", description="🎒 اعرض محتويات مخزونك")
    @app_commands.describe(
        الصفحة="رقم الصفحة (اختياري)",
        النوع="تصفية حسب نوع العنصر"
    )
    @app_commands.choices(النوع=[
        app_commands.Choice(name="🧪 جميع العناصر", value="all"),
        app_commands.Choice(name="🧪 جرعات", value="consumable"),
        app_commands.Choice(name="⚡ معدات دائمة", value="permanent"),
        app_commands.Choice(name="🔨 مواد صياغة", value="crafting"),
        app_commands.Choice(name="💎 شظايا", value="shard"),
        app_commands.Choice(name="🔑 مفاتيح", value="key"),
        app_commands.Choice(name="📜 عناصر مهمة", value="quest")
    ])
    @rate_limit("مخزني")
    async def inventory_command(
        self,
        interaction: discord.Interaction,
        الصفحة: Optional[int] = 1,
        النوع: Optional[str] = "all"
    ):
        """عرض محتويات المخزون"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            await self.bot.db.create_player(user_id, interaction.user.name)
            player = await self.bot.db.get_player(user_id)
        
        # الحصول على المخزون
        inventory = await self.bot.db.get_inventory(user_id)
        
        if not inventory:
            embed = discord.Embed(
                title="🎒 مخزونك فارغ",
                description="لم تحصل على أي عناصر بعد. العب أكثر لتحصل على عناصر!",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تصفية حسب النوع
        if النوع != "all":
            filtered = []
            for item in inventory:
                item_data = get_item(item['item_id'])
                if item_data and item_data.type.value == النوع:
                    filtered.append(item)
            inventory = filtered
        
        if not inventory:
            embed = discord.Embed(
                title="🎒 لا توجد عناصر",
                description=f"لا توجد عناصر من نوع '{النوع}' في مخزونك",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # ترتيب العناصر حسب الندرة
        rarity_order = {
            "خرافي": 0,
            "أسطوري": 1,
            "نادر جداً": 2,
            "نادر": 3,
            "شائع": 4
        }
        
        inventory.sort(key=lambda x: rarity_order.get(x.get('rarity', 'شائع'), 5))
        
        # تقسيم إلى صفحات (10 عناصر كل صفحة)
        items_per_page = 10
        pages = []
        
        for i in range(0, len(inventory), items_per_page):
            page_items = inventory[i:i + items_per_page]
            
            embed = discord.Embed(
                title=f"🎒 مخزون {interaction.user.name}",
                color=0x2ecc71
            )
            
            for item in page_items:
                item_id = item['item_id']
                item_data = get_item(item_id)
                
                if item_data:
                    # تحديد لون الندرة
                    rarity_colors = {
                        "خرافي": "🟪",
                        "أسطوري": "🟨",
                        "نادر جداً": "🟥",
                        "نادر": "🟦",
                        "شائع": "⬜"
                    }
                    rarity_color = rarity_colors.get(item_data.rarity.value, "⬜")
                    
                    name = f"{rarity_color} {item.get('item_emoji', '📦')} **{item.get('item_name', item_id)}**"
                    if item['quantity'] > 1:
                        name += f" x{item['quantity']}"
                    
                    value = item_data.description
                    if item_data.usable:
                        value += f"\n*قابل للاستخدام*"
                    
                    embed.add_field(
                        name=name,
                        value=value,
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"📦 **{item.get('item_name', item_id)}** x{item['quantity']}",
                        value="عنصر غير معروف",
                        inline=False
                    )
            
            # إحصائيات سريعة
            total_items = sum(item.get('quantity', 0) for item in inventory)
            unique_items = len(inventory)
            
            embed.set_footer(
 text=f"صفحة {i//items_per_page + 1}/{(len(inventory)-1)//items_per_page + 1} • "
                f"{unique_items} نوع • {total_items} عنصر"
            )
            
            pages.append(embed)
        
        if len(pages) == 1:
            await interaction.response.send_message(embed=pages[0])
        else:
            # عرض مع أزرار التنقل
            view = PaginatedView(interaction.user.id, pages, timeout=120)
            await interaction.response.send_message(
                embed=pages[الصفحة - 1] if 1 <= الصفحة <= len(pages) else pages[0],
                view=view
            )
    
    # ============================================
    # أمر /استخدم - استخدام عنصر
    # ============================================
    
    @app_commands.command(name="استخدم", description="🧪 استخدم عنصراً من مخزونك")
    @app_commands.describe(
        العنصر="معرف العنصر (مثل: potion, pure_shard, ...)"
    )
    @rate_limit("استخدم")
    async def use_item_command(
        self,
        interaction: discord.Interaction,
        العنصر: str
    ):
        """استخدام عنصر من المخزون"""
        
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
        
        item_id = العنصر.lower()
        item_data = get_item(item_id)
        
        if not item_data:
            embed = discord.Embed(
                title="❌ عنصر غير معروف",
                description=f"لا يوجد عنصر باسم '{العنصر}'\nاستخدم `/مخزني` لرؤية عناصرك",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من امتلاك العنصر
        if not await self.bot.db.has_item(user_id, item_id, 1):
            embed = discord.Embed(
                title="❌ عنصر غير موجود",
                description=f"ليس لديك {item_data.emoji} **{item_data.name}** في مخزونك",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من إمكانية الاستخدام
        if not can_use_item(item_data, player):
            embed = discord.Embed(
                title="❌ لا يمكن استخدام هذا العنصر الآن",
                description="قد لا تستوفي المتطلبات اللازمة",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تطبيق التأثيرات
        updates = apply_item_effects(item_data, player)
        
        if updates:
            await self.bot.db.update_player(user_id, updates)
            
            # إزالة العنصر من المخزون
            await self.bot.db.remove_from_inventory(user_id, item_id, 1)
            
            # إضافة خبرة
            xp_gain = 5
            new_xp, level_up, new_level = LevelSystem.add_xp(
                player.get("xp", 0),
                "item_use"
            )
            await self.bot.db.update_player(user_id, {"xp": new_xp})
            
            # إنشاء رسالة النجاح
            embed = discord.Embed(
                title="✅ تم استخدام العنصر",
                description=f"استخدمت {item_data.emoji} **{item_data.name}**",
                color=0x2ecc71
            )
            
            # عرض التأثيرات
            effects_text = []
            for key, value in updates.items():
                if key == "corruption":
                    effects_text.append(f"🌑 **الفساد:** {player.get(key, 0)} → {value}")
                elif key == "alignment":
                    effects_text.append(f"⚖️ **التوجه:** {player.get(key, 'Gray')} → {value}")
                elif key == "shards":
                    effects_text.append(f"💎 **الشظايا:** {player.get(key, 0)} → {value}")
                elif key in ["fantasy_power", "memories", "tech_level", "identity"]:
                    name = {
                        "fantasy_power": "✨ قوة فانتازيا",
                        "memories": "📜 ذكريات",
                        "tech_level": "⚙️ تكنولوجيا",
                        "identity": "🌀 هوية"
                    }.get(key, key)
                    effects_text.append(f"**{name}:** {player.get(key, 0)} → {value}")
            
            if effects_text:
                embed.add_field(name="📊 التغييرات", value="\n".join(effects_text), inline=False)
            
            embed.add_field(name="🌟 خبرة", value=f"+{xp_gain} XP", inline=True)
            
            if level_up:
                embed.add_field(
                    name="⬆️ زيادة مستوى!",
                    value=f"وصلت إلى المستوى {new_level}!",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ لا تأثير",
                description="استخدام هذا العنصر لم يغير شيئاً",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============================================
    # أمر /دمج - صياغة عناصر جديدة
    # ============================================
    
    @app_commands.command(name="دمج", description="🔨 ادمج عناصر لصنع عناصر أقوى")
    @app_commands.describe(
        الوصفة="اسم الوصفة التي تريد صنعها"
    )
    @rate_limit("دمج")
    async def craft_command(
        self,
        interaction: discord.Interaction,
        الوصفة: Optional[str] = None
    ):
        """صياغة عناصر جديدة"""
        
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
        
        # إذا لم يحدد وصفة، عرض كل الوصفات المتاحة
        if not الوصفة:
            await self._show_crafting_recipes(interaction, player)
            return
        
        recipe_id = الوصفة.lower().replace(" ", "_")
        recipe = CRAFTING_RECIPES.get(recipe_id)
        
        if not recipe:
            embed = discord.Embed(
                title="❌ وصفة غير معروفة",
                description=f"لا توجد وصفة باسم '{الوصفة}'\nاستخدم `/دمج` بدون معامل لرؤية الوصفات المتاحة",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # الحصول على مخزون اللاعب كقاموس
        inventory_items = await self.bot.db.get_inventory(user_id)
        inventory_dict = {item['item_id']: item['quantity'] for item in inventory_items}
        
        # التحقق من إمكانية الصياغة
        if not can_craft(recipe_id, inventory_dict, player.get("level", 1)):
            embed = discord.Embed(
                title="❌ لا يمكنك صنع هذا العنصر",
                color=0xf39c12
            )
            
            # عرض المتطلبات
            requirements = []
            
            # المستوى
            req_level = recipe.get("level_required", 1)
            if player.get("level", 1) < req_level:
                requirements.append(f"• المستوى {req_level} مطلوب (لديك {player.get('level', 1)})")
            
            # المواد
            for ingredient, qty in recipe["ingredients"].items():
                item = get_item(ingredient)
                name = item.name if item else ingredient
                have = inventory_dict.get(ingredient, 0)
                if have < qty:
                    requirements.append(f"• {name} x{qty} (لديك {have})")
            
            if requirements:
                embed.add_field(name="📋 المتطلبات الناقصة", value="\n".join(requirements), inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # طلب تأكيد
        result_item = get_item(recipe["result"])
        
        embed = discord.Embed(
            title="🔨 تأكيد الصياغة",
            description=f"هل تريد صنع **{result_item.emoji} {result_item.name}**؟",
            color=0x3498db
        )
        
        # عرض المواد المطلوبة
        ingredients_text = []
        for ingredient, qty in recipe["ingredients"].items():
            item = get_item(ingredient)
            name = item.name if item else ingredient
            ingredients_text.append(f"• {item.emoji if item else '📦'} {name} x{qty}")
        
        embed.add_field(name="📦 المواد المطلوبة", value="\n".join(ingredients_text), inline=False)
        
        # عرض النتيجة
        embed.add_field(
            name="🎁 النتيجة",
            value=f"{result_item.emoji} **{result_item.name}** x{recipe['quantity']}\n{result_item.description}",
            inline=False
        )
        
        async def confirm(interaction: discord.Interaction):
            # تنفيذ الصياغة
            result = craft_item(recipe_id, inventory_dict)
            
            if result:
                # تحديث المخزون في قاعدة البيانات
                for ingredient, qty in recipe["ingredients"].items():
                    await self.bot.db.remove_from_inventory(user_id, ingredient, qty)
                
                await self.bot.db.add_to_inventory(
                    user_id,
                    recipe["result"],
                    result_item.name,
                    recipe["quantity"]
                )
                
                # إضافة خبرة
                new_xp, level_up, new_level = LevelSystem.add_xp(
                    player.get("xp", 0),
                    "craft"
                )
                await self.bot.db.update_player(user_id, {"xp": new_xp})
                
                embed = discord.Embed(
                    title="✅ تمت الصياغة بنجاح!",
                    description=f"صنعت {result_item.emoji} **{result_item.name}** x{recipe['quantity']}",
                    color=0x2ecc71
                )
                
                if level_up:
                    embed.add_field(name="⬆️ زيادة مستوى!", value=f"وصلت إلى المستوى {new_level}!")
                
                await interaction.response.edit_message(embed=embed, view=None)
            else:
                embed = discord.Embed(
                    title="❌ فشلت الصياغة",
                    description="حدث خطأ أثناء الصياغة",
                    color=0xe74c3c
                )
                await interaction.response.edit_message(embed=embed, view=None)
        
        async def cancel(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ تم الإلغاء",
                description="تم إلغاء عملية الصياغة",
                color=0x95a5a6
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        view = ConfirmView(interaction.user.id, confirm, cancel)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def _show_crafting_recipes(self, interaction: discord.Interaction, player: dict):
        """عرض وصفات الصياغة المتاحة"""
        
        embed = discord.Embed(
            title="🔨 وصفات الصياغة",
            description="اختر وصفة لصنع عناصر جديدة",
            color=0x3498db
        )
        
        # الحصول على مخزون اللاعب
        inventory_items = await self.bot.db.get_inventory(interaction.user.id)
        inventory_dict = {item['item_id']: item['quantity'] for item in inventory_items}
        
        # تجميع الوصفات حسب العالم
        recipes_by_world = {}
        for recipe_id, recipe in CRAFTING_RECIPES.items():
            world = recipe.get("world", "general")
            if world not in recipes_by_world:
                recipes_by_world[world] = []
            recipes_by_world[world].append((recipe_id, recipe))
        
        # عرض الوصفات المتاحة
        for world_id, recipes in recipes_by_world.items():
            world_name = WORLD_NAMES.get(world_id, "عام")
            world_emoji = WORLD_EMOJIS.get(world_id, "🌍")
            
            recipes_text = []
            for recipe_id, recipe in recipes[:5]:  # حد أقصى 5 لكل عالم
                result_item = get_item(recipe["result"])
                if not result_item:
                    continue
                
                # التحقق من إمكانية الصنع
                can_make = can_craft(recipe_id, inventory_dict, player.get("level", 1))
                status = "✅" if can_make else "❌"
                
                recipes_text.append(
                    f"{status} **{result_item.emoji} {result_item.name}**\n"
                    f"  المستوى {recipe.get('level_required', 1)}"
                )
            
            if recipes_text:
                embed.add_field(
                    name=f"{world_emoji} {world_name}",
                    value="\n".join(recipes_text),
                    inline=False
                )
        
        embed.add_field(
            name="💡 كيفية الاستخدام",
            value="استخدم `/دمج اسم_الوصفة` لصنع عنصر\nمثال: `/دمج pure_shard`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ============================================
    # أمر /بيع - بيع عنصر
    # ============================================
    
    @app_commands.command(name="بيع", description="💰 بع عنصراً من مخزونك")
    @app_commands.describe(
        العنصر="معرف العنصر",
        الكمية="الكمية (افتراضي 1)"
    )
    @rate_limit("بيع")
    async def sell_command(
        self,
        interaction: discord.Interaction,
        العنصر: str,
        الكمية: Optional[int] = 1
    ):
        """بيع عنصر والحصول على عملات"""
        
        user_id = interaction.user.id
        player = await self.bot.db.get_player(user_id)
        
        if not player:
            embed = discord.Embed(
                title="❌ لا يوجد تقدم",
                description="لم تبدأ رحلتك بعد!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        item_id = العنصر.lower()
        item_data = get_item(item_id)
        
        if not item_data:
            embed = discord.Embed(
                title="❌ عنصر غير معروف",
                description=f"لا يوجد عنصر باسم '{العنصر}'",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من الكمية
        if الكمية < 1:
            embed = discord.Embed(
                title="❌ كمية غير صالحة",
                description="يجب أن تكون الكمية 1 على الأقل",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من امتلاك العنصر
        if not await self.bot.db.has_item(user_id, item_id, الكمية):
            embed = discord.Embed(
                title="❌ كمية غير كافية",
                description=f"ليس لديك {الكمية} من {item_data.emoji} **{item_data.name}**",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من إمكانية البيع
        if not item_data.tradeable:
            embed = discord.Embed(
                title="❌ لا يمكن بيع هذا العنصر",
                description=f"{item_data.emoji} **{item_data.name}** عنصر غير قابل للبيع",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # حساب السعر
        base_price = item_data.value
        total_price = base_price * الكمية
        
        # تطبيق تأثير السمعة على السعر
        reputation = player.get("reputation", 0)
        rep_effects = ReputationSystem.get_effects(reputation)
        
        if "discount" in rep_effects and rep_effects["discount"] < 1.0:
            # السمعة العالية تعطي سعر بيع أفضل
            total_price = int(total_price / rep_effects["discount"])
        elif "tax" in rep_effects and rep_effects["tax"] > 1.0:
            # السمعة المنخفضة تخفض سعر البيع
            total_price = int(total_price / rep_effects["tax"])
        
        # طلب تأكيد
        embed = discord.Embed(
            title="💰 تأكيد البيع",
            description=f"هل تريد بيع {الكمية} من {item_data.emoji} **{item_data.name}**؟",
            color=0xf1c40f
        )
        
        embed.add_field(
            name="💵 السعر",
            value=f"{total_price} 💰 قطعة ذهبية",
            inline=False
        )
        
        async def confirm(interaction: discord.Interaction):
            # إزالة العنصر وإضافة العملات
            await self.bot.db.remove_from_inventory(user_id, item_id, الكمية)
            
            # إضافة العملات (سنستخدم gold_coin)
            await self.bot.db.add_to_inventory(
                user_id,
                "gold_coin",
                "🪙 عملة ذهبية",
                total_price
            )
            
            embed = discord.Embed(
                title="✅ تم البيع",
                description=f"بعت {الكمية} من {item_data.emoji} **{item_data.name}** وحصلت على {total_price} 🪙",
                color=0x2ecc71
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        async def cancel(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ تم الإلغاء",
                description="تم إلغاء عملية البيع",
                color=0x95a5a6
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        view = ConfirmView(interaction.user.id, confirm, cancel)
        await interaction.response.send_message(embed=embed, view=view)
    
    # ============================================
    # أمر /هدية - إهداء عنصر للاعب آخر
    # ============================================
    
    @app_commands.command(name="هدية", description="🎁 أهدِ عنصراً للاعب آخر")
    @app_commands.describe(
        اللاعب="اللاعب المستلم",
        العنصر="معرف العنصر",
        الكمية="الكمية (افتراضي 1)"
    )
    @rate_limit("هدية")
    async def gift_command(
        self,
        interaction: discord.Interaction,
        اللاعب: discord.User,
        العنصر: str,
        الكمية: Optional[int] = 1
    ):
        """إهداء عنصر للاعب آخر"""
        
        # منع إهداء النفس
        if اللاعب.id == interaction.user.id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك إهداء نفسك! استخدم `/استخدم` بدلاً من ذلك",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_id = interaction.user.id
        target_id = اللاعب.id
        
        player = await self.bot.db.get_player(user_id)
        target = await self.bot.db.get_player(target_id)
        
        if not player:
            embed = discord.Embed(
                title="❌ لا يوجد تقدم",
                description="لم تبدأ رحلتك بعد!",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not target:
            # إنشاء حساب للهدف إذا لم يكن موجوداً
            await self.bot.db.create_player(target_id, اللاعب.name)
        
        item_id = العنصر.lower()
        item_data = get_item(item_id)
        
        if not item_data:
            embed = discord.Embed(
                title="❌ عنصر غير معروف",
                description=f"لا يوجد عنصر باسم '{العنصر}'",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من الكمية
        if الكمية < 1:
            embed = discord.Embed(
                title="❌ كمية غير صالحة",
                description="يجب أن تكون الكمية 1 على الأقل",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من امتلاك العنصر
        if not await self.bot.db.has_item(user_id, item_id, الكمية):
            embed = discord.Embed(
                title="❌ كمية غير كافية",
                description=f"ليس لديك {الكمية} من {item_data.emoji} **{item_data.name}**",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # التحقق من إمكانية التداول
        if not item_data.tradeable:
            embed = discord.Embed(
                title="❌ لا يمكن إهداء هذا العنصر",
                description=f"{item_data.emoji} **{item_data.name}** عنصر غير قابل للتداول",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # طلب تأكيد
        embed = discord.Embed(
            title="🎁 تأكيد الإهداء",
            description=f"هل تريد إهداء {الكمية} من {item_data.emoji} **{item_data.name}** إلى {اللاعب.mention}؟",
            color=0x9b59b6
        )
        
        async def confirm(interaction: discord.Interaction):
            # إزالة من المرسل
            await self.bot.db.remove_from_inventory(user_id, item_id, الكمية)
            
            # إضافة إلى المستلم
            await self.bot.db.add_to_inventory(
                target_id,
                item_id,
                item_data.name,
                الكمية
            )
            
            embed = discord.Embed(
                title="✅ تمت الإهداء",
                description=f"أهديت {الكمية} من {item_data.emoji} **{item_data.name}** إلى {اللاعب.mention}",
                color=0x2ecc71
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            # إرسال رسالة خاصة للمستلم
            try:
                dm_embed = discord.Embed(
                    title="🎁 هدية جديدة!",
                    description=f"استلمت {الكمية} من {item_data.emoji} **{item_data.name}** من {interaction.user.mention}",
                    color=0x9b59b6
                )
                await اللاعب.send(embed=dm_embed)
            except:
                pass
        
        async def cancel(interaction: discord.Interaction):
            embed = discord.Embed(
                title="❌ تم الإلغاء",
                description="تم إلغاء عملية الإهداء",
                color=0x95a5a6
            )
            await interaction.response.edit_message(embed=embed, view=None)
        
        view = ConfirmView(interaction.user.id, confirm, cancel)
        await interaction.response.send_message(embed=embed, view=view)


# ============================================
# إضافة الكوج إلى البوت
# ============================================

async def setup(bot: NexusBot):
    await bot.add_cog(InventoryCommands(bot))
    logger.info("✅ تم تحميل أوامر المخزون")
