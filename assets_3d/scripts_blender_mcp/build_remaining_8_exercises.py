# [OWNER: M2] Script Blender 5.3 dung 8 bai tap 3D con thieu de dat 39/39 bai co chuyen dong that
"""
8 bai tap duoc bo sung trong dot nay (phoi hop cung build_sprint2_exercises.py):
  1. BARBELL_OVERHEAD_PRESS  -> barbell_overhead_press.glb
  2. ONE_ARM_DUMBBELL_ROW    -> one_arm_dumbbell_row.glb
  3. GOBLET_SQUAT            -> goblet_squat.glb
  4. KETTLEBELL_SWING        -> kettlebell_swing.glb
  5. MACHINE_CHEST_PRESS     -> machine_chest_press.glb
  6. CABLE_BICEP_CURL        -> cable_bicep_curl.glb
  7. CLOSE_GRIP_BENCH_PRESS  -> close_grip_bench_press.glb
  8. STANDING_CALF_RAISE     -> standing_calf_raise.glb
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from mathutils import Matrix, Vector  # type: ignore

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import build_base_mannequin as base_mod


def _s2():
    import build_sprint2_exercises as s2

    return s2


# ---------------------------------------------------------------------------
# Bo sung Modular Equipment Builders cho Kettlebell, Machine Chest Press, Calf Raise
# ---------------------------------------------------------------------------
def _build_kettlebell_object(collection, name: str = "Equip_Kettlebell"):
    """Ta am Kettlebell Low-Poly (~320 tris, tam tay nam ngang doc truc X tai (0,0,0), qua ta o -Z)."""
    import bmesh  # type: ignore

    s2 = _s2()
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", s2.STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_iron = base_mod._create_pbr_material("Mat_Equip_Iron", s2.PLATE_IRON_COLOR, roughness=0.45, metallic=0.80)
    mat_collar = base_mod._create_pbr_material("Mat_Equip_Collar", s2.PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    # Tay cam ngang doc X (-0.088 .. +0.088) tai Z=0
    grip_faces = s2._create_equip_cylinder(
        bm, Vector((-0.082, 0.0, 0.0)), Vector((0.082, 0.0, 0.0)), 0.017, 10
    )
    horn_faces = set()
    for sx in (1.0, -1.0):
        # Bo cong quai ta am noi xuong co ta
        horn_faces |= s2._create_equip_cylinder(
            bm, Vector((sx * 0.082, 0.0, 0.0)), Vector((sx * 0.095, 0.0, -0.055)), 0.016, 8
        )
        horn_faces |= s2._create_equip_cylinder(
            bm, Vector((sx * 0.095, 0.0, -0.055)), Vector((sx * 0.055, 0.0, -0.105)), 0.017, 8
        )
    # Vong co nhan do va bau ta gang tron day phang (center tai Z = -0.175)
    collar_faces = s2._create_equip_cylinder(
        bm, Vector((0.0, 0.0, -0.102)), Vector((0.0, 0.0, -0.116)), 0.048, 12
    )
    bell_faces = set()
    bell_faces |= s2._create_equip_cylinder(
        bm, Vector((0.0, 0.0, -0.115)), Vector((0.0, 0.0, -0.145)), 0.084, 14
    )
    bell_faces |= s2._create_equip_cylinder(
        bm, Vector((0.0, 0.0, -0.145)), Vector((0.0, 0.0, -0.215)), 0.105, 16
    )
    bell_faces |= s2._create_equip_cylinder(
        bm, Vector((0.0, 0.0, -0.215)), Vector((0.0, 0.0, -0.245)), 0.072, 14
    )

    s2._assign_bmesh_materials(bm, [(grip_faces, 0), (horn_faces | bell_faces, 1), (collar_faces, 2)])
    return s2._bmesh_to_object(bm, collection, name, [mat_steel, mat_iron, mat_collar])


def _build_chest_press_machine(
    collection,
    pivot_pos: Vector = Vector((0.0, 0.08, 1.54)),
):
    """May day nguc ngoi (Equip_ChestPressMachine + cum can day doi Equip_ChestPressArms xoay quanh pivot)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    s2 = _s2()
    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", s2.BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", s2.STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", s2.PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", s2.PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # Khung de san & tru do ghe (thap ta dat phia sau Y=+0.56 de thoang goc nhin truoc & ngang)
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.18, 0.025), (0.64, 1.18, 0.05))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.58, 0.025), (0.72, 0.44, 0.05))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.06, 0.24), (0.08, 0.44, 0.06))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.04, 0.24), (0.07, 0.07, 0.40))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.24, 0.24), (0.07, 0.07, 0.40))

    # Dem ngoi (top Z=0.48, Y=-0.10..+0.24) + tua lung 80 deg
    pad_faces |= s2._create_equip_box(bm, (0.0, 0.06, 0.445), (0.33, 0.34, 0.07))
    back_rad = math.radians(80.0)
    back_up = Vector((0.0, math.cos(back_rad), math.sin(back_rad)))
    back_n = Vector((0.0, -math.sin(back_rad), math.cos(back_rad)))
    back_hinge = Vector((0.0, 0.21, 0.49))
    back_center = back_hinge + back_up * 0.38 - back_n * 0.032
    pad_faces |= s2._create_equip_box(
        bm, tuple(back_center), (0.30, 0.72, 0.065), Matrix.Rotation(back_rad, 4, "X")
    )
    frame_faces |= s2._create_equip_cylinder(
        bm, Vector((0.0, 0.34, 0.40)), back_hinge + back_up * 0.48 - back_n * 0.065, 0.026, 8
    )

    # Thap ta phia sau (Y=+0.58) & thanh vuon tren cao toi cum truc xoay pivot_pos (0, 0.08, 1.54)
    for sx in (1.0, -1.0):
        frame_faces |= s2._create_equip_box(bm, (sx * 0.20, 0.58, 0.84), (0.065, 0.065, 1.66))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.58, 1.64), (0.48, 0.24, 0.06))
    steel_faces |= s2._create_equip_box(bm, (0.0, 0.58, 0.58), (0.24, 0.18, 0.78))
    frame_faces |= s2._create_equip_box(bm, (0.0, 0.33, pivot_pos.z + 0.04), (0.12, 0.58, 0.07))
    accent_faces |= s2._create_equip_cylinder(
        bm,
        Vector((-0.38, pivot_pos.y, pivot_pos.z)),
        Vector((0.38, pivot_pos.y, pivot_pos.z)),
        0.034,
        12,
    )

    s2._assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = s2._bmesh_to_object(bm, collection, "Equip_ChestPressMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Can day doi (origin tai pivot_pos; local +Y doc xuong toi muc nguc; local -Z huong ra phia truoc tay cam)
    bm_a = bmesh.new()
    a_frame = set()
    a_steel = set()
    a_pad = set()
    a_accent = set()
    for sx in (1.0, -1.0):
        arm_x = sx * 0.35
        grip_x = sx * 0.27
        a_accent |= s2._create_equip_cylinder(
            bm_a, Vector((arm_x - sx * 0.025, 0.0, 0.0)), Vector((arm_x + sx * 0.025, 0.0, 0.0)), 0.042, 12
        )
        # Can doc xuong ben ngoai vai (khong cham vai/tay)
        a_frame |= s2._create_equip_cylinder(
            bm_a, Vector((arm_x, 0.0, 0.0)), Vector((arm_x, 0.54, 0.0)), 0.022, 10
        )
        # Thanh vuon ra phia truoc (-Z) toi tay cam ngang nguc (grip tai (±0.27, 0.54, -0.28))
        a_frame |= s2._create_equip_cylinder(
            bm_a, Vector((arm_x, 0.54, 0.0)), Vector((arm_x, 0.54, -0.28)), 0.020, 10
        )
        a_steel |= s2._create_equip_cylinder(
            bm_a, Vector((arm_x, 0.54, -0.28)), Vector((grip_x - sx * 0.055, 0.54, -0.28)), 0.015, 10
        )
        a_pad |= s2._create_equip_cylinder(
            bm_a, Vector((grip_x + sx * 0.050, 0.54, -0.28)), Vector((grip_x - sx * 0.050, 0.54, -0.28)), 0.019, 10
        )

    s2._assign_bmesh_materials(bm_a, [(a_frame, 0), (a_steel, 1), (a_pad, 2), (a_accent, 3)])
    press_arms = s2._bmesh_to_object(bm_a, collection, "Equip_ChestPressArms", [mat_frame, mat_steel, mat_pad, mat_accent])
    return machine, press_arms


def _build_standing_calf_machine(collection):
    """May nhon bap chan dung (Equip_CalfMachine + khung vai nang Equip_CalfYoke) thoang mat sau."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    s2 = _s2()
    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", s2.BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", s2.STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", s2.PAD_COLOR, roughness=0.72, metallic=0.05)
    mat_accent = base_mod._create_pbr_material("Mat_Equip_Collar", s2.PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    frame_faces = set()
    steel_faces = set()
    pad_faces = set()
    accent_faces = set()

    # De san + buc ke mui chan (step block Z=0..0.16 tai Y=-0.26..-0.04 de got chan treo thoang va nhon sau)
    frame_faces |= s2._create_equip_box(bm, (0.0, -0.32, 0.025), (0.84, 1.02, 0.05))
    frame_faces |= s2._create_equip_box(bm, (0.0, -0.15, 0.080), (0.58, 0.22, 0.16))
    steel_faces |= s2._create_equip_box(bm, (0.0, -0.15, 0.162), (0.56, 0.20, 0.012))

    # Hai tru dan huong thanh manh phia truoc (X=+-0.38, Y=-0.58) -> thong thoang moi goc nhin 3D
    for sx in (1.0, -1.0):
        px = sx * 0.38
        frame_faces |= s2._create_equip_box(bm, (px, -0.58, 0.98), (0.05, 0.05, 1.96))
        steel_faces |= s2._create_equip_cylinder(
            bm, Vector((sx * 0.16, -0.60, 0.05)), Vector((sx * 0.16, -0.60, 1.94)), 0.012, 8
        )
    frame_faces |= s2._create_equip_box(bm, (0.0, -0.58, 1.94), (0.82, 0.10, 0.055))
    steel_faces |= s2._create_equip_box(bm, (0.0, -0.60, 0.56), (0.34, 0.18, 0.72))

    s2._assign_bmesh_materials(bm, [(frame_faces, 0), (steel_faces, 1), (pad_faces, 2), (accent_faces, 3)])
    machine = s2._bmesh_to_object(bm, collection, "Equip_CalfMachine", [mat_frame, mat_steel, mat_pad, mat_accent])
    machine.parent = bpy.data.objects.get("Floor_Origin")

    # Khung dem vai + tay nam truoc (origin tai diem dat tren vai/traps giua, Z=0 tiep xuc vai)
    bm_y = bmesh.new()
    y_frame = set()
    y_steel = set()
    y_pad = set()
    y_accent = set()

    # Thanh ngang phia truoc noi ra hai tru truot (Y=-0.58 relative to traps at Y~0)
    y_frame |= s2._create_equip_box(bm_y, (0.0, -0.54, 0.06), (0.76, 0.055, 0.055))
    for sx in (1.0, -1.0):
        # Can vuon tu khung truoc ve hai vai (X=+-0.165)
        y_frame |= s2._create_equip_box(bm_y, (sx * 0.165, -0.26, 0.065), (0.048, 0.56, 0.048))
        # Dem vai em (Z=0.005..0.055) om tren cau vai/vai
        y_pad |= s2._create_equip_box(bm_y, (sx * 0.165, 0.01, 0.025), (0.11, 0.22, 0.055))
        # Tay nam phia truoc ngang tam tay (X=+-0.21, Y=-0.30, Z=-0.03)
        y_frame |= s2._create_equip_cylinder(
            bm_y, Vector((sx * 0.165, -0.30, 0.04)), Vector((sx * 0.22, -0.30, -0.02)), 0.014, 8
        )
        y_pad |= s2._create_equip_cylinder(
            bm_y, Vector((sx * 0.15, -0.30, -0.02)), Vector((sx * 0.27, -0.30, -0.02)), 0.019, 10
        )
        y_accent |= s2._create_equip_cylinder(
            bm_y, Vector((sx * 0.38, -0.56, 0.06)), Vector((sx * 0.38, -0.52, 0.06)), 0.032, 10
        )

    s2._assign_bmesh_materials(bm_y, [(y_frame, 0), (y_steel, 1), (y_pad, 2), (y_accent, 3)])
    yoke = s2._bmesh_to_object(bm_y, collection, "Equip_CalfYoke", [mat_frame, mat_steel, mat_pad, mat_accent])
    return machine, yoke


# ---------------------------------------------------------------------------
# 1. BARBELL OVERHEAD PRESS (Dung day vai don ta)
# ---------------------------------------------------------------------------
def _pose_barbell_overhead_press(arm_obj, depth: float, bad_form: bool) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: day hong ve truoc (-Y) va ngua vong that lung qua muc (+26 deg) de bu luc vai
        pelvis_y = -0.09 - 0.04 * (1.0 - depth)
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.90)))
        lean_deg = 25.0 - 11.0 * depth
        a_pel = math.radians(lean_deg * 0.6)
        a_sp = math.radians(lean_deg)
        s2._aim_bone_world(arm_obj, "Pelvis", Vector((0.0, math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, Vector((0.0, math.sin(a_sp), math.cos(a_sp))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.05, 0.998)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.10, 0.995)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: dung thang cung loi, hoi nga nhe khi don qua cam (d=1) roi khoa thang qua dinh dau (d=0)
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.02, 0.92)))
        back_deg = 2.0 + 5.0 * depth
        torso_dir = Vector((0.0, math.sin(math.radians(back_deg)), math.cos(math.radians(back_deg)))).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.06 * depth, 0.998)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, 0.04 * depth - 0.03, 0.999)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.17, 0.02, 0.092))
        knee_pole = Vector((sx * 0.18, -0.86, 0.45))
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # d=0 -> khoa tren dau (0, 0.00, 1.94); d=1 -> ha truoc nguc tren (0, -0.145, 1.44)
    if bad_form:
        bar_pos = Vector((0.0, -0.18 - 0.06 * depth, 1.90 - 0.44 * depth))
    else:
        bar_pos = Vector((0.0, -0.02 - 0.125 * depth, 1.93 - 0.49 * depth))
    s2._set_bone_world_head(arm_obj, "Bone_Barbell", bar_pos)

    fists: list[Vector] = []
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.275, 0.0, 0.0))
        finger_dir = Vector((0.0, -0.16, 0.987)).normalized()
        elbow_pole = (
            Vector((sx * 0.94, 0.10, -0.32)).normalized()
            if bad_form
            else Vector((sx * 0.48, -0.82, -0.30)).normalized()
        )
        roll_arm = Vector((-sx * 1.0, 0.0, 0.0))
        fist_pos = s2._solve_arm_grip_ik(
            arm_obj,
            side,
            palm_pos,
            finger_dir,
            roll_arm,
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        fists.append(fist_pos)
    s2._set_bone_world_head(
        arm_obj,
        "Bone_Barbell",
        Vector((0.0, 0.5 * (fists[0].y + fists[1].y), 0.5 * (fists[0].z + fists[1].z))),
    )


def build_barbell_overhead_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_Barbell")
    barbell = s2._build_barbell_object(col, "Equip_Barbell")
    s2._parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_barbell_overhead_press(arm_obj, d, bad_form=is_bad)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Shoulders"],
        secondary=["Mat_Muscle_Triceps", "Mat_Muscle_Traps"],
        stabilizer=["Mat_Muscle_Abs_Core", "Mat_Muscle_Glutes"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 2. ONE-ARM DUMBBELL ROW (Keo lung mot tay ta don chong ghe phang)
# ---------------------------------------------------------------------------
def _pose_one_arm_dumbbell_row(arm_obj, depth: float, bad_form: bool) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    # Ghe phang dat lech sang ben Trai (X=+0.18), mat dem Z=0.43; nguoi tap chong goi L & tay L len ghe
    # Chan Phai R tru san (-0.28, 0.24, 0.092), tay Phai R keo ta don doc sườn
    pull = 1.0 - depth  # pull=1 o dinh keo (d=0), pull=0 o day duoi xo (d=1)

    if bad_form:
        # Loi: giat vai & xoay van cot song manh len phia Phai (-X) o dinh keo (pull=1)
        twist_rad = math.radians(34.0 * pull)
        pitch_deg = 16.0 + 18.0 * pull
        pelvis_pos = Vector((-0.04, 0.28, 0.85 + 0.03 * pull))
        roll_thorax = Vector((math.cos(twist_rad), 0.0, -math.sin(twist_rad))).normalized()
    else:
        twist_rad = 0.0
        pitch_deg = 16.0
        pelvis_pos = Vector((-0.03, 0.28, 0.85))
        roll_thorax = Vector((1.0, 0.0, 0.0))

    s2._set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
    torso_dir = Vector((0.0, -math.cos(math.radians(pitch_deg)), math.sin(math.radians(pitch_deg)))).normalized()
    s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Spine_01", torso_dir, Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Spine_02", torso_dir, (Vector((1.0, 0.0, 0.0)).lerp(roll_thorax, 0.55)).normalized())
    s2._aim_bone_world(arm_obj, "Spine_03", torso_dir, roll_thorax)
    s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.84, 0.54)).normalized(), Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.68, 0.73)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan Trai L: chong goi len mat ghe (Z=0.43, X=+0.18), cang chan duoi ve sau tren dem (Y=+0.56, Z=0.51)
    s2._solve_two_bone_ik_world(
        arm_obj,
        "Thigh_L",
        "Calf_L",
        Vector((0.18, 0.56, 0.51)),
        Vector((0.18, 0.05, -0.99)).normalized(),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    s2._aim_bone_world(arm_obj, "Foot_L", Vector((0.0, -0.18, -0.98)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Chan Phai R: dung vung tren san ben ngoai ghe (-0.28, 0.24, 0.092)
    s2._solve_two_bone_ik_world(
        arm_obj,
        "Thigh_R",
        "Calf_R",
        Vector((-0.28, 0.24, 0.092)),
        Vector((-0.30, -0.88, 0.45)).normalized(),
        Vector((1.0, 0.0, 0.0)),
        Vector((1.0, 0.0, 0.0)),
    )
    s2._aim_bone_world(arm_obj, "Foot_R", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Tay Trai L: chong thang chac chan xuong mep truoc ghe phang (0.17, -0.26, 0.46)
    s2._solve_arm_grip_ik(
        arm_obj,
        "L",
        Vector((0.17, -0.26, 0.465)),
        Vector((0.0, -0.98, -0.18)).normalized(),
        Vector((-1.0, 0.0, 0.0)),
        Vector((0.20, 0.85, 0.48)).normalized(),
        Vector((0.0, -1.0, 0.0)),
        Vector((0.0, -1.0, 0.0)),
    )

    # Tay Phai R: keo ta don theo quy dao cung ve hong ("ve tui quan") -> d=0 o dinh keo, d=1 duoi sau
    if bad_form:
        db_pos = Vector((-0.30 + 0.04 * depth, -0.02 - 0.14 * depth, 0.84 - 0.44 * depth))
        elbow_pole = Vector((-0.88, 0.35, 0.32)).normalized()
    else:
        db_pos = Vector((-0.25, 0.05 - 0.19 * depth, 0.78 - 0.40 * depth))
        elbow_pole = Vector((-0.24, 0.72, 0.65)).normalized()

    fist_pos = s2._solve_arm_grip_ik(
        arm_obj,
        "R",
        db_pos,
        Vector((0.35, 0.0, -0.93)).normalized(),
        Vector((0.0, -1.0, 0.0)),
        elbow_pole,
        Vector((0.0, -1.0, 0.0)),
        Vector((0.0, -1.0, 0.0)),
    )
    # Thanh ta don huong truoc-sau (-Y -> +Y) trong long ban tay trung tinh
    s2._set_bone_world_axes(
        arm_obj,
        "Bone_Dumbbell_R",
        fist_pos,
        Vector((0.0, -1.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
        Vector((-1.0, 0.0, 0.0)),
    )


def build_one_arm_dumbbell_row(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_Dumbbell_R")
    bench = s2._build_flat_bench_object(col, "Equip_Bench")
    bench.location = Vector((0.18, 0.0, 0.0))
    db = s2._build_dumbbell_object(col, "Equip_Dumbbell")
    s2._parent_equip_to_bone(db, arm_obj, "Bone_Dumbbell_R")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_one_arm_dumbbell_row(arm_obj, d, bad_form=is_bad)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Back_Lats"],
        secondary=["Mat_Muscle_Traps", "Mat_Muscle_Biceps"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 3. GOBLET SQUAT (Squat om ta don truoc nguc)
# ---------------------------------------------------------------------------
def _pose_goblet_squat(arm_obj, depth: float, bad_form: bool) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: gu lung tren chu C khi giu ta truoc nguc + chum goi vao trong (Knee Valgus)
        pelvis_pos = Vector((0.0, 0.02 + 0.16 * depth, 0.90 - 0.32 * depth))
        s2._set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        a_pel = math.radians(6.0 + 18.0 * depth)
        a_sp1 = math.radians(6.0 + 26.0 * depth)
        a_sp2 = math.radians(8.0 + 38.0 * depth)
        a_sp3 = math.radians(10.0 + 48.0 * depth)
        s2._aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a_pel), math.cos(a_pel))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a_sp1), math.cos(a_sp1))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a_sp2), math.cos(a_sp2))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a_sp3), math.cos(a_sp3))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.52, 0.85)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.32, 0.95)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu nguc mo cao (~18 deg khi xuong sau), ha hong sau duoi song song
        pelvis_pos = Vector((0.0, 0.02 + 0.14 * depth, 0.90 - 0.40 * depth))
        s2._set_bone_world_head(arm_obj, "Pelvis", pelvis_pos)
        torso_rad = math.radians(4.0 + 15.0 * depth)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.14 * depth, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.08 * depth, 0.996)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.21, 0.02, 0.092))
        if bad_form:
            knee_pole = Vector((-sx * 0.58 * depth, -0.78, 0.18)).normalized()
        else:
            knee_pole = Vector((sx * 0.38, -0.91, 0.18)).normalized()
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((sx * 0.18, -0.92, -0.34)).normalized(), Vector((1.0, 0.0, 0.0)))

    # Dat ta don dung thang (axis_x = +Z) ngay truoc xuong uc
    if bad_form:
        db_pos = Vector((0.0, -0.22 - 0.12 * depth, pelvis_pos.z + 0.31 - 0.06 * depth))
    else:
        db_pos = Vector((0.0, -0.21 - 0.03 * depth, pelvis_pos.z + 0.34))

    s2._set_bone_world_axes(
        arm_obj,
        "Bone_Dumbbell",
        db_pos,
        Vector((0.0, 0.0, 1.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((-1.0, 0.0, 0.0)),
    )

    fists: list[Vector] = []
    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Hai ban tay om hai ben duoi dia ta tren (Z + 0.058)
        palm_pos = db_pos + Vector((sx * 0.062, -0.015, 0.058))
        finger_dir = Vector((-sx * 0.40, 0.72, 0.56)).normalized()
        elbow_pole = (
            Vector((sx * 0.78, -0.20, -0.58)).normalized()
            if bad_form
            else Vector((sx * 0.18, -0.55, -0.81)).normalized()
        )
        roll_arm = Vector((0.0, -0.85, 0.52)).normalized()
        fist_pos = s2._solve_arm_grip_ik(
            arm_obj,
            side,
            palm_pos,
            finger_dir,
            Vector((0.0, 0.0, 1.0)),
            elbow_pole,
            roll_arm,
            roll_arm,
        )
        fists.append(fist_pos)
    s2._set_bone_world_head(
        arm_obj,
        "Bone_Dumbbell",
        Vector((0.0, 0.5 * (fists[0].y + fists[1].y) + 0.015, 0.5 * (fists[0].z + fists[1].z) - 0.058)),
    )


def build_goblet_squat(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_Dumbbell")
    db = s2._build_dumbbell_object(col, "Equip_Dumbbell")
    s2._parent_equip_to_bone(db, arm_obj, "Bone_Dumbbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_goblet_squat(arm_obj, d, bad_form=is_bad)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Quads", "Mat_Muscle_Glutes"],
        secondary=["Mat_Muscle_Abs_Core"],
        stabilizer=["Mat_Muscle_Back_Lats"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 4. KETTLEBELL SWING (Vung ta am Kettlebell bang ban le hong)
# ---------------------------------------------------------------------------
def _pose_kettlebell_swing(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: Squat ha thap goi & gap lưng thay vi Hip Hinge + dung hai tay keo/co khuyu nang ta len qua vai
        pelvis_y = -0.02 + 0.08 * depth
        pelvis_z = 0.90 - 0.30 * depth
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        lean_deg = -14.0 + 38.0 * depth
        a1 = math.radians(lean_deg)
        a2 = math.radians(lean_deg + 14.0 * depth)
        s2._aim_bone_world(arm_obj, "Pelvis", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -math.sin(a1), math.cos(a1))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -math.sin(a2), math.cos(a2))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -math.sin(a2), math.cos(a2))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.18 * depth, 0.98)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.08 * depth, 0.996)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: d=0 dung thang khoa hong & mong cung cap; d=1 Hip Hinge sau (lung phang ~58 deg)
        hinge = depth ** 0.85
        pelvis_y = 0.01 + 0.29 * hinge
        pelvis_z = 0.91 - 0.14 * hinge
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))
        torso_rad = math.radians(2.0 + 58.0 * hinge)
        torso_dir = Vector((0.0, -math.sin(torso_rad), math.cos(torso_rad))).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.38 * hinge, 0.92)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.24 * hinge, 0.97)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.26, 0.04, 0.092))
        knee_pole = Vector((sx * 0.34, -0.92, 0.22)).normalized()
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((sx * 0.15, -0.93, -0.34)).normalized(), Vector((1.0, 0.0, 0.0)))

    bpy.context.view_layer.update()
    sh_l = (arm_obj.matrix_world @ arm_obj.pose.bones["UpperArm_L"].matrix).translation
    sh_r = (arm_obj.matrix_world @ arm_obj.pose.bones["UpperArm_R"].matrix).translation
    sh_mid = 0.5 * (sh_l + sh_r)

    if bad_form:
        # Co khuyu nang ta len ngang cam (Z=1.50) o d=0, tha roi xuong giua hai goi (Y=-0.22, Z=0.48) o d=1
        swing_ang = math.radians(22.0 - 94.0 * depth)
        arm_len = 0.43 + 0.09 * depth
        kb_axis_z = Vector((0.0, math.sin(swing_ang) * 0.3, math.cos(swing_ang))).normalized()
    else:
        # Canh tay duoi thang nhu con lac tu vai -> d=0 ngang vai (-78 deg tu thang dung? -> ngang -Y ~ 82 deg), d=1 sau hang (+28 deg ve +Y)
        swing_deg = 82.0 - 110.0 * depth
        swing_rad = math.radians(swing_deg)
        arm_dir = Vector((0.0, -math.sin(swing_rad), -math.cos(swing_rad))).normalized()
        # Doi voi arm_dir: o d=0 (-0.99, 0.14) ta nam ngang nguc; o d=1 (+0.47, -0.88) luon sau giua 2 dui
        # Kettlebell qua nang bung ra ngoai theo phuong doc canh tay (-arm_dir la huong quai cam -> +arm_dir la qua ta)
        arm_len = 0.555
        grip_mid = sh_mid + arm_dir * arm_len
        elbow_pole_base = Vector((0.0, -arm_dir.z * 0.5, arm_dir.y * 0.5)).normalized()
        kb_z = (-arm_dir).normalized()  # quai (+Z_local) huong ve phia co tay/vai; qua ta (-Z_local) vang ly tam ra ngoai!

    if bad_form:
        # Direct grip_mid cho BadForm co gap khuyu
        grip_mid = Vector((0.0, -0.36 * (1.0 - depth) - 0.16 * depth, 1.50 - 1.02 * depth))
        elbow_pole_base = Vector((0.0, 0.72, -0.42))
        kb_z = (sh_mid - grip_mid).normalized()

    kb_x = Vector((1.0, 0.0, 0.0))
    kb_y = kb_z.cross(kb_x).normalized()
    kb_z = kb_x.cross(kb_y).normalized()
    s2._set_bone_world_axes(arm_obj, "Bone_Kettlebell", grip_mid, kb_x, kb_y, kb_z)

    fists: list[Vector] = []
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = grip_mid + Vector((sx * 0.048, 0.0, 0.0))
        finger_dir = (-kb_z).normalized()
        pole_v = Vector((sx * (0.72 if bad_form else 0.15), elbow_pole_base.y, elbow_pole_base.z)).normalized()
        roll_arm = Vector((-sx * 1.0, 0.0, 0.0))
        fist_pos = s2._solve_arm_grip_ik(
            arm_obj,
            side,
            palm_pos,
            finger_dir,
            roll_arm,
            pole_v,
            roll_arm,
            roll_arm,
        )
        fists.append(fist_pos)
    s2._set_bone_world_head(
        arm_obj,
        "Bone_Kettlebell",
        Vector((0.0, 0.5 * (fists[0].y + fists[1].y), 0.5 * (fists[0].z + fists[1].z))),
    )


def build_kettlebell_swing(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_Kettlebell")
    kb = _build_kettlebell_object(col, "Equip_Kettlebell")
    s2._parent_equip_to_bone(kb, arm_obj, "Bone_Kettlebell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_kettlebell_swing(arm_obj, d, bad_form=is_bad)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Glutes", "Mat_Muscle_Hamstrings"],
        secondary=["Mat_Muscle_Abs_Core", "Mat_Muscle_Shoulders"],
        stabilizer=["Mat_Muscle_Back_Lats"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 5. MACHINE CHEST PRESS (Day nguc may ngoi)
# ---------------------------------------------------------------------------
def _pose_machine_chest_press(
    arm_obj,
    depth: float,
    bad_form: bool,
    pivot_pos: Vector = Vector((0.0, 0.08, 1.54)),
) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: nho vai & gu lung tren roi khoi dem tua khi day (d=0), khuyu xoe 90 deg ngang vai
        protract = 1.0 - depth
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.05 - 0.04 * protract, 0.56)))
        s2._aim_bone_world(arm_obj, "Pelvis", Vector((0.0, math.cos(math.radians(80.0)), math.sin(math.radians(80.0)))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_01", Vector((0.0, math.cos(math.radians(80.0 + 10.0 * protract)), math.sin(math.radians(80.0 + 10.0 * protract)))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_02", Vector((0.0, math.cos(math.radians(80.0 + 22.0 * protract)), math.sin(math.radians(80.0 + 22.0 * protract)))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Spine_03", Vector((0.0, math.cos(math.radians(80.0 + 28.0 * protract)), math.sin(math.radians(80.0 + 28.0 * protract)))).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.22 * protract, 0.98)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.14 * protract, 0.99)).normalized(), Vector((1.0, 0.0, 0.0)))
    else:
        # Dung ky thuat: giu 2 xuong ba vai khoa chat vao dem tua 80 deg
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.05, 0.56)))
        torso_dir = Vector((0.0, math.cos(math.radians(80.0)), math.sin(math.radians(80.0)))).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.05, 0.998)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.04, 0.999)).normalized(), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.19, -0.44, 0.092))
        knee_pole = Vector((sx * 0.22, -0.78, 0.58))
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Goc xoay can may: d=0 day thang ra truoc (theta=32 deg); d=1 ha ve ngang nguc (theta=-2 deg)
    theta_rad = math.radians(32.0 * (1.0 - depth) - 2.0 * depth)
    axis_x = Vector((1.0, 0.0, 0.0))
    axis_y = Vector((0.0, -math.sin(theta_rad), -math.cos(theta_rad))).normalized()
    axis_z = axis_x.cross(axis_y).normalized()
    s2._set_bone_world_axes(arm_obj, "Bone_PressArms", pivot_pos, axis_x, axis_y, axis_z)

    for side, sx in (("L", 1.0), ("R", -1.0)):
        # Tay cam tai local (sx*0.27, 0.54, -0.28) quy doi chinh xac sang world
        grip_pos = pivot_pos + axis_x * (sx * 0.27) + axis_y * 0.54 + axis_z * (-0.28)
        finger_dir = Vector((0.0, -0.96, 0.28)).normalized()
        elbow_pole = (
            Vector((sx * 0.94, 0.28, 0.18)).normalized()
            if bad_form
            else Vector((sx * 0.68, 0.44, -0.58)).normalized()
        )
        roll_arm = Vector((0.0, 0.35, -0.94)).normalized()
        s2._solve_arm_grip_ik(
            arm_obj,
            side,
            grip_pos,
            finger_dir,
            Vector((-sx * 1.0, 0.0, 0.0)),
            elbow_pole,
            roll_arm,
            roll_arm,
        )


def build_machine_chest_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pivot_pos = Vector((0.0, 0.08, 1.54))
    s2._add_ctrl_bone(arm_obj, "Bone_PressArms")
    _, press_arms = _build_chest_press_machine(col, pivot_pos=pivot_pos)
    s2._parent_equip_to_bone(press_arms, arm_obj, "Bone_PressArms")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_machine_chest_press(arm_obj, d, bad_form=is_bad, pivot_pos=pivot_pos)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Chest"],
        secondary=["Mat_Muscle_Triceps", "Mat_Muscle_Shoulders"],
        stabilizer=[],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 6. CABLE BICEP CURL (Cuon tay truoc voi day cap thap)
# ---------------------------------------------------------------------------
def _pose_cable_bicep_curl(
    arm_obj,
    depth: float,
    bad_form: bool,
    pulley_pos: Vector = Vector((0.0, -0.88, 0.18)),
) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: nhac vai & lac lung ra sau (-20 deg o dinh) khi keo cap nang
        pelvis_y = -0.02 + 0.10 * depth
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, 0.92)))
        lean_deg = -20.0 + 30.0 * depth
        torso_dir = Vector((0.0, -math.sin(math.radians(lean_deg)), math.cos(math.radians(lean_deg)))).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.04, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        curl_deg = 138.0 - 110.0 * depth
        elbow_y = -0.14 + 0.10 * depth
        elbow_z = 1.25 - 0.10 * depth
        elbow_pole_base = Vector((0.0, 0.65, -0.75))
    else:
        # Dung ky thuat: khoa cung khuyu tay ben suon, than nguoi dung thang
        s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.04, 0.92)))
        torso_dir = Vector((0.0, -0.03, 1.0)).normalized()
        s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.03, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
        curl_deg = 128.0 - 102.0 * depth
        elbow_y, elbow_z = -0.01, 1.145
        elbow_pole_base = Vector((0.0, 0.85, -0.50))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.16, 0.04, 0.092))
        knee_pole = Vector((sx * 0.17, -0.85, 0.45))
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    curl_rad = math.radians(curl_deg)
    forearm_dir = Vector((0.0, -math.sin(curl_rad), -math.cos(curl_rad))).normalized()
    bar_pos = Vector((0.0, elbow_y, elbow_z)) + forearm_dir * 0.295

    roll_upper = Vector((0.0, -1.0, 0.15)).normalized()
    roll_lower = forearm_dir.cross(Vector((1.0, 0.0, 0.0))).normalized()
    fists: list[Vector] = []
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = bar_pos + Vector((sx * 0.19, 0.0, 0.0))
        side_pole = Vector((sx * 0.18, elbow_pole_base.y, elbow_pole_base.z)).normalized()
        fist_pos = s2._solve_arm_grip_ik(
            arm_obj,
            side,
            palm_pos,
            forearm_dir,
            Vector((sx * 1.0, 0.0, 0.0)),
            side_pole,
            roll_upper,
            roll_lower,
        )
        fists.append(fist_pos)

    bar_mid = Vector((0.0, 0.5 * (fists[0].y + fists[1].y), 0.5 * (fists[0].z + fists[1].z)))
    cable_vec_bar = pulley_pos - bar_mid
    cable_dir = cable_vec_bar.normalized()
    bar_x = Vector((1.0, 0.0, 0.0))
    bar_y_ax = cable_dir.cross(bar_x).normalized()
    s2._set_bone_world_axes(arm_obj, "Bone_StraightBar", bar_mid, bar_x, bar_y_ax, cable_dir)

    bar_anchor = bar_mid + cable_dir * 0.036
    c_vec = bar_anchor - pulley_pos
    c_len = max(0.05, c_vec.length)
    s2._set_bone_world_head(arm_obj, "Bone_Cable_Center", pulley_pos)
    s2._aim_bone_world(arm_obj, "Bone_Cable_Center", c_vec.normalized(), Vector((1.0, 0.0, 0.0)))
    arm_obj.pose.bones["Bone_Cable_Center"].scale = Vector((1.0, c_len, 1.0))


def build_cable_bicep_curl(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    pulley_pos = Vector((0.0, -0.88, 0.18))
    for bname in ("Bone_StraightBar", "Bone_Cable_Center"):
        s2._add_ctrl_bone(arm_obj, bname)

    _, straight_bar, cable = s2._build_single_cable_tower(col, pulley_pos=pulley_pos)
    s2._parent_equip_to_bone(straight_bar, arm_obj, "Bone_StraightBar")
    s2._parent_equip_to_bone(cable, arm_obj, "Bone_Cable_Center")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_cable_bicep_curl(arm_obj, d, bad_form=is_bad, pulley_pos=pulley_pos)
            s2._key_all_pose_bones(arm_obj, f, key_scale=True)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Biceps"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 7. CLOSE-GRIP BENCH PRESS (Day nguc & tay sau nam hep tay)
# ---------------------------------------------------------------------------
def _pose_close_grip_bench_press(arm_obj, depth: float, bad_form: bool) -> None:
    s2 = _s2()
    s2._reset_pose(arm_obj)

    hip_lift = 0.11 * depth if bad_form else 0.0
    s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.34, 0.56 + hip_lift)))
    torso_dir = Vector((0.0, 1.0, 0.02 - 0.16 * hip_lift)).normalized()
    s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        s2._aim_bone_world(arm_obj, bname, Vector((0.0, 1.0, 0.02)), Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.99, 0.08)), Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Head", Vector((0.0, 0.99, 0.14)), Vector((1.0, 0.0, 0.0)))

    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.22, -0.68, 0.092))
        knee_pole = Vector((sx * 0.28, -0.85, 0.55))
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Good: ha don ve chan uc (Y=-0.02, Z=0.68), nam ngang vai (X=+-0.195), khuyu khep sat suon
    # Bad: nam tay qua sat (X=+-0.085) xoan co tay & xoe rong khuyu tay, hong nhac & ha cao ve co/vai
    bar_y = 0.05 + (0.09 * depth if bad_form else -0.07 * depth)
    bar_z = 1.03 - (0.29 * depth if bad_form else 0.35 * depth)
    grip_x = 0.085 if bad_form else 0.195

    fists: list[Vector] = []
    for side, sx in (("L", 1.0), ("R", -1.0)):
        palm_pos = Vector((sx * grip_x, bar_y, bar_z))
        elbow_pole = (
            Vector((sx * 0.95, 0.08, -0.22)).normalized()
            if bad_form
            else Vector((sx * 0.24, -0.88, -0.44)).normalized()
        )
        fist_pos = s2._solve_arm_grip_ik(
            arm_obj,
            side,
            palm_pos,
            Vector((0.0, 0.0, 1.0)),
            Vector((-sx * 1.0, 0.0, 0.0)),
            elbow_pole,
            Vector((0.0, -1.0, 0.0)),
            Vector((-sx * 0.6, -0.8, 0.0)).normalized(),
        )
        fists.append(fist_pos)
    s2._set_bone_world_head(
        arm_obj,
        "Bone_Barbell",
        Vector((0.0, 0.5 * (fists[0].y + fists[1].y), max(0.66, 0.5 * (fists[0].z + fists[1].z)))),
    )


def build_close_grip_bench_press(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_Barbell")
    s2._build_flat_bench_object(col, "Equip_Bench")
    barbell = s2._build_barbell_object(col, "Equip_Barbell")
    s2._parent_equip_to_bone(barbell, arm_obj, "Bone_Barbell")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        s2._begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_close_grip_bench_press(arm_obj, d, bad_form=is_bad)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Triceps", "Mat_Muscle_Chest"],
        secondary=["Mat_Muscle_Shoulders"],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}


# ---------------------------------------------------------------------------
# 8. STANDING CALF RAISE (Nhon bap chan dung voi may)
# ---------------------------------------------------------------------------
def _pose_standing_calf_raise(
    arm_obj,
    depth: float,
    bad_form: bool,
    frame: int = 1,
) -> None:
    import bpy  # type: ignore

    s2 = _s2()
    s2._reset_pose(arm_obj)

    if bad_form:
        # Loi: nhun nay nhanh nong can, chung goi (0.045m) & khong giu duoi cang o day
        # Tao dao dong nay nhip doi quanh vung day (frame 25..75)
        bounce = 0.26 * math.sin((frame - 1) * 0.35) if 25 <= frame <= 75 else 0.0
        eff = max(0.0, min(0.70, depth * 0.50 + bounce))
        ankle_y = -0.03 + 0.02 * eff
        ankle_z = 0.285 - 0.045 * eff
        knee_bend = 0.042 + 0.020 * math.sin(eff * math.pi)
        pelvis_z = ankle_z + 0.805 - knee_bend
        knee_pole_y = -0.72
        foot_z = -0.50 + 0.34 * eff
    else:
        # Dung ky thuat: d=0 nhon cao het co (ankle Z=0.330); d=1 ha got sau duoi mep buc Z=0.16 (ankle Z=0.175) va giu 1s
        eff = depth
        ankle_y = -0.035 + 0.050 * eff
        ankle_z = 0.330 - 0.155 * eff
        pelvis_z = ankle_z + 0.806
        knee_pole_y = -0.92
        foot_z = -0.70 + 0.94 * eff

    s2._set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, 0.03, pelvis_z)))
    torso_dir = Vector((0.0, -0.02, 1.0)).normalized()
    s2._aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        s2._aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.03, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))
    s2._aim_bone_world(arm_obj, "Head", Vector((0.0, -0.02, 1.0)).normalized(), Vector((1.0, 0.0, 0.0)))

    foot_dir = Vector((0.0, -math.sqrt(max(0.1, 1.0 - foot_z * foot_z * 0.5)), foot_z * 0.7)).normalized()
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.14, ankle_y, ankle_z))
        knee_pole = Vector((sx * 0.14, knee_pole_y, 0.32)).normalized()
        s2._solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            knee_pole,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        s2._aim_bone_world(arm_obj, f"Foot_{side}", foot_dir, Vector((1.0, 0.0, 0.0)))

    # Dat dem vai cua may khit len cau vai / Spine_03 tail (yoke origin tai vai top)
    bpy.context.view_layer.update()
    sp3_mat = arm_obj.matrix_world @ arm_obj.pose.bones["Spine_03"].matrix
    yoke_pos = Vector((0.0, sp3_mat.translation.y, sp3_mat.translation.z + 0.115))
    s2._set_bone_world_axes(
        arm_obj,
        "Bone_CalfYoke",
        yoke_pos,
        Vector((1.0, 0.0, 0.0)),
        Vector((0.0, 1.0, 0.0)),
        Vector((0.0, 0.0, 1.0)),
    )

    # Hai tay nam chac tay cam phia truoc cua khung vai (relative: (+-0.21, -0.30, -0.02))
    for side, sx in (("L", 1.0), ("R", -1.0)):
        grip_pos = yoke_pos + Vector((sx * 0.21, -0.30, -0.02))
        s2._solve_arm_grip_ik(
            arm_obj,
            side,
            grip_pos,
            Vector((0.0, -0.65, -0.76)).normalized(),
            Vector((-sx * 1.0, 0.0, 0.0)),
            Vector((sx * 0.55, 0.80, -0.20)).normalized(),
            Vector((0.0, -1.0, 0.0)),
            Vector((0.0, -1.0, 0.0)),
        )


def build_standing_calf_raise(
    export_paths: list[Path],
    blend_path: Path | None = None,
    heatmap_preview: bool = False,
) -> dict:
    import bpy  # type: ignore

    s2 = _s2()
    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False, grip_hands=True)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    s2._add_ctrl_bone(arm_obj, "Bone_CalfYoke")
    _, yoke = _build_standing_calf_machine(col)
    s2._parent_equip_to_bone(yoke, arm_obj, "Bone_CalfYoke")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes_good = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    keyframes_bad = [1, 14, 24, 34, 42, 48, 54, 62, 72, 86, 100]
    for clip_name, is_bad, kf in [
        ("Anim_GoodForm", False, keyframes_good),
        ("Anim_BadForm", True, keyframes_bad),
    ]:
        s2._begin_action(arm_obj, clip_name)
        for f in kf:
            d = s2._rep_curve(f, 1, 45, 55, 100)
            _pose_standing_calf_raise(arm_obj, d, bad_form=is_bad, frame=f)
            s2._key_all_pose_bones(arm_obj, f)
        s2._push_action_to_nla(arm_obj, clip_name, 1, 100)

    s2._export_and_save_outputs(
        arm_obj,
        export_paths=export_paths,
        blend_path=blend_path,
        primary=["Mat_Muscle_Calves"],
        secondary=[],
        stabilizer=["Mat_Muscle_Abs_Core"],
        heatmap_preview=heatmap_preview,
    )
    return {"frames": 100}
