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
        pass


class NINO_PT_wireframe(bpy.types.Panel):
    bl_label = "Wireframe"
    bl_idname = "NINO_PT_wireframe"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"
    bl_parent_id = "NINO_PT_tools_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="SHADING_WIRE")

    def draw(self, context):
        layout = self.layout
        settings = context.scene.nino_tools_settings
        layout.prop(settings, "wireframe_on_selected")
        layout.prop(settings, "wireframe_hierarchy")


class NINO_PT_subd_tools(bpy.types.Panel):
    bl_label = "Subd Tools"
    bl_idname = "NINO_PT_subd_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"
    bl_parent_id = "NINO_PT_tools_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="MOD_SUBSURF")

    def draw(self, context):
        layout = self.layout
        settings = context.scene.nino_tools_settings

        layout.prop(settings, "subd_auto_create")

        # Level buttons: -, 1, 2, 3, 4, +
        row = layout.row(align=True)
        row.operator("nino.decrease_subsurf_level", text="-")
        for lvl in (1, 2, 3, 4):
            row.operator("nino.set_subsurf_level", text=str(lvl)).level = lvl
        row.operator("nino.increase_subsurf_level", text="+")

        # Toggle buttons: Edit, Toggle, Opt
        row = layout.row(align=True)
        row.operator("nino.cycle_subsurf_preview", text="Edit", icon="EDITMODE_HLT")
        row.operator("nino.toggle_subd", text="Toggle", icon="HIDE_OFF")
        row.operator("nino.toggle_optimal_display", text="Opt", icon="MOD_WIREFRAME")

        # Subdivide buttons: Smooth, Smooth (corners)
        row = layout.row(align=True)
        row.operator("nino.subdivide_selection", text="Smooth")
        row.operator("nino.subdivide_selection_keep_corners", text="Smooth (corners)")


class NINO_PT_modifier_tools(bpy.types.Panel):
    bl_label = "Modifier Tools"
    bl_idname = "NINO_PT_modifier_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"
    bl_parent_id = "NINO_PT_tools_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="MODIFIER")

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("nino.refresh_shrinkwrap", text="Refresh Shrinkwrap")


class NINO_PT_image_tools(bpy.types.Panel):
    bl_label = "Image Tools"
    bl_idname = "NINO_PT_image_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"
    bl_parent_id = "NINO_PT_tools_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="IMAGE_DATA")

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("nino.reload_all_images", text="Reload All Images")


class NINO_PT_texture_tools(bpy.types.Panel):
    bl_label = "Texture Tools"
    bl_idname = "NINO_PT_texture_tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Nino's Tools"
    bl_parent_id = "NINO_PT_tools_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="TEXTURE")

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("nino.stamp_texture_groups", text="Stamp Texture Groups")


classes = (
    NINO_PT_tools_panel,
    NINO_PT_wireframe,
    NINO_PT_subd_tools,
    NINO_PT_modifier_tools,
    NINO_PT_image_tools,
    NINO_PT_texture_tools,
)
