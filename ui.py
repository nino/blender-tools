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

        box.prop(settings, "subd_auto_create")

        # Level buttons: -, 1, 2, 3, 4, +
        row = box.row(align=True)
        row.operator("nino.decrease_subsurf_level", text="-")
        for lvl in (1, 2, 3, 4):
            row.operator("nino.set_subsurf_level", text=str(lvl)).level = lvl
        row.operator("nino.increase_subsurf_level", text="+")

        # Toggle buttons: Edit, Toggle, Opt
        row = box.row(align=True)
        row.operator(
            "nino.cycle_subsurf_preview", text="Edit", icon="EDITMODE_HLT"
        )
        row.operator("nino.toggle_subd", text="Toggle", icon="HIDE_OFF")
        row.operator(
            "nino.toggle_optimal_display", text="Opt", icon="MOD_WIREFRAME"
        )

        # Subdivide buttons: Smooth, Smooth (corners)
        row = box.row(align=True)
        row.operator("nino.subdivide_selection", text="Smooth")
        row.operator(
            "nino.subdivide_selection_keep_corners", text="Smooth (corners)"
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
