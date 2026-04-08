import bpy
from typing import Set, Dict, List, Optional
from bpy.types import (
    Operator, 
    Panel, 
    Context, 
    UILayout, 
    WindowManager,
    Event
)
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .ui_utils import UIStyle, draw_section_header, wrap_text_label
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t, get_languages_list
from ..core.armature_validation import AvatarToolkit_OT_HighlightProblemBones, AvatarToolkit_OT_ClearBoneHighlighting

class AvatarToolkit_OT_TranslationRestartPopup(Operator):
    """Popup dialog shown after language change to inform about restart requirement"""
    bl_idname: str = "avatar_toolkit.translation_restart_popup"
    bl_label: str = t("Language.changed.title")
    
    def execute(self, context: Context) -> Set[str]:
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        wm: WindowManager = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        col = layout.column(align=True)
        col.label(text=t("Language.changed.success"))
        col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
        wrap_text_label(col, t("Language.changed.restart"), max_length=50)

class AvatarToolKit_PT_SettingsPanel(Panel):
    """Settings panel for Avatar Toolkit containing language preferences"""
    bl_label: str = t("Settings.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit_settings"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('settings')
    bl_options = set() if not should_open_by_default('SETTINGS') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw the settings panel layout with language selection"""
        layout: UILayout = self.layout
        props = context.scene.avatar_toolkit
        
        # Language Settings
        col = draw_section_header(layout, t("Settings.language"), icon='WORLD')
        col.prop(props, "language", text="")
        
        # Validation Settings with help text
        col = draw_section_header(layout, t("Settings.validation_mode"), icon='CHECKMARK')
        col.prop(props, "validation_mode", text="")
        # Help text for validation mode
        col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
        wrap_text_label(col, "Select how strictly to validate armature bone structure and naming conventions.", max_length=40)
        
        # Bone Highlighting Settings
        col = draw_section_header(layout, t("Settings.bone_highlighting"), icon='BONE_DATA')
        col.prop(props, "highlight_problem_bones")
        if props.highlight_problem_bones:
            col.operator(AvatarToolkit_OT_HighlightProblemBones.bl_idname, icon='COLOR')
        else:
            col.operator(AvatarToolkit_OT_ClearBoneHighlighting.bl_idname, icon='X')

        # Debug Settings
        debug_box = layout.box()
        col = debug_box.column()
        row = col.row(align=True)
        row.prop(props, "debug_expand", 
                icon="TRIA_DOWN" if props.debug_expand 
                else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text=t("Settings.debug"), icon='CONSOLE')
        
        if props.debug_expand:
            col = debug_box.column(align=True)
            col.prop(props, "enable_logging")
            
            if props.enable_logging:
                col.prop(props, "log_level")