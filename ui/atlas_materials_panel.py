from bpy.types import UIList, Panel, UILayout, Object, Context, Material, Operator
import bpy
from math import sqrt
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .panel_layout import get_panel_order, should_open_by_default
from ..core.common import SceneMatClass, MaterialListBool, get_active_armature
from ..functions.atlas_materials import AvatarToolKit_OT_AtlasMaterials
from ..core.translations import t
from ..core.logging_setup import logger
import traceback

class AvatarToolKit_OT_SelectAllMaterials(Operator):
    bl_idname = 'avatar_toolkit.select_all_materials'
    bl_label = "Select All"
    bl_description = "Select all materials for atlas"

    def execute(self, context):
        for item in context.scene.avatar_toolkit.materials:
            item.mat.include_in_atlas = True
        return {'FINISHED'}

class AvatarToolKit_OT_SelectNoneMaterials(Operator):
    bl_idname = 'avatar_toolkit.select_none_materials'
    bl_label = "Select None"
    bl_description = "Deselect all materials"

    def execute(self, context):
        for item in context.scene.avatar_toolkit.materials:
            item.mat.include_in_atlas = False
        return {'FINISHED'}

class AvatarToolKit_OT_ExpandAllMaterials(Operator):
    bl_idname = 'avatar_toolkit.expand_all_materials'
    bl_label = "Expand All"
    bl_description = "Expand all material settings"

    def execute(self, context):
        for item in context.scene.avatar_toolkit.materials:
            item.mat.material_expanded = True
        return {'FINISHED'}

class AvatarToolKit_OT_CollapseAllMaterials(Operator):
    bl_idname = 'avatar_toolkit.collapse_all_materials'
    bl_label = "Collapse All"
    bl_description = "Collapse all material settings"

    def execute(self, context):
        for item in context.scene.avatar_toolkit.materials:
            item.mat.material_expanded = False
        return {'FINISHED'}

class AvatarToolKit_OT_ExpandSectionMaterials(Operator):
    bl_idname = 'avatar_toolkit.expand_section_materials'
    bl_label = ""
    bl_description = ""

    @classmethod
    def poll(cls, context: Context) -> bool:
        return True
        
    def execute(self, context: Context) -> set:
        try:
            if not context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown:
                context.scene.avatar_toolkit.materials.clear()
                newlist: list[Material] = []
                
                logger.debug("Loading materials for texture atlas")
                for obj in context.scene.objects:
                    if len(obj.material_slots) > 0:
                        for mat_slot in obj.material_slots:
                            if mat_slot.material:
                                if mat_slot.material not in newlist:
                                    newlist.append(mat_slot.material)
                                    newitem: SceneMatClass = context.scene.avatar_toolkit.materials.add()
                                    newitem.mat = mat_slot.material
                
                MaterialListBool.old_list[context.scene.name] = newlist
                context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown = True
                logger.info(f"Loaded {len(newlist)} materials for texture atlas")
            else:
                context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown = False
                logger.debug("Hiding material list")
            
            return {'FINISHED'}
        except Exception:
            logger.error(f"Error loading materials: {traceback.format_exc()}", exc_info=True)
            self.report({'ERROR'}, t("TextureAtlas.load_error"))
            return {'CANCELLED'}

class AvatarToolKit_UL_MaterialTextureAtlasProperties(UIList):
    bl_label = t("TextureAtlas.material_list_label")
    bl_idname = "Material_UL_avatar_toolkit_texture_atlas_mat_list_mat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw_header(self, context):
        layout = self.layout
        
        row = layout.row(align=True)
        row.scale_y = 1.2
        
        row.operator(AvatarToolKit_OT_SelectAllMaterials.bl_idname, text="", icon='CHECKBOX_HLT', 
                    emboss=True).tooltip = t("TextureAtlas.select_all_tooltip")
        row.operator(AvatarToolKit_OT_SelectNoneMaterials.bl_idname, text="", icon='CHECKBOX_DEHLT', 
                    emboss=True).tooltip = t("TextureAtlas.select_none_tooltip")
        row.separator(factor=0.5)
        row.operator(AvatarToolKit_OT_ExpandAllMaterials.bl_idname, text="", icon='DISCLOSURE_TRI_DOWN', 
                    emboss=True).tooltip = t("TextureAtlas.expand_all_tooltip")
        row.operator(AvatarToolKit_OT_CollapseAllMaterials.bl_idname, text="", icon='DISCLOSURE_TRI_RIGHT', 
                    emboss=True).tooltip = t("TextureAtlas.collapse_all_tooltip")
        
        row.separator(factor=1.0)
        search_row = row.row()
        search_row.scale_x = 2.0
        search_row.prop(context.scene.avatar_toolkit, "material_search_filter", text="", icon='VIEWZOOM')
        
        box = layout.box()
        size_row = box.row()
        size_row.alignment = 'CENTER'
        size_text = self.calculate_atlas_size(context)
        size_row.label(text=f"{t('TextureAtlas.estimated_size')}: {size_text}px", icon='TEXTURE')

    def draw_item(self, context: Context, layout: UILayout, data: Object, item: SceneMatClass, icon, active_data, active_propname, index):
        if context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown:
            if (context.scene.avatar_toolkit.material_search_filter and 
                context.scene.avatar_toolkit.material_search_filter.lower() not in item.mat.name.lower()):
                return

            # Main material
            row = layout.row()
            row.prop(item.mat, "include_in_atlas", text="", 
                    icon='CHECKBOX_HLT' if item.mat.include_in_atlas else 'CHECKBOX_DEHLT',
                    emboss=False) 
            
            # Material name
            row.prop(item.mat, "material_expanded", 
                    text=item.mat.name,
                    icon='DOWNARROW_HLT' if item.mat.material_expanded else 'RIGHTARROW',
                    emboss=False)
            
            row.label(text="", icon='MATERIAL')
            
            if item.mat.material_expanded:
                box = layout.box()
                col = box.column(align=True)
                
                header_row = col.row()
                header_row.alignment = 'CENTER'
                header_row.label(text=t("TextureAtlas.texture_maps"), icon='IMAGE')
                col.separator(factor=0.5)
                self.draw_texture_row(col, item.mat, "texture_atlas_albedo", "IMAGE_RGB", t("TextureAtlas.albedo"))
                self.draw_texture_row(col, item.mat, "texture_atlas_normal", "NORMALS_FACE", t("TextureAtlas.normal"))
                self.draw_texture_row(col, item.mat, "texture_atlas_emission", "LIGHT", t("TextureAtlas.emission"))
                self.draw_texture_row(col, item.mat, "texture_atlas_ambient_occlusion", "SHADING_SOLID", t("TextureAtlas.ambient_occlusion"))
                self.draw_texture_row(col, item.mat, "texture_atlas_height", "IMAGE_ZDEPTH", t("TextureAtlas.height"))
                self.draw_texture_row(col, item.mat, "texture_atlas_roughness", "MATERIAL", t("TextureAtlas.roughness"))
                
                col.separator(factor=0.5)
                
                status_row = col.row()
                status_row.alignment = 'CENTER'
                is_ready = self.is_material_ready(item.mat)
                
                if item.mat.include_in_atlas:
                    status_text = t("TextureAtlas.material_ready") if is_ready else t("TextureAtlas.material_not_ready")
                    status_icon = 'CHECKMARK' if is_ready else 'ERROR'
                else:
                    status_text = t("TextureAtlas.material_not_included")
                    status_icon = 'INFO'
                
                status_row.label(text=status_text, icon=status_icon)

    def draw_texture_row(self, layout, material, prop_name, icon, label_text):
        row = layout.row(align=True)
        icon_row = row.row()
        icon_row.scale_x = 0.5
        icon_row.label(text="", icon=icon)
        
        # Texture selector
        row.prop(material, prop_name, text=label_text)
        status_row = row.row()
        status_row.scale_x = 0.5
        if getattr(material, prop_name):
            status_row.label(text="", icon='CHECKMARK')
        else:
            status_row.label(text="", icon='X')

    def is_material_ready(self, material):
        return bool(material.texture_atlas_albedo or 
                   material.texture_atlas_normal or 
                   material.texture_atlas_emission)

    def calculate_atlas_size(self, context):
        total_size = 0
        selected_count = 0
        
        for mat in context.scene.avatar_toolkit.materials:
            if mat.mat.include_in_atlas:
                selected_count += 1
                if mat.mat.texture_atlas_albedo:
                    img = bpy.data.images[mat.mat.texture_atlas_albedo]
                    total_size += img.size[0] * img.size[1]
        
        if total_size == 0:
            return f"0x0 ({t('TextureAtlas.no_materials_selected')})"
        size = int(sqrt(total_size))
        pot_size = 2 ** (size - 1).bit_length()  # Next power of 2
        
        return f"{pot_size}x{pot_size} ({selected_count} {t('TextureAtlas.materials')})"

class AvatarToolKit_PT_TextureAtlasPanel(Panel):
    bl_label = t("TextureAtlas.label")
    bl_idname = "OBJECT_PT_avatar_toolkit_texture_atlas"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORY_NAME
    bl_parent_id = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order = get_panel_order('texture_atlas')
    bl_options = set() if not should_open_by_default('TEXTURE_ATLAS') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context):
        layout = self.layout
        armature = get_active_armature(context)
        
        if armature:
            header_row = layout.row()
            header_row.label(text=t("TextureAtlas.label"), icon='TEXTURE')
            layout.separator(factor=0.5)
            info_box = layout.box()
            info_col = info_box.column()
            info_col.scale_y = 0.9
            info_col.label(text=t("TextureAtlas.description_1"), icon='INFO')
            info_col.label(text=t("TextureAtlas.description_2"))
            
            if not bpy.data.filepath:
                warning_box = layout.box()
                warning_col = warning_box.column()
                warning_col.scale_y = 0.9
                warning_col.alert = True
                warning_col.label(text=t("TextureAtlas.save_file_first"), icon='ERROR')
                warning_col.label(text=t("TextureAtlas.save_file_instructions"))
                warning_col.operator("wm.save_as_mainfile", text=t("TextureAtlas.save_file_button"), icon='FILE_TICK')
                layout.separator(factor=0.5)
            
            layout.separator(factor=0.5)
            box = layout.box()
            row = box.row(align=True)
            row.scale_y = 1.2
            direction_icon = 'RIGHTARROW' if not context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown else 'DOWNARROW_HLT'
            button_text = t("TextureAtlas.reload_list") if not context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown else t("TextureAtlas.loaded_list")
            row.operator(AvatarToolKit_OT_ExpandSectionMaterials.bl_idname, 
                        text=button_text, 
                        icon=direction_icon)
            
            # Material list expanded
            if context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown:
                row = box.row()
                row.template_list(AvatarToolKit_UL_MaterialTextureAtlasProperties.bl_idname, 
                                'material_list', 
                                context.scene.avatar_toolkit, 
                                'materials', 
                                context.scene.avatar_toolkit, 
                                'texture_atlas_material_index', 
                                rows=12, 
                                type='DEFAULT')
            
            layout.separator(factor=1.0)
            
            row = layout.row()
            row.scale_y = 1.5
            row.enabled = context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown
            
            has_selected = False
            if context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown:
                for item in context.scene.avatar_toolkit.materials:
                    if item.mat.include_in_atlas:
                        has_selected = True
                        break
            
            if not has_selected and context.scene.avatar_toolkit.texture_atlas_Has_Mat_List_Shown:
                row.operator(AvatarToolKit_OT_AtlasMaterials.bl_idname, 
                            text=t("TextureAtlas.no_materials_selected"), 
                            icon='ERROR')
            else:
                row.operator(AvatarToolKit_OT_AtlasMaterials.bl_idname, 
                            text=t("TextureAtlas.atlas_materials"), 
                            icon='NODE_TEXTURE')
        else:
            layout.label(text=t("Tools.select_armature"), icon='ERROR')
            
            box = layout.box()
            col = box.column()
            col.scale_y = 0.9
            col.label(text=t("TextureAtlas.select_armature_first"), icon='INFO')
            col.label(text=t("TextureAtlas.how_to_use_1"))
            col.label(text=t("TextureAtlas.how_to_use_2"))
