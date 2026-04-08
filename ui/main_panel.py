import bpy
from typing import Optional, Set
from bpy.types import Panel, Context, UILayout
from .ui_utils import UIStyle, wrap_text_label
from ..core.translations import t

CATEGORY_NAME: str = "Avatar Toolkit"

def draw_title(self: Panel) -> None:
    """Draw the main panel title and description"""
    layout: UILayout = self.layout
    box: UILayout = layout.box()
    col: UILayout = box.column(align=True)
    
    # Add a nice header
    row: UILayout = col.row()
    row.scale_y: float = 1.2
    row.label(text=t("AvatarToolkit.label"), icon='ARMATURE_DATA')
    
    # Description
    col.separator(factor=UIStyle.SECTION_SEPARATOR_FACTOR)
    description = " ".join([
        t("AvatarToolkit.desc1"),
        t("AvatarToolkit.desc2"),
        t("AvatarToolkit.desc3")
    ])
    wrap_text_label(col, description, max_length=50)

class AvatarToolKit_PT_AvatarToolkitPanel(Panel):
    """Main panel for Avatar Toolkit containing general information and settings"""
    bl_label: str = t("AvatarToolkit.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME

    def draw(self, context: Context) -> None:
        """Draw the main panel layout"""
        draw_title(self)
