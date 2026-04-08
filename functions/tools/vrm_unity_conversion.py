import bpy
from bpy.types import Operator
from ...core.common import get_active_armature
from ...core.translations import t
from ...core.vrm_unity_converter import convert_vrm_to_unity, validate_unity_hierarchy
from ...core.logging_setup import logger
from ...core.armature_validation import validate_armature


class AvatarToolkit_OT_ConvertVRMToUnity(Operator):
    """Convert VRM armature bone names to Unity humanoid format"""
    bl_idname = "avatar_toolkit.convert_vrm_to_unity"
    bl_label = t("VRM.convert_to_unity.label")
    bl_description = t("VRM.convert_to_unity.desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        armature = get_active_armature(context)
        return armature is not None
    
    def execute(self, context):
        armature = get_active_armature(context)
        if not armature:
            logger.warning("No active armature found for VRM conversion")
            self.report({'ERROR'}, t("VRM.no_armature_selected"))
            return {'CANCELLED'}
        
        logger.info(f"Starting VRM to Unity conversion for armature: {armature.name}")
        
        # Get conversion settings
        remove_colliders = context.scene.avatar_toolkit.vrm_remove_colliders
        remove_root = context.scene.avatar_toolkit.vrm_remove_root
        logger.info(f"Collider removal setting: {remove_colliders}")
        logger.info(f"Root bone removal setting: {remove_root}")
        
        # Log all objects with 'collider' in name for debugging
        collider_objects = [obj.name for obj in bpy.data.objects if 'collider' in obj.name.lower()]
        if collider_objects:
            logger.info(f"Found {len(collider_objects)} objects with 'collider' in name:")
            for obj_name in collider_objects:
                logger.info(f"  - {obj_name}")
        
        success, messages, converted_count = convert_vrm_to_unity(armature, remove_colliders, remove_root)
        
        if not success:
            logger.warning(f"VRM conversion failed: {messages}")
            for msg in messages:
                self.report({'WARNING'}, msg)
            return {'CANCELLED'}
        
        logger.info(f"VRM conversion completed successfully. Converted {converted_count} bones")
        for msg in messages:
            self.report({'INFO'}, msg)
        
        # Validate the converted armature
        try:
            is_valid, validation_messages = validate_unity_hierarchy(armature)
            
            if is_valid:
                logger.info("Unity hierarchy validation passed")
                self.report({'INFO'}, t("VRM.validation.hierarchy_passed"))
            else:
                logger.warning("Unity hierarchy validation found issues")
                self.report({'WARNING'}, t("VRM.validation.hierarchy_issues"))
                for msg in validation_messages:
                    self.report({'WARNING'}, msg)
            
            try:
                armature_valid, armature_messages, _ = validate_armature(armature)
                if armature_valid:
                    logger.info("Full armature validation passed")
                    self.report({'INFO'}, t("VRM.validation.armature_passed"))
                else:
                    logger.info("Full armature validation found minor issues")
                    # Don't report these as errors since the conversion was successful
                    # Just log them for debugging
                    for msg in armature_messages[:3]:  
                        logger.debug(f"Armature validation: {msg}")
            except Exception as e:
                logger.warning(f"Error during full armature validation: {str(e)}")
                # Don't fail the operation for validation errors
                
        except Exception as e:
            logger.error(f"Error during hierarchy validation: {str(e)}")
            self.report({'WARNING'}, t("VRM.validation.failed", error=str(e)))
        
        return {'FINISHED'}