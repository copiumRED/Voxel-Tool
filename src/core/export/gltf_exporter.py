from __future__ import annotations

import base64
import json
import struct
from dataclasses import dataclass
from math import sqrt

from core.meshing.mesh import SurfaceMesh
from core.meshing.solidify import build_solid_mesh
from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class GltfExportStats:
    vertex_count: int
    triangle_count: int


def export_voxels_to_gltf(
    voxels: VoxelGrid,
    path: str,
    mesh: SurfaceMesh | None = None,
    *,
    scale_factor: float = 1.0,
) -> GltfExportStats:
    export_mesh = mesh or build_solid_mesh(voxels, greedy=True)
    if export_mesh.face_count == 0:
        payload = {
            "asset": {"version": "2.0", "generator": "VoxelTool"},
            "scenes": [{"nodes": []}],
            "scene": 0,
            "nodes": [],
            "meshes": [],
        }
        with open(path, "w", encoding="utf-8") as file_obj:
            json.dump(payload, file_obj, indent=2)
        return GltfExportStats(vertex_count=0, triangle_count=0)

    scale = float(scale_factor)
    positions = [(x * scale, y * scale, z * scale) for x, y, z in export_mesh.vertices]
    indices: list[int] = []
    for a, b, c, d in export_mesh.quads:
        indices.extend((a, b, c, a, c, d))
    normals = _build_vertex_normals(export_mesh, len(positions))

    vertex_bytes = b"".join(struct.pack("<3f", x, y, z) for x, y, z in positions)
    normal_bytes = b"".join(struct.pack("<3f", nx, ny, nz) for nx, ny, nz in normals)
    index_bytes = b"".join(struct.pack("<I", idx) for idx in indices)
    if len(vertex_bytes) % 4 != 0:
        vertex_bytes += b"\x00" * (4 - (len(vertex_bytes) % 4))
    if len(normal_bytes) % 4 != 0:
        normal_bytes += b"\x00" * (4 - (len(normal_bytes) % 4))
    if len(index_bytes) % 4 != 0:
        index_bytes += b"\x00" * (4 - (len(index_bytes) % 4))
    combined = vertex_bytes + normal_bytes + index_bytes
    data_uri = "data:application/octet-stream;base64," + base64.b64encode(combined).decode("ascii")

    min_bounds = [min(v[i] for v in positions) for i in range(3)]
    max_bounds = [max(v[i] for v in positions) for i in range(3)]
    payload = {
        "asset": {"version": "2.0", "generator": "VoxelTool"},
        "buffers": [{"byteLength": len(combined), "uri": data_uri}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(vertex_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(vertex_bytes), "byteLength": len(normal_bytes), "target": 34962},
            {
                "buffer": 0,
                "byteOffset": len(vertex_bytes) + len(normal_bytes),
                "byteLength": len(index_bytes),
                "target": 34963,
            },
        ],
        "accessors": [
            {
                "bufferView": 0,
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(positions),
                "type": "VEC3",
                "min": min_bounds,
                "max": max_bounds,
            },
            {
                "bufferView": 1,
                "byteOffset": 0,
                "componentType": 5126,
                "count": len(normals),
                "type": "VEC3",
            },
            {
                "bufferView": 2,
                "byteOffset": 0,
                "componentType": 5125,
                "count": len(indices),
                "type": "SCALAR",
            },
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "mode": 4}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)
    return GltfExportStats(vertex_count=len(positions), triangle_count=len(indices) // 3)


def _build_vertex_normals(mesh: SurfaceMesh, vertex_count: int) -> list[tuple[float, float, float]]:
    accum = [(0.0, 0.0, 0.0) for _ in range(vertex_count)]
    for face_index, quad in enumerate(mesh.quads):
        nx, ny, nz = mesh.quad_normal(face_index)
        for vertex_index in quad:
            ax, ay, az = accum[vertex_index]
            accum[vertex_index] = (ax + nx, ay + ny, az + nz)

    normals: list[tuple[float, float, float]] = []
    for nx, ny, nz in accum:
        length = sqrt((nx * nx) + (ny * ny) + (nz * nz))
        if length <= 1e-9:
            normals.append((0.0, 1.0, 0.0))
            continue
        normals.append((nx / length, ny / length, nz / length))
    return normals
