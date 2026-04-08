"""UI utilities and styling helpers for consistent Avatar Toolkit panel design"""

from typing import Callable, Optional
from bpy.types import UILayout, Context, Operator


class UIStyle:
    """Centralized UI styling constants for consistent appearance"""
    
    SECTION_SEPARATOR_FACTOR: float = 0.5
    SUBSECTION_SEPARATOR_FACTOR: float = 0.3
    PRIMARY_BUTTON_SCALE: float = 1.5
    STANDARD_BUTTON_SCALE: float = 1.0
    COMPACT_BUTTON_SCALE: float = 0.9
    DEFAULT_PADDING: float = 1.0
    COMPACT_PADDING: float = 0.5
    
    CATEGORY_ICONS = {
        'optimization': 'MOD_SMOOTH',
        'tools': 'TOOL_SETTINGS',
        'custom': 'TOOL_OPTIONS',
        'eye_tracking': 'OBJECT_CAMERA',
        'settings': 'PREFERENCES',
        'import_export': 'EXPORT',
        'pose': 'POSE_HLT',
        'materials': 'MATERIAL',
        'mesh': 'MESH_DATA',
        'bones': 'BONE_DATA',
        'vfx': 'MOD_DISPLACE'
    }


def draw_section_header(layout: UILayout, title: str, icon: str = 'NONE', separator: bool = True) -> UILayout:
    """Draw a consistent section header with optional icon and separator"""
    header_box = layout.box()
    col = header_box.column(align=True)
    row = col.row()
    row.scale_y = 1.2
    row.label(text=title, icon=icon)
    
    if separator:
        col.separator(factor=UIStyle.SECTION_SEPARATOR_FACTOR)
    
    return col


def draw_subsection(layout: UILayout, title: str, icon: str = 'NONE') -> UILayout:
    """Draw a subsection with reduced visual weight (no box)"""
    col = layout.column(align=True)
    row = col.row()
    row.label(text=title, icon=icon)
    col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
    return col


def draw_info_text(layout: UILayout, text: str, icon: str = 'INFO') -> None:
    """Draw informational text that can wrap (replaces multiple labels)"""
    col = layout.column()
    col.alert = False
    # Split long text for wrapping
    row = col.row()
    row.label(text=text, icon=icon)


def draw_warning_text(layout: UILayout, text: str) -> None:
    """Draw warning-styled text"""
    col = layout.column()
    col.alert = True
    row = col.row()
    row.label(text=text, icon='ERROR')


def draw_primary_button(layout: UILayout, operator_idname: str, text: str = "", 
                       icon: str = 'NONE', **kwargs) -> None:
    """Draw a primary action button with standard scaling"""
    row = layout.row(align=True)
    row.scale_y = UIStyle.PRIMARY_BUTTON_SCALE
    row.operator(operator_idname, text=text, icon=icon, **kwargs)


def draw_operator_row(layout: UILayout, operators: list[tuple[str, str, str]],
                     scale_y: float = 1.0, equal_width: bool = True) -> None:
    """Draw multiple operators in a single row with consistent sizing"""
    if not operators:
        return
    
    row = layout.row(align=equal_width)
    row.scale_y = scale_y
    
    for op_id, text, icon in operators:
        row.operator(op_id, text=text, icon=icon)


def draw_collapsible_section(layout: UILayout, title: str, icon: str, 
                            draw_func: Callable[[UILayout], None],
                            context: Context, storage_attr: str) -> None:
    """Draw a collapsible section (using context scene properties for state)"""
    col = layout.column(align=True)
    row = col.row()
    
    scene = context.scene
    attr_name = f"_ui_expand_{storage_attr}"
    is_expanded = getattr(scene, attr_name, False)
    icon_name = 'DISCLOSURE_TRI_DOWN' if is_expanded else 'DISCLOSURE_TRI_RIGHT'
    row.prop(scene, attr_name, text="", icon=icon_name, emboss=False)
    row.label(text=title, icon=icon)
    
    if is_expanded:
        col.separator(factor=UIStyle.SUBSECTION_SEPARATOR_FACTOR)
        draw_func(col)


def apply_operator_disable_feedback(operator: Operator, layout: UILayout, 
                                   is_disabled: bool, reason: str = "") -> UILayout:
    """Prepare layout for disabled operator with visual feedback"""
    if is_disabled:
        layout.enabled = False
    return layout


def wrap_text_label(layout: UILayout, text: str, max_length: int = 50) -> None:
    """Draw a label that wraps long text across multiple lines"""
    words = text.split()
    current_line = ""
    
    col = layout.column()
    
    for word in words:
        test_line = (current_line + " " + word).strip()
        if len(test_line) > max_length and current_line:
            col.label(text=current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        col.label(text=current_line)
