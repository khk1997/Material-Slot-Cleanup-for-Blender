bl_info = {
    "name": "Remove Unused Empty Materials",
    "author": "khk1997",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Properties > Material > Material Slot Cleanup",
    "description": "Remove unused and empty material slots from selected mesh objects.",
    "category": "Material",
}

import bpy
from bpy.props import BoolProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup


class MaterialSlotCleanupSettings(PropertyGroup):
    purge_orphan_data: BoolProperty(
        name="Purge Orphan Data",
        description="Also remove unused orphan data after cleaning material slots",
        default=True,
    )


def clean_material_slots(obj):
    mesh = obj.data
    used_indices = {polygon.material_index for polygon in mesh.polygons}
    old_materials = [slot.material for slot in obj.material_slots]
    keep_indices = [
        index
        for index, material in enumerate(old_materials)
        if material is not None and index in used_indices
    ]

    # If faces point only to empty slots, keep the first real material instead
    # of leaving the object with no material slots at all.
    if not keep_indices:
        for index, material in enumerate(old_materials):
            if material is not None:
                keep_indices = [index]
                break

    if len(keep_indices) == len(old_materials):
        return False

    index_map = {
        old_index: new_index
        for new_index, old_index in enumerate(keep_indices)
    }
    old_polygon_indices = [polygon.material_index for polygon in mesh.polygons]
    kept_materials = [old_materials[index] for index in keep_indices]

    mesh.materials.clear()
    for material in kept_materials:
        mesh.materials.append(material)

    for polygon, old_index in zip(mesh.polygons, old_polygon_indices):
        polygon.material_index = index_map.get(old_index, 0)

    return True


def purge_orphan_data():
    for _ in range(5):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True,
        )


class MATERIAL_OT_clean_unused_empty_slots(Operator):
    bl_idname = "material.clean_unused_empty_slots"
    bl_label = "Clean Material Slots"
    bl_description = "Clean unused and empty material slots on selected mesh objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_objects = list(context.selected_objects)
        active_object = context.view_layer.objects.active
        mesh_objects = [obj for obj in selected_objects if obj.type == "MESH"]

        if not mesh_objects:
            self.report({"WARNING"}, "No selected mesh objects to clean.")
            return {"CANCELLED"}

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")

        changed_count = 0
        for obj in mesh_objects:
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj

            if clean_material_slots(obj):
                changed_count += 1

        bpy.ops.object.select_all(action="DESELECT")
        for obj in selected_objects:
            if obj.name in context.scene.objects:
                obj.select_set(True)

        if active_object and active_object.name in context.scene.objects:
            context.view_layer.objects.active = active_object

        settings = context.scene.material_slot_cleanup_settings
        if settings.purge_orphan_data:
            purge_orphan_data()

        self.report(
            {"INFO"},
            f"Cleaned {changed_count} of {len(mesh_objects)} selected mesh object(s).",
        )
        return {"FINISHED"}


class MATERIAL_PT_slot_cleanup(Panel):
    bl_label = "Material Slot Cleanup"
    bl_idname = "MATERIAL_PT_slot_cleanup"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_order = -1

    def draw(self, context):
        layout = self.layout
        settings = context.scene.material_slot_cleanup_settings

        layout.prop(settings, "purge_orphan_data")
        layout.operator(
            MATERIAL_OT_clean_unused_empty_slots.bl_idname,
            icon="BRUSH_DATA",
        )


classes = (
    MaterialSlotCleanupSettings,
    MATERIAL_OT_clean_unused_empty_slots,
    MATERIAL_PT_slot_cleanup,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.material_slot_cleanup_settings = PointerProperty(
        type=MaterialSlotCleanupSettings,
    )


def unregister():
    del bpy.types.Scene.material_slot_cleanup_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
