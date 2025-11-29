import bpy

for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.data.materials.clear()


material = bpy.data.materials.get("Nothing")

for obj in bpy.data.objects:
    if obj.type == "MESH":
        if len(obj.data.materials) == 0:
            obj.data.materials.append(material)
        else:
            for i in range(len(obj.data.materials)):
                obj.data.materials[i] = material
