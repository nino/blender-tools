"""
Nino's Tools - A Blender addon for subdivision surface management and more.
"""

bl_info = {
    "name": "Nino's Tools",
    "author": "Nino",
    "version": (1, 7, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel > Nino's Tools",
    "description": "Collection of helpful modeling tools",
    "category": "3D View",
}

# Support Blender's module reloading
if "bpy" in locals():
    import importlib

    importlib.reload(subd)
    importlib.reload(display)
    importlib.reload(stamping)
    importlib.reload(operators)
    importlib.reload(ui)

import bpy

from . import subd, display, stamping, operators, ui

_all_classes = (
    *display.classes,
    *subd.classes,
    *operators.classes,
    *stamping.classes,
    *ui.classes,
)

addon_keymaps = []


def register():
    for cls in _all_classes:
        bpy.utils.register_class(cls)

    display.register()

    # Add keymaps
    wm = bpy.context.window_manager
    assert wm is not None
    if wm.keyconfigs.addon:
        kc = wm.keyconfigs.addon
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

        # CMD-1: Decrease subd level
        kmi = km.keymap_items.new(
            "nino.decrease_subsurf_level",
            type="ONE",
            value="PRESS",
            oskey=True,
        )
        addon_keymaps.append((km, kmi))

        # CMD-2: Increase subd level
        kmi = km.keymap_items.new(
            "nino.increase_subsurf_level",
            type="TWO",
            value="PRESS",
            oskey=True,
        )
        addon_keymaps.append((km, kmi))

        # CMD-3: Cycle subd preview
        kmi = km.keymap_items.new(
            "nino.cycle_subsurf_preview",
            type="THREE",
            value="PRESS",
            oskey=True,
        )
        addon_keymaps.append((km, kmi))

        # CMD-SHIFT-D: Subdivide selection
        kmi = km.keymap_items.new(
            "nino.subdivide_selection",
            type="D",
            value="PRESS",
            oskey=True,
            shift=True,
        )
        addon_keymaps.append((km, kmi))

        # Backspace: Smart delete (in edit mode)
        km_mesh = kc.keymaps.new(name="Mesh", space_type="EMPTY")
        kmi = km_mesh.keymap_items.new(
            "nino.smart_delete",
            type="BACK_SPACE",
            value="PRESS",
        )
        addon_keymaps.append((km_mesh, kmi))


def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    display.unregister()

    for cls in reversed(_all_classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
