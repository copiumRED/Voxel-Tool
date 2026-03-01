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
    multiplier = float(baseline.get("regression_multiplier", 20.0))

    brush_time = _measure_brush_paint()
    fill_time = _measure_fill()
    solidify_time = _measure_solidify()
    viewport_time = _measure_viewport_surrogate()

    assert brush_time < float(baseline["brush_paint_seconds"]) * multiplier
    assert fill_time < float(baseline["fill_seconds"]) * multiplier
    assert solidify_time < float(baseline["solidify_seconds"]) * multiplier
    assert viewport_time < float(baseline["viewport_surrogate_seconds"]) * multiplier


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
