import bpy
from bpy.types import Operator
from ...core.logging_setup import logger


class AvatarToolkit_OT_RemoveAllColliders(Operator):
    """Remove all objects with 'collider' in their name"""
    bl_idname = "avatar_toolkit.remove_all_colliders"
    bl_label = "Remove All Colliders"
    bl_description = "Remove all objects that have 'collider' in their name"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        logger.info("Starting standalone collider removal")
        
        # Store current mode and active object
        current_mode = bpy.context.mode
        original_active = bpy.context.view_layer.objects.active
        
        # Switch to object mode
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        try:
            # Find all collider objects
            collider_names = []
            all_objects = list(bpy.data.objects)
            
            logger.info(f"Scanning {len(all_objects)} objects for colliders")
            
            for obj in all_objects:
                if 'collider' in obj.name.lower():
                    collider_names.append(obj.name)
                    logger.info(f"Found collider: {obj.name}")
            
            if not collider_names:
                self.report({'INFO'}, "No collider objects found")
                logger.info("No collider objects found")
                return {'FINISHED'}
            
            logger.info(f"Found {len(collider_names)} collider objects to remove")
            self.report({'INFO'}, f"Found {len(collider_names)} collider objects")
            
            # Remove each collider
            removed_count = 0
            failed_count = 0
            
            for obj_name in collider_names:
                try:
                    if obj_name in bpy.data.objects:
                        obj = bpy.data.objects[obj_name]
                        
                        # Deselect all objects first
                        bpy.ops.object.select_all(action='DESELECT')
                        
                        # Select and make active
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                        
                        # Delete the object
                        bpy.ops.object.delete(use_global=False)
                        
                        removed_count += 1
                        logger.info(f"Removed collider: {obj_name}")
                        
                    else:
                        logger.debug(f"Object {obj_name} no longer exists")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to remove {obj_name}: {str(e)}")
                    self.report({'WARNING'}, f"Failed to remove {obj_name}: {str(e)}")
            
            # Report results
            if removed_count > 0:
                success_msg = f"Successfully removed {removed_count} collider objects"
                logger.info(success_msg)
                self.report({'INFO'}, success_msg)
            
            if failed_count > 0:
                failure_msg = f"Failed to remove {failed_count} collider objects"
                logger.warning(failure_msg)
                self.report({'WARNING'}, failure_msg)
            
        except Exception as e:
            error_msg = f"Error during collider removal: {str(e)}"
            logger.error(error_msg)
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}
        
        finally:
            # Restore original state
            try:
                if original_active and original_active.name in bpy.data.objects:
                    bpy.context.view_layer.objects.active = original_active
                
                if current_mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode=current_mode)
            except:
                pass
        
        return {'FINISHED'}