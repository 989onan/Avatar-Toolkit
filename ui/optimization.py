import bpy
from ..core.register import register_wrap
from .panel import AvatarToolkitPanel

@register_wrap
class AvatarToolkitOptimizationPanel(bpy.types.Panel):
    bl_label = "Optimization"
    bl_idname = "OBJECT_PT_avatar_toolkit_optimization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Avatar Toolkit"
    bl_parent_id = "OBJECT_PT_avatar_toolkit"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Optimization Options")
        
        row = layout.row()
        row.scale_y = 1.2 
        row.operator("avatar_toolkit.combine_materials", text="Combine Materials")

        layout.separator(factor=0.5)
        
        row = layout.row(align=True)
        row.scale_y = 1.2 
        row.operator("avatar_toolkit.join_all_meshes", text="Join All Meshes")
        row.operator("avatar_toolkit.join_selected_meshes", text="Join Selected Meshes")

        # Add optimization options here

