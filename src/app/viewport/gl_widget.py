from __future__ import annotations

import logging
from array import array
from ctypes import c_void_p
from math import cos, radians, sin
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMatrix4x4, QPainter, QVector3D
from PySide6.QtOpenGL import (
    QOpenGLBuffer,
    QOpenGLShader,
    QOpenGLShaderProgram,
    QOpenGLVertexArrayObject,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from core.commands.demo_commands import build_box_plane_cells, build_brush_cells, build_line_plane_cells
from core.voxels.raycast import resolve_brush_target_cell

if TYPE_CHECKING:
    from app.app_context import AppContext


class GLViewportWidget(QOpenGLWidget):
    voxel_edit_applied = Signal(str)
    viewport_ready = Signal(str)
    viewport_diagnostics = Signal(str)
    viewport_error = Signal(str)

    _GL_COLOR_BUFFER_BIT = 0x00004000
    _GL_DEPTH_BUFFER_BIT = 0x00000100
    _GL_POINTS = 0x0000
    _GL_LINES = 0x0001
    _GL_FLOAT = 0x1406
    _GL_DEPTH_TEST = 0x0B71
    _GL_ARRAY_BUFFER = 0x8892
    _GL_VENDOR = 0x1F00
    _GL_RENDERER = 0x1F01
    _GL_VERSION = 0x1F02
    _GL_NO_ERROR = 0
    _DEFAULT_YAW_DEG = 45.0
    _DEFAULT_PITCH_DEG = -30.0
    _DEFAULT_DISTANCE = 25.0
    _VOXEL_HALF_EXTENT = 0.45

    _PALETTE: tuple[tuple[float, float, float], ...] = (
        (0.95, 0.35, 0.35),
        (0.96, 0.62, 0.27),
        (0.97, 0.88, 0.30),
        (0.45, 0.85, 0.40),
        (0.30, 0.70, 0.95),
        (0.60, 0.55, 0.95),
        (0.90, 0.45, 0.85),
        (0.85, 0.85, 0.85),
    )

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self._app_context: AppContext | None = None
        self._program: QOpenGLShaderProgram | None = None
        self._buffer: QOpenGLBuffer | None = None
        self._vao: QOpenGLVertexArrayObject | None = None
        self._logger = logging.getLogger("voxel_tool")
        self.last_gl_info = "unknown"
        self._shader_profile = "unknown"
        self._init_error_text: str | None = None
        self._logged_pipeline_missing = False
        self.debug_overlay_enabled = True
        self.yaw_deg = self._DEFAULT_YAW_DEG
        self.pitch_deg = self._DEFAULT_PITCH_DEG
        self.distance = self._DEFAULT_DISTANCE
        self.target = QVector3D(0.0, 0.0, 0.0)
        self._last_mouse_pos: tuple[float, float] | None = None
        self._left_press_pos: QPointF | None = None
        self._left_dragging = False
        self._brush_stroke_active = False
        self._brush_stroke_last_cell: tuple[int, int, int] | None = None
        self._hover_preview_cells: set[tuple[int, int, int]] = set()
        self._hover_preview_source: str | None = None
        self._hover_preview_erase = False
        self._shape_preview_cells: set[tuple[int, int, int]] = set()
        self._shape_preview_erase = False

    def set_context(self, ctx: "AppContext") -> None:
        self._app_context = ctx
        self.frame_to_voxels()
        self.update()

    def reset_camera(self) -> None:
        self.yaw_deg = self._DEFAULT_YAW_DEG
        self.pitch_deg = self._DEFAULT_PITCH_DEG
        self.distance = self._DEFAULT_DISTANCE
        self.target = QVector3D(0.0, 0.0, 0.0)
        self.update()

    def set_view_preset(self, preset: str) -> None:
        preset_key = preset.strip().lower()
        if preset_key == "top":
            self.yaw_deg = 0.0
            self.pitch_deg = -89.0
        elif preset_key == "bottom":
            self.yaw_deg = 0.0
            self.pitch_deg = 89.0
        elif preset_key == "front":
            self.yaw_deg = 90.0
            self.pitch_deg = 0.0
        elif preset_key == "back":
            self.yaw_deg = -90.0
            self.pitch_deg = 0.0
        elif preset_key == "left":
            self.yaw_deg = 180.0
            self.pitch_deg = 0.0
        elif preset_key == "right":
            self.yaw_deg = 0.0
            self.pitch_deg = 0.0
        else:
            raise ValueError(f"Unsupported view preset: {preset}")
        self.update()

    def frame_to_voxels(self) -> None:
        if self._app_context is None:
            return

        voxel_points = self._visible_voxel_points()
        if not voxel_points:
            self.reset_camera()
            return

        xs = [point[0] for point in voxel_points]
        ys = [point[1] for point in voxel_points]
        zs = [point[2] for point in voxel_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)

        self.target = QVector3D(
            (min_x + max_x) * 0.5,
            (min_y + max_y) * 0.5,
            (min_z + max_z) * 0.5,
        )
        max_extent = max(max_x - min_x, max_y - min_y, max_z - min_z, 1)
        self.distance = self._clamp(max_extent * 2.5 + 2.0, 2.0, 200.0)
        self.update()

    def initializeGL(self) -> None:
        try:
            self._logger.info("initializeGL called.")
            funcs = self.context().functions()
            funcs.glClearColor(0.18, 0.22, 0.27, 1.0)
            funcs.glEnable(self._GL_DEPTH_TEST)

            vendor = self._gl_string(funcs, self._GL_VENDOR)
            renderer = self._gl_string(funcs, self._GL_RENDERER)
            version = self._gl_string(funcs, self._GL_VERSION)
            self.last_gl_info = f"{version} | {vendor} | {renderer}"

            program, shader_profile = self._create_shader_program()
            if program is None:
                raise RuntimeError("Viewport shader compilation/link failed. Check logs for details.")
            self._program = program
            self._shader_profile = shader_profile

            buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
            buffer.create()
            self._buffer = buffer

            vao = QOpenGLVertexArrayObject(self)
            vao.create()
            self._vao = vao
            self._init_error_text = None
            self._logged_pipeline_missing = False
            self._logger.info("Viewport GL pipeline initialized (shader=%s).", self._shader_profile)
            self.viewport_ready.emit(self.last_gl_info)
            self.viewport_diagnostics.emit(self._viewport_status_message(readiness="ready"))
        except Exception as exc:  # pragma: no cover
            self._init_error_text = str(exc)
            self.viewport_diagnostics.emit(self._viewport_status_message(readiness="unavailable"))
            self.viewport_error.emit(str(exc))
            self._logger.exception("OpenGL initialization failed")

    def paintGL(self) -> None:
        funcs = self.context().functions()
        funcs.glClear(self._GL_COLOR_BUFFER_BIT | self._GL_DEPTH_BUFFER_BIT)
        if self._app_context is None:
            return
        voxel_count = len(self._visible_voxel_points())
        if self._program is None or self._buffer is None or self._vao is None:
            if not self._logged_pipeline_missing:
                self._logger.error(
                    "Viewport render pipeline missing (program=%s buffer=%s vao=%s).",
                    self._program is not None,
                    self._buffer is not None,
                    self._vao is not None,
                )
                self._logged_pipeline_missing = True
            self._draw_overlay_text(
                voxel_count,
                error_text=self._init_error_text or "Viewport render pipeline unavailable. Check OpenGL status.",
            )
            return

        mvp = self._build_view_projection_matrix()
        self._draw_world_grid(funcs, mvp)
        self._draw_mirror_guides(funcs, mvp)
        if hasattr(funcs, "glPointSize"):
            funcs.glPointSize(8.0)
        point_vertices, line_vertices = self._build_visible_part_vertices()
        if point_vertices:
            funcs.glDisable(self._GL_DEPTH_TEST)
            self._draw_colored_vertices(funcs, line_vertices, self._GL_LINES, mvp)
            draw_count = self._draw_colored_vertices(funcs, point_vertices, self._GL_POINTS, mvp)
            funcs.glEnable(self._GL_DEPTH_TEST)
            if draw_count == 0:
                self._logger.warning("Voxel draw count was zero; rebuilding GL buffer.")
                self._buffer.destroy()
                self._buffer.create()
                self._draw_colored_vertices(funcs, line_vertices, self._GL_LINES, mvp)
                self._draw_colored_vertices(funcs, point_vertices, self._GL_POINTS, mvp)

        self._draw_hover_preview(funcs, mvp)
        self._draw_shape_preview(funcs, mvp)

        if self.debug_overlay_enabled:
            self._draw_overlay_text(voxel_count, error_text=None)

    def _draw_colored_vertices(self, funcs, vertex_data: array, mode: int, mvp: QMatrix4x4) -> int:
        if self._program is None or self._buffer is None or len(vertex_data) == 0:
            return 0

        if self._vao is not None:
            self._vao.bind()

        self._buffer.bind()
        self._buffer.allocate(vertex_data.tobytes(), len(vertex_data) * 4)
        funcs.glBindBuffer(self._GL_ARRAY_BUFFER, self._buffer.bufferId())

        self._program.bind()
        self._program.setUniformValue("u_mvp", mvp)

        stride = 6 * 4
        position_location = self._program.attributeLocation("position")
        color_location = self._program.attributeLocation("color")
        if position_location < 0 or color_location < 0:
            self._logger.error(
                "Shader attributes missing (position=%s color=%s, profile=%s).",
                position_location,
                color_location,
                self._shader_profile,
            )
            self._program.release()
            self._buffer.release()
            if self._vao is not None:
                self._vao.release()
            return 0
        self._program.enableAttributeArray(position_location)
        self._program.enableAttributeArray(color_location)
        self._program.setAttributeBuffer(position_location, self._GL_FLOAT, 0, 3, stride)
        self._program.setAttributeBuffer(color_location, self._GL_FLOAT, 3 * 4, 3, stride)
        count = len(vertex_data) // 6
        funcs.glDrawArrays(mode, 0, count)
        self._program.disableAttributeArray(position_location)
        self._program.disableAttributeArray(color_location)
        self._program.release()
        self._buffer.release()
        if self._vao is not None:
            self._vao.release()

        if hasattr(funcs, "glGetError"):
            gl_error = funcs.glGetError()
            if gl_error != self._GL_NO_ERROR:
                self._logger.error("OpenGL draw error: 0x%X", gl_error)
        return count

    def _draw_world_grid(self, funcs, mvp: QMatrix4x4) -> None:
        line_vertices = array("f")

        axis_len = 20.0
        line_vertices.extend((0.0, 0.0, 0.0, 1.0, 0.2, 0.2, axis_len, 0.0, 0.0, 1.0, 0.2, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 1.0, 0.2, 0.0, axis_len, 0.0, 0.2, 1.0, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 0.5, 1.0, 0.0, 0.0, axis_len, 0.2, 0.5, 1.0))

        if self._app_context is not None and not self._app_context.grid_visible:
            self._draw_colored_vertices(funcs, line_vertices, self._GL_LINES, mvp)
            return

        spacing = 1
        if self._app_context is not None:
            spacing = max(1, int(self._app_context.grid_spacing))
        grid_min = -20
        grid_max = 20
        for i in range(grid_min, grid_max + 1, spacing):
            shade = 0.45 if i == 0 else 0.30
            line_vertices.extend((float(i), 0.0, float(grid_min), shade, shade, shade))
            line_vertices.extend((float(i), 0.0, float(grid_max), shade, shade, shade))
            line_vertices.extend((float(grid_min), 0.0, float(i), shade, shade, shade))
            line_vertices.extend((float(grid_max), 0.0, float(i), shade, shade, shade))

        self._draw_colored_vertices(funcs, line_vertices, self._GL_LINES, mvp)

    def _draw_mirror_guides(self, funcs, mvp: QMatrix4x4) -> None:
        if self._app_context is None:
            return
        guide_extent = 20.0
        vertices = array("f")

        if self._app_context.mirror_x_enabled:
            color = (0.95, 0.35, 0.35)
            offset = float(self._app_context.mirror_x_offset)
            for i in range(-20, 21, 2):
                vertices.extend((offset, float(i), -guide_extent, color[0], color[1], color[2]))
                vertices.extend((offset, float(i), guide_extent, color[0], color[1], color[2]))
                vertices.extend((offset, -guide_extent, float(i), color[0], color[1], color[2]))
                vertices.extend((offset, guide_extent, float(i), color[0], color[1], color[2]))

        if self._app_context.mirror_y_enabled:
            color = (0.35, 0.95, 0.35)
            offset = float(self._app_context.mirror_y_offset)
            for i in range(-20, 21, 2):
                vertices.extend((float(i), offset, -guide_extent, color[0], color[1], color[2]))
                vertices.extend((float(i), offset, guide_extent, color[0], color[1], color[2]))
                vertices.extend((-guide_extent, offset, float(i), color[0], color[1], color[2]))
                vertices.extend((guide_extent, offset, float(i), color[0], color[1], color[2]))

        if self._app_context.mirror_z_enabled:
            color = (0.35, 0.6, 0.95)
            offset = float(self._app_context.mirror_z_offset)
            for i in range(-20, 21, 2):
                vertices.extend((float(i), -guide_extent, offset, color[0], color[1], color[2]))
                vertices.extend((float(i), guide_extent, offset, color[0], color[1], color[2]))
                vertices.extend((-guide_extent, float(i), offset, color[0], color[1], color[2]))
                vertices.extend((guide_extent, float(i), offset, color[0], color[1], color[2]))

        if vertices:
            self._draw_colored_vertices(funcs, vertices, self._GL_LINES, mvp)

    def _draw_overlay_text(self, voxel_count: int, error_text: str | None) -> None:
        painter = QPainter(self)
        painter.setPen(QColor(230, 230, 230))
        painter.drawText(12, 20, f"Voxels: {voxel_count}")
        painter.drawText(12, 38, f"Yaw: {self.yaw_deg:.1f}  Pitch: {self.pitch_deg:.1f}  Dist: {self.distance:.1f}")
        painter.drawText(
            12,
            56,
            f"Target: {self.target.x():.2f} {self.target.y():.2f} {self.target.z():.2f}",
        )
        if error_text:
            painter.setPen(QColor(255, 180, 90))
            painter.drawText(12, 74, error_text)
        painter.end()

    def _viewport_status_message(self, readiness: str) -> str:
        return f"Viewport: {readiness.upper()} | Shader: {self._shader_profile} | OpenGL: {self.last_gl_info}"

    def _draw_hover_preview(self, funcs, mvp: QMatrix4x4) -> None:
        if not self._hover_preview_cells or self._app_context is None:
            return
        if self._app_context.voxel_tool_shape != self._app_context.TOOL_SHAPE_BRUSH:
            return

        color = (1.0, 0.35, 0.35) if self._hover_preview_erase else (0.20, 1.0, 0.90)
        outline_vertices = array("f")
        for cell in sorted(self._hover_preview_cells):
            outline_vertices.extend(self._build_cell_outline_vertices(cell, color))
        self._draw_colored_vertices(funcs, outline_vertices, self._GL_LINES, mvp)

    def _draw_shape_preview(self, funcs, mvp: QMatrix4x4) -> None:
        if not self._shape_preview_cells:
            return
        color = (1.0, 0.45, 0.20) if self._shape_preview_erase else (0.25, 0.85, 1.0)
        outline_vertices = array("f")
        for cell in sorted(self._shape_preview_cells):
            outline_vertices.extend(self._build_cell_outline_vertices(cell, color))
        self._draw_colored_vertices(funcs, outline_vertices, self._GL_LINES, mvp)

    def _build_cell_outline_vertices(
        self,
        cell: tuple[int, int, int],
        color: tuple[float, float, float],
    ) -> array:
        x, y, z = cell
        half = self._VOXEL_HALF_EXTENT + 0.04
        edges = (
            ((-half, -half, -half), (half, -half, -half)),
            ((half, -half, -half), (half, half, -half)),
            ((half, half, -half), (-half, half, -half)),
            ((-half, half, -half), (-half, -half, -half)),
            ((-half, -half, half), (half, -half, half)),
            ((half, -half, half), (half, half, half)),
            ((half, half, half), (-half, half, half)),
            ((-half, half, half), (-half, -half, half)),
            ((-half, -half, -half), (-half, -half, half)),
            ((half, -half, -half), (half, -half, half)),
            ((half, half, -half), (half, half, half)),
            ((-half, half, -half), (-half, half, half)),
        )
        vertices = array("f")
        fx = float(x)
        fy = float(y)
        fz = float(z)
        for start, end in edges:
            vertices.extend(
                (
                    fx + start[0],
                    fy + start[1],
                    fz + start[2],
                    color[0],
                    color[1],
                    color[2],
                    fx + end[0],
                    fy + end[1],
                    fz + end[2],
                    color[0],
                    color[1],
                    color[2],
                )
            )
        return vertices

    def _create_shader_program(self) -> tuple[QOpenGLShaderProgram | None, str]:
        candidates = (
            (
                "glsl-330-core",
                """
                #version 330 core
                in vec3 position;
                in vec3 color;
                out vec3 v_color;
                uniform mat4 u_mvp;
                void main() {
                    v_color = color;
                    gl_Position = u_mvp * vec4(position, 1.0);
                    gl_PointSize = 12.0;
                }
                """,
                """
                #version 330 core
                in vec3 v_color;
                out vec4 frag_color;
                void main() {
                    frag_color = vec4(v_color, 1.0);
                }
                """,
            ),
            (
                "glsl-300-es",
                """
                #version 300 es
                precision highp float;
                in vec3 position;
                in vec3 color;
                out vec3 v_color;
                uniform mat4 u_mvp;
                void main() {
                    v_color = color;
                    gl_Position = u_mvp * vec4(position, 1.0);
                    gl_PointSize = 12.0;
                }
                """,
                """
                #version 300 es
                precision highp float;
                in vec3 v_color;
                out vec4 frag_color;
                void main() {
                    frag_color = vec4(v_color, 1.0);
                }
                """,
            ),
            (
                "glsl-120-compat",
                """
                #version 120
                attribute vec3 position;
                attribute vec3 color;
                varying vec3 v_color;
                uniform mat4 u_mvp;
                void main() {
                    v_color = color;
                    gl_Position = u_mvp * vec4(position, 1.0);
                    gl_PointSize = 12.0;
                }
                """,
                """
                #version 120
                varying vec3 v_color;
                void main() {
                    gl_FragColor = vec4(v_color, 1.0);
                }
                """,
            ),
        )
        errors: list[str] = []
        for profile, vertex_src, fragment_src in candidates:
            program = QOpenGLShaderProgram(self)
            vertex_ok = program.addShaderFromSourceCode(QOpenGLShader.Vertex, vertex_src)
            if not vertex_ok:
                errors.append(f"{profile} vertex compile failed: {program.log().strip()}")
                continue
            fragment_ok = program.addShaderFromSourceCode(QOpenGLShader.Fragment, fragment_src)
            if not fragment_ok:
                errors.append(f"{profile} fragment compile failed: {program.log().strip()}")
                continue
            link_ok = program.link()
            if link_ok:
                self._logger.info("Viewport shader profile selected: %s", profile)
                return program, profile
            errors.append(f"{profile} link failed: {program.log().strip()}")
        self._logger.error("Failed to compile/link viewport shaders: %s", " | ".join(errors))
        return None, "none"

    def _build_voxel_line_vertices(
        self,
        voxel_rows: list[list[int]],
        transform: QMatrix4x4 | None = None,
    ) -> array:
        half = self._VOXEL_HALF_EXTENT
        edges = (
            ((-half, -half, -half), (half, -half, -half)),
            ((half, -half, -half), (half, half, -half)),
            ((half, half, -half), (-half, half, -half)),
            ((-half, half, -half), (-half, -half, -half)),
            ((-half, -half, half), (half, -half, half)),
            ((half, -half, half), (half, half, half)),
            ((half, half, half), (-half, half, half)),
            ((-half, half, half), (-half, -half, half)),
            ((-half, -half, -half), (-half, -half, half)),
            ((half, -half, -half), (half, -half, half)),
            ((half, half, -half), (half, half, half)),
            ((-half, half, -half), (-half, half, half)),
        )
        vertices = array("f")
        for x, y, z, color_index in voxel_rows:
            color = self._PALETTE[color_index % len(self._PALETTE)]
            fx = float(x)
            fy = float(y)
            fz = float(z)
            for start, end in edges:
                sx = fx + start[0]
                sy = fy + start[1]
                sz = fz + start[2]
                ex = fx + end[0]
                ey = fy + end[1]
                ez = fz + end[2]
                if transform is not None:
                    start_vec = transform.map(QVector3D(sx, sy, sz))
                    end_vec = transform.map(QVector3D(ex, ey, ez))
                    sx, sy, sz = start_vec.x(), start_vec.y(), start_vec.z()
                    ex, ey, ez = end_vec.x(), end_vec.y(), end_vec.z()
                vertices.extend(
                    (
                        sx,
                        sy,
                        sz,
                        color[0],
                        color[1],
                        color[2],
                        ex,
                        ey,
                        ez,
                        color[0],
                        color[1],
                        color[2],
                    )
                )
        return vertices

    def mousePressEvent(self, event) -> None:
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            pos = event.position()
            self._last_mouse_pos = (pos.x(), pos.y())
        if event.button() == Qt.LeftButton:
            self._left_press_pos = event.position()
            self._left_dragging = False
            self._begin_brush_stroke_if_applicable(event.position(), event.modifiers())
            self._update_drag_preview(self._left_press_pos, self._left_press_pos, event.modifiers())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._last_mouse_pos is None:
            self._update_hover_preview(event.position(), event.modifiers())
            super().mouseMoveEvent(event)
            return
        pos = event.position()
        dx = pos.x() - self._last_mouse_pos[0]
        dy = pos.y() - self._last_mouse_pos[1]
        self._last_mouse_pos = (pos.x(), pos.y())

        if event.buttons() & Qt.LeftButton:
            if self._left_press_pos is not None and not self._left_dragging:
                press_dx = pos.x() - self._left_press_pos.x()
                press_dy = pos.y() - self._left_press_pos.y()
                if (press_dx * press_dx + press_dy * press_dy) >= 9.0:
                    self._left_dragging = True
            if self._left_dragging:
                if (
                    self._app_context is None
                    or self._app_context.voxel_tool_shape != self._app_context.TOOL_SHAPE_BRUSH
                ):
                    self.yaw_deg += dx * 0.4
                    self.pitch_deg = self._clamp(self.pitch_deg + dy * 0.4, -89.0, 89.0)
                    if (
                        self._app_context is not None
                        and self._app_context.camera_snap_enabled
                        and self._app_context.camera_snap_degrees > 0
                    ):
                        step = float(self._app_context.camera_snap_degrees)
                        self.yaw_deg = round(self.yaw_deg / step) * step
                        self.pitch_deg = round(self.pitch_deg / step) * step
                    self.update()
            if self._brush_stroke_active:
                self._continue_brush_stroke(pos, event.modifiers())
            elif self._left_press_pos is not None:
                self._update_drag_preview(self._left_press_pos, pos, event.modifiers())
        elif event.buttons() & Qt.RightButton:
            _, _, right, up = self._camera_vectors()
            pan_scale = self.distance * 0.0025
            offset = (right * (-dx * pan_scale)) + (up * (dy * pan_scale))
            self.target += offset
            self.update()

        self._update_hover_preview(pos, event.modifiers())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if self._brush_stroke_active:
                self._end_brush_stroke()
            elif (
                self._app_context is not None
                and self._app_context.voxel_tool_shape in (
                    self._app_context.TOOL_SHAPE_BOX,
                    self._app_context.TOOL_SHAPE_LINE,
                )
                and self._left_press_pos is not None
            ):
                if self._app_context.voxel_tool_shape == self._app_context.TOOL_SHAPE_BOX:
                    self._handle_box_drag(self._left_press_pos, event.position(), event.modifiers())
                else:
                    self._handle_line_drag(self._left_press_pos, event.position(), event.modifiers())
            elif (
                self._app_context is not None
                and self._app_context.voxel_tool_shape == self._app_context.TOOL_SHAPE_FILL
                and not self._left_dragging
            ):
                self._handle_fill_click(event.position(), event.modifiers())
            elif not self._left_dragging:
                self._handle_left_click(event.position(), event.modifiers())
            self._shape_preview_cells = set()
            self._left_press_pos = None
            self._left_dragging = False
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            self._last_mouse_pos = None
        self._update_hover_preview(event.position(), event.modifiers())
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event) -> None:
        steps = event.angleDelta().y() / 120.0
        if steps != 0:
            self.distance = self._clamp(self.distance * (0.9 ** steps), 2.0, 200.0)
            self.update()
        super().wheelEvent(event)

    def leaveEvent(self, event) -> None:
        if self._hover_preview_cells or self._shape_preview_cells:
            self._hover_preview_cells = set()
            self._hover_preview_source = None
            self._shape_preview_cells = set()
            self.update()
        super().leaveEvent(event)

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(max_value, value))

    def _camera_vectors(self) -> tuple[QVector3D, QVector3D, QVector3D, QVector3D]:
        yaw = radians(self.yaw_deg)
        pitch = radians(self.pitch_deg)
        eye = QVector3D(
            self.target.x() + self.distance * cos(pitch) * cos(yaw),
            self.target.y() + self.distance * sin(pitch),
            self.target.z() + self.distance * cos(pitch) * sin(yaw),
        )
        forward = (self.target - eye).normalized()
        world_up = QVector3D(0.0, 1.0, 0.0)
        right = QVector3D.crossProduct(forward, world_up).normalized()
        up = QVector3D.crossProduct(right, forward).normalized()
        return eye, forward, right, up

    def _build_view_projection_matrix(self) -> QMatrix4x4:
        width = max(1, self.width())
        height = max(1, self.height())
        mvp = QMatrix4x4()
        mvp.perspective(45.0, width / height, 0.1, 200.0)
        eye, _, _, _ = self._camera_vectors()
        mvp.lookAt(eye, self.target, QVector3D(0.0, 1.0, 0.0))
        return mvp

    def _handle_left_click(self, pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None or self._active_part_is_locked():
            return
        resolved = self._resolve_brush_target(pos, modifiers)
        if resolved is None:
            return
        (x, y, z), should_erase = resolved

        if should_erase:
            from core.commands.demo_commands import RemoveVoxelCommand

            self._app_context.command_stack.do(RemoveVoxelCommand(x, y, z), self._app_context)
            self.voxel_edit_applied.emit(f"Erase: ({x}, {y}, {z})")
        else:
            from core.commands.demo_commands import PaintVoxelCommand

            color_index = self._app_context.active_color_index
            self._app_context.command_stack.do(PaintVoxelCommand(x, y, z, color_index), self._app_context)
            self.voxel_edit_applied.emit(f"Paint: ({x}, {y}, {z}) color {color_index}")
        self.update()

    def _resolve_brush_target(
        self,
        pos: QPointF,
        modifiers: Qt.KeyboardModifier,
    ) -> tuple[tuple[int, int, int], bool] | None:
        if self._app_context is None:
            return None
        temporary_erase = bool(modifiers & Qt.ShiftModifier)
        mode = self._app_context.voxel_tool_mode
        should_erase = temporary_erase or mode == self._app_context.TOOL_MODE_ERASE
        allow_plane_fallback = (
            not should_erase and self._app_context.pick_mode == self._app_context.PICK_MODE_PLANE_LOCK
        )
        ray = self._screen_to_world_ray(pos.x(), pos.y())
        if ray is None:
            return None
        origin, direction = ray
        plane_cell = self._screen_to_plane_cell(pos) if allow_plane_fallback else None
        target = resolve_brush_target_cell(
            self._app_context.current_project.voxels,
            (origin.x(), origin.y(), origin.z()),
            (direction.x(), direction.y(), direction.z()),
            erase_mode=should_erase,
            plane_fallback_cell=plane_cell,
        )
        if target is None:
            return None
        return target[0], should_erase

    def _begin_brush_stroke_if_applicable(
        self,
        pos: QPointF,
        modifiers: Qt.KeyboardModifier,
    ) -> None:
        if self._app_context is None:
            return
        if self._app_context.voxel_tool_shape != self._app_context.TOOL_SHAPE_BRUSH:
            return
        if self._active_part_is_locked():
            return
        self._brush_stroke_active = True
        self._brush_stroke_last_cell = None
        self._app_context.command_stack.begin_transaction("Brush Stroke")
        self._continue_brush_stroke(pos, modifiers)

    def _continue_brush_stroke(self, pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None or not self._brush_stroke_active:
            return
        resolved = self._resolve_brush_target(pos, modifiers)
        if resolved is None:
            return
        current_cell, should_erase = resolved

        from core.commands.demo_commands import (
            PaintVoxelCommand,
            RemoveVoxelCommand,
            rasterize_brush_stroke_segment,
        )

        if self._brush_stroke_last_cell is None:
            segment_cells = [current_cell]
        else:
            segment_cells = rasterize_brush_stroke_segment(self._brush_stroke_last_cell, current_cell)

        for x, y, z in segment_cells:
            if should_erase:
                self._app_context.command_stack.do(RemoveVoxelCommand(x, y, z), self._app_context)
            else:
                self._app_context.command_stack.do(
                    PaintVoxelCommand(x, y, z, self._app_context.active_color_index),
                    self._app_context,
                )
        self._brush_stroke_last_cell = current_cell
        self.voxel_edit_applied.emit(f"Brush {'erase' if should_erase else 'paint'} stroke")
        self.update()

    def _end_brush_stroke(self) -> None:
        if self._app_context is None:
            return
        if not self._brush_stroke_active:
            return
        self._brush_stroke_active = False
        self._brush_stroke_last_cell = None
        self._app_context.command_stack.end_transaction()
        self.update()

    def _update_hover_preview(self, pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None:
            return
        shape = self._app_context.voxel_tool_shape
        if shape == self._app_context.TOOL_SHAPE_FILL:
            fill_cell = self._screen_to_plane_cell(pos)
            next_cells: set[tuple[int, int, int]] = {fill_cell} if fill_cell is not None else set()
            if fill_cell is not None:
                next_cells = self._app_context.expand_mirrored_cells(next_cells)
            temporary_erase = bool(modifiers & Qt.ShiftModifier)
            mode = self._app_context.voxel_tool_mode
            should_erase = temporary_erase or mode == self._app_context.TOOL_MODE_ERASE
            if next_cells != self._shape_preview_cells or should_erase != self._shape_preview_erase:
                self._shape_preview_cells = next_cells
                self._shape_preview_erase = should_erase
                self.update()
            if self._hover_preview_cells:
                self._hover_preview_cells = set()
                self._hover_preview_source = None
                self.update()
            return
        if shape != self._app_context.TOOL_SHAPE_BRUSH:
            if self._hover_preview_cells:
                self._hover_preview_cells = set()
                self._hover_preview_source = None
                self.update()
            return
        if self._shape_preview_cells:
            self._shape_preview_cells = set()
            self.update()

        ray = self._screen_to_world_ray(pos.x(), pos.y())
        if ray is None:
            return
        origin, direction = ray
        temporary_erase = bool(modifiers & Qt.ShiftModifier)
        mode = self._app_context.voxel_tool_mode
        should_erase = temporary_erase or mode == self._app_context.TOOL_MODE_ERASE
        allow_plane_fallback = (
            not should_erase and self._app_context.pick_mode == self._app_context.PICK_MODE_PLANE_LOCK
        )
        plane_cell = self._screen_to_plane_cell(pos) if allow_plane_fallback else None
        target = resolve_brush_target_cell(
            self._app_context.current_project.voxels,
            (origin.x(), origin.y(), origin.z()),
            (direction.x(), direction.y(), direction.z()),
            erase_mode=should_erase,
            plane_fallback_cell=plane_cell,
        )
        next_cell = target[0] if target is not None else None
        next_source = target[1] if target is not None else None
        next_cells: set[tuple[int, int, int]] = set()
        if next_cell is not None:
            next_cells = build_brush_cells(
                next_cell,
                brush_size=self._app_context.brush_size,
                brush_shape=self._app_context.brush_shape,
            )
        if (
            next_cells != self._hover_preview_cells
            or next_source != self._hover_preview_source
            or should_erase != self._hover_preview_erase
        ):
            self._hover_preview_cells = next_cells
            self._hover_preview_source = next_source
            self._hover_preview_erase = should_erase
            self.update()

    def _update_drag_preview(
        self,
        start_pos: QPointF,
        end_pos: QPointF,
        modifiers: Qt.KeyboardModifier,
    ) -> None:
        if self._app_context is None:
            return
        shape = self._app_context.voxel_tool_shape
        if shape not in (self._app_context.TOOL_SHAPE_BOX, self._app_context.TOOL_SHAPE_LINE):
            return
        start_cell = self._screen_to_plane_cell(start_pos)
        end_cell = self._screen_to_plane_cell(end_pos)
        if start_cell is None or end_cell is None:
            if self._shape_preview_cells:
                self._shape_preview_cells = set()
                self.update()
            return
        start_x, start_y, z = start_cell
        end_x, end_y, _ = end_cell
        if shape == self._app_context.TOOL_SHAPE_BOX:
            cells = build_box_plane_cells(start_x, start_y, end_x, end_y, z)
        else:
            cells = build_line_plane_cells(start_x, start_y, end_x, end_y, z)
        cells = self._app_context.expand_mirrored_cells(cells)
        temporary_erase = bool(modifiers & Qt.ShiftModifier)
        mode = self._app_context.voxel_tool_mode
        should_erase = temporary_erase or mode == self._app_context.TOOL_MODE_ERASE
        if cells != self._shape_preview_cells or should_erase != self._shape_preview_erase:
            self._shape_preview_cells = cells
            self._shape_preview_erase = should_erase
            self.update()

    def _handle_box_drag(self, start_pos: QPointF, end_pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None or self._active_part_is_locked():
            return
        start_cell = self._screen_to_plane_cell(start_pos)
        end_cell = self._screen_to_plane_cell(end_pos)
        if start_cell is None or end_cell is None:
            return

        start_x, start_y, z = start_cell
        end_x, end_y, _ = end_cell
        temporary_erase = modifiers & Qt.ShiftModifier
        mode = self._app_context.voxel_tool_mode
        command_mode = "erase" if temporary_erase or mode == self._app_context.TOOL_MODE_ERASE else "paint"

        from core.commands.demo_commands import BoxVoxelCommand

        color_index = self._app_context.active_color_index if command_mode == "paint" else None
        self._app_context.command_stack.do(
            BoxVoxelCommand(
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                z=z,
                mode=command_mode,
                color_index=color_index,
            ),
            self._app_context,
        )
        self.voxel_edit_applied.emit(f"Box {command_mode}: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        self.update()

    def _handle_line_drag(self, start_pos: QPointF, end_pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None or self._active_part_is_locked():
            return
        start_cell = self._screen_to_plane_cell(start_pos)
        end_cell = self._screen_to_plane_cell(end_pos)
        if start_cell is None or end_cell is None:
            return

        start_x, start_y, z = start_cell
        end_x, end_y, _ = end_cell
        temporary_erase = modifiers & Qt.ShiftModifier
        mode = self._app_context.voxel_tool_mode
        command_mode = "erase" if temporary_erase or mode == self._app_context.TOOL_MODE_ERASE else "paint"

        from core.commands.demo_commands import LineVoxelCommand

        color_index = self._app_context.active_color_index if command_mode == "paint" else None
        self._app_context.command_stack.do(
            LineVoxelCommand(
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                z=z,
                mode=command_mode,
                color_index=color_index,
            ),
            self._app_context,
        )
        self.voxel_edit_applied.emit(f"Line {command_mode}: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        self.update()

    def _handle_fill_click(self, pos: QPointF, modifiers: Qt.KeyboardModifier) -> None:
        if self._app_context is None or self._active_part_is_locked():
            return
        hit_cell = self._screen_to_plane_cell(pos)
        if hit_cell is None:
            return
        x, y, z = hit_cell
        temporary_erase = modifiers & Qt.ShiftModifier
        mode = self._app_context.voxel_tool_mode
        command_mode = "erase" if temporary_erase or mode == self._app_context.TOOL_MODE_ERASE else "paint"

        from core.commands.demo_commands import FillVoxelCommand

        color_index = self._app_context.active_color_index if command_mode == "paint" else None
        command = FillVoxelCommand(x=x, y=y, z=z, mode=command_mode, color_index=color_index)
        self._app_context.command_stack.do(
            command,
            self._app_context,
        )
        if command.aborted_by_threshold:
            self.voxel_edit_applied.emit(
                f"Fill blocked: region exceeded limit ({command.aborted_threshold_limit} cells)"
            )
            self.update()
            return
        self.voxel_edit_applied.emit(f"Fill {command_mode}: ({x}, {y}, {z})")
        self.update()

    def _screen_to_plane_cell(self, pos: QPointF) -> tuple[int, int, int] | None:
        ray = self._screen_to_world_ray(pos.x(), pos.y())
        if ray is None:
            return None
        origin, direction = ray
        if abs(direction.z()) < 1e-6:
            return None

        t = -origin.z() / direction.z()
        if t <= 0.0:
            return None

        hit = origin + (direction * t)
        return int(round(hit.x())), int(round(hit.y())), 0

    def _screen_to_world_ray(self, x: float, y: float) -> tuple[QVector3D, QVector3D] | None:
        width = max(1, self.width())
        height = max(1, self.height())
        ndc_x = (2.0 * x / width) - 1.0
        ndc_y = 1.0 - (2.0 * y / height)
        aspect = width / height
        tan_half_fov = 0.41421356237  # tan(45deg / 2)
        eye, forward, right, up = self._camera_vectors()
        direction = (
            forward + (right * (ndc_x * aspect * tan_half_fov)) + (up * (ndc_y * tan_half_fov))
        ).normalized()
        return eye, direction

    @staticmethod
    def _gl_string(funcs, token: int) -> str:
        value = funcs.glGetString(token)
        if isinstance(value, (bytes, bytearray)):
            return value.decode(errors="replace")
        return str(value) if value is not None else "unknown"

    def _visible_voxel_rows(self) -> list[list[int]]:
        if self._app_context is None:
            return []
        rows: list[list[int]] = []
        for part in self._app_context.current_project.scene.iter_visible_parts():
            rows.extend(part.voxels.to_list())
        return rows

    def _visible_voxel_points(self) -> list[tuple[float, float, float]]:
        if self._app_context is None:
            return []
        points: list[tuple[float, float, float]] = []
        for part in self._app_context.current_project.scene.iter_visible_parts():
            transform = self._part_transform_matrix(part)
            for x, y, z, _ in part.voxels.to_list():
                mapped = transform.map(QVector3D(float(x), float(y), float(z)))
                points.append((mapped.x(), mapped.y(), mapped.z()))
        return points

    def _build_visible_part_vertices(self) -> tuple[array, array]:
        point_vertices = array("f")
        line_vertices = array("f")
        if self._app_context is None:
            return point_vertices, line_vertices
        for part in self._app_context.current_project.scene.iter_visible_parts():
            transform = self._part_transform_matrix(part)
            part_rows = part.voxels.to_list()
            for x, y, z, color_index in part_rows:
                color = self._PALETTE[color_index % len(self._PALETTE)]
                mapped = transform.map(QVector3D(float(x), float(y), float(z)))
                point_vertices.extend((mapped.x(), mapped.y(), mapped.z(), color[0], color[1], color[2]))
            line_vertices.extend(self._build_voxel_line_vertices(part_rows, transform))
        return point_vertices, line_vertices

    @staticmethod
    def _part_transform_matrix(part) -> QMatrix4x4:
        matrix = QMatrix4x4()
        px, py, pz = part.position
        rx, ry, rz = part.rotation
        sx, sy, sz = part.scale
        matrix.translate(float(px), float(py), float(pz))
        matrix.rotate(float(rx), 1.0, 0.0, 0.0)
        matrix.rotate(float(ry), 0.0, 1.0, 0.0)
        matrix.rotate(float(rz), 0.0, 0.0, 1.0)
        matrix.scale(float(sx), float(sy), float(sz))
        return matrix

    def _active_part_is_locked(self) -> bool:
        if self._app_context is None:
            return False
        active_part = self._app_context.active_part
        if not active_part.locked:
            return False
        self.voxel_edit_applied.emit(f"Part locked: {active_part.name}")
        return True
