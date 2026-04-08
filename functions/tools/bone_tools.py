import traceback
import bpy
import bpy_extras
from bpy_extras import anim_utils
import re
from bpy.types import Operator, Context, EditBone, Object, Armature, Mesh
from typing import Optional, Dict, Any, List, Tuple
from ...core.translations import t
from ...core.common import (
    get_active_armature, 
    get_all_meshes,
    ProgressTracker,
    restore_bone_transforms,
    remove_unused_vertex_groups,
    identify_bones,
    duplicate_bone,
    store_breaking_settings_armature,
    restore_breaking_settings_armature,
)
import traceback
from ...core.armature_validation import validate_armature, validate_bone_hierarchy


class AvatarToolKit_OT_CreateDigitigradeLegs(Operator):
    """Operator to convert standard legs to digitigrade setup"""
    bl_idname = "avatar_toolkit.create_digitigrade"
    bl_label = t("Tools.create_digitigrade")
    bl_description = t("Tools.create_digitigrade_desc")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Check if operator can be executed"""
        armature = get_active_armature(context)
        if not armature:
            return False
        valid, _, _ = validate_armature(armature)
        return (valid and 
                (context.mode == 'EDIT_ARMATURE' or context.mode == 'POSE') and
                context.selected_editable_bones is not None and
                len(context.selected_editable_bones) == 2)
    
    def process_leg_chain(self, digi0: EditBone) -> bool:
        """Process a single leg bone chain"""
        try:
            bpy.ops.object.mode_set(mode='EDIT')

            # Get bone chain
            digi1: EditBone = digi0.children[0]
            digi2: EditBone = digi1.children[0]
            digi3: EditBone = digi2.children[0]
            digi4: Optional[EditBone] = digi3.children[0] if digi3.children else None

            # Clear roll for all bones
            for bone in [digi0, digi1, digi2, digi3] + ([digi4] if digi4 else []):
                bone.select = True
            bpy.ops.armature.roll_clear()
            bpy.ops.armature.select_all(action='DESELECT')
            
            # Create and position calf bone
            prev_connect = digi1.use_connect
            digi1.use_connect = False
            calf = duplicate_bone(digi1)
            digi1.use_connect = prev_connect
            calf.name = digi1.name.split('.')[0]
            calf.parent = digi0
            
            # Calculate new positions
            
            
            end = (((digi0.tail-digi0.head)*(1/digi0.length))*(digi0.length+digi2.length) + digi0.head)
            calf.head = end
            calf.tail = (digi1.tail-digi1.head)+calf.head
            digi2.tail = calf.tail
            
            # Reparent foot to new calf
            digi3.parent = calf

            #enforce parallelagram onto midparts.
            digi1.tail = (digi0.tail)+(calf.tail-calf.head)
            
            calf.name = calf.name.replace("<noik>","")
            
            # Mark original bones as non-IK
            for bone in [digi1, digi2]:
                if "<noik>" not in bone.name:
                    bone.name = bone.name.split('.')[0] + "<noik>"
            return True

        except Exception as e:
            self.report({'ERROR'}, t("Tools.digitigrade_error", error=traceback.format_exc()))
            return False

    def execute(self, context: Context) -> set[str]:
        """Execute the digitigrade conversion"""
        bpy.ops.object.mode_set(mode='EDIT')
        data_breaking = store_breaking_settings_armature(context.active_object)
        with ProgressTracker(context, len(context.selected_editable_bones), t("Tools.digitigrade")) as progress:
            for digi0 in context.selected_editable_bones:
                progress.step(t("Tools.processing_leg", bone=digi0.name))
                if not self.process_leg_chain(digi0):
                    return {'CANCELLED'}
        restore_breaking_settings_armature(context.active_object, data_breaking)
        self.report({'INFO'}, t("Tools.digitigrade_success"))
        return {'FINISHED'}

class AvatarToolKit_OT_DeleteBoneConstraints(Operator):
    """Operator to remove all bone constraints from armature"""
    bl_idname = "avatar_toolkit.clean_constraints"
    bl_label = t("Tools.clean_constraints")
    bl_description = t("Tools.clean_constraints_desc")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Check if operator can be executed"""
        armature = get_active_armature(context)
        if not armature:
            return False
        valid, _, _ = validate_armature(armature)
        return valid

    def execute(self, context: Context) -> set[str]:
        """Execute the constraint removal operation"""
        bpy.ops.object.mode_set(mode='OBJECT')
        armature = get_active_armature(context)
        bpy.ops.object.select_all(action='DESELECT')
        armature.select_set(True)
        data_breaking = store_breaking_settings_armature(armature)

        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        constraints_removed = 0
        for bone in armature.pose.bones:
            while bone.constraints:
                bone.constraints.remove(bone.constraints[0])
                constraints_removed += 1

        bpy.ops.object.mode_set(mode='OBJECT')
        restore_breaking_settings_armature(armature, data_breaking)
        self.report({'INFO'}, t("Tools.clean_constraints_success", count=constraints_removed))
        return {'FINISHED'}

class AvatarToolKit_OT_RemoveZeroWeightBones(Operator):
    """Operator to remove bones with no vertex weights"""
    bl_idname = "avatar_toolkit.clean_weights"
    bl_label = t("Tools.clean_weights")
    bl_description = t("Tools.clean_weights_desc")
    bl_options = {'REGISTER', 'UNDO'}

    def should_preserve_bone(self, bone_name: str, context: Context) -> bool:
        """Check if bone should be preserved based on settings"""
        toolkit = context.scene.avatar_toolkit
        bone = context.active_object.data.bones.get(bone_name)
        
        if not bone:
            return False
            
        if toolkit.preserve_parent_bones and bone.children:
            return True
            
        if toolkit.target_bone_type == 'DEFORM' and not bone.use_deform:
            return True
            
        if toolkit.target_bone_type == 'NON_DEFORM' and bone.use_deform:
            return True
            
        return False

    def populate_bone_list(self, context: Context, zero_weight_bones: List[str]) -> None:
        """Populate the zero weight bones list"""
        toolkit = context.scene.avatar_toolkit
        toolkit.zero_weight_bones.clear()
        
        armature = get_active_armature(context)
        for bone_name in zero_weight_bones:
            bone = armature.data.bones.get(bone_name)
            if bone:
                item = toolkit.zero_weight_bones.add()
                item.name = bone_name
                item.has_children = len(bone.children) > 0
                item.is_deform = bone.use_deform

    def execute(self, context: Context) -> set[str]:
        """Execute the zero weight bone removal operation"""
        armature = get_active_armature(context)
        if not armature:
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        initial_transforms: Dict[str, Dict[str, Any]] = {}
        data_breaking = store_breaking_settings_armature(armature)

        for bone in armature.data.edit_bones:
            initial_transforms[bone.name] = {
                'head': bone.head.copy(),
                'tail': bone.tail.copy(),
                'roll': bone.roll,
                'matrix': bone.matrix.copy(),
                'parent': bone.parent.name if bone.parent else None
            }

        # Get bones with any weight
        weighted_bones: List[str] = []
        meshes = get_all_meshes(context)
        for mesh in meshes:
            for vertex in mesh.data.vertices:
                for group in vertex.groups:
                    if group.weight > context.scene.avatar_toolkit.merge_weights_threshold:
                        vg = mesh.vertex_groups[group.group]
                        if vg.name not in weighted_bones:
                            weighted_bones.append(vg.name)

        armature_data = armature.data
        removed_count = 0
        zero_weight_bones: List[str] = []

        def is_zero_weight_chain(bone, weighted_bones, preserve_check_fn):
            if bone.name in weighted_bones or preserve_check_fn(bone.name, context):
                return False
            return all(is_zero_weight_chain(child, weighted_bones, preserve_check_fn) for child in bone.children)

        for bone in armature_data.edit_bones[:]:
            if bone.name in weighted_bones or self.should_preserve_bone(bone.name, context):
                continue

            if not is_zero_weight_chain(bone, weighted_bones, self.should_preserve_bone):
                continue

            if context.scene.avatar_toolkit.list_only_mode:
                zero_weight_bones.append(bone.name)
                continue

            # Traverse and collect the full empty chain
            stack = [bone]
            chain = []

            while stack:
                b = stack.pop()
                chain.append(b)
                stack.extend(b.children)

            for b in reversed(chain):  # Remove children before parents
                for child in b.children:
                    child.use_connect = False
                    if b.parent:
                        child.parent = b.parent
                if b.name in armature_data.edit_bones:
                    armature_data.edit_bones.remove(b)
                    removed_count += 1

        bpy.ops.object.mode_set(mode='OBJECT')

        if context.scene.avatar_toolkit.list_only_mode:
            self.populate_bone_list(context, zero_weight_bones)
            return {'FINISHED'}

        restore_breaking_settings_armature(armature, data_breaking)
        self.report({'INFO'}, t("Tools.clean_weights_success", count=removed_count))
        return {'FINISHED'}

class AvatarToolKit_OT_RemoveZeroWeightVertexGroups(Operator):
    """Operator to remove vertex groups with no weights"""
    bl_idname = "avatar_toolkit.clean_vertex_groups"
    bl_label = t("Tools.clean_vertex_groups")
    bl_description = t("Tools.clean_vertex_groups_desc")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: Context) -> set[str]:
        meshes: list[bpy.types.Object] = get_all_meshes(context)
        removed: int = 0
        for mesh_obj in meshes:
            removed = removed+remove_unused_vertex_groups(mesh_obj)

        self.report({'INFO'}, t("Tools.vertex_groups_removed", count=removed))
        return {'FINISHED'}


class AvatarToolKit_OT_RemoveSelectedBones(Operator):
    """Operator to remove selected bones from the zero weight bones list"""
    bl_idname = "avatar_toolkit.remove_selected_bones"
    bl_label = t("Tools.remove_selected_bones")
    bl_description = t("Tools.remove_selected_bones_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context: Context) -> set[str]:
        armature = get_active_armature(context)
        data_breaking = store_breaking_settings_armature(armature)
        toolkit = context.scene.avatar_toolkit
        
        selected_bones = [item.name for item in toolkit.zero_weight_bones 
                         if item.selected]
        
        bpy.ops.object.mode_set(mode='EDIT')
        for bone_name in selected_bones:
            if bone_name in armature.data.edit_bones:
                armature.data.edit_bones.remove(armature.data.edit_bones[bone_name])
                
        bpy.ops.object.mode_set(mode='OBJECT')
        toolkit.zero_weight_bones.clear()
        restore_breaking_settings_armature(armature, data_breaking)
        self.report({'INFO'}, t("Tools.bones_removed", count=len(selected_bones)))
        return {'FINISHED'}


class AvatarToolKit_OT_FlipCurrentKeyFrames(Operator):
    """Operator to flip the selected bone keyframes using blender's flip pose."""
    bl_idname = "avatar_toolkit.flip_pose_frames"
    bl_label = t("Tools.flip_pose_frames")
    bl_description = t("Tools.flip_pose_frames_desc")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: Context) -> bool:
        """Check if operator can be executed"""
        armature = get_active_armature(context)
        if not armature:
            return False
        if context.mode != 'POSE':
            return False
        if not armature.animation_data:
            return False
        valid, _, _ = validate_armature(armature)
        return valid

    def execute(self, context: Context) -> set[str]:
        armature = get_active_armature(context)
        data_breaking = store_breaking_settings_armature(armature)
        
        

        armature_data: bpy.types.Armature = armature.data

        standard_mappings: Dict[str,str] = identify_bones(armature_data)

        

        
        # Do we need this? If flipping in the future has issues, then uncommenting this may help - @989onan
        #To make sure our flip pose is extremely reliable, we're gonna temp rename all bones to standard names to make the posing work.
        #for standard,bone_name in standard_mappings.items():
        #    armature_data.bones[bone_name].name = standard
        
        #save our selection
        selected: list[bool] = [False] * len(armature_data.bones)
        armature_data.bones.foreach_get("select", selected) 
        #select everything
        armature_data.bones.foreach_set("select", [False] * len(armature_data.bones)) 


        # Get channelbag for the action using Blender 5.0 API
        action = armature.animation_data.action
        if not action.slots:
            slot = action.slots.new(for_id=armature.data)
        else:
            slot = action.slots[0]
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
        
        #create a set for every frame time where we need to key a keyframe for the flipped pose
        times: Dict[float,list[bpy.types.FCurve]] = {}
        for curve in channelbag.fcurves:
            if not curve.data_path.startswith("pose"):
                continue
            for point in curve.keyframe_points:
                if point.select_control_point:
                    if point.co.x not in times:
                        times[point.co.x] = []
                
                    times[point.co.x].append(curve)

        for time,curves in times.items():
            context.scene.frame_set(frame=int(time), subframe=float(time-float(int(time))))
            armature_data.bones.foreach_set("select", [True] * len(armature_data.bones)) 
            bpy.ops.pose.copy()
            armature_data.bones.foreach_set("select", [False] * len(armature_data.bones)) 
            bpy.ops.pose.paste(flipped=True,selected_mask=False)
            

            

            for curve in curves:

                bone_name: str = curve.data_path.replace("pose.bones[\"","")
                bone_name = bone_name[:bone_name.index("\"")]
                
                armature_data.bones[bone_name].select = True

                bpy.ops.pose.select_mirror(extend=False)

                #this can get the opposite side bone's data path and key it, if it is ever needed - @989onan
                #for bone in armature_data.bones:
                #    if bone.select == True:
                #        bone_name = bone.name
                #        break
                #new_path = curve.data_path[:curve.data_path.index("[")+1]+"\""+bone_name+"\""+curve.data_path[curve.data_path.index("]"):]

                if armature.keyframe_insert(data_path=curve.data_path, index=curve.array_index, frame=time):
                    #if armature.keyframe_insert(data_path=new_path, index=curve.array_index, frame=time):
                    continue
                self.report({'ERROR'}, f"Keyframe insertion for key with data path \"{curve.data_path}\" and frame {time} failed!")
                restore_breaking_settings_armature(armature, data_breaking)
                return {'FINISHED'}


                    
        




        
        # Do we need this? If flipping in the future has issues, then uncommenting this may help - @989onan
        #bring our names back as to not break their model.
        #for standard,bone_name in standard_mappings.items():
        #    armature_data.bones[standard].name = bone_name

        # restore selection
        armature_data.bones.foreach_set("select", selected) 
        restore_breaking_settings_armature(armature, data_breaking)
        return {'FINISHED'}
