# GPL License

import bpy
from typing import Set, Dict, List, Optional, Any
from bpy.types import (
    Operator, 
    Panel, 
    Context, 
    UILayout, 
    WindowManager,
    Event,
    Object
)
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t
from ..core.logging_setup import logger
from ..core.common import get_active_armature, ProgressTracker

# Module-level cache for UI performance (avoids Blender scene property write restrictions)
_ui_cache = {
    'translation_status': {},
    'deepl_config': {},
    'libretranslate_config': {},
    'last_refresh_frame': 0,
    'cache_refresh_interval': 30
}


class AvatarToolkit_OT_TranslateNames(Operator):
    """Translate names using the translation system"""
    bl_idname: str = "avatar_toolkit.translate_names"
    bl_label: str = t("Translation.translate_names")
    bl_description: str = t("Translation.translate_names_desc")
    
    translation_type: bpy.props.EnumProperty(
        items=[
            ('bones', t("Translation.type.bones"), t("Translation.type.bones_desc")),
            ('shapekeys', t("Translation.type.shapekeys"), t("Translation.type.shapekeys_desc")),
            ('materials', t("Translation.type.materials"), t("Translation.type.materials_desc")), 
            ('objects', t("Translation.type.objects"), t("Translation.type.objects_desc")),
            ('all', t("Translation.type.all"), t("Translation.type.all_desc"))
        ],
        default='bones'
    )
    
    def execute(self, context: Context) -> Set[str]:
        logger.info(f"Starting translation operation: {self.translation_type}")
        
        try:
            from ..core.translation_manager import get_avatar_translation_manager
            manager = get_avatar_translation_manager()
            
            # Set up progress callback for detailed feedback
            def progress_callback(current: int, total: int, message: str):
                progress_percent = (current / max(total, 1)) * 100
                logger.info(f"Translation progress: {current}/{total} ({progress_percent:.1f}%) - {message}")
                context.area.header_text_set(f"Translating: {current}/{total} - {message}")
                
            manager.set_progress_callback(progress_callback)
            
            results = []
            armature = get_active_armature(context)
            
            total_steps = 0
            if self.translation_type == 'bones' or self.translation_type == 'all':
                if armature:
                    total_steps += len(armature.data.bones)
            if self.translation_type == 'shapekeys' or self.translation_type == 'all':
                meshes = [obj for obj in context.scene.objects if obj.type == 'MESH']
                for mesh in meshes:
                    if mesh.data.shape_keys:
                        total_steps += len(mesh.data.shape_keys.key_blocks)
            if self.translation_type == 'materials' or self.translation_type == 'all':
                materials = set()
                for obj in context.scene.objects:
                    if obj.type == 'MESH' and obj.data.materials:
                        for mat in obj.data.materials:
                            if mat:
                                materials.add(mat)
                total_steps += len(materials)
            if self.translation_type == 'objects' or self.translation_type == 'all':
                objects = [obj for obj in context.scene.objects if obj.type in {'MESH', 'ARMATURE', 'EMPTY'}]
                total_steps += len(objects)
            
            logger.info(f"Translation operation will process approximately {total_steps} items")
            
            with ProgressTracker(context, total_steps, "Translation") as progress:
                if self.translation_type == 'bones' or self.translation_type == 'all':
                    if armature:
                        logger.info(f"Starting bone translation for armature: {armature.name}")
                        self.report({'INFO'}, f"Translating {len(armature.data.bones)} bones...")
                        
                        bone_results = manager.translate_armature_bones(armature, apply_results=True)
                        results.extend(bone_results)
                        
                        successful_bones = sum(1 for r in bone_results if r.method not in ['failed', 'skipped'])
                        progress.step(f"Bones: {successful_bones}/{len(bone_results)} translated")
                        logger.info(f"Bone translation complete: {successful_bones}/{len(bone_results)} successful")
                    else:
                        self.report({'WARNING'}, t("Translation.no_armature"))
                        logger.warning("No armature selected for bone translation")
                        
                if self.translation_type == 'shapekeys' or self.translation_type == 'all':
                    meshes = [obj for obj in context.scene.objects if obj.type == 'MESH']
                    logger.info(f"Starting shape key translation for {len(meshes)} mesh objects")
                    
                    total_shapekeys = 0
                    for mesh in meshes:
                        if mesh.data.shape_keys:
                            shapekey_count = len(mesh.data.shape_keys.key_blocks)
                            self.report({'INFO'}, f"Translating {shapekey_count} shape keys in {mesh.name}...")
                            
                            shapekey_results = manager.translate_object_shapekeys(mesh, apply_results=True)
                            results.extend(shapekey_results)
                            total_shapekeys += len(shapekey_results)
                    
                    successful_shapekeys = sum(1 for r in results[-total_shapekeys:] if r.method not in ['failed', 'skipped'])
                    progress.step(f"Shape keys: {successful_shapekeys}/{total_shapekeys} translated")
                    logger.info(f"Shape key translation complete: {successful_shapekeys}/{total_shapekeys} successful")
                    
                if self.translation_type == 'materials' or self.translation_type == 'all':
                    logger.info("Starting material translation")
                    self.report({'INFO'}, "Translating materials...")
                    
                    material_results = manager.translate_scene_materials(apply_results=True)
                    results.extend(material_results)
                    
                    successful_materials = sum(1 for r in material_results if r.method not in ['failed', 'skipped'])
                    progress.step(f"Materials: {successful_materials}/{len(material_results)} translated")
                    logger.info(f"Material translation complete: {successful_materials}/{len(material_results)} successful")
                    
                if self.translation_type == 'objects' or self.translation_type == 'all':
                    logger.info("Starting object translation")
                    self.report({'INFO'}, "Translating objects...")
                    
                    object_results = manager.translate_scene_objects(apply_results=True)
                    results.extend(object_results)
                    
                    successful_objects = sum(1 for r in object_results if r.method not in ['failed', 'skipped'])
                    progress.step(f"Objects: {successful_objects}/{len(object_results)} translated")
                    logger.info(f"Object translation complete: {successful_objects}/{len(object_results)} successful")
            
            manager.set_progress_callback(None)
            context.area.header_text_set(None)
            
            # Final results summary
            successful = sum(1 for r in results if r.method not in ['failed', 'skipped'])
            total = len(results)
            
            dictionary_count = sum(1 for r in results if r.method == 'dictionary')
            api_count = sum(1 for r in results if r.method == 'api')
            cache_count = sum(1 for r in results if r.method == 'cache')
            failed_count = sum(1 for r in results if r.method == 'failed')
            
            logger.info(f"Translation summary: {successful}/{total} successful (Dictionary: {dictionary_count}, API: {api_count}, Cache: {cache_count}, Failed: {failed_count})")
            
            if successful > 0:
                success_msg = f"Successfully translated {successful}/{total} items"
                if dictionary_count > 0:
                    success_msg += f" (Dictionary: {dictionary_count}"
                if api_count > 0:
                    success_msg += f", API: {api_count}"
                if cache_count > 0:
                    success_msg += f", Cache: {cache_count}"
                if dictionary_count > 0 or api_count > 0 or cache_count > 0:
                    success_msg += ")"
                    
                self.report({'INFO'}, success_msg)
            else:
                if total > 0:
                    self.report({'WARNING'}, f"No translations were applied ({total} items checked)")
                else:
                    self.report({'WARNING'}, "No items found to translate")
                
            return {'FINISHED'}
            
        except Exception as e:
            try:
                manager.set_progress_callback(None)
                context.area.header_text_set(None)
            except:
                pass
                
            logger.error(f"Translation operation failed: {e}", exc_info=True)
            self.report({'ERROR'}, f"Translation failed: {str(e)}")
            return {'CANCELLED'}


class AvatarToolkit_OT_TestTranslationService(Operator):
    """Test the currently selected translation service"""
    bl_idname: str = "avatar_toolkit.test_translation_service"  
    bl_label: str = t("Translation.test_service")
    bl_description: str = t("Translation.test_service_desc")
    
    def execute(self, context: Context) -> Set[str]:
        logger.info("Starting translation service test")
        
        try:
            from ..core.translation_manager import get_avatar_translation_manager
            manager = get_avatar_translation_manager()
            
            self.report({'INFO'}, "Testing translation service...")
            context.area.header_text_set("Testing translation service...")
            
            # Test translation with a simple word
            test_word = "テスト"  # "Test" in Japanese
            logger.info(f"Testing translation of '{test_word}'")
            
            result = manager.translate_single(test_word, "auto")
            
            # Clear status
            context.area.header_text_set(None)
            
            if result.method == "failed":
                logger.error(f"Translation test failed: {result}")
                self.report({'ERROR'}, t("Translation.test_failed"))
            else:
                service_info = f" ({result.service})" if result.service else ""
                success_msg = f"Translation test successful: '{test_word}' → '{result.translated}' via {result.method}{service_info}"
                logger.info(f"Translation test successful: {result}")
                self.report({'INFO'}, success_msg)
                
            return {'FINISHED'}
            
        except Exception as e:
            try:
                context.area.header_text_set(None)
            except:
                pass
                
            logger.error(f"Translation service test failed: {e}", exc_info=True)
            self.report({'ERROR'}, f"Service test failed: {str(e)}")
            return {'CANCELLED'}


class AvatarToolkit_OT_ClearTranslationCache(Operator):
    """Clear all translation caches"""
    bl_idname: str = "avatar_toolkit.clear_translation_cache"
    bl_label: str = t("Translation.clear_cache")
    bl_description: str = t("Translation.clear_cache_desc")
    
    def execute(self, context: Context) -> Set[str]:
        try:
            from ..core.translation_manager import get_avatar_translation_manager
            manager = get_avatar_translation_manager()
            manager.clear_all_caches()
            
            self.report({'INFO'}, t("Translation.cache_cleared"))
            return {'FINISHED'}
            
        except Exception as e:
            logger.error(f"Failed to clear translation cache: {e}")
            self.report({'ERROR'}, f"Failed to clear cache: {str(e)}")
            return {'CANCELLED'}


class AvatarToolkit_OT_ConfigureDeepL(Operator):
    """Configure DeepL API settings"""
    bl_idname: str = "avatar_toolkit.configure_deepl"
    bl_label: str = t("Translation.configure_deepl")
    bl_description: str = t("Translation.configure_deepl_desc")
    
    api_key: bpy.props.StringProperty(
        name=t("Translation.deepl_api_key"),
        description=t("Translation.deepl_api_key_desc"),
        default="",
        subtype='PASSWORD'
    )
    
    def execute(self, context: Context) -> Set[str]:
        try:
            if not self.api_key.strip():
                self.report({'ERROR'}, "API key cannot be empty")
                return {'CANCELLED'}
                
            from ..core.translation_manager import configure_translation_service
            success = configure_translation_service("deepl", api_key=self.api_key.strip())
            
            if success:
                _ui_cache['deepl_config'].clear()
                _ui_cache['translation_status'].clear()
                if 'batch_info' in _ui_cache:
                    del _ui_cache['batch_info']
                self.report({'INFO'}, "DeepL API configured successfully")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to configure DeepL API - check your API key")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"DeepL configuration failed: {e}")
            self.report({'ERROR'}, f"Configuration failed: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        # Load existing API key if available
        try:
            from ..core.addon_preferences import get_preference
            existing_key = get_preference("deepl_api_key", "")
            if existing_key:
                # Show only first/last few characters for security
                if len(existing_key) > 8:
                    display_key = existing_key[:4] + "..." + existing_key[-4:]
                    self.api_key = existing_key  # Keep full key for editing
                else:
                    self.api_key = existing_key
        except:
            pass
            
        wm: WindowManager = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
    
    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        
        info_box = layout.box()
        info_col = info_box.column()
        info_col.label(text="DeepL API Configuration", icon='SETTINGS')
        info_col.separator()
        info_col.label(text="1. Visit deepl.com/pro to get your free API key")
        info_col.label(text="2. Free tier: 500,000 characters/month")
        info_col.label(text="3. Higher quality than other services")
        info_col.label(text="4. The Fastest Option due to native batching support")
        
        layout.separator()
        layout.prop(self, "api_key")


class AvatarToolkit_OT_ConfigureLibreTranslate(Operator):
    """Configure LibreTranslate server settings"""
    bl_idname: str = "avatar_toolkit.configure_libretranslate"
    bl_label: str = t("Translation.configure_libretranslate")
    bl_description: str = t("Translation.configure_libretranslate_desc")
    
    server_url: bpy.props.StringProperty(
        name=t("Translation.server_url"),
        description=t("Translation.server_url_desc"),
        default="https://libretranslate.com"
    )
    
    api_key: bpy.props.StringProperty(
        name=t("Translation.api_key"),
        description=t("Translation.api_key_desc"),
        default="",
        subtype='PASSWORD'
    )
    
    def execute(self, context: Context) -> Set[str]:
        try:
            if not self.server_url.strip():
                self.report({'ERROR'}, "Server URL cannot be empty")
                return {'CANCELLED'}
                
            from ..core.translation_manager import configure_translation_service
            success = configure_translation_service("libretranslate", 
                                                   server_url=self.server_url.strip(), 
                                                   api_key=self.api_key.strip() if self.api_key.strip() else None)
            
            if success:
                _ui_cache['libretranslate_config'].clear()
                _ui_cache['translation_status'].clear()
                if 'batch_info' in _ui_cache:
                    del _ui_cache['batch_info']
                self.report({'INFO'}, f"LibreTranslate server configured: {self.server_url}")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "Failed to connect to LibreTranslate server")
                return {'CANCELLED'}
                
        except Exception as e:
            logger.error(f"LibreTranslate configuration failed: {e}")
            self.report({'ERROR'}, f"Configuration failed: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        # Load existing server URL and API key if available
        try:
            from ..core.addon_preferences import get_preference
            existing_url = get_preference("libretranslate_url", "https://libretranslate.com")
            existing_api_key = get_preference("libretranslate_api_key", "")
            self.server_url = existing_url
            self.api_key = existing_api_key
        except:
            pass
            
        wm: WindowManager = context.window_manager
        return wm.invoke_props_dialog(self, width=500)
    
    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        
        info_box = layout.box()
        info_col = info_box.column()
        info_col.label(text="LibreTranslate Server Configuration", icon='SETTINGS')
        info_col.separator()
        info_col.label(text="⚠ libretranslate.com requires payment for API access")
        info_col.label(text="✓ You can run your own LibreTranslate server")
        info_col.label(text="✓ Or find community-hosted instances")
        info_col.separator()
        info_col.label(text="Examples:")
        info_col.label(text="  • Your server: https://translate.yoursite.com")
        info_col.label(text="  • Docker local: http://localhost:5000")
        
        layout.separator()
        layout.prop(self, "server_url")
        layout.prop(self, "api_key")


class AvatarToolkit_OT_TranslationStats(Operator):
    """Show translation statistics"""
    bl_idname: str = "avatar_toolkit.translation_stats"
    bl_label: str = t("Translation.show_stats")
    bl_description: str = t("Translation.show_stats_desc")
    
    def execute(self, context: Context) -> Set[str]:
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        wm: WindowManager = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
    
    def draw(self, context: Context) -> None:
        layout: UILayout = self.layout
        
        try:
            from ..core.translation_manager import get_avatar_translation_manager
            manager = get_avatar_translation_manager()
            stats = manager.get_translation_stats()
            
            dict_box = layout.box()
            dict_box.label(text="Dictionary Translations", icon='BOOKMARKS')
            dict_stats = stats['dictionary_translations']
            for category, count in dict_stats.items():
                if count > 0:
                    dict_box.label(text=f"{category.title()}: {count}")
            
            cache_box = layout.box()
            cache_box.label(text="Translation Cache", icon='FILE_CACHE')
            cache_stats = stats['cache_stats']
            cache_box.label(text=f"Language pairs: {cache_stats['language_pairs']}")
            cache_box.label(text=f"Total cached: {cache_stats['total_entries']}")
            
            service_box = layout.box()
            service_box.label(text="Translation Services", icon='WORLD')
            service_box.label(text=f"Current mode: {stats['current_mode']}")
            service_box.label(text=f"Primary service: {stats['primary_service']}")
            
            available_services = stats['available_services']
            if available_services:
                service_box.label(text="Available services:")
                for service_id, service_name in available_services:
                    service_box.label(text=f"  • {service_name}")
            else:
                service_box.label(text="No services available", icon='ERROR')
                
        except Exception as e:
            layout.label(text=f"Error loading stats: {str(e)}", icon='ERROR')


class AvatarToolKit_PT_TranslationPanel(Panel):
    """Translation panel for Avatar Toolkit"""
    bl_label: str = t("Translation.label")
    bl_idname: str = "OBJECT_PT_avatar_toolkit_translation"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('translation')
    bl_options = set() if not should_open_by_default('TRANSLATION') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw the translation panel layout"""
        layout: UILayout = self.layout
        props = context.scene.avatar_toolkit
        
        # Translation Service Settings
        service_box: UILayout = layout.box()
        col: UILayout = service_box.column(align=True)
        row: UILayout = col.row()
        row.scale_y = 1.2
        row.label(text=t("Translation.service_settings"), icon='WORLD')
        col.separator()
        
        col.prop(props, "translation_service", text="")
        
        col.prop(props, "translation_mode", text="")
        
        row = col.row(align=True)
        row.prop(props, "translation_expand", 
                icon="TRIA_DOWN" if props.translation_expand else "TRIA_RIGHT", 
                icon_only=True, emboss=False)
        row.label(text=t("Translation.advanced_settings"))
        
        if props.translation_expand:
            config_col = service_box.column(align=True)
            
            # MyMemory settings (no configuration needed)
            if props.translation_service == 'mymemory':
                config_col.separator()
                config_col.label(text="MyMemory Configuration:", icon='CHECKMARK')
                success_col = config_col.column()
                success_col.alert = False
                success_col.label(text="✓ No API key required!", icon='CHECKMARK')
                success_col.label(text="✓ Completely free service")
                success_col.label(text="✓ 1000 translations per day")
                success_col.label(text="✓ Slowest Option due to no native batching")
                success_col.label(text="✓ Ready to use!")
            
            elif props.translation_service == 'libretranslate':
                config_col.separator()
                config_col.label(text="LibreTranslate Configuration:", icon='SETTINGS')
                
                # Check current server configuration (cached to avoid performance issues)
                try:
                    if 'libretranslate_url' not in _ui_cache['libretranslate_config']:
                        from ..core.addon_preferences import get_preference
                        _ui_cache['libretranslate_config']['libretranslate_url'] = get_preference("libretranslate_url", "https://libretranslate.com")
                    
                    server_url = _ui_cache['libretranslate_config']['libretranslate_url']
                    
                    info_col = config_col.column()
                    info_col.alert = False
                    info_col.label(text=f"Server: {server_url}", icon='URL')
                    
                    if "libretranslate.com" in server_url.lower():
                        warning_col = config_col.column()
                        warning_col.alert = True
                        warning_col.label(text="⚠ Default server requires payment", icon='ERROR')
                        warning_col.label(text="Configure your own LibreTranslate server")
                    else:
                        success_col = config_col.column()
                        success_col.alert = False
                        success_col.label(text="✓ Custom server configured", icon='CHECKMARK')
                        
                    config_row = config_col.row()
                    config_row.operator("avatar_toolkit.configure_libretranslate", text="Configure Server", icon='SETTINGS')
                except Exception as e:
                    config_col.label(text="LibreTranslate configuration error", icon='ERROR')
            
            elif props.translation_service == 'deepl':
                config_col.separator()
                config_col.label(text="DeepL Configuration:", icon='SETTINGS')
                
                # Check if API key is configured (cached to avoid performance issues)
                try:
                    if 'deepl_api_key' not in _ui_cache['deepl_config']:
                        from ..core.addon_preferences import get_preference
                        _ui_cache['deepl_config']['deepl_api_key'] = get_preference("deepl_api_key", "")
                    
                    deepl_api_key = _ui_cache['deepl_config']['deepl_api_key']
                    
                    if deepl_api_key and deepl_api_key.strip():
                        success_col = config_col.column()
                        success_col.alert = False
                        success_col.label(text="✓ API key configured", icon='CHECKMARK')
                        success_col.label(text="✓ High quality translations")
                        success_col.label(text="✓ 500,000 chars/month free")
                        success_col.label(text="✓ Ready to use!")
                        
                        reconfig_row = config_col.row()
                        reconfig_row.operator("avatar_toolkit.configure_deepl", text="Reconfigure API Key", icon='SETTINGS')
                    else:
                        warning_col = config_col.column()
                        warning_col.alert = True
                        warning_col.label(text="⚠ API key required!", icon='ERROR')
                        warning_col.label(text="Get free key at deepl.com/pro")
                        warning_col.label(text="500,000 characters/month free")
                        
                        config_row = config_col.row()
                        config_row.operator("avatar_toolkit.configure_deepl", text="Configure API Key", icon='PLUS')
                except Exception as e:
                    config_col.label(text="DeepL configuration error", icon='ERROR')
            
            
        
        # Language Settings
        lang_box: UILayout = layout.box()
        col = lang_box.column(align=True)
        row = col.row()
        row.scale_y = 1.2
        row.label(text=t("Translation.language_settings"), icon='SYNTAX_ON')
        col.separator()
        col.prop(props, "translation_source_language", text="From")
        col.prop(props, "translation_target_language", text="To")
        
        # Quick Actions
        action_box: UILayout = layout.box()
        col = action_box.column(align=True)
        row = col.row()
        row.scale_y = 1.2
        row.label(text=t("Translation.quick_actions"), icon='PLAY')
        col.separator()
        
        # Translate buttons
        row = col.row(align=True)
        op_bones = row.operator(AvatarToolkit_OT_TranslateNames.bl_idname, text="Bones", icon='BONE_DATA')
        op_bones.translation_type = 'bones'
        
        op_shapes = row.operator(AvatarToolkit_OT_TranslateNames.bl_idname, text="Shape Keys", icon='SHAPEKEY_DATA')
        op_shapes.translation_type = 'shapekeys'
        
        row = col.row(align=True)
        op_mats = row.operator(AvatarToolkit_OT_TranslateNames.bl_idname, text="Materials", icon='MATERIAL_DATA')
        op_mats.translation_type = 'materials'
        
        op_objs = row.operator(AvatarToolkit_OT_TranslateNames.bl_idname, text="Objects", icon='OBJECT_DATA')
        op_objs.translation_type = 'objects'
        
        col.separator()
        op_all = col.operator(AvatarToolkit_OT_TranslateNames.bl_idname, text="Translate All", icon='WORLD')
        op_all.translation_type = 'all'
        
        # Utility buttons
        util_box: UILayout = layout.box()
        col = util_box.column(align=True)
        row = col.row()
        row.scale_y = 1.2
        row.label(text=t("Translation.utilities"), icon='TOOL_SETTINGS')
        col.separator()
        
        row = col.row(align=True)
        row.operator(AvatarToolkit_OT_TestTranslationService.bl_idname, icon='PLAY')
        row.operator(AvatarToolkit_OT_TranslationStats.bl_idname, icon='INFO')
        
        col.operator(AvatarToolkit_OT_ClearTranslationCache.bl_idname, icon='TRASH')
        
        status_box = layout.box()
        status_col = status_box.column()
        
        try:
            status_cache_key = f"translation_status_{props.translation_service}_{props.translation_mode}"
            
            # Refresh cache periodically 
            frame = context.scene.frame_current
            cache_expired = (frame - _ui_cache['last_refresh_frame'] >= _ui_cache['cache_refresh_interval']) or status_cache_key not in _ui_cache['translation_status']
            
            if cache_expired:
                from ..core.translation_manager import get_available_translation_services, get_avatar_translation_manager
                
                manager = get_avatar_translation_manager()
                available_services = get_available_translation_services()
                
                _ui_cache['translation_status'][status_cache_key] = {
                    'available_services': available_services,
                    'manager': manager,
                    'cache_stats': None
                }
                _ui_cache['last_refresh_frame'] = frame
                
                try:
                    stats = manager.get_translation_stats()
                    _ui_cache['translation_status'][status_cache_key]['cache_stats'] = stats['cache_stats']
                except:
                    pass
            
            # Use cached data
            cached_data = _ui_cache['translation_status'].get(status_cache_key, {})
            available_services = cached_data.get('available_services', [])
            cache_stats = cached_data.get('cache_stats')
            
            if available_services:
                status_col.label(text="Translation services ready", icon='CHECKMARK')
                
                # Show current service status
                current_service = props.translation_service
                service_available = any(service_id == current_service for service_id, _ in available_services)
                
                if service_available:
                    service_name = next((name for sid, name in available_services if sid == current_service), current_service)
                    status_col.label(text=f"Active: {service_name}", icon='WORLD')
                    
                    # Show translation mode
                    mode_display = {
                        'hybrid': 'Dictionary + API',
                        'dictionary_only': 'Dictionary Only', 
                        'api_only': 'API Only'
                    }.get(props.translation_mode, props.translation_mode)
                    status_col.label(text=f"Mode: {mode_display}", icon='SETTINGS')
                    
                    # Show cache status
                    if cache_stats and cache_stats['total_entries'] > 0:
                        status_col.label(text=f"Cache: {cache_stats['total_entries']} translations", icon='FILE_CACHE')
                    
                    # Show batch translation capability
                    try:
                        if 'batch_info' not in _ui_cache:
                            from ..core.translation_manager import get_batch_translation_info
                            _ui_cache['batch_info'] = get_batch_translation_info()
                        
                        batch_info = _ui_cache['batch_info'].get(current_service, {})
                        if batch_info.get('supports_batch', False):
                            batch_type = batch_info.get('batch_type', 'individual')
                            if batch_type == 'native':
                                status_col.label(text="⚡ DeepL Native batch translation (up to 50x faster)", icon='LIGHT')
                            elif batch_type == 'concurrent':
                                if current_service == 'mymemory':
                                    status_col.label(text="⚡ Slowest Option, no native Batching", icon='LIGHT')
                                else:
                                    status_col.label(text="⚡ Slightly Faster then MyMemory processing (3x faster)", icon='LIGHT')
                    except:
                        pass
                        
                else:
                    warning_col = status_col.column()
                    warning_col.alert = True
                    warning_col.label(text=f"Service unavailable: {props.translation_service}", icon='ERROR')
                    
                    
            else:
                warning_col = status_col.column()
                warning_col.alert = True
                warning_col.label(text="No translation services available", icon='ERROR')
                
                if props.translation_service == 'mymemory':
                    warning_col.label(text="Internet connection required")
                
        except Exception as e:
            error_col = status_col.column()
            error_col.alert = True
            error_col.label(text="Translation system error", icon='ERROR')
            logger.error(f"Status display error: {e}")
            
        try:
            if hasattr(context.area, 'header_text') and context.area.header_text:
                progress_col = status_col.column()
                progress_col.alert = False
                progress_col.label(text=context.area.header_text, icon='TIME')
        except:
            pass


