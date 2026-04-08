import bpy
import numpy as np
from bpy.types import Operator, Context
from typing import Set, Literal
from ...core.translations import t
from ...core.logging_setup import logger
from ...core.common import get_active_armature, get_all_meshes
from ...core.armature_validation import validate_armature

import bmesh


class MapItem():
    length: int
    current_node: bmesh.types.BMVert
    marched_paths: list[bmesh.types.BMEdge]

class AvatarToolkit_OT_SelectShortestSeamPath(Operator):
    """Find the shortest seam path between two vertices."""
    bl_idname = "avatar_toolkit.find_shortest_seam_path"
    bl_label = t("Tools.find_shortest_seam_path")
    bl_description = t("Tools.find_shortest_seam_path_desc")
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        if context.mode != "EDIT_MESH":
            return False
        mesh_data: bpy.types.Mesh = context.active_object.data
        mesh = bmesh.from_edit_mesh(mesh_data)
        selected: int = 0
        for vert in mesh.verts:
            if vert.select == True:
                selected = selected+1
                if selected > 2:
                    return False
                found_seam: bool = False
                for edge in vert.link_edges:
                    if edge.seam:
                        found_seam = True
                if not found_seam:
                    return False
        if selected < 2:
            return False
        armature = get_active_armature(context)
        if not armature:
            return False
        valid, _, _ = validate_armature(armature)
        return valid
        
    def execute(self, context: Context) -> Set[str]:
        mesh_data: bpy.types.Mesh = context.active_object.data
        mesh = bmesh.from_edit_mesh(mesh_data)
        vert1: bmesh.types.BMVert = None
        vert2: bmesh.types.BMVert = None
        for vert in mesh.verts:
            if vert.select == True:
                if vert1 == None:
                    vert1 = vert
                else:
                    vert2 = vert
        
        current_verts: list[MapItem] = []

        first_item: MapItem  = MapItem()
        first_item.current_node = vert1
        first_item.length = 0
        first_item.marched_paths = []
        current_verts.append(first_item)

        def find_next_edge() -> list[bmesh.types.BMEdge]:
            if len(current_verts) == 0: #all paths have been exausted.
                return []
            for mapeditem in current_verts:
                current_verts.remove(mapeditem)
                for edge in mapeditem.current_node.link_edges:
                    if edge.seam and (edge not in mapeditem.marched_paths):
                        for vert_new in edge.verts:
                            if vert_new != mapeditem.current_node:
                                if vert_new == vert2:
                                    mapeditem.marched_paths.append(edge)
                                    return mapeditem.marched_paths
                                first_item: MapItem  = MapItem()
                                first_item.current_node = vert_new
                                first_item.length = mapeditem.length+1
                                first_item.marched_paths = []
                                first_item.marched_paths.extend(mapeditem.marched_paths)
                                first_item.marched_paths.append(edge)
                                current_verts.append(first_item)
            return find_next_edge()
            
        mesh.select_flush(False)
        path: list[bmesh.types.BMEdge] = find_next_edge()
        for edge in path:
            edge.select = True
            for vert in edge.verts:
                vert.select = True
        bpy.ops.mesh.select_mode(type='EDGE')
    
        return {'FINISHED'}

class AvatarToolkit_OT_ExplodeMesh(Operator):
    """Explodes the mesh for use with painting programs, or painting inside blender."""
    bl_idname = "avatar_toolkit.explode_mesh"
    bl_label = t("Tools.explode_mesh")
    bl_description = t("Tools.explode_mesh_desc")
    bl_options = {'REGISTER', 'UNDO'}
    distance: bpy.props.FloatProperty(default=2.0,name=t("Tools.explode_mesh.distance"),description=t("Tools.explode_mesh.distance_desc"))
    split_on_seams: bpy.props.BoolProperty(default=True,name=t("Tools.explode_mesh.split_on_seams"),description=t("Tools.explode_mesh.split_on_seams_desc"))

    def draw(self, context: Context) -> None:
        """Draw the operator's UI"""
        layout = self.layout
        layout.prop(self, "distance")

    def invoke(self, context: Context, event: bpy.types.Event) -> set[str]:
        """Initialize the operator"""
        return context.window_manager.invoke_props_dialog(self)
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        active_obj = context.view_layer.objects.active
        return (active_obj is not None and 
                active_obj.type == "MESH" and 
                len(context.view_layer.objects.selected) == 1)
    
    

    def execute(self, context: Context) -> Set[str]:

        mesh_obj: bpy.types.Object = context.view_layer.objects.active.type
        mesh: bpy.types.Mesh = context.view_layer.objects.active.data
        if(self.split_on_seams):
            
            #set to correct mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')

            #mark seams by islands
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.uv.select_all(action="SELECT")
            bpy.ops.uv.seams_from_islands(mark_seams=True,mark_sharp=False)
            
            #clear selection
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode='OBJECT')
            bm = bmesh.new()   # create an empty BMesh
            bm.from_mesh(mesh)   # fill it in from active mesh

            #select seam edges
            for idx,edge in enumerate(bm.edges):
                edge.select = edge.seam
            bm.to_mesh(mesh)
            bm.free()

            #split edges.
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.edge_split()
        
        #separate by loose.
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        
        bpy.ops.mesh.select_all(action="SELECT")
        
        bpy.ops.mesh.separate(type='LOOSE')

        
        distance: float = self.distance
        

        #set origins to geometry
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY",center="BOUNDS")

        #store original settings
        origin_only_orig: bool = context.scene.tool_settings.use_transform_data_origin
        pos_only_orig: bool = context.scene.tool_settings.use_transform_pivot_point_align
        parents_only_orig: bool = context.scene.tool_settings.use_transform_skip_children
        original_pivot: Literal['BOUNDING_BOX_CENTER', 'CURSOR', 'INDIVIDUAL_ORIGINS', 'MEDIAN_POINT', 'ACTIVE_ELEMENT'] = context.scene.tool_settings.transform_pivot_point 

        #set scene settings correctly.
        context.scene.tool_settings.use_transform_data_origin = False
        context.scene.tool_settings.use_transform_pivot_point_align = True
        context.scene.tool_settings.use_transform_skip_children = False
        context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'

        #spread out separated objects
        bpy.ops.transform.resize(value=(self.distance, self.distance, self.distance), orient_type='GLOBAL')
        
        #restore settings.
        context.scene.tool_settings.use_transform_data_origin = origin_only_orig
        context.scene.tool_settings.use_transform_pivot_point_align = pos_only_orig
        context.scene.tool_settings.use_transform_skip_children = parents_only_orig
        context.scene.tool_settings.transform_pivot_point = original_pivot
        return {'FINISHED'}