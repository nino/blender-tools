"""Stamp texture group properties on objects based on collection membership."""

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

COLLECTION_TO_TEXTURE_GROUP = {
    "Hull Parts": "Main_Hull",
    "Glass Parts": "Glass",
}


class NINO_OT_stamp_texture_groups(bpy.types.Operator):
    """Stamp texture_group custom property on objects based on collection membership"""

    bl_idname = "nino.stamp_texture_groups"
    bl_label = "Stamp Texture Groups"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        updated_count = 0

        for collection_name, group_name in COLLECTION_TO_TEXTURE_GROUP.items():
            collection = bpy.data.collections.get(collection_name)
            if collection is None:
                continue
            for obj in collection.objects:
                obj["texture_group"] = group_name
                updated_count += 1

        self.report({"INFO"}, f"Set texture_group on {updated_count} object(s)")
        return {"FINISHED"}


classes = (NINO_OT_stamp_texture_groups,)
