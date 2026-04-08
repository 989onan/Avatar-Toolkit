import bpy
from typing import Set, Dict, List, Optional, Tuple
from bpy.types import (
    Operator, 
    Panel, 
    Menu, 
    Context, 
    UILayout, 
    WindowManager,
    Object
)
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .ui_utils import UIStyle, draw_section_header, draw_operator_row
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t
from ..core.common import (
    get_active_armature, 
    clear_default_objects, 
    get_armature_list,
    get_armature_stats
)

# Module-level cache for UI performance (avoids Blender scene property write restrictions)
_validation_cache = {}
_stats_cache = {}

def clear_armature_caches():
    """Clear all armature-related caches - called when armature changes"""
    global _validation_cache, _stats_cache
    _validation_cache.clear()
    _stats_cache.clear()

from ..functions.pose_mode import (
    AvatarToolkit_OT_StartPoseMode,
    AvatarToolkit_OT_StopPoseMode,
    AvatarToolkit_OT_ApplyPoseAsShapekey,
    AvatarToolkit_OT_ApplyPoseAsRest
)
from ..core.armature_validation import validate_armature, AvatarToolkit_OT_ValidateTPose, is_pmx_model
from ..core.importers.importer import AvatarToolKit_OT_Import
from ..core.resonite_utils import AvatarToolKit_OT_ExportResonite
from ..functions.tools.standardize_armature import AvatarToolkit_OT_StandardizeArmature

class AvatarToolKit_OT_ExportFBX(Operator):
    """Export selected objects as FBX"""
    bl_idname: str = "avatar_toolkit.export_fbx"
    bl_label: str = t("QuickAccess.export_fbx")
    
    def execute(self, context: Context) -> Set[str]:
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        return {'FINISHED'}

class AvatarToolKit_MT_ExportMenu(Menu):
    """Export menu containing various export options"""
    bl_idname: str = "AVATAR_TOOLKIT_MT_export_menu"
    bl_label: str = t("QuickAccess.export")

    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        layout.operator(AvatarToolKit_OT_ExportFBX.bl_idname, text=t("QuickAccess.export_fbx"))
        layout.operator(AvatarToolKit_OT_ExportResonite.bl_idname, text=t("QuickAccess.export_resonite"))

class AvatarToolKit_OT_ExportMenu(Operator):
    """Open the export menu"""
    bl_idname: str = "avatar_toolkit.export"
    bl_label: str = t("QuickAccess.export")

    @classmethod
    def poll(cls, context: Context) -> bool:
        return get_active_armature(context) is not None
    
    def execute(self, context: Context) -> Set[str]:
        bpy.context.window_manager.popup_menu(AvatarToolKit_MT_ExportMenu.draw)
        return {'FINISHED'}
    
class AvatarToolKit_PT_QuickAccessPanel(Panel):
    """Quick access panel for common Avatar Toolkit operations"""
    bl_label: str = t("QuickAccess.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit_quick_access"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('quick_access')
    bl_options = {'DEFAULT_CLOSED'} if should_open_by_default('QUICK_ACCESS') else set()

    def draw(self, context: Context) -> None:
        """Draw the panel layout"""
        layout: UILayout = self.layout
        props = context.scene.avatar_toolkit
        
        # Armature Selection
        col = draw_section_header(layout, t("QuickAccess.select_armature"), icon='ARMATURE_DATA')
        col.prop(context.scene.avatar_toolkit, "active_armature", text="")
        
        # Get active armature
        active_armature: Optional[Object] = get_active_armature(context)
        if active_armature:
            # Validation Section
            col = draw_section_header(layout, t("Validation.label", "Armature Validation"), icon='CHECKMARK')
            
            # Main validate button with prominent styling
            validate_row = col.row(align=True)
            validate_row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
            validate_row.operator("avatar_toolkit.validate_armature_manual", 
                                text=t("Validation.validate_now", "Validate Armature Now"), 
                                icon='CHECKMARK')
            
            # Validation mode selector
            col.prop(props, "validation_mode", text=t("Settings.validation_mode", "Mode"))
            
            # Show validation results if flag is set
            if props.show_validation_results:
                # Cache validation results
                cache_key = f"validation_{active_armature.name}_{active_armature.data.name}_{len(active_armature.data.bones)}"
                
                if cache_key not in _validation_cache:
                    _validation_cache[cache_key] = validate_armature(active_armature, detailed_messages=True)
                
                is_valid, messages, is_acceptable, hierarchy_messages, scale_messages, non_standard_messages = _validation_cache[cache_key]
                
                # Check if this is a PMX model
                pmx_detected = is_pmx_model(active_armature)
                
                results_box = col.box()
                row = results_box.row()
                row.prop(props, "show_validation_results", text=t("Validation.results", "Validation Results"), 
                        icon='TRIA_DOWN' if props.show_validation_results else 'TRIA_RIGHT', emboss=False)
                
                # PMX Model Notice
                if pmx_detected:
                    pmx_box = results_box.box()
                    pmx_box.label(text=t("Armature.validation.pmx_model_detected"), icon='INFO')
                    
                    validation_mode = context.scene.avatar_toolkit.validation_mode
                    if validation_mode == 'STRICT':
                        pmx_box.label(text=t("Armature.validation.pmx_model_strict"))
                        pmx_box.label(text=t("Armature.validation.pmx_model_standardize"))
                    else:
                        pmx_box.label(text=t("Armature.validation.pmx_model_basic"))
                
                # Validation Results
                if not is_valid:
                    # Display found bones
                    if messages and len(messages) > 0:
                        bones_section = results_box.box()
                        row = bones_section.row()
                        row.prop(props, "show_found_bones", text=t("Validation.section.found_bones"), 
                                icon='TRIA_DOWN' if props.show_found_bones else 'TRIA_RIGHT', emboss=False)
                        if props.show_found_bones:
                            for line in messages[0].split('\n'):
                                bones_section.label(text=line)
                    
                    # Status message
                    status_box = results_box.box()
                    row = status_box.row()
                    row.alert = True
                    row.label(text=t("Validation.status.failed"), icon='ERROR')
                    
                    # Error explanation
                    error_box = results_box.box()
                    error_box.alert = True
                    error_box.label(text=t("Validation.message.failed.line1"))
                    error_box.label(text=t("Validation.message.failed.line2"))
                    error_box.label(text=t("Validation.message.failed.line3"))
                    
                    # Non-Standard Bones section
                    if non_standard_messages or pmx_detected:
                        ns_section = results_box.box()
                        row = ns_section.row()
                        row.alert = True
                        row.prop(props, "show_non_standard", text=t("Validation.section.non_standard"), 
                                icon='TRIA_DOWN' if props.show_non_standard else 'TRIA_RIGHT', emboss=False)
                        if props.show_non_standard:
                            if non_standard_messages and len(non_standard_messages) > 0:
                                for message in non_standard_messages:
                                    for line in message.split('\n'):
                                        sub_row = ns_section.row()
                                        sub_row.alert = True
                                        sub_row.label(text=line)
                            elif pmx_detected:
                                ns_section.alert = True
                                ns_section.label(text=t("Armature.validation.pmx_model_basic"))
                                ns_section.label(text=t("Armature.validation.pmx_model_strict"))
                                ns_section.label(text=t("Armature.validation.pmx_model_standardize"))
                            else:
                                ns_section.label(text=t("Validation.no_non_standard_issues"))
                    
                    # Hierarchy Issues section
                    if hierarchy_messages:
                        hier_section = results_box.box()
                        row = hier_section.row()
                        row.alert = True
                        row.prop(props, "show_hierarchy", text=t("Validation.section.hierarchy"), 
                                icon='TRIA_DOWN' if props.show_hierarchy else 'TRIA_RIGHT', emboss=False)
                        if props.show_hierarchy:
                            for message in hierarchy_messages:
                                sub_row = hier_section.row()
                                sub_row.alert = True
                                sub_row.label(text=message)
                    
                    # Scale Issues section
                    if scale_messages:
                        scale_section = results_box.box()
                        row = scale_section.row()
                        row.alert = True
                        row.prop(props, "show_scale_issues", text=t("Validation.section.scale_issues"), 
                                icon='TRIA_DOWN' if props.show_scale_issues else 'TRIA_RIGHT', emboss=False)
                        if props.show_scale_issues:
                            for scale_msg in scale_messages:
                                sub_row = scale_section.row()
                                sub_row.alert = True
                                sub_row.label(text=scale_msg)
                
                elif is_valid and not is_acceptable:
                    # Valid armature - show stats
                    stats_cache_key = f"stats_{active_armature.name}_{active_armature.data.name}_{len(active_armature.data.bones)}"
                    
                    if stats_cache_key not in _stats_cache:
                        _stats_cache[stats_cache_key] = get_armature_stats(active_armature)
                    
                    stats = _stats_cache[stats_cache_key]
                    
                    status_box = results_box.box()
                    row = status_box.row()
                    row.label(text=t("QuickAccess.valid_armature"), icon='CHECKMARK')
                    split = row.split(factor=0.4)
                    split.label(text=t("QuickAccess.bones_count", count=stats['bone_count']))
                    
                    if stats['has_pose']:
                        results_box.label(text=t("QuickAccess.pose_bones_available"), icon='POSE_HLT')
                
                elif is_valid and is_acceptable:
                    # Acceptable standard
                    status_box = results_box.box()
                    status_box.label(text=t("Armature.validation.acceptable_standard.success"), icon='INFO')
                    status_box.label(text=t("Armature.validation.acceptable_standard.note"))
                    status_box.label(text=t("Armature.validation.acceptable_standard.option"))
                    
                    # Add standardize button
                    standardize_box = results_box.box()
                    standardize_box.operator(AvatarToolkit_OT_StandardizeArmature.bl_idname, 
                                        text=t("QuickAccess.standardize_armature"),
                                        icon='MODIFIER')

            # T-Pose Validation
            col = draw_section_header(layout, t("Validation.tpose.label"), icon='ARMATURE_DATA')
            col.operator(AvatarToolkit_OT_ValidateTPose.bl_idname, text=t("Validation.tpose.validate_now"), icon='CHECKMARK')

            if props.show_tpose_validation:
                validation_result_col = col.column(align=True)
                if props.tpose_validation_result:
                    validation_result_col.label(text=t("Validation.tpose.valid"), icon='CHECKMARK')
                else:
                    validation_result_col.alert = True
                    validation_result_col.label(text=t("Validation.tpose.warning"), icon='ERROR')
                    
                    for msg in props.tpose_validation_messages:
                        validation_result_col.label(text=msg.name)

            # Pose Mode Controls
            col = draw_section_header(layout, t("QuickAccess.pose_controls"), icon='ARMATURE_DATA')
            
            if context.mode == "POSE":
                col.operator(AvatarToolkit_OT_StopPoseMode.bl_idname, icon='POSE_HLT')
                col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
                draw_operator_row(col, [
                    (AvatarToolkit_OT_ApplyPoseAsRest.bl_idname, t("QuickAccess.apply_pose_as_rest.label"), 'MOD_ARMATURE'),
                    (AvatarToolkit_OT_ApplyPoseAsShapekey.bl_idname, t("QuickAccess.apply_pose_as_shapekey.label"), 'MOD_ARMATURE')
                ])
            else:
                col.operator(AvatarToolkit_OT_StartPoseMode.bl_idname, icon='POSE_HLT')

        # Import/Export Section
        col = draw_section_header(layout, t("QuickAccess.import_export"), icon='IMPORT')
        
        # Import/Export Buttons
        draw_operator_row(col, [
            (AvatarToolKit_OT_Import.bl_idname, t("QuickAccess.import"), 'IMPORT'),
            (AvatarToolKit_OT_ExportMenu.bl_idname, t("QuickAccess.export"), 'EXPORT')
        ], scale_y=UIStyle.PRIMARY_BUTTON_SCALE)

