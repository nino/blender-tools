"""
Nino's Tools - A Blender addon for subdivision surface management and more.
"""

bl_info = {
    "name": "Nino's Tools",
    "author": "Nino",
    "version": (1, 4, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel > Nino's Tools",
    "description": "Collection of helpful modeling tools",
    "category": "3D View",
}

from typing import cast, Literal
import uuid

import bpy
from bpy.types import Context, SubsurfModifier, Object, PropertyGroup
from bpy.props import BoolProperty
from bpy.app.handlers import persistent

OperatorReturnItems = Literal[
    "RUNNING_MODAL",  # Running Modal.Keep the operator running with blender.
    "CANCELLED",  # Cancelled.The operator exited without doing anything, so no undo entry should be pushed.
    "FINISHED",  # Finished.The operator exited after completing its action.
    "PASS_THROUGH",  # Pass Through.Do nothing and pass the event on.
    "INTERFACE",  # Interface.Handled but not executed (popup menus).
]


# Utility function to get or create subdivision surface modifier
def get_or_create_subsurf(
    obj, default_viewport_level=2, default_render_level=2
) -> SubsurfModifier:
    """
    Get the last subdivision surface modifier or create one if none exists.

    Args:
        obj: The mesh object
        default_viewport_level: Viewport level to set if creating new modifier
        default_render_level: Render level to set if creating new modifier

    Returns:
        The subdivision surface modifier
    """
    # Find all subsurf modifiers
    subsurf_mods = [mod for mod in obj.modifiers if mod.type == "SUBSURF"]

    if subsurf_mods:
        # Use the last one
        return cast(SubsurfModifier, subsurf_mods[-1])
    else:
        # Create a new one
        mod = cast(
            SubsurfModifier, obj.modifiers.new(name="Subdivision", type="SUBSURF")
        )
        mod.levels = default_viewport_level
        mod.render_levels = default_render_level
        mod.show_on_cage = False
        mod.show_in_editmode = False
        mod.show_viewport = True
        mod.show_render = True
        return mod


class NINO_OT_decrease_subsurf_level(bpy.types.Operator):
    """Decrease subdivision surface viewport level by 1"""

    bl_idname = "nino.decrease_subsurf_level"
    bl_label = "Decrease Subd Level"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                mod = get_or_create_subsurf(
                    obj, default_viewport_level=2, default_render_level=2
                )
                mod.levels -= 1
                processed_count += 1

        if processed_count > 0:
            self.report(
                {"INFO"}, f"Decreased subd level for {processed_count} object(s)"
            )
        else:
            self.report({"WARNING"}, "No mesh objects selected")

        return {"FINISHED"}


class NINO_OT_increase_subsurf_level(bpy.types.Operator):
    """Increase subdivision surface viewport level by 1"""

    bl_idname = "nino.increase_subsurf_level"
    bl_label = "Increase Subd Level"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                mod = get_or_create_subsurf(
                    obj, default_viewport_level=1, default_render_level=2
                )
                mod.levels += 1
                processed_count += 1

        if processed_count > 0:
            self.report(
                {"INFO"}, f"Increased subd level for {processed_count} object(s)"
            )
        else:
            self.report({"WARNING"}, "No mesh objects selected")

        return {"FINISHED"}


class NINO_OT_cycle_subsurf_preview(bpy.types.Operator):
    """Cycle subdivision surface preview mode (on cage / edit mode)"""

    bl_idname = "nino.cycle_subsurf_preview"
    bl_label = "Cycle Subd Preview"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                mod = get_or_create_subsurf(
                    obj, default_viewport_level=2, default_render_level=2
                )

                # Determine current state and cycle to next
                # States:
                # 1. on_cage=False, edit_mode=False
                # 2. on_cage=False, edit_mode=True
                # 3. on_cage=True, edit_mode=True
                # Note: on_cage=True, edit_mode=False is treated as state 1

                if not mod.show_on_cage and not mod.show_in_editmode:
                    # State 1 -> State 2
                    mod.show_on_cage = False
                    mod.show_in_editmode = True
                elif not mod.show_on_cage and mod.show_in_editmode:
                    # State 2 -> State 3
                    mod.show_on_cage = True
                    mod.show_in_editmode = True
                else:
                    # State 3 (or invalid state) -> State 1
                    mod.show_on_cage = False
                    mod.show_in_editmode = False

                processed_count += 1

        if processed_count > 0:
            self.report(
                {"INFO"}, f"Cycled subd preview for {processed_count} object(s)"
            )
        else:
            self.report({"WARNING"}, "No mesh objects selected")

        return {"FINISHED"}


class NINO_OT_toggle_subd(bpy.types.Operator):
    """Toggle subdivision surface visibility for selected objects"""

    bl_idname = "nino.toggle_subd"
    bl_label = "Toggle Subd"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        # Build list of (object, subsurf_modifier) for all selected objects with subsurf
        objects_with_subsurf: list[tuple[Object, SubsurfModifier]] = []

        for obj in context.selected_objects:
            if obj.type == "MESH":
                subsurf_mods = [mod for mod in obj.modifiers if mod.type == "SUBSURF"]
                for mod in subsurf_mods:
                    objects_with_subsurf.append((obj, cast(SubsurfModifier, mod)))

        if not objects_with_subsurf:
            self.report({"WARNING"}, "No selected objects with subsurf modifiers")
            return {"CANCELLED"}

        # Check the first modifier's viewport visibility to determine action
        first_mod = objects_with_subsurf[0][1]
        should_enable = not first_mod.show_viewport

        # Toggle all subsurf modifiers
        for obj, mod in objects_with_subsurf:
            mod.show_viewport = should_enable
            mod.show_render = should_enable

        action = "Enabled" if should_enable else "Disabled"
        self.report(
            {"INFO"}, f"{action} subd for {len(objects_with_subsurf)} modifier(s)"
        )

        return {"FINISHED"}


class NINO_OT_toggle_optimal_display(bpy.types.Operator):
    """Toggle optimal display for all subsurf modifiers on selected objects"""

    bl_idname = "nino.toggle_optimal_display"
    bl_label = "Toggle Optimal Display"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        # Build list of subsurf modifiers for all selected objects
        subsurf_mods: list[SubsurfModifier] = []

        for obj in context.selected_objects:
            if obj.type == "MESH":
                for mod in obj.modifiers:
                    if mod.type == "SUBSURF":
                        subsurf_mods.append(cast(SubsurfModifier, mod))

        if not subsurf_mods:
            self.report({"WARNING"}, "No selected objects with subsurf modifiers")
            return {"CANCELLED"}

        # Check the first modifier's optimal display state to determine action
        first_mod = subsurf_mods[0]
        should_enable = not first_mod.show_only_control_edges

        # Toggle all subsurf modifiers
        for mod in subsurf_mods:
            mod.show_only_control_edges = should_enable

        action = "Enabled" if should_enable else "Disabled"
        self.report(
            {"INFO"}, f"{action} optimal display for {len(subsurf_mods)} modifier(s)"
        )

        return {"FINISHED"}


def _subdivide_selection_impl(
    context: Context, boundary_smooth: str = "All"
) -> tuple[set[OperatorReturnItems], str]:
    """
    Subdivide selected geometry using geometry nodes.

    Args:
        context: Blender context
        boundary_smooth: Boundary smooth mode ('All' or 'Keep Corners')

    Returns:
        Tuple of (operator return set, message)
    """
    # Check if we're in edit mode
    if context.mode != "EDIT_MESH":
        return {"CANCELLED"}, "Must be in edit mode"

    obj = context.active_object
    if obj is None or obj.type != "MESH":
        return {"CANCELLED"}, "No active mesh object"

    # 1. Generate a random ID
    random_id = str(uuid.uuid4())[:8]
    vertex_group_name = f"vertex-group-{random_id}"
    modifier_name = f"geonodes-{random_id}"

    # 2. Assign current selection to a new vertex group
    vertex_group = obj.vertex_groups.new(name=vertex_group_name)
    bpy.ops.object.vertex_group_assign()

    # 3. Switch to object mode to add modifier
    bpy.ops.object.mode_set(mode="OBJECT")

    # 4. Add geometry nodes modifier
    modifier = obj.modifiers.new(name=modifier_name, type="NODES")

    # Create a new geometry nodes tree
    node_tree = bpy.data.node_groups.new(
        name=f"Subdivide-{random_id}", type="GeometryNodeTree"
    )
    modifier.node_group = node_tree

    # Create nodes
    nodes = node_tree.nodes
    links = node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Group Input and Group Output nodes
    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")

    # Position nodes
    group_input.location = (-600, 0)
    group_output.location = (600, 0)

    # Create required sockets on the node tree
    node_tree.interface.new_socket(
        name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    node_tree.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    # Create Separate Geometry node
    separate_geo = nodes.new("GeometryNodeSeparateGeometry")
    separate_geo.location = (-300, 0)
    separate_geo.domain = "POINT"

    # Create Named Attribute node for vertex group
    named_attr = nodes.new("GeometryNodeInputNamedAttribute")
    named_attr.location = (-500, -150)
    named_attr.data_type = "FLOAT"
    named_attr.inputs[0].default_value = vertex_group_name

    # Create Subdivision Surface node
    subsurf = nodes.new("GeometryNodeSubdivisionSurface")
    subsurf.location = (0, 100)
    subsurf.inputs["Level"].default_value = 1
    subsurf.inputs[6].default_value = boundary_smooth

    # Create Named Attribute node for edge crease
    edge_crease_attr = nodes.new("GeometryNodeInputNamedAttribute")
    edge_crease_attr.location = (-200, -100)
    edge_crease_attr.data_type = "FLOAT"
    edge_crease_attr.inputs[0].default_value = "crease_edge"

    # Create Named Attribute node for vertex crease
    vert_crease_attr = nodes.new("GeometryNodeInputNamedAttribute")
    vert_crease_attr.location = (-200, -200)
    vert_crease_attr.data_type = "FLOAT"
    vert_crease_attr.inputs[0].default_value = "crease_vert"

    # Create Join Geometry node
    join_geo = nodes.new("GeometryNodeJoinGeometry")
    join_geo.location = (300, 0)

    # Link nodes
    # Group Input -> Separate Geometry
    links.new(group_input.outputs["Geometry"], separate_geo.inputs["Geometry"])

    # Named Attribute -> Separate Geometry (Selection)
    links.new(named_attr.outputs["Attribute"], separate_geo.inputs["Selection"])

    # Separate Geometry (Selection) -> Subdivision Surface
    links.new(separate_geo.outputs["Selection"], subsurf.inputs["Mesh"])

    # Edge Crease attribute -> Subdivision Surface
    links.new(edge_crease_attr.outputs["Attribute"], subsurf.inputs["Edge Crease"])

    # Vertex Crease attribute -> Subdivision Surface
    links.new(vert_crease_attr.outputs["Attribute"], subsurf.inputs["Vertex Crease"])

    # Subdivision Surface -> Join Geometry
    links.new(subsurf.outputs["Mesh"], join_geo.inputs["Geometry"])

    # Separate Geometry (Inverted) -> Join Geometry
    links.new(separate_geo.outputs["Inverted"], join_geo.inputs["Geometry"])

    # Join Geometry -> Group Output
    links.new(join_geo.outputs["Geometry"], group_output.inputs["Geometry"])

    # 5. Apply the modifier
    bpy.ops.object.modifier_apply(modifier=modifier_name)

    # 6. Go back to edit mode
    bpy.ops.object.mode_set(mode="EDIT")

    active_object = bpy.context.active_object
    group = active_object.vertex_groups.get(vertex_group_name)
    if group:
        active_object.vertex_groups.remove(group)

    return {"FINISHED"}, "Subdivided selection"


class NINO_OT_subdivide_selection(bpy.types.Operator):
    """Subdivide selected geometry using geometry nodes (smooth all)"""

    bl_idname = "nino.subdivide_selection"
    bl_label = "Subdivide Selection (Smooth All)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        result, message = _subdivide_selection_impl(context, boundary_smooth="All")
        if result == {"CANCELLED"}:
            self.report({"WARNING"}, message)
        else:
            self.report({"INFO"}, message)
        return result


class NINO_OT_subdivide_selection_keep_corners(bpy.types.Operator):
    """Subdivide selected geometry using geometry nodes (keep corners)"""

    bl_idname = "nino.subdivide_selection_keep_corners"
    bl_label = "Subdivide Selection (Keep Corners)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        result, message = _subdivide_selection_impl(
            context, boundary_smooth="Keep Corners"
        )
        if result == {"CANCELLED"}:
            self.report({"WARNING"}, message)
        else:
            self.report({"INFO"}, message)
        return result


class NINO_OT_refresh_shrinkwrap(bpy.types.Operator):
    """Refresh shrinkwrap modifier by duplicating and applying"""

    bl_idname = "nino.refresh_shrinkwrap"
    bl_label = "Refresh Shrinkwrap"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        # Check if we have a mesh object selected
        obj = context.active_object
        if obj is None or obj.type != "MESH":
            self.report({"WARNING"}, "No mesh object selected")
            return {"CANCELLED"}

        # Find the first shrinkwrap modifier
        shrinkwrap_mod = None
        for mod in obj.modifiers:
            if mod.type == "SHRINKWRAP":
                shrinkwrap_mod = mod
                break

        if shrinkwrap_mod is None:
            self.report({"WARNING"}, "No shrinkwrap modifier found")
            return {"CANCELLED"}

        # Remember if we were in edit mode
        was_in_edit_mode = context.mode == "EDIT_MESH"

        # Switch to object mode if needed
        if was_in_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")

        # Duplicate the shrinkwrap modifier
        modifier_name = shrinkwrap_mod.name
        bpy.ops.object.modifier_copy(modifier=modifier_name)

        # Apply the original modifier (the copy is now after it)
        bpy.ops.object.modifier_apply(modifier=modifier_name)

        # Go back to edit mode if needed
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
            # Only reload images that have a filepath (skip generated/packed images)
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


# Keymap storage
addon_keymaps = []

# Store previous selection state for wire display toggle
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

    # Get settings
    settings = bpy.context.scene.nino_tools_settings

    # Early exit if wireframe on selected is disabled
    if not settings.wireframe_on_selected:
        return

    # Get currently selected objects
    current_selection = set(obj.name for obj in bpy.context.selected_objects)

    # Find newly selected objects
    newly_selected = current_selection - _previous_selection

    # Find newly deselected objects
    newly_deselected = _previous_selection - current_selection

    # Enable wire display for newly selected objects
    for obj_name in newly_selected:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if settings.wireframe_hierarchy:
                set_wire_recursive(obj, True)
            elif obj.type == "MESH":
                obj.show_wire = True

    # Disable wire display for newly deselected objects
    for obj_name in newly_deselected:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if settings.wireframe_hierarchy:
                set_wire_recursive(obj, False)
            elif obj.type == "MESH":
                obj.show_wire = False

    # Update the previous selection state
    _previous_selection = current_selection


def register():
    bpy.utils.register_class(NinoToolsSettings)
    bpy.utils.register_class(NINO_OT_decrease_subsurf_level)
    bpy.utils.register_class(NINO_OT_increase_subsurf_level)
    bpy.utils.register_class(NINO_OT_cycle_subsurf_preview)
    bpy.utils.register_class(NINO_OT_toggle_subd)
    bpy.utils.register_class(NINO_OT_toggle_optimal_display)
    bpy.utils.register_class(NINO_OT_subdivide_selection)
    bpy.utils.register_class(NINO_OT_subdivide_selection_keep_corners)
    bpy.utils.register_class(NINO_OT_refresh_shrinkwrap)
    bpy.utils.register_class(NINO_OT_reload_all_images)
    bpy.utils.register_class(NINO_PT_tools_panel)

    # Add settings to scene
    bpy.types.Scene.nino_tools_settings = bpy.props.PointerProperty(
        type=NinoToolsSettings
    )

    # Clear previous selection state
    global _previous_selection
    _previous_selection = set()

    # Register the wire display handler (avoid duplicates)
    if update_wire_display not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(update_wire_display)

    # Add keymaps
    wm = bpy.context.window_manager
    assert wm is not None
    if wm.keyconfigs.addon:
        kc = wm.keyconfigs.addon
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

        # CMD-1: Decrease subd level
        kmi = km.keymap_items.new(
            NINO_OT_decrease_subsurf_level.bl_idname,
            type="ONE",
            value="PRESS",
            oskey=True,  # oskey is CMD on macOS
        )
        addon_keymaps.append((km, kmi))

        # CMD-2: Increase subd level
        kmi = km.keymap_items.new(
            NINO_OT_increase_subsurf_level.bl_idname,
            type="TWO",
            value="PRESS",
            oskey=True,
        )
        addon_keymaps.append((km, kmi))

        # CMD-3: Cycle subd preview
        kmi = km.keymap_items.new(
            NINO_OT_cycle_subsurf_preview.bl_idname,
            type="THREE",
            value="PRESS",
            oskey=True,
        )
        addon_keymaps.append((km, kmi))

        # CMD-SHIFT-D: Subdivide selection
        kmi = km.keymap_items.new(
            NINO_OT_subdivide_selection.bl_idname,
            type="D",
            value="PRESS",
            oskey=True,
            shift=True,
        )
        addon_keymaps.append((km, kmi))


def unregister():
    # Unregister the wire display handler
    if update_wire_display in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_wire_display)

    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    # Remove settings from scene
    del bpy.types.Scene.nino_tools_settings

    bpy.utils.unregister_class(NINO_PT_tools_panel)
    bpy.utils.unregister_class(NINO_OT_reload_all_images)
    bpy.utils.unregister_class(NINO_OT_refresh_shrinkwrap)
    bpy.utils.unregister_class(NINO_OT_subdivide_selection_keep_corners)
    bpy.utils.unregister_class(NINO_OT_subdivide_selection)
    bpy.utils.unregister_class(NINO_OT_toggle_subd)
    bpy.utils.unregister_class(NINO_OT_toggle_optimal_display)
    bpy.utils.unregister_class(NINO_OT_cycle_subsurf_preview)
    bpy.utils.unregister_class(NINO_OT_increase_subsurf_level)
    bpy.utils.unregister_class(NINO_OT_decrease_subsurf_level)
    bpy.utils.unregister_class(NinoToolsSettings)


if __name__ == "__main__":
    register()
