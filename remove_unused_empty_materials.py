import bpy

# Keep current selection so we can restore it after cleanup.
selected_objects = list(bpy.context.selected_objects)
active_object = bpy.context.view_layer.objects.active

# Make sure we are in Object Mode.
if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode="OBJECT")

for obj in selected_objects:
    if obj.type != "MESH":
        continue

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Remove material slots that are not assigned to any faces.
    bpy.ops.object.material_slot_remove_unused()

    # Remove empty material slots with no material assigned.
    for index in reversed(range(len(obj.material_slots))):
        if obj.material_slots[index].material is None:
            obj.active_material_index = index
            bpy.ops.object.material_slot_remove()

# Restore original selection.
bpy.ops.object.select_all(action="DESELECT")
for obj in selected_objects:
    if obj.name in bpy.context.scene.objects:
        obj.select_set(True)

if active_object and active_object.name in bpy.context.scene.objects:
    bpy.context.view_layer.objects.active = active_object

# Purge unused orphan data.
# Repeat a few times because removing one data block can orphan another.
for _ in range(5):
    bpy.ops.outliner.orphans_purge(
        do_local_ids=True,
        do_linked_ids=True,
        do_recursive=True
    )

print("Done: removed unused material slots, empty material slots, and purged orphan data.")
