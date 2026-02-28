from __future__ import annotations

import base64
import json
import struct
from dataclasses import dataclass

from core.meshing.solidify import build_solid_mesh
from core.voxels.voxel_grid import VoxelGrid


@dataclass(slots=True)
class GltfExportStats:
    vertex_count: int
    triangle_count: int


def export_voxels_to_gltf(voxels: VoxelGrid, path: str) -> GltfExportStats:
    mesh = build_solid_mesh(voxels, greedy=True)
    if mesh.face_count == 0:
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

    positions = mesh.vertices
    indices: list[int] = []
    for a, b, c, d in mesh.quads:
        indices.extend((a, b, c, a, c, d))

    vertex_bytes = b"".join(struct.pack("<3f", x, y, z) for x, y, z in positions)
    index_bytes = b"".join(struct.pack("<I", idx) for idx in indices)
    if len(vertex_bytes) % 4 != 0:
        vertex_bytes += b"\x00" * (4 - (len(vertex_bytes) % 4))
    if len(index_bytes) % 4 != 0:
        index_bytes += b"\x00" * (4 - (len(index_bytes) % 4))
    combined = vertex_bytes + index_bytes
    data_uri = "data:application/octet-stream;base64," + base64.b64encode(combined).decode("ascii")

    min_bounds = [min(v[i] for v in positions) for i in range(3)]
    max_bounds = [max(v[i] for v in positions) for i in range(3)]
    payload = {
        "asset": {"version": "2.0", "generator": "VoxelTool"},
        "buffers": [{"byteLength": len(combined), "uri": data_uri}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(vertex_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": len(vertex_bytes), "byteLength": len(index_bytes), "target": 34963},
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
                "componentType": 5125,
                "count": len(indices),
                "type": "SCALAR",
            },
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    with open(path, "w", encoding="utf-8") as file_obj:
        json.dump(payload, file_obj, indent=2)
    return GltfExportStats(vertex_count=len(positions), triangle_count=len(indices) // 3)
