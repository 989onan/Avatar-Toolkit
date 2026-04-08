import traceback
import bpy
import math
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from bpy.types import Operator, Context, Object, EditBone, Bone
from ...core.translations import t
from ...core.logging_setup import logger
from ...core.common import get_active_armature, ProgressTracker
from ...core.armature_validation import validate_armature
from ...core.dictionaries import (
    standard_bones,
    bone_names,
    bone_hierarchy,
    acceptable_bone_names,
    acceptable_bone_hierarchy,
    non_standard_mappings,
    reverse_bone_lookup,
    simplify_bonename
)

class AvatarToolkit_OT_StandardizeArmature(Operator):
    """Standardize armature bone names and hierarchy to match Avatar Toolkit requirements"""
    bl_idname: str = "avatar_toolkit.standardize_armature"
    bl_label: str = t("Tools.standardize_armature")
    bl_description: str = t("Tools.standardize_armature_desc")
    bl_options: Set[str] = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        armature: Optional[Object] = get_active_armature(context)
        return armature is not None and context.mode in {'OBJECT', 'EDIT_ARMATURE', 'POSE'}
    
    def invoke(self, context: Context, event: Any) -> Set[str]:
        logger.debug("Invoking standardize armature dialog")
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context: Context) -> None:
        layout = self.layout
        toolkit = context.scene.avatar_toolkit
        
        layout.prop(toolkit, "standardize_fix_names")
        layout.prop(toolkit, "standardize_fix_hierarchy")
        layout.prop(toolkit, "standardize_fix_scale")
        layout.separator()
        layout.label(text=t("Tools.standardize_warning"), icon='ERROR')
    
    def execute(self, context: Context) -> Set[str]:
        armature: Optional[Object] = get_active_armature(context)
        toolkit = context.scene.avatar_toolkit
        
        if not armature:
            logger.warning("No active armature found for standardization")
            self.report({'ERROR'}, t("Validation.no_armature"))
            return {'CANCELLED'}
        
        logger.info(f"Starting armature standardization for {armature.name}")
        
        original_mode: str = context.mode
        logger.debug(f"Original mode: {original_mode}")
        bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        try:
            with ProgressTracker(context, 3, "Standardizing Armature") as progress:
                # Step 1: Fix bone names
                if toolkit.standardize_fix_names:
                    progress.step("Fixing bone names")
                    renamed_bones: Dict[str, str] = self.standardize_bone_names(armature)
                    logger.info(f"Renamed {len(renamed_bones)} bones")
                    for old_name, new_name in renamed_bones.items():
                        logger.debug(f"Renamed bone: {old_name} -> {new_name}")
                
                # Step 2: Fix hierarchy
                if toolkit.standardize_fix_hierarchy:
                    progress.step("Fixing bone hierarchy")
                    fixed_hierarchy: int = self.standardize_bone_hierarchy(armature)
                    logger.info(f"Fixed {fixed_hierarchy} hierarchy relationships")
                
                # Step 3: Fix scale issues
                if toolkit.standardize_fix_scale:
                    progress.step("Fixing bone scale")
                    fixed_scale: int = self.standardize_bone_scale(armature)
                    logger.info(f"Fixed {fixed_scale} scale issues")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            is_valid, messages, _ = validate_armature(armature, override_mode='STRICT')
            
            if is_valid:
                logger.info("Armature successfully standardized")
                self.report({'INFO'}, t("Tools.standardize_success"))
            else:
                logger.warning(f"Armature partially standardized. {len(messages)} issues remain")
                bpy.ops.avatar_toolkit.standardize_issues_popup('INVOKE_DEFAULT')
                self.report({'WARNING'}, t("Tools.standardize_partial"))
            
            if original_mode == 'EDIT_ARMATURE':
                bpy.ops.object.mode_set(mode='EDIT')
            if original_mode == 'POSE':
                bpy.ops.object.mode_set(mode='POSE')
            
            return {'FINISHED'}
            
        except Exception:
            logger.error(f"Failed to standardize armature: {traceback.format_exc()}")
            self.report({'ERROR'}, traceback.format_exc())
            
            try:
                if original_mode == 'EDIT_ARMATURE':
                    bpy.ops.object.mode_set(mode='EDIT')
                if original_mode == 'POSE':
                    bpy.ops.object.mode_set(mode='POSE')
                else:
                    bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                logger.error(f"Failed to restore original mode: {traceback.format_exc()}")
                
            return {'CANCELLED'}
    
    def standardize_bone_names(self, armature: Object) -> Dict[str, str]:
        """Rename bones to match standard naming conventions"""
        logger.debug("Starting bone name standardization")
        renamed_bones: Dict[str, str] = {}
        edit_bones = armature.data.edit_bones
        
        # First, check which standard bones already exist
        existing_standard_bones: Set[str] = set()
        for bone in edit_bones:
            if bone.name in standard_bones.values():
                existing_standard_bones.add(bone.name)
                logger.debug(f"Found existing standard bone: {bone.name}")
        
        # Use the reverse bone lookup that's already built and simplified
        name_mapping: Dict[str, str] = {}
        for simplified_name, category in reverse_bone_lookup.items():
            if category in standard_bones:
                standard_name = standard_bones[category]
                # Skip if this standard bone already exists
                if standard_name not in existing_standard_bones:
                    name_mapping[simplified_name] = standard_name
        
        # First pass: identify bones to rename
        bones_to_rename: Dict[str, str] = {}
        for bone in edit_bones:
            original_name: str = bone.name
            
            # Skip if this is already a standard bone name
            if original_name in standard_bones.values():
                continue
                
            simplified_name: str = simplify_bonename(original_name)
            
            # Check if this simplified bone name has a standard mapping
            if simplified_name in name_mapping:
                standard_name = name_mapping[simplified_name]
                if original_name != standard_name:
                    bones_to_rename[original_name] = standard_name
                    logger.debug(f"Identified bone to rename: {original_name} -> {standard_name}")
        
        # Special case for spine/chest hierarchy
        # If we don't have an upper chest, don't rename chest to upper chest because it will break hierarchy
        has_chest: bool = False
        has_upper_chest: bool = False
        
        for bone_name in edit_bones.keys():
            if bone_name == standard_bones['chest']:
                has_chest = True
            elif bone_name == standard_bones['upper_chest']:
                has_upper_chest = True
        
        # If we have a chest but no upper chest, don't rename anything to upper chest
        if has_chest and not has_upper_chest:
            for original_name, new_name in list(bones_to_rename.items()):
                if new_name == standard_bones['upper_chest']:
                    logger.debug(f"Skipping upper chest rename for {original_name} as chest already exists")
                    del bones_to_rename[original_name]
        
        # Second pass: rename bones (in reverse to avoid naming conflicts)
        for original_name, new_name in sorted(bones_to_rename.items(), reverse=True):
            if original_name in edit_bones:
                temp_name: str = f"TEMP_{original_name}"
                edit_bones[original_name].name = temp_name
                renamed_bones[original_name] = new_name
                logger.debug(f"Temporarily renamed: {original_name} -> {temp_name}")
        
        # Third pass: apply final names
        for original_name, new_name in renamed_bones.items():
            temp_name: str = f"TEMP_{original_name}"
            if temp_name in edit_bones:
                edit_bones[temp_name].name = new_name
                logger.debug(f"Applied final rename: {temp_name} -> {new_name}")
        
        logger.info(f"Standardized {len(renamed_bones)} bone names")
        return renamed_bones
    
    def standardize_bone_hierarchy(self, armature: Object) -> int:
        """Fix bone hierarchy to match standard relationships"""
        logger.debug("Starting bone hierarchy standardization")
        edit_bones = armature.data.edit_bones
        fixed_count: int = 0
        
        # Build a mapping of standard bone names to their expected parents
        hierarchy_map: Dict[str, str] = {}
        for parent, child in bone_hierarchy:
            if parent in edit_bones and child in edit_bones:
                hierarchy_map[child] = parent
                logger.debug(f"Found standard hierarchy: {parent} -> {child}")
        
        for parent, child in acceptable_bone_hierarchy:
            if parent in edit_bones and child in edit_bones:
                # Only add if not already in the map
                if child not in hierarchy_map:
                    hierarchy_map[child] = parent
                    logger.debug(f"Found acceptable hierarchy: {parent} -> {child}")
        
        for child_name, parent_name in hierarchy_map.items():
            if child_name in edit_bones and parent_name in edit_bones:
                child_bone: EditBone = edit_bones[child_name]
                parent_bone: EditBone = edit_bones[parent_name]
                
                if child_bone.parent != parent_bone:
                    logger.debug(f"Fixing hierarchy: {child_name} parent was {child_bone.parent.name if child_bone.parent else 'None'}, setting to {parent_name}")
                    child_bone.parent = parent_bone
                    fixed_count += 1
        
        logger.info(f"Fixed {fixed_count} bone hierarchy relationships")
        return fixed_count
    
    def standardize_bone_scale(self, armature: Object) -> int:
        """Fix bone scale issues by normalizing bone lengths"""
        logger.debug("Starting bone scale standardization")
        edit_bones = armature.data.edit_bones
        fixed_count: int = 0
        
        # Calculate median bone length for reference
        lengths: List[float] = [bone.length for bone in edit_bones if bone.length > 0.0001]
        if not lengths:
            logger.warning("No valid bone lengths found for scale standardization")
            return 0
            
        lengths.sort()
        median_length: float = lengths[len(lengths) // 2]
        logger.debug(f"Median bone length: {median_length}")
        
        # Calculate mean and standard deviation
        mean: float = sum(lengths) / len(lengths)
        variance: float = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        std_dev: float = math.sqrt(variance)
        logger.debug(f"Mean bone length: {mean}, Standard deviation: {std_dev}")
    
        small_threshold: float = max(median_length * 0.05, mean - 3 * std_dev)
        large_threshold: float = min(median_length * 15, mean + 5 * std_dev)
        logger.debug(f"Scale thresholds - small: {small_threshold}, large: {large_threshold}")
        
        for bone in edit_bones:
            is_finger: bool = any(finger in bone.name.lower() for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger'])
            
            if bone.length < small_threshold and not is_finger:
                old_length: float = bone.length
                bone.length = small_threshold
                logger.debug(f"Fixed small bone {bone.name}: {old_length} -> {bone.length}")
                fixed_count += 1
            elif bone.length > large_threshold:
                old_length: float = bone.length
                bone.length = large_threshold
                logger.debug(f"Fixed large bone {bone.name}: {old_length} -> {bone.length}")
                fixed_count += 1
        
        logger.info(f"Fixed {fixed_count} bone scale issues")
        return fixed_count

class AvatarToolkit_OT_StandardizeIssuesPopup(Operator):
    """Display information about remaining issues after standardization"""
    bl_idname: str = "avatar_toolkit.standardize_issues_popup"
    bl_label: str = t("Tools.standardize_issues_title")
    bl_options: Set[str] = {'INTERNAL'}
    
    def execute(self, context: Context) -> Set[str]:
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Any) -> Set[str]:
        logger.debug("Showing standardization issues popup")
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context: Context) -> None:
        layout = self.layout
        col = layout.column(align=True)
        
        col.label(text=t("Tools.standardize_issues_header"), icon='INFO')
        col.separator()
        
        col.label(text=t("Tools.standardize_issues_line1"))
        col.label(text=t("Tools.standardize_issues_line2"))
        col.label(text=t("Tools.standardize_issues_line3"))
        col.separator()
        col.label(text=t("Tools.standardize_issues_line4"))
        col.label(text=t("Tools.standardize_issues_line5"))
        col.separator()
        col.label(text=t("Tools.standardize_issues_line6"))

