import bpy
from typing import Set
from bpy.types import Panel, Context, UILayout, Operator
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .ui_utils import UIStyle, draw_section_header, draw_operator_row
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t
from ..functions.optimization.materials_tools import AvatarToolkit_OT_CombineMaterials
from ..functions.optimization.remove_doubles import AvatarToolkit_OT_RemoveDoubles
from ..functions.optimization.mesh_tools import AvatarToolkit_OT_JoinAllMeshes, AvatarToolkit_OT_JoinSelectedMeshes

class AvatarToolKit_PT_OptimizationPanel(Panel):
    """Panel containing mesh and material optimization tools for avatar optimization"""
    bl_label: str = t("Optimization.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit_optimization"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('optimization')
    bl_options = set() if not should_open_by_default('OPTIMIZATION') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draws the optimization panel interface with material, mesh cleanup and join mesh tools"""
        layout: UILayout = self.layout
        
        # Materials section
        col = draw_section_header(layout, t("Optimization.materials_title"), icon='MATERIAL')
        col.operator(AvatarToolkit_OT_CombineMaterials.bl_idname, icon='MATERIAL')
        
        # Mesh Cleanup section
        col = draw_section_header(layout, t("Optimization.cleanup_title"), icon='MESH_DATA')
        col.operator(AvatarToolkit_OT_RemoveDoubles.bl_idname, icon='MESH_DATA')
        
        # Join Meshes section
        col = draw_section_header(layout, t("Optimization.join_meshes_title"), icon='OBJECT_DATA')
        draw_operator_row(col, [
            (AvatarToolkit_OT_JoinAllMeshes.bl_idname, t("Optimization.join_all_meshes"), 'OBJECT_DATA'),
            (AvatarToolkit_OT_JoinSelectedMeshes.bl_idname, t("Optimization.join_selected_meshes"), 'RESTRICT_SELECT_OFF')
        ])
