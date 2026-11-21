# [OWNER: M2] Script Blender 5.3 / Blender MCP dung bo bai tap 3D Sprint 2 (T-M2-07: F07, F10, F12)
"""
Hien thuc hoa quy trinh Sprint 2 theo gym.txt & system-design-spec.md:
- Phase 1 (Kiem thu Nhom co Nguc - Chest):
  1. BARBELL_BENCH_PRESS     -> barbell_bench_press.glb     (Equip_Barbell + Equip_Bench 0 deg)
  2. INCLINE_DUMBBELL_PRESS  -> incline_dumbbell_press.glb  (2x Equip_Dumbbell + Equip_Bench_Incline 30 deg)
  3. CABLE_CHEST_FLY         -> cable_chest_fly.glb         (Equip_CableMachine + 2x Handles & Dynamic Cables)
- Phase 2 (Nhom co Xo - Lats):
  4. WIDE_GRIP_PULLUP            -> wide_grip_pullup.glb            (Equip_PullupRack + Kipping BadForm)
  5. LAT_PULLDOWN                -> lat_pulldown.glb                (Equip_LatMachine + Equip_LatBar + Dynamic Cable)
  6. STRAIGHT_ARM_CABLE_PULLDOWN -> straight_arm_cable_pulldown.glb (Equip_CableTower + Equip_StraightBar + Dynamic Cable)
- Phase 3 (Nhom co Lung giua & Lung duoi - Mid & Lower Back):
  7. BARBELL_BENT_OVER_ROW       -> barbell_bent_over_row.glb       (Equip_Barbell + Gap nguoi keo ta)
  8. SEATED_CABLE_ROW            -> seated_cable_row.glb            (Equip_SeatedRowMachine + Equip_VHandle + Dynamic Cable)
  9. BARBELL_DEADLIFT            -> barbell_deadlift.glb            (Equip_Barbell + Conventional Deadlift)
- Phase 4 (Nhom co Vai - Shoulders):
  10. DUMBBELL_SHOULDER_PRESS    -> dumbbell_shoulder_press.glb     (2x Equip_Dumbbell + Equip_Bench_Upright80 80 deg)
  11. DUMBBELL_LATERAL_RAISE     -> dumbbell_lateral_raise.glb      (2x Equip_Dumbbell + Dang ta ngang)
  12. CABLE_FACE_PULL            -> cable_face_pull.glb             (Equip_CableTower_FacePull + 2-Nhanh Rope & Knobs)
- Phase 5 (Nhom co Tay truoc - Biceps):
  13. BARBELL_BICEP_CURL         -> barbell_bicep_curl.glb          (Equip_Barbell + Dung cuon ta don)
  14. DUMBBELL_HAMMER_CURL       -> dumbbell_hammer_curl.glb        (2x Equip_Dumbbell + Cuon kieu bua)
  15. INCLINE_DUMBBELL_CURL      -> incline_dumbbell_curl.glb       (2x Equip_Dumbbell + Equip_Bench_Incline45 45 deg)
- Phase 6 (Nhom co Tay sau - Triceps):
  16. CABLE_TRICEP_PUSHDOWN      -> cable_tricep_pushdown.glb       (Equip_CableTower_FacePull + 2-Nhanh Rope & Knobs)
  17. SKULL_CRUSHER              -> skull_crusher.glb               (Equip_Bench + Equip_Barbell ha qua tran)
  18. OVERHEAD_DUMBBELL_TRICEP_EXT -> overhead_dumbbell_tricep_ext.glb (Equip_Dumbbell dung thang sau dau)
- Phase 7 (Nhom co Dui truoc - Quadriceps):
  19. BARBELL_SQUAT              -> barbell_squat.glb               (Equip_SquatRack + Equip_Barbell + Squat chuan)
  20. LEG_PRESS                  -> leg_press.glb                   (Equip_LegPressMachine + Equip_LegPressSled 40 deg)
  21. LEG_EXTENSION              -> leg_extension.glb               (Equip_LegExtMachine + Equip_LegExtArm pivot goi)
- Phase 8 (Nhom co Dui sau - Hamstrings):
  22. ROMANIAN_DEADLIFT          -> romanian_deadlift.glb           (Equip_Barbell + Hip Hinge goc goi ~15 deg)
  23. LEG_CURL_MACHINE           -> leg_curl_machine.glb            (Equip_LyingCurlMachine + Equip_LyingCurlArm)
  24. SEATED_LEG_CURL            -> seated_leg_curl.glb             (Equip_SeatedCurlMachine + Dem khoa dui + Con lan Achilles)
- Phase 9 (Nhom co Mong - Glutes):
  25. BARBELL_HIP_THRUST         -> barbell_hip_thrust.glb          (Equip_HipThrustBench + Equip_Barbell tren hong)
  26. WALKING_LUNGE              -> walking_lunge.glb               (2x Equip_Dumbbell + Chung chan 90-90 deg)
  27. CABLE_GLUTE_KICKBACK       -> cable_glute_kickback.glb        (Equip_CableTower_Kickback + AnkleStrap + Cap dong)
- Phase 10 (Nhom co Bung & Loi - Abs & Core):
  28. HANGING_LEG_RAISE          -> hanging_leg_raise.glb           (Equip_PullupRack + Treo nguoi nang chan)
  29. CABLE_CRUNCH               -> cable_crunch.glb                (Equip_CableTower_FacePull + Rope + Tham quy)
  30. PLANK                      -> plank.glb                       (Equip_Mat + Chong khuyu tay giu thang)

Quy chuan bat buoc:
- KHONG goi bpy.ops.wm.read_factory_settings(...) (dung clear_scene_safely cua build_base_mannequin)
- Giu nguyen 11 Mesh & Material (`Mesh_Muscle_*` / `Mat_Muscle_*`) + `Armature_GymHuman` + 4 Sockets
- Moi bai co du 2 animation clips: `Anim_GoodForm` & `Anim_BadForm` (30 FPS, 100 frames)
- Kiem tra header .glb (`<= 25,000 tris`, du 11 Mat_Muscle_*, du 2 clips) va cap nhat SHA-256 vao:
  + `assets_3d/exported_glb/assets_manifest.json`
  + `mobile/assets/mock_json/mock_m2_exercises.json`
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import struct
import sys
from pathlib import Path
from typing import Callable

from mathutils import Euler, Matrix, Quaternion, Vector  # type: ignore

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import build_base_mannequin as base_mod

STEEL_COLOR = (0.58, 0.62, 0.68, 1.0)
DARK_STEEL_COLOR = (0.14, 0.16, 0.19, 1.0)
PLATE_IRON_COLOR = (0.045, 0.052, 0.065, 1.0)
PLATE_ACCENT_COLOR = (0.65, 0.08, 0.08, 1.0)
BENCH_FRAME_COLOR = (0.04, 0.045, 0.055, 1.0)
PAD_COLOR = (0.025, 0.030, 0.040, 1.0)
CABLE_COLOR = (0.03, 0.035, 0.042, 1.0)

CHEST_PREVIEW_COLORS = {
    "Mat_Muscle_Chest": (0.898, 0.224, 0.208, 1.0),      # #E53935 Primary Red
    "Mat_Muscle_Shoulders": (0.984, 0.549, 0.000, 1.0),  # #FB8C00 Secondary Orange
    "Mat_Muscle_Triceps": (0.984, 0.549, 0.000, 1.0),    # #FB8C00 Secondary Orange
    "Mat_Muscle_Abs_Core": (0.992, 0.847, 0.208, 1.0),   # #FDD835 Stabilizer Yellow
}


def apply_exercise_muscle_preview(
    primary: list[str],
    secondary: list[str],
    stabilizer: list[str],
    enabled: bool = True,
) -> None:
    """To mau heatmap theo bai tap de kiem tra truc quan trong Blender MCP `look`, hoac reset ve xam chuan."""
    import bpy  # type: ignore

    for _, mat_name in base_mod.MUSCLE_MESH_MATERIAL_PAIRS:
        mat = bpy.data.materials.get(mat_name)
        if not mat or not mat.node_tree:
            continue
        bsdf = next(
            (n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
            None,
        )
        if not bsdf:
            continue
        if not enabled:
            rgba = base_mod.COLOR_MUSCLE_GREY
        elif mat_name in primary:
            rgba = (0.78, 0.04, 0.04, 1.0)   # Linear approx #E53935
        elif mat_name in secondary:
            rgba = (0.95, 0.26, 0.00, 1.0)   # Linear approx #FB8C00
        elif mat_name in stabilizer:
            rgba = (0.98, 0.68, 0.03, 1.0)   # Linear approx #FDD835
        else:
            rgba = base_mod.COLOR_MUSCLE_GREY
        bsdf.inputs["Base Color"].default_value = rgba


# ---------------------------------------------------------------------------
# Geometric Mesh Primitives & Modular Gym Equipment Builders (F12)
# ---------------------------------------------------------------------------
def _create_equip_cylinder(
    bm,
    p0: Vector,
    p1: Vector,
    radius: float,
    segs: int = 12,
    cap_ends: bool = True,
) -> set:
    import bmesh  # type: ignore

    axis = p1 - p0
    length = axis.length
    if length < 1e-6:
        return set()
    prev = set(bm.faces)
    rot = axis.to_track_quat("Z", "Y").to_matrix().to_4x4()
    mid = 0.5 * (p0 + p1)
    mat = Matrix.Translation(mid) @ rot
    bmesh.ops.create_cone(
        bm,
        cap_ends=cap_ends,
        cap_tris=False,
        segments=segs,
        radius1=radius,
        radius2=radius,
        depth=length,
        matrix=mat,
    )
    return set(bm.faces) - prev


def _create_equip_box(
    bm,
    center: tuple[float, float, float],
    size: tuple[float, float, float],
    rot_matrix: Matrix | None = None,
) -> set:
    import bmesh  # type: ignore

    prev = set(bm.faces)
    rot = rot_matrix if rot_matrix is not None else Matrix.Identity(4)
    mat = Matrix.Translation(center) @ rot @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    return set(bm.faces) - prev


def _finalize_equip_mesh(
    bm,
    collection,
    name: str,
    materials: list,
    face_groups: list[tuple[set, int]],
):
    import bpy  # type: ignore
    import bmesh  # type: ignore

    face_to_slot: dict = {}
    for face_set, slot_idx in face_groups:
        for f in face_set:
            face_to_slot[f] = slot_idx

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for mat in materials:
        mesh.materials.append(mat)

    # Note: bm faces map 1-to-1 by index to mesh.polygons before bm.free(),
    # so re-build index lookup cleanly via center/order when needed:
    # Actually assign material_index inside bmesh via `f.material_index = slot_idx` BEFORE to_mesh!
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def _assign_bmesh_materials(bm, face_groups: list[tuple[set, int]]) -> None:
    for face_set, slot_idx in face_groups:
        for f in face_set:
            if f.is_valid:
                f.material_index = slot_idx


def _bmesh_to_object(bm, collection, name: str, materials: list):
    import bpy  # type: ignore
    import bmesh  # type: ignore

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for mat in materials:
        mesh.materials.append(mat)
    for poly in mesh.polygons:
        poly.use_smooth = False
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def _build_barbell_object(collection, name: str = "Equip_Barbell"):
    """Olympic Barbell + banh ta Low-Poly (~600 tris, tam thanh don tai (0,0,0) doc truc X)."""
    import bmesh  # type: ignore

    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_iron = base_mod._create_pbr_material("Mat_Equip_Iron", PLATE_IRON_COLOR, roughness=0.45, metallic=0.80)
    mat_collar = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    steel_faces = _create_equip_cylinder(bm, Vector((-0.68, 0.0, 0.0)), Vector((0.68, 0.0, 0.0)), 0.015, 10)
    for sx in (-1.0, 1.0):
        steel_faces |= _create_equip_cylinder(bm, Vector((sx * 0.67, 0.0, 0.0)), Vector((sx * 1.03, 0.0, 0.0)), 0.025, 10)

    plate_faces = set()
    collar_faces = set()
    for sx in (-1.0, 1.0):
        plate_faces |= _create_equip_cylinder(bm, Vector((sx * 0.70, 0.0, 0.0)), Vector((sx * 0.75, 0.0, 0.0)), 0.215, 16)
        plate_faces |= _create_equip_cylinder(bm, Vector((sx * 0.76, 0.0, 0.0)), Vector((sx * 0.80, 0.0, 0.0)), 0.165, 16)
        collar_faces |= _create_equip_cylinder(bm, Vector((sx * 0.805, 0.0, 0.0)), Vector((sx * 0.84, 0.0, 0.0)), 0.042, 12)

    _assign_bmesh_materials(bm, [(steel_faces, 0), (plate_faces, 1), (collar_faces, 2)])
    return _bmesh_to_object(bm, collection, name, [mat_steel, mat_iron, mat_collar])


def _build_dumbbell_object(collection, name: str = "Equip_Dumbbell"):
    """Ta don luc giac Low-Poly (~220 tris, tam tay nam tai (0,0,0) doc truc X)."""
    import bmesh  # type: ignore

    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_iron = base_mod._create_pbr_material("Mat_Equip_Iron", PLATE_IRON_COLOR, roughness=0.45, metallic=0.80)
    mat_collar = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    # Handle shaft along X: -0.075 .. +0.075
    handle_faces = _create_equip_cylinder(bm, Vector((-0.075, 0.0, 0.0)), Vector((0.075, 0.0, 0.0)), 0.016, 10)
    head_faces = set()
    ring_faces = set()
    for sx in (-1.0, 1.0):
        ring_faces |= _create_equip_cylinder(bm, Vector((sx * 0.070, 0.0, 0.0)), Vector((sx * 0.082, 0.0, 0.0)), 0.025, 8)
        head_faces |= _create_equip_cylinder(bm, Vector((sx * 0.082, 0.0, 0.0)), Vector((sx * 0.150, 0.0, 0.0)), 0.078, 8)
        head_faces |= _create_equip_cylinder(bm, Vector((sx * 0.150, 0.0, 0.0)), Vector((sx * 0.162, 0.0, 0.0)), 0.068, 8)

    _assign_bmesh_materials(bm, [(handle_faces, 0), (head_faces, 1), (ring_faces, 2)])
    return _bmesh_to_object(bm, collection, name, [mat_steel, mat_iron, mat_collar])


def _build_flat_bench_object(collection, name: str = "Equip_Bench"):
    """Ghe Bench phang 0 deg dat tai Floor_Origin (mat dem top Z = 0.43)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)

    bm = bmesh.new()
    pad_faces = _create_equip_box(bm, (0.0, 0.14, 0.395), (0.30, 1.08, 0.07))
    frame_faces = set()
    frame_faces |= _create_equip_box(bm, (0.0, 0.14, 0.33), (0.08, 0.94, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -0.26, 0.175), (0.07, 0.07, 0.33))
    frame_faces |= _create_equip_box(bm, (0.0, 0.52, 0.175), (0.07, 0.07, 0.33))
    frame_faces |= _create_equip_box(bm, (0.0, -0.26, 0.025), (0.46, 0.08, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.52, 0.025), (0.46, 0.08, 0.05))

    _assign_bmesh_materials(bm, [(frame_faces, 0), (pad_faces, 1)])
    obj = _bmesh_to_object(bm, collection, name, [mat_frame, mat_pad])
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


def _build_incline_bench_object(collection, name: str = "Equip_Bench_Incline", angle_deg: float = 30.0):
    """Ghe Incline Bench 30 deg chuan phong Gym dat tai Floor_Origin."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)

    rad = math.radians(angle_deg)
    # Mat tua lung huong doc len theo vector (0, cos(30), sin(30)), mat tren huong ve (0, -sin(30), cos(30))
    hinge_top = Vector((0.0, -0.05, 0.42))
    axis_up_pad = Vector((0.0, math.cos(rad), math.sin(rad)))
    normal_pad = Vector((0.0, -math.sin(rad), math.cos(rad)))
    pad_len = 0.84
    pad_thick = 0.065
    pad_center = hinge_top + axis_up_pad * (0.5 * pad_len) - normal_pad * (0.5 * pad_thick)
    # Rotation around X by +angle_deg tilts local +Y toward +Z and local +Z toward -Y
    rot_back = Matrix.Rotation(rad, 4, "X")

    # Dem ngoi ngan phia truoc (Y = -0.35 .. -0.06, hoi nghieng 8 deg giu hong)
    seat_rad = math.radians(-8.0)
    rot_seat = Matrix.Rotation(seat_rad, 4, "X")

    bm = bmesh.new()
    pad_faces = set()
    pad_faces |= _create_equip_box(bm, tuple(pad_center), (0.29, pad_len, pad_thick), rot_back)
    pad_faces |= _create_equip_box(bm, (0.0, -0.21, 0.39), (0.29, 0.30, 0.06), rot_seat)

    # Khung thep do ghe & tru chong tua lung
    frame_faces = set()
    frame_faces |= _create_equip_box(bm, (0.0, 0.14, 0.25), (0.07, 0.96, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -0.30, 0.195), (0.06, 0.06, 0.35))
    frame_faces |= _create_equip_box(bm, (0.0, 0.56, 0.135), (0.06, 0.06, 0.23))
    frame_faces |= _create_equip_box(bm, (0.0, -0.30, 0.025), (0.48, 0.08, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.56, 0.025), (0.52, 0.08, 0.05))
    # Thanh chong nghieng noi tu khung duoi len mat sau cua tua lung
    back_brace_top = hinge_top + axis_up_pad * 0.55 - normal_pad * 0.065
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, 0.35, 0.27)), back_brace_top, 0.024, 8)
    # Thanh do duoi dem ngoi
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, -0.26, 0.26)), Vector((0.0, -0.21, 0.37)), 0.022, 8)

    _assign_bmesh_materials(bm, [(frame_faces, 0), (pad_faces, 1)])
    obj = _bmesh_to_object(bm, collection, name, [mat_frame, mat_pad])
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


def _build_cable_crossover_machine(
    collection,
    pulley_l: Vector = Vector((1.05, 0.42, 1.38)),
    pulley_r: Vector = Vector((-1.05, 0.42, 1.38)),
):
    """Khung may cap doi (Cable Crossover) + 2 tay cam D-Handle + 2 day cap co dan dong."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    accent_faces = set()

    # Hai thap cap trai/phai + khoi ta
    ty = pulley_l.y + 0.14
    for sx in (1.0, -1.0):
        tx = sx * (abs(pulley_l.x) + 0.06)
        # Tru chinh truoc/sau
        frame_faces |= _create_equip_box(bm, (tx, ty - 0.14, 1.075), (0.07, 0.07, 2.15))
        frame_faces |= _create_equip_box(bm, (tx + sx * 0.18, ty + 0.18, 1.075), (0.06, 0.06, 2.15))
        # Chan de san
        frame_faces |= _create_equip_box(bm, (tx + sx * 0.09, ty + 0.02, 0.025), (0.34, 0.56, 0.05))
        # Dinh thap
        frame_faces |= _create_equip_box(bm, (tx + sx * 0.09, ty + 0.02, 2.125), (0.32, 0.48, 0.05))
        # Khoi ta (Weight stack)
        steel_faces |= _create_equip_box(bm, (tx + sx * 0.12, ty + 0.08, 0.55), (0.14, 0.24, 0.72))
        # Cum rong roc truot (Pulley carriage) tai do cao nguc/vai
        px = pulley_l.x if sx > 0 else pulley_r.x
        py = pulley_l.y
        pz = pulley_l.z
        accent_faces |= _create_equip_box(bm, (px + sx * 0.04, py + 0.02, pz), (0.06, 0.08, 0.12))
        steel_faces |= _create_equip_cylinder(
            bm,
            Vector((px - 0.02, py, pz)),
            Vector((px + 0.02, py, pz)),
            0.045,
            12,
        )

    # Thanh xa noi dinh hai thap (Z = 2.125)
    bridge_w = 2.0 * (abs(pulley_l.x) + 0.06)
    frame_faces |= _create_equip_box(bm, (0.0, ty, 2.125), (bridge_w, 0.07, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, ty + 0.13, 2.125), (bridge_w, 0.05, 0.05))

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (accent_faces, 2)])
    machine = _bmesh_to_object(bm, collection, "Equip_CableMachine", [mat_frame, mat_steel, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # 2 D-Handles (origin tai tam nam trong long ban tay)
    handles = {}
    for side in ("L", "R"):
        bm_h = bmesh.new()
        grip_faces = _create_equip_cylinder(bm_h, Vector((-0.055, 0.0, 0.0)), Vector((0.055, 0.0, 0.0)), 0.015, 8)
        strap_faces = _create_equip_cylinder(bm_h, Vector((-0.055, 0.0, 0.0)), Vector((0.0, 0.11, 0.0)), 0.008, 6)
        strap_faces |= _create_equip_cylinder(bm_h, Vector((0.055, 0.0, 0.0)), Vector((0.0, 0.11, 0.0)), 0.008, 6)
        _assign_bmesh_materials(bm_h, [(grip_faces, 0), (strap_faces, 1)])
        handles[side] = _bmesh_to_object(bm_h, collection, f"Equip_Handle_{side}", [mat_pad, mat_cable])

    # 2 Day cap don vi (dai 1.0m doc truc +Y tu (0,0,0) -> (0,1,0)) de scale theo chieu dai that
    cables = {}
    for side in ("L", "R"):
        bm_c = bmesh.new()
        c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
        _assign_bmesh_materials(bm_c, [(c_faces, 0)])
        cables[side] = _bmesh_to_object(bm_c, collection, f"Equip_Cable_{side}", [mat_cable])

    return machine, handles, cables


def _build_pullup_rack_object(
    collection,
    bar_y: float = -0.04,
    bar_z: float = 2.24,
    name: str = "Equip_PullupRack",
):
    """Khung xa don (Pull-up Rack) Low-Poly dat tai Floor_Origin, thoang mat sau de nhin ro co Xo."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    post_x = 0.64
    for sx in (1.0, -1.0):
        px = sx * post_x
        # Tru dung chinh + de san dai
        frame_faces |= _create_equip_box(bm, (px, bar_y, 1.15), (0.065, 0.065, 2.30))
        frame_faces |= _create_equip_box(bm, (px, 0.04, 0.025), (0.08, 0.96, 0.05))
        # Thanh giang cheo chan de (khong can khong gian chan o giua)
        frame_faces |= _create_equip_cylinder(
            bm, Vector((px, bar_y - 0.34, 0.04)), Vector((px, bar_y, 0.44)), 0.020, 8
        )
        frame_faces |= _create_equip_cylinder(
            bm, Vector((px, bar_y + 0.42, 0.04)), Vector((px, bar_y, 0.48)), 0.020, 8
        )
        # Khoi gia co dinh thanh xa
        accent_faces |= _create_equip_box(bm, (px - sx * 0.02, bar_y, bar_z), (0.05, 0.08, 0.08))

    # Thanh giang ngang phia sau chan de
    frame_faces |= _create_equip_box(bm, (0.0, 0.48, 0.025), (1.36, 0.07, 0.05))
    # Xa don chinh nam ngang (doc truc X) + tay nam boc cao su
    steel_faces |= _create_equip_cylinder(
        bm, Vector((-post_x + 0.02, bar_y, bar_z)), Vector((post_x - 0.02, bar_y, bar_z)), 0.017, 12
    )
    for sx in (1.0, -1.0):
        pad_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.24, bar_y, bar_z)), Vector((sx * 0.50, bar_y, bar_z)), 0.020, 12
        )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    rack = _bmesh_to_object(bm, collection, name, [mat_frame, mat_steel, mat_pad, mat_accent])
    rack.parent = bpy.data.objects.get("Floor_Origin")
    return rack


def _build_lat_pulldown_machine(
    collection,
    pulley_pos: Vector = Vector((0.0, 0.08, 2.20)),
):
    """May keo xo Lat Pulldown (ghe ngoi + con lan khoa dui + thap ta + thanh Lat bar + cap dong)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & truc doc
    frame_faces |= _create_equip_box(bm, (0.0, -0.18, 0.025), (0.58, 1.24, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, -0.62, 0.025), (0.64, 0.42, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.14, 0.23), (0.07, 0.07, 0.38))
    frame_faces |= _create_equip_box(bm, (0.0, 0.14, 0.40), (0.12, 0.34, 0.05))

    # Dem ngoi (mat tren Z = 0.49)
    pad_faces |= _create_equip_box(bm, (0.0, 0.16, 0.455), (0.31, 0.40, 0.07))

    # Tru con lan khoa dui (dat o Y=-0.32 de khong cham cang chan nguoi tap; con lan Z=0.69 om sat mat tren dui)
    frame_faces |= _create_equip_box(bm, (0.0, -0.32, 0.365), (0.06, 0.06, 0.67))
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, -0.32, 0.69)), Vector((0.0, -0.02, 0.69)), 0.022, 8)
    for sx in (1.0, -1.0):
        pad_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.05, -0.02, 0.69)), Vector((sx * 0.25, -0.02, 0.69)), 0.052, 12
        )

    # Thap ta phia truoc (Y=-0.64) + khoi ta
    for sx in (1.0, -1.0):
        frame_faces |= _create_equip_box(bm, (sx * 0.18, -0.64, 1.13), (0.065, 0.065, 2.26))
    frame_faces |= _create_equip_box(bm, (0.0, -0.64, 2.24), (0.44, 0.22, 0.06))
    steel_faces |= _create_equip_box(bm, (0.0, -0.64, 0.60), (0.24, 0.18, 0.80))

    # Can vuon rong roc phia tren (vuon toi Y=0.08 ngay phia tren nguc tren)
    frame_faces |= _create_equip_box(bm, (0.0, -0.27, 2.24), (0.08, 0.78, 0.07))
    accent_faces |= _create_equip_box(bm, (0.0, pulley_pos.y, pulley_pos.z + 0.04), (0.07, 0.09, 0.08))
    steel_faces |= _create_equip_cylinder(
        bm,
        Vector((-0.025, pulley_pos.y, pulley_pos.z)),
        Vector((0.025, pulley_pos.y, pulley_pos.z)),
        0.055,
        12,
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_LatMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Thanh keo xo Lat Bar (origin tai tam thanh ngang, diem moc cap o Z=+0.04)
    bm_b = bmesh.new()
    b_steel = set()
    b_pad = set()
    b_accent = set()
    b_steel |= _create_equip_cylinder(bm_b, Vector((-0.26, 0.0, 0.0)), Vector((0.26, 0.0, 0.0)), 0.015, 10)
    b_accent |= _create_equip_cylinder(bm_b, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.042)), 0.016, 8)
    for sx in (1.0, -1.0):
        p_in = Vector((sx * 0.255, 0.0, 0.0))
        p_out = Vector((sx * 0.52, 0.0, -0.09))
        b_steel |= _create_equip_cylinder(bm_b, p_in, p_out, 0.015, 10)
        g0 = p_in.lerp(p_out, 0.18)
        g1 = p_in.lerp(p_out, 0.88)
        b_pad |= _create_equip_cylinder(bm_b, g0, g1, 0.019, 10)
    _assign_bmesh_materials(bm_b, [(b_steel, 0), (b_pad, 1), (b_accent, 2)])
    lat_bar = _bmesh_to_object(bm_b, collection, "Equip_LatBar", [mat_steel, mat_pad, mat_accent])

    # Day cap don vi doc +Y (0 -> 1) de scale theo khoang cach thuc te
    bm_c = bmesh.new()
    c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
    _assign_bmesh_materials(bm_c, [(c_faces, 0)])
    cable = _bmesh_to_object(bm_c, collection, "Equip_Cable_Lat", [mat_cable])

    return machine, lat_bar, cable


def _build_single_cable_tower(
    collection,
    pulley_pos: Vector = Vector((0.0, -0.96, 1.98)),
):
    """Thap cap don (Single Cable Tower) + thanh Straight Bar + day cap dong cho bai Straight-Arm Pulldown."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    accent_faces = set()

    ty = pulley_pos.y - 0.14
    frame_faces |= _create_equip_box(bm, (0.0, ty + 0.12, 1.075), (0.075, 0.075, 2.15))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.18, 1.075), (0.07, 0.07, 2.15))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 0.025), (0.48, 0.62, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 2.125), (0.36, 0.44, 0.05))
    steel_faces |= _create_equip_box(bm, (0.0, ty - 0.04, 0.58), (0.24, 0.18, 0.78))

    accent_faces |= _create_equip_box(bm, (0.0, pulley_pos.y - 0.02, pulley_pos.z), (0.07, 0.09, 0.12))
    steel_faces |= _create_equip_cylinder(
        bm,
        Vector((-0.025, pulley_pos.y, pulley_pos.z)),
        Vector((0.025, pulley_pos.y, pulley_pos.z)),
        0.048,
        12,
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (accent_faces, 2)])
    tower = _bmesh_to_object(bm, collection, "Equip_CableTower", [mat_frame, mat_steel, mat_accent])
    tower.parent = bpy.data.objects.get("Floor_Origin")

    # Thanh thang ngan Straight Bar (origin tai tam nam, diem moc cap tai (0, 0, +0.036))
    bm_b = bmesh.new()
    b_steel = _create_equip_cylinder(bm_b, Vector((-0.26, 0.0, 0.0)), Vector((0.26, 0.0, 0.0)), 0.015, 10)
    b_pad = set()
    for sx in (1.0, -1.0):
        b_pad |= _create_equip_cylinder(bm_b, Vector((sx * 0.12, 0.0, 0.0)), Vector((sx * 0.25, 0.0, 0.0)), 0.019, 10)
    b_accent = _create_equip_cylinder(bm_b, Vector((0.0, 0.0, 0.0)), Vector((0.0, 0.0, 0.036)), 0.015, 8)
    _assign_bmesh_materials(bm_b, [(b_steel, 0), (b_pad, 1), (b_accent, 2)])
    straight_bar = _bmesh_to_object(bm_b, collection, "Equip_StraightBar", [mat_steel, mat_pad, mat_accent])

    bm_c = bmesh.new()
    c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
    _assign_bmesh_materials(bm_c, [(c_faces, 0)])
    cable = _bmesh_to_object(bm_c, collection, "Equip_Cable_Center", [mat_cable])

    return tower, straight_bar, cable


def _build_seated_row_machine(
    collection,
    pulley_pos: Vector = Vector((0.0, -1.06, 0.62)),
):
    """May ngoi keo cap ngang (Seated Cable Row) + tay cam V-Handle hep + day cap dong."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & ghe ngoi dai (mat dem top Z = 0.44, Y = -0.34 .. +0.58)
    frame_faces |= _create_equip_box(bm, (0.0, -0.36, 0.025), (0.56, 1.88, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.12, 0.34), (0.10, 0.86, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, 0.44, 0.18), (0.08, 0.08, 0.32))
    frame_faces |= _create_equip_box(bm, (0.0, -0.24, 0.18), (0.08, 0.08, 0.32))
    pad_faces |= _create_equip_box(bm, (0.0, 0.12, 0.405), (0.30, 0.92, 0.07))

    # Thanh noi & ban dap chan nghieng (dual footplates tai X=+-0.15, Y=-0.84, Z=0.47, nghieng ~22 deg)
    frame_faces |= _create_equip_box(bm, (0.0, -0.61, 0.34), (0.08, 0.62, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -0.84, 0.25), (0.07, 0.08, 0.38))
    plate_rot = Matrix.Rotation(math.radians(22.0), 4, "X")
    for sx in (1.0, -1.0):
        steel_faces |= _create_equip_box(bm, (sx * 0.15, -0.84, 0.47), (0.18, 0.03, 0.32), plate_rot)
    frame_faces |= _create_equip_box(bm, (0.0, -0.88, 0.40), (0.42, 0.06, 0.06))

    # Thap ta phia truoc (Y = -1.24, chieu cao 2.05m) + khoi ta + cum rong roc thap
    for sx in (1.0, -1.0):
        frame_faces |= _create_equip_box(bm, (sx * 0.18, -1.24, 1.03), (0.065, 0.065, 2.06))
    frame_faces |= _create_equip_box(bm, (0.0, -1.24, 2.04), (0.46, 0.28, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -1.24, 0.025), (0.60, 0.46, 0.05))
    steel_faces |= _create_equip_box(bm, (0.0, -1.24, 0.58), (0.24, 0.18, 0.78))

    # Khop rong roc thap tai pulley_pos
    frame_faces |= _create_equip_cylinder(
        bm, Vector((0.0, -1.18, pulley_pos.z)), Vector((0.0, pulley_pos.y, pulley_pos.z)), 0.025, 8
    )
    accent_faces |= _create_equip_box(bm, (0.0, pulley_pos.y - 0.02, pulley_pos.z), (0.07, 0.08, 0.10))
    steel_faces |= _create_equip_cylinder(
        bm,
        Vector((-0.022, pulley_pos.y, pulley_pos.z)),
        Vector((0.022, pulley_pos.y, pulley_pos.z)),
        0.045,
        12,
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_SeatedRowMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Tay cam V-Handle hep trung tinh (2 tay cam doc tai X=+-0.085, diem moc cap tai Y=-0.14)
    bm_v = bmesh.new()
    v_steel = set()
    v_pad = set()
    v_accent = set()
    eye_pt = Vector((0.0, -0.14, 0.0))
    v_accent |= _create_equip_cylinder(bm_v, Vector((0.0, -0.105, 0.0)), eye_pt, 0.015, 8)
    for sx in (1.0, -1.0):
        gx = sx * 0.085
        v_steel |= _create_equip_cylinder(bm_v, Vector((gx, 0.0, 0.075)), Vector((gx, 0.0, -0.075)), 0.014, 10)
        v_pad |= _create_equip_cylinder(bm_v, Vector((gx, 0.0, 0.065)), Vector((gx, 0.0, -0.065)), 0.016, 10)
        v_steel |= _create_equip_cylinder(bm_v, Vector((gx, 0.0, 0.055)), Vector((0.0, -0.11, 0.0)), 0.011, 8)
        v_steel |= _create_equip_cylinder(bm_v, Vector((gx, 0.0, -0.055)), Vector((0.0, -0.11, 0.0)), 0.011, 8)
    _assign_bmesh_materials(bm_v, [(v_steel, 0), (v_pad, 1), (v_accent, 2)])
    v_handle = _bmesh_to_object(bm_v, collection, "Equip_VHandle", [mat_steel, mat_pad, mat_accent])

    # Day cap don vi doc +Y (0 -> 1) scale dong
    bm_c = bmesh.new()
    c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
    _assign_bmesh_materials(bm_c, [(c_faces, 0)])
    cable = _bmesh_to_object(bm_c, collection, "Equip_Cable_Row", [mat_cable])

    return machine, v_handle, cable


def _build_cable_rope_station(
    collection,
    pulley_pos: Vector = Vector((0.0, -1.12, 1.58)),
):
    """Thap cap don ngang tran + day cap dong + cum day thung chu Y 2 nhanh co nut chan cao su cho Face Pull."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)
    mat_rope = base_mod._create_pbr_material("Mat_Equip_Rope", (0.045, 0.045, 0.052, 1.0), roughness=0.88, metallic=0.02)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    accent_faces = set()

    ty = pulley_pos.y - 0.14
    frame_faces |= _create_equip_box(bm, (0.0, ty + 0.12, 1.075), (0.075, 0.075, 2.15))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.18, 1.075), (0.07, 0.07, 2.15))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 0.025), (0.50, 0.64, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 2.125), (0.38, 0.46, 0.05))
    steel_faces |= _create_equip_box(bm, (0.0, ty - 0.04, 0.58), (0.24, 0.18, 0.78))

    accent_faces |= _create_equip_box(bm, (0.0, pulley_pos.y - 0.02, pulley_pos.z), (0.07, 0.09, 0.12))
    steel_faces |= _create_equip_cylinder(
        bm,
        Vector((-0.025, pulley_pos.y, pulley_pos.z)),
        Vector((0.025, pulley_pos.y, pulley_pos.z)),
        0.048,
        12,
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (accent_faces, 2)])
    tower = _bmesh_to_object(bm, collection, "Equip_CableTower_FacePull", [mat_frame, mat_steel, mat_accent])
    tower.parent = bpy.data.objects.get("Floor_Origin")

    # Khop chia nhanh trung tam (Carabiner hub)
    bm_hub = bmesh.new()
    h_steel = _create_equip_cylinder(bm_hub, Vector((0.0, -0.025, 0.0)), Vector((0.0, 0.025, 0.0)), 0.016, 10)
    h_accent = _create_equip_box(bm_hub, (0.0, 0.0, 0.0), (0.032, 0.026, 0.036))
    _assign_bmesh_materials(bm_hub, [(h_steel, 0), (h_accent, 1)])
    rope_hub = _bmesh_to_object(bm_hub, collection, "Equip_RopeHub", [mat_steel, mat_accent])

    # Day cap thep chinh don vi (+Y 0 -> 1)
    bm_c = bmesh.new()
    c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
    _assign_bmesh_materials(bm_c, [(c_faces, 0)])
    cable = _bmesh_to_object(bm_c, collection, "Equip_Cable_FacePull", [mat_cable])

    # 2 nhanh day thung don vi (+Y 0 -> 1) va 2 nut chan cao su o dau tay nam
    branches = {}
    knobs = {}
    for side in ("L", "R"):
        bm_b = bmesh.new()
        b_faces = _create_equip_cylinder(bm_b, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.014, 10)
        _assign_bmesh_materials(bm_b, [(b_faces, 0)])
        branches[side] = _bmesh_to_object(bm_b, collection, f"Equip_RopeBranch_{side}", [mat_rope])

        bm_k = bmesh.new()
        k_pad = _create_equip_cylinder(bm_k, Vector((0.0, -0.028, 0.0)), Vector((0.0, 0.028, 0.0)), 0.030, 12)
        k_cap = _create_equip_cylinder(bm_k, Vector((0.0, 0.025, 0.0)), Vector((0.0, 0.032, 0.0)), 0.024, 12)
        _assign_bmesh_materials(bm_k, [(k_pad, 0), (k_cap, 1)])
        knobs[side] = _bmesh_to_object(bm_k, collection, f"Equip_RopeKnob_{side}", [mat_pad, mat_accent])

    return tower, rope_hub, cable, branches, knobs


def _build_squat_rack_object(
    collection,
    name: str = "Equip_SquatRack",
):
    """Khung Half-Rack ganh ta don Low-Poly dat tai Floor_Origin (J-cups phia truoc, thanh bao hiem Z=0.68)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    accent_faces = set()

    post_x = 0.58
    post_y = -0.58
    for sx in (1.0, -1.0):
        px = sx * post_x
        # Tru dung chinh truoc (tranh tam nhin lung/co dui khi quay sau & nghieng)
        frame_faces |= _create_equip_box(bm, (px, post_y, 0.94), (0.065, 0.065, 1.88))
        # Chan de san dai (-0.78 .. +0.58)
        frame_faces |= _create_equip_box(bm, (px, -0.10, 0.025), (0.075, 1.36, 0.05))
        # Thanh giang cheo giup khung vung
        frame_faces |= _create_equip_cylinder(
            bm, Vector((px, post_y + 0.42, 0.04)), Vector((px, post_y, 0.44)), 0.020, 8
        )
        # J-Cups dat don ta (Z=1.38)
        accent_faces |= _create_equip_box(bm, (px, post_y + 0.06, 1.38), (0.055, 0.07, 0.07))
        # Thanh bao hiem (Safety spotter arms) chay nguoc ve sau o Z=0.68
        frame_faces |= _create_equip_box(bm, (px, -0.09, 0.68), (0.055, 0.92, 0.055))
        steel_faces |= _create_equip_box(bm, (px, -0.09, 0.712), (0.048, 0.90, 0.012))

    # Thanh giang san phia sau & tren cao mat truoc (khong che goc nhin nguoi tap)
    frame_faces |= _create_equip_box(bm, (0.0, 0.54, 0.025), (1.24, 0.07, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, post_y, 1.86), (1.24, 0.06, 0.06))

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (accent_faces, 2)])
    rack = _bmesh_to_object(bm, collection, name, [mat_frame, mat_steel, mat_accent])
    rack.parent = bpy.data.objects.get("Floor_Origin")
    return rack


def _build_leg_press_machine(
    collection,
):
    """May dap dui nghieng 40 deg (Equip_LegPressMachine + ban dap truot Equip_LegPressSled)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_iron = base_mod._create_pbr_material("Mat_Equip_Iron", PLATE_IRON_COLOR, roughness=0.45, metallic=0.80)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    ang40 = math.radians(40.0)
    track_dir = Vector((0.0, -math.cos(ang40), math.sin(ang40))).normalized()
    track_perp = Vector((0.0, math.sin(ang40), math.cos(ang40))).normalized()

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & tru do chinh
    frame_faces |= _create_equip_box(bm, (0.0, -0.10, 0.025), (0.64, 2.08, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, -0.96, 0.025), (0.86, 0.24, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.86, 0.025), (0.72, 0.22, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.36, 0.12), (0.34, 0.56, 0.16))

    # Dem ngoi (Y=0.14..0.44, top Z=0.25) & tua lung nghieng 35 deg tu (0, 0.40, 0.23)
    pad_faces |= _create_equip_box(bm, (0.0, 0.28, 0.215), (0.32, 0.28, 0.07))
    back_rad = math.radians(35.0)
    back_up = Vector((0.0, math.cos(back_rad), math.sin(back_rad)))
    back_n = Vector((0.0, -math.sin(back_rad), math.cos(back_rad)))
    back_hinge = Vector((0.0, 0.41, 0.24))
    back_len = 0.78
    back_center = back_hinge + back_up * (0.5 * back_len) - back_n * 0.032
    pad_faces |= _create_equip_box(bm, tuple(back_center), (0.31, back_len, 0.065), Matrix.Rotation(back_rad, 4, "X"))
    # Dem goi dau & thanh chong tua lung
    head_center = back_hinge + back_up * 0.85 - back_n * 0.030
    pad_faces |= _create_equip_box(bm, tuple(head_center), (0.24, 0.16, 0.07), Matrix.Rotation(back_rad, 4, "X"))
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, 0.86, 0.05)), back_hinge + back_up * 0.65 - back_n * 0.06, 0.028, 8)

    # 2 tay nam hai ben hong
    for sx in (1.0, -1.0):
        hx = sx * 0.26
        frame_faces |= _create_equip_box(bm, (hx, 0.28, 0.17), (0.04, 0.04, 0.28))
        pad_faces |= _create_equip_cylinder(bm, Vector((hx, 0.16, 0.32)), Vector((hx, 0.36, 0.32)), 0.019, 10)

    # Hai duong ray truot 40 deg dat ngoai khoang chan (X = +-0.34) chay tu de len tru truoc
    rail_start = Vector((0.0, 0.14, 0.24))
    rail_end = rail_start + track_dir * 1.38
    for sx in (1.0, -1.0):
        rx = sx * 0.34
        p0 = Vector((rx, rail_start.y, rail_start.z))
        p1 = Vector((rx, rail_end.y, rail_end.z))
        steel_faces |= _create_equip_cylinder(bm, p0, p1, 0.020, 10)
        # Tru chong dau tren cua ray xuong san
        frame_faces |= _create_equip_box(bm, (rx, p1.y, 0.5 * p1.z), (0.055, 0.055, p1.z))
        frame_faces |= _create_equip_box(bm, (rx, p0.y, 0.5 * p0.z), (0.055, 0.055, p0.z))
    frame_faces |= _create_equip_box(bm, (0.0, rail_end.y, rail_end.z), (0.74, 0.06, 0.06))

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_LegPressMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Ban dap truot + tạ dia (local axis: +X=left, +Y=up along plate, +Z=away along track_dir)
    # Mat phang ban dap tiep xuc chan nam tai Z=0; toan bo tam thep & banh ta lui ve +Z (>0)
    bm_s = bmesh.new()
    s_frame = set()
    s_steel = set()
    s_iron = set()
    s_accent = set()
    # Tam dap thep van chong truot (-0.27..+0.27 X, -0.18..+0.28 Y, 0..+0.035 Z)
    s_frame |= _create_equip_box(bm_s, (0.0, 0.05, 0.018), (0.54, 0.46, 0.036))
    s_steel |= _create_equip_box(bm_s, (0.0, 0.05, 0.002), (0.50, 0.42, 0.006))
    # Hop truot noi ra 2 thanh ray o X=+-0.34
    s_frame |= _create_equip_box(bm_s, (0.0, 0.04, 0.11), (0.70, 0.12, 0.14))
    for sx in (1.0, -1.0):
        s_accent |= _create_equip_cylinder(bm_s, Vector((sx * 0.34, -0.10, 0.14)), Vector((sx * 0.34, 0.14, 0.14)), 0.032, 10)
        # Chot nap banh ta ben ngoai + 2 banh ta 20kg
        s_steel |= _create_equip_cylinder(bm_s, Vector((sx * 0.36, 0.04, 0.16)), Vector((sx * 0.56, 0.04, 0.16)), 0.024, 10)
        s_iron |= _create_equip_cylinder(bm_s, Vector((sx * 0.39, 0.04, 0.16)), Vector((sx * 0.435, 0.04, 0.16)), 0.195, 16)
        s_iron |= _create_equip_cylinder(bm_s, Vector((sx * 0.445, 0.04, 0.16)), Vector((sx * 0.485, 0.04, 0.16)), 0.165, 16)
        s_accent |= _create_equip_cylinder(bm_s, Vector((sx * 0.49, 0.04, 0.16)), Vector((sx * 0.52, 0.04, 0.16)), 0.038, 12)

    _assign_bmesh_materials(bm_s, [(s_frame, 0), (s_steel, 1), (s_iron, 2), (s_accent, 3)])
    sled = _bmesh_to_object(bm_s, collection, "Equip_LegPressSled", [mat_frame, mat_steel, mat_iron, mat_accent])
    return machine, sled


def _build_leg_extension_machine(
    collection,
    pivot_pos: Vector = Vector((0.0, -0.37, 0.56)),
):
    """May ngoi da dui truoc (Equip_LegExtMachine + can da quay quanh tam goi Equip_LegExtArm)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Thap ta dat lui phia sau lech ben phai (X=-0.44, Y=0.54) de khong che mat ben dui truoc & lung
    frame_faces |= _create_equip_box(bm, (0.0, 0.0, 0.025), (0.52, 1.08, 0.05))
    frame_faces |= _create_equip_box(bm, (-0.22, 0.54, 0.025), (0.56, 0.42, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.02, 0.24), (0.08, 0.62, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -0.26, 0.24), (0.07, 0.07, 0.42))
    frame_faces |= _create_equip_box(bm, (0.0, 0.22, 0.24), (0.07, 0.07, 0.42))

    # Dem ngoi cao (Z_top=0.495) + dem tua lung nghieng nhe 10 deg phia sau
    pad_faces |= _create_equip_box(bm, (0.0, -0.06, 0.46), (0.32, 0.56, 0.07))
    back_rad = math.radians(80.0)
    back_up = Vector((0.0, math.cos(back_rad), math.sin(back_rad)))
    back_n = Vector((0.0, -math.sin(back_rad), math.cos(back_rad)))
    back_hinge = Vector((0.0, 0.20, 0.50))
    back_center = back_hinge + back_up * 0.28 - back_n * 0.032
    pad_faces |= _create_equip_box(bm, tuple(back_center), (0.29, 0.52, 0.065), Matrix.Rotation(back_rad, 4, "X"))
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, 0.30, 0.44)), back_hinge + back_up * 0.34 - back_n * 0.065, 0.026, 8)

    # 2 tay nam hai ben ghế
    for sx in (1.0, -1.0):
        hx = sx * 0.26
        frame_faces |= _create_equip_box(bm, (hx, -0.02, 0.42), (0.04, 0.04, 0.24))
        pad_faces |= _create_equip_cylinder(bm, Vector((hx, -0.14, 0.53)), Vector((hx, 0.06, 0.53)), 0.019, 10)

    # Thap ta ben phai phia sau (X=-0.44, Y=0.54) + cum truc khop xoay tam goi
    for dy in (-0.11, 0.11):
        frame_faces |= _create_equip_box(bm, (-0.44, 0.54 + dy, 0.64), (0.06, 0.06, 1.28))
    frame_faces |= _create_equip_box(bm, (-0.44, 0.54, 1.28), (0.22, 0.32, 0.06))
    steel_faces |= _create_equip_box(bm, (-0.44, 0.54, 0.40), (0.16, 0.18, 0.56))
    # Thanh vuon ra tam khop goi ben ngoai (X=-0.28, Y=-0.37, Z=0.56)
    frame_faces |= _create_equip_box(bm, (-0.28, 0.08, 0.32), (0.06, 0.96, 0.06))
    frame_faces |= _create_equip_box(bm, (-0.28, pivot_pos.y, 0.30), (0.06, 0.06, 0.52))
    accent_faces |= _create_equip_cylinder(
        bm, Vector((-0.31, pivot_pos.y, pivot_pos.z)), Vector((-0.24, pivot_pos.y, pivot_pos.z)), 0.055, 14
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_LegExtMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Can da xoay quanh (0,0,0) (local +Y = doc cang chan tu goi xuong co chan; local -Z = phia truoc ong dong)
    bm_a = bmesh.new()
    a_steel = set()
    a_pad = set()
    a_accent = set()
    # Thanh can xuong ben ngoai X=-0.26 tu tam goi (Y=0) toi muc co chan (Y=0.31, Z=-0.090)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.0, 0.0)), Vector((-0.26, 0.31, -0.02)), 0.018, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.31, -0.02)), Vector((-0.26, 0.31, -0.090)), 0.016, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.31, -0.090)), Vector((0.26, 0.31, -0.090)), 0.015, 10)
    a_accent |= _create_equip_cylinder(bm_a, Vector((-0.27, 0.0, 0.0)), Vector((-0.24, 0.0, 0.0)), 0.036, 12)
    # 2 con lan dem mu co chan boc xop (X = +-0.04 .. +-0.23, Y=0.31, Z=-0.090, R=0.046)
    for sx in (1.0, -1.0):
        a_pad |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.04, 0.31, -0.090)), Vector((sx * 0.24, 0.31, -0.090)), 0.046, 14
        )
        a_accent |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.24, 0.31, -0.090)), Vector((sx * 0.255, 0.31, -0.090)), 0.042, 12
        )

    _assign_bmesh_materials(bm_a, [(a_steel, 0), (a_pad, 1), (a_accent, 2)])
    lever_arm = _bmesh_to_object(bm_a, collection, "Equip_LegExtArm", [mat_steel, mat_pad, mat_accent])
    return machine, lever_arm


def _build_lying_leg_curl_machine(
    collection,
    pivot_pos: Vector = Vector((0.0, 0.47, 0.49)),
):
    """May nam sap moc dui sau (Equip_LyingCurlMachine + can moc con lan Achilles Equip_LyingCurlArm)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & tru do dem nam sap (thap ta dat lui ve truoc X=-0.46, Y=-0.78 de thoang tam nhin hong/dui)
    frame_faces |= _create_equip_box(bm, (0.0, 0.04, 0.025), (0.50, 1.32, 0.05))
    frame_faces |= _create_equip_box(bm, (-0.23, -0.78, 0.025), (0.58, 0.42, 0.05))
    frame_faces |= _create_equip_box(bm, (-0.44, -0.36, 0.025), (0.08, 0.88, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.0, 0.22), (0.08, 0.92, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, -0.40, 0.22), (0.07, 0.07, 0.40))
    frame_faces |= _create_equip_box(bm, (0.0, 0.36, 0.22), (0.07, 0.07, 0.40))

    # Dem nam sap (Y = -0.46 .. +0.43, top Z = 0.45) - ket thuc ngay truoc banh che goi o Y=+0.47
    pad_faces |= _create_equip_box(bm, (0.0, -0.015, 0.415), (0.34, 0.89, 0.07))

    # 2 tay nam phia truoc dau ghe (Y = -0.52, Z = 0.36)
    for sx in (1.0, -1.0):
        hx = sx * 0.23
        frame_faces |= _create_equip_box(bm, (hx * 0.5, -0.52, 0.26), (abs(hx), 0.045, 0.045))
        frame_faces |= _create_equip_box(bm, (hx, -0.52, 0.31), (0.04, 0.04, 0.14))
        pad_faces |= _create_equip_cylinder(bm, Vector((hx, -0.58, 0.36)), Vector((hx, -0.46, 0.36)), 0.019, 10)

    # Thap ta dat lech ben phai-truoc (X=-0.46, Y=-0.78) tranh che khuat hong & dui khi nhin ngang
    for dy in (-0.11, 0.11):
        frame_faces |= _create_equip_box(bm, (-0.46, -0.78 + dy, 0.62), (0.06, 0.06, 1.24))
    frame_faces |= _create_equip_box(bm, (-0.46, -0.78, 1.24), (0.22, 0.32, 0.06))
    steel_faces |= _create_equip_box(bm, (-0.46, -0.78, 0.38), (0.16, 0.18, 0.54))

    # Thanh vuon ra tam khop goi ben ngoai (X=-0.28, pivot_pos=(0, 0.47, 0.49))
    frame_faces |= _create_equip_box(bm, (-0.28, 0.16, 0.30), (0.06, 0.72, 0.06))
    frame_faces |= _create_equip_box(bm, (-0.28, pivot_pos.y, 0.28), (0.06, 0.06, 0.46))
    accent_faces |= _create_equip_cylinder(
        bm, Vector((-0.31, pivot_pos.y, pivot_pos.z)), Vector((-0.24, pivot_pos.y, pivot_pos.z)), 0.052, 14
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_LyingCurlMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Can moc xoay quanh pivot (local +Y = doc cang chan ve +Y; local +Z = phia sau Achilles)
    bm_a = bmesh.new()
    a_steel = set()
    a_pad = set()
    a_accent = set()
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.0, 0.0)), Vector((-0.26, 0.32, 0.02)), 0.018, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.32, 0.02)), Vector((-0.26, 0.32, 0.088)), 0.016, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.32, 0.088)), Vector((0.26, 0.32, 0.088)), 0.015, 10)
    a_accent |= _create_equip_cylinder(bm_a, Vector((-0.27, 0.0, 0.0)), Vector((-0.24, 0.0, 0.0)), 0.036, 12)
    for sx in (1.0, -1.0):
        a_pad |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.04, 0.32, 0.088)), Vector((sx * 0.24, 0.32, 0.088)), 0.044, 14
        )
        a_accent |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.24, 0.32, 0.088)), Vector((sx * 0.255, 0.32, 0.088)), 0.040, 12
        )

    _assign_bmesh_materials(bm_a, [(a_steel, 0), (a_pad, 1), (a_accent, 2)])
    curl_arm = _bmesh_to_object(bm_a, collection, "Equip_LyingCurlArm", [mat_steel, mat_pad, mat_accent])
    return machine, curl_arm


def _build_seated_leg_curl_machine(
    collection,
    pivot_pos: Vector = Vector((0.0, -0.37, 0.56)),
):
    """May ngoi moc dui sau (Equip_SeatedCurlMachine co dem khoa dui + can moc Achilles Equip_SeatedCurlArm)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & tru ghe lui ve Y=+0.10 de gam duoi goi hoan toan thong thoang khi moc cang chan sau
    frame_faces |= _create_equip_box(bm, (0.0, 0.02, 0.025), (0.52, 1.12, 0.05))
    frame_faces |= _create_equip_box(bm, (-0.22, 0.54, 0.025), (0.56, 0.42, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.14, 0.25), (0.08, 0.24, 0.06))
    frame_faces |= _create_equip_box(bm, (0.0, 0.10, 0.35), (0.07, 0.07, 0.24))
    frame_faces |= _create_equip_box(bm, (0.0, 0.22, 0.24), (0.07, 0.07, 0.42))

    # Dem ngoi cao (Z_top=0.495) + dem tua lung nghieng 80 deg
    pad_faces |= _create_equip_box(bm, (0.0, -0.06, 0.46), (0.32, 0.56, 0.07))
    back_rad = math.radians(80.0)
    back_up = Vector((0.0, math.cos(back_rad), math.sin(back_rad)))
    back_n = Vector((0.0, -math.sin(back_rad), math.cos(back_rad)))
    back_hinge = Vector((0.0, 0.20, 0.50))
    back_center = back_hinge + back_up * 0.28 - back_n * 0.032
    pad_faces |= _create_equip_box(bm, tuple(back_center), (0.29, 0.52, 0.065), Matrix.Rotation(back_rad, 4, "X"))
    frame_faces |= _create_equip_cylinder(bm, Vector((0.0, 0.30, 0.44)), back_hinge + back_up * 0.34 - back_n * 0.065, 0.026, 8)

    # Dem khoa chat tren dau goi (Thigh Lockdown Pad tai Y=-0.25, Z=0.655) + 2 tay nam phia tren (Z=0.725)
    frame_faces |= _create_equip_box(bm, (-0.24, -0.25, 0.52), (0.045, 0.045, 0.30))
    steel_faces |= _create_equip_cylinder(bm, Vector((-0.24, -0.25, 0.655)), Vector((0.24, -0.25, 0.655)), 0.016, 10)
    for sx in (1.0, -1.0):
        pad_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.04, -0.25, 0.655)), Vector((sx * 0.22, -0.25, 0.655)), 0.046, 14
        )
        accent_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.22, -0.25, 0.655)), Vector((sx * 0.235, -0.25, 0.655)), 0.042, 12
        )
        # 2 tay cam dung/ngang ngay tren dem khoa dui
        frame_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.18, -0.25, 0.67)), Vector((sx * 0.18, -0.25, 0.725)), 0.015, 8
        )
        pad_faces |= _create_equip_cylinder(
            bm, Vector((sx * 0.14, -0.25, 0.725)), Vector((sx * 0.24, -0.25, 0.725)), 0.019, 10
        )

    # Thap ta ben phai phia sau (X=-0.44, Y=0.54) + cum truc khop xoay tam goi
    for dy in (-0.11, 0.11):
        frame_faces |= _create_equip_box(bm, (-0.44, 0.54 + dy, 0.64), (0.06, 0.06, 1.28))
    frame_faces |= _create_equip_box(bm, (-0.44, 0.54, 1.28), (0.22, 0.32, 0.06))
    steel_faces |= _create_equip_box(bm, (-0.44, 0.54, 0.40), (0.16, 0.18, 0.56))
    frame_faces |= _create_equip_box(bm, (-0.28, 0.08, 0.32), (0.06, 0.96, 0.06))
    frame_faces |= _create_equip_box(bm, (-0.28, pivot_pos.y, 0.30), (0.06, 0.06, 0.52))
    accent_faces |= _create_equip_cylinder(
        bm, Vector((-0.31, pivot_pos.y, pivot_pos.z)), Vector((-0.24, pivot_pos.y, pivot_pos.z)), 0.055, 14
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = _bmesh_to_object(bm, collection, "Equip_SeatedCurlMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Can moc xoay quanh tam goi (local +Y = doc cang chan; local +Z = phia sau got Achilles!)
    bm_a = bmesh.new()
    a_steel = set()
    a_pad = set()
    a_accent = set()
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.0, 0.0)), Vector((-0.26, 0.31, 0.02)), 0.018, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.31, 0.02)), Vector((-0.26, 0.31, 0.088)), 0.016, 10)
    a_steel |= _create_equip_cylinder(bm_a, Vector((-0.26, 0.31, 0.088)), Vector((0.26, 0.31, 0.088)), 0.015, 10)
    a_accent |= _create_equip_cylinder(bm_a, Vector((-0.27, 0.0, 0.0)), Vector((-0.24, 0.0, 0.0)), 0.036, 12)
    for sx in (1.0, -1.0):
        a_pad |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.04, 0.31, 0.088)), Vector((sx * 0.24, 0.31, 0.088)), 0.046, 14
        )
        a_accent |= _create_equip_cylinder(
            bm_a, Vector((sx * 0.24, 0.31, 0.088)), Vector((sx * 0.255, 0.31, 0.088)), 0.042, 12
        )

    _assign_bmesh_materials(bm_a, [(a_steel, 0), (a_pad, 1), (a_accent, 2)])
    curl_arm = _bmesh_to_object(bm_a, collection, "Equip_SeatedCurlArm", [mat_steel, mat_pad, mat_accent])
    return machine, curl_arm


def _build_hip_thrust_bench_object(
    collection,
    name: str = "Equip_HipThrustBench",
):
    """Buc ghe tua ngang chuyen dung cho Hip Thrust dat tai Floor_Origin (mep truoc Y=+0.39, mat top Z=0.405)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)

    bm = bmesh.new()
    # Dem ghe dat ngang truc X (width 0.86m, depth 0.36m tai Y=+0.39..+0.75, top Z=0.405)
    pad_faces = _create_equip_box(bm, (0.0, 0.57, 0.368), (0.86, 0.36, 0.075))
    frame_faces = set()
    frame_faces |= _create_equip_box(bm, (0.0, 0.57, 0.305), (0.76, 0.28, 0.05))
    for sx in (1.0, -1.0):
        px = sx * 0.34
        frame_faces |= _create_equip_box(bm, (px, 0.57, 0.165), (0.065, 0.065, 0.29))
        frame_faces |= _create_equip_box(bm, (px, 0.58, 0.025), (0.08, 0.44, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, 0.72, 0.14), (0.74, 0.05, 0.05))

    _assign_bmesh_materials(bm, [(frame_faces, 0), (pad_faces, 1)])
    obj = _bmesh_to_object(bm, collection, name, [mat_frame, mat_pad])
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


def _build_cable_kickback_station(
    collection,
    pulley_pos: Vector = Vector((-0.14, -0.82, 0.16)),
):
    """Thap cap don rong roc thap nhat + tay vin ngang nguc + dai co chan & cap dong cho Glute Kickback."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_cable = base_mod._create_pbr_material("Mat_Equip_Cable", CABLE_COLOR, roughness=0.35, metallic=0.60)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Thap cap dat tai Y=-0.96, rong roc thap dat thang hang chan phai X=-0.14, Y=-0.82, Z=0.16
    ty = pulley_pos.y - 0.14
    frame_faces |= _create_equip_box(bm, (0.0, ty + 0.12, 1.05), (0.075, 0.075, 2.10))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.18, 1.05), (0.07, 0.07, 2.10))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 0.025), (0.56, 0.64, 0.05))
    frame_faces |= _create_equip_box(bm, (0.0, ty - 0.02, 2.08), (0.40, 0.44, 0.05))
    steel_faces |= _create_equip_box(bm, (0.0, ty - 0.04, 0.58), (0.24, 0.18, 0.78))

    # Thanh tay vin ngang nguc vuon ra Y=-0.64, Z=1.18
    for sx in (1.0, -1.0):
        frame_faces |= _create_equip_box(bm, (sx * 0.20, -0.74, 1.18), (0.04, 0.24, 0.04))
    frame_faces |= _create_equip_box(bm, (0.0, -0.84, 1.18), (0.44, 0.045, 0.045))
    pad_faces |= _create_equip_cylinder(bm, Vector((-0.24, -0.64, 1.18)), Vector((0.24, -0.64, 1.18)), 0.020, 10)

    # Cum rong roc thap nhat tai pulley_pos (-0.14, -0.82, 0.16)
    frame_faces |= _create_equip_box(bm, (pulley_pos.x * 0.5, pulley_pos.y - 0.02, pulley_pos.z), (abs(pulley_pos.x) + 0.06, 0.05, 0.05))
    accent_faces |= _create_equip_box(bm, (pulley_pos.x, pulley_pos.y - 0.02, pulley_pos.z), (0.06, 0.08, 0.10))
    steel_faces |= _create_equip_cylinder(
        bm,
        Vector((pulley_pos.x - 0.02, pulley_pos.y, pulley_pos.z)),
        Vector((pulley_pos.x + 0.02, pulley_pos.y, pulley_pos.z)),
        0.042,
        12,
    )

    _assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    tower = _bmesh_to_object(bm, collection, "Equip_CableTower_Kickback", [mat_frame, mat_steel, mat_pad, mat_accent])
    tower.parent = bpy.data.objects.get("Floor_Origin")

    # Dai co chan (Ankle Strap) + khoen moc huong ve rong roc (+Y = -world_Y khi dat strap_y huong -Y)
    bm_st = bmesh.new()
    st_pad = _create_equip_cylinder(bm_st, Vector((0.0, 0.0, -0.028)), Vector((0.0, 0.0, 0.028)), 0.054, 14)
    st_accent = _create_equip_cylinder(bm_st, Vector((0.0, 0.048, 0.0)), Vector((0.0, 0.072, 0.0)), 0.014, 8)
    _assign_bmesh_materials(bm_st, [(st_pad, 0), (st_accent, 1)])
    ankle_strap = _bmesh_to_object(bm_st, collection, "Equip_AnkleStrap", [mat_pad, mat_accent])

    # Day cap don vi doc +Y (0 -> 1) scale dong
    bm_c = bmesh.new()
    c_faces = _create_equip_cylinder(bm_c, Vector((0.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), 0.005, 6)
    _assign_bmesh_materials(bm_c, [(c_faces, 0)])
    cable = _bmesh_to_object(bm_c, collection, "Equip_Cable_Kickback", [mat_cable])

    return tower, ankle_strap, cable


def _build_kneeling_mat_object(
    collection,
    name: str = "Equip_Mat",
    center_y: float = 0.04,
    length_y: float = 1.88,
):
    """Tham tap yoga/gym Low-Poly dat tai Floor_Origin (Z = 0..0.018)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_yoga = base_mod._create_pbr_material("Mat_Equip_Mat", (0.04, 0.075, 0.115, 1.0), roughness=0.80, metallic=0.05)
    bm = bmesh.new()
    faces = _create_equip_box(bm, (0.0, center_y, 0.009), (0.85, length_y, 0.018))
    _assign_bmesh_materials(bm, [(faces, 0)])
    obj = _bmesh_to_object(bm, collection, name, [mat_yoga])
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


# ---------------------------------------------------------------------------
# Rigging, IK & Animation Helpers
# ---------------------------------------------------------------------------
def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _rep_curve(frame: int, f_start: int, f_bot_start: int, f_bot_end: int, f_end: int) -> float:
    if frame <= f_start or frame >= f_end:
        return 0.0
    if frame < f_bot_start:
        return _smoothstep((frame - f_start) / max(1, f_bot_start - f_start))
    if frame <= f_bot_end:
        return 1.0
    return 1.0 - _smoothstep((frame - f_bot_end) / max(1, f_end - f_bot_end))


def _reset_pose(arm_obj) -> None:
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.location = Vector((0.0, 0.0, 0.0))
        pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        pb.scale = Vector((1.0, 1.0, 1.0))


def _add_ctrl_bone(arm_obj, bone_name: str, head_pos: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> None:
    import bpy  # type: ignore

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_obj.data.edit_bones
    b = eb.new(bone_name)
    b.head = Vector(head_pos)
    b.tail = Vector((head_pos[0], head_pos[1] + 0.15, head_pos[2]))
    b.parent = eb["Root"]
    b.use_connect = False
    b.align_roll(Vector((0.0, 0.0, 1.0)))
    bpy.ops.object.mode_set(mode="OBJECT")


def _parent_equip_to_bone(equip_obj, arm_obj, bone_name: str, local_rot_euler: Euler | None = None) -> None:
    import bpy  # type: ignore

    bone_len = arm_obj.data.bones[bone_name].length
    equip_obj.parent = arm_obj
    equip_obj.parent_type = "BONE"
    equip_obj.parent_bone = bone_name
    bpy.context.view_layer.update()
    equip_obj.matrix_parent_inverse = Matrix.Identity(4)
    equip_obj.location = Vector((0.0, -bone_len, 0.0))
    if local_rot_euler is not None:
        equip_obj.rotation_euler = local_rot_euler


def _set_bone_world_head(arm_obj, bone_name: str, target_world_pos: Vector) -> None:
    import bpy  # type: ignore

    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones[bone_name]
    cur_mat = arm_obj.matrix_world @ pb.matrix
    delta_world = target_world_pos - cur_mat.translation
    rest_frame_world = cur_mat.to_3x3() @ pb.rotation_quaternion.to_matrix().inverted()
    pb.location = pb.location + rest_frame_world.inverted() @ delta_world
    bpy.context.view_layer.update()


def _aim_bone_world(
    arm_obj,
    bone_name: str,
    target_y_dir_world: Vector,
    roll_reference_z_world: Vector | None = None,
) -> None:
    import bpy  # type: ignore

    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones[bone_name]
    cur_mat_world = arm_obj.matrix_world @ pb.matrix
    cur_y = cur_mat_world.col[1].to_3d().normalized()
    tgt_y = target_y_dir_world.normalized()
    rot_delta = cur_y.rotation_difference(tgt_y)

    new_rot3 = rot_delta.to_matrix() @ cur_mat_world.to_3x3()
    if roll_reference_z_world is not None:
        ref = roll_reference_z_world - tgt_y * roll_reference_z_world.dot(tgt_y)
        if ref.length > 1e-4:
            new_z = ref.normalized()
            new_x = tgt_y.cross(new_z).normalized()
            new_z = new_x.cross(tgt_y).normalized()
            new_rot3 = Matrix((new_x, tgt_y, new_z)).transposed()

    new_world = Matrix.Translation(cur_mat_world.translation) @ new_rot3.to_4x4()
    pb.matrix = arm_obj.matrix_world.inverted() @ new_world
    bpy.context.view_layer.update()


def _set_bone_world_axes(
    arm_obj,
    bone_name: str,
    world_pos: Vector,
    axis_x: Vector,
    axis_y: Vector,
    axis_z: Vector,
) -> None:
    import bpy  # type: ignore

    _set_bone_world_head(arm_obj, bone_name, world_pos)
    pb = arm_obj.pose.bones[bone_name]
    rot3 = Matrix((axis_x.normalized(), axis_y.normalized(), axis_z.normalized())).transposed()
    new_world = Matrix.Translation(world_pos) @ rot3.to_4x4()
    pb.matrix = arm_obj.matrix_world.inverted() @ new_world
    bpy.context.view_layer.update()


def _solve_two_bone_ik_world(
    arm_obj,
    upper_name: str,
    lower_name: str,
    target_world: Vector,
    pole_hint_dir: Vector,
    roll_z_upper: Vector,
    roll_z_lower: Vector,
) -> None:
    import bpy  # type: ignore

    bpy.context.view_layer.update()
    pb_up = arm_obj.pose.bones[upper_name]
    pb_lo = arm_obj.pose.bones[lower_name]

    root_pos = (arm_obj.matrix_world @ pb_up.matrix).translation
    len1 = pb_up.bone.length
    len2 = pb_lo.bone.length

    to_target = target_world - root_pos
    dist = max(0.05, min(len1 + len2 - 0.005, to_target.length))
    fwd = to_target.normalized()

    cos_a = max(-1.0, min(1.0, (len1 * len1 + dist * dist - len2 * len2) / (2.0 * len1 * dist)))
    ang_a = math.acos(cos_a)

    bend_dir = pole_hint_dir - fwd * pole_hint_dir.dot(fwd)
    if bend_dir.length < 1e-4:
        bend_dir = Vector((0.0, 1.0, 0.0)).cross(fwd)
    bend_dir.normalize()

    upper_dir = (fwd * math.cos(ang_a) + bend_dir * math.sin(ang_a)).normalized()
    joint_pos = root_pos + upper_dir * len1
    lower_dir = (target_world - joint_pos).normalized()

    _aim_bone_world(arm_obj, upper_name, upper_dir, roll_z_upper)
    _aim_bone_world(arm_obj, lower_name, lower_dir, roll_z_lower)


def _key_all_pose_bones(arm_obj, frame: int, key_scale: bool = False) -> None:
    for pb in arm_obj.pose.bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        if key_scale:
            pb.keyframe_insert(data_path="scale", frame=frame)


def _begin_action(arm_obj, action_name: str) -> None:
    import bpy  # type: ignore

    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    action = bpy.data.actions.new(name=action_name)
    arm_obj.animation_data.action = action
    _reset_pose(arm_obj)


def _push_action_to_nla(arm_obj, action_name: str, frame_start: int, frame_end: int) -> None:
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    action = arm_obj.animation_data.action
    action.name = action_name
    track = arm_obj.animation_data.nla_tracks.new()
    track.name = action_name
    strip = track.strips.new(action_name, frame_start, action)
    strip.name = action_name
    strip.action_frame_start = float(frame_start)
    strip.action_frame_end = float(frame_end)
    track.mute = True
    arm_obj.animation_data.action = None


# ---------------------------------------------------------------------------
# NHOM 1: CO NGUC (CHEST) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 1. BARBELL BENCH PRESS (Day nguc ngang voi ta don)
def _pose_barbell_bench_press(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    # Nam ngua tren ghe Bench (top pad Z=0.43). Pelvis tai Z=0.56 de lung & mong cham dem tu nhien khong clip
    hip_lift = 0.12 * depth if bad_form else 0.0
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.34, 0.56 + hip_lift)))

    torso_dir = Vector((0.0, 1.0, 0.02 - 0.18 * hip_lift)).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, Vector((0.0, 1.0, 0.02)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.99, 0.08)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, 0.99, 0.14)), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.22, -0.68, 0.092))
        knee_pole = Vector((sx * 0.28, -0.85, 0.55))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Good: ha don ve giua nguc duoi (Y=0.06, Z=0.66); Bad: don troi cao ve co/vai (Y=0.14, Z=0.66) + xoe khuyu 90 deg
    bar_y = 0.08 + (0.06 * depth if bad_form else -0.02 * depth)
    bar_z = 1.01 - 0.35 * depth
    _set_bone_world_head(arm_obj, "Bone_Barbell", Vector((0.0, bar_y, bar_z)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Dat co tay cach thanh don 5.2cm xuong duoi (-Z) de long ban tay om dung tam thanh don
        grip_target = Vector((sx * 0.34, bar_y, bar_z - 0.052))
        elbow_pole = Vector((sx * 0.96, 0.06, -0.26)) if bad_form else Vector((sx * 0.56, -0.68, -0.47))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            grip_target,
            elbow_pole,
            Vector((0.0, -1.0, 0.0)),
            Vector((0.0, -1.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", Vector((0.0, 0.0, 1.0)), Vector((sx * 1.0, 0.0, 0.0)))


def _export_and_save_outputs(
    arm_obj,
    export_paths: list[Path],
    blend_path: Path | None,
    primary: list[str],
    secondary: list[str],
    stabilizer: list[str],
    heatmap_preview: bool,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)
    # 1. Xuat file .glb voi mau co bap xam chuan (de Flutter to mau dong theo F09 / F23)
    apply_exercise_muscle_preview(primary, secondary, stabilizer, enabled=False)
    if export_paths:
        first_out = export_paths[0]
        base_mod.export_draco_glb(str(first_out), use_draco=False)
        for extra_out in export_paths[1:]:
            extra_out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(first_out, extra_out)
            print(f"[VigorAI] Copied identical .glb -> {extra_out}")

    # 2. Luu file .blend de kiem tra truc quan trong Blender (kem mau heatmap neu bat)
    apply_exercise_muscle_preview(primary, secondary, stabilizer, enabled=heatmap_preview)
    if "Anim_GoodForm" in bpy.data.actions:
        arm_obj.animation_data.action = bpy.data.actions["Anim_GoodForm"]
    if blend_path is not None:
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
        print(f"[VigorAI] Saved .blend -> {blend_path}")


def build_barbell_bench_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    _build_flat_bench_object(col, "Equip_Bench")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_bench_press(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Chest"],
        secondary=["Mat_Muscle_Shoulders", "Mat_Muscle_Triceps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 2. INCLINE DUMBBELL PRESS (Day nguc tren voi ta don - ghe doc 30 deg)
def _pose_incline_dumbbell_press(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    rad = math.radians(30.0)
    torso_dir = Vector((0.0, math.cos(rad), math.sin(rad))).normalized()
    chest_normal = Vector((0.0, -math.sin(rad), math.cos(rad))).normalized()

    # Dat Pelvis tren giao diem ghe ngoi & tua lung (khong clip vao dem)
    # Mat tua lung tai hinge_top = (0, -0.05, 0.42), back surface cach tam xuong song ~0.145m theo chest_normal
    # Khi bad_form: uon lung qua muc day hong ve phia truoc (-Y) va len (+Z)
    arch_offset = Vector((0.0, -0.07 * depth, 0.04 * depth)) if bad_form else Vector((0.0, 0.0, 0.0))
    pelvis_pos = Vector((0.0, -0.14, 0.56)) + arch_offset
    _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    spine_dir = Vector((0.0, math.cos(rad + (0.08 * depth if bad_form else 0.0)), math.sin(rad + (0.08 * depth if bad_form else 0.0)))).normalized()
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, spine_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.78, 0.63)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, 0.62, 0.78)), Vector((1.0, 0.0, 0.0)))

    # Hai chan dap vung tren san phia truoc ghe (-Y)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.22, -0.58, 0.092))
        knee_pole = Vector((sx * 0.27, -0.82, 0.56))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Vi tri vai trong World ~ (sx*0.20, 0.22, 0.89). Quy dao day thang len (+Z) & hoi hoi tu vao trong o dinh
    for side, sx in (("L", 1.0), ("R", -1.0)):
        if bad_form:
            # Bad: ha ta qua sau ve sau vai (+Y), xoe rong ngang khuyu 90 deg
            db_x = sx * (0.19 + 0.25 * depth)
            db_y = 0.08 + 0.14 * depth
            db_z = 1.38 - 0.44 * depth
            elbow_pole = Vector((sx * 0.96, 0.14, -0.24))
        else:
            # Good: hoi tu nhe o dinh (X=+/-0.15), ha xuong canh nguc tren (X=+/-0.32), khuyu khep 45 deg ve truoc (-Y)
            db_x = sx * (0.15 + 0.17 * depth)
            db_y = 0.05 + 0.04 * depth
            db_z = 1.38 - 0.39 * depth
            elbow_pole = Vector((sx * 0.56, -0.68, -0.46))

        db_pos = Vector((db_x, db_y, db_z))
        # Xoay nhe ta don vao trong 18 deg cho tu nhien o co tay
        yaw = math.radians(-sx * 18.0)
        db_ax = Vector((math.cos(yaw), math.sin(yaw), 0.0))
        db_ay = Vector((-math.sin(yaw), math.cos(yaw), 0.0))
        db_az = Vector((0.0, 0.0, 1.0))
        _set_bone_world_axes(arm_obj, f"Bone_Dumbbell_{side}", db_pos, db_ax, db_ay, db_az)

        # Dat co tay cach tam ta don 5.2cm xuong duoi (-Z) de long ban tay nam gon thanh ta don
        wrist_target = db_pos - Vector((0.0, 0.0, 0.052))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            Vector((0.0, -1.0, 0.0)),
            Vector((0.0, -1.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", Vector((0.0, 0.0, 1.0)), Vector((sx * 1.0, 0.0, 0.0)))


def build_incline_dumbbell_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_L")
    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    _build_incline_bench_object(col, "Equip_Bench_Incline", angle_deg=30.0)
    for side in ("L", "R"):
        db_obj = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db_obj, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_incline_dumbbell_press(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Chest"],
        secondary=["Mat_Muscle_Shoulders", "Mat_Muscle_Triceps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 3. CABLE CHEST FLY (Ep nguc voi may day cap)
def _pose_cable_chest_fly(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_l: Vector,
    pulley_r: Vector,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # Dung tu the chan truoc chan sau (Split stance) vung chac phia truoc thap cap (Y ~ 0)
    lean_deg = 12.0 + (24.0 * (1.0 - depth) if bad_form else 2.0 * (1.0 - depth))
    lean_rad = math.radians(lean_deg)
    pelvis_y = -0.05 - (0.10 * (1.0 - depth) if bad_form else 0.01)
    pelvis_z = 0.87 - (0.04 * (1.0 - depth) if bad_form else 0.0)
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))

    torso_dir = Vector((0.0, -math.sin(lean_rad), math.cos(lean_rad))).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for idx, bname in enumerate(("Spine_01", "Spine_02", "Spine_03")):
        extra = math.radians(10.0 * (idx + 1) * (1.0 - depth)) if bad_form else 0.0
        ang = lean_rad + extra
        _aim_bone_world(
            arm_obj,
            bname,
            Vector((0.0, -math.sin(ang), math.cos(ang))).normalized(),
            Vector((1.0, 0.0, 0.0)),
        )
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.22, 0.97)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.10, 0.99)), Vector((1.0, 0.0, 0.0)))

    # Chan trai buoc len truoc (-Y), chan phai tru sau (+Y)
    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_L",
        "Calf_L",
        Vector((0.17, -0.24, 0.092)),
        Vector((0.18, -0.95, 0.15)),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_R",
        "Calf_R",
        Vector((-0.17, 0.25, 0.092)),
        Vector((-0.18, -0.90, 0.15)),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_R", Vector((0.0, -0.88, -0.47)), Vector((1.0, 0.0, 0.0)))

    bpy.context.view_layer.update()
    shoulder_l = (arm_obj.matrix_world @ arm_obj.pose.bones["UpperArm_L"].matrix).translation
    shoulder_z = shoulder_l.z
    shoulder_y = shoulder_l.y

    # depth=0 -> 2 tay khep sat truoc nguc; depth=1 -> dang rong cung ~18 deg cang co nguc
    for side, sx, pulley_pos in (("L", 1.0, pulley_l), ("R", -1.0, pulley_r)):
        if bad_form:
            theta = math.radians(15.0 + 55.0 * depth)
            reach = 0.28 + 0.18 * depth
            hand_pos = Vector((
                sx * (0.09 + reach * math.sin(theta)),
                shoulder_y - reach * math.cos(theta) * 0.72,
                shoulder_z - 0.05 + 0.08 * depth,
            ))
            elbow_pole = Vector((sx * 0.85, 0.45, -0.20))
        else:
            theta = math.radians(10.0 + 72.0 * depth)
            arc_rx = 0.56
            arc_ry = 0.52
            hand_pos = Vector((
                sx * (0.08 + arc_rx * math.sin(theta)),
                shoulder_y - arc_ry * math.cos(theta),
                shoulder_z - 0.12 + 0.07 * depth,
            ))
            elbow_pole = Vector((sx * 0.65, 0.72, -0.22))

        grip_dir = (Vector((0.0, hand_pos.y - 0.14, hand_pos.z)) - hand_pos).normalized()
        wrist_pos = hand_pos - grip_dir * 0.045
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_pos,
            elbow_pole,
            Vector((0.0, 0.0, 1.0)),
            Vector((0.0, 0.0, 1.0)),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", grip_dir, Vector((0.0, 0.0, 1.0)))

        # Dat D-Handle tai long ban tay va huong day deo ve phia rong roc
        to_pulley = pulley_pos - hand_pos
        cable_dir = to_pulley.normalized()
        hx = Vector((0.0, 0.0, 1.0)).cross(cable_dir)
        if hx.length < 1e-4:
            hx = Vector((1.0, 0.0, 0.0))
        hx.normalize()
        hz = hx.cross(cable_dir).normalized()
        _set_bone_world_axes(arm_obj, f"Bone_Handle_{side}", hand_pos, hx, cable_dir, hz)

        handle_anchor = hand_pos + cable_dir * 0.105
        cable_vec = handle_anchor - pulley_pos
        cable_len = max(0.05, cable_vec.length)
        _set_bone_world_head(arm_obj, f"Bone_Cable_{side}", pulley_pos)
        _aim_bone_world(arm_obj, f"Bone_Cable_{side}", cable_vec.normalized(), Vector((0.0, 0.0, 1.0)))
        arm_obj.pose.bones[f"Bone_Cable_{side}"].scale = Vector((1.0, cable_len, 1.0))


def build_cable_chest_fly(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_l = Vector((1.08, 0.50, 1.40))
    pulley_r = Vector((-1.08, 0.50, 1.40))
    for bname in ("Bone_Handle_L", "Bone_Handle_R", "Bone_Cable_L", "Bone_Cable_R"):
        _add_ctrl_bone(arm_obj, bname)

    _, handles, cables = _build_cable_crossover_machine(col, pulley_l=pulley_l, pulley_r=pulley_r)
    for side in ("L", "R"):
        _parent_equip_to_bone(handles[side], arm_obj, f"Bone_Handle_{side}")
        _parent_equip_to_bone(cables[side], arm_obj, f"Bone_Cable_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_cable_chest_fly(arm_obj, d, bad_form=is_bad, pulley_l=pulley_l, pulley_r=pulley_r)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Chest"],
        secondary=["Mat_Muscle_Shoulders"],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Biceps"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 2: CO XO (LATS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 4. WIDE-GRIP PULL-UP (Hit xa don rong tay)
def _pose_wide_grip_pullup(
    arm_obj,
    depth: float,
    bad_form: bool,
    bar_y: float = -0.04,
    bar_z: float = 2.24,
    frame: int = 1,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # depth=0 -> dinh dong tac (cam cao hon xa); depth=1 -> duoi thang tay (dead hang)
    # bad_form -> Kipping Pull-up: dap chan vung nguoi lay da + khong len het bien do
    phase = 2.0 * math.pi * (frame - 1) / 99.0
    kip_y = -0.14 * math.sin(phase) if bad_form else 0.0
    eff_depth = min(1.0, 0.22 + 0.78 * depth) if bad_form else depth

    pelvis_z = 1.62 - 0.40 * eff_depth
    pelvis_y = 0.09 - 0.08 * eff_depth + kip_y
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))

    # Good: than nguoi vung chai, ngua nhe ~9 deg khi keo len dinh; Bad: dao dong lung manh theo da vung
    torso_tilt_y = (0.15 - 0.13 * eff_depth) + (0.26 * math.sin(phase) if bad_form else 0.0)
    torso_dir = Vector((0.0, torso_tilt_y, 1.0)).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))

    neck_dir = Vector((0.0, torso_tilt_y - 0.05, 1.0)).normalized()
    head_dir = Vector((0.0, -0.14 if bad_form else -0.05, 1.0)).normalized()
    _aim_bone_world(arm_obj, "Neck", neck_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", head_dir, Vector((1.0, 0.0, 0.0)))

    # Chan gap gon phia sau khi good form; vung manh ra truoc (-Y) / sau (+Y) khi kipping
    bpy.context.view_layer.update()
    leg_kick = math.sin(phase) if bad_form else 0.0
    for side, sx in (("L", 1.0), ("R", -1.0)):
        thigh_dir = Vector((sx * 0.06, -0.22 - 0.45 * max(0.0, leg_kick), -0.96)).normalized()
        calf_dir = Vector((-sx * 0.08, 0.62 - 0.35 * leg_kick, -0.78)).normalized()
        _aim_bone_world(arm_obj, f"Thigh_{side}", thigh_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, f"Calf_{side}", calf_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.65, -0.76)), Vector((1.0, 0.0, 0.0)))

    # Hai tay nam sap pronated (1.5x vai) tren thanh xa; giu cung mat phang gap khuyu tranh xoan co tay
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_target = Vector((sx * 0.38, bar_y, bar_z))
        finger_dir = Vector((0.0, -0.35, 0.94)).normalized()
        wrist_target = palm_target - finger_dir * 0.048 - Vector((0.0, -0.015, 0.0))
        elbow_pole = Vector((sx * 0.84, 0.12, -0.52))
        roll_arm = Vector((0.0, -0.65, 0.76)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            Vector((0.0, -0.82, 0.57)).normalized(),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_wide_grip_pullup(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    bar_y, bar_z = -0.04, 2.24
    _build_pullup_rack_object(col, bar_y=bar_y, bar_z=bar_z, name="Equip_PullupRack")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_wide_grip_pullup(arm_obj, d, bad_form=is_bad, bar_y=bar_y, bar_z=bar_z, frame=f)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats"],
        secondary=["Mat_Muscle_Biceps", "Mat_Muscle_Traps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 5. LAT PULLDOWN (Keo xo truoc nguc voi may cap)
def _pose_lat_pulldown(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # Ngoi tren dem (mat tren Z=0.49), dui luon duoi con lan khoa dui (Y=-0.02, Z=0.69), ban chan dat tren de thep (top Z=0.05)
    pelvis_y = 0.24 - (0.05 * (1.0 - depth) if bad_form else 0.0)
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.59)))

    # Good: nga nhe ~12 deg khi keo xuong nguc, ~3 deg khi tha len; Bad: nga nguoi qua sau (~44 deg) lay da
    if bad_form:
        lean_deg = 44.0 * (1.0 - 0.85 * depth)
    else:
        lean_deg = 12.0 - 9.0 * depth
    lean_rad = math.radians(lean_deg)
    torso_dir = Vector((0.0, math.sin(lean_rad), math.cos(lean_rad))).normalized()

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.25 * math.sin(lean_rad), 1.0)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.05, 1.0)), Vector((1.0, 0.0, 0.0)))

    # Hai chan ngoi vung: dui khoa duoi pad Z=0.69, ban chan cham mat de Z=0.05 (ankle Z=0.14)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, -0.14, 0.140))
        knee_pole = Vector((sx * 0.17, -0.85, 0.82))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Vi tri thanh Lat Bar (trong tam voi: keo thang xuong truoc xuong don 1.18m -> duoi tay het co 1.60m)
    bar_z = (1.08 if bad_form else 1.18) + (0.48 if bad_form else 0.42) * depth
    bar_y = 0.08
    bar_pos = Vector((0.0, bar_y, bar_z))
    _set_bone_world_axes(
        arm_obj,
        "Bone_LatBar",
        bar_pos,
        Vector((1.0, 0.0, 0.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
    )

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Tay nam sap doi xung tren phan be cong ngoai cua Lat Bar (X=+-0.38, Z=-0.048)
        palm_pos = bar_pos + Vector((sx * 0.38, 0.0, -0.048))
        finger_dir = Vector((-sx * 0.18, -0.32, 0.93)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.78, 0.35 if bad_form else 0.05, -0.52))
        roll_arm = Vector((0.0, -0.75, 0.66)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            Vector((0.0, -0.85, 0.52)).normalized(),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, -0.25, 0.0)))

    # Cap dong noi tu rong roc tren (pulley_pos) xuong moc thanh don (bar_pos + (0,0,0.04))
    bar_anchor = bar_pos + Vector((0.0, 0.0, 0.040))
    cable_vec = bar_anchor - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_Lat", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_Lat", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_Lat"].scale = Vector((1.0, cable_len, 1.0))


def build_lat_pulldown(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, 0.08, 2.20))
    for bname in ("Bone_LatBar", "Bone_Cable_Lat"):
        _add_ctrl_bone(arm_obj, bname)

    _, lat_bar, cable = _build_lat_pulldown_machine(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(lat_bar, arm_obj, "Bone_LatBar")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_Lat")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_lat_pulldown(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats"],
        secondary=["Mat_Muscle_Biceps", "Mat_Muscle_Traps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 6. STRAIGHT-ARM CABLE PULLDOWN (Keo xo tay thang voi day cap)
def _pose_straight_arm_cable_pulldown(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # Dung gap hong ~26 deg huong ve thap cap (-Y); Bad: lung uon/nhun theo da khi keo
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.06, 0.89)))

    hinge_deg = 28.0 - 16.0 * depth if bad_form else 26.0
    hinge_rad = math.radians(hinge_deg)
    torso_dir = Vector((0.0, -math.sin(hinge_rad), math.cos(hinge_rad))).normalized()

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.35, 0.94)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.25, 0.97)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan dung vung rong bang vai, goi hoi chung nhe
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.14, 0.05, 0.092))
        knee_pole = Vector((sx * 0.15, -0.85, 0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    bpy.context.view_layer.update()
    shoulder_mid_y = (arm_obj.matrix_world @ arm_obj.pose.bones["UpperArm_L"].matrix).translation.y
    shoulder_mid_z = (arm_obj.matrix_world @ arm_obj.pose.bones["UpperArm_L"].matrix).translation.z

    if bad_form:
        # Loi: gap khuyu tay >90 deg giong day tay sau (Tricep Pushdown)
        bar_y = shoulder_mid_y - 0.30 - 0.06 * math.sin(depth * math.pi)
        bar_z = shoulder_mid_z - 0.50 + 0.36 * depth
        elbow_pole = Vector((0.0, 0.85, -0.50))
        reach_dir = Vector((0.0, -1.0, -0.25 + 0.55 * depth)).normalized()
    else:
        # Dung ky thuat: giu canh tay gan nhu thang (~20 deg mem khuyu), quet cung tron quanh khop vai
        theta = math.radians(-72.0 + 94.0 * depth)
        arm_arc = 0.565
        bar_y = shoulder_mid_y - arm_arc * math.cos(theta)
        bar_z = shoulder_mid_z + arm_arc * math.sin(theta)
        elbow_pole = Vector((0.0, 0.65, -0.75))
        reach_dir = Vector((0.0, -arm_arc * math.cos(theta), arm_arc * math.sin(theta))).normalized()

    bar_pos = Vector((0.0, bar_y, bar_z))
    cable_vec_bar = pulley_pos - bar_pos
    cable_dir = cable_vec_bar.normalized()
    bar_x = Vector((1.0, 0.0, 0.0))
    bar_y_ax = cable_dir.cross(bar_x).normalized()
    _set_bone_world_axes(arm_obj, "Bone_StraightBar", bar_pos, bar_x, bar_y_ax, cable_dir)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Nam sap (overhand pronated) om phia tren Straight Bar (long ban tay huong xuong -Z, ngon cai huong vao trong)
        palm_pos = bar_pos + Vector((sx * 0.19, 0.0, 0.0))
        finger_dir = (reach_dir + Vector((0.0, -0.45, -0.35))).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        side_pole = Vector((sx * 0.25, elbow_pole.y, elbow_pole.z)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            side_pole,
            Vector((-sx * 0.25, -0.65, 0.72)).normalized(),
            Vector((-sx * 0.25, -0.65, 0.72)).normalized(),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))

    bar_anchor = bar_pos + cable_dir * 0.036
    c_vec = bar_anchor - pulley_pos
    c_len = max(0.05, c_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_Center", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_Center", c_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_Center"].scale = Vector((1.0, c_len, 1.0))


def build_straight_arm_cable_pulldown(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -0.96, 1.98))
    for bname in ("Bone_StraightBar", "Bone_Cable_Center"):
        _add_ctrl_bone(arm_obj, bname)

    _, straight_bar, cable = _build_single_cable_tower(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(straight_bar, arm_obj, "Bone_StraightBar")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_Center")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_straight_arm_cable_pulldown(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats"],
        secondary=["Mat_Muscle_Triceps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 3: CO LUNG GIUA & LUNG DUOI (MID & LOWER BACK) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 7. BARBELL BENT-OVER ROW (Gap nguoi keo ta don)
def _pose_barbell_bent_over_row(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # Hai chan dung rong bang vai, goi hoi chung, ban chan dat phang tren san
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.22 - (0.09 * (1.0 - depth) if bad_form else 0.0), 0.85)))

    if bad_form:
        # Loi: giat than nguoi dung thang (~18 deg) lay da & gu lung tren (>75 deg) khi ha ta
        base_deg = 18.0 + 38.0 * depth
        s1_dir = Vector((0.0, -math.sin(math.radians(base_deg)), math.cos(math.radians(base_deg)))).normalized()
        s2_dir = Vector((0.0, -math.sin(math.radians(base_deg + 14.0 * depth)), math.cos(math.radians(base_deg + 14.0 * depth)))).normalized()
        s3_dir = Vector((0.0, -math.sin(math.radians(base_deg + 24.0 * depth)), math.cos(math.radians(base_deg + 24.0 * depth)))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", s1_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", s1_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", s2_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", s3_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.82, 0.57)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.58, 0.81)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu lung phang co dinh 45 deg trong suot rep
        torso_dir = Vector((0.0, -0.7071, 0.7071)).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.60, 0.80)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.45, 0.89)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, 0.04, 0.092))
        knee_pole = Vector((sx * 0.17, -0.82, 0.48))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Thanh don di chuyen doc thang tu bung duoi/suon (depth=0) xuong duoi goi/giua ong dong (depth=1)
    bar_y = -0.11 - 0.05 * depth - (0.04 * (1.0 - depth) if bad_form else 0.0)
    bar_z = (0.94 if bad_form else 0.88) - (0.28 if bad_form else 0.22) * depth
    bar_pos = Vector((0.0, bar_y, bar_z))
    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.32, 0.0, 0.0))
        finger_dir = Vector((0.0, 0.15, -0.99)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * (0.78 if bad_form else 0.36), 0.65, 0.68))
        roll_arm = Vector((0.0, -0.85, -0.52)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_barbell_bent_over_row(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_bent_over_row(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats", "Mat_Muscle_Traps"],
        secondary=["Mat_Muscle_Biceps", "Mat_Muscle_Shoulders"],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Hamstrings"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 8. SEATED CABLE ROW (Ngoi keo cap hep tay)
def _pose_seated_cable_row(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.14, 0.54)))

    if bad_form:
        # Loi: ngả qua sau (~30 deg) khi keo va cong tron lung duoi (~52 deg) khi duoi tay ve truoc
        lean_s1 = math.radians(-30.0 + 54.0 * depth)
        lean_s2 = math.radians(-30.0 + 70.0 * depth)
        lean_s3 = math.radians(-30.0 + 84.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(lean_s1), math.cos(lean_s1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(lean_s1), math.cos(lean_s1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(lean_s2), math.cos(lean_s2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(lean_s3), math.cos(lean_s3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.35 * depth, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.18 * depth, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu than vung thang (~4 deg sau -> ~6 deg truoc)
        lean_rad = math.radians(-4.0 + 10.0 * depth)
        torso_dir = Vector((0.0, -math.sin(lean_rad), math.cos(lean_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.05, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan duoi hoi chung ~15 deg, ban chan dat len ban dap nghieng 22 deg
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.15, -0.64, 0.44))
        knee_pole = Vector((sx * 0.16, -0.25, 0.98))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.42, 0.91)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Vi tri tay cam V-Handle hep trung tinh (depth=0 -> sat ron; depth=1 -> duoi tay truoc mat)
    handle_y = -0.10 - (0.38 if bad_form else 0.24) * depth
    handle_z = 0.72 - (0.04 * depth if bad_form else -0.02 * depth)
    handle_pos = Vector((0.0, handle_y, handle_z))
    _set_bone_world_axes(
        arm_obj,
        "Bone_VHandle",
        handle_pos,
        Vector((1.0, 0.0, 0.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
    )

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Tay cam kieu neutral grip doi xung (long ban tay trai -X, phai +X; ngon cai huong +Z)
        palm_pos = handle_pos + Vector((sx * 0.085, 0.0, 0.0))
        finger_dir = Vector((0.0, -1.0, 0.0))
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * (0.65 if bad_form else 0.35), 0.80, -0.50))
        roll_arm = Vector((-sx * 0.55, 0.0, 0.83)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((0.0, 0.0, 1.0)))

    handle_anchor = handle_pos + Vector((0.0, -0.14, 0.0))
    cable_vec = handle_anchor - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_Row", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_Row", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_Row"].scale = Vector((1.0, cable_len, 1.0))


def build_seated_cable_row(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -1.06, 0.62))
    for bname in ("Bone_VHandle", "Bone_Cable_Row"):
        _add_ctrl_bone(arm_obj, bname)

    _, v_handle, cable = _build_seated_row_machine(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(v_handle, arm_obj, "Bone_VHandle")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_Row")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_seated_cable_row(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats", "Mat_Muscle_Traps"],
        secondary=["Mat_Muscle_Biceps", "Mat_Muscle_Shoulders"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 9. CONVENTIONAL DEADLIFT (Keo ta don tu san)
def _pose_barbell_deadlift(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # depth=0 -> dung khoa khop dinh (lockout); depth=1 -> dat banh ta R=0.215m xuong san Z=0
    hinge = depth ** 0.78
    if bad_form:
        # Loi: hong cao, lung duoi & lung tren cong chu C ro ret, thanh don troi xa ong dong
        pelvis_y = 0.04 + 0.16 * hinge
        pelvis_z = 0.94 - 0.24 * (depth ** 0.90)
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        a1 = math.radians(2.0 + 53.0 * hinge)
        a2 = math.radians(2.0 + 76.0 * hinge)
        a3 = math.radians(2.0 + 94.0 * hinge)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a2), math.cos(a2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a3), math.cos(a3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.78, 0.62)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.60, 0.80)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: lung phang co dinh goc gap hong muot, vai luon o phia tren thanh don
        pelvis_y = 0.04 + 0.28 * hinge
        pelvis_z = 0.94 - 0.41 * (depth ** 0.90)
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        torso_rad = math.radians(2.0 + 60.0 * hinge)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        neck_rad = math.radians(2.0 + 48.0 * hinge)
        head_rad = math.radians(2.0 + 36.0 * hinge)
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -math.sin(neck_rad), math.cos(neck_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -math.sin(head_rad), math.cos(head_rad))).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.14, 0.02, 0.092))
        knee_pole = Vector((sx * 0.15, -0.88, 0.42))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Banh ta ngoai R=0.215m -> tai depth=1 thanh don o Z=0.215m (cham san chuan xac!)
    bar_y = -0.11 - (0.14 * depth if bad_form else 0.0)
    bar_z = 0.885 - 0.670 * depth
    bar_pos = Vector((0.0, bar_y, bar_z))
    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Tay nam ngoai cang chan (X=+-0.27), giu canh tay duoi thang keo sat ong dong
        palm_pos = bar_pos + Vector((sx * 0.27, 0.0, 0.0))
        finger_dir = Vector((0.0, 0.12, -0.99)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.25, 0.85, 0.20))
        roll_arm = Vector((0.0, -0.95, 0.0)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_barbell_deadlift(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_deadlift(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats", "Mat_Muscle_Hamstrings", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Traps", "Mat_Muscle_Abs_Core"],
        stabilizer=["Mat_Muscle_Quads"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 4: CO VAI (SHOULDERS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 10. SEATED DUMBBELL SHOULDER PRESS (Ngoi day vai qua dau voi ta don - ghe doc 80 deg)
def _pose_dumbbell_shoulder_press(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    rad80 = math.radians(80.0)
    # Mat tua lung 80 deg: axis_up = (0, cos(80), sin(80)); BadForm uon lung ve truoc tach khoi dem
    arch_fwd = Vector((0.0, -0.08 * depth, 0.0)) if bad_form else Vector((0.0, 0.0, 0.0))
    pelvis_pos = Vector((0.0, -0.165, 0.58)) + arch_fwd
    _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)

    back_tilt = math.radians(72.0 if bad_form else 80.0)
    torso_dir = Vector((0.0, math.cos(back_tilt), math.sin(back_tilt))).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.21, -0.44, 0.092))
        knee_pole = Vector((sx * 0.24, -0.78, 0.60))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # depth=0 -> day dinh (khuyu hoi mem); depth=1 -> ha ngang tai (Good) hoac sau qua vai gay hai khop vai (Bad)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        if bad_form:
            db_pos = Vector((
                sx * (0.24 + 0.16 * depth),
                -0.12 - 0.02 * depth,
                1.56 - 0.54 * depth,
            ))
            elbow_pole = Vector((sx * 0.70, 0.62, -0.35))
        else:
            db_pos = Vector((
                sx * (0.23 + 0.14 * depth),
                -0.10 - 0.04 * depth,
                1.59 - 0.35 * depth,
            ))
            elbow_pole = Vector((sx * 0.85, -0.38, -0.35))

        finger_dir = Vector((0.0, -0.18, 0.98)).normalized()
        wrist_target = db_pos - finger_dir * 0.048
        roll_arm = Vector((0.0, -0.82, 0.57)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))

        # Dat ta don trong long ban tay xoay nhe theo mat phang xuong ba vai
        db_x = Vector((1.0, sx * 0.25, 0.0)).normalized()
        db_y = Vector((-sx * 0.25, 1.0, 0.0)).normalized()
        db_z = db_x.cross(db_y).normalized()
        _set_bone_world_axes(arm_obj, f"Bone_Dumbbell_{side}", db_pos, db_x, db_y, db_z)


def build_dumbbell_shoulder_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_L")
    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    _build_incline_bench_object(col, "Equip_Bench_Upright80", angle_deg=80.0)
    for side in ("L", "R"):
        db = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_dumbbell_shoulder_press(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Shoulders"],
        secondary=["Mat_Muscle_Triceps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 11. DUMBBELL LATERAL RAISE (Dang ta don sang ngang cho vai giua)
def _pose_dumbbell_lateral_raise(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    if bad_form:
        # Loi: vung hong giat da (-18 deg sau -> +22 deg truoc) va nhun vai qua cao tren tai voi khuyu gap ~65 deg
        pelvis_y = -0.10 + 0.18 * depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.92)))
        lean_deg = -18.0 + 40.0 * depth
        torso_dir = Vector((0.0, -math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.05, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu than on dinh, do nhe ~6 deg ve truoc
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.02, 0.92)))
        torso_dir = Vector((0.0, -0.10, 0.995)).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.06, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.15, 0.0, 0.092))
        knee_pole = Vector((sx * 0.16, -0.85, 0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    bpy.context.view_layer.update()
    # depth=0 -> dinh dang ngang vai (~85 deg); depth=1 -> ha ben hong (~12 deg, khong cham dui)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        shoulder_pos = (arm_obj.matrix_world @ arm_obj.pose.bones[f"UpperArm_{side}"].matrix).translation
        if bad_form:
            elev_deg = 122.0 - 110.0 * depth
            arc_r = 0.42 + 0.08 * depth
        else:
            elev_deg = 85.0 - 73.0 * depth
            arc_r = 0.555

        elev_rad = math.radians(elev_deg)
        scap_ang = math.radians(20.0)
        horiz = math.sin(elev_rad)
        vert = -math.cos(elev_rad)
        arm_out = Vector((
            sx * horiz * math.cos(scap_ang),
            -horiz * math.sin(scap_ang) - 0.06,
            vert,
        )).normalized()
        db_pos = shoulder_pos + arm_out * arc_r

        finger_dir = arm_out
        thumb_dir = Vector((0.0, -1.0, 0.0))
        wrist_target = db_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.20, 0.85, 0.45))
        roll_arm = Vector((0.0, -0.85, -0.52)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, thumb_dir)

        # Thanh ta don nam doc truoc-sau trong long ban tay (axis_x = thumb_dir)
        db_x = thumb_dir
        db_y = finger_dir.cross(db_x).normalized()
        db_z = db_x.cross(db_y).normalized()
        _set_bone_world_axes(arm_obj, f"Bone_Dumbbell_{side}", db_pos, db_x, db_y, db_z)


def build_dumbbell_lateral_raise(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_L")
    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    for side in ("L", "R"):
        db = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_dumbbell_lateral_raise(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Shoulders"],
        secondary=["Mat_Muscle_Traps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 12. CABLE FACE PULL (Keo cap huong mat cho vai sau)
def _pose_cable_face_pull(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector,
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    # Tu the Split Stance giu thang bang vung chac truoc thap cap ngang tran
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.08, 0.90)))
    lean_deg = (20.0 * (1.0 - 0.65 * depth)) if bad_form else 7.0
    torso_dir = Vector((0.0, math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan truoc L tru truoc (-0.14), chan sau R tru vung (+0.18)
    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_L",
        "Calf_L",
        Vector((0.15, -0.14, 0.092)),
        Vector((0.16, -0.92, 0.35)),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_R",
        "Calf_R",
        Vector((-0.15, 0.18, 0.092)),
        Vector((-0.16, -0.88, 0.35)),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_R", Vector((0.0, -0.90, -0.44)), Vector((1.0, 0.0, 0.0)))

    # depth=0 -> keo xoay ngoai cao ngang tran/tai; depth=1 -> duoi tay ve phia rong roc
    if bad_form:
        hand_x_abs = 0.22 - 0.12 * depth
        hand_y = -0.06 - 0.30 * depth
        hand_z = 1.44 + 0.10 * depth
    else:
        hand_x_abs = 0.31 - 0.21 * depth
        hand_y = 0.07 - 0.43 * depth
        hand_z = 1.62 - 0.08 * depth

    # Tinh giao diem chia nhanh day thung co chieu dai nhanh co dinh L_rope = 0.42m
    mid = Vector((0.0, hand_y, hand_z))
    to_pulley = (pulley_pos - mid).normalized()
    split_dist = math.sqrt(max(0.08 * 0.08, 0.42 * 0.42 - hand_x_abs * hand_x_abs))
    split_pos = mid + to_pulley * split_dist

    hub_x = Vector((1.0, 0.0, 0.0))
    hub_z = hub_x.cross(to_pulley).normalized()
    _set_bone_world_axes(arm_obj, "Bone_RopeHub", split_pos, hub_x, to_pulley, hub_z)

    cable_vec = split_pos - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_FacePull", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_FacePull", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_FacePull"].scale = Vector((1.0, cable_len, 1.0))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        hand_pos = Vector((sx * hand_x_abs, hand_y, hand_z))
        to_split = (split_pos - hand_pos).normalized()
        finger_dir = to_split
        thumb_dir = Vector((0.0, 0.35 * (1.0 - depth), 1.0)).normalized()
        wrist_target = hand_pos - finger_dir * 0.048

        if bad_form:
            # Loi: khuyu tay tut thap hon co tay (< vai)
            elbow_pole = Vector((sx * 0.38, 0.30, -0.90))
            roll_arm = Vector((0.0, -0.88, -0.45)).normalized()
        else:
            # Dung ky thuat: keo khuyu rong ra sau ngang vai va xoay ngoai cang tay ben thai duong
            elbow_pole = Vector((sx * 0.92, 0.48, 0.12))
            roll_arm = Vector((0.0, -0.78, 0.62)).normalized()

        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, thumb_dir)

        rope_end = hand_pos - to_split * 0.055
        b_vec = rope_end - split_pos
        b_len = max(0.05, b_vec.length)
        _set_bone_world_head(arm_obj, f"Bone_RopeBranch_{side}", split_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeBranch_{side}", b_vec.normalized(), Vector((0.0, 0.0, 1.0)))
        arm_obj.pose.bones[f"Bone_RopeBranch_{side}"].scale = Vector((1.0, b_len, 1.0))

        knob_pos = hand_pos - to_split * 0.062
        _set_bone_world_head(arm_obj, f"Bone_RopeKnob_{side}", knob_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeKnob_{side}", (-to_split).normalized(), Vector((0.0, 0.0, 1.0)))


def build_cable_face_pull(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -1.12, 1.58))
    for bname in (
        "Bone_RopeHub",
        "Bone_Cable_FacePull",
        "Bone_RopeBranch_L",
        "Bone_RopeBranch_R",
        "Bone_RopeKnob_L",
        "Bone_RopeKnob_R",
    ):
        _add_ctrl_bone(arm_obj, bname)

    _, rope_hub, cable, branches, knobs = _build_cable_rope_station(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(rope_hub, arm_obj, "Bone_RopeHub")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_FacePull")
    for side in ("L", "R"):
        _parent_equip_to_bone(branches[side], arm_obj, f"Bone_RopeBranch_{side}")
        _parent_equip_to_bone(knobs[side], arm_obj, f"Bone_RopeKnob_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_cable_face_pull(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Shoulders", "Mat_Muscle_Traps"],
        secondary=["Mat_Muscle_Back_Lats"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 5: CO TAY TRUOC (BICEPS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 13. BARBELL BICEP CURL (Dung cuon ta don)
def _pose_barbell_bicep_curl(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi: dua hong & lac lung ra sau (-22 deg o dinh, +16 deg o day), hat khuyu tay ra truoc som
        pelvis_y = -0.09 + 0.14 * depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.92)))
        lean_deg = -22.0 + 38.0 * depth
        torso_dir = Vector((0.0, -math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu than vung chac, co dinh khuyu tay hai ben suon
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.02, 0.92)))
        torso_dir = Vector((0.0, -0.02, 1.0)).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.03, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, 0.02, 0.092))
        knee_pole = Vector((sx * 0.17, -0.85, 0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Cung tron quanh khuyu tay co dinh tai (elbow_y=-0.03, elbow_z=1.14), R=0.295m; BadForm hat thanh don xa & cao
    curl_deg = (138.0 if bad_form else 128.0) - (118.0 if bad_form else 106.0) * depth
    curl_rad = math.radians(curl_deg)
    forearm_dir = Vector((0.0, -math.sin(curl_rad), -math.cos(curl_rad))).normalized()

    if bad_form:
        elbow_y = -0.15 + 0.12 * depth
        elbow_z = 1.24 - 0.10 * depth
        bar_pos = Vector((0.0, elbow_y, elbow_z)) + forearm_dir * 0.295
        elbow_pole = Vector((0.0, -0.65, -0.72))
    else:
        elbow_y, elbow_z = -0.03, 1.145
        bar_pos = Vector((0.0, elbow_y, elbow_z)) + forearm_dir * 0.295
        elbow_pole = Vector((0.0, 0.85, -0.50))

    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    roll_upper = Vector((0.0, -1.0, 0.15)).normalized()
    roll_lower = forearm_dir.cross(Vector((1.0, 0.0, 0.0))).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.22, 0.0, 0.0))
        wrist_target = palm_pos - forearm_dir * 0.048
        side_pole = Vector((sx * 0.18, elbow_pole.y, elbow_pole.z)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            side_pole,
            roll_upper,
            roll_lower,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", forearm_dir, Vector((sx * 1.0, 0.0, 0.0)))


def build_barbell_bicep_curl(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_bicep_curl(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Biceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Shoulders"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 14. DUMBBELL HAMMER CURL (Cuon ta don kieu bua - nam trung tinh)
def _pose_dumbbell_hammer_curl(
    arm_obj,
    depth: float,
    bad_form: bool,
    frame: int = 1,
) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi: tha roi ta nhanh pha ha (eccentric) roi vang ta ra sau hong & giat lung lay da
        eff_depth = min(1.0, depth ** 0.42) if frame < 45 else depth
        pelvis_y = -0.06 + 0.12 * eff_depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.92)))
        lean_deg = -16.0 + 34.0 * eff_depth
        torso_dir = Vector((0.0, -math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        curl_deg = 128.0 - 146.0 * eff_depth
        elbow_pole_y = -0.45 if curl_deg > 75.0 else 0.78
    else:
        eff_depth = depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.02, 0.92)))
        torso_dir = Vector((0.0, -0.03, 1.0)).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.03, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        curl_deg = 126.0 - 112.0 * eff_depth
        elbow_pole_y = 0.85

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, 0.02, 0.092))
        knee_pole = Vector((sx * 0.17, -0.85, 0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    curl_rad = math.radians(curl_deg)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        elbow_x = sx * (0.245 + 0.020 * eff_depth)
        elbow_y = -0.08 + 0.10 * eff_depth if bad_form else -0.02
        elbow_anchor = Vector((elbow_x, elbow_y, 1.145))
        forearm_dir = Vector((-sx * 0.04, -math.sin(curl_rad), -math.cos(curl_rad))).normalized()
        db_pos = elbow_anchor + forearm_dir * 0.295

        hinge_inside = forearm_dir.cross(Vector((1.0, 0.0, 0.0))).normalized()
        wrist_target = db_pos - forearm_dir * 0.048
        side_pole = Vector((sx * 0.20, elbow_pole_y, -0.50)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            side_pole,
            Vector((sx * 0.72, -0.68, 0.12)).normalized(),
            hinge_inside,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", forearm_dir, hinge_inside)

        # Dat ta don theo kieu Hammer (axis_x = hinge_inside doc theo ngon cai - ngon ut)
        db_x = hinge_inside
        db_y = Vector((1.0, 0.0, 0.0))
        db_z = db_x.cross(db_y).normalized()
        _set_bone_world_axes(arm_obj, f"Bone_Dumbbell_{side}", db_pos, db_x, db_y, db_z)


def build_dumbbell_hammer_curl(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_L")
    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    for side in ("L", "R"):
        db = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_dumbbell_hammer_curl(arm_obj, d, bad_form=is_bad, frame=f)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Biceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 15. INCLINE DUMBBELL CURL (Cuon ta don tren ghe nghieng 45 deg)
def _pose_incline_dumbbell_curl(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    # Dem tua lung 45 deg (hinge_top = (0, -0.05, 0.42)): tam xuong song ap khit mat dem tai (-0.06, 0.61)
    pelvis_pos = Vector((0.0, -0.06, 0.61))
    _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)

    torso_dir = Vector((0.0, 0.7071, 0.7071)).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))

    neck_dir = Vector((0.0, 0.25 if bad_form else 0.58, 0.97 if bad_form else 0.81)).normalized()
    head_dir = Vector((0.0, 0.12 if bad_form else 0.45, 0.99 if bad_form else 0.89)).normalized()
    _aim_bone_world(arm_obj, "Neck", neck_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", head_dir, Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.22, -0.52, 0.092))
        knee_pole = Vector((sx * 0.25, -0.82, 0.56))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Good: canh tay tren buong thang dung sau than, khuyu co dinh tai (sx*0.26, 0.29, 0.69);
    # Bad: khuyu lao manh ve phia truoc (y = -0.02, z = 0.88) khi cuon ta len
    curl_deg = 126.0 - 110.0 * depth
    curl_rad = math.radians(curl_deg)
    forearm_dir = Vector((0.0, -math.sin(curl_rad), -math.cos(curl_rad))).normalized()

    roll_upper = Vector((0.0, -1.0, 0.15)).normalized()
    roll_lower = forearm_dir.cross(Vector((1.0, 0.0, 0.0))).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        if bad_form:
            elbow_anchor = Vector((sx * 0.24, 0.02 + 0.26 * depth, 0.88 - 0.19 * depth))
            elbow_pole = Vector((sx * 0.25, -0.75 + 1.40 * depth, -0.60))
        else:
            elbow_anchor = Vector((sx * 0.265, 0.285, 0.69))
            elbow_pole = Vector((sx * 0.18, 0.75, -0.64))

        db_pos = elbow_anchor + forearm_dir * 0.295
        wrist_target = db_pos - forearm_dir * 0.048
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_upper,
            roll_lower,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", forearm_dir, Vector((sx * 1.0, 0.0, 0.0)))

        # Dat ta don nam ngang (supinated grip, axis_x = +X)
        db_x = Vector((1.0, 0.0, 0.0))
        db_y = roll_lower
        db_z = db_x.cross(db_y).normalized()
        _set_bone_world_axes(arm_obj, f"Bone_Dumbbell_{side}", db_pos, db_x, db_y, db_z)


def build_incline_dumbbell_curl(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_L")
    _add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    _build_incline_bench_object(col, "Equip_Bench_Incline45", angle_deg=45.0)
    for side in ("L", "R"):
        db = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_incline_dumbbell_curl(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Biceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Shoulders"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 6: CO TAY SAU (TRICEPS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 16. TRICEP ROPE PUSHDOWN (Day cap day thung xuong)
def _pose_cable_tricep_pushdown(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector,
) -> None:
    _reset_pose(arm_obj)

    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.05, 0.91)))
    lean_deg = (8.0 + 20.0 * depth) if bad_form else 12.0
    torso_dir = Vector((0.0, -math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.18, 0.98)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.10, 0.995)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.15, 0.04, 0.092))
        knee_pole = Vector((sx * 0.16, -0.82, 0.46))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # depth=0 -> day khoa tay duoi hoan toan & tach day thung hai ben dui; depth=1 -> gap khuỷu ~105 deg
    if bad_form:
        hand_x_abs = 0.20 - 0.08 * depth
        hand_y = -0.25 - 0.12 * depth
        hand_z = 0.90 + 0.42 * depth
    else:
        hand_x_abs = 0.24 - 0.13 * depth
        hand_y = -0.22 - 0.10 * depth
        hand_z = 0.86 + 0.38 * depth

    mid = Vector((0.0, hand_y, hand_z))
    to_pulley = (pulley_pos - mid).normalized()
    split_dist = math.sqrt(max(0.08 * 0.08, 0.36 * 0.36 - hand_x_abs * hand_x_abs))
    split_pos = mid + to_pulley * split_dist

    hub_x = Vector((1.0, 0.0, 0.0))
    hub_z = hub_x.cross(to_pulley).normalized()
    _set_bone_world_axes(arm_obj, "Bone_RopeHub", split_pos, hub_x, to_pulley, hub_z)

    cable_vec = split_pos - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_FacePull", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_FacePull", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_FacePull"].scale = Vector((1.0, cable_len, 1.0))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        hand_pos = Vector((sx * hand_x_abs, hand_y, hand_z))
        if bad_form:
            elbow_anchor = Vector((sx * 0.34, -0.24, 1.22 + 0.08 * depth))
            elbow_pole = Vector((sx * 0.92, -0.25, 0.25))
        else:
            elbow_anchor = Vector((sx * 0.21, -0.09, 1.13))
            elbow_pole = Vector((sx * 0.18, 0.85, -0.50))

        forearm_dir = (hand_pos - elbow_anchor).normalized()
        hinge_inside = forearm_dir.cross(Vector((1.0, 0.0, 0.0))).normalized()
        wrist_target = hand_pos - forearm_dir * 0.048
        roll_upper = Vector((sx * 0.65 if bad_form else 0.0, -0.80, 0.20)).normalized()

        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_upper,
            hinge_inside,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", forearm_dir, hinge_inside)

        to_split = (split_pos - hand_pos).normalized()
        rope_end = hand_pos - to_split * 0.055
        b_vec = rope_end - split_pos
        b_len = max(0.05, b_vec.length)
        _set_bone_world_head(arm_obj, f"Bone_RopeBranch_{side}", split_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeBranch_{side}", b_vec.normalized(), Vector((0.0, 0.0, 1.0)))
        arm_obj.pose.bones[f"Bone_RopeBranch_{side}"].scale = Vector((1.0, b_len, 1.0))

        knob_pos = hand_pos - to_split * 0.062
        _set_bone_world_head(arm_obj, f"Bone_RopeKnob_{side}", knob_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeKnob_{side}", (-to_split).normalized(), Vector((0.0, 0.0, 1.0)))


def build_cable_tricep_pushdown(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -0.76, 1.98))
    for bname in (
        "Bone_RopeHub",
        "Bone_Cable_FacePull",
        "Bone_RopeBranch_L",
        "Bone_RopeBranch_R",
        "Bone_RopeKnob_L",
        "Bone_RopeKnob_R",
    ):
        _add_ctrl_bone(arm_obj, bname)

    _, rope_hub, cable, branches, knobs = _build_cable_rope_station(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(rope_hub, arm_obj, "Bone_RopeHub")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_FacePull")
    for side in ("L", "R"):
        _parent_equip_to_bone(branches[side], arm_obj, f"Bone_RopeBranch_{side}")
        _parent_equip_to_bone(knobs[side], arm_obj, f"Bone_RopeKnob_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_cable_tricep_pushdown(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Triceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 17. SKULL CRUSHER (Nam ha ta don qua tran)
def _pose_skull_crusher(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    # Nam ngua vung chai tren ghe Bench phang (top pad Z=0.43)
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.34, 0.56)))
    torso_dir = Vector((0.0, 1.0, 0.02)).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.99, 0.08)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, 0.99, 0.14)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.22, -0.68, 0.092))
        knee_pole = Vector((sx * 0.28, -0.85, 0.55))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Cung tron quanh khuyu giu hoi nga ve sau dau (0, 0.22, 0.86); depth=0 -> duoi dinh; depth=1 -> ha qua tran
    ext_deg = 12.0 + 92.0 * depth
    ext_rad = math.radians(ext_deg)
    if bad_form:
        bar_pos = Vector((0.0, 0.14 + 0.24 * depth, 1.13 - 0.34 * depth))
        elbow_pole_base = Vector((0.0, -0.15, 0.15))
        forearm_dir = (bar_pos - Vector((0.0, 0.20, 0.80))).normalized()
    else:
        forearm_dir = Vector((0.0, math.sin(ext_rad), math.cos(ext_rad))).normalized()
        bar_pos = Vector((0.0, 0.22, 0.86)) + forearm_dir * 0.295
        elbow_pole_base = Vector((0.0, -0.85, 0.45))

    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    roll_arm = Vector((0.0, -math.cos(ext_rad), math.sin(ext_rad))).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.19, 0.0, 0.0))
        wrist_target = palm_pos - forearm_dir * 0.048
        side_pole = Vector((sx * (0.95 if bad_form else 0.14), elbow_pole_base.y, elbow_pole_base.z)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            side_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", forearm_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_skull_crusher(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    _build_flat_bench_object(col, "Equip_Bench")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_skull_crusher(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Triceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Shoulders", "Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 18. OVERHEAD DUMBBELL TRICEP EXTENSION (Duoi ta don qua dau hai tay)
def _pose_overhead_dumbbell_tricep_ext(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi: uon lung duoi ra sau (-16 deg) va xoe hai khuyu sang ngang 90 deg
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.06, 0.92)))
        lean_rad = math.radians(16.0 - 8.0 * depth)
        torso_dir = Vector((0.0, math.sin(lean_rad), math.cos(lean_rad))).normalized()
    else:
        # Dung ky thuat: do nhe ~8.5 deg giu core chac tranh va cham lung tren/so & xac lap khuyu khep sat dau
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.02, 0.92)))
        torso_dir = Vector((0.0, -0.15, 0.988)).normalized()

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.07, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.10, 0.995)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, 0.02, 0.092))
        knee_pole = Vector((sx * 0.17, -0.85, 0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Ta don dung thang (axis_x = +Z) giu phia sau dau (Y=+0.13..+0.25) de khong xuyen qua so & vai
    if bad_form:
        db_pos = Vector((0.0, 0.20 + 0.08 * depth, 1.91 - 0.33 * depth))
        elbow_pole_base = Vector((0.0, 0.10, 0.20))
    else:
        db_pos = Vector((0.0, 0.13 + 0.11 * depth, 1.90 - 0.42 * depth))
        elbow_pole_base = Vector((0.0, -0.78, 0.58))

    _set_bone_world_axes(
        arm_obj,
        "Bone_Dumbbell",
        db_pos,
        Vector((0.0, 0.0, 1.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((-1.0, 0.0, 0.0)),
    )

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Hai ban tay om phia duoi banh ta tren (+Z+0.065)
        palm_pos = db_pos + Vector((sx * 0.048, 0.0, 0.065))
        finger_dir = Vector((-sx * 0.35, 0.15 + 0.35 * depth, 0.92 - 0.30 * depth)).normalized()
        wrist_target = palm_pos - finger_dir * 0.045
        side_pole = Vector((sx * (0.96 if bad_form else 0.24), elbow_pole_base.y, elbow_pole_base.z)).normalized()
        roll_arm = Vector((0.0, -0.82, 0.57)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            side_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((0.0, 1.0, 0.0)))


def build_overhead_dumbbell_tricep_ext(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Dumbbell")
    db = _build_dumbbell_object(col, "Equip_Dumbbell")
    _parent_equip_to_bone(db, arm_obj, "Bone_Dumbbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_overhead_dumbbell_tricep_ext(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Triceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 7: CO DUI TRUOC (QUADRICEPS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 19. BARBELL SQUAT (Ganh ta don - Barbell Back Squat)
def _pose_barbell_squat(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    if bad_form:
        # Loi: Chum goi vao trong (Knee Valgus), nhac got chan & gap lung chu C (Good-Morning Squat)
        pelvis_y = 0.02 + 0.24 * depth
        pelvis_z = 0.90 - 0.31 * depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        a_pel = math.radians(5.0 + 30.0 * depth)
        a_sp1 = math.radians(5.0 + 36.0 * depth)
        a_sp2 = math.radians(5.0 + 44.0 * depth)
        a_sp3 = math.radians(5.0 + 52.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a_sp1), math.cos(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a_sp2), math.cos(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a_sp3), math.cos(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.45, 0.89)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.25, 0.97)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: ha hong sau duoi song song (0.90 -> 0.46), lung phang nghieng 28 deg
        pelvis_y = 0.02 + 0.24 * depth
        pelvis_z = 0.90 - 0.44 * depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        torso_rad = math.radians(4.0 + 24.0 * depth)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        neck_rad = math.radians(5.0 + 15.0 * depth)
        head_rad = math.radians(3.0 + 9.0 * depth)
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -math.sin(neck_rad), math.cos(neck_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -math.sin(head_rad), math.cos(head_rad))).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        if bad_form:
            ankle_target = Vector((sx * 0.175, 0.06 - 0.05 * depth, 0.092 + 0.075 * depth))
            knee_pole = Vector((-sx * 0.65 * depth, -0.75, 0.10)).normalized()
            foot_dir = Vector((sx * 0.08, -0.82, -0.57)).normalized()
        else:
            ankle_target = Vector((sx * 0.175, 0.06, 0.092))
            knee_pole = Vector((sx * 0.28, -0.95, 0.14)).normalized()
            foot_dir = Vector((sx * 0.16, -0.93, -0.34)).normalized()

        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

    # Dat thanh don ta tren be cau vai sau (Spine_03 tail)
    bpy.context.view_layer.update()
    sp3_mat = arm_obj.matrix_world @ arm_obj.pose.bones["Spine_03"].matrix
    sp3_head = sp3_mat.translation
    sp3_up = sp3_mat.col[1].to_3d().normalized()
    sp3_back = sp3_mat.col[0].to_3d().normalized()
    bar_pos = sp3_head + sp3_up * 0.105 + sp3_back * (0.070 if bad_form else 0.078)
    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.35, -0.01, -0.01))
        finger_dir = Vector((-sx * 0.10, -0.82, 0.56)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.42, 0.86, -0.28)).normalized()
        roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((sx * 1.0, 0.0, 0.0)))


def build_barbell_squat(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    _build_squat_rack_object(col, "Equip_SquatRack")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_squat(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Quads", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Hamstrings"],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Back_Lats"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 20. LEG PRESS (Dap dui tren may - Machine Leg Press)
def _pose_leg_press(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    ang40 = math.radians(40.0)
    track_dir = Vector((0.0, -math.cos(ang40), math.sin(ang40))).normalized()
    plate_up = Vector((0.0, math.sin(ang40), math.cos(ang40))).normalized()
    track_origin = Vector((0.0, 0.34, 0.36))

    if bad_form:
        # Loi: dinh khoa cung goi, cuon nhac xuong cut (Butt Wink) giu lung tren tua dem, goi chum & tay roi tay nam
        s = 0.896 - 0.396 * depth
        butt_wink = Vector((0.0, -0.03 * depth, 0.065 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.34, 0.35)) + butt_wink)
        a_pel = math.radians(35.0 - 16.0 * depth)
        a_sp1 = math.radians(35.0 - 8.0 * depth)
        a_sp2 = math.radians(35.0 - 2.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, math.cos(a_pel), math.sin(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, math.cos(a_sp1), math.sin(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, math.cos(a_sp2), math.sin(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, math.cos(math.radians(35.0)), math.sin(math.radians(35.0)))).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: lung & mong ep chat dem ghe 35 deg, khong khoa goi o dinh (s=0.87 -> 0.615)
        s = 0.870 - 0.255 * depth
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.34, 0.35)))
        back_dir = Vector((0.0, math.cos(math.radians(35.0)), math.sin(math.radians(35.0)))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", back_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, back_dir, Vector((1.0, 0.0, 0.0)))

    _aim_bone_world(arm_obj, "Neck", Vector((0.0, math.cos(math.radians(52.0)), math.sin(math.radians(52.0)))).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, math.cos(math.radians(66.0)), math.sin(math.radians(66.0)))).normalized(), Vector((1.0, 0.0, 0.0)))

    sled_pos = track_origin + track_dir * s
    _set_bone_world_axes(
        arm_obj,
        "Bone_LegPressSled",
        sled_pos,
        Vector((1.0, 0.0, 0.0)),
        plate_up,
        track_dir,
    )

    foot_dir = (plate_up * 0.94 + track_dir * 0.34).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = sled_pos + Vector((sx * 0.165, 0.0, 0.0)) - track_dir * 0.085 - plate_up * 0.03
        if bad_form:
            knee_pole = Vector((-sx * 0.45 * depth, plate_up.y, plate_up.z)).normalized()
        else:
            knee_pole = Vector((sx * 0.18, plate_up.y, plate_up.z)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

        # Tay nam hai ben hong (GoodForm) hoac buong tay dat len goi (BadForm)
        if bad_form:
            wrist_target = Vector((sx * 0.15, 0.05 - 0.02 * depth, 0.62 + 0.08 * depth))
            finger_dir = Vector((-sx * 0.15, -0.78, 0.60)).normalized()
            elbow_pole = Vector((sx * 0.85, 0.40, -0.32)).normalized()
            roll_arm = Vector((0.0, -1.0, 0.0))
        else:
            wrist_target = Vector((sx * 0.26, 0.24, 0.355))
            finger_dir = Vector((-sx * 0.30, -0.35, -0.89)).normalized()
            elbow_pole = Vector((sx * 0.50, 0.80, -0.32)).normalized()
            roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((0.0, 0.0, 1.0)))


def build_leg_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_LegPressSled")
    _, sled = _build_leg_press_machine(col)
    _parent_equip_to_bone(sled, arm_obj, "Bone_LegPressSled")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_leg_press(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Quads", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Hamstrings"],
        stabilizer=[],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 21. LEG EXTENSION (Ngoi da dui truoc voi may - Leg Extension)
def _pose_leg_extension(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    pivot_pos = Vector((0.0, -0.37, 0.56))
    if bad_form:
        # Loi: truot mong ve truoc & nhac khoi dem (+10 cm) lay da than tren khong cham tua lung
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.06 - 0.13 * depth, 0.56 + 0.10 * depth)))
        back_rad = math.radians(80.0 - 18.0 * depth)
        torso_dir = Vector((0.0, math.cos(back_rad), math.sin(back_rad))).normalized()
    else:
        # Dung ky thuat: ngoi co dinh mong & lung tren ghe nghieng 80 deg, hai tay bam chat tay nam
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.06, 0.56)))
        back_rad = math.radians(80.0)
        torso_dir = Vector((0.0, math.cos(back_rad), math.sin(back_rad))).normalized()

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.08, 0.996)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.06, 0.998)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Goc cang chan: 84 deg (gap) -> 4 deg (duoi thang siet co dui truoc)
    ang_rad = math.radians(84.0 * (1.0 - depth) + (2.0 if bad_form else 4.0) * depth)
    down_dir = Vector((0.0, -math.cos(ang_rad), -math.sin(ang_rad))).normalized()
    front_normal = Vector((0.0, -math.sin(ang_rad), math.cos(ang_rad))).normalized()
    axis_x = Vector((1.0, 0.0, 0.0))
    axis_z = axis_x.cross(down_dir).normalized()

    _set_bone_world_axes(arm_obj, "Bone_LegExtArm", pivot_pos, axis_x, down_dir, axis_z)

    foot_dir = (front_normal * 0.94 + down_dir * 0.34).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        knee_center = Vector((sx * 0.138, pivot_pos.y + 0.015, pivot_pos.z - 0.005))
        ankle_target = knee_center + down_dir * 0.402
        knee_pole = Vector((sx * 0.10, -0.70, 0.70)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

        # Tay bam tay nam ben hong hoac buong long khi giat nguoi (BadForm)
        if bad_form:
            wrist_target = Vector((sx * 0.25, 0.02 + 0.08 * depth, 0.62 + 0.12 * depth))
            elbow_pole = Vector((sx * 0.75, 0.65, -0.10)).normalized()
        else:
            wrist_target = Vector((sx * 0.26, -0.04, 0.545))
            elbow_pole = Vector((sx * 0.52, 0.80, -0.28)).normalized()
        finger_dir = Vector((0.0, -0.88, -0.47)).normalized()
        roll_arm = Vector((-sx * 0.85, 0.0, -0.52)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((0.0, 0.0, 1.0)))


def build_leg_extension(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_LegExtArm")
    _, lever_arm = _build_leg_extension_machine(col, pivot_pos=Vector((0.0, -0.37, 0.56)))
    _parent_equip_to_bone(lever_arm, arm_obj, "Bone_LegExtArm")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_leg_extension(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Quads"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 8: CO DUI SAU (HAMSTRINGS) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 22. ROMANIAN DEADLIFT (Keo ta don kieu Romania)
def _pose_romanian_deadlift(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    hinge = depth ** 0.80
    if bad_form:
        # Loi: gap goi sau thanh Squat, cuon cong lung chu C va de ta troi xa ong dong
        pelvis_y = 0.03 + 0.19 * hinge
        pelvis_z = 0.91 - 0.34 * (depth ** 0.90)
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        a1 = math.radians(2.0 + 54.0 * hinge)
        a2 = math.radians(2.0 + 78.0 * hinge)
        a3 = math.radians(2.0 + 95.0 * hinge)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a2), math.cos(a2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a3), math.cos(a3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.78, 0.62)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.58, 0.81)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: Hip Hinge day mong ve sau (Y=+0.30, Z=0.77), chung nhe goi ~15 deg, lung phang 72 deg
        pelvis_y = 0.03 + 0.27 * hinge
        pelvis_z = 0.91 - 0.14 * hinge
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        torso_rad = math.radians(2.0 + 70.0 * hinge)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        neck_rad = math.radians(2.0 + 56.0 * hinge)
        head_rad = math.radians(2.0 + 44.0 * hinge)
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -math.sin(neck_rad), math.cos(neck_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -math.sin(head_rad), math.cos(head_rad))).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.14, 0.02, 0.092))
        knee_pole = Vector((sx * 0.14, -0.92, 0.20 if bad_form else 0.35)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # RDL khong cham san: thanh don truot sat truoc dui -> ngang giua ong dong (Z=0.42)
    bar_y = -0.105 - (0.15 * depth if bad_form else 0.02 * depth)
    bar_z = 0.885 - 0.465 * depth
    bar_pos = Vector((0.0, bar_y, bar_z))
    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.26, 0.0, 0.0))
        finger_dir = Vector((0.0, 0.12, -0.99)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.24, 0.86, 0.18)).normalized()
        roll_arm = Vector((0.0, -0.95, 0.0)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_romanian_deadlift(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_romanian_deadlift(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Hamstrings", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Back_Lats"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 23. LYING LEG CURL MACHINE (Nam sap moc dui sau voi may)
def _pose_leg_curl_machine(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    pivot_pos = Vector((0.0, 0.47, 0.49))
    if bad_form:
        # Loi: nhom hong/xuong chau khoi dem (+10.5 cm) tao goc gap chu V an gian luc khi moc ta
        pelvis_pos = Vector((0.0, 0.055, 0.545 + 0.105 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(-18.0 * depth)
        a_sp1 = math.radians(-12.0 * depth)
        a_sp2 = math.radians(-5.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.cos(a_pel), math.sin(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.cos(a_sp1), math.sin(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.cos(a_sp2), math.sin(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -1.0, 0.02)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: nam sap ep sat bung & hong len mat dem (Z_top=0.45), dau huong ve -Y
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.055, 0.545)))
        prone_dir = Vector((0.0, -1.0, 0.0))
        _aim_bone_world(arm_obj, "Pelvis", prone_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, prone_dir, Vector((1.0, 0.0, 0.0)))

    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.96, 0.28)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.82, 0.57)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Can moc cang chan: 8 deg (duoi thang) -> 102 deg (moc sat mong)
    curl_rad = math.radians(8.0 * (1.0 - depth) + 102.0 * depth)
    calf_dir = Vector((0.0, math.cos(curl_rad), math.sin(curl_rad))).normalized()
    axis_x = Vector((1.0, 0.0, 0.0))
    axis_z = axis_x.cross(calf_dir).normalized()  # huong ve phia sau Achilles (+Z o 8 deg, -Y o 90 deg)
    _set_bone_world_axes(arm_obj, "Bone_LyingCurlArm", pivot_pos, axis_x, calf_dir, axis_z)

    # Giu vector truoc cang chan lien tuc (khong xoan co chan khi vuot 90 deg)
    front_shin = calf_dir.cross(axis_x).normalized()
    foot_dir = (front_shin * 0.94 + calf_dir * 0.34).normalized()

    for side, sx in (("L", 1.0), ("R", -1.0)):
        knee_anchor = Vector((sx * 0.135, pivot_pos.y, pivot_pos.z + 0.012))
        ankle_target = knee_anchor + calf_dir * 0.402
        knee_pole = Vector((sx * 0.05, 0.0, -1.0)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

        # Hai tay nam om tay cam truoc dau ghe (X=+-0.23, Y=-0.52, Z=0.36)
        wrist_target = Vector((sx * 0.245, -0.495, 0.395))
        finger_dir = Vector((-sx * 0.45, -0.35, -0.82)).normalized()
        elbow_pole = Vector((sx * 0.72, 0.35, 0.59)).normalized()
        roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_leg_curl_machine(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_LyingCurlArm")
    _, curl_arm = _build_lying_leg_curl_machine(col, pivot_pos=Vector((0.0, 0.47, 0.49)))
    _parent_equip_to_bone(curl_arm, arm_obj, "Bone_LyingCurlArm")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_leg_curl_machine(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Hamstrings"],
        secondary=["Mat_Muscle_Calves"],
        stabilizer=[],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 24. SEATED LEG CURL (Ngoi moc dui sau voi may)
def _pose_seated_leg_curl(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    pivot_pos = Vector((0.0, -0.37, 0.56))
    if bad_form:
        # Loi: nhom lung & vai ve phia truoc tach khoi dem tua (80 -> 114 deg) dung da giat ta
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.06 - 0.04 * depth, 0.56 + 0.03 * depth)))
        back_rad = math.radians(80.0 + 34.0 * depth)
        torso_dir = Vector((0.0, math.cos(back_rad), math.sin(back_rad))).normalized()
    else:
        # Dung ky thuat: ngoi tua chat lung vao dem (80 deg), dui khoa duoi dem, tay nam thanh cam tren goi
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.06, 0.56)))
        back_rad = math.radians(80.0)
        torso_dir = Vector((0.0, math.cos(back_rad), math.sin(back_rad))).normalized()

    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.02 - 0.25 * depth if bad_form else 0.06, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.08 - 0.15 * depth if bad_form else -0.06, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Goc cang chan duoi truoc (8 deg) -> moc sau duoi gam ghe (96 deg duoi phuong ngang)
    ang_rad = math.radians(8.0 * (1.0 - depth) + (90.0 if bad_form else 96.0) * depth)
    down_dir = Vector((0.0, -math.cos(ang_rad), -math.sin(ang_rad))).normalized()
    axis_x = Vector((1.0, 0.0, 0.0))
    axis_z = axis_x.cross(down_dir).normalized()  # phia sau bap chan / got Achilles
    _set_bone_world_axes(arm_obj, "Bone_SeatedCurlArm", pivot_pos, axis_x, down_dir, axis_z)

    front_shin = down_dir.cross(axis_x).normalized()
    foot_dir = (front_shin * 0.94 + down_dir * 0.34).normalized()

    for side, sx in (("L", 1.0), ("R", -1.0)):
        knee_center = Vector((sx * 0.138, pivot_pos.y + 0.015, pivot_pos.z - 0.005))
        ankle_target = knee_center + down_dir * 0.402
        knee_pole = Vector((sx * 0.08, -0.70, 0.70)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

        # Hai tay nam om thanh cam phia tren dem khoa dui (X=+-0.19, Y=-0.25, Z=0.725)
        wrist_target = Vector((sx * 0.19, -0.22, 0.755))
        finger_dir = Vector((0.0, -0.65, -0.76)).normalized()
        elbow_pole = Vector((sx * 0.65, 0.50, -0.55)).normalized()
        roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_seated_leg_curl(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_SeatedCurlArm")
    _, curl_arm = _build_seated_leg_curl_machine(col, pivot_pos=Vector((0.0, -0.37, 0.56)))
    _parent_equip_to_bone(curl_arm, arm_obj, "Bone_SeatedCurlArm")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_seated_leg_curl(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Hamstrings"],
        secondary=["Mat_Muscle_Calves"],
        stabilizer=[],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 9: CO MONG (GLUTES) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 25. BARBELL HIP THRUST (Day hong voi ta don)
def _pose_barbell_hip_thrust(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    if bad_form:
        # Loi: dat chan qua gan mong (Y=-0.22), uon vong qua muc that lung o dinh (Z=0.54) va ngua co/dau ra sau
        pelvis_pos = Vector((0.0, 0.02 - 0.02 * depth, 0.25 + 0.29 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(30.0 - 20.0 * depth)
        a_sp1 = math.radians(30.0 - 30.0 * depth)
        a_sp2 = math.radians(30.0 - 38.0 * depth)
        a_sp3 = math.radians(30.0 - 44.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, math.cos(a_pel), math.sin(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, math.cos(a_sp1), math.sin(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, math.cos(a_sp2), math.sin(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, math.cos(a_sp3), math.sin(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        neck_dir = Vector((0.0, 0.94, -0.34 if depth > 0.3 else 0.34)).normalized()
        head_dir = Vector((0.0, 0.78, -0.62 if depth > 0.3 else 0.62)).normalized()
        _aim_bone_world(arm_obj, "Neck", neck_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", head_dir, Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: ba vai tua co dinh tren mep ghe (Y=+0.39, Z=0.405), day hong ngang goi (Z=0.48), thu cam nhin truoc
        pelvis_pos = Vector((0.0, 0.02 - 0.02 * depth, 0.25 + 0.23 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        torso_rad = math.radians(30.0 * (1.0 - depth) + 2.0 * depth)
        torso_dir = Vector((0.0, math.cos(torso_rad), math.sin(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        neck_rad = math.radians(52.0 - 10.0 * depth)
        head_rad = math.radians(74.0 - 8.0 * depth)
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, math.cos(neck_rad), math.sin(neck_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, math.cos(head_rad), math.sin(head_rad))).normalized(), Vector((1.0, 0.0, 0.0)))

    ankle_y = -0.22 if bad_form else -0.40
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.165, ankle_y, 0.092))
        knee_pole = Vector((sx * 0.20, -0.35, 0.92)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Thanh don ta dat tren nep gap hong truoc (bar_pos cao hon mat truoc xuong chau tranh xuyen bung/dui)
    bpy.context.view_layer.update()
    pel_mat = arm_obj.matrix_world @ arm_obj.pose.bones["Pelvis"].matrix
    pel_head = pel_mat.translation
    pel_up = pel_mat.col[1].to_3d().normalized()
    pel_ant = (-pel_mat.col[0].to_3d()).normalized()
    bar_pos = pel_head + pel_ant * 0.120 + pel_up * 0.025
    _set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.30, 0.0, 0.0))
        finger_dir = Vector((0.0, -0.62, -0.78)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.55, 0.65, -0.52)).normalized()
        roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_barbell_hip_thrust(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_ctrl_bone(arm_obj, "Bone_Barbell")
    _build_hip_thrust_bench_object(col, "Equip_HipThrustBench")
    barbell = _build_barbell_object(col, "Equip_Barbell")
    _parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_hip_thrust(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Hamstrings", "Mat_Muscle_Quads"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 26. DUMBBELL WALKING LUNGE (Buoc chung chan voi ta don)
def _pose_walking_lunge(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi: buoc ngan, lao manh goi truoc qua mui chan + chum goi vao trong (Knee Valgus) & do lung 34 deg
        pelvis_pos = Vector((0.0, -0.02 - 0.16 * depth, 0.80 - 0.25 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        torso_rad = math.radians(6.0 + 28.0 * depth)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.25, 0.97)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.14, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))

        # Chan trai buoc truoc ngan + nhac got; chan phai sau
        ankle_l = Vector((0.135, -0.22, 0.092 + 0.055 * depth))
        pole_l = Vector((-0.55 * depth, -0.82, 0.10)).normalized()
        _solve_two_bone_ik_world(arm_obj, "Thigh_L", "Calf_L", ankle_l, pole_l, Vector((1.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.84, -0.54)).normalized(), Vector((1.0, 0.0, 0.0)))

        ankle_r = Vector((-0.135, 0.28, 0.145))
        pole_r = Vector((-0.08, -0.88, -0.46)).normalized()
        _solve_two_bone_ik_world(arm_obj, "Thigh_R", "Calf_R", ankle_r, pole_r, Vector((1.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Foot_R", Vector((0.0, -0.60, -0.80)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: buoc tach chan rong chuan 90-90 deg, goi truoc khong qua mui chan, than tren thang ~6 deg
        pelvis_pos = Vector((0.0, -0.02, 0.80 - 0.29 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        torso_rad = math.radians(6.0)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.08, 0.996)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.05, 0.998)).normalized(), Vector((1.0, 0.0, 0.0)))

        ankle_l = Vector((0.145, -0.34, 0.092))
        pole_l = Vector((0.12, -0.98, 0.14)).normalized()
        _solve_two_bone_ik_world(arm_obj, "Thigh_L", "Calf_L", ankle_l, pole_l, Vector((1.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

        ankle_r = Vector((-0.145, 0.34, 0.145))
        pole_r = Vector((-0.08, -0.88, -0.46)).normalized()
        _solve_two_bone_ik_world(arm_obj, "Thigh_R", "Calf_R", ankle_r, pole_r, Vector((1.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Foot_R", Vector((0.0, -0.60, -0.80)).normalized(), Vector((1.0, 0.0, 0.0)))

    # 2 ta don cam doc hai ben hong (tranh cham dui & mong)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        db_y = pelvis_pos.y - (0.20 * depth if bad_form else 0.03)
        db_z = pelvis_pos.z - (0.04 if bad_form else 0.01)
        db_pos = Vector((sx * 0.275, db_y, db_z))
        _set_bone_world_axes(
            arm_obj,
            f"Bone_Dumbbell_{side}",
            db_pos,
            Vector((0.0, 1.0, 0.0)),
            Vector((-sx * 1.0, 0.0, 0.0)),
            Vector((0.0, 0.0, 1.0)),
        )
        wrist_target = db_pos + Vector((0.0, 0.0, 0.045))
        elbow_pole = Vector((sx * 0.65, 0.72, 0.22)).normalized()
        roll_arm = Vector((0.0, -0.85, 0.52)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", Vector((0.0, 0.0, -1.0)), Vector((0.0, 1.0, 0.0)))


def build_walking_lunge(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    for side in ("L", "R"):
        _add_ctrl_bone(arm_obj, f"Bone_Dumbbell_{side}")
        db = _build_dumbbell_object(col, f"Equip_Dumbbell_{side}")
        _parent_equip_to_bone(db, arm_obj, f"Bone_Dumbbell_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_walking_lunge(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Quads", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Hamstrings"],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Calves"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 27. CABLE GLUTE KICKBACK (Da chan ra sau voi day cap)
def _pose_cable_glute_kickback(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector = Vector((-0.14, -0.82, 0.16)),
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    if bad_form:
        # Loi: vong lung duoi qua muc & vung chan da qua cao (ankle Z=0.68) an gian bang that lung
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.06, 0.87)))
        a_pel = math.radians(28.0 - 16.0 * depth)
        a_sp1 = math.radians(26.0 - 28.0 * depth)
        a_sp2 = math.radians(24.0 - 34.0 * depth)
        a_sp3 = math.radians(22.0 - 20.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a_sp1), math.cos(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a_sp2), math.cos(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a_sp3), math.cos(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.35, 0.94)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.15, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu than tren nghieng phang co dinh 24 deg, hai tay vin thanh cam truoc nguc
        _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.06, 0.87)))
        torso_rad = math.radians(24.0)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.28, 0.96)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.14, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan tru trai (L) bam san vung chac tai (0.14, -0.10, 0.092)
    ankle_l = Vector((0.14, -0.10, 0.092))
    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_L",
        "Calf_L",
        ankle_l,
        Vector((0.14, -0.92, 0.36)).normalized(),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Chan da phai (R) duoi thang co kiem soat ra sau (BadForm vong that lung qua muc & vang thang ra xa Y=+0.66, Z=0.50)
    if bad_form:
        ankle_r = Vector((-0.14, -0.14 + 0.80 * depth, 0.14 + 0.36 * depth))
        foot_r_dir = Vector((0.0, -0.62, -0.78)).normalized()
    else:
        ankle_r = Vector((-0.14, -0.16 + 0.68 * depth, 0.14 + 0.30 * depth))
        foot_r_dir = Vector((0.0, -0.82 + 0.24 * depth, -0.57 - 0.10 * depth)).normalized()

    _solve_two_bone_ik_world(
        arm_obj,
        "Thigh_R",
        "Calf_R",
        ankle_r,
        Vector((-0.14, -0.88, -0.45)).normalized(),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    _aim_bone_world(arm_obj, "Foot_R", foot_r_dir, Vector((1.0, 0.0, 0.0)))

    # Hai tay nam thanh vin truoc nguc (Y=-0.64, Z=1.18)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = Vector((sx * 0.17, -0.64, 1.195))
        finger_dir = Vector((0.0, -0.58, -0.81)).normalized()
        wrist_target = palm_pos - finger_dir * 0.045
        elbow_pole = Vector((sx * 0.45, 0.50, -0.74)).normalized()
        roll_arm = Vector((0.0, 1.0, 0.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))

    # Dai co chan (AnkleStrap) om co chan phai (R) & day cap dong toi rong roc thap (pulley_pos)
    bpy.context.view_layer.update()
    calf_mat = arm_obj.matrix_world @ arm_obj.pose.bones["Calf_R"].matrix
    calf_y = calf_mat.col[1].to_3d().normalized()
    strap_pos = ankle_r - calf_y * 0.045
    strap_y = Vector((0.0, -1.0, 0.0))
    strap_z = calf_y
    strap_x = strap_y.cross(strap_z).normalized()
    strap_y = strap_z.cross(strap_x).normalized()
    _set_bone_world_axes(arm_obj, "Bone_AnkleStrap", strap_pos, strap_x, strap_y, strap_z)

    cable_anchor = strap_pos + strap_y * 0.068
    cable_vec = cable_anchor - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_Kickback", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_Kickback", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_Kickback"].scale = Vector((1.0, cable_len, 1.0))


def build_cable_glute_kickback(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((-0.14, -0.82, 0.16))
    for bname in ("Bone_AnkleStrap", "Bone_Cable_Kickback"):
        _add_ctrl_bone(arm_obj, bname)

    _, ankle_strap, cable = _build_cable_kickback_station(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(ankle_strap, arm_obj, "Bone_AnkleStrap")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_Kickback")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_cable_glute_kickback(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Hamstrings"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# NHOM 10: CO BUNG & LOI (ABS & CORE) - 3 BAI TRONG gym.txt
# ---------------------------------------------------------------------------

# 28. HANGING LEG RAISE (Treo nguoi nang chan)
def _pose_hanging_leg_raise(
    arm_obj,
    depth: float,
    bad_form: bool,
    bar_y: float = -0.02,
    bar_z: float = 2.28,
) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi: dung dua vung nguoi lay da (Kipping Swing): f=0 vung ra sau, f=1 quang hong ra truoc & gap goi cau tha
        pelvis_pos = Vector((0.0, 0.18 - 0.40 * depth, 1.15 + 0.09 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_torso = math.radians(18.0 - 44.0 * depth)  # +18 (ngả trước) -> -26 (ngả mạnh ra sau)
        torso_dir = Vector((0.0, -math.sin(a_torso), math.cos(a_torso))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.10, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.14, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))

        # Chan vung sau o day (0.48) roi co goi nem thap o dinh (Z=0.98)
        for side, sx in (("L", 1.0), ("R", -1.0)):
            ankle_target = Vector((sx * 0.12, 0.44 - 0.88 * depth, 0.46 + 0.54 * depth))
            knee_pole = Vector((sx * 0.18, -0.96, 0.15)).normalized()
            _solve_two_bone_ik_world(
                arm_obj,
                f"Thigh_{side}",
                f"Calf_{side}",
                ankle_target,
                knee_pole,
                Vector((1.0, 0.0, 0.0)),
                Vector((1.0, 0.0, 0.0)),
            )
            _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.65, -0.76)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: treo on dinh khong dung dua, cuon xuong chau nhe (+22 deg) & nang thang hai chan cao qua ngang
        pelvis_pos = Vector((0.0, -0.05 * depth, 1.18 + 0.03 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(-2.0 - 22.0 * depth)  # posterior pelvic tilt (-Y = +0.37)
        a_sp1 = math.radians(-2.0 - 12.0 * depth)
        a_sp2 = math.radians(-2.0 - 4.0 * depth)
        a_sp3 = math.radians(2.0)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a_sp1), math.cos(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a_sp2), math.cos(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a_sp3), math.cos(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.04, 0.999)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.08, 0.996)).normalized(), Vector((1.0, 0.0, 0.0)))

        # Cung quy dao nang thang chan tu -86 deg (duoi thang) len +14 deg (cao tren phuong ngang)
        ang_rad = math.radians(-86.0 * (1.0 - depth) + 14.0 * depth)
        leg_r = 0.802 - 0.042 * depth
        for side, sx in (("L", 1.0), ("R", -1.0)):
            ankle_target = Vector((
                sx * 0.115,
                pelvis_pos.y - leg_r * math.cos(ang_rad),
                pelvis_pos.z + leg_r * math.sin(ang_rad),
            ))
            knee_pole = Vector((sx * 0.08, -0.82, 0.56)).normalized()
            _solve_two_bone_ik_world(
                arm_obj,
                f"Thigh_{side}",
                f"Calf_{side}",
                ankle_target,
                knee_pole,
                Vector((1.0, 0.0, 0.0)),
                Vector((1.0, 0.0, 0.0)),
            )
            foot_dir = Vector((0.0, -0.45 * (1.0 - depth) + 0.65 * depth, -0.89 + 0.25 * depth)).normalized()
            _aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

    # Hai tay nam chac thanh xa rong bang vai (X=+-0.24, bar_y=-0.02, bar_z=2.28)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = Vector((sx * 0.24, bar_y, bar_z))
        finger_dir = Vector((0.0, -0.35, 0.94)).normalized()
        wrist_target = palm_pos - finger_dir * 0.048
        elbow_pole = Vector((sx * 0.72, 0.16, -0.67)).normalized()
        roll_arm = Vector((0.0, -0.75, 0.66)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((-sx * 1.0, 0.0, 0.0)))


def build_hanging_leg_raise(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    bar_y, bar_z = -0.02, 2.28
    _build_pullup_rack_object(col, bar_y=bar_y, bar_z=bar_z, name="Equip_PullupRack")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_hanging_leg_raise(arm_obj, d, bad_form=is_bad, bar_y=bar_y, bar_z=bar_z)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Abs_Core"],
        secondary=["Mat_Muscle_Back_Lats"],
        stabilizer=["Mat_Muscle_Quads"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 29. CABLE CRUNCH (Quy goi gap bung voi day cap)
def _pose_cable_crunch(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector = Vector((0.0, -0.76, 1.88)),
) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)

    if bad_form:
        # Loi: giu lung thang do, gap khop hong ha mong ngoi lui ve sau (Pelvis Y=+0.24, Z=0.31)
        pelvis_pos = Vector((0.0, 0.00 + 0.24 * depth, 0.465 - 0.155 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        torso_rad = math.radians(22.0 + 36.0 * depth)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu hong cao co dinh, cuon tron tung dot song nguc (24 -> 96 deg) bang co bung
        pelvis_pos = Vector((0.0, 0.00 + 0.04 * depth, 0.465 - 0.015 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(18.0 + 6.0 * depth)
        a_sp1 = math.radians(22.0 + 22.0 * depth)
        a_sp2 = math.radians(26.0 + 44.0 * depth)
        a_sp3 = math.radians(30.0 + 66.0 * depth)
        a_neck = math.radians(34.0 + 70.0 * depth)
        a_head = math.radians(38.0 + 72.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a_sp1), math.cos(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a_sp2), math.cos(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a_sp3), math.cos(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -math.sin(a_neck), math.cos(a_neck))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -math.sin(a_head), math.cos(a_head))).normalized(), Vector((1.0, 0.0, 0.0)))

    # Quy hai goi tren mat tham (Z >= 0.018), mui chan bam tham o Y=+0.30
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.15, 0.30, 0.195))
        knee_pole = Vector((sx * 0.12, -0.96, -0.25)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.42, -0.91)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Cap nhat ma tran Head de khoa hai dau day thung & tay ngay hai ben thai duong
    bpy.context.view_layer.update()
    head_mat = arm_obj.matrix_world @ arm_obj.pose.bones["Head"].matrix
    head_base = head_mat.translation
    head_up = head_mat.col[1].to_3d().normalized()
    head_front = (-head_mat.col[0].to_3d()).normalized()

    mid_grip = head_base + head_up * 0.095 + head_front * 0.045
    to_pulley = (pulley_pos - mid_grip).normalized()
    split_pos = mid_grip + to_pulley * 0.25

    hub_x = Vector((1.0, 0.0, 0.0))
    hub_z = hub_x.cross(to_pulley).normalized()
    _set_bone_world_axes(arm_obj, "Bone_RopeHub", split_pos, hub_x, to_pulley, hub_z)

    cable_vec = split_pos - pulley_pos
    cable_len = max(0.05, cable_vec.length)
    _set_bone_world_head(arm_obj, "Bone_Cable_FacePull", pulley_pos)
    _aim_bone_world(arm_obj, "Bone_Cable_FacePull", cable_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_FacePull"].scale = Vector((1.0, cable_len, 1.0))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        hand_pos = mid_grip + Vector((sx * 0.145, 0.0, 0.0))
        to_split = (split_pos - hand_pos).normalized()
        wrist_target = hand_pos - to_split * 0.045
        elbow_pole = Vector((sx * 0.42, -0.86, -0.28)).normalized()
        roll_arm = Vector((0.0, -0.75, 0.65)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", to_split, Vector((-sx * 1.0, 0.0, 0.0)))

        rope_end = hand_pos - to_split * 0.055
        b_vec = rope_end - split_pos
        b_len = max(0.05, b_vec.length)
        _set_bone_world_head(arm_obj, f"Bone_RopeBranch_{side}", split_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeBranch_{side}", b_vec.normalized(), Vector((0.0, 0.0, 1.0)))
        arm_obj.pose.bones[f"Bone_RopeBranch_{side}"].scale = Vector((1.0, b_len, 1.0))

        knob_pos = hand_pos - to_split * 0.062
        _set_bone_world_head(arm_obj, f"Bone_RopeKnob_{side}", knob_pos)
        _aim_bone_world(arm_obj, f"Bone_RopeKnob_{side}", (-to_split).normalized(), Vector((0.0, 0.0, 1.0)))


def build_cable_crunch(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -0.76, 1.88))
    ctrl_bones = [
        "Bone_RopeHub",
        "Bone_Cable_FacePull",
        "Bone_RopeBranch_L",
        "Bone_RopeBranch_R",
        "Bone_RopeKnob_L",
        "Bone_RopeKnob_R",
    ]
    for bname in ctrl_bones:
        _add_ctrl_bone(arm_obj, bname)

    _build_kneeling_mat_object(col, name="Equip_KneelingMat", center_y=0.06, length_y=1.10)
    _, rope_hub, cable, branches, knobs = _build_cable_rope_station(col, pulley_pos=pulley_pos)
    _parent_equip_to_bone(rope_hub, arm_obj, "Bone_RopeHub")
    _parent_equip_to_bone(cable, arm_obj, "Bone_Cable_FacePull")
    for side in ("L", "R"):
        _parent_equip_to_bone(branches[side], arm_obj, f"Bone_RopeBranch_{side}")
        _parent_equip_to_bone(knobs[side], arm_obj, f"Bone_RopeKnob_{side}")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_cable_crunch(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            _key_all_pose_bones(arm_obj, f, key_scale=True)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Abs_Core"],
        secondary=[],
        stabilizer=["Mat_Muscle_Shoulders"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# 30. FOREARM PLANK (Chong khuyu tay giu thang nguoi)
def _pose_plank(arm_obj, depth: float, bad_form: bool) -> None:
    _reset_pose(arm_obj)

    if bad_form:
        # Loi kep: day mong nhong cao chu V (depth=0, Z=0.49) -> sup vong that lung xuong thap (depth=1, Z=0.19)
        pelvis_z = 0.49 - 0.30 * depth
        pelvis_pos = Vector((0.0, -0.05, pelvis_z))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(-18.0 + 36.0 * depth)
        a_sp1 = math.radians(-14.0 + 34.0 * depth)
        a_sp2 = math.radians(-8.0 + 34.0 * depth)
        a_sp3 = math.radians(-2.0 + 30.0 * depth)
        _aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.cos(a_pel), math.sin(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.cos(a_sp1), math.sin(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.cos(a_sp2), math.sin(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.cos(a_sp3), math.sin(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.82, 0.57)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.70, 0.71)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu than & chan tao thanh duong thang (~9 deg) tu mui chan toi vai, nhip tho siet core
        pelvis_pos = Vector((0.0, -0.06, 0.285 + 0.014 * depth))
        _set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        plank_rad = math.radians(9.0 + 1.0 * depth)
        torso_dir = Vector((0.0, -math.cos(plank_rad), math.sin(plank_rad))).normalized()
        _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.96, 0.28)).normalized(), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.99, 0.14)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan duoi thang ra sau, mui chan chong dung tren mat tham (khong xuyen xuong duoi Z=0.018)
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.13, 0.72, 0.17))
        knee_pole = Vector((sx * 0.06, 0.0, -1.0)).normalized()
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.62, -0.785)).normalized(), Vector((1.0, 0.0, 0.0)))

        # Chong hai khuyu tay ngay duoi vai, cang tay dat song song tren mat tham toi Y=-0.785
        wrist_target = Vector((sx * 0.18, -0.785, 0.075))
        finger_dir = Vector((-sx * 0.08, -0.996, 0.0)).normalized()
        elbow_pole = Vector((sx * 0.08, 0.85, -0.52)).normalized()
        roll_arm = Vector((0.0, 0.0, 1.0))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            Vector((0.0, -1.0, 0.0)),
            roll_arm,
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", finger_dir, Vector((0.0, 0.0, 1.0)))


def build_plank(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _build_kneeling_mat_object(col, name="Equip_Mat", center_y=0.04, length_y=1.88)

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_plank(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Abs_Core"],
        secondary=["Mat_Muscle_Shoulders", "Mat_Muscle_Glutes"],
        stabilizer=[],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# Registry, GLB Verification & Manifest / Mock JSON Sync
# ---------------------------------------------------------------------------
EXERCISE_SPECS: dict[str, dict] = {
    "BARBELL_BENCH_PRESS": {
        "file_name": "barbell_bench_press.glb",
        "blend_name": "chest_barbell_bench_press.blend",
        "builder": build_barbell_bench_press,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "INCLINE_DUMBBELL_PRESS": {
        "file_name": "incline_dumbbell_press.glb",
        "blend_name": "chest_incline_dumbbell_press.blend",
        "builder": build_incline_dumbbell_press,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "CABLE_CHEST_FLY": {
        "file_name": "cable_chest_fly.glb",
        "blend_name": "chest_cable_chest_fly.blend",
        "builder": build_cable_chest_fly,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "WIDE_GRIP_PULLUP": {
        "file_name": "wide_grip_pullup.glb",
        "blend_name": "lats_wide_grip_pullup.blend",
        "builder": build_wide_grip_pullup,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "LAT_PULLDOWN": {
        "file_name": "lat_pulldown.glb",
        "blend_name": "lats_lat_pulldown.blend",
        "builder": build_lat_pulldown,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "STRAIGHT_ARM_CABLE_PULLDOWN": {
        "file_name": "straight_arm_cable_pulldown.glb",
        "blend_name": "lats_straight_arm_cable_pulldown.blend",
        "builder": build_straight_arm_cable_pulldown,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "BARBELL_BENT_OVER_ROW": {
        "file_name": "barbell_bent_over_row.glb",
        "blend_name": "back_barbell_bent_over_row.blend",
        "builder": build_barbell_bent_over_row,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "SEATED_CABLE_ROW": {
        "file_name": "seated_cable_row.glb",
        "blend_name": "back_seated_cable_row.blend",
        "builder": build_seated_cable_row,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "BARBELL_DEADLIFT": {
        "file_name": "barbell_deadlift.glb",
        "blend_name": "back_barbell_deadlift.blend",
        "builder": build_barbell_deadlift,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "DUMBBELL_SHOULDER_PRESS": {
        "file_name": "dumbbell_shoulder_press.glb",
        "blend_name": "shoulders_dumbbell_shoulder_press.blend",
        "builder": build_dumbbell_shoulder_press,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "DUMBBELL_LATERAL_RAISE": {
        "file_name": "dumbbell_lateral_raise.glb",
        "blend_name": "shoulders_dumbbell_lateral_raise.blend",
        "builder": build_dumbbell_lateral_raise,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "CABLE_FACE_PULL": {
        "file_name": "cable_face_pull.glb",
        "blend_name": "shoulders_cable_face_pull.blend",
        "builder": build_cable_face_pull,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "BARBELL_BICEP_CURL": {
        "file_name": "barbell_bicep_curl.glb",
        "blend_name": "biceps_barbell_bicep_curl.blend",
        "builder": build_barbell_bicep_curl,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "DUMBBELL_HAMMER_CURL": {
        "file_name": "dumbbell_hammer_curl.glb",
        "blend_name": "biceps_dumbbell_hammer_curl.blend",
        "builder": build_dumbbell_hammer_curl,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "INCLINE_DUMBBELL_CURL": {
        "file_name": "incline_dumbbell_curl.glb",
        "blend_name": "biceps_incline_dumbbell_curl.blend",
        "builder": build_incline_dumbbell_curl,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "CABLE_TRICEP_PUSHDOWN": {
        "file_name": "cable_tricep_pushdown.glb",
        "blend_name": "triceps_cable_tricep_pushdown.blend",
        "builder": build_cable_tricep_pushdown,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "SKULL_CRUSHER": {
        "file_name": "skull_crusher.glb",
        "blend_name": "triceps_skull_crusher.blend",
        "builder": build_skull_crusher,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "OVERHEAD_DUMBBELL_TRICEP_EXT": {
        "file_name": "overhead_dumbbell_tricep_ext.glb",
        "blend_name": "triceps_overhead_dumbbell_tricep_ext.blend",
        "builder": build_overhead_dumbbell_tricep_ext,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "BARBELL_SQUAT": {
        "file_name": "barbell_squat.glb",
        "blend_name": "quads_barbell_squat.blend",
        "builder": build_barbell_squat,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "LEG_PRESS": {
        "file_name": "leg_press.glb",
        "blend_name": "quads_leg_press.blend",
        "builder": build_leg_press,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "LEG_EXTENSION": {
        "file_name": "leg_extension.glb",
        "blend_name": "quads_leg_extension.blend",
        "builder": build_leg_extension,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "ROMANIAN_DEADLIFT": {
        "file_name": "romanian_deadlift.glb",
        "blend_name": "hamstrings_romanian_deadlift.blend",
        "builder": build_romanian_deadlift,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "LEG_CURL_MACHINE": {
        "file_name": "leg_curl_machine.glb",
        "blend_name": "hamstrings_leg_curl_machine.blend",
        "builder": build_leg_curl_machine,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "SEATED_LEG_CURL": {
        "file_name": "seated_leg_curl.glb",
        "blend_name": "hamstrings_seated_leg_curl.blend",
        "builder": build_seated_leg_curl,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "BARBELL_HIP_THRUST": {
        "file_name": "barbell_hip_thrust.glb",
        "blend_name": "glutes_barbell_hip_thrust.blend",
        "builder": build_barbell_hip_thrust,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "WALKING_LUNGE": {
        "file_name": "walking_lunge.glb",
        "blend_name": "glutes_walking_lunge.blend",
        "builder": build_walking_lunge,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "CABLE_GLUTE_KICKBACK": {
        "file_name": "cable_glute_kickback.glb",
        "blend_name": "glutes_cable_glute_kickback.blend",
        "builder": build_cable_glute_kickback,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "HANGING_LEG_RAISE": {
        "file_name": "hanging_leg_raise.glb",
        "blend_name": "abs_hanging_leg_raise.blend",
        "builder": build_hanging_leg_raise,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "CABLE_CRUNCH": {
        "file_name": "cable_crunch.glb",
        "blend_name": "abs_cable_crunch.blend",
        "builder": build_cable_crunch,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
    "PLANK": {
        "file_name": "plank.glb",
        "blend_name": "abs_plank.blend",
        "builder": build_plank,
        "bundled": True,
        "phase_keyframes": {
            "eccentric": [0, 45],
            "isometric": [45, 55],
            "concentric": [55, 100],
        },
    },
}


def inspect_glb_file(glb_path: Path) -> dict:
    raw = glb_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    chunk_len, _ = struct.unpack("<2I", raw[12:20])
    gltf = json.loads(raw[20 : 20 + chunk_len].decode("utf-8"))
    mats = {m.get("name") for m in gltf.get("materials", [])}
    anims = [a.get("name") for a in gltf.get("animations", [])]

    required_mats = {m for _, m in base_mod.MUSCLE_MESH_MATERIAL_PAIRS}
    missing = sorted(required_mats - mats)
    if missing:
        raise AssertionError(f"{glb_path.name} thieu Material chuan: {missing}")

    return {
        "size_bytes": len(raw),
        "sha256": sha,
        "extensions_used": gltf.get("extensionsUsed", []),
        "materials": sorted(required_mats),
        "clips": anims,
    }


def sync_manifest_and_mock_json(repo_root: Path) -> dict:
    """Cap nhat assets_manifest.json va mock_m2_exercises.json voi SHA-256 that cua tat ca .glb."""
    exported_dir = repo_root / "assets_3d" / "exported_glb"
    bundled_dir = repo_root / "mobile" / "assets" / "3d_bundled"

    ordered_specs: list[tuple[str, str, bool, dict | None]] = [
        ("BASE_MANNEQUIN", "base_mannequin.glb", True, None),
        ("BASE_MANNEQUIN_FEMALE", "base_mannequin_female.glb", True, None),
        (
            "BARBELL_SQUAT",
            "barbell_squat.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "PUSH_UP",
            "push_up.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_BENCH_PRESS",
            "barbell_bench_press.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "INCLINE_DUMBBELL_PRESS",
            "incline_dumbbell_press.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "CABLE_CHEST_FLY",
            "cable_chest_fly.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "WIDE_GRIP_PULLUP",
            "wide_grip_pullup.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "LAT_PULLDOWN",
            "lat_pulldown.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "STRAIGHT_ARM_CABLE_PULLDOWN",
            "straight_arm_cable_pulldown.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_BENT_OVER_ROW",
            "barbell_bent_over_row.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "SEATED_CABLE_ROW",
            "seated_cable_row.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_DEADLIFT",
            "barbell_deadlift.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "DUMBBELL_SHOULDER_PRESS",
            "dumbbell_shoulder_press.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "DUMBBELL_LATERAL_RAISE",
            "dumbbell_lateral_raise.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "CABLE_FACE_PULL",
            "cable_face_pull.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_BICEP_CURL",
            "barbell_bicep_curl.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "DUMBBELL_HAMMER_CURL",
            "dumbbell_hammer_curl.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "INCLINE_DUMBBELL_CURL",
            "incline_dumbbell_curl.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "CABLE_TRICEP_PUSHDOWN",
            "cable_tricep_pushdown.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "SKULL_CRUSHER",
            "skull_crusher.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "OVERHEAD_DUMBBELL_TRICEP_EXT",
            "overhead_dumbbell_tricep_ext.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "LEG_PRESS",
            "leg_press.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "LEG_EXTENSION",
            "leg_extension.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "ROMANIAN_DEADLIFT",
            "romanian_deadlift.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "LEG_CURL_MACHINE",
            "leg_curl_machine.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "SEATED_LEG_CURL",
            "seated_leg_curl.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_HIP_THRUST",
            "barbell_hip_thrust.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "WALKING_LUNGE",
            "walking_lunge.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "CABLE_GLUTE_KICKBACK",
            "cable_glute_kickback.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "HANGING_LEG_RAISE",
            "hanging_leg_raise.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "CABLE_CRUNCH",
            "cable_crunch.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "PLANK",
            "plank.glb",
            True,
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
    ]

    assets_entries = []
    total_bundled_bytes = 0
    bundled_info_by_code: dict[str, dict] = {}

    for code, fname, bundled, phases in ordered_specs:
        target = (bundled_dir / fname) if (bundled and (bundled_dir / fname).exists()) else (exported_dir / fname)
        if not target.exists():
            continue
        meta = inspect_glb_file(target)
        if bundled:
            total_bundled_bytes += meta["size_bytes"]
        if phases is not None:
            for req in ("Anim_GoodForm", "Anim_BadForm"):
                if req not in meta["clips"]:
                    raise AssertionError(f"{fname} thieu clip {req}: {meta['clips']}")
        entry = {
            "code": code,
            "file_name": fname,
            "bundled": bundled,
            "size_bytes": meta["size_bytes"],
            "sha256": meta["sha256"],
            "extensions_used": meta["extensions_used"],
            "materials": meta["materials"],
        }
        if phases is not None:
            entry["clips"] = meta["clips"]
            entry["phase_keyframes"] = phases
        assets_entries.append(entry)
        bundled_info_by_code[code] = {**entry, "file_name": fname}
        print(f"[VERIFIED] {fname:28s} size={meta['size_bytes']:7d}B sha256={meta['sha256'][:12]}... anims={meta['clips']}")

    manifest = {
        "schema_version": "1.1.0",
        "owner": "M2",
        "compression": "Binary_glTF_FastLoad",
        "max_triangles_budget": 25000,
        "total_bundled_bytes": total_bundled_bytes,
        "assets": assets_entries,
    }
    manifest_path = exported_dir / "assets_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[VigorAI] Updated {manifest_path} (total bundled: {total_bundled_bytes / 1024:.1f} KB)")

    # Sync bundled Chest & MVP exercises in mobile/assets/mock_json/mock_m2_exercises.json
    mock_path = repo_root / "mobile" / "assets" / "mock_json" / "mock_m2_exercises.json"
    if mock_path.exists():
        mock_data = json.loads(mock_path.read_text(encoding="utf-8"))
        for ex in mock_data.get("exercises", []):
            code = ex.get("code")
            info = bundled_info_by_code.get(code)
            if info and info["bundled"]:
                ex["model_3d_glb_url"] = f"assets/3d_bundled/{info['file_name']}"
                ex["asset_checksum"] = info["sha256"]
                ex["bundled"] = True
                ex["clips"] = info.get("clips", ["Anim_GoodForm", "Anim_BadForm"])
        mock_path.write_text(json.dumps(mock_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[VigorAI] Synced SHA-256 & bundled flags into {mock_path}")

    return manifest


def build_exercises(
    repo_root: Path,
    only_codes: list[str] | None = None,
    heatmap_preview: bool = False,
) -> None:
    exported_dir = repo_root / "assets_3d" / "exported_glb"
    bundled_dir = repo_root / "mobile" / "assets" / "3d_bundled"
    blend_dir = repo_root / "assets_3d" / "source_blend"

    targets = [c.upper() for c in only_codes] if only_codes else list(EXERCISE_SPECS.keys())
    for code in targets:
        spec = EXERCISE_SPECS.get(code)
        if spec is None:
            raise ValueError(f"Chua ho tro ma bai tap: {code}")
        out_paths = [exported_dir / spec["file_name"]]
        if spec["bundled"]:
            out_paths.append(bundled_dir / spec["file_name"])
        spec["builder"](
            export_paths=out_paths,
            blend_path=blend_dir / spec["blend_name"],
            heatmap_preview=heatmap_preview,
        )

    sync_manifest_and_mock_json(repo_root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Sprint 2 3D Exercises via Blender")
    parser.add_argument("--only", nargs="*", help="Only build specific exercise codes")
    parser.add_argument("--preview", action="store_true", help="Keep muscle heatmap preview colors in scene/.blend")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    build_exercises(root, only_codes=args.only, heatmap_preview=args.preview)
