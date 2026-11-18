# [OWNER: M2] Script chuan hoa Blender MCP dung base_mannequin.glb (T-M2-01)
"""
Chay trong moi truong Blender 4.x (hoac thong qua Blender MCP `execute_blender_code`).
Tuan thu quy uoc dat ten bat buoc trong Muc 6 docs/system-design-spec.md:
- 11 Mesh & Material co bap doc lap
- Bo xuong: Armature_GymHuman
- Sockets: Socket_Hand_L, Socket_Hand_R, Socket_Back_Barbell, Floor_Origin
- Xuat .glb nen Draco (<= 25,000 triangles)
"""

MUSCLE_MESH_MATERIAL_PAIRS = [
    ("Mesh_Muscle_Chest", "Mat_Muscle_Chest"),
    ("Mesh_Muscle_Shoulders", "Mat_Muscle_Shoulders"),
    ("Mesh_Muscle_Biceps", "Mat_Muscle_Biceps"),
    ("Mesh_Muscle_Triceps", "Mat_Muscle_Triceps"),
    ("Mesh_Muscle_Back_Lats", "Mat_Muscle_Back_Lats"),
    ("Mesh_Muscle_Traps", "Mat_Muscle_Traps"),
    ("Mesh_Muscle_Abs_Core", "Mat_Muscle_Abs_Core"),
    ("Mesh_Muscle_Glutes", "Mat_Muscle_Glutes"),
    ("Mesh_Muscle_Quads", "Mat_Muscle_Quads"),
    ("Mesh_Muscle_Hamstrings", "Mat_Muscle_Hamstrings"),
    ("Mesh_Muscle_Calves", "Mat_Muscle_Calves"),
]

ARMATURE_NAME = "Armature_GymHuman"
REQUIRED_SOCKETS = [
    "Socket_Hand_L",
    "Socket_Hand_R",
    "Socket_Back_Barbell",
    "Floor_Origin",
]
REQUIRED_CLIPS = ["Anim_GoodForm", "Anim_BadForm"]


def export_draco_glb(filepath: str) -> None:
    import bpy  # type: ignore

    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format="GLB",
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_animations=True,
    )
