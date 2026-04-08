# -*- coding: utf-8 -*-
# Copyright 2014 MMD Tools authors
# This file was originally part of the MMD Tools add-on for Blender
# You can find MMD Tools here: https://github.com/MMD-Blender/blender_mmd_tools
# Neoneko has modified this file to work with Avatar Toolkit and may of made changes or improvements.
# MMD Tools is licensed under the terms of the GNU General Public License version 3 (GPLv3) same as Avatar Toolkit.

import bpy


def patch_library_overridable(property: "bpy.props._PropertyDeferred") -> "bpy.props._PropertyDeferred":
    """Apply recursively for each mmd_tools property class annotations.
    Args:
        property: The property to be patched.

    Returns:
        The patched property.
    """
    property.keywords.setdefault("override", set()).add("LIBRARY_OVERRIDABLE")

    if property.function.__name__ not in {"PointerProperty", "CollectionProperty"}:
        return property

    property_type = property.keywords["type"]
    # The __annotations__ cannot be inherited. Manually search for base classes.
    for inherited_type in (property_type, *property_type.__bases__):
        if not inherited_type.__module__.startswith("mmd_tools.properties"):
            continue
        for annotation in inherited_type.__annotations__.values():
            if not isinstance(annotation, bpy.props._PropertyDeferred):
                continue
            patch_library_overridable(annotation)

    return property
