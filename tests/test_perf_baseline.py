from __future__ import annotations

import json
import time
from pathlib import Path

from app.app_context import AppContext
from core.commands.demo_commands import FillVoxelCommand, PaintVoxelCommand
from core.meshing.solidify import build_solid_mesh
from core.project import Project


def test_perf_baseline_harness_non_blocking_thresholds() -> None:
    baseline_path = Path(__file__).with_name("perf_baseline.json")
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    default_multiplier = float(baseline.get("regression_multiplier", 12.0))
    metric_multipliers = baseline.get("metric_multipliers", {})

    brush_time = _measure_brush_paint()
    fill_time = _measure_fill()
    solidify_time = _measure_solidify()
    viewport_time = _measure_viewport_surrogate()
    viewport_repeat_time = _measure_viewport_surrogate_repeat()
    dense_64_time = _measure_dense_scene_tier(64)
    dense_96_time = _measure_dense_scene_tier(96)
    dense_128_time = _measure_dense_scene_tier(128)

    assert brush_time < float(baseline["brush_paint_seconds"]) * float(
        metric_multipliers.get("brush_paint_seconds", default_multiplier)
    )
    assert fill_time < float(baseline["fill_seconds"]) * float(
        metric_multipliers.get("fill_seconds", default_multiplier)
    )
    assert solidify_time < float(baseline["solidify_seconds"]) * float(
        metric_multipliers.get("solidify_seconds", default_multiplier)
    )
    assert viewport_time < float(baseline["viewport_surrogate_seconds"]) * float(
        metric_multipliers.get("viewport_surrogate_seconds", default_multiplier)
    )
    assert viewport_repeat_time < float(baseline["viewport_surrogate_repeat_seconds"]) * float(
        metric_multipliers.get("viewport_surrogate_repeat_seconds", default_multiplier)
    )
    assert dense_64_time < float(baseline["dense_64_seconds"]) * float(
        metric_multipliers.get("dense_64_seconds", default_multiplier)
    )
    assert dense_96_time < float(baseline["dense_96_seconds"]) * float(
        metric_multipliers.get("dense_96_seconds", default_multiplier)
    )
    assert dense_128_time < float(baseline["dense_128_seconds"]) * float(
        metric_multipliers.get("dense_128_seconds", default_multiplier)
    )


def _measure_brush_paint() -> float:
    ctx = AppContext(current_project=Project(name="Perf Brush"))
    start = time.perf_counter()
    for i in range(300):
        x = i % 30
        y = i // 30
        ctx.command_stack.do(PaintVoxelCommand(x, y, 0, 3), ctx)
    return time.perf_counter() - start


def _measure_fill() -> float:
    ctx = AppContext(current_project=Project(name="Perf Fill"))
    voxels = ctx.current_project.voxels
    for x in range(35):
        for y in range(35):
            voxels.set(x, y, 0, 1)
    start = time.perf_counter()
    ctx.command_stack.do(FillVoxelCommand(0, 0, 0, mode="erase"), ctx)
    return time.perf_counter() - start


def _measure_solidify() -> float:
    ctx = AppContext(current_project=Project(name="Perf Solidify"))
    voxels = ctx.current_project.voxels
    for x in range(18):
        for y in range(18):
            for z in range(6):
                voxels.set(x, y, z, 2)
    start = time.perf_counter()
    build_solid_mesh(voxels, greedy=True)
    return time.perf_counter() - start


def _measure_viewport_surrogate() -> float:
    ctx = AppContext(current_project=Project(name="Perf Viewport Surrogate"))
    second = ctx.current_project.scene.add_part("Part 2")
    for x in range(20):
        for y in range(10):
            ctx.current_project.voxels.set(x, y, 0, 1)
            second.voxels.set(-x, y, 1, 2)
    start = time.perf_counter()
    total = 0
    for _ in range(10):
        for part in ctx.current_project.scene.iter_visible_parts():
            total += len(part.voxels.to_list())
    # Prevent loop elimination assumptions in future refactors.
    assert total > 0
    return time.perf_counter() - start


def _measure_viewport_surrogate_repeat() -> float:
    # Repeated viewport-surrogate pass acts as a hot-path guard for navigation loops.
    first = _measure_viewport_surrogate()
    second = _measure_viewport_surrogate()
    return min(first, second)


def _measure_dense_scene_tier(size: int) -> float:
    ctx = AppContext(current_project=Project(name=f"Perf Dense {size}"))
    voxels = ctx.current_project.voxels
    # Tiered sparse fill keeps runtime stable while still scaling the working bounds.
    for x in range(0, int(size), 4):
        for y in range(0, int(size), 4):
            for z in range(0, int(size), 8):
                voxels.set(x, y, z, ((x + y + z) % 6) + 1)
    start = time.perf_counter()
    build_solid_mesh(voxels, greedy=True)
    return time.perf_counter() - start
