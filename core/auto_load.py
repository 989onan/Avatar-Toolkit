import os
import bpy
import typing
import inspect
import pkgutil
import tomllib
import importlib
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Type, Tuple, Generator, TypeVar

__all__ = (
    "init",
    "register",
    "unregister",
)

T = TypeVar('T')
modules: Optional[List[Any]] = None
ordered_classes: Optional[List[Type]] = None

def init() -> None:
    """Initialize the auto-loader by discovering modules and classes"""
    global modules
    global ordered_classes

    from .logging_setup import configure_logging
    configure_logging(False)
    
    from .addon_preferences import get_preference
    log_level = get_preference("log_level", "WARNING")
    configure_logging(get_preference("enable_logging", False), log_level)

    print("Auto-load init starting")
    
    package_name = __package__.rsplit('.', 1)[0]
    directory = Path(__file__).parent.parent
    modules = get_all_submodules(directory, package_name)
    ordered_classes = get_ordered_classes_to_register(modules)
    print(f"Found modules: {modules}")
    print(f"Found classes: {ordered_classes}")

def register() -> None:
    """Register all discovered classes and modules"""
    global modules, ordered_classes
    
    print("Registering classes")
    
    if not ordered_classes:
        print("Warning: No classes to register")
        ordered_classes = []
    
    for cls in ordered_classes:
        print(f"Registering: {cls}")
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            continue

    if not modules:
        print("Warning: No modules to register")
        modules = []
        
    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()

def unregister() -> None:
    """Unregister all classes and modules in reverse order"""
    for cls in reversed(ordered_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            continue

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()

def get_all_submodules(directory: Path, package_name: str) -> List[Any]:
    """Discover and import all submodules in the given directory"""
    return list(iter_submodules(directory, package_name))

def iter_submodules(directory: Path, package_name: str) -> Generator[Any, None, None]:
    """Iterate through submodules in a package"""
    for name in sorted(iter_submodule_names(directory)):
        try:
            yield importlib.import_module("." + name, package_name)
            print(f"Successfully imported {name} from {package_name}")
        except ImportError as e:
            print(f"Error importing {name} from {package_name}: {e}")

def iter_submodule_names(path: Path, root: str = "") -> Generator[str, None, None]:
    """Iterate through module names in a directory"""
    print(f"Scanning path: {path}")
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name

def get_ordered_classes_to_register(modules: List[Any]) -> List[Type]:
    """Get a topologically sorted list of classes to register"""
    return toposort(get_register_deps_dict(modules))

def get_register_deps_dict(modules: List[Any]) -> Dict[Type, Set[Type]]:
    """Get dependencies dictionary for class registration"""
    my_classes = set(iter_classes_to_register(modules))
    my_classes_by_idname = {cls.bl_idname: cls for cls in my_classes if hasattr(cls, "bl_idname")}
    
    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set()
        deps_dict[cls].update(iter_deps_from_annotations(cls, my_classes))
        deps_dict[cls].update(iter_deps_from_parent_id(cls, my_classes_by_idname))
    
    return deps_dict

def iter_deps_from_annotations(cls: Type, my_classes: Set[Type]) -> Generator[Type, None, None]:
    """Iterate through dependencies from class annotations"""
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None and dependency in my_classes:
            yield dependency

def iter_deps_from_parent_id(cls: Type, my_classes_by_idname: Dict[str, Type]) -> Generator[Type, None, None]:
    """Iterate through dependencies from panel parent IDs"""
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls

def get_dependency_from_annotation(value: Any) -> Optional[Type]:
    """Get dependency type from a type annotation"""
    if isinstance(value, bpy.props._PropertyDeferred):
        return value.keywords.get("type")
    return None

def iter_classes_to_register(modules: List[Any]) -> Generator[Type, None, None]:
    """Iterate through classes that need to be registered"""
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if not getattr(cls, "_is_registered", False):
                yield cls

def get_classes_in_modules(modules: List[Any]) -> Set[Type]:
    """Get all classes defined in the modules"""
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes

def iter_classes_in_module(module: Any) -> Generator[Type, None, None]:
    """Iterate through classes defined in a module"""
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value

def get_register_base_types() -> Set[Type]:
    """Get set of base types that need registration"""
    return set(getattr(bpy.types, name) for name in [
        "Panel", "Operator", "PropertyGroup",
        "AddonPreferences", "Header", "Menu",
        "Node", "NodeSocket", "NodeTree",
        "UIList", "RenderEngine",
        "Gizmo", "GizmoGroup",
    ])

def toposort(deps_dict: Dict[Type, Set[Type]]) -> List[Type]:
    """Topologically sort classes based on their dependencies"""
    sorted_list = []
    sorted_values = set()
    
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        
        deps_dict = {value: deps_dict[value] - sorted_values for value in unsorted}
    
    return sorted_list
