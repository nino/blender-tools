"""Subdivision surface operators and utilities."""

from typing import cast, Literal
import uuid

import bpy
from bpy.props import IntProperty
from bpy.types import Context, SubsurfModifier, Object

OperatorReturnItems = Literal[
    "RUNNING_MODAL",
    "CANCELLED",
    "FINISHED",
    "PASS_THROUGH",
    "INTERFACE",
]


def get_existing_subsurf(obj) -> SubsurfModifier | None:
    """Get the last subdivision surface modifier, or None if none exists."""
    subsurf_mods = [mod for mod in obj.modifiers if mod.type == "SUBSURF"]
    return cast(SubsurfModifier, subsurf_mods[-1]) if subsurf_mods else None


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
    subsurf_mods = [mod for mod in obj.modifiers if mod.type == "SUBSURF"]

    if subsurf_mods:
        return cast(SubsurfModifier, subsurf_mods[-1])
    else:
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
        auto_create = context.scene.nino_tools_settings.subd_auto_create
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                if auto_create:
                    mod = get_or_create_subsurf(
                        obj, default_viewport_level=2, default_render_level=2
                    )
                else:
                    mod = get_existing_subsurf(obj)
                    if mod is None:
                        continue
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
        auto_create = context.scene.nino_tools_settings.subd_auto_create
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                if auto_create:
                    mod = get_or_create_subsurf(
                        obj, default_viewport_level=1, default_render_level=2
                    )
                else:
                    mod = get_existing_subsurf(obj)
                    if mod is None:
                        continue
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
        auto_create = context.scene.nino_tools_settings.subd_auto_create
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                if auto_create:
                    mod = get_or_create_subsurf(
                        obj, default_viewport_level=2, default_render_level=2
                    )
                else:
                    mod = get_existing_subsurf(obj)
                    if mod is None:
                        continue

                # Toggle between both off and both on
                both_on = mod.show_on_cage and mod.show_in_editmode
                mod.show_on_cage = not both_on
                mod.show_in_editmode = not both_on

                processed_count += 1

        if processed_count > 0:
            self.report(
                {"INFO"}, f"Cycled subd preview for {processed_count} object(s)"
            )
        else:
            self.report({"WARNING"}, "No mesh objects selected")

        return {"FINISHED"}


class NINO_OT_set_subsurf_level(bpy.types.Operator):
    """Set subdivision surface viewport level to a specific value"""

    bl_idname = "nino.set_subsurf_level"
    bl_label = "Set Subd Level"
    bl_options = {"REGISTER", "UNDO"}

    level: IntProperty(name="Level", default=2, min=0, max=11)

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        auto_create = context.scene.nino_tools_settings.subd_auto_create
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == "MESH":
                if auto_create:
                    mod = get_or_create_subsurf(
                        obj,
                        default_viewport_level=self.level,
                        default_render_level=max(self.level, 2),
                    )
                else:
                    mod = get_existing_subsurf(obj)
                    if mod is None:
                        continue
                mod.levels = self.level
                processed_count += 1

        if processed_count > 0:
            self.report(
                {"INFO"},
                f"Set subd level to {self.level} for {processed_count} object(s)",
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
        objects_with_subsurf: list[tuple[Object, SubsurfModifier]] = []

        for obj in context.selected_objects:
            if obj.type == "MESH":
                subsurf_mods = [mod for mod in obj.modifiers if mod.type == "SUBSURF"]
                for mod in subsurf_mods:
                    objects_with_subsurf.append((obj, cast(SubsurfModifier, mod)))

        if not objects_with_subsurf:
            self.report({"WARNING"}, "No selected objects with subsurf modifiers")
            return {"CANCELLED"}

        first_mod = objects_with_subsurf[0][1]
        should_enable = not first_mod.show_viewport

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
        subsurf_mods: list[SubsurfModifier] = []

        for obj in context.selected_objects:
            if obj.type == "MESH":
                for mod in obj.modifiers:
                    if mod.type == "SUBSURF":
                        subsurf_mods.append(cast(SubsurfModifier, mod))

        if not subsurf_mods:
            self.report({"WARNING"}, "No selected objects with subsurf modifiers")
            return {"CANCELLED"}

        first_mod = subsurf_mods[0]
        should_enable = not first_mod.show_only_control_edges

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
    if context.mode != "EDIT_MESH":
        return {"CANCELLED"}, "Must be in edit mode"

    obj = context.active_object
    if obj is None or obj.type != "MESH":
        return {"CANCELLED"}, "No active mesh object"

    random_id = str(uuid.uuid4())[:8]
    vertex_group_name = f"vertex-group-{random_id}"
    modifier_name = f"geonodes-{random_id}"

    vertex_group = obj.vertex_groups.new(name=vertex_group_name)
    bpy.ops.object.vertex_group_assign()

    bpy.ops.object.mode_set(mode="OBJECT")

    modifier = obj.modifiers.new(name=modifier_name, type="NODES")

    node_tree = bpy.data.node_groups.new(
        name=f"Subdivide-{random_id}", type="GeometryNodeTree"
    )
    modifier.node_group = node_tree

    nodes = node_tree.nodes
    links = node_tree.links

    nodes.clear()

    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")

    group_input.location = (-600, 0)
    group_output.location = (600, 0)

    node_tree.interface.new_socket(
        name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"
    )
    node_tree.interface.new_socket(
        name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry"
    )

    separate_geo = nodes.new("GeometryNodeSeparateGeometry")
    separate_geo.location = (-300, 0)
    separate_geo.domain = "POINT"

    named_attr = nodes.new("GeometryNodeInputNamedAttribute")
    named_attr.location = (-500, -150)
    named_attr.data_type = "FLOAT"
    named_attr.inputs[0].default_value = vertex_group_name

    subsurf = nodes.new("GeometryNodeSubdivisionSurface")
    subsurf.location = (0, 100)
    subsurf.inputs["Level"].default_value = 1
    subsurf.inputs[6].default_value = boundary_smooth

    edge_crease_attr = nodes.new("GeometryNodeInputNamedAttribute")
    edge_crease_attr.location = (-200, -100)
    edge_crease_attr.data_type = "FLOAT"
    edge_crease_attr.inputs[0].default_value = "crease_edge"

    vert_crease_attr = nodes.new("GeometryNodeInputNamedAttribute")
    vert_crease_attr.location = (-200, -200)
    vert_crease_attr.data_type = "FLOAT"
    vert_crease_attr.inputs[0].default_value = "crease_vert"

    join_geo = nodes.new("GeometryNodeJoinGeometry")
    join_geo.location = (300, 0)

    links.new(group_input.outputs["Geometry"], separate_geo.inputs["Geometry"])
    links.new(named_attr.outputs["Attribute"], separate_geo.inputs["Selection"])
    links.new(separate_geo.outputs["Selection"], subsurf.inputs["Mesh"])
    links.new(edge_crease_attr.outputs["Attribute"], subsurf.inputs["Edge Crease"])
    links.new(vert_crease_attr.outputs["Attribute"], subsurf.inputs["Vertex Crease"])
    links.new(subsurf.outputs["Mesh"], join_geo.inputs["Geometry"])
    links.new(separate_geo.outputs["Inverted"], join_geo.inputs["Geometry"])
    links.new(join_geo.outputs["Geometry"], group_output.inputs["Geometry"])

    bpy.ops.object.modifier_apply(modifier=modifier_name)

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


classes = (
    NINO_OT_decrease_subsurf_level,
    NINO_OT_increase_subsurf_level,
    NINO_OT_set_subsurf_level,
    NINO_OT_cycle_subsurf_preview,
    NINO_OT_toggle_subd,
    NINO_OT_toggle_optimal_display,
    NINO_OT_subdivide_selection,
    NINO_OT_subdivide_selection_keep_corners,
)
