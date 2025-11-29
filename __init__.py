"""
Nino's Tools - A Blender addon for subdivision surface management and more.
"""

bl_info = {
    "name": "Nino's Tools",
    "author": "Nino",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel > Nino's Tools",
    "description": "Collection of helpful modeling tools",
    "category": "3D View",
}

import bpy


# Utility function to get or create subdivision surface modifier
def get_or_create_subsurf(obj, default_viewport_level=2, default_render_level=2):
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
    subsurf_mods = [mod for mod in obj.modifiers if mod.type == 'SUBSURF']

    if subsurf_mods:
        # Use the last one
        return subsurf_mods[-1]
    else:
        # Create a new one
        mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
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
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                mod = get_or_create_subsurf(obj, default_viewport_level=2, default_render_level=2)
                mod.levels -= 1
                processed_count += 1

        if processed_count > 0:
            self.report({'INFO'}, f"Decreased subd level for {processed_count} object(s)")
        else:
            self.report({'WARNING'}, "No mesh objects selected")

        return {'FINISHED'}


class NINO_OT_increase_subsurf_level(bpy.types.Operator):
    """Increase subdivision surface viewport level by 1"""
    bl_idname = "nino.increase_subsurf_level"
    bl_label = "Increase Subd Level"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                mod = get_or_create_subsurf(obj, default_viewport_level=1, default_render_level=2)
                mod.levels += 1
                processed_count += 1

        if processed_count > 0:
            self.report({'INFO'}, f"Increased subd level for {processed_count} object(s)")
        else:
            self.report({'WARNING'}, "No mesh objects selected")

        return {'FINISHED'}


class NINO_OT_cycle_subsurf_preview(bpy.types.Operator):
    """Cycle subdivision surface preview mode (on cage / edit mode)"""
    bl_idname = "nino.cycle_subsurf_preview"
    bl_label = "Cycle Subd Preview"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        processed_count = 0

        for obj in context.selected_objects:
            if obj.type == 'MESH':
                mod = get_or_create_subsurf(obj, default_viewport_level=2, default_render_level=2)

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
            self.report({'INFO'}, f"Cycled subd preview for {processed_count} object(s)")
        else:
            self.report({'WARNING'}, "No mesh objects selected")

        return {'FINISHED'}


class NINO_PT_tools_panel(bpy.types.Panel):
    """Creates a Panel in the N-panel"""
    bl_label = "Nino's Tools"
    bl_idname = "NINO_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Nino's Tools"

    def draw(self, context):
        layout = self.layout

        # Subd tools section
        box = layout.box()
        box.label(text="Subd Tools", icon='MOD_SUBSURF')

        col = box.column(align=True)
        col.operator("nino.decrease_subsurf_level", text="Decrease Subd Level")
        col.operator("nino.increase_subsurf_level", text="Increase Subd Level")
        col.operator("nino.cycle_subsurf_preview", text="Cycle Subd Preview")


# Keymap storage
addon_keymaps = []


def register():
    bpy.utils.register_class(NINO_OT_decrease_subsurf_level)
    bpy.utils.register_class(NINO_OT_increase_subsurf_level)
    bpy.utils.register_class(NINO_OT_cycle_subsurf_preview)
    bpy.utils.register_class(NINO_PT_tools_panel)

    # Add keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')

        # CMD-1: Decrease subd level
        kmi = km.keymap_items.new(
            NINO_OT_decrease_subsurf_level.bl_idname,
            type='ONE',
            value='PRESS',
            oskey=True  # oskey is CMD on macOS
        )
        addon_keymaps.append((km, kmi))

        # CMD-2: Increase subd level
        kmi = km.keymap_items.new(
            NINO_OT_increase_subsurf_level.bl_idname,
            type='TWO',
            value='PRESS',
            oskey=True
        )
        addon_keymaps.append((km, kmi))

        # CMD-3: Cycle subd preview
        kmi = km.keymap_items.new(
            NINO_OT_cycle_subsurf_preview.bl_idname,
            type='THREE',
            value='PRESS',
            oskey=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(NINO_PT_tools_panel)
    bpy.utils.unregister_class(NINO_OT_cycle_subsurf_preview)
    bpy.utils.unregister_class(NINO_OT_increase_subsurf_level)
    bpy.utils.unregister_class(NINO_OT_decrease_subsurf_level)


if __name__ == "__main__":
    register()
