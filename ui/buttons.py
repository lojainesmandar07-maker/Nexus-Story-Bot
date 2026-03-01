# ui/buttons.py - أنماط وتصميم الأزرار المتقدمة
# هذا الملف مسؤول عن تخصيص شكل وسلوك الأزرار

import discord
from discord.ui import Button, View
from typing import Optional, Dict, Any, List, Callable
import random

from core.constants import BUTTON_STYLES, WORLD_EMOJIS


class NexusButton(Button):
    """
    كلاس أساسي للأزرار - يرث من Button
    يضيف خصائص مشتركة لكل الأزرار
    """
    
    def __init__(
        self,
        label: str,
        emoji: Optional[str] = None,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        custom_id: Optional[str] = None,
        row: Optional[int] = None,
        disabled: bool = False
    ):
        super().__init__(
            label=label,
            emoji=emoji,
            style=style,
            custom_id=custom_id,
            row=row,
            disabled=disabled
        )
        
        # إحصائيات الزر
        self.click_count = 0
        self.created_at = discord.utils.utcnow()
    
    async def callback(self, interaction: discord.Interaction):
        """يتم استدعاؤها عند الضغط على الزر"""
        self.click_count += 1
        # يتم override في الأزرار المخصصة


# ============================================
# أزرار القصة
# ============================================

class StoryChoiceButton(NexusButton):
    """
    زر يمثل خياراً في القصة
    هذا أكثر زر استخداماً
    """
    
    def __init__(
        self,
        choice_data: Dict[str, Any],
        choice_index: int,
        world_id: str,
        part_id: str,
        user_id: int,
        row: int
    ):
        # تحديد النمط حسب نوع الخيار
        style = self._get_style(choice_data)
        
        # إنشاء custom_id فريد
        custom_id = f"nexus_{world_id}_{part_id}_{choice_index}"
        
        super().__init__(
            label=choice_data.get('text', f'خيار {choice_index+1}')[:80],
            emoji=choice_data.get('emoji'),
            style=style,
            custom_id=custom_id,
            row=row
        )
        
        self.choice_data = choice_data
        self.choice_index = choice_index
        self.world_id = world_id
        self.part_id = part_id
        self.user_id = user_id
        self.bot = None  # يضاف لاحقاً من الكولباك
    
    def _get_style(self, choice: Dict) -> discord.ButtonStyle:
        """تحديد لون الزر حسب نوع الخيار"""
        text = choice.get('text', '').lower()
        emoji = choice.get('emoji', '')
        
        # أنماط مختلفة
        if '⚔️' in emoji or any(word in text for word in ['قتال', 'هاجم', 'اضرب', 'واجه']):
            return BUTTON_STYLES['combat']  # أحمر
        
        elif '🔍' in emoji or any(word in text for word in ['استكشف', 'بحث', 'افحص', 'انظر']):
            return BUTTON_STYLES['explore']  # أزرق
        
        elif '💬' in emoji or any(word in text for word in ['تحدث', 'حوار', 'اسأل', 'كلم']):
            return BUTTON_STYLES['talk']  # رمادي
        
        elif '🏃' in emoji or any(word in text for word in ['اهرب', 'هروب', 'ارحل', 'انسحب']):
            return BUTTON_STYLES['flee']  # رمادي
        
        elif '💎' in emoji or any(word in text for word in ['شظية', 'كنز', 'جمع']):
            return BUTTON_STYLES['shard']  # أخضر
        
        elif '💰' in emoji or any(word in text for word in ['مكافأة', 'نقود', 'شراء']):
            return BUTTON_STYLES['success']  # أخضر
        
        elif '🤝' in emoji or any(word in text for word in ['صادق', 'ساعد', 'تعاون']):
            return BUTTON_STYLES['primary']  # أزرق
        
        elif '🕊️' in emoji or any(word in text for word in ['سامح', 'ارحم', 'تسامح']):
            return BUTTON_STYLES['success']  # أخضر
        
        else:
            return BUTTON_STYLES['primary']  # أزرق عادي
    
    async def callback(self, interaction: discord.Interaction):
        """معالجة الضغط على الزر"""
        # التحقق من أن المستخدم هو صاحب القصة
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذه القصة ليست لك! ابدأ رحلتك الخاصة بـ `/ابدأ`",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تمرير المعالجة للـ view
        await self.view.on_choice_selected(interaction, self.choice_index, self.choice_data)


# ============================================
# أزرار العوالم
# ============================================

class WorldButton(NexusButton):
    """زر لاختيار عالم"""
    
    def __init__(self, world_id: str, world_name: str, emoji: str, unlocked: bool, row: int):
        style = discord.ButtonStyle.primary if unlocked else discord.ButtonStyle.secondary
        disabled = not unlocked
        
        super().__init__(
            label=world_name,
            emoji=emoji,
            style=style,
            custom_id=f"world_select_{world_id}",
            row=row,
            disabled=disabled
        )
        
        self.world_id = world_id
        self.unlocked = unlocked
    
    async def callback(self, interaction: discord.Interaction):
        if not self.unlocked:
            embed = discord.Embed(
                title="🔒 عالم مقفل",
                description="أكمل العالم السابق أولاً لفتح هذا العالم",
                color=0xf39c12
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # إرسال إشارة للـ view بالعالم المختار
        await self.view.on_world_selected(interaction, self.world_id)


# ============================================
# أزرار التأكيد
# ============================================

class ConfirmButton(NexusButton):
    """زر تأكيد (نعم)"""
    
    def __init__(self, row: int = 0):
        super().__init__(
            label="نعم",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id="confirm_yes",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.on_confirm(interaction)


class CancelButton(NexusButton):
    """زر إلغاء (لا)"""
    
    def __init__(self, row: int = 0):
        super().__init__(
            label="لا",
            emoji="❌",
            style=discord.ButtonStyle.danger,
            custom_id="confirm_no",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.on_cancel(interaction)


# ============================================
# أزرار المخزون
# ============================================

class UseItemButton(NexusButton):
    """زر استخدام عنصر من المخزون"""
    
    def __init__(self, item_data: Dict, user_id: int, row: int):
        super().__init__(
            label=f"استخدم {item_data.get('item_name', 'عنصر')}",
            emoji=item_data.get('item_emoji', '📦'),
            style=discord.ButtonStyle.success,
            custom_id=f"use_item_{item_data.get('item_id')}_{user_id}",
            row=row
        )
        
        self.item_data = item_data
        self.user_id = user_id
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        await self.view.on_item_used(interaction, self.item_data)


# ============================================
# أزرار التنقل
# ============================================

class NextPageButton(NexusButton):
    """زر الصفحة التالية"""
    
    def __init__(self, current_page: int, max_page: int, row: int = 0):
        disabled = current_page >= max_page
        
        super().__init__(
            label="التالي",
            emoji="⏩",
            style=discord.ButtonStyle.primary,
            custom_id=f"next_page_{current_page}",
            row=row,
            disabled=disabled
        )
        
        self.current_page = current_page
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.on_next_page(interaction, self.current_page + 1)


class PrevPageButton(NexusButton):
    """زر الصفحة السابقة"""
    
    def __init__(self, current_page: int, row: int = 0):
        disabled = current_page <= 1
        
        super().__init__(
            label="السابق",
            emoji="⏪",
            style=discord.ButtonStyle.primary,
            custom_id=f"prev_page_{current_page}",
            row=row,
            disabled=disabled
        )
        
        self.current_page = current_page
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.on_prev_page(interaction, self.current_page - 1)


class BackButton(NexusButton):
    """زر العودة للقائمة الرئيسية"""
    
    def __init__(self, row: int = 0):
        super().__init__(
            label="عودة",
            emoji="🔙",
            style=discord.ButtonStyle.secondary,
            custom_id="back_button",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.on_back(interaction)


# ============================================
# أزرار معلوماتية
# ============================================

class InfoButton(NexusButton):
    """زر معلومات إضافية"""
    
    def __init__(self, info_text: str, row: int = 0):
        super().__init__(
            label="معلومات",
            emoji="ℹ️",
            style=discord.ButtonStyle.secondary,
            custom_id="info_button",
            row=row
        )
        
        self.info_text = info_text
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="ℹ️ معلومات",
            description=self.info_text,
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class HelpButton(NexusButton):
    """زر مساعدة سريعة"""
    
    def __init__(self, row: int = 0):
        super().__init__(
            label="مساعدة",
            emoji="❓",
            style=discord.ButtonStyle.secondary,
            custom_id="help_button",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="❓ مساعدة سريعة",
            description=(
                "**🎮 طريقة اللعب**\n"
                "• اختر خياراتك بحكمة - كل قرار يغير مسار القصة\n"
                "• راقب الفساد - لا تدعه يسيطر عليك\n"
                "• اجمع الشظايا لتصبح أقوى\n"
                "• أكمل العوالم الأربعة لتصبح أسطورة\n\n"
                "**📝 الأوامر**\n"
                "• /ابدأ - بدء رحلة جديدة\n"
                "• /استمر - متابعة الرحلة\n"
                "• /حالتي - عرض إحصائياتك\n"
                "• /مساعدة - عرض المساعدة الكاملة"
            ),
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================
# أزرار إدارية
# ============================================

class AdminButton(NexusButton):
    """زر للمشرفين فقط"""
    
    def __init__(self, label: str, emoji: str, command: str, admin_only: bool = True, row: int = 0):
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.danger,
            custom_id=f"admin_{command}",
            row=row
        )
        
        self.command = command
        self.admin_only = admin_only
    
    async def callback(self, interaction: discord.Interaction):
        # التحقق من صلاحيات المشرف
        if self.admin_only and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الأمر للمشرفين فقط!", ephemeral=True)
            return
        
        await self.view.on_admin_command(interaction, self.command)


# ============================================
# أزرار الصفحات المتعددة
# ============================================

class PaginatedView(View):
    """
    عرض متعدد الصفحات مع أزرار تنقل
    يستخدم لعرض القوائم الطويلة
    """
    
    def __init__(self, user_id: int, pages: List[Any], timeout: float = 180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.pages = pages
        self.current_page = 1
        self.max_page = len(pages)
        
        self._update_buttons()
    
    def _update_buttons(self):
        """تحديث حالة الأزرار حسب الصفحة الحالية"""
        self.clear_items()
        
        # زر الصفحة السابقة
        if self.current_page > 1:
            self.add_item(PrevPageButton(self.current_page))
        
        # عرض رقم الصفحة
        page_label = Button(
            label=f"صفحة {self.current_page}/{self.max_page}",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            row=0
        )
        self.add_item(page_label)
        
        # زر الصفحة التالية
        if self.current_page < self.max_page:
            self.add_item(NextPageButton(self.current_page, self.max_page))
        
        # زر العودة
        self.add_item(BackButton(row=1))
    
    async def on_next_page(self, interaction: discord.Interaction, page: int):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        self.current_page = page
        self._update_buttons()
        
        # تحديث الرسالة بالصفحة الجديدة
        await interaction.response.edit_message(
            embed=self.pages[self.current_page - 1],
            view=self
        )
    
    async def on_prev_page(self, interaction: discord.Interaction, page: int):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        self.current_page = page
        self._update_buttons()
        
        await interaction.response.edit_message(
            embed=self.pages[self.current_page - 1],
            view=self
        )
    
    async def on_back(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        await self.on_timeout()
        await interaction.response.edit_message(view=None)


# ============================================
# أزرار الصياغة (Crafting)
# ============================================

class CraftButton(NexusButton):
    """زر صياغة عنصر"""
    
    def __init__(self, recipe_data: Dict, user_id: int, can_craft: bool, row: int):
        super().__init__(
            label=f"اصنع {recipe_data.get('result', {}).get('name', 'عنصر')}",
            emoji="🔨",
            style=discord.ButtonStyle.success if can_craft else discord.ButtonStyle.secondary,
            custom_id=f"craft_{recipe_data.get('id', 'unknown')}_{user_id}",
            row=row,
            disabled=not can_craft
        )
        
        self.recipe_data = recipe_data
        self.user_id = user_id
        self.can_craft = can_craft
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        if not self.can_craft:
            await interaction.response.send_message("❌ لا تملك المواد اللازمة!", ephemeral=True)
            return
        
        await self.view.on_craft(interaction, self.recipe_data)


# ============================================
# دوال مساعدة لإنشاء الأزرار
# ============================================

def create_story_buttons(
    choices: List[Dict],
    world_id: str,
    part_id: str,
    user_id: int
) -> List[StoryChoiceButton]:
    """إنشاء أزرار للخيارات في القصة"""
    buttons = []
    
    for i, choice in enumerate(choices):
        row = i // 3  # كل 3 أزرار في سطر
        button = StoryChoiceButton(choice, i, world_id, part_id, user_id, row)
        buttons.append(button)
    
    return buttons


def create_world_buttons(
    available_worlds: List[str],
    unlocked_worlds: List[str]
) -> List[WorldButton]:
    """إنشاء أزرار اختيار العوالم"""
    buttons = []
    
    for i, world_id in enumerate(available_worlds):
        from story.worlds import world_manager
        world = world_manager.get_world(world_id)
        
        if world:
            unlocked = world_id in unlocked_worlds
            row = i // 2  # كل 2 في سطر
            button = WorldButton(world_id, world.NAME, world.EMOJI, unlocked, row)
            buttons.append(button)
    
    return buttons


def create_confirm_buttons() -> List[NexusButton]:
    """إنشاء أزرار تأكيد (نعم/لا)"""
    return [ConfirmButton(0), CancelButton(0)]


# ============================================
# تصدير الكلاسات والدوال
# ============================================

__all__ = [
    'NexusButton',
    'StoryChoiceButton',
    'WorldButton',
    'ConfirmButton',
    'CancelButton',
    'UseItemButton',
    'NextPageButton',
    'PrevPageButton',
    'BackButton',
    'InfoButton',
    'HelpButton',
    'AdminButton',
    'PaginatedView',
    'CraftButton',
    'create_story_buttons',
    'create_world_buttons',
    'create_confirm_buttons'
]
