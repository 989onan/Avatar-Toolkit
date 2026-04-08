# -*- coding: utf-8 -*-
# Copyright 2014 MMD Tools authors
# This file was originally part of the MMD Tools add-on for Blender
# You can find MMD Tools here: https://github.com/MMD-Blender/blender_mmd_tools
# Neoneko has modified this file to work with Avatar Toolkit and may of made changes or improvements.
# MMD Tools is licensed under the terms of the GNU General Public License version 3 (GPLv3) same as Avatar Toolkit.

import bpy
from typing import Optional, Set, Dict, Any, List, Tuple, Union

from ..bpyutils import FnContext
from ..core.bone import FnBone, MigrationFnBone
from ..core.model import FnModel, Model
from ....core.logging_setup import logger


class MorphSliderSetup(bpy.types.Operator):
    bl_idname = "mmd_tools.morph_slider_setup"
    bl_label = "Morph Slider Setup"
    bl_description = "Translate MMD morphs of selected object into format usable by Blender"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    type: bpy.props.EnumProperty(
        name="Type",
        description="Select type",
        items=[
            ("CREATE", "Create", "Create placeholder object for morph sliders", "SHAPEKEY_DATA", 0),
            ("BIND", "Bind", "Bind morph sliders", "DRIVER", 1),
            ("UNBIND", "Unbind", "Unbind morph sliders", "X", 2),
        ],
        default="CREATE",
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None

        logger.debug(f"Executing MorphSliderSetup with type: {self.type}")
        with FnContext.temp_override_active_layer_collection(context, root_object):
            rig = Model(root_object)
            if self.type == "BIND":
                logger.info(f"Binding morph sliders for {root_object.name}")
                rig.morph_slider.bind()
            elif self.type == "UNBIND":
                logger.info(f"Unbinding morph sliders for {root_object.name}")
                rig.morph_slider.unbind()
            else:
                logger.info(f"Creating morph sliders for {root_object.name}")
                rig.morph_slider.create()
            FnContext.set_active_object(context, active_object)

        return {"FINISHED"}


class CleanRiggingObjects(bpy.types.Operator):
    bl_idname = "mmd_tools.clean_rig"
    bl_label = "Clean Rig"
    bl_description = "Delete temporary physics objects of selected object and revert physics to default MMD state"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        root_object = FnModel.find_root_object(context.active_object)
        assert root_object is not None

        logger.info(f"Cleaning rig for {root_object.name}")
        rig = Model(root_object)
        rig.clean()
        FnContext.set_active_object(context, root_object)
        return {"FINISHED"}


class BuildRig(bpy.types.Operator):
    bl_idname = "mmd_tools.build_rig"
    bl_label = "Build Rig"
    bl_description = "Translate physics of selected object into format usable by Blender"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    non_collision_distance_scale: bpy.props.FloatProperty(
        name="Non-Collision Distance Scale",
        description="The distance scale for creating extra non-collision constraints while building physics",
        min=0,
        soft_max=10,
        default=1.5,
    )

    collision_margin: bpy.props.FloatProperty(
        name="Collision Margin",
        description="The collision margin between rigid bodies. If 0, the default value for each shape is adopted.",
        unit="LENGTH",
        min=0,
        soft_max=10,
        default=1e-06,
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        root_object = FnModel.find_root_object(context.active_object)

        logger.info(f"Building rig for {root_object.name} with non_collision_distance_scale={self.non_collision_distance_scale}, collision_margin={self.collision_margin}")
        with FnContext.temp_override_active_layer_collection(context, root_object):
            rig = Model(root_object)
            rig.build(self.non_collision_distance_scale, self.collision_margin)
            FnContext.set_active_object(context, root_object)

        return {"FINISHED"}


class CleanAdditionalTransformConstraints(bpy.types.Operator):
    bl_idname = "mmd_tools.clean_additional_transform"
    bl_label = "Clean Additional Transform"
    bl_description = "Delete shadow bones of selected object and revert bones to default MMD state"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None
        
        logger.info(f"Cleaning additional transform constraints for {root_object.name}")
        armature_object = FnModel.find_armature_object(root_object)
        FnBone.clean_additional_transformation(armature_object)
        FnContext.set_active_object(context, active_object)
        return {"FINISHED"}


class ApplyAdditionalTransformConstraints(bpy.types.Operator):
    bl_idname = "mmd_tools.apply_additional_transform"
    bl_label = "Apply Additional Transform"
    bl_description = "Translate appended bones of selected object for Blender"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None

        logger.info(f"Applying additional transform constraints for {root_object.name}")
        armature_object = FnModel.find_armature_object(root_object)
        assert armature_object is not None

        MigrationFnBone.fix_mmd_ik_limit_override(armature_object)
        FnBone.apply_additional_transformation(armature_object)
        FnContext.set_active_object(context, active_object)
        return {"FINISHED"}


class SetupBoneFixedAxes(bpy.types.Operator):
    bl_idname = "mmd_tools.bone_fixed_axis_setup"
    bl_label = "Setup Bone Fixed Axis"
    bl_description = "Setup fixed axis of selected bones"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    type: bpy.props.EnumProperty(
        name="Type",
        description="Select type",
        items=[
            ("DISABLE", "Disable", "Disable MMD fixed axis of selected bones", 0),
            ("LOAD", "Load", "Load/Enable MMD fixed axis of selected bones from their Y-axis or the only rotatable axis", 1),
            ("APPLY", "Apply", "Align bone axes to MMD fixed axis of each bone", 2),
        ],
        default="LOAD",
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        armature_object = context.active_object
        if not armature_object or armature_object.type != "ARMATURE":
            self.report({"ERROR"}, "Active object is not an armature object")
            logger.error("Setup Bone Fixed Axis failed: Active object is not an armature object")
            return {"CANCELLED"}

        logger.info(f"Setting up bone fixed axes with type: {self.type}")
        if self.type == "APPLY":
            FnBone.apply_bone_fixed_axis(armature_object)
            FnBone.apply_additional_transformation(armature_object)
        else:
            FnBone.load_bone_fixed_axis(armature_object, enable=(self.type == "LOAD"))
        return {"FINISHED"}


class SetupBoneLocalAxes(bpy.types.Operator):
    bl_idname = "mmd_tools.bone_local_axes_setup"
    bl_label = "Setup Bone Local Axes"
    bl_description = "Setup local axes of each bone"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    type: bpy.props.EnumProperty(
        name="Type",
        description="Select type",
        items=[
            ("DISABLE", "Disable", "Disable MMD local axes of selected bones", 0),
            ("LOAD", "Load", "Load/Enable MMD local axes of selected bones from their bone axes", 1),
            ("APPLY", "Apply", "Align bone axes to MMD local axes of each bone", 2),
        ],
        default="LOAD",
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        armature_object = context.active_object
        if not armature_object or armature_object.type != "ARMATURE":
            self.report({"ERROR"}, "Active object is not an armature object")
            logger.error("Setup Bone Local Axes failed: Active object is not an armature object")
            return {"CANCELLED"}

        logger.info(f"Setting up bone local axes with type: {self.type}")
        if self.type == "APPLY":
            FnBone.apply_bone_local_axes(armature_object)
            FnBone.apply_additional_transformation(armature_object)
        else:
            FnBone.load_bone_local_axes(armature_object, enable=(self.type == "LOAD"))
        return {"FINISHED"}


class AddMissingVertexGroupsFromBones(bpy.types.Operator):
    bl_idname = "mmd_tools.add_missing_vertex_groups_from_bones"
    bl_label = "Add Missing Vertex Groups from Bones"
    bl_description = "Add the missing vertex groups to the selected mesh"
    bl_options = {"REGISTER", "UNDO"}

    search_in_all_meshes: bpy.props.BoolProperty(
        name="Search in all meshes",
        description="Search for vertex groups in all meshes",
        default=False,
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return FnModel.find_root_object(context.active_object) is not None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object: bpy.types.Object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None

        logger.info(f"Adding missing vertex groups from bones for {root_object.name}, search_in_all_meshes={self.search_in_all_meshes}")
        bone_order_mesh_object = FnModel.find_bone_order_mesh_object(root_object)
        if bone_order_mesh_object is None:
            logger.error("Failed to find bone order mesh object")
            return {"CANCELLED"}

        FnModel.add_missing_vertex_groups_from_bones(root_object, bone_order_mesh_object, self.search_in_all_meshes)

        return {"FINISHED"}


class CreateMMDModelRoot(bpy.types.Operator):
    bl_idname = "mmd_tools.create_mmd_model_root_object"
    bl_label = "Create a MMD Model Root Object"
    bl_description = "Create a MMD model root object with a basic armature"
    bl_options = {"REGISTER", "UNDO"}

    name_j: bpy.props.StringProperty(
        name="Name",
        description="The name of the MMD model",
        default="New MMD Model",
    )
    name_e: bpy.props.StringProperty(
        name="Name(Eng)",
        description="The english name of the MMD model",
        default="New MMD Model",
    )
    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale",
        default=0.08,
    )

    def execute(self, context: bpy.types.Context) -> Set[str]:
        logger.info(f"Creating MMD model root object with name_j={self.name_j}, name_e={self.name_e}, scale={self.scale}")
        rig = Model.create(self.name_j, self.name_e, self.scale, add_root_bone=True)
        rig.initialDisplayFrames()
        return {"FINISHED"}

    def invoke(self, context: bpy.types.Context, event: Any) -> Set[str]:
        vm = context.window_manager
        return vm.invoke_props_dialog(self)


class ConvertToMMDModel(bpy.types.Operator):
    bl_idname = "mmd_tools.convert_to_mmd_model"
    bl_label = "Convert to a MMD Model"
    bl_description = "Convert active armature with its meshes to a MMD model (experimental)"
    bl_options = {"REGISTER", "UNDO"}

    ambient_color_source: bpy.props.EnumProperty(
        name="Ambient Color Source",
        description="Select ambient color source",
        items=[
            ("DIFFUSE", "Diffuse", "Diffuse color", 0),
            ("MIRROR", "Mirror", 'Mirror color (if property "mirror_color" is available)', 1),
        ],
        default="DIFFUSE",
    )
    edge_threshold: bpy.props.FloatProperty(
        name="Edge Threshold",
        description="MMD toon edge will not be enabled if freestyle line color alpha less than this value",
        min=0,
        max=1.001,
        precision=3,
        step=0.1,
        default=0.1,
    )
    edge_alpha_min: bpy.props.FloatProperty(
        name="Minimum Edge Alpha",
        description="Minimum alpha of MMD toon edge color",
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=0.5,
    )
    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scaling factor for converting the model",
        default=0.08,
    )
    convert_material_nodes: bpy.props.BoolProperty(
        name="Convert Material Nodes",
        default=True,
    )
    middle_joint_bones_lock: bpy.props.BoolProperty(
        name="Middle Joint Bones Lock",
        description="Lock specific bones for backward compatibility.",
        default=False,
    )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        obj = context.active_object
        return obj and obj.type == "ARMATURE" and obj.mode != "EDIT"

    def invoke(self, context: bpy.types.Context, event: Any) -> Set[str]:
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context) -> Set[str]:
        logger.info(f"Converting to MMD model with scale={self.scale}, convert_material_nodes={self.convert_material_nodes}")
        # TODO convert some basic MMD properties
        armature_object = context.active_object
        scale = self.scale
        model_name = "New MMD Model"

        root_object = FnModel.find_root_object(armature_object)
        if root_object is None or root_object != armature_object.parent:
            logger.debug("Creating new MMD model")
            Model.create(model_name, model_name, scale, armature_object=armature_object)

        self.__attach_meshes_to(armature_object, FnContext.get_scene_objects(context))
        self.__configure_rig(context, Model(armature_object.parent))
        return {"FINISHED"}

    def __attach_meshes_to(self, armature_object: bpy.types.Object, objects: bpy.types.SceneObjects) -> None:
        def __is_child_of_armature(mesh: bpy.types.Object) -> bool:
            if mesh.parent is None:
                return False
            return mesh.parent == armature_object or __is_child_of_armature(mesh.parent)

        def __is_using_armature(mesh: bpy.types.Object) -> bool:
            for m in mesh.modifiers:
                if m.type == "ARMATURE" and m.object == armature_object:
                    return True
            return False

        def __get_root(mesh: bpy.types.Object) -> bpy.types.Object:
            if mesh.parent is None:
                return mesh
            return __get_root(mesh.parent)

        attached_count = 0
        for x in objects:
            if __is_using_armature(x) and not __is_child_of_armature(x):
                x_root = __get_root(x)
                m = x_root.matrix_world
                x_root.parent_type = "OBJECT"
                x_root.parent = armature_object
                x_root.matrix_world = m
                attached_count += 1
        
        logger.debug(f"Attached {attached_count} meshes to armature")

    def __configure_rig(self, context: bpy.types.Context, mmd_model: Model) -> None:
        root_object = mmd_model.rootObject()
        armature_object = mmd_model.armature()
        mesh_objects = tuple(mmd_model.meshes())

        logger.info(f"Configuring rig for {root_object.name} with {len(mesh_objects)} meshes")
        mmd_model.loadMorphs()

        if self.middle_joint_bones_lock:
            vertex_groups = {g.name for mesh in mesh_objects for g in mesh.vertex_groups}
            locked_bones = 0
            for pose_bone in armature_object.pose.bones:
                if not pose_bone.parent:
                    continue
                if not pose_bone.bone.use_connect and pose_bone.name not in vertex_groups:
                    continue
                pose_bone.lock_location = (True, True, True)
                locked_bones += 1
            logger.debug(f"Locked {locked_bones} middle joint bones")

        from ..core.material import FnMaterial

        FnMaterial.set_nodes_are_readonly(not self.convert_material_nodes)
        try:
            converted_materials = 0
            for m in (x for mesh in mesh_objects for x in mesh.data.materials if x):
                FnMaterial.convert_to_mmd_material(m, context)
                mmd_material = m.mmd_material
                if self.ambient_color_source == "MIRROR" and hasattr(m, "mirror_color"):
                    mmd_material.ambient_color = m.mirror_color
                else:
                    mmd_material.ambient_color = [0.5 * c for c in mmd_material.diffuse_color]

                if hasattr(m, "line_color"):  # freestyle line color
                    line_color = list(m.line_color)
                    mmd_material.enabled_toon_edge = line_color[3] >= self.edge_threshold
                    mmd_material.edge_color = line_color[:3] + [max(line_color[3], self.edge_alpha_min)]
                converted_materials += 1
            logger.debug(f"Converted {converted_materials} materials")
        finally:
            FnMaterial.set_nodes_are_readonly(False)
        from .display_item import DisplayItemQuickSetup

        FnBone.sync_display_item_frames_from_bone_collections(armature_object)
        mmd_model.initialDisplayFrames(reset=False)  # ensure default frames
        DisplayItemQuickSetup.load_facial_items(root_object.mmd_root)
        root_object.mmd_root.active_display_item_frame = 0


class ResetObjectVisibility(bpy.types.Operator):
    bl_idname = "mmd_tools.reset_object_visibility"
    bl_label = "Reset Object Visivility"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        active_object: bpy.types.Object = context.active_object
        return FnModel.find_root_object(active_object) is not None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object: bpy.types.Object = context.active_object
        mmd_root_object = FnModel.find_root_object(active_object)
        assert mmd_root_object is not None
        mmd_root = mmd_root_object.mmd_root

        logger.info(f"Resetting object visibility for {mmd_root_object.name}")
        mmd_root_object.hide_set(False)

        rigid_group_object = FnModel.find_rigid_group_object(mmd_root_object)
        if rigid_group_object:
            rigid_group_object.hide_set(True)

        joint_group_object = FnModel.find_joint_group_object(mmd_root_object)
        if joint_group_object:
            joint_group_object.hide_set(True)

        temporary_group_object = FnModel.find_temporary_group_object(mmd_root_object)
        if temporary_group_object:
            temporary_group_object.hide_set(True)

        mmd_root.show_meshes = True
        mmd_root.show_armature = True
        mmd_root.show_temporary_objects = False
        mmd_root.show_rigid_bodies = False
        mmd_root.show_names_of_rigid_bodies = False
        mmd_root.show_joints = False
        mmd_root.show_names_of_joints = False

        return {"FINISHED"}


class AssembleAll(bpy.types.Operator):
    bl_idname = "mmd_tools.assemble_all"
    bl_label = "Assemble All"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None

        logger.info(f"Assembling all components for {root_object.name}")
        with FnContext.temp_override_active_layer_collection(context, root_object) as context:
            rig = Model(root_object)
            MigrationFnBone.fix_mmd_ik_limit_override(rig.armature())
            FnBone.apply_additional_transformation(rig.armature())
            rig.build()
            rig.morph_slider.bind()

            logger.debug("Binding SDEF weights")
            with context.temp_override(selected_objects=[active_object]):
                bpy.ops.mmd_tools.sdef_bind()
            root_object.mmd_root.use_property_driver = True

            FnContext.set_active_object(context, active_object)

        return {"FINISHED"}


class DisassembleAll(bpy.types.Operator):
    bl_idname = "mmd_tools.disassemble_all"
    bl_label = "Disassemble All"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context: bpy.types.Context) -> Set[str]:
        active_object = context.active_object
        root_object = FnModel.find_root_object(active_object)
        assert root_object is not None

        logger.info(f"Disassembling all components for {root_object.name}")
        with FnContext.temp_override_active_layer_collection(context, root_object) as context:
            root_object.mmd_root.use_property_driver = False
            logger.debug("Unbinding SDEF weights")
            with context.temp_override(selected_objects=[active_object]):
                bpy.ops.mmd_tools.sdef_unbind()

            rig = Model(root_object)
            rig.morph_slider.unbind()
            rig.clean()
            FnBone.clean_additional_transformation(rig.armature())

            FnContext.set_active_object(context, active_object)

        return {"FINISHED"}
