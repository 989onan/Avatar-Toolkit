from ast import Dict
from itertools import count
import bpy
import re
from typing import List, Tuple, Optional, TypedDict
from bpy.types import Material, Operator, Context, Object
from ..core.register import register_wrap
from ..core.common import get_selected_armature, is_valid_armature, select_current_armature, get_all_meshes
from ..functions.translations import t

class meshEntry(TypedDict):
    mesh: bpy.types.Object
    shapekeys: list[str]

@register_wrap
class RemoveDoublesSafely(Operator):
    bl_idname = "avatar_toolkit.remove_doubles_safely"
    bl_label = t("Optimization.remove_doubles_safely.label")
    bl_description = t("Optimization.remove_doubles_safely.desc")
    bl_options = {'REGISTER', 'UNDO'}
    objects_to_do: list[meshEntry] = []
    merge_distance: bpy.props.FloatProperty(default=0.0001)

    @classmethod
    def poll(cls, context: Context) -> bool:
        armature = get_selected_armature(context)
        return armature is not None and is_valid_armature(armature)

    def execute(self, context: Context) -> set:
        if not select_current_armature(context):
            self.report({'WARNING'}, t("Optimization.no_armature_selected"))
            return {'CANCELLED'}

        armature = get_selected_armature(context)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        objects: List[Object] = get_all_meshes(context)

        for mesh in objects:
            if mesh.data.name not in [stored_object["mesh"].data.name for stored_object in self.objects_to_do]:
                mesh_shapekeys = {"mesh":mesh,"shapekeys":[]}
                mesh_data: bpy.types.Mesh = mesh.data
                shape: bpy.types.ShapeKey = None
                if mesh_data.shape_keys:
                    for shape in mesh_data.shape_keys.key_blocks:
                        mesh_shapekeys["shapekeys"].append(shape.name)
                self.objects_to_do.append(mesh_shapekeys)
        
        return {'FINISHED'}
        
    def invoke(self, context: Context, event: bpy.types.Event) -> set:
        self.execute(context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modify_mesh(self, context: Context, mesh: meshEntry):
        mesh["mesh"].select_set(True)
        context.view_layer.objects.active = mesh["mesh"]
        context.view_layer.objects.active = mesh["mesh"]
        mesh_data: bpy.types.Mesh = mesh["mesh"].data
        bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        for index, point in enumerate(mesh["mesh"].active_shape_key.points):
            if point.co.xyz != mesh_data.shape_keys.key_blocks[0].points[index].co.xyz:
                mesh_data.vertices[index].select = True
                print("shapekey has a moved vertex at index \""+str(index)+"\", excluding from double merging!")
        bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        mesh["mesh"].select_set(False)

    def modal(self, context: Context, event: bpy.types.Event) -> set:
        if len(self.objects_to_do) > 0:
            mesh = self.objects_to_do[0]
            mesh_data: bpy.types.Mesh = mesh["mesh"].data
            if len(mesh['shapekeys']) > 0:
                shapekeyname: str = mesh['shapekeys'].pop(0)
                
                target_shapekey: int = mesh_data.shape_keys.key_blocks.find(shapekeyname)
                mesh["mesh"].active_shape_key_index = target_shapekey
                print("doing shapekey \""+shapekeyname+"\" on mesh \""+mesh['mesh'].name+"\".")
                self.modify_mesh(context, mesh)

            elif not (mesh_data.shape_keys):
                print("doing mesh with no shapekeys named \""+mesh['mesh'].name+"\".")
                mesh["mesh"].select_set(True)
                context.view_layer.objects.active = mesh["mesh"]
                bpy.ops.object.mode_set(mode='EDIT')
                mesh_data.vertices.foreach_set("select",[False]*len(mesh_data.vertices))
    
                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.remove_doubles(threshold=self.merge_distance,use_unselected=False)

                bpy.ops.object.mode_set(mode='OBJECT')
                mesh["mesh"].select_set(False)
                self.objects_to_do.pop(0)
            else:
                mesh["mesh"].select_set(True)
                context.view_layer.objects.active = mesh["mesh"]
                bpy.ops.object.mode_set(mode='EDIT')

                bpy.ops.mesh.select_all(action="INVERT")
                bpy.ops.mesh.remove_doubles(threshold=self.merge_distance,use_unselected=False)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                mesh["mesh"].select_set(False)
                
                self.objects_to_do.pop(0)
                if len(self.objects_to_do) > 0:
                    mesh = self.objects_to_do[0]
                    mesh["mesh"].select_set(True)
                    context.view_layer.objects.active = mesh["mesh"]
                    bpy.ops.object.mode_set(mode='EDIT')
                    mesh_data.vertices.foreach_set("select",[False]*len(mesh_data.vertices))
                    bpy.ops.object.mode_set(mode='OBJECT')
                    mesh["mesh"].select_set(False)

        else:
            self.report({'INFO'}, t("Optimization.remove_doubles_completed"))
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
