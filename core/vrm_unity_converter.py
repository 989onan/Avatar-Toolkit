import bpy
from typing import Dict, List, Optional, Tuple, Set
from bpy.types import Object, Bone
from .common import get_active_armature
from .dictionaries import simplify_bonename, standard_bones, bone_hierarchy, reverse_bone_lookup
from .logging_setup import logger
from .translations import t


def detect_vrm_armature(armature: Object) -> bool:
    """
    Detect if armature uses VRM bone naming conventions
    """
    if not armature or armature.type != 'ARMATURE':
        return False
    
    vrm_patterns = [
        'jbipchips', 'jbipcspine', 'jbipcchest', 'jbipcneck', 'jbipchead',
        # Right arm patterns (both single and double R)
        'jbiprlshoulder', 'jbiprshoulder', 'jbiprupperarm', 'jbiprforearm', 'jbiprhand', 'jbiprlowerarm',
        'jbiprrupperarm', 'jbiprrforearm', 'jbiprrhand',
        # Left arm patterns  
        'jbipllshoulder', 'jbiplshoulder', 'jbiplupperarm', 'jbipllforearm', 'jbipllhand', 'jbipllowerarm', 'jbiplhand',
        # Right leg patterns (both single and double R)
        'jbiprupperleg', 'jbiprlowerleg', 'jbiprfoot', 'jbiprtoe', 'jbiprtoebase',
        'jbiprrupperleg', 'jbiprrlowerleg', 'jbiprrfoot', 'jbiprrtoe',
        # Left leg patterns
        'jbiplupperleg', 'jbipllowerleg', 'jbipllfoot', 'jbiplfoot', 'jbiplltoe', 'jbipltoebase',
        # Finger patterns
        'jbipllittle1', 'jbiprlittle1',
        'jbiplthumb1', 'jbiplthumb2', 'jbiplthumb3',
        'jbiplindex1', 'jbiplindex2', 'jbiplindex3',
        'jbiplmiddle1', 'jbiplmiddle2', 'jbiplmiddle3',
        'jbiplring1', 'jbiplring2', 'jbiplring3',
        # Face eye patterns
        'jadjlfaceeye', 'jadjrfaceeye',
        # Breast patterns
        'jseclbust1', 'jseclbust2', 'jseclbust3',
        'jsecrbust1', 'jsecrbust2', 'jsecrbust3',
        'jbipc', 'jbipr', 'jbipl'  
    ]
    
    found_vrm_bones = 0
    for bone_name in armature.data.bones.keys():
        simplified_name = simplify_bonename(bone_name)
        if simplified_name.startswith('jbip') or any(pattern in simplified_name for pattern in vrm_patterns):
            found_vrm_bones += 1
    
    # Consider it VRM if we find at least 5 VRM bones
    logger.debug(f"Found {found_vrm_bones} VRM bones in armature {armature.name}")
    return found_vrm_bones >= 5




def find_vrm_bones_in_armature(armature: Object) -> Dict[str, str]:
    """
    Find VRM bones in armature and return mapping to their actual names using dictionary lookup
    """
    found_bones = {}
    
    for bone_name in armature.data.bones.keys():
        simplified_name = simplify_bonename(bone_name)
        
        # Check if this bone exists in our reverse lookup dictionary
        if simplified_name in reverse_bone_lookup:
            standard_bone_key = reverse_bone_lookup[simplified_name]
            
            # Get the Unity name from standard_bones
            if standard_bone_key in standard_bones:
                unity_name = standard_bones[standard_bone_key]
                found_bones[bone_name] = unity_name
                logger.debug(f"Found VRM bone via dictionary: {bone_name} -> {unity_name}")
            else:
                logger.debug(f"Standard bone key '{standard_bone_key}' not found in standard_bones for bone '{bone_name}'")
        
        # Fallback for unrecognized VRM bones that start with 'jbip'
        elif simplified_name.startswith('jbip') and bone_name not in found_bones:
            unity_equivalent = guess_unity_name_from_vrm(simplified_name)
            if unity_equivalent:
                found_bones[bone_name] = unity_equivalent
                logger.debug(f"Guessed VRM bone mapping: {bone_name} -> {unity_equivalent}")
    
    return found_bones


def guess_unity_name_from_vrm(vrm_simplified: str) -> Optional[str]:
    """
    Attempt to guess Unity bone name from VRM simplified name using dictionary lookup
    """
    if vrm_simplified in reverse_bone_lookup:
        standard_bone_key = reverse_bone_lookup[vrm_simplified]
        
        if standard_bone_key in standard_bones:
            return standard_bones[standard_bone_key]
    
    return None


def is_vrm_collider_object(obj_name: str) -> bool:
    """
    Test if an object name represents a VRM collider
    """
    obj_name_lower = obj_name.lower()
    collider_patterns = ['collider', 'collision', 'dynamic', 'spring', 'physics', 'secondary']
    
    # Must contain a collider pattern
    contains_collider = any(pattern in obj_name_lower for pattern in collider_patterns)
    if not contains_collider:
        return False
    
    # Must be VRM-related (multiple detection methods)
    is_vrm = (
        'j_bip' in obj_name_lower or
        'jbip' in simplify_bonename(obj_name) or
        any(vrm_part in obj_name_lower for vrm_part in ['j_bip_c_', 'j_bip_l_', 'j_bip_r_'])
    )
    
    return is_vrm


def remove_collection_from_hierarchy(collection_to_remove) -> bool:
    """
    Recursively remove a collection from all parent collections in the hierarchy
    """
    removed_from_any_parent = False
    
    try:
        # Check scene collection
        scene_collection = bpy.context.scene.collection
        if collection_to_remove in scene_collection.children:
            scene_collection.children.unlink(collection_to_remove)
            logger.debug(f"    Unlinked '{collection_to_remove.name}' from scene collection")
            removed_from_any_parent = True
        
        # Check all other collections recursively
        for parent_collection in list(bpy.data.collections):
            if parent_collection != collection_to_remove and collection_to_remove in parent_collection.children:
                try:
                    parent_collection.children.unlink(collection_to_remove)
                    logger.debug(f"    Unlinked '{collection_to_remove.name}' from parent '{parent_collection.name}'")
                    removed_from_any_parent = True
                except Exception as unlink_error:
                    logger.warning(f"    Failed to unlink '{collection_to_remove.name}' from '{parent_collection.name}': {str(unlink_error)}")
        
        return removed_from_any_parent
        
    except Exception as e:
        logger.error(f"Error removing collection '{collection_to_remove.name}' from hierarchy: {str(e)}")
        return False


def remove_vrm_colliders(armature: Object = None) -> Tuple[int, List[str], int]:
    """
    Simple approach: Remove ALL objects with 'collider' in their name and clean up empty collections
    """
    objects_to_remove = []
    removed_names = []
    collections_to_check = set()
    
    # Store the current mode and active object
    current_mode = bpy.context.mode
    original_active = bpy.context.view_layer.objects.active
    
    if current_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    try:
        logger.info("Starting simple collider removal - removing ALL objects with 'collider' in name")
        
        collider_object_names = []
        for obj in bpy.data.objects:
            if 'collider' in obj.name.lower():
                collider_object_names.append(obj.name)
                # Track collections this object is in
                for collection in obj.users_collection:
                    collections_to_check.add(collection)
                logger.info(f"Found collider object: {obj.name}")
        
        logger.info(f"Found {len(collider_object_names)} collider objects to remove")
        
        # Remove collider objects by name
        removed_count = 0
        for obj_name in collider_object_names:
            try:
                # Check if object still exists
                if obj_name in bpy.data.objects:
                    obj = bpy.data.objects[obj_name]
                    logger.info(f"Removing collider object: {obj_name}")
                    
                    # Remove from all collections first
                    for collection in list(obj.users_collection):
                        collection.objects.unlink(obj)
                        logger.debug(f"  Unlinked from collection: {collection.name}")
                    
                    bpy.data.objects.remove(obj, do_unlink=True)
                    removed_count += 1
                    removed_names.append(obj_name)
                    logger.info(f"  Successfully removed: {obj_name}")
                else:
                    logger.debug(f"Object {obj_name} already removed")
                
            except Exception as e:
                logger.error(f"Failed to remove collider object {obj_name}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        logger.info(f"Successfully removed {removed_count} collider objects")
        
        # Clean up empty collections (prioritize collider-related collections)
        empty_collections_removed = 0
        
        # Also check all collections in the scene for collider-related names
        all_collections_to_check = set(collections_to_check)
        for collection in bpy.data.collections:
            collection_name_lower = collection.name.lower()
            if any(pattern in collection_name_lower for pattern in ['collider', 'collision', 'physics', 'dynamic']):
                all_collections_to_check.add(collection)
                logger.debug(f"Found collider-related collection to check: {collection.name}")
        
        for collection in list(all_collections_to_check):
            try:
                # Check if collection exists and is empty
                if collection.name not in bpy.data.collections:
                    logger.debug(f"Collection {collection.name} already removed")
                    continue
                
                collection_name_lower = collection.name.lower()
                is_collider_collection = any(pattern in collection_name_lower for pattern in ['collider', 'collision', 'physics', 'dynamic'])
                is_empty = len(collection.objects) == 0 and len(collection.children) == 0
                is_protected = collection.name in ["Collection", "Master Collection"]
                
                # Remove if empty and (was used by colliders OR has collider-related name)
                if is_empty and not is_protected and (collection in collections_to_check or is_collider_collection):
                    logger.info(f"Removing empty {'collider-related ' if is_collider_collection else ''}collection: {collection.name}")
                    
                    # Use helper function to remove from all parent collections
                    removed_from_parents = remove_collection_from_hierarchy(collection)
                    
                    if not removed_from_parents:
                        logger.debug(f"  Collection {collection.name} was not found in any parent collections")
                    
                    # Remove the collection data
                    try:
                        bpy.data.collections.remove(collection)
                        empty_collections_removed += 1
                        logger.info(f"  Successfully removed collection: {collection.name}")
                    except Exception as remove_error:
                        logger.warning(f"  Failed to remove collection {collection.name}: {str(remove_error)}")
                        # Continue with other collections even if this one fails
                    
            except Exception as e:
                logger.warning(f"Failed to remove empty collection {collection.name}: {str(e)}")
                import traceback
                logger.debug(f"Collection removal traceback: {traceback.format_exc()}")
        
        if empty_collections_removed > 0:
            logger.info(f"Cleaned up {empty_collections_removed} empty collections")
        
    except Exception as e:
        logger.error(f"Error during collider removal: {str(e)}")
        return 0, [], 0
    
    finally:
        if original_active and original_active.name in bpy.data.objects:
            bpy.context.view_layer.objects.active = original_active
        
        if current_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode=current_mode)
            except:
                pass
    
    logger.info(f"Collider removal complete. Removed {len(removed_names)} objects and {empty_collections_removed} collections")
    return len(removed_names), removed_names, empty_collections_removed


def remove_vrm_root_bone(armature: Object) -> Tuple[bool, str]:
    """
    Remove unnecessary VRM root bone and make Hips the root bone

    """
    if not armature or armature.type != 'ARMATURE':
        return False, "No valid armature provided"
    
    # Look for potential root bones and Hips bone
    potential_roots = []
    hips_bone = None
    
    for bone in armature.data.edit_bones:
        bone_name_lower = bone.name.lower()
        
        # Check if this could be Hips (various naming conventions)
        if any(hips_name in bone_name_lower for hips_name in ['hips', 'hip', 'pelvis', 'jbipchips']):
            hips_bone = bone
            logger.debug(f"Found Hips bone: {bone.name}")
        
        # Check if this could be a root bone
        if bone.parent is None and len(bone.children) > 0:
            # Common VRM root bone names
            if any(root_name in bone_name_lower for root_name in ['root', 'vrm', 'armature', 'rig']):
                potential_roots.append(bone)
                logger.debug(f"Found potential root bone: {bone.name}")
    
    if not hips_bone:
        return False, "Could not find Hips bone to promote as root"
    
    if not potential_roots:
        logger.info("No unnecessary root bone found - Hips may already be root")
        return True, "No root bone removal needed"
    
    # Find the root bone that is the parent of Hips
    root_to_remove = None
    for root_bone in potential_roots:
        if hips_bone.parent == root_bone:
            root_to_remove = root_bone
            break
    
    if not root_to_remove:
        # Check if Hips is already parentless (already root)
        if hips_bone.parent is None:
            logger.info("Hips bone is already the root bone")
            return True, "Hips is already root - no changes needed"
        else:
            logger.warning(f"Hips bone has parent '{hips_bone.parent.name}' but no matching root found")
            return False, "Could not identify safe root bone to remove"
    
    root_name = root_to_remove.name
    logger.info(f"Removing root bone '{root_name}' and promoting Hips to root")
    
    # Reparent all children of the root bone (except Hips) to Hips
    children_to_reparent = []
    for child in root_to_remove.children:
        if child != hips_bone:
            children_to_reparent.append(child)
    
    hips_bone.parent = None
    
    for child in children_to_reparent:
        child.parent = hips_bone
        logger.debug(f"Reparented {child.name} from {root_name} to {hips_bone.name}")
    
    armature.data.edit_bones.remove(root_to_remove)
    
    message = f"Removed root bone '{root_name}' - Hips is now the root bone"
    logger.info(message)
    return True, message


def convert_vrm_to_unity(armature: Object, remove_colliders: bool = True, remove_root: bool = True) -> Tuple[bool, List[str], int]:
    """
    Convert VRM armature bone names to Unity humanoid format
    """
    if not armature or armature.type != 'ARMATURE':
        return False, ["No valid armature selected"], 0
    
    logger.info(f"Starting VRM to Unity conversion for armature: {armature.name}")
    
    # Check if this is a VRM armature
    if not detect_vrm_armature(armature):
        return False, ["Selected armature does not appear to be a VRM armature"], 0
    
    messages = []
    converted_count = 0
    failed_conversions = []
    collider_count = 0
    
    current_mode = bpy.context.mode
    if current_mode != 'EDIT':
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
    
    try:
        # First, remove collider objects and bones if requested
        if remove_colliders:
            collider_count, removed_colliders, collections_removed = remove_vrm_colliders(armature)
            if collider_count > 0 or collections_removed > 0:
                if collections_removed > 0:
                    messages.append(f"Removed {collider_count} VRM collider objects and {collections_removed} empty collections")
                else:
                    messages.append(f"Removed {collider_count} VRM collider objects")
                logger.info(f"Removed {collider_count} VRM colliders: {removed_colliders}")
        
        vrm_bones = find_vrm_bones_in_armature(armature)
        
        if not vrm_bones:
            if remove_colliders and (collider_count > 0 or collections_removed > 0):
                messages.append("No VRM bones found to convert (colliders were removed)")
                return True, messages, 0  
            else:
                return False, ["No VRM bones found in armature"], 0
        
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Remove unnecessary root bone if requested
        if remove_root:
            root_success, root_message = remove_vrm_root_bone(armature)
            messages.append(root_message)
            if not root_success:
                logger.warning(f"Root bone removal failed: {root_message}")
        
        # Rename bones
        for vrm_bone_name, unity_name in vrm_bones.items():
            if vrm_bone_name in armature.data.edit_bones:
                bone = armature.data.edit_bones[vrm_bone_name]
                
                # Check if target name already exists
                if unity_name in armature.data.edit_bones and unity_name != vrm_bone_name:
                    failed_conversions.append(f"{vrm_bone_name} -> {unity_name} (name conflict)")
                    continue
                
                # Rename the bone
                bone.name = unity_name
                converted_count += 1
                logger.debug(f"Renamed bone: {vrm_bone_name} -> {unity_name}")
        
        messages.append(f"Successfully converted {converted_count} VRM bones to Unity format")
        
        if failed_conversions:
            messages.append("Failed conversions due to name conflicts:")
            messages.extend(failed_conversions)
        
        logger.info(f"VRM to Unity conversion completed. Converted {converted_count} bones")
        
    except Exception as e:
        logger.error(f"Error during VRM conversion: {str(e)}")
        messages.append(f"Error during conversion: {str(e)}")
        return False, messages, converted_count
    
    finally:
        # Restore original mode
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
    
    return converted_count > 0 or (remove_colliders and collider_count > 0), messages, converted_count


def validate_unity_hierarchy(armature: Object) -> Tuple[bool, List[str]]:
    """
    Validate that the converted armature has proper Unity humanoid hierarchy
    """
    if not armature or armature.type != 'ARMATURE':
        return False, ["No valid armature to validate"]
    
    messages = []
    is_valid = True
    
    # Check for essential Unity bones
    essential_unity_bones = [
        standard_bones['hips'],
        standard_bones['spine'],
        standard_bones['chest'],
        standard_bones['neck'],
        standard_bones['head']
    ]
    
    missing_bones = []
    for bone_name in essential_unity_bones:
        if bone_name not in armature.data.bones:
            missing_bones.append(bone_name)
    
    if missing_bones:
        is_valid = False
        messages.append("Missing essential Unity bones:")
        messages.extend([f"- {bone}" for bone in missing_bones])
    
    # Validate basic hierarchy
    hierarchy_issues = []
    for parent_name, child_name in bone_hierarchy:
        if parent_name in armature.data.bones and child_name in armature.data.bones:
            parent_bone = armature.data.bones[parent_name]
            child_bone = armature.data.bones[child_name]
            
            if child_bone.parent != parent_bone:
                hierarchy_issues.append(f"{parent_name} -> {child_name}")
    
    if hierarchy_issues:
        is_valid = False
        messages.append("Hierarchy issues found:")
        messages.extend([f"- {issue}" for issue in hierarchy_issues])
    
    if is_valid:
        messages.append("Unity hierarchy validation passed")
    
    return is_valid, messages