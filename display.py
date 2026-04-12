"""Wireframe display system: settings, handler, and utilities."""

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty
from bpy.app.handlers import persistent

_previous_selection = set()


class NinoToolsSettings(PropertyGroup):
    """Settings for Nino's Tools"""

    wireframe_on_selected: BoolProperty(
        name="Show Wireframe on Selected",
        description="Automatically show wireframe on selected objects",
        default=False,
    )

    wireframe_hierarchy: BoolProperty(
        name="Wireframe on Hierarchy",
        description="Enable wireframe on selected objects and their children",
        default=False,
    )


def set_wire_recursive(obj, enabled):
    """Recursively set wireframe display for an object and its children"""
    if obj.type == "MESH":
        obj.show_wire = enabled
    for child in obj.children:
        set_wire_recursive(child, enabled)


@persistent
def update_wire_display(scene, depsgraph):
    """
    Automatically toggle show_wire on selected objects and off on deselected objects.
    This handler runs on every depsgraph update.
    """
    global _previous_selection

    settings = bpy.context.scene.nino_tools_settings

    if not settings.wireframe_on_selected:
        return

    current_selection = set(obj.name for obj in bpy.context.selected_objects)

    newly_selected = current_selection - _previous_selection
    newly_deselected = _previous_selection - current_selection

    for obj_name in newly_selected:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if settings.wireframe_hierarchy:
                set_wire_recursive(obj, True)
            elif obj.type == "MESH":
                obj.show_wire = True

    for obj_name in newly_deselected:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if settings.wireframe_hierarchy:
                set_wire_recursive(obj, False)
            elif obj.type == "MESH":
                obj.show_wire = False

    _previous_selection = current_selection


def register():
    """Register scene property and depsgraph handler."""
    global _previous_selection
    _previous_selection = set()

    bpy.types.Scene.nino_tools_settings = bpy.props.PointerProperty(
        type=NinoToolsSettings
    )

    if update_wire_display not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(update_wire_display)


def unregister():
    """Unregister scene property and depsgraph handler."""
    if update_wire_display in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_wire_display)

    del bpy.types.Scene.nino_tools_settings


classes = (NinoToolsSettings,)
