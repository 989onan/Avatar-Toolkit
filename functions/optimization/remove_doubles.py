import traceback
import bpy
import numpy as np
from typing import List, TypedDict, Any, Literal, TypeAlias, cast
from bpy.types import Operator, Context, Object, Event
from ...core.logging_setup import logger
from ...core.translations import t
from ...core.common import (
    get_active_armature,
    get_all_meshes,
)
from ...core.armature_validation import validate_armature
import bmesh
import mathutils

# Constants
MERGE_ITERATION_COUNT = 20
MERGE_DISTANCE_DEFAULT = 0.0001

# Type definitions
ModalReturnType: TypeAlias = Literal['RUNNING_MODAL', 'FINISHED', 'CANCELLED']

class MeshEntry(TypedDict):
    mesh: Object
    shapekeys: list[bpy.types.Object]

def create_duplicate_for_merge(context: Context, mesh: Object, shapekey_name: str = "") -> Object:
    """Creates a duplicate mesh object for merge testing"""

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    context.view_layer.objects.active = mesh
    bpy.ops.object.duplicate()
    duplicate = context.view_layer.objects.active
    
    if(shapekey_name != ""):
        for shape in duplicate.data.shape_keys.key_blocks:
            shape.value = 0
        duplicate.active_shape_key_index = mesh.data.shape_keys.key_blocks.find(shapekey_name)
        duplicate.active_shape_key.value = 1
        bpy.ops.object.shape_key_remove(all=True,apply_mix=True)
        duplicate.name = f"{shapekey_name}_object_is_{mesh.name}"
    else:
        duplicate.name = f"object_is_{mesh.name}"
    return duplicate

def select_obj(context: Context, obj: Object, target_mode='OBJECT'):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=target_mode)


class AvatarToolkit_OT_RemoveDoubles(Operator):
    bl_idname = "avatar_toolkit.remove_doubles"
    bl_label = t("Optimization.remove_doubles")
    bl_description = t("Optimization.remove_doubles_desc")
    bl_options = {'REGISTER', 'UNDO'}

    objects_to_do: list[MeshEntry] = []
    merge_distance: bpy.props.FloatProperty(name=t("Optimization.merge_distance"), description=t("Optimization.merge_distance_desc"), default=.001)
    @classmethod
    def poll(cls, context: Context) -> bool:
        """Check if the operator can be executed"""
        armature = get_active_armature(context)
        if not armature:
            return False
        valid, _, _ = validate_armature(armature)
        return valid

    def draw(self, context: Context) -> None:
        """Draw the operator's UI"""
        layout = self.layout
        layout.prop(self, "merge_distance")

    def invoke(self, context: Context, event: Event) -> set[str]:
        """Initialize the operator"""
        logger.info("Starting modal execution of merge doubles safely")
        return context.window_manager.invoke_props_dialog(self)

    def setup_mesh_entry(self, context: Context, mesh: Object) -> MeshEntry:
        """Set up mesh entry data structure"""
        #create shapekey objects to merge doubles on.
        shapes: list[bpy.types.Object] = []
        if(mesh.data.shape_keys):
            for shape in mesh.data.shape_keys.key_blocks:
                shapes.append(create_duplicate_for_merge(context,mesh,shape.name))
        else:
            shapes.append(create_duplicate_for_merge(context,mesh))
        mesh_entry: MeshEntry = {
            "mesh": mesh,
            "shapekeys": shapes
        }

        return mesh_entry

    def execute(self, context: Context) -> set[str]:
        """Execute the remove doubles operator"""
        try:
            armature = get_active_armature(context)
            if not armature:
                self.report({'WARNING'}, t("Optimization.no_armature"))
                return {'CANCELLED'}

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            objects = get_all_meshes(context)
            self.objects_to_do = []

            for mesh in objects:
                if mesh.data.name not in [obj["mesh"].data.name for obj in self.objects_to_do]:
                    logger.debug(f"Setting up data for object {mesh.name}")
                    mesh_entry = self.setup_mesh_entry(context, mesh)
                    self.objects_to_do.append(mesh_entry)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
            
        except Exception:
            logger.error(f"Error in execute: {traceback.format_exc()}")
            return {'CANCELLED'}
    def modal(self, context: Context, event: Event) -> set[ModalReturnType]:
        """Modal operator execution"""
        try:
            if not self.objects_to_do or len(self.objects_to_do) <= 0:
                self.report({'INFO'}, t("Optimization.remove_doubles_completed"))
                logger.info("Finishing modal execution of merge doubles safely")
                return {'FINISHED'}
            
            mesh: MeshEntry = self.objects_to_do.pop(0)
            merge_distance: float = self.merge_distance
            
            
            #find which vertices merge on all shapekeys using bmesh, a fast way of doing it - @989onan
            #final_merged_vertex_group = [i for i in range(0,len(mesh['mesh'].data.vertices))]
            final_merged_vertex_group: dict[set[int],list[int]] = []
            for shape in mesh["shapekeys"]:
                select_obj(context, shape, target_mode='EDIT')
                bmesh_mesh: bmesh.types.BMesh = bmesh.from_edit_mesh(shape.data)
                selected_verts: list[bmesh.types.BMVert] = [vert for vert in bmesh_mesh.verts if vert.select == True]
                i: int = 0
                merged_vertices: dict[set[int],list[int]] = {} #make a list of sets which act as pairs. the pairs being sets means it doesn't matter if element 0 is at index 1, it is still considered the same pair
                mergers: dict[bmesh.types.BMVert, bmesh.types.BMVert]
                for name,mergers in bmesh.ops.find_doubles(bmesh_mesh,verts=selected_verts,dist=merge_distance).items():
                    for source_vert,target_vert in mergers.items():
                        pair: set[int] = set()
                        pair.add(source_vert.index)
                        pair.add(target_vert.index)
                        frozen_pair = frozenset(pair)
                        merged_vertices[frozen_pair] = [source_vert.index,target_vert.index] #put the pairs we have found into a list.
                    
                if(final_merged_vertex_group == []): #populate list if it is empty
                    final_merged_vertex_group = merged_vertices
                new_dict: dict[set[int],list[int]] = {}

                #update our final list, keeping pairs that exist on all shapekeys and not just one.
                for key,value in final_merged_vertex_group.items():
                    if key in merged_vertices.keys():
                        new_dict[key] = value
                final_merged_vertex_group = new_dict 
            
            #create an edit mesh and ensure it's vertex table
            select_obj(context, mesh['mesh'], target_mode='EDIT')
            data_mesh: bpy.types.Mesh = mesh['mesh'].data
            mappings: dict[bmesh.types.BMVert,bmesh.types.BMVert] = {}
            bmesh_mesh: bmesh.types.BMesh = bmesh.from_edit_mesh(data_mesh)
            bmesh_mesh.verts.ensure_lookup_table()

            #turn our pairs into a dictionary, which allows for merging vertices based on the shared pairs.
            for key,value in final_merged_vertex_group.items():
                mappings[bmesh_mesh.verts[value[0]]] = bmesh_mesh.verts[value[1]]

            #weld the verts and update the source mesh
            bmesh.ops.weld_verts(bmesh_mesh,targetmap=mappings)
            bmesh.update_edit_mesh(data_mesh, destructive=True)

            #delete the shapekey reading meshes.
            for shape in mesh["shapekeys"]: 
                bpy.data.objects.remove(shape)

            return {'RUNNING_MODAL'}
            
        except Exception as e:
            print(traceback.format_exception(e))
            logger.error(f"Error in modal: {traceback.format_exception(e)}")
            return {'CANCELLED'}
