"""Lattice helper operators: add, apply, and discard lattice deformations."""

import uuid
from typing import Literal, cast

import bmesh
import bpy
from bpy.props import EnumProperty, IntProperty
from bpy.types import Context, LatticeModifier, Object
from mathutils import Matrix, Vector

OperatorReturnItems = Literal[
    "RUNNING_MODAL",
    "CANCELLED",
    "FINISHED",
    "PASS_THROUGH",
    "INTERFACE",
]

LATTICE_MAGIC_KEY = "nino_lattice_tool"
LATTICE_VGROUP_KEY = "nino_lattice_vgroup"

MIN_DIMENSION = 0.001


def _get_orientation_matrix(orientation: str, obj: Object, context: Context) -> Matrix:
    """Return a rotation-only 4x4 matrix for the given orientation mode."""
    if orientation == "LOCAL":
        return obj.matrix_world.to_3x3().normalized().to_4x4()
    elif orientation == "CURSOR":
        return context.scene.cursor.matrix.to_3x3().normalized().to_4x4()
    # WORLD
    return Matrix.Identity(4)


def _find_lattice_targets(
    lattice_obj: Object,
) -> list[tuple[Object, LatticeModifier]]:
    """Find all mesh objects with a lattice modifier referencing the given lattice."""
    targets: list[tuple[Object, LatticeModifier]] = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for mod in obj.modifiers:
            if mod.type == "LATTICE":
                lat_mod = cast(LatticeModifier, mod)
                if lat_mod.object == lattice_obj:
                    targets.append((obj, lat_mod))
    return targets


def _remove_vgroup(obj: Object, lattice_obj: Object) -> None:
    """Remove the vertex group stored on the lattice, if it exists on the mesh."""
    vgroup_name = lattice_obj.get(LATTICE_VGROUP_KEY)
    if not vgroup_name:
        return
    vg = obj.vertex_groups.get(vgroup_name)
    if vg:
        obj.vertex_groups.remove(vg)


class NINO_OT_add_lattice(bpy.types.Operator):
    """Add a lattice deformer fitted to the selected geometry"""

    bl_idname = "nino.add_lattice"
    bl_label = "Add Lattice"
    bl_options = {"REGISTER", "UNDO"}

    orientation: EnumProperty(  # type: ignore[valid-type]
        name="Orientation",
        items=[
            ("LOCAL", "Local", "Align to object's local space"),
            ("WORLD", "World", "Align to world axes"),
            ("CURSOR", "3D Cursor", "Align to 3D cursor rotation"),
        ],
        default="LOCAL",
    )
    u_res: IntProperty(name="U", default=2, min=2, max=64)  # type: ignore[valid-type]
    v_res: IntProperty(name="V", default=2, min=2, max=64)  # type: ignore[valid-type]
    w_res: IntProperty(name="W", default=2, min=2, max=64)  # type: ignore[valid-type]

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        # --- Validate and enter edit mode ---
        if context.mode == "OBJECT":
            if obj is None or obj.type != "MESH":
                self.report({"WARNING"}, "Active object must be a mesh")
                return {"CANCELLED"}
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
        elif context.mode == "EDIT_MESH":
            if obj is None or obj.type != "MESH":
                self.report({"WARNING"}, "Active object must be a mesh")
                return {"CANCELLED"}
        else:
            self.report({"WARNING"}, "Must be in Object or Edit mode")
            return {"CANCELLED"}

        # --- Get selected verts via bmesh ---
        bm = bmesh.from_edit_mesh(obj.data)  # type: ignore[arg-type]
        bm.verts.ensure_lookup_table()

        selected_verts = [v for v in bm.verts if v.select]
        if not selected_verts:
            bpy.ops.mesh.select_all(action="SELECT")
            selected_verts = list(bm.verts)

        # --- Compute oriented bounding box ---
        # Force depsgraph update so matrix_world is current (stale after undo-before-redo)
        context.view_layer.update()  # type: ignore[union-attr]
        orient = _get_orientation_matrix(self.orientation, obj, context)
        orient_inv = orient.inverted()

        oriented_coords = [
            orient_inv @ (obj.matrix_world @ v.co) for v in selected_verts
        ]

        min_co = Vector(
            (
                min(c.x for c in oriented_coords),
                min(c.y for c in oriented_coords),
                min(c.z for c in oriented_coords),
            )
        )
        max_co = Vector(
            (
                max(c.x for c in oriented_coords),
                max(c.y for c in oriented_coords),
                max(c.z for c in oriented_coords),
            )
        )

        center_oriented = (min_co + max_co) / 2
        size = max_co - min_co

        for i in range(3):
            if size[i] < MIN_DIMENSION:
                size[i] = MIN_DIMENSION

        world_center = orient @ center_oriented

        # --- Create vertex group ---
        vgroup_name = f"nino_lattice_{uuid.uuid4().hex[:8]}"
        vgroup = obj.vertex_groups.new(name=vgroup_name)
        obj.vertex_groups.active_index = vgroup.index
        bpy.ops.object.vertex_group_assign()

        # --- Switch to object mode ---
        bpy.ops.object.mode_set(mode="OBJECT")

        # --- Create lattice ---
        lattice_data = bpy.data.lattices.new(name="NinoLattice")
        lattice_data.points_u = self.u_res
        lattice_data.points_v = self.v_res
        lattice_data.points_w = self.w_res

        lattice_obj = bpy.data.objects.new(name="NinoLattice", object_data=lattice_data)
        context.collection.objects.link(lattice_obj)

        lattice_obj.location = world_center
        lattice_obj.rotation_euler = orient.to_euler()

        # Compute scale from the lattice data's actual extent so the physical
        # size matches the bounding box regardless of point count.
        all_co = [p.co_deform for p in lattice_data.points]
        extent = Vector(
            (
                max(c.x for c in all_co) - min(c.x for c in all_co),
                max(c.y for c in all_co) - min(c.y for c in all_co),
                max(c.z for c in all_co) - min(c.z for c in all_co),
            )
        )
        lattice_obj.scale = (
            size.x / extent.x if extent.x > MIN_DIMENSION else size.x,
            size.y / extent.y if extent.y > MIN_DIMENSION else size.y,
            size.z / extent.z if extent.z > MIN_DIMENSION else size.z,
        )

        # Tag lattice with magic properties
        lattice_obj[LATTICE_MAGIC_KEY] = True
        lattice_obj[LATTICE_VGROUP_KEY] = vgroup_name

        # --- Add lattice modifier to mesh (first in stack) ---
        lat_mod = cast(
            LatticeModifier, obj.modifiers.new(name="NinoLattice", type="LATTICE")
        )
        lat_mod.object = lattice_obj
        lat_mod.vertex_group = vgroup_name

        # Move to first position — requires mesh to be active
        context.view_layer.objects.active = obj
        bpy.ops.object.modifier_move_to_index(modifier=lat_mod.name, index=0)

        # --- Select the lattice ---
        obj.select_set(False)
        lattice_obj.select_set(True)
        context.view_layer.objects.active = lattice_obj

        self.report({"INFO"}, "Added lattice deformer")
        return {"FINISHED"}


class NINO_OT_apply_lattice(bpy.types.Operator):
    """Apply the active lattice deformation and clean up"""

    bl_idname = "nino.apply_lattice"
    bl_label = "Apply Lattice"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object
        return obj is not None and obj.type == "LATTICE" and LATTICE_MAGIC_KEY in obj

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        lattice_obj = context.active_object
        assert lattice_obj is not None

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        targets = _find_lattice_targets(lattice_obj)

        for mesh_obj, mod in targets:
            context.view_layer.objects.active = mesh_obj
            mesh_obj.select_set(True)
            bpy.ops.object.modifier_apply(modifier=mod.name)
            _remove_vgroup(mesh_obj, lattice_obj)
            mesh_obj.select_set(False)

        bpy.data.objects.remove(lattice_obj, do_unlink=True)

        self.report({"INFO"}, "Applied lattice deformation")
        return {"FINISHED"}


class NINO_OT_discard_lattice(bpy.types.Operator):
    """Discard the active lattice deformation and clean up"""

    bl_idname = "nino.discard_lattice"
    bl_label = "Discard Lattice"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object
        return obj is not None and obj.type == "LATTICE" and LATTICE_MAGIC_KEY in obj

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        lattice_obj = context.active_object
        assert lattice_obj is not None

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        targets = _find_lattice_targets(lattice_obj)

        for mesh_obj, mod in targets:
            mesh_obj.modifiers.remove(mod)
            _remove_vgroup(mesh_obj, lattice_obj)

        bpy.data.objects.remove(lattice_obj, do_unlink=True)

        self.report({"INFO"}, "Discarded lattice deformation")
        return {"FINISHED"}


classes = (
    NINO_OT_add_lattice,
    NINO_OT_apply_lattice,
    NINO_OT_discard_lattice,
)
