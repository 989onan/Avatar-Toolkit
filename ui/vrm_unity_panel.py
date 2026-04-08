import bpy
from bpy.types import Panel, Context, UILayout
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t
from ..core.common import get_active_armature
from ..core.vrm_unity_converter import detect_vrm_armature
from ..functions.tools.vrm_unity_conversion import AvatarToolkit_OT_ConvertVRMToUnity


class AvatarToolKit_PT_VRMUnityPanel(Panel):
    """Panel for VRM to Unity conversion tools"""
    bl_label = t("VRM.panel.label")
    bl_idname = "OBJECT_PT_avatar_toolkit_vrm_unity"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order = get_panel_order('vrm_unity')
    bl_options = set() if not should_open_by_default('VRM_UNITY') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw the VRM to Unity conversion panel interface"""
        layout: UILayout = self.layout
        
        # VRM Conversion Tools
        vrm_box: UILayout = layout.box()
        col: UILayout = vrm_box.column(align=True)
        col.label(text=t("VRM.converter.title"), icon='ARMATURE_DATA')
        col.separator(factor=0.5)
        
        # Check if we have an active armature
        armature = get_active_armature(context)
        
        if not armature:
            col.label(text=t("VRM.no_armature_selected"), icon='ERROR')
            col.label(text=t("VRM.select_armature_to_convert"))
            return
        
        # Check if the armature appears to be VRM
        is_vrm = detect_vrm_armature(armature)
        
        if is_vrm:
            col.label(text=t("VRM.armature_name", name=armature.name), icon='CHECKMARK')
            col.label(text=t("VRM.armature_detected"), icon='INFO')
            col.separator(factor=0.3)
            
            toolkit = context.scene.avatar_toolkit
            col.prop(toolkit, 'vrm_remove_colliders', text=t("VRM.remove_colliders"))
            col.prop(toolkit, 'vrm_remove_root', text=t("VRM.remove_root_bone"))
            col.separator(factor=0.2)
            
            col.operator(
                AvatarToolkit_OT_ConvertVRMToUnity.bl_idname,
                text=t("VRM.convert_to_unity_format"),
                icon='EXPORT'
            )
            
            info_box = vrm_box.box()
            info_col = info_box.column(align=True)
            info_col.label(text=t("VRM.conversion_info.title"), icon='INFO')
            info_col.label(text=t("VRM.conversion_info.renames_bones"))
            info_col.label(text=t("VRM.conversion_info.removes_colliders"))
            info_col.label(text=t("VRM.conversion_info.removes_root"))
            info_col.label(text=t("VRM.conversion_info.maintains_hierarchy"))
            info_col.label(text=t("VRM.conversion_info.validates_results"))
            info_col.label(text=t("VRM.conversion_info.preserves_animations"))
            
        else:
            col.label(text=t("VRM.armature_name", name=armature.name), icon='ERROR')
            col.label(text=t("VRM.no_vrm_bones_detected"), icon='CANCEL')
            col.separator(factor=0.3)
            
            row = col.row()
            row.enabled = False
            row.operator(
                AvatarToolkit_OT_ConvertVRMToUnity.bl_idname,
                text=t("VRM.convert_to_unity_format"),
                icon='CANCEL'
            )
            
            help_box = vrm_box.box()
            help_col = help_box.column(align=True)
            help_col.label(text=t("VRM.detection_failed.title"), icon='QUESTION')
            help_col.label(text=t("VRM.detection_failed.not_vrm_format"))
            help_col.label(text=t("VRM.detection_failed.bones_start_with"))
            help_col.label(text=t("VRM.detection_failed.need_five_bones"))
            help_col.label(text=t("VRM.detection_failed.check_bone_names"))