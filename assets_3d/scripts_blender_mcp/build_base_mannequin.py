# [OWNER: M2] Script chuan hoa Blender 5.3 / Blender MCP dung base_mannequin.glb (T-M2-01)
"""
Chay trong live Blender MCP (`execute_blender_code`) hoac Blender 5.3 CLI `--background --python`.
LUU Y: Tuyet doi KHONG goi `bpy.ops.wm.read_factory_settings(...)` de khong ngat ket noi Blender MCP.

Nguon hinh hoc: Blender Studio official CC0 Human Base Meshes (`GEO-body_male_realistic`).
Tu dong hoa qua bpy:
- Chuan hoa chieu cao 1.78m, ban chan cham Z=0.0, huong mat -Y (glTF +Z)
- Decimate doi xung X sang phong cach Low-Poly Anatomical Faceted (flat-shaded)
- Phan vung chinh xac 11 Mesh & Material co bap doc lap (`Mesh_Muscle_*` / `Mat_Muscle_*`)
- 2 Mesh khung trung tinh (`Body_Head_Neck`, `Body_Joints_Hands_Feet` -> `Mat_Body_Neutral`)
- Gan xuong tu dong (Automatic Heat Weights) tren luoi lien khoi truoc khi tach de 0 ho khop
- Bo xuong `Armature_GymHuman` + 4 Empty Sockets (`Socket_Hand_L/R`, `Socket_Back_Barbell`, `Floor_Origin`)
- Xuat `.glb` nen Draco level 6 (`<= 25,000 triangles`, `<= 2.0 MB`)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

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

DEFAULT_BUNDLE_PATH = Path(
    r"D:\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend"
)
LEGACY_BUNDLE_PATH = Path(
    r"C:\Users\tranh\Downloads\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend"
)


def resolve_bundle_path(bundle_path: str | Path | None = None) -> Path:
    """Resolve human_base_meshes_bundle.blend path from arg, env, or known local paths."""
    candidates: list[Path] = []
    if bundle_path is not None:
        candidates.append(Path(bundle_path))
    env_path = os.environ.get("VIGORAI_HUMAN_BUNDLE_PATH")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend([DEFAULT_BUNDLE_PATH, LEGACY_BUNDLE_PATH])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Khong tim thay human_base_meshes_bundle.blend tai cac duong dan: {[str(c) for c in candidates]}"
    )

# Linear RGBA conversions for VigorAI PBR colors
COLOR_MUSCLE_GREY = (0.341, 0.341, 0.341, 1.0)  # sRGB #9E9E9E
COLOR_BODY_NEUTRAL = (0.089, 0.105, 0.130, 1.0)  # sRGB #545B66

# Preview heatmap palette for visual inspection of muscle regions
HEATMAP_PREVIEW_COLORS = {
    "Mat_Muscle_Chest": (0.78, 0.04, 0.04, 1.0),       # Red #E53935
    "Mat_Muscle_Quads": (0.78, 0.04, 0.04, 1.0),       # Red #E53935
    "Mat_Muscle_Shoulders": (0.95, 0.26, 0.00, 1.0),   # Orange #FB8C00
    "Mat_Muscle_Triceps": (0.90, 0.12, 0.52, 1.0),     # Magenta preview tint (distinct from Shoulders)
    "Mat_Muscle_Hamstrings": (0.85, 0.20, 0.02, 1.0),  # Amber-Orange
    "Mat_Muscle_Abs_Core": (0.98, 0.68, 0.03, 1.0),    # Yellow #FDD835
    "Mat_Muscle_Biceps": (0.08, 0.42, 0.80, 1.0),      # Blue tint
    "Mat_Muscle_Back_Lats": (0.04, 0.45, 0.35, 1.0),   # Teal tint
    "Mat_Muscle_Traps": (0.32, 0.18, 0.65, 1.0),       # Purple tint
    "Mat_Muscle_Glutes": (0.78, 0.08, 0.28, 1.0),      # Crimson-Rose tint
    "Mat_Muscle_Calves": (0.06, 0.50, 0.18, 1.0),      # Green tint
}


def clear_scene_safely() -> None:
    """Xoa sach scene bang bpy.data.* ma khong reset Addon / Blender MCP socket."""
    import bpy  # type: ignore

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        if col != bpy.context.scene.collection:
            bpy.data.collections.remove(col)
    for bc in (
        bpy.data.meshes,
        bpy.data.armatures,
        bpy.data.materials,
        bpy.data.actions,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.images,
    ):
        for item in list(bc):
            try:
                bc.remove(item, do_unlink=True)
            except Exception:
                pass


def _ensure_collection(name: str):
    import bpy  # type: ignore

    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def _create_pbr_material(
    name: str,
    rgba: tuple[float, float, float, float],
    roughness: float = 0.55,
    metallic: float = 0.05,
):
    import bpy  # type: ignore

    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    if not getattr(mat, "use_nodes", True):
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        nt.nodes.clear()
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _load_and_normalize_base_mesh(
    bundle_path: Path,
    collection,
    mesh_object_name: str = "GEO-body_male_realistic",
    target_height: float = 1.78,
):
    import bpy  # type: ignore
    from mathutils import Vector  # type: ignore

    resolved = resolve_bundle_path(bundle_path)
    with bpy.data.libraries.load(str(resolved), link=False) as (df, dt):
        if mesh_object_name not in df.objects:
            raise ValueError(
                f"Khong tim thay '{mesh_object_name}' trong {resolved}"
            )
        dt.objects = [mesh_object_name]

    src_obj = dt.objects[0]
    collection.objects.link(src_obj)
    src_obj.name = "Mannequin_Unified"
    src_obj.modifiers.clear()
    src_obj.animation_data_clear()
    src_obj.data.materials.clear()

    # Clear drivers on object/mesh if any
    if src_obj.data.animation_data:
        src_obj.data.animation_data_clear()

    bpy.context.view_layer.objects.active = src_obj
    bpy.ops.object.select_all(action="DESELECT")
    src_obj.select_set(True)

    # Apply existing transform first, then center vertices strictly in mesh local space
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = src_obj.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    h = max(zs) - min(zs)
    scale = target_height / h
    cx = 0.5 * (min(xs) + max(xs))
    cy = 0.5 * (min(ys) + max(ys))
    cz = min(zs)
    for v in me.vertices:
        v.co = Vector(((v.co.x - cx) * scale, (v.co.y - cy) * scale, (v.co.z - cz) * scale))
    me.update()
    return src_obj


def _classify_polygon(
    sid: int,
    cx: float,
    cy: float,
    cz: float,
    nx: float,
    ny: float,
    nz: float,
) -> str:
    """Phan loai tung mat da giac vao dung 11 vung co bap hoac 2 phan khung trung tinh."""
    ax = abs(cx)

    # 1. Head & Neck (all cranial/face face sets + neck column above clavicle/collar)
    if sid in {2, 3, 4, 5, 7, 8, 22}:
        return "Mat_Body_Head_Neck_Tmp"
    if sid == 17:
        if cz >= 1.495 or (ax < 0.065 and cy < 0.030):
            return "Mat_Body_Head_Neck_Tmp"
    if cz >= 1.525:
        return "Mat_Body_Head_Neck_Tmp"

    # 2. Feet & Toes (neutral dark slate)
    if sid in {13, 14} or (25 <= sid <= 63) or cz < 0.155:
        return "Mat_Body_Neutral"

    # 3. Hands & Fingers (neutral dark slate)
    if sid in {9, 10} or sid >= 64:
        return "Mat_Body_Neutral"

    # 4. Forearms (neutral dark slate)
    if sid in {11, 12}:
        return "Mat_Body_Neutral"

    # 5. Lower Legs -> Calves (posterior gastrocnemius bulge) vs Shins (neutral)
    if sid in {15, 16} or (0.155 <= cz < 0.465 and ax > 0.06):
        y_shin = 0.094 - 0.049 * max(0.0, min(1.0, (cz - 0.092) / 0.398))
        if 0.175 <= cz < 0.458 and cy > y_shin + 0.012 and ny > -0.15:
            return "Mat_Muscle_Calves"
        return "Mat_Body_Neutral"

    # 6. Knee cap / joint ring -> neutral dark slate
    if 0.462 <= cz < 0.515 and ax < 0.24:
        return "Mat_Body_Neutral"

    # 7. Thighs -> Quads (anterior/outer) vs Hamstrings (posterior), keep narrow central groin neutral
    if sid in {23, 24} or (0.515 <= cz < 0.875 and ax < 0.23):
        if ax < 0.046 and cz > 0.770:
            return "Mat_Body_Neutral"
        y_thigh = 0.045 - 0.033 * max(0.0, min(1.0, (cz - 0.490) / 0.412))
        if cy <= y_thigh + 0.012:
            return "Mat_Muscle_Quads"
        return "Mat_Muscle_Hamstrings"

    # 8. Upper Arms -> Shoulders (deltoid cap) vs Biceps (anterior) vs Triceps (posterior)
    if sid in {20, 21}:
        if cz >= 1.325 or (ax >= 0.175 and cz >= 1.315):
            return "Mat_Muscle_Shoulders"
        if cz < 1.158:
            return "Mat_Body_Neutral"  # Elbow hinge
        if cy <= 0.028:
            return "Mat_Muscle_Biceps"
        return "Mat_Muscle_Triceps"

    # 9. Pelvis / Hips -> Glutes (posterior) vs V-line lower Abs (anterior) vs neutral briefs
    if sid == 18:
        if cy >= 0.022 and cz >= 0.825:
            return "Mat_Muscle_Glutes"
        if cz >= 0.905 and cy < 0.005 and ax <= 0.095 * max(0.0, (cz - 0.865) / 0.140):
            return "Mat_Muscle_Abs_Core"
        return "Mat_Body_Neutral"

    # 10. Waist / Mid-Core (`FS 19`) -> eliminate awkward horizontal lower-back gap
    if sid == 19:
        if cy >= 0.035:
            if cz >= 1.035:
                return "Mat_Muscle_Back_Lats"
            return "Mat_Muscle_Glutes"
        return "Mat_Muscle_Abs_Core"

    # 11. Upper Torso (`FS 1` & collar overlap of `FS 17`)
    # Deltoid transition on outer shoulder shelf
    if ax >= 0.155 and cz >= 1.345:
        return "Mat_Muscle_Shoulders"

    # Upper Trapezius collar flanking neck (visible cleanly from front & back)
    if cz >= 1.438 and ax >= 0.052 and ax < 0.155 and cy >= -0.045:
        return "Mat_Muscle_Traps"

    # Anterior Torso -> Chest (below clavicle line) vs Abs
    if cy <= 0.012:
        if cz >= 1.245 and cz < 1.438:
            return "Mat_Muscle_Chest"
        if cz < 1.245:
            return "Mat_Muscle_Abs_Core"
        return "Mat_Body_Neutral"

    # Posterior Torso -> Traps (upper diamond + collar) vs Back Lats (V-taper wings)
    if cz >= 1.280:
        if cz <= 1.445:
            trap_half_w = 0.035 + 0.105 * ((cz - 1.280) / 0.165)
        else:
            trap_half_w = 0.140 - 0.065 * min(1.0, (cz - 1.445) / 0.080)
        if ax <= trap_half_w:
            return "Mat_Muscle_Traps"
    if cz >= 1.035:
        return "Mat_Muscle_Back_Lats"
    return "Mat_Body_Neutral"


def _create_armature(collection, height_scale: float = 1.0):
    import bpy  # type: ignore
    from mathutils import Vector  # type: ignore

    arm_data = bpy.data.armatures.new(ARMATURE_NAME)
    arm_data.display_type = "STICK"
    arm_obj = bpy.data.objects.new(ARMATURE_NAME, arm_data)
    collection.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def sc(pt: tuple[float, float, float]) -> Vector:
        return Vector((pt[0] * height_scale, pt[1] * height_scale, pt[2] * height_scale))

    def add_bone(
        name: str,
        head: tuple[float, float, float],
        tail: tuple[float, float, float],
        parent_name: str | None,
        connected: bool = False,
        roll_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
    ):
        b = eb.new(name)
        b.head = sc(head)
        b.tail = sc(tail)
        if parent_name:
            b.parent = eb[parent_name]
            b.use_connect = connected
        b.align_roll(Vector(roll_axis))
        return b

    # Spine & Head matching measured GEO-body_male_realistic landmarks
    add_bone("Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.16), None, False, (1.0, 0.0, 0.0))
    add_bone("Pelvis", (0.0, 0.024, 0.900), (0.0, 0.020, 1.040), "Root", False, (1.0, 0.0, 0.0))
    add_bone("Spine_01", (0.0, 0.020, 1.040), (0.0, 0.015, 1.185), "Pelvis", True, (1.0, 0.0, 0.0))
    add_bone("Spine_02", (0.0, 0.015, 1.185), (0.0, -0.005, 1.335), "Spine_01", True, (1.0, 0.0, 0.0))
    add_bone("Spine_03", (0.0, -0.005, 1.335), (0.0, 0.004, 1.481), "Spine_02", True, (1.0, 0.0, 0.0))
    add_bone("Neck", (0.0, 0.004, 1.481), (0.0, -0.020, 1.575), "Spine_03", True, (1.0, 0.0, 0.0))
    add_bone("Head", (0.0, -0.020, 1.575), (0.0, -0.040, 1.775), "Neck", True, (1.0, 0.0, 0.0))

    # Arms
    for side, sx in (("L", 1.0), ("R", -1.0)):
        add_bone(
            f"Clavicle_{side}",
            (sx * 0.035, -0.005, 1.435),
            (sx * 0.198, 0.027, 1.425),
            "Spine_03",
            False,
            (0.0, -1.0, 0.0),
        )
        add_bone(
            f"UpperArm_{side}",
            (sx * 0.198, 0.027, 1.425),
            (sx * 0.307, 0.035, 1.156),
            f"Clavicle_{side}",
            True,
            (0.0, -1.0, 0.0),
        )
        add_bone(
            f"Forearm_{side}",
            (sx * 0.307, 0.035, 1.156),
            (sx * 0.397, -0.036, 0.928),
            f"UpperArm_{side}",
            True,
            (0.0, -1.0, 0.0),
        )
        add_bone(
            f"Hand_{side}",
            (sx * 0.397, -0.036, 0.928),
            (sx * 0.432, -0.095, 0.810),
            f"Forearm_{side}",
            True,
            (0.0, -1.0, 0.0),
        )

    # Legs
    for side, sx in (("L", 1.0), ("R", -1.0)):
        add_bone(
            f"Thigh_{side}",
            (sx * 0.112, 0.012, 0.902),
            (sx * 0.132, 0.045, 0.490),
            "Pelvis",
            False,
            (1.0, 0.0, 0.0),
        )
        add_bone(
            f"Calf_{side}",
            (sx * 0.132, 0.045, 0.490),
            (sx * 0.160, 0.094, 0.092),
            f"Thigh_{side}",
            True,
            (1.0, 0.0, 0.0),
        )
        add_bone(
            f"Foot_{side}",
            (sx * 0.160, 0.094, 0.092),
            (sx * 0.162, -0.080, 0.018),
            f"Calf_{side}",
            True,
            (1.0, 0.0, 0.0),
        )

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def _create_sockets(collection, arm_obj, height_scale: float = 1.0) -> dict[str, object]:
    import bpy  # type: ignore
    from mathutils import Matrix  # type: ignore

    sockets = {}

    def add_socket(name: str, world_pos: tuple[float, float, float], bone_name: str | None):
        scaled = (
            world_pos[0] * height_scale,
            world_pos[1] * height_scale,
            world_pos[2] * height_scale,
        )
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 0.06
        collection.objects.link(empty)
        if bone_name is not None:
            empty.parent = arm_obj
            empty.parent_type = "BONE"
            empty.parent_bone = bone_name
            bpy.context.view_layer.update()
            empty.matrix_world = Matrix.Translation(scaled)
        else:
            empty.location = scaled
        sockets[name] = empty
        return empty

    add_socket("Socket_Hand_L", (0.415, -0.078, 0.855), "Hand_L")
    add_socket("Socket_Hand_R", (-0.415, -0.078, 0.855), "Hand_R")
    add_socket("Socket_Back_Barbell", (0.0, 0.115, 1.445), "Spine_03")
    add_socket("Floor_Origin", (0.0, 0.0, 0.0), None)
    return sockets


def _ensure_fallback_weights(mesh_obj, arm_obj) -> int:
    """Bao dam 100% vertex co it nhat 1 bone weight hop le neu ARMATURE_AUTO bo sot."""
    from mathutils import Vector  # type: ignore

    me = mesh_obj.data
    bone_segments = []
    for b in arm_obj.data.bones:
        if b.name == "Root":
            continue
        p0 = arm_obj.matrix_world @ b.head_local
        p1 = arm_obj.matrix_world @ b.tail_local
        bone_segments.append((b.name, p0, p1))

    fixed = 0
    for v in me.vertices:
        total = sum(g.weight for g in v.groups)
        if total > 1e-4:
            continue
        pos = mesh_obj.matrix_world @ v.co
        best_bone = "Pelvis"
        best_dist = 1e9
        for bname, p0, p1 in bone_segments:
            seg = p1 - p0
            seg_len_sq = seg.length_squared
            t = 0.0 if seg_len_sq < 1e-9 else max(0.0, min(1.0, (pos - p0).dot(seg) / seg_len_sq))
            proj = p0 + seg * t
            d = (pos - proj).length
            if d < best_dist:
                best_dist = d
                best_bone = bname
        vg = mesh_obj.vertex_groups.get(best_bone) or mesh_obj.vertex_groups.new(name=best_bone)
        vg.add([v.index], 1.0, "REPLACE")
        fixed += 1
    return fixed


def set_heatmap_preview_colors(enabled: bool = True) -> None:
    """Doi mau 11 Mat_Muscle_* sang bang mau Heatmap mau (de kiem tra ranh gioi) hoac ve Xam chuan."""
    import bpy  # type: ignore

    for _, mat_name in MUSCLE_MESH_MATERIAL_PAIRS:
        mat = bpy.data.materials.get(mat_name)
        if mat and mat.node_tree:
            bsdf = next(
                (n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
                None,
            )
            if bsdf:
                rgba = HEATMAP_PREVIEW_COLORS[mat_name] if enabled else COLOR_MUSCLE_GREY
                bsdf.inputs["Base Color"].default_value = rgba


def build_mannequin(
    blend_path: str | Path | None = None,
    glb_paths: Iterable[str | Path] = (),
    bundle_path: Path | None = None,
    decimate_ratio: float = 0.56,
    keep_heatmap_preview: bool = False,
    mesh_object_name: str = "GEO-body_male_realistic",
    target_height: float = 1.78,
    use_draco: bool = False,
) -> dict:
    """Dung hoan chinh Base Mannequin Low-Poly Anatomical Faceted tu Blender Human Base Meshes."""
    import bpy  # type: ignore
    import bmesh  # type: ignore
    from mathutils.kdtree import KDTree  # type: ignore

    clear_scene_safely()
    col = _ensure_collection("VigorAI_Mannequin")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 90

    resolved_bundle = resolve_bundle_path(bundle_path)
    height_scale = target_height / 1.78

    # 1. Load & normalize official Blender Human Base Mesh
    unified = _load_and_normalize_base_mesh(
        resolved_bundle,
        col,
        mesh_object_name=mesh_object_name,
        target_height=target_height,
    )
    orig_me = unified.data

    # Build KDTree of original polygon centers -> original .sculpt_face_set ID
    orig_fs = orig_me.attributes.get(".sculpt_face_set")
    kd = KDTree(len(orig_me.polygons))
    orig_sids = []
    for i, poly in enumerate(orig_me.polygons):
        kd.insert(poly.center, i)
        orig_sids.append(orig_fs.data[i].value if orig_fs else 1)
    kd.balance()

    # 2. Decimate symmetrically to Low-Poly Anatomical Faceted (~11k - 13k triangles)
    bpy.ops.object.select_all(action="DESELECT")
    unified.select_set(True)
    bpy.context.view_layer.objects.active = unified

    dec = unified.modifiers.new(name="Decimate_LowPoly", type="DECIMATE")
    dec.decimate_type = "COLLAPSE"
    dec.ratio = decimate_ratio
    dec.use_symmetry = True
    dec.symmetry_axis = "X"
    bpy.ops.object.modifier_apply(modifier=dec.name)

    # Clean tiny seam duplicates & recalculate outward normals before skinning
    bm = bmesh.new()
    bm.from_mesh(unified.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(unified.data)
    bm.free()

    # Enforce strict Flat Shading (Low-Poly Faceted look)
    me = unified.data
    if len(me.polygons) > 0:
        me.polygons.foreach_set("use_smooth", [False] * len(me.polygons))
    me.update()

    # 3. Create all 11 muscle materials + temporary head/neck + neutral body material
    mat_slots_order = [mat_name for _, mat_name in MUSCLE_MESH_MATERIAL_PAIRS] + [
        "Mat_Body_Head_Neck_Tmp",
        "Mat_Body_Neutral",
    ]
    mat_name_to_obj = {}
    for mname in mat_slots_order:
        rgba = COLOR_BODY_NEUTRAL if "Body_" in mname else COLOR_MUSCLE_GREY
        mat_obj = _create_pbr_material(mname, rgba, roughness=0.55, metallic=0.05)
        me.materials.append(mat_obj)
        mat_name_to_obj[mname] = mat_obj

    slot_index = {mname: idx for idx, mname in enumerate(mat_slots_order)}

    # Assign each decimated polygon cleanly using original face-set + normalized anatomical rules
    inv_scale = 1.0 / height_scale if height_scale > 0 else 1.0
    for poly in me.polygons:
        _, orig_idx, _ = kd.find(poly.center)
        sid = orig_sids[orig_idx]
        c = poly.center
        n = poly.normal
        target_mat = _classify_polygon(
            sid,
            c.x * inv_scale,
            c.y * inv_scale,
            c.z * inv_scale,
            n.x,
            n.y,
            n.z,
        )
        poly.material_index = slot_index[target_mat]
    me.update()

    # 4. Create Armature_GymHuman and bind unified watertight mesh via Automatic Heat Weights
    arm_obj = _create_armature(col, height_scale=height_scale)
    bpy.ops.object.select_all(action="DESELECT")
    unified.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")

    fixed_verts = _ensure_fallback_weights(unified, arm_obj)
    if fixed_verts > 0:
        print(f"[VigorAI] Fallback nearest-bone weights assigned to {fixed_verts} vertices")

    # 5. Separate unified skinned mesh by material into 13 seamless objects
    bpy.ops.object.select_all(action="DESELECT")
    unified.select_set(True)
    bpy.context.view_layer.objects.active = unified
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.separate(type="MATERIAL")
    bpy.ops.object.mode_set(mode="OBJECT")

    mat_to_mesh_name = {mat_name: mesh_name for mesh_name, mat_name in MUSCLE_MESH_MATERIAL_PAIRS}
    mat_to_mesh_name["Mat_Body_Head_Neck_Tmp"] = "Body_Head_Neck"
    mat_to_mesh_name["Mat_Body_Neutral"] = "Body_Joints_Hands_Feet"

    mat_neutral = mat_name_to_obj["Mat_Body_Neutral"]
    tmp_head_mat = mat_name_to_obj["Mat_Body_Head_Neck_Tmp"]

    for obj in list(bpy.data.objects):
        if obj.type != "MESH" or not obj.data.materials:
            continue
        obj.data.validate(verbose=False)
        obj.data.update()
        mname = obj.data.materials[0].name
        canonical = mat_to_mesh_name.get(mname)
        if canonical:
            obj.name = canonical
            obj.data.name = canonical
        if mname == "Mat_Body_Head_Neck_Tmp":
            obj.data.materials[0] = mat_neutral

    if tmp_head_mat.users == 0:
        bpy.data.materials.remove(tmp_head_mat)

    # 6. Create 4 Empty Sockets parented to bones
    _create_sockets(col, arm_obj, height_scale=height_scale)
    bpy.context.view_layer.update()

    total_tris = sum(
        sum(max(0, len(p.vertices) - 2) for p in obj.data.polygons)
        for obj in bpy.data.objects
        if obj.type == "MESH"
    )
    print(f"[VigorAI] Seamless Base Mannequin ({mesh_object_name}) built: {total_tris} triangles across {sum(1 for o in bpy.data.objects if o.type == 'MESH')} meshes")

    if keep_heatmap_preview:
        set_heatmap_preview_colors(True)
    else:
        set_heatmap_preview_colors(False)

    if blend_path is not None:
        blend_path = Path(blend_path)
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        print(f"[VigorAI] Saved .blend -> {blend_path}")

    for glb_out in glb_paths:
        export_draco_glb(str(glb_out), use_draco=use_draco)

    return {"total_triangles": total_tris}


def export_draco_glb(filepath: str, use_draco: bool = False) -> None:
    import bpy  # type: ignore

    out = Path(filepath)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(out),
        export_format="GLB",
        export_draco_mesh_compression_enable=use_draco,
        export_texcoords=False,
        export_tangents=False,
        export_normals=True,
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_force_sampling=False,
        export_skins=True,
        export_apply=False,
    )
    print(f"[VigorAI] Exported Binary glTF .glb -> {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    preview = bool(os.environ.get("VIGORAI_HEATMAP_PREVIEW"))
    use_draco = bool(os.environ.get("VIGORAI_USE_DRACO"))

    # 1. Male Mannequin (1.78m)
    build_mannequin(
        blend_path=repo_root / "assets_3d" / "source_blend" / "base_mannequin.blend",
        glb_paths=[
            repo_root / "assets_3d" / "exported_glb" / "base_mannequin.glb",
            repo_root / "mobile" / "assets" / "3d_bundled" / "base_mannequin.glb",
        ],
        mesh_object_name="GEO-body_male_realistic",
        target_height=1.78,
        keep_heatmap_preview=preview,
        use_draco=use_draco,
    )

    # 2. Female Mannequin (1.66m) for Body Avatar F13
    build_mannequin(
        blend_path=repo_root / "assets_3d" / "source_blend" / "base_mannequin_female.blend",
        glb_paths=[
            repo_root / "assets_3d" / "exported_glb" / "base_mannequin_female.glb",
            repo_root / "mobile" / "assets" / "3d_bundled" / "base_mannequin_female.glb",
        ],
        mesh_object_name="GEO-body_female_realistic",
        target_height=1.66,
        keep_heatmap_preview=preview,
        use_draco=use_draco,
    )
