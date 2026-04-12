"""N-panel UI for Nino's Tools."""

import bpy


class NINO_PT_tools_panel(bpy.types.Panel):
    """Creates a Panel in the N-panel"""

    bl_label = "Nino's Tools"
    bl_idname = "NINO_PT_tools_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"

    def draw(self, context):
        layout = self.layout
        assert layout is not None

        settings = context.scene.nino_tools_settings

        # Wireframe settings section
        box = layout.box()
        box.label(text="Wireframe", icon="SHADING_WIRE")
        box.prop(settings, "wireframe_on_selected")
        box.prop(settings, "wireframe_hierarchy")

        # Subd tools section
        box = layout.box()
        box.label(text="Subd Tools", icon="MOD_SUBSURF")

        col = box.column(align=True)
        col.operator("nino.decrease_subsurf_level", text="Decrease Subd Level")
        col.operator("nino.increase_subsurf_level", text="Increase Subd Level")
        col.operator("nino.cycle_subsurf_preview", text="Cycle Subd Preview")
        col.operator("nino.toggle_subd", text="Toggle Subd")
        col.operator("nino.toggle_optimal_display", text="Toggle Optimal Display")
        col.operator(
            "nino.subdivide_selection", text="Subdivide Selection (Smooth All)"
        )
        col.operator(
            "nino.subdivide_selection_keep_corners",
            text="Subdivide Selection (Keep Corners)",
        )

        # Modifier tools section
        box = layout.box()
        box.label(text="Modifier Tools", icon="MODIFIER")

        col = box.column(align=True)
        col.operator("nino.refresh_shrinkwrap", text="Refresh Shrinkwrap")

        # Image tools section
        box = layout.box()
        box.label(text="Image Tools", icon="IMAGE_DATA")

        col = box.column(align=True)
        col.operator("nino.reload_all_images", text="Reload All Images")

        # Texture tools section
        box = layout.box()
        box.label(text="Texture Tools", icon="TEXTURE")

        col = box.column(align=True)
        col.operator("nino.stamp_texture_groups", text="Stamp Texture Groups")


classes = (NINO_PT_tools_panel,)
