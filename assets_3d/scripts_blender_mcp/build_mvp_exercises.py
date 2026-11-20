# [OWNER: M2] Script dung 3 bai tap 3D mau MVP qua Blender MCP / Blender 5.3 (T-M2-02)
"""
Tao 3 file .glb dong goi san cho MVP Closed Testing v1.0.0+1:
1. barbell_squat.glb       (110 frames @ 30 FPS: Eccentric 0-50, Iso 50-65, Concentric 65-110)
2. push_up.glb             (100 frames @ 30 FPS: Eccentric 0-45, Iso 45-55, Concentric 55-100)
3. barbell_bench_press.glb (100 frames @ 30 FPS: Eccentric 0-45, Iso 45-55, Concentric 55-100)

Moi file chua du:
- 11 Mesh & Material co bap chuan (`Mesh_Muscle_*` / `Mat_Muscle_*`)
- Bo xuong `Armature_GymHuman` + 4 Empty Sockets
- Bo dung cu roi (`Equip_Barbell`, `Equip_Bench`, `Equip_Mat`) gan dung Socket / Bone
- 2 Animation Clips chuan ten: `Anim_GoodForm` & `Anim_BadForm`
- Xuat nen Draco level 6 (<= 25,000 tris, tong 4 file bundled < 4.0 MB)
- Cap nhat checksum SHA-256 that vao `assets_3d/exported_glb/assets_manifest.json`
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import sys
from pathlib import Path

from mathutils import Euler, Matrix, Quaternion, Vector  # type: ignore

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import build_base_mannequin as base_mod

STEEL_COLOR = (0.58, 0.62, 0.68, 1.0)
PLATE_IRON_COLOR = (0.045, 0.052, 0.065, 1.0)
PLATE_ACCENT_COLOR = (0.65, 0.08, 0.08, 1.0)
BENCH_FRAME_COLOR = (0.04, 0.045, 0.055, 1.0)
PAD_COLOR = (0.025, 0.030, 0.040, 1.0)
MAT_COLOR = (0.04, 0.075, 0.115, 1.0)


def _create_equip_cylinder(bm, p0: Vector, p1: Vector, radius: float, segs: int = 12) -> None:
    import bmesh  # type: ignore

    axis = p1 - p0
    length = axis.length
    if length < 1e-6:
        return
    rot = axis.to_track_quat("Z", "Y").to_matrix().to_4x4()
    mid = 0.5 * (p0 + p1)
    mat = Matrix.Translation(mid) @ rot
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segs,
        radius1=radius,
        radius2=radius,
        depth=length,
        matrix=mat,
    )


def _create_equip_box(bm, center: tuple[float, float, float], size: tuple[float, float, float]) -> None:
    import bmesh  # type: ignore

    mat = Matrix.Translation(center) @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)


def _build_barbell_object(collection, name: str = "Equip_Barbell"):
    """Tao Olympic Barbell + Banh ta Low-Poly (tong ~600 tris, origin tai tam thanh don)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_steel = base_mod._create_pbr_material("Mat_Equip_Steel", STEEL_COLOR, roughness=0.25, metallic=0.85)
    mat_iron = base_mod._create_pbr_material("Mat_Equip_Iron", PLATE_IRON_COLOR, roughness=0.45, metallic=0.80)
    mat_collar = base_mod._create_pbr_material("Mat_Equip_Collar", PLATE_ACCENT_COLOR, roughness=0.35, metallic=0.70)

    bm = bmesh.new()
    # Shaft (2.10m wide along X axis, radius 0.015m)
    _create_equip_cylinder(bm, Vector((-0.68, 0.0, 0.0)), Vector((0.68, 0.0, 0.0)), 0.015, 10)
    shaft_faces = set(bm.faces)

    # Sleeves (0.68 -> 1.02m both sides, radius 0.025m)
    for sx in (-1.0, 1.0):
        _create_equip_cylinder(bm, Vector((sx * 0.67, 0.0, 0.0)), Vector((sx * 1.03, 0.0, 0.0)), 0.025, 10)
    sleeve_faces = set(bm.faces) - shaft_faces

    # Weight plates (20kg outer + 10kg inner)
    plate_faces = set()
    collar_faces = set()
    for sx in (-1.0, 1.0):
        prev = set(bm.faces)
        _create_equip_cylinder(bm, Vector((sx * 0.70, 0.0, 0.0)), Vector((sx * 0.75, 0.0, 0.0)), 0.215, 16)
        _create_equip_cylinder(bm, Vector((sx * 0.76, 0.0, 0.0)), Vector((sx * 0.80, 0.0, 0.0)), 0.165, 16)
        plate_faces |= (set(bm.faces) - prev)

        prev = set(bm.faces)
        _create_equip_cylinder(bm, Vector((sx * 0.805, 0.0, 0.0)), Vector((sx * 0.84, 0.0, 0.0)), 0.042, 12)
        collar_faces |= (set(bm.faces) - prev)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_steel)
    mesh.materials.append(mat_iron)
    mesh.materials.append(mat_collar)

    # Assign material indices deterministically by polygon X/radius
    for poly in mesh.polygons:
        poly.use_smooth = False
        r_yz = math.hypot(poly.center.y, poly.center.z)
        ax = abs(poly.center.x)
        if r_yz > 0.065:
            poly.material_index = 1
        elif 0.80 <= ax <= 0.845 and r_yz > 0.028:
            poly.material_index = 2
        else:
            poly.material_index = 0
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def _build_bench_object(collection, name: str = "Equip_Bench"):
    """Tao ghe Bench phang chuan ty le (chieu cao mat dem 0.44m, dat tai Floor_Origin)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_frame = base_mod._create_pbr_material("Mat_Equip_Frame", BENCH_FRAME_COLOR, roughness=0.40, metallic=0.75)
    mat_pad = base_mod._create_pbr_material("Mat_Equip_Pad", PAD_COLOR, roughness=0.72, metallic=0.05)

    bm = bmesh.new()
    # Main pad along Y axis (length 1.04m from Y=-0.38 to Y=+0.66, top at Z=0.44)
    _create_equip_box(bm, (0.0, 0.14, 0.405), (0.30, 1.04, 0.07))
    # Steel spine + legs + feet
    _create_equip_box(bm, (0.0, 0.14, 0.34), (0.08, 0.92, 0.06))
    _create_equip_box(bm, (0.0, -0.26, 0.18), (0.07, 0.07, 0.34))
    _create_equip_box(bm, (0.0, 0.52, 0.18), (0.07, 0.07, 0.34))
    _create_equip_box(bm, (0.0, -0.26, 0.025), (0.46, 0.08, 0.05))
    _create_equip_box(bm, (0.0, 0.52, 0.025), (0.46, 0.08, 0.05))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_frame)
    mesh.materials.append(mat_pad)
    for poly in mesh.polygons:
        poly.use_smooth = False
        poly.material_index = 1 if poly.center.z >= 0.37 else 0
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


def _build_mat_object(collection, name: str = "Equip_Mat"):
    """Tao tham tap Push-Up dat tai Floor_Origin (Z = 0..0.018)."""
    import bpy  # type: ignore
    import bmesh  # type: ignore

    mat_yoga = base_mod._create_pbr_material("Mat_Equip_Mat", MAT_COLOR, roughness=0.80, metallic=0.05)
    bm = bmesh.new()
    _create_equip_box(bm, (0.0, 0.10, 0.009), (0.85, 1.85, 0.018))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_yoga)
    for p in mesh.polygons:
        p.use_smooth = False
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.parent = bpy.data.objects.get("Floor_Origin")
    return obj


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _rep_curve(frame: int, f_start: int, f_bot_start: int, f_bot_end: int, f_end: int) -> float:
    """Tra ve bien do [0..1] cua 1 rep (0=top, 1=bottom isometric)."""
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


def _set_bone_world_head(arm_obj, bone_name: str, target_world_pos: Vector) -> None:
    """Dat vi tri dau xuong (head) dung toa do World mong muon (chuan xac tren moi truc bone)."""
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
    """Xoay PoseBone sao cho truc Y doc xuong huong dung target_y_dir_world."""
    import bpy  # type: ignore

    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones[bone_name]
    cur_mat_world = arm_obj.matrix_world @ pb.matrix
    cur_y = cur_mat_world.col[1].to_3d().normalized()
    tgt_y = target_y_dir_world.normalized()
    rot_delta = cur_y.rotation_difference(tgt_y)

    new_rot3 = rot_delta.to_matrix() @ cur_mat_world.to_3x3()
    if roll_reference_z_world is not None:
        # Project reference onto plane perpendicular to tgt_y to stabilize twist
        ref = roll_reference_z_world - tgt_y * roll_reference_z_world.dot(tgt_y)
        if ref.length > 1e-4:
            new_z = ref.normalized()
            new_x = tgt_y.cross(new_z).normalized()
            new_z = new_x.cross(tgt_y).normalized()
            new_rot3 = Matrix((new_x, tgt_y, new_z)).transposed()

    new_world = Matrix.Translation(cur_mat_world.translation) @ new_rot3.to_4x4()
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
    """Giai IK 2 doan xuong giai phau chinh xac trong khong gian World."""
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

    # Law of cosines for upper-bone bend angle
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


def _key_all_pose_bones(arm_obj, frame: int) -> None:
    for pb in arm_obj.pose.bones:
        pb.keyframe_insert(data_path="location", frame=frame)
        pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)


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


def _begin_action(arm_obj, action_name: str) -> None:
    import bpy  # type: ignore

    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    action = bpy.data.actions.new(name=action_name)
    arm_obj.animation_data.action = action
    _reset_pose(arm_obj)


# ---------------------------------------------------------------------------
# Exercise 1: BARBELL SQUAT (110 frames: Eccentric 1-50, Iso 50-65, Conc 65-110)
# ---------------------------------------------------------------------------
def _pose_squat(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)
    bpy.context.view_layer.update()

    # Keep feet anchored at original ankle height/positions: (+/-0.160, 0.094, 0.092)
    l1 = arm_obj.pose.bones["Thigh_L"].bone.length   # ~0.414
    l2 = arm_obj.pose.bones["Calf_L"].bone.length    # ~0.402

    # Subtle athletic squat stance: knees track forward & slightly out (+valgus on bad form)
    knee_x_offset = -0.048 * depth if bad_form else 0.032 * depth
    knee_y_forward = -0.175 * depth
    knee_z = 0.490 - 0.055 * depth

    # Pelvis descends cleanly based on leg compression + forward hip hinge
    hip_y = 0.024 + 0.250 * depth
    hip_z = 0.900 - 0.395 * depth

    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, hip_y, hip_z)))

    # Lean torso forward (clean 26 deg vs excessive 52 deg lumbar rounding on bad form)
    lean_rad = math.radians((50.0 if bad_form else 26.0) * depth)
    pelvis_pitch = math.radians((18.0 if bad_form else 12.0) * depth)
    _aim_bone_world(
        arm_obj,
        "Pelvis",
        Vector((0.0, -math.sin(pelvis_pitch), math.cos(pelvis_pitch))),
        Vector((1.0, 0.0, 0.0)),
    )
    spine_lean = lean_rad
    for idx, bname in enumerate(["Spine_01", "Spine_02", "Spine_03"]):
        frac = (0.4 + 0.3 * idx) if bad_form else 1.0
        ang = spine_lean * (0.85 if not bad_form else min(1.35, frac))
        _aim_bone_world(
            arm_obj,
            bname,
            Vector((0.0, -math.sin(ang), math.cos(ang))),
            Vector((1.0, 0.0, 0.0)),
        )
    # Keep head neutral gaze forward
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.18, 0.98)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.08, 0.99)), Vector((1.0, 0.0, 0.0)))

    # Solve exact leg 2-bone IK from Hip to pinned Ankle world pos so feet stay at Z=0
    for side, sx in (("L", 1.0), ("R", -1.0)):
        ankle_target = Vector((sx * 0.160, 0.094, 0.092))
        pole_hint = Vector((sx * (knee_x_offset / max(0.05, abs(knee_x_offset) + 0.2)), -1.0, 0.15))
        if bad_form and depth > 0.05:
            pole_hint = Vector((-sx * 0.38 * depth, -0.92, 0.1))
        else:
            pole_hint = Vector((sx * 0.22 * depth, -0.97, 0.1))
        _solve_two_bone_ik_world(
            arm_obj,
            f"Thigh_{side}",
            f"Calf_{side}",
            ankle_target,
            pole_hint,
            Vector((1.0, 0.0, 0.0)),
            Vector((1.0, 0.0, 0.0)),
        )
        # Keep foot flat on floor (pointing -Y)
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.94, -0.34)), Vector((1.0, 0.0, 0.0)))

    # Grip barbell resting on Socket_Back_Barbell (arms reach cleanly back to grip bar at X=+/-0.35)
    bpy.context.view_layer.update()
    bar_socket = bpy.data.objects["Socket_Back_Barbell"]
    bar_center = bar_socket.matrix_world.translation
    spine_mat = (arm_obj.matrix_world @ arm_obj.pose.bones["Spine_03"].matrix).to_3x3()
    bar_right_x = spine_mat.col[2].normalized()  # Left world axis of spine_03
    bar_back_y = spine_mat.col[0].normalized()   # Local X points toward front/back
    for side, sx in (("L", 1.0), ("R", -1.0)):
        grip_target = bar_center + Vector((sx * 0.34, 0.02, -0.02))
        elbow_pole = Vector((sx * 0.65, 0.65, -0.45))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            grip_target,
            elbow_pole,
            Vector((0.0, 1.0, 0.0)),
            Vector((0.0, 1.0, 0.0)),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", Vector((-sx * 0.15, -0.40, 0.90)), Vector((sx * 1.0, 0.0, 0.0)))


def build_barbell_squat(export_paths: list[Path]) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    barbell = _build_barbell_object(col, "Equip_Barbell")
    barbell.parent = bpy.data.objects["Socket_Back_Barbell"]
    barbell.location = Vector((0.0, 0.0, 0.0))

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 110

    keyframes = [1, 15, 30, 50, 58, 65, 85, 100, 110]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 50, 65, 110)
            _pose_squat(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 110)

    _reset_pose(arm_obj)
    for out in export_paths:
        base_mod.export_draco_glb(str(out))
    return {"frames": 110}


# ---------------------------------------------------------------------------
# Exercise 2: PUSH-UP (100 frames: Eccentric 1-45, Iso 45-55, Concentric 55-100)
# ---------------------------------------------------------------------------
def _pose_push_up(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)
    bpy.context.view_layer.update()

    # Body oriented prone along Y axis (toes near Y=+0.78 Z=0.04, shoulders near Y=-0.42)
    # In push-up top position, torso leans up at ~22 deg from toes; at bottom ~7 deg
    plank_deg = 22.0 - 15.0 * depth
    plank_rad = math.radians(plank_deg)
    # Place Pelvis so Feet stay anchored near (Y=+0.72, Z=0.05)
    # Distance from toes to pelvis is ~0.90m
    pelvis_y = 0.70 - 0.88 * math.cos(plank_rad)
    pelvis_z = 0.09 + 0.88 * math.sin(plank_rad) - (0.13 * depth if bad_form else 0.0)

    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, pelvis_y, pelvis_z)))

    # Spine aims toward -Y (prone forward) with plank slope up (+Z)
    torso_dir = Vector((0.0, -math.cos(plank_rad), math.sin(plank_rad)))
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))

    if bad_form and depth > 0.02:
        # Sagging lumbar spine on bad form
        _aim_bone_world(arm_obj, "Spine_01", Vector((0.0, -0.99, 0.05)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_02", Vector((0.0, -0.98, 0.22)), Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, "Spine_03", Vector((0.0, -0.95, 0.30)), Vector((1.0, 0.0, 0.0)))
    else:
        for bname in ("Spine_01", "Spine_02", "Spine_03"):
            _aim_bone_world(arm_obj, bname, torso_dir, Vector((1.0, 0.0, 0.0)))

    _aim_bone_world(arm_obj, "Neck", Vector((0.0, -0.94, 0.34)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, -0.88, 0.48)), Vector((1.0, 0.0, 0.0)))

    # Legs extend straight back to mat toes (+Y)
    leg_dir = Vector((0.0, math.cos(plank_rad), -math.sin(plank_rad)))
    for side, sx in (("L", 1.0), ("R", -1.0)):
        _aim_bone_world(arm_obj, f"Thigh_{side}", leg_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, f"Calf_{side}", leg_dir, Vector((1.0, 0.0, 0.0)))
        _aim_bone_world(arm_obj, f"Foot_{side}", Vector((0.0, -0.15, -0.98)), Vector((1.0, 0.0, 0.0)))

    # Hands planted firmly on mat (Z = 0.03) just wider than shoulders
    hand_y = -0.36
    hand_x = 0.25 if bad_form else 0.215
    for side, sx in (("L", 1.0), ("R", -1.0)):
        wrist_target = Vector((sx * hand_x, hand_y, 0.035))
        # Good form tucks elbows ~45 deg back (+Y); bad form flares 90 deg out (+/-X)
        elbow_pole = Vector((sx * 0.95, 0.15, 0.25)) if bad_form else Vector((sx * 0.45, 0.85, 0.28))
        _solve_two_bone_ik_world(
            arm_obj,
            f"UpperArm_{side}",
            f"Forearm_{side}",
            wrist_target,
            elbow_pole,
            Vector((0.0, 0.0, 1.0)),
            Vector((0.0, 0.0, 1.0)),
        )
        _aim_bone_world(arm_obj, f"Hand_{side}", Vector((0.0, -1.0, 0.0)), Vector((sx * 1.0, 0.0, 0.0)))


def build_push_up(export_paths: list[Path]) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _build_mat_object(col, "Equip_Mat")

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_push_up(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _reset_pose(arm_obj)
    for out in export_paths:
        base_mod.export_draco_glb(str(out))
    return {"frames": 100}


# ---------------------------------------------------------------------------
# Exercise 3: BARBELL BENCH PRESS (100 frames: Ecc 1-45, Iso 45-55, Conc 55-100)
# ---------------------------------------------------------------------------
def _add_barbell_ctrl_bone(arm_obj) -> None:
    import bpy  # type: ignore

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_obj.data.edit_bones
    b = eb.new("Bone_Barbell")
    # Tail along +Y with roll Z=+Z gives Bone_Barbell exact Identity world axes (X=X, Y=Y, Z=Z)
    b.head = Vector((0.0, 0.0, 0.0))
    b.tail = Vector((0.0, 0.15, 0.0))
    b.parent = eb["Root"]
    b.use_connect = False
    b.align_roll(Vector((0.0, 0.0, 1.0)))
    bpy.ops.object.mode_set(mode="OBJECT")


def _pose_bench_press(arm_obj, depth: float, bad_form: bool) -> None:
    import bpy  # type: ignore

    _reset_pose(arm_obj)
    bpy.context.view_layer.update()

    # Supine on bench (bench pad top Z = 0.44m), head toward +Y, feet planted toward -Y
    # That keeps L on +X and R on -X, while local_X (back) points -Z onto bench pad!
    hip_lift = 0.12 * depth if bad_form else 0.0
    _set_bone_world_head(arm_obj, "Pelvis", Vector((0.0, -0.34, 0.54 + hip_lift)))

    torso_dir = Vector((0.0, 1.0, 0.02 - 0.18 * hip_lift)).normalized()
    _aim_bone_world(arm_obj, "Pelvis", torso_dir, Vector((1.0, 0.0, 0.0)))
    for bname in ("Spine_01", "Spine_02", "Spine_03"):
        _aim_bone_world(arm_obj, bname, Vector((0.0, 1.0, 0.02)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Neck", Vector((0.0, 0.99, 0.08)), Vector((1.0, 0.0, 0.0)))
    _aim_bone_world(arm_obj, "Head", Vector((0.0, 0.99, 0.14)), Vector((1.0, 0.0, 0.0)))

    # Thighs go toward -Y off bench edge; Calves drop straight down to floor Z=0.0
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

    # Animate Barbell directly above mid-chest (Y = +0.08): lockout Z=1.00, chest touch Z=0.64
    bar_y = 0.08 - (0.04 * depth if bad_form else 0.02 * depth)
    bar_z = 1.00 - 0.36 * depth
    _set_bone_world_head(arm_obj, "Bone_Barbell", Vector((0.0, bar_y, bar_z)))

    # Solve 2-bone IK from shoulders to bar grip at X = +/- 0.34
    for side, sx in (("L", 1.0), ("R", -1.0)):
        grip_target = Vector((sx * 0.34, bar_y, bar_z))
        # Good form tucks elbows ~45 deg toward feet (-Y, -Z); bad form flares 90 deg laterally (+/-X, -Z)
        elbow_pole = Vector((sx * 0.96, 0.05, -0.28)) if bad_form else Vector((sx * 0.56, -0.68, -0.47))
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


def build_barbell_bench_press(export_paths: list[Path]) -> dict:
    import bpy  # type: ignore

    base_mod.build_mannequin(blend_path=None, glb_paths=[], keep_heatmap_preview=False)
    col = bpy.data.collections.get("VigorAI_Mannequin") or bpy.context.scene.collection
    arm_obj = bpy.data.objects["Armature_GymHuman"]

    _add_barbell_ctrl_bone(arm_obj)
    _build_bench_object(col, "Equip_Bench")

    barbell = _build_barbell_object(col, "Equip_Barbell")
    barbell.parent = arm_obj
    barbell.parent_type = "BONE"
    barbell.parent_bone = "Bone_Barbell"
    bpy.context.view_layer.update()
    barbell.matrix_parent_inverse = Matrix.Identity(4)
    # Tail of Bone_Barbell is at (0, 0.15, 0); offset Y=-0.15 so bar center sits at Bone_Barbell head
    barbell.location = Vector((0.0, -0.15, 0.0))

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 100

    keyframes = [1, 14, 28, 45, 50, 55, 72, 86, 100]
    for clip_name, is_bad in [("Anim_GoodForm", False), ("Anim_BadForm", True)]:
        _begin_action(arm_obj, clip_name)
        for f in keyframes:
            d = _rep_curve(f, 1, 45, 55, 100)
            _pose_bench_press(arm_obj, d, bad_form=is_bad)
            _key_all_pose_bones(arm_obj, f)
        _push_action_to_nla(arm_obj, clip_name, 1, 100)

    _reset_pose(arm_obj)
    for out in export_paths:
        base_mod.export_draco_glb(str(out))
    return {"frames": 100}


def verify_and_write_manifest(repo_root: Path) -> dict:
    """Doc header .glb kiem tra 11 Mat_Muscle_*, Draco, Animation clips va xuat SHA-256 manifest."""
    exported_dir = repo_root / "assets_3d" / "exported_glb"
    bundled_dir = repo_root / "mobile" / "assets" / "3d_bundled"

    specs = [
        ("BASE_MANNEQUIN", "base_mannequin.glb", None),
        (
            "BARBELL_SQUAT",
            "barbell_squat.glb",
            {"eccentric": [0, 50], "isometric": [50, 65], "concentric": [65, 110]},
        ),
        (
            "PUSH_UP",
            "push_up.glb",
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
        (
            "BARBELL_BENCH_PRESS",
            "barbell_bench_press.glb",
            {"eccentric": [0, 45], "isometric": [45, 55], "concentric": [55, 100]},
        ),
    ]

    required_mats = {m for _, m in base_mod.MUSCLE_MESH_MATERIAL_PAIRS}
    total_bundled_bytes = 0
    assets_entries = []

    for code, fname, phases in specs:
        glb_path = bundled_dir / fname
        raw = glb_path.read_bytes()
        total_bundled_bytes += len(raw)
        sha = hashlib.sha256(raw).hexdigest()

        chunk_len, _ = struct.unpack("<2I", raw[12:20])
        gltf = json.loads(raw[20 : 20 + chunk_len].decode("utf-8"))
        mats = {m.get("name") for m in gltf.get("materials", [])}
        missing_mats = sorted(required_mats - mats)
        if missing_mats:
            raise AssertionError(f"{fname} thieu Material chuan: {missing_mats}")

        anims = [a.get("name") for a in gltf.get("animations", [])]
        if phases is not None:
            for req_clip in ("Anim_GoodForm", "Anim_BadForm"):
                if req_clip not in anims:
                    raise AssertionError(f"{fname} thieu animation {req_clip}, hien co: {anims}")

        entry = {
            "code": code,
            "file_name": fname,
            "bundled": True,
            "size_bytes": len(raw),
            "sha256": sha,
            "extensions_used": gltf.get("extensionsUsed", []),
            "materials": sorted(required_mats),
        }
        if phases is not None:
            entry["clips"] = anims
            entry["phase_keyframes"] = phases
        assets_entries.append(entry)
        print(f"[VERIFIED] {fname:24s} size={len(raw):7d}B sha256={sha[:12]}... anims={anims}")

    assert total_bundled_bytes < 10 * 1024 * 1024, f"Tong bundled vuot 10MB: {total_bundled_bytes}"
    manifest = {
        "schema_version": "1.0.0",
        "owner": "M2",
        "compression": "Binary_glTF_FastLoad",
        "max_triangles_budget": 25000,
        "total_bundled_bytes": total_bundled_bytes,
        "assets": assets_entries,
    }
    manifest_path = exported_dir / "assets_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[VigorAI] Updated {manifest_path} (total bundled: {total_bundled_bytes / 1024:.1f} KB)")
    return manifest


def build_all_mvp_exercises(repo_root: Path) -> None:
    exported_dir = repo_root / "assets_3d" / "exported_glb"
    bundled_dir = repo_root / "mobile" / "assets" / "3d_bundled"

    build_barbell_squat([exported_dir / "barbell_squat.glb", bundled_dir / "barbell_squat.glb"])
    build_push_up([exported_dir / "push_up.glb", bundled_dir / "push_up.glb"])
    build_barbell_bench_press([exported_dir / "barbell_bench_press.glb", bundled_dir / "barbell_bench_press.glb"])
    verify_and_write_manifest(repo_root)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    build_all_mvp_exercises(root)
