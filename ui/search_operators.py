"""Base classes for reusable search operators"""

from typing import Set, Callable, Optional
from bpy.types import Operator, Context, Event, WindowManager


class SearchOperatorBase(Operator):
    """
    Reusable base class for search/selection operators.
    
    This is an abstract base class - do not use directly.
    Subclass and implement your specific search operator instead.
    
    Subclasses should:
    1. Define bl_idname, bl_label, bl_description
    2. Define search_property_name (name of EnumProperty)
    3. Define target_property_name (name of property to set on scene)
    4. Define get_items_func (function to get enum items)
    5. Optionally override get_enum_property() to customize the enum

    This was created because search in ATK was all over the place and inconsistent, this way we have a standard way to do it.
    """
    
    # Mark this as abstract by setting a non-Blender-compatible idname
    bl_idname = "wm.search_operator_base"  # Will be overridden in subclasses
    bl_label = "Search and Select"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    # These should be overridden in subclasses
    search_property_name: str = "search_enum"
    target_property_name: str = "target_property"
    
    @staticmethod
    def get_items_func(scene, context) -> list:
        """Override this to provide enum items. Return list of (id, name, description) tuples"""
        return []
    
    def get_enum_property(self) -> None:
        """
        Create the enum property dynamically. Override if you need custom behavior.
        This is called during class creation.
        """
        import bpy
        setattr(
            type(self),
            self.search_property_name,
            bpy.props.EnumProperty(
                name="Search",
                description="Select item",
                items=self.get_items_func
            )
        )
    
    def execute(self, context: Context) -> Set[str]:
        """Set the target property from the search selection"""
        search_value = getattr(self, self.search_property_name, None)
        if search_value:
            setattr(context.scene.avatar_toolkit, self.target_property_name, search_value)
        return {'FINISHED'}
    
    def invoke(self, context: Context, event: Event) -> Set[str]:
        """Open search popup"""
        wm: WindowManager = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}


class ArmatureSearchOperator(SearchOperatorBase):
    """Specialized search operator for selecting armatures"""
    
    bl_label = "Search Armatures"
    search_property_name: str = "search_armature_enum"
    
    @staticmethod
    def get_items_func(scene, context) -> list:
        """Get list of all armature objects in scene"""
        import bpy
        return [
            (obj.name, obj.name, "")
            for obj in bpy.data.objects
            if obj.type == 'ARMATURE'
        ]


class MeshSearchOperator(SearchOperatorBase):
    """Specialized search operator for selecting meshes"""
    
    bl_label = "Search Meshes"
    search_property_name: str = "search_mesh_enum"
    
    @staticmethod
    def get_items_func(scene, context) -> list:
        """Get list of all mesh objects without armature modifiers"""
        import bpy
        return [
            (obj.name, obj.name, "")
            for obj in bpy.data.objects
            if obj.type == 'MESH'
            and not any(mod.type == 'ARMATURE' for mod in obj.modifiers)
        ]


class BoneSearchOperator(SearchOperatorBase):
    """Specialized search operator for selecting bones from active armature"""
    
    bl_label = "Search Bones"
    search_property_name: str = "search_bone_enum"
    
    @staticmethod
    def get_items_func(scene, context) -> list:
        """Get list of all bones from active armature"""
        from ..core.common import get_active_armature
        
        armature = get_active_armature(context)
        if not armature:
            return []
        
        return [
            (bone.name, bone.name, "")
            for bone in armature.data.bones
        ]
