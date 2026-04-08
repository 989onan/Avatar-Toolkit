import traceback
import bpy
import re
from typing import Any, Set, Dict, List, Optional, Tuple
from bpy.types import (
    Operator, 
    Context, 
    Object, 
    Material, 
    NodeTree,
    ShaderNodeTexImage
)
import mathutils
import bmesh
from ...core.logging_setup import logger
from ...core.translations import t
from ...core.common import (
    get_active_armature,
    get_all_meshes,
    ProgressTracker,
    calculate_bone_orientation,
    add_armature_modifier,
    get_modifiers,
    has_shapekeys
)
from ...core.armature_validation import validate_armature

class AvatarToolkit_OT_ApplyModifierForShapkeyObj(bpy.types.Operator):
    """Operator for forcing the application of a modifier. A shortened way of saying \"Apply modifier for object with shapekeys\""""
    bl_idname: str = 'avatar_toolkit.apply_shapekey_force'
    bl_label: str = t('Tools.apply_modifier_on_shapekey_obj')
    bl_description: str = t('Tools.apply_modifier_on_shapekey_obj_desc')
    bl_options: Set[str] = {'REGISTER', 'UNDO'}

    modifier: bpy.props.EnumProperty(items=get_modifiers,name="Modifier To Apply")


    def draw(self, context: Context) -> None:
        """Draw the operator's UI"""
        layout = self.layout
        layout.prop(self, "modifier")

    def invoke(self, context: Context, event: bpy.types.Event) -> set[str]:
        """Initialize the operator"""
        return context.window_manager.invoke_props_dialog(self)
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        if context.active_object != None:
            return context.active_object.type == "MESH"
        return False
    
    def execute(self, context: Context) -> Set[str]:
        
        obj: bpy.types.Object = context.active_object
        mesh: bpy.types.Mesh = obj.data

        shapes: list[bpy.types.Object] = []
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        if has_shapekeys(obj):
            #reset shapekeys
            for idx,key in enumerate(mesh.shape_keys.key_blocks):
                obj.active_shape_key_index = idx
                obj.active_shape_key.value = 0
                
            for idx,key in enumerate(mesh.shape_keys.key_blocks):
                # duplicate object for shapekey
                bpy.ops.object.select_all(action="DESELECT")
                context.view_layer.objects.active = obj
                obj.select_set(True) 
                bpy.ops.object.duplicate()
                
                # name new object after shapekey
                new_obj = context.view_layer.objects.active
                new_obj.select_set(True) 
                new_obj.active_shape_key_index = idx
                new_obj.name = new_obj.active_shape_key.name
                
                #add to cleanup list
                shapes.append(new_obj)
                
                #make basis the same shape as shapekey
                for idx,point in enumerate(new_obj.active_shape_key.points):
                    new_obj.data.vertices[idx].co.xyz = point.co.xyz

                #remove all shaoekeys on new object and then apply modifier
                bpy.ops.object.shape_key_remove(all=True,apply_mix=False)
                try:
                    bpy.ops.object.modifier_apply(modifier=self.modifier)
                except Exception as e:
                    self.report({'ERROR'}, f"Shapekey modifier apply for shapekey \"{new_obj.name}\" failed!!")
                    print(f"Shapekey modifier apply for shapekey \"{new_obj.name}\" failed!!")
                    print(traceback.format_exc(e))
                    #clean up after critical failure
                    for shape in shapes: 
                       bpy.data.objects.remove(shape)#faster than ops delete
                bpy.ops.object.select_all(action="DESELECT")
                    
                    
                    
            try:
                #remove shapekeys on original object
                bpy.ops.object.select_all(action="DESELECT")    
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.object.shape_key_remove(all=True,apply_mix=False)
                bpy.ops.object.modifier_apply(modifier=self.modifier)
                bpy.ops.object.select_all(action="DESELECT")    
                #delete first shapekey object aka basis
                bpy.data.objects.remove(shapes.pop(0))

                #join all objects with applied modifiers back together as shapes
                for shape in shapes:
                    shape.select_set(True)
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.object.join_shapes()
            except Exception:
                
                self.report({'ERROR'}, f"Shapekey joining failed!!")
                print(f"Shapekey joining failed!!")
                print(traceback.format_exc())
                
            #final clean up
            for shape in shapes: 
                bpy.data.objects.remove(shape)#faster than ops delete

        else:
            #mesh has no shapekeys, just apply normally.
            bpy.ops.object.modifier_apply(modifier=self.modifier)



        return {'FINISHED'}
    

