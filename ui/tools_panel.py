import bpy
from typing import Set
from bpy.types import Panel, Context, UILayout, Operator, UIList
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .ui_utils import UIStyle, draw_section_header, draw_operator_row
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t

from ..core.resonite_utils import AvatarToolkit_OT_ConvertResonite
from ..functions.tools.mesh_separation import AvatarToolKit_OT_SeparateByLooseParts, AvatarToolKit_OT_SeparateByMaterials
from ..functions.tools.additional_tools import AvatarToolkit_OT_ApplyTransforms, AvatarToolkit_OT_CleanShapekeys
from ..functions.tools.bone_tools import (
    AvatarToolKit_OT_CreateDigitigradeLegs, 
    AvatarToolKit_OT_DeleteBoneConstraints, 
    AvatarToolKit_OT_RemoveSelectedBones, 
    AvatarToolKit_OT_RemoveZeroWeightBones, 
    AvatarToolKit_OT_RemoveZeroWeightVertexGroups,
    AvatarToolKit_OT_FlipCurrentKeyFrames
)
from ..functions.tools.standardize_armature import AvatarToolkit_OT_StandardizeArmature
from ..functions.tools.merge_tools import AvatarToolkit_OT_MergeToActive, AvatarToolkit_OT_MergeToParent, AvatarToolkit_OT_ConnectBones
from ..functions.tools.rigify_converter import AvatarToolkit_OT_ConvertRigifyToUnity
from ..functions.tools.general_mesh_tools import AvatarToolkit_OT_SelectShortestSeamPath, AvatarToolkit_OT_ExplodeMesh
from ..functions.custom_tools.force_apply_modifier import AvatarToolkit_OT_ApplyModifierForShapkeyObj

class AvatarToolKit_PT_ToolsPanel(Panel):
    """Panel containing various tools for avatar customization and optimization"""
    bl_label: str = t("Tools.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit_tools"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('tools')
    bl_options = set() if not should_open_by_default('TOOLS') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw the tools panel interface"""
        layout: UILayout = self.layout
        toolkit = context.scene.avatar_toolkit
        
        # General Tools
        col = draw_section_header(layout, t("Tools.general_title"), icon='TOOL_SETTINGS')
        col.operator(AvatarToolkit_OT_ConvertResonite.bl_idname, text=t("Tools.convert_resonite"), icon='EXPORT')
        
        # Separation Tools
        col = draw_section_header(layout, t("Tools.separate_title"), icon='MOD_EXPLODE')
        draw_operator_row(col, [
            (AvatarToolKit_OT_SeparateByMaterials.bl_idname, t("Tools.separate_materials"), 'MATERIAL'),
            (AvatarToolKit_OT_SeparateByLooseParts.bl_idname, t("Tools.separate_loose"), 'MESH_DATA')
        ])
        
        # Bone Tools
        col = draw_section_header(layout, t("Tools.bone_title"), icon='BONE_DATA')
        col.operator(AvatarToolKit_OT_CreateDigitigradeLegs.bl_idname, text=t("Tools.create_digitigrade"), icon='BONE_DATA')
        col.operator(AvatarToolKit_OT_FlipCurrentKeyFrames.bl_idname, text=t("Tools.flip_pose_frames"), icon="ACTION")

        # Mesh Tools
        col = draw_section_header(layout, t("Tools.mesh_title"), icon='MESH_DATA')
        col.operator(AvatarToolkit_OT_SelectShortestSeamPath.bl_idname, text=t("Tools.find_shortest_seam_path"), icon="MESH_DATA")
        col.operator(AvatarToolkit_OT_ApplyModifierForShapkeyObj.bl_idname, text=t("Tools.apply_modifier_on_shapekey_obj"), icon="SHAPEKEY_DATA")
        col.operator(AvatarToolkit_OT_ExplodeMesh.bl_idname, text=t("Tools.explode_mesh"), icon="MOD_EXPLODE")
        
        # Standardization Tools
        col = draw_section_header(layout, t("Tools.standardize_title"), icon='OUTLINER_OB_ARMATURE')
        col.operator(AvatarToolkit_OT_StandardizeArmature.bl_idname, icon='CHECKMARK')

        # Weight Tools
        col = draw_section_header(layout, t("Tools.weight_title"), icon='GROUP_BONE')
        col.prop(toolkit, "merge_twist_bones", text=t("Tools.merge_twist_bones"))
        col.prop(toolkit, "preserve_parent_bones")
        col.prop(toolkit, "target_bone_type")
        col.prop(toolkit, "list_only_mode")
        
        if toolkit.list_only_mode and len(toolkit.zero_weight_bones) > 0:
            sub_col = col.box()
            row = sub_col.row()
            row.template_list("AVATAR_TOOLKIT_UL_ZeroWeightBones", "", 
                            toolkit, "zero_weight_bones",
                            toolkit, "zero_weight_bones_index")
            
            sub_col.operator(AvatarToolKit_OT_RemoveSelectedBones.bl_idname, 
                           text=t("Tools.remove_selected_bones"))
        
        # Combine weight
        draw_operator_row(col, [
            (AvatarToolKit_OT_RemoveZeroWeightBones.bl_idname, t("Tools.clean_weights"), 'GROUP_BONE'),
            (AvatarToolKit_OT_DeleteBoneConstraints.bl_idname, t("Tools.clean_constraints"), 'CONSTRAINT_BONE')
        ])
        col.operator(AvatarToolKit_OT_RemoveZeroWeightVertexGroups.bl_idname, text=t("Tools.clean_vertex_groups"), icon='CONSTRAINT_BONE')
        
        # Merge Tools
        col = draw_section_header(layout, t("Tools.merge_title"), icon='AUTOMERGE_ON')
        draw_operator_row(col, [
            (AvatarToolkit_OT_MergeToActive.bl_idname, t("Tools.merge_to_active"), 'BONE_DATA'),
            (AvatarToolkit_OT_MergeToParent.bl_idname, t("Tools.merge_to_parent"), 'BONE_DATA')
        ])
        col.operator(AvatarToolkit_OT_ConnectBones.bl_idname, text=t("Tools.connect_bones"), icon='BONE_DATA')
        
        # Additional Tools
        col = draw_section_header(layout, t("Tools.additional_title"), icon='TOOL_SETTINGS')
        col.operator(AvatarToolkit_OT_ApplyTransforms.bl_idname, text=t("Tools.apply_transforms"), icon='OBJECT_DATA')
        col.operator(AvatarToolkit_OT_CleanShapekeys.bl_idname, text=t("Tools.clean_shapekeys"), icon='SHAPEKEY_DATA')

        # Rigify Tools
        col = draw_section_header(layout, t("Tools.rigify_title"), icon='ARMATURE_DATA')
        col.operator(AvatarToolkit_OT_ConvertRigifyToUnity.bl_idname, icon='ARMATURE_DATA')
        col.prop(context.scene.avatar_toolkit, "merge_twist_bones")


class AVATAR_TOOLKIT_UL_ZeroWeightBones(UIList):
    """UI List for displaying zero weight bones with selection options"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "selected", text="")
            row.label(text=item.name)
            if item.has_children:
                row.label(text="", icon='OUTLINER_OB_ARMATURE')
            if item.is_deform:
                row.label(text="", icon='MOD_ARMATURE')