import bpy
from typing import Set
from bpy.types import Panel, Context, UILayout, Operator, Event, WindowManager
from .main_panel import AvatarToolKit_PT_AvatarToolkitPanel, CATEGORY_NAME
from .ui_utils import UIStyle, draw_section_header, wrap_text_label
from .panel_layout import get_panel_order, should_open_by_default
from ..core.translations import t
from ..core.common import get_active_armature, get_all_meshes
from ..functions.eye_tracking import (
    CreateEyesAV3Button,
    CreateEyesSDK2Button,
    StartTestingButton,
    StopTestingButton,
    ResetRotationButton,
    AdjustEyesButton,
    TestBlinking,
    TestLowerlid,
    ResetBlinkTest,
    ResetEyeTrackingButton,
    RotateEyeBonesForAv3Button
)

class AvatarToolKit_PT_EyeTrackingPanel(Panel):
    """Panel containing eye tracking setup and testing tools"""
    bl_label: str = t("EyeTracking.label")
    bl_idname: str = "VIEW3D_PT_avatar_toolkit_eye_tracking"
    bl_space_type: str = 'VIEW_3D'
    bl_region_type: str = 'UI'
    bl_category: str = CATEGORY_NAME
    bl_parent_id: str = AvatarToolKit_PT_AvatarToolkitPanel.bl_idname
    bl_order: int = get_panel_order('eye_tracking')
    bl_options: Set[str] = set() if not should_open_by_default('EYE_TRACKING') else {'DEFAULT_CLOSED'}

    def draw(self, context: Context) -> None:
        """Draw the eye tracking panel interface"""
        layout: UILayout = self.layout
        toolkit = context.scene.avatar_toolkit

        # SDK Version Selection
        col = draw_section_header(layout, t("EyeTracking.sdk_version"), icon='PRESET')
        row: UILayout = col.row(align=True)
        row.prop(toolkit, "eye_tracking_type", expand=True)

        if toolkit.eye_tracking_type == 'SDK2':
            # SDK2 Warning
            warning_box: UILayout = layout.box()
            col: UILayout = warning_box.column(align=True)
            col.alert = True
            col.label(text=t("EyeTracking.sdk2_warning"), icon='ERROR')
            col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
            
            warning_text = "\n".join([
                t("EyeTracking.sdk2_warning_detail1"),
                t("EyeTracking.sdk2_warning_detail2"),
                t("EyeTracking.sdk2_warning_detail3"),
                t("EyeTracking.sdk2_warning_detail4")
            ])
            wrap_text_label(col, warning_text, max_length=45)
            
            # Mode Selection
            col = draw_section_header(layout, t("EyeTracking.setup"), icon='TOOL_SETTINGS')
            col.prop(toolkit, "eye_mode", expand=True)

            if toolkit.eye_mode == 'CREATION':
                self.draw_creation_mode(context, layout)
            else:
                self.draw_testing_mode(context, layout)
        else:
            # AV3 bone setup only
            self.draw_av3_setup(context, layout)

    def draw_av3_setup(self, context: Context, layout: UILayout) -> None:
        """Draw the AV3 eye tracking setup interface"""
        toolkit = context.scene.avatar_toolkit

        # Bone Setup
        col = draw_section_header(layout, t("EyeTracking.bone_setup"), icon='BONE_DATA')


        armature = get_active_armature(context)
        if armature:
            col.prop_search(toolkit, "head", armature.data, "bones", text=t("EyeTracking.head_bone"))
            col.prop_search(toolkit, "eye_left", armature.data, "bones", text=t("EyeTracking.eye_left"))
            col.prop_search(toolkit, "eye_right", armature.data, "bones", text=t("EyeTracking.eye_right"))
        else:
            col.label(text=t("EyeTracking.no_armature"), icon='ERROR')

        row: UILayout = layout.row(align=True)
        row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
        row.operator(CreateEyesAV3Button.bl_idname, icon='PLAY')

    def draw_creation_mode(self, context: Context, layout: UILayout) -> None:
        """Draw the eye tracking creation mode interface"""
        toolkit = context.scene.avatar_toolkit

        # Bone Setup
        col = draw_section_header(layout, t("EyeTracking.bone_setup"), icon='BONE_DATA')
        armature = get_active_armature(context)
        if armature:
            col.prop_search(toolkit, "head", armature.data, "bones", text=t("EyeTracking.head_bone"))
            col.prop_search(toolkit, "eye_left", armature.data, "bones", text=t("EyeTracking.eye_left"))
            col.prop_search(toolkit, "eye_right", armature.data, "bones", text=t("EyeTracking.eye_right"))
        else:
            col.label(text=t("EyeTracking.no_armature"), icon='ERROR')

        # Mesh Setup
        col = draw_section_header(layout, t("EyeTracking.mesh_setup"), icon='MESH_DATA')
        col.prop_search(toolkit, "mesh_name_eye", bpy.data, "objects", text="")

        # Shape Key Setup
        col = draw_section_header(layout, t("EyeTracking.shapekey_setup"), icon='SHAPEKEY_DATA')
        mesh = bpy.data.objects.get(toolkit.mesh_name_eye)
        if mesh and mesh.data.shape_keys:
            col.prop_search(toolkit, "wink_left", mesh.data.shape_keys, "key_blocks", text=t("EyeTracking.wink_left"))
            col.prop_search(toolkit, "wink_right", mesh.data.shape_keys, "key_blocks", text=t("EyeTracking.wink_right"))
            col.prop_search(toolkit, "lowerlid_left", mesh.data.shape_keys, "key_blocks", text=t("EyeTracking.lowerlid_left"))
            col.prop_search(toolkit, "lowerlid_right", mesh.data.shape_keys, "key_blocks", text=t("EyeTracking.lowerlid_right"))
        else:
            col.label(text=t("EyeTracking.no_shapekeys"), icon='ERROR')

        # Options
        col = draw_section_header(layout, t("EyeTracking.options"), icon='SETTINGS')
        col.prop(toolkit, "disable_eye_blinking")
        col.prop(toolkit, "disable_eye_movement")
        if not toolkit.disable_eye_movement:
            col.prop(toolkit, "eye_distance")

        row: UILayout = layout.row(align=True)
        row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
        row.operator(CreateEyesSDK2Button.bl_idname, icon='PLAY')

    def draw_testing_mode(self, context: Context, layout: UILayout) -> None:
        """Draw the eye tracking testing mode interface"""
        toolkit = context.scene.avatar_toolkit

        if context.mode != 'POSE':
            # Testing Start
            col = draw_section_header(layout, t("EyeTracking.testing"), icon='PLAY')
            row: UILayout = col.row(align=True)
            row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
            row.operator(StartTestingButton.bl_idname, icon='PLAY')
        else:
            # Eye Rotation
            col = draw_section_header(layout, t("EyeTracking.rotation_controls"), icon='DRIVER_ROTATIONAL_DIFFERENCE')
            col.prop(toolkit, "eye_rotation_x", text=t("EyeTracking.rotation.x"))
            col.prop(toolkit, "eye_rotation_y", text=t("EyeTracking.rotation.y"))
            col.operator(ResetRotationButton.bl_idname, icon='LOOP_BACK')

            # Eye Adjustment
            col = draw_section_header(layout, t("EyeTracking.adjustments"), icon='MODIFIER')
            col.prop(toolkit, "eye_distance")
            col.operator(AdjustEyesButton.bl_idname, icon='CON_TRACKTO')

            # Blinking Test
            col = draw_section_header(layout, t("EyeTracking.blink_testing"), icon='HIDE_OFF')
            row: UILayout = col.row(align=True)
            row.prop(toolkit, "eye_blink_shape")
            row.operator(TestBlinking.bl_idname, icon='RESTRICT_VIEW_OFF')
            row: UILayout = col.row(align=True)
            row.prop(toolkit, "eye_lowerlid_shape")
            row.operator(TestLowerlid.bl_idname, icon='RESTRICT_VIEW_OFF')
            col.operator(ResetBlinkTest.bl_idname, icon='LOOP_BACK')

            # Stop Testing Button
            row: UILayout = layout.row(align=True)
            row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
            row.operator(StopTestingButton.bl_idname, icon='PAUSE')

        # Reset Button
        row: UILayout = layout.row(align=True)
        row.operator(ResetEyeTrackingButton.bl_idname, icon='FILE_REFRESH')
