import bpy
import math
from mathutils import Vector, Color
from typing import Tuple, List, Dict, Set, Optional, Union
from bpy.types import Object, Bone, Operator
from ..core.common import get_armature_list, get_active_armature
from ..core.translations import t
from ..core.dictionaries import (
    standard_bones,
    bone_hierarchy,
    finger_hierarchy,
    acceptable_bone_hierarchy,
    acceptable_bone_names,
    simplify_bonename
)
from ..core.logging_setup import logger

def is_pmx_model(armature: Object) -> bool:
    """
    Check if the armature is a PMX/MMD model.
    PMX models have an mmd_type attribute set to 'ROOT' on the root object.
    """
    if not armature:
        return False
    
    # Check if armature itself has mmd_type set to ROOT
    if hasattr(armature, 'mmd_type') and armature.mmd_type == 'ROOT':
        return True
    
    # Check if parent has mmd_type set to ROOT (parent container model)
    if hasattr(armature, 'parent') and armature.parent:
        parent = armature.parent
        if hasattr(parent, 'mmd_type') and parent.mmd_type == 'ROOT':
            return True
    
    return False

def validate_armature(armature: Object, detailed_messages: bool = False, override_mode: Optional[str] = None) -> Union[Tuple[bool, List[str], bool], Tuple[bool, List[str], bool, List[str], List[str], List[str]]]:
    """
    Validates armature and returns validation results
    """
    logger.debug(f"Validating armature: {armature.name if armature else 'None'}")
    validation_mode = override_mode if override_mode else bpy.context.scene.avatar_toolkit.validation_mode
    messages: List[str] = []
    hierarchy_messages: List[str] = []
    non_standard_messages: List[str] = []
    scale_messages: List[str] = []
    
    # Check if this is a PMX model
    pmx_model = is_pmx_model(armature)
    if pmx_model:
        logger.debug("Detected PMX model, using specialized validation")
    
    if validation_mode == 'NONE':
        logger.debug("Validation mode is NONE, skipping validation")
        if detailed_messages:
            return True, [t("Validation.mode.none")], False, [], [], []
        else:
            return True, [t("Validation.mode.none")], False
        
    if not armature or armature.type != 'ARMATURE' or not armature.data.bones:
        logger.warning("Basic armature check failed")
        if detailed_messages:
            return False, [t("Armature.validation.basic_check_failed")], False, [], [], []
        else:
            return False, [t("Armature.validation.basic_check_failed")], False
        
    found_bones: Dict[str, Bone] = {bone.name: bone for bone in armature.data.bones}
    logger.debug(f"Found {len(found_bones)} bones in armature")
    is_acceptable = check_acceptable_standards(found_bones)
    
    # List all bones in armature
    bone_list = "\n".join([f"- {bone}" for bone in found_bones.keys()])
    messages.append(t("Armature.validation.found_bones", bones=bone_list))
    
    # Basic validation for both STRICT and LIMITED modes
    # Check for missing required bones
    essential_bones = {standard_bones[key] for key in ['hips', 'spine', 'chest', 'neck', 'head']}
    missing_bones = [bone for bone in essential_bones if bone not in found_bones]
    
    if missing_bones:
        missing_list = "\n".join([f"- {bone}" for bone in missing_bones])
        logger.warning(f"Missing essential bones: {', '.join(missing_bones)}")
        hierarchy_messages.append(t("Armature.validation.missing_bones", bones=missing_list))

    if validation_mode == 'STRICT':
        logger.debug("Performing strict validation")
        # Add scale issue detection in STRICT mode
        scale_issues = detect_scale_issues(found_bones)
        if scale_issues:
            logger.warning(f"Found {len(scale_issues)} scale issues")
            # CHANGE: Don't combine into a single string, keep as separate items
            scale_messages.extend(scale_issues)
        
        # Validate bone hierarchy
        for parent, child in bone_hierarchy:
            if parent in found_bones and child in found_bones:
                if not validate_bone_hierarchy(found_bones, parent, child):
                    logger.warning(f"Invalid hierarchy: {parent} -> {child}")
                    hierarchy_messages.append(t("Armature.validation.invalid_hierarchy", 
                                    parent=parent, child=child))
        
        # Validate symmetry
        logger.debug("Validating bone symmetry")
        symmetry_pairs = [('arm', 'L', 'R'), ('leg', 'L', 'R')]
        for base, left, right in symmetry_pairs:
            if not validate_symmetry(found_bones, base, left, right):
                logger.warning(f"Asymmetric bones found: {base}")
                hierarchy_messages.append(t("Armature.validation.asymmetric_bones", bone=base))
               
        if (not validate_symmetry(found_bones, 'hand', 'L', 'R') and
            not validate_symmetry(found_bones, 'wrist', 'L', 'R')):
            logger.warning("Asymmetric hand/wrist bones found")
            hierarchy_messages.append(t("Armature.validation.asymmetric_hand_wrist"))
           
        # Validate finger hierarchies
        logger.debug("Validating finger hierarchies")
        for side in ['left', 'right']:
            for finger_chain in finger_hierarchy[side]:
                if all(bone in found_bones for bone in finger_chain):
                    if not validate_finger_chain(found_bones, finger_chain):
                        logger.warning(f"Invalid finger hierarchy: {finger_chain[0]}")
                        hierarchy_messages.append(t("Armature.validation.invalid_finger", finger=finger_chain[0]))
        
        # Non-standard bones check
        non_standard_bones = []
        
        # Bones to ignore
        ignore_patterns = [
            'tail', 'skirt', 'dress', 'hair', 'ribbon', 'bow', 'hat', 'cap',
            'butt', 'breast', 'boob', 'chest_', 'belly', 'stomach',
            'wing', 'fin', 'horn', 'ear_', 'accessory', 'extra',
            'cloth', 'fabric', 'cape', 'coat', 'jacket', 'shirt',
            'pants', 'shoe', 'boot', 'sock', 'glove', 'mitten',
            'belt', 'strap', 'buckle', 'button', 'zipper',
            'jewel', 'gem', 'ring', 'necklace', 'earring',
            'flower', 'leaf', 'feather', 'fur', 'scale',
            'bangs', 'sideburn', 'bell', 'leash', 'ears', 'chain',
            'headband', 'necklace', 'necktie', 'strapNeck', 'ring',
            'pin', 'hair',

        ]
        
        # Create normalized lookup sets for faster comparison
        normalized_standard_bones = {simplify_bonename(name) for name in standard_bones.values()}
        normalized_acceptable_bones = set()
        for names in acceptable_bone_names.values():
            normalized_acceptable_bones.update(simplify_bonename(name) for name in names)
        
        for bone_name in found_bones:
            # Normalize bone name for comparison
            normalized_bone_name = simplify_bonename(bone_name)
            
            # Check if bone should be ignored (accessory bone)
            is_ignored = any(pattern in normalized_bone_name for pattern in ignore_patterns)
            
            if not is_ignored:
                # Check if bone is in standard or acceptable lists
                is_standard = normalized_bone_name in normalized_standard_bones
                is_acceptable_bone = normalized_bone_name in normalized_acceptable_bones
                
                if not (is_standard or is_acceptable_bone):
                    non_standard_bones.append(bone_name)
        
        if non_standard_bones:
            non_standard_list = "\n".join([f"- {bone}" for bone in non_standard_bones])
            non_standard_messages.append(t("Armature.validation.non_standard_bones", bones=non_standard_list))
            
            non_standard_messages.append(t("Armature.validation.accessory_bones_note.line1"))
            non_standard_messages.append(t("Armature.validation.accessory_bones_note.line2"))
            non_standard_messages.append(t("Armature.validation.accessory_bones_note.line3"))
            non_standard_messages.append(t("Armature.validation.accessory_bones_note.line4"))
            non_standard_messages.append("")  # Add a blank line for spacing
            non_standard_messages.append(t("Armature.validation.standardize_note.line1"))
            non_standard_messages.append(t("Armature.validation.standardize_note.line2"))
            non_standard_messages.append(t("Armature.validation.standardize_note.line3"))
    
    # Special handling for PMX models
    if pmx_model:
        logger.info("PMX model detected, applying specialized validation")
        # For PMX models, we'll be more lenient with validation
        # and provide specific guidance for these models
        if not messages:
            messages = [t("Armature.validation.pmx_model_detected")]
        
        # Add PMX-specific messages
        if validation_mode == 'STRICT':
            messages.append(t("Armature.validation.pmx_model_strict"))
            messages.append(t("Armature.validation.pmx_model_standardize"))
        else:
            messages.append(t("Armature.validation.pmx_model_basic"))
    
    # Combine messages in correct order
    messages.extend(non_standard_messages)
    
    is_valid = len(non_standard_messages) == 0 and len(hierarchy_messages) == 0 and len(scale_messages) == 0
    
    if not is_valid and is_acceptable:
        if non_standard_bones:
            logger.info("Armature has non-standard bones but is acceptable")
            if detailed_messages:
                return False, messages, False, hierarchy_messages, scale_messages, non_standard_messages
            else:
                return False, messages, False
        
        logger.info("Armature meets acceptable standards")
        messages = [
            t("Armature.validation.acceptable_standard.success"),
            t("Armature.validation.acceptable_standard.note"),
            t("Armature.validation.acceptable_standard.option")
        ]
        if detailed_messages:
            return True, messages, True, [], [], []
        else:
            return True, messages, True
    
    # Ensure messages has at least one element
    if not messages:
        messages = [t("Armature.validation.unknown_format")]
    
    logger.info(f"Armature validation complete. Valid: {is_valid}")
    if detailed_messages:
        return is_valid, messages, False, hierarchy_messages, scale_messages, non_standard_messages
    else:
        return is_valid, messages, False

def validate_bone_hierarchy(bones: Dict[str, Bone], parent_name: str, child_name: str) -> bool:
    """Validate if there is a valid parent-child relationship between bones"""
    if parent_name not in bones or child_name not in bones:
        return False
    return bones[child_name].parent == bones[parent_name]

def extract_bone_side_info(bone_name: str) -> Tuple[str, str]:
    """
    Extract base bone name and side indicator from a bone name.
    Returns (base_name, side) where side is 'L', 'R', or ''
    """
    normalized = simplify_bonename(bone_name)
    original = bone_name
    
    # Common left/right patterns to check
    left_patterns = [
        'left', 'l', 'lft', 'lt',
        '.l', '_l', '-l', ' l',
        '左', 'ひだり'
    ]
    
    right_patterns = [
        'right', 'r', 'rgt', 'rt', 
        '.r', '_r', '-r', ' r',
        '右', 'みぎ'
    ]
    
    # Check for left patterns
    for pattern in left_patterns:
        pattern_norm = simplify_bonename(pattern)
        if normalized.startswith(pattern_norm):
            base = normalized[len(pattern_norm):]
            if base:  # Make sure there's something left
                return base, 'L'
        elif normalized.endswith(pattern_norm):
            base = normalized[:-len(pattern_norm)]
            if base:
                return base, 'L'
        elif pattern_norm in normalized:
            # Handle cases like ArmLeft
            parts = normalized.split(pattern_norm)
            if len(parts) == 2:
                base = parts[0] + parts[1]
                if base:
                    return base, 'L'
    
    # Check for right patterns
    for pattern in right_patterns:
        pattern_norm = simplify_bonename(pattern)
        if normalized.startswith(pattern_norm):
            base = normalized[len(pattern_norm):]
            if base:
                return base, 'R'
        elif normalized.endswith(pattern_norm):
            base = normalized[:-len(pattern_norm)]
            if base:
                return base, 'R'
        elif pattern_norm in normalized:
            parts = normalized.split(pattern_norm)
            if len(parts) == 2:
                base = parts[0] + parts[1]
                if base:
                    return base, 'R'
    
    return normalized, ''

def find_symmetric_bone_pairs(bones: Dict[str, Bone]) -> Dict[str, Tuple[List[str], List[str]]]:
    """
    Automatically find symmetric bone pairs in the armature.
    Returns dict mapping base_name to (left_bones, right_bones)
    """
    bone_groups = {}
    
    for bone_name in bones.keys():
        base, side = extract_bone_side_info(bone_name)
        
        if side:
            if base not in bone_groups:
                bone_groups[base] = {'L': [], 'R': []}
            bone_groups[base][side].append(bone_name)
    
    symmetric_pairs = {}
    for base, sides in bone_groups.items():
        if sides['L'] and sides['R']:
            symmetric_pairs[base] = (sides['L'], sides['R'])
    
    return symmetric_pairs

def validate_armature_symmetry(armature: Object) -> Tuple[bool, List[str]]:
    """
    Comprehensive symmetry validation that provides detailed feedback
    """
    if not armature or armature.type != 'ARMATURE':
        return False, ["Invalid armature"]
    
    bones = {bone.name: bone for bone in armature.data.bones}
    symmetric_pairs = find_symmetric_bone_pairs(bones)
    
    messages = []
    is_symmetric = True
    
    if symmetric_pairs:
        messages.append("Found symmetric bone pairs:")
        for base, (left_bones, right_bones) in symmetric_pairs.items():
            left_count = len(left_bones)
            right_count = len(right_bones)
            
            if left_count == right_count:
                messages.append(f"  ✓ {base}: {left_count} bones on each side")
                for l_bone, r_bone in zip(sorted(left_bones), sorted(right_bones)):
                    messages.append(f"    {l_bone} ↔ {r_bone}")
            else:
                is_symmetric = False
                messages.append(f"  ✗ {base}: {left_count} left, {right_count} right bones")
                messages.append(f"    Left: {', '.join(sorted(left_bones))}")
                messages.append(f"    Right: {', '.join(sorted(right_bones))}")
    else:
        messages.append("No symmetric bone pairs detected")
        is_symmetric = False
    
    return is_symmetric, messages

def validate_symmetry(bones: Dict[str, Bone], base: str, left: str, right: str) -> bool:
    """Validate if matching left and right bones exist for a given base bone name"""
    # First try the new intelligent detection
    symmetric_pairs = find_symmetric_bone_pairs(bones)
    
    # Look for bones that match the requested base type
    matching_left_bones = []
    matching_right_bones = []
    
    # Check each detected symmetric pair
    for pair_base, (left_bones, right_bones) in symmetric_pairs.items():
        if base.lower() in pair_base.lower() or pair_base.lower() in base.lower():
            matching_left_bones.extend(left_bones)
            matching_right_bones.extend(right_bones)
    
    if matching_left_bones or matching_right_bones:
        left_bases = {}
        right_bases = {}
        
        for bone_name in matching_left_bones:
            bone_base, side = extract_bone_side_info(bone_name)
            if bone_base not in left_bases:
                left_bases[bone_base] = []
            left_bases[bone_base].append(bone_name)
        
        for bone_name in matching_right_bones:
            bone_base, side = extract_bone_side_info(bone_name)
            if bone_base not in right_bases:
                right_bases[bone_base] = []
            right_bases[bone_base].append(bone_name)
        
        all_bases = set(left_bases.keys()) | set(right_bases.keys())
        for bone_base in all_bases:
            left_count = len(left_bases.get(bone_base, []))
            right_count = len(right_bases.get(bone_base, []))
            if left_count != right_count:
                return False
        
        return len(all_bases) > 0
    
    # Fallback to original dictionary-based method
    left_bone_names = set()
    right_bone_names = set()
    
    # Normalize bone names in the bones dict for comparison
    normalized_bones = {simplify_bonename(name): name for name in bones.keys()}
    
    # Add standard bones
    for key, value in standard_bones.items():
        if base in key.lower():
            if '_l' in key.lower():
                left_bone_names.add(simplify_bonename(value))
            elif '_r' in key.lower():
                right_bone_names.add(simplify_bonename(value))
                
    # Add acceptable bones
    for key, names in acceptable_bone_names.items():
        if base in key.lower():
            if '_l' in key.lower():
                left_bone_names.update(simplify_bonename(name) for name in names)
            elif '_r' in key.lower():
                right_bone_names.update(simplify_bonename(name) for name in names)
    
    # Check if at least one pair exists and matches
    left_exists = any(name in normalized_bones for name in left_bone_names)
    right_exists = any(name in normalized_bones for name in right_bone_names)
    
    return left_exists == right_exists

def validate_finger_chain(bones: Dict[str, Bone], chain: Tuple[str, ...]) -> bool:
    """Validate if a finger bone chain has correct hierarchy"""
    for i in range(len(chain) - 1):
        if not validate_bone_hierarchy(bones, chain[i], chain[i + 1]):
            return False
    return True

def check_acceptable_standards(bones: Dict[str, Bone]) -> bool:
    """Check if armature matches acceptable non-standard hierarchy"""
    logger.debug("Checking for acceptable standards")
    
    # Create normalized lookup for existing bones
    normalized_bones = {simplify_bonename(name): name for name in bones.keys()}
    
    # Check if bones exist in acceptable list
    for bone_category, acceptable_names in acceptable_bone_names.items():
        found = False
        for name in acceptable_names:
            normalized_name = simplify_bonename(name)
            if normalized_name in normalized_bones:
                found = True
                break
        if not found:
            logger.debug(f"Missing acceptable bone for category: {bone_category}")
            return False
    
    # Validate acceptable hierarchy using normalized names
    for parent, child in acceptable_bone_hierarchy:
        parent_normalized = simplify_bonename(parent)
        child_normalized = simplify_bonename(child)
        
        # Find actual bone names from normalized names
        actual_parent = normalized_bones.get(parent_normalized)
        actual_child = normalized_bones.get(child_normalized)
        
        if actual_parent and actual_child:
            if not validate_bone_hierarchy(bones, actual_parent, actual_child):
                logger.debug(f"Invalid acceptable hierarchy: {actual_parent} -> {actual_child}")
                return False
                
    logger.debug("Armature meets acceptable standards")
    return True

def validate_tpose(armature):
    """Validate if armature is in a proper T-pose"""
    logger.debug(f"Validating T-pose for armature: {armature.name if armature else 'None'}")
    if not armature or armature.type != 'ARMATURE':
        logger.warning("No valid armature for T-pose validation")
        return False, [t("Validation.tpose.no_armature")]
    
    issues = []
    
    if armature.mode == 'POSE':
        bones_collection = armature.pose.bones
        get_direction = lambda bone: bone.matrix.to_3x3().col[1].normalized()
    else:
        bones_collection = armature.data.bones
        get_direction = lambda bone: bone.y_axis
    
    # Get left and right upper arm bones using standard bone names
    left_arm = None
    right_arm = None
    
    left_arm_candidates = [standard_bones['left_arm']]  # UpperArm.L
    if 'arm_l' in acceptable_bone_names:
        left_arm_candidates.extend(acceptable_bone_names['arm_l'])
    
    right_arm_candidates = [standard_bones['right_arm']]  # UpperArm.R
    if 'arm_r' in acceptable_bone_names:
        right_arm_candidates.extend(acceptable_bone_names['arm_r'])
    
    for name in left_arm_candidates:
        if name in armature.data.bones:
            left_arm = armature.data.bones[name]
            logger.debug(f"Found left arm bone: {name}")
            break
            
    for name in right_arm_candidates:
        if name in armature.data.bones:
            right_arm = armature.data.bones[name]
            logger.debug(f"Found right arm bone: {name}")
            break
    
    # Check arm bones are horizontal
    if left_arm:
        direction = left_arm.y_axis
        if abs(direction.x) < 0.7:  # Not pointing mostly along X axis
            logger.warning("Left arm is not horizontal")
            issues.append(t("Validation.tpose.left_arm_not_horizontal"))
    
    if right_arm:
        direction = right_arm.y_axis
        if abs(direction.x) < 0.7:  # Not pointing mostly along X axis
            logger.warning("Right arm is not horizontal")
            issues.append(t("Validation.tpose.right_arm_not_horizontal"))
    
    spine = None
    spine_candidates = [standard_bones['spine']]  # Spine
    if 'spine' in acceptable_bone_names:
        spine_candidates.extend(acceptable_bone_names['spine'])
    
    for name in spine_candidates:
        if name in armature.data.bones:
            spine = armature.data.bones[name]
            logger.debug(f"Found spine bone: {name}")
            break
            
    if spine:
        direction = spine.y_axis
        if abs(direction.z) < 0.7:  # Not pointing mostly along Z axis
            logger.warning("Spine is not vertical")
            issues.append(t("Validation.tpose.spine_not_vertical"))
    
    if issues:
        logger.warning(f"T-pose validation failed with {len(issues)} issues")
        return False, issues
    
    logger.info("T-pose validation successful")
    return True, []

def detect_scale_issues(bones):
    """Detect bones with abnormal scale (too small or too large)"""
    logger.debug("Detecting scale issues")
    scale_issues = []
    
    # Calculate median bone length for reference (more robust than average)
    lengths = [bone.length for bone in bones.values()]
    lengths.sort()
    
    if not lengths:
        logger.debug("No bones with length found")
        return []
    
    median_length = lengths[len(lengths) // 2]
    
    # Filter out zero-length bones for standard deviation calculation
    non_zero_lengths = [l for l in lengths if l > 0.0001]
    
    if not non_zero_lengths:
        logger.debug("No non-zero length bones found")
        return []
    
    mean = sum(non_zero_lengths) / len(non_zero_lengths)
    variance = sum((l - mean) ** 2 for l in non_zero_lengths) / len(non_zero_lengths)
    std_dev = math.sqrt(variance)
    
    small_threshold = max(median_length * 0.05, mean - 3 * std_dev)
    large_threshold = min(median_length * 15, mean + 5 * std_dev)
    
    logger.debug(f"Scale thresholds - small: {small_threshold}, large: {large_threshold}")
    
    # Get finger bones from standard and acceptable bone dictionaries
    finger_bone_names = set()
    
    for key in standard_bones:
        if any(finger in key.lower() for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger']):
            finger_bone_names.add(standard_bones[key])
    
    for key, names in acceptable_bone_names.items():
        if any(finger in key.lower() for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger']):
            finger_bone_names.update(names)
    
    for name, bone in bones.items():
        is_finger = (name in finger_bone_names or 
                    any(finger in name.lower() for finger in ['thumb', 'index', 'middle', 'ring', 'pinky', 'finger']))
        
        if bone.length < small_threshold and not is_finger:
            logger.debug(f"Bone {name} is too small: {bone.length}")
            scale_issues.append(f"- {name}: {t('Validation.scale_issue.too_small')} ({bone.length:.4f})")
        elif bone.length > large_threshold:
            logger.debug(f"Bone {name} is too large: {bone.length}")
            scale_issues.append(f"- {name}: {t('Validation.scale_issue.too_large')} ({bone.length:.4f})")
    
    logger.debug(f"Found {len(scale_issues)} scale issues")
    return scale_issues

def clear_bone_highlighting(armature: Object) -> None:
    """Clear bone highlighting by removing bone collections and resetting colors"""
    logger.debug(f"Clearing bone highlighting for armature: {armature.name if armature else 'None'}")
    if not armature or armature.type != 'ARMATURE':
        logger.warning("No valid armature for clearing bone highlighting")
        return
        
    current_mode = bpy.context.mode
    
    collection_name = "Problem Bones"
    if collection_name in armature.data.collections:
        problem_collection = armature.data.collections[collection_name]
        armature.data.collections.remove(problem_collection)
        logger.debug("Removed problem bones collection")
    
    for bone in armature.data.bones:
        bone.color.palette = 'DEFAULT'
    
    if len(armature.data.collections) == 0:
        armature.data.show_bone_colors = False
        logger.debug("Disabled bone colors display")
    
    logger.info("Bone highlighting cleared")
    return

class AvatarToolkit_OT_HighlightProblemBones(Operator):
    """Highlight bones that fail validation in the 3D viewport"""
    bl_idname = "avatar_toolkit.highlight_problem_bones"
    bl_label = t("Validation.highlight_problem_bones")
    bl_description = t("Validation.highlight_problem_bones_desc")
    
    @classmethod
    def poll(cls, context):
        return get_active_armature(context) is not None
    
    def execute(self, context):
        armature = get_active_armature(context)
        if not armature:
            logger.warning("No active armature found for highlighting problem bones")
            self.report({'ERROR'}, t("Validation.no_armature"))
            return {'CANCELLED'}
            
        logger.info(f"Highlighting problem bones for armature: {armature.name}")
        
        current_mode = context.mode
        
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        context.view_layer.objects.active = armature
        
        # First remove all bone collections
        collection_name = "Problem Bones"
        if collection_name in armature.data.collections:
            problem_collection = armature.data.collections[collection_name]
            armature.data.collections.remove(problem_collection)
            logger.debug("Removed existing problem bones collection")
        
        is_valid, messages, _ = validate_armature(armature)
        
        if is_valid:
            logger.info("No validation issues found")
            self.report({'INFO'}, t("Validation.no_issues"))
            bpy.ops.object.mode_set(mode='EDIT')
            return {'FINISHED'}
        
        problem_collection = armature.data.collections.new(name="Problem Bones")
        logger.debug("Created new problem bones collection")
        armature.data.show_bone_colors = True
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Extract bone names from validation messages
        problem_bones = self._extract_problem_bones(messages)
        
        # Assign bones to collection and set colors
        highlighted_count = 0
        for category, bone_names in problem_bones.items():
            for bone_name in bone_names:
                if bone_name in armature.data.edit_bones:
                    bone = armature.data.edit_bones[bone_name]
                    problem_collection.assign(bone)
                    
                    if 'hierarchy' in category.lower():
                        bone.color.palette = 'THEME09'  # Orange
                    elif 'scale' in category.lower():
                        bone.color.palette = 'THEME03'  # Yellow
                    else:
                        bone.color.palette = 'THEME01'  # Red
                    
                    highlighted_count += 1
        
        logger.info(f"Highlighted {highlighted_count} problem bones")
        self.report({'INFO'}, t("Validation.highlighting_complete"))
        return {'FINISHED'}
    
    def _extract_problem_bones(self, messages):
        problem_bones = {
            "Hierarchy Issues": [],
            "Scale Issues": [],
            "Missing Bones": []
        }
        
        # Extract bone names from validation messages
        for message in messages:
            if isinstance(message, str):
                # Parse message to extract bone names
                for line in message.split('\n'):
                    if '- ' in line:
                        bone_name = line.split('- ')[1].strip()
                        if ':' in bone_name:  # Handle "bone_name: message" format
                            bone_name = bone_name.split(':')[0].strip()
                        
                        if 'hierarchy' in message.lower():
                            problem_bones["Hierarchy Issues"].append(bone_name)
                        elif 'scale' in message.lower():
                            problem_bones["Scale Issues"].append(bone_name)
                        else:
                            problem_bones["Missing Bones"].append(bone_name)
        
        logger.debug(f"Extracted problem bones: {problem_bones}")
        return problem_bones

class AvatarToolkit_OT_ValidateTPose(Operator):
    """Validate if armature is in a proper T-pose"""
    bl_idname = "avatar_toolkit.validate_tpose"
    bl_label = t("Validation.tpose.label")
    bl_description = t("Validation.tpose.desc")
    
    @classmethod
    def poll(cls, context):
        return get_active_armature(context) is not None
    
    def execute(self, context):
        armature = get_active_armature(context)
        if not armature:
            logger.warning("No active armature found for T-pose validation")
            self.report({'ERROR'}, t("Validation.no_armature"))
            return {'CANCELLED'}
        
        logger.info(f"Validating T-pose for armature: {armature.name}")
        is_valid, messages = validate_tpose(armature)
        props = context.scene.avatar_toolkit
        props.tpose_validation_result = is_valid
        props.tpose_validation_messages.clear()
        
        for msg in messages:
            item = props.tpose_validation_messages.add()
            item.name = msg
        
        props.show_tpose_validation = True
        
        if is_valid:
            logger.info("T-pose validation successful")
            self.report({'INFO'}, t("Validation.tpose.valid"))
        else:
            for msg in messages:
                self.report({'WARNING'}, msg)
            logger.warning("T-pose validation failed")
            self.report({'WARNING'}, t("Validation.tpose.warning"))
        
        return {'FINISHED'}

class AvatarToolkit_OT_ClearBoneHighlighting(Operator):
    """Clear bone highlighting and reset bone colors"""
    bl_idname = "avatar_toolkit.clear_bone_highlighting"
    bl_label = t("Validation.clear_bone_highlighting")
    bl_description = t("Validation.clear_bone_highlighting_desc")
    
    @classmethod
    def poll(cls, context):
        return get_active_armature(context) is not None
    
    def execute(self, context):
        armature = get_active_armature(context)
        if not armature:
            logger.warning("No active armature found for clearing bone highlighting")
            self.report({'ERROR'}, t("Validation.no_armature"))
            return {'CANCELLED'}
        
        logger.info(f"Clearing bone highlighting for armature: {armature.name}")
        current_mode = context.mode
        
        # Switch to object mode as collection editing is not possible in edit mode
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        context.view_layer.objects.active = armature
        
        collection_name = "Problem Bones"
        if collection_name in armature.data.collections:
            # Remove the collection
            problem_collection = armature.data.collections[collection_name]
            armature.data.collections.remove(problem_collection)
            logger.debug("Removed problem bones collection")
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Reset all bone colors
        for bone in armature.data.edit_bones:
            bone.color.palette = 'DEFAULT'
        
        # Turn off bone colors display if no other collections are using it
        if len(armature.data.collections) == 0:
            armature.data.show_bone_colors = False
            logger.debug("Disabled bone colors display")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        logger.info("Bone highlighting cleared")
        self.report({'INFO'}, t("Validation.highlighting_cleared"))
        return {'FINISHED'}

class AvatarToolkit_OT_ValidateArmatureManual(Operator):
    """Manually validate armature and show results"""
    bl_idname = "avatar_toolkit.validate_armature_manual"
    bl_label = t("Validation.validate_now", "Validate Armature Now")
    bl_description = t("Validation.validate_now_desc", "Run armature validation and display detailed results")
    
    @classmethod
    def poll(cls, context):
        return get_active_armature(context) is not None
    
    def execute(self, context):
        armature = get_active_armature(context)
        if not armature:
            logger.warning("No active armature found for validation")
            self.report({'ERROR'}, t("Validation.no_armature"))
            return {'CANCELLED'}
        
        logger.info(f"Running manual validation for armature: {armature.name}")
        
        # Clear the validation cache to force a refresh
        from ..ui.quick_access_panel import clear_armature_caches
        clear_armature_caches()
        
        # Toggle the show_validation_results flag to display results
        props = context.scene.avatar_toolkit
        props.show_validation_results = True
        
        # Run validation
        is_valid, messages, is_acceptable = validate_armature(armature, detailed_messages=False)
        
        if is_valid:
            if is_acceptable:
                self.report({'INFO'}, t("Armature.validation.acceptable_standard.success"))
            else:
                self.report({'INFO'}, t("QuickAccess.valid_armature"))
        else:
            self.report({'WARNING'}, t("Validation.status.failed"))
        
        logger.info("Manual validation complete")
        return {'FINISHED'}
