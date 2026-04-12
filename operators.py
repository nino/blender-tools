"""Standalone operators: shrinkwrap refresh, image reload, smart delete."""

from typing import Literal

import bpy
from bpy.types import Context

OperatorReturnItems = Literal[
    "RUNNING_MODAL",
    "CANCELLED",
    "FINISHED",
    "PASS_THROUGH",
    "INTERFACE",
]


class NINO_OT_refresh_shrinkwrap(bpy.types.Operator):
    """Refresh shrinkwrap modifier by duplicating and applying"""

    bl_idname = "nino.refresh_shrinkwrap"
    bl_label = "Refresh Shrinkwrap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object
        if obj is None or obj.type != "MESH":
            self.report({"WARNING"}, "No mesh object selected")
            return {"CANCELLED"}

        shrinkwrap_mod = None
        for mod in obj.modifiers:
            if mod.type == "SHRINKWRAP":
                shrinkwrap_mod = mod
                break

        if shrinkwrap_mod is None:
            self.report({"WARNING"}, "No shrinkwrap modifier found")
            return {"CANCELLED"}

        was_in_edit_mode = context.mode == "EDIT_MESH"

        if was_in_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")

        modifier_name = shrinkwrap_mod.name
        bpy.ops.object.modifier_copy(modifier=modifier_name)
        bpy.ops.object.modifier_apply(modifier=modifier_name)

        if was_in_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")

        self.report({"INFO"}, "Refreshed shrinkwrap modifier")
        return {"FINISHED"}


class NINO_OT_reload_all_images(bpy.types.Operator):
    """Reload all images in the current Blender file"""

    bl_idname = "nino.reload_all_images"
    bl_label = "Reload All Images"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        reloaded_count = 0

        for img in bpy.data.images:
            if img.filepath:
                try:
                    img.reload()
                    reloaded_count += 1
                except Exception as e:
                    self.report({"WARNING"}, f"Failed to reload {img.name}: {str(e)}")

        if reloaded_count > 0:
            self.report({"INFO"}, f"Reloaded {reloaded_count} image(s)")
        else:
            self.report({"INFO"}, "No images to reload")

        return {"FINISHED"}


class NINO_OT_smart_delete(bpy.types.Operator):
    """Delete faces/vertices or dissolve edges based on current selection mode"""

    bl_idname = "nino.smart_delete"
    bl_label = "Smart Delete"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.mode == "EDIT_MESH"

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        tool_settings = context.tool_settings
        select_mode = tool_settings.mesh_select_mode

        if select_mode[0]:
            bpy.ops.mesh.delete(type="VERT")
        elif select_mode[1]:
            bpy.ops.mesh.dissolve_edges()
        elif select_mode[2]:
            bpy.ops.mesh.delete(type="FACE")

        return {"FINISHED"}


classes = (
    NINO_OT_refresh_shrinkwrap,
    NINO_OT_reload_all_images,
    NINO_OT_smart_delete,
)
