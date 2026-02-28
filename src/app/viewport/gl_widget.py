from __future__ import annotations

import logging
from array import array
from ctypes import c_void_p
from math import cos, radians, sin
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMatrix4x4, QPainter, QVector3D
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram
from PySide6.QtOpenGLWidgets import QOpenGLWidget

if TYPE_CHECKING:
    from app.app_context import AppContext


class GLViewportWidget(QOpenGLWidget):
    voxel_edit_applied = Signal(str)
    viewport_ready = Signal(str)
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
        self._logger = logging.getLogger("voxel_tool")
        self.last_gl_info = "unknown"
        self.debug_overlay_enabled = True
        self.yaw_deg = self._DEFAULT_YAW_DEG
        self.pitch_deg = self._DEFAULT_PITCH_DEG
        self.distance = self._DEFAULT_DISTANCE
        self.target = QVector3D(0.0, 0.0, 0.0)
        self._last_mouse_pos: tuple[float, float] | None = None
        self._left_press_pos: QPointF | None = None
        self._left_dragging = False

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

    def frame_to_voxels(self) -> None:
        if self._app_context is None:
            return

        voxel_rows = self._app_context.current_project.voxels.to_list()
        if not voxel_rows:
            self.reset_camera()
            return

        xs = [row[0] for row in voxel_rows]
        ys = [row[1] for row in voxel_rows]
        zs = [row[2] for row in voxel_rows]
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
            funcs = self.context().functions()
            funcs.glClearColor(0.18, 0.22, 0.27, 1.0)
            funcs.glEnable(self._GL_DEPTH_TEST)

            vendor = self._gl_string(funcs, self._GL_VENDOR)
            renderer = self._gl_string(funcs, self._GL_RENDERER)
            version = self._gl_string(funcs, self._GL_VERSION)
            self.last_gl_info = f"{version} | {vendor} | {renderer}"
            self.viewport_ready.emit(self.last_gl_info)

            program = QOpenGLShaderProgram(self)
            program.addShaderFromSourceCode(
                QOpenGLShader.Vertex,
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
            )
            program.addShaderFromSourceCode(
                QOpenGLShader.Fragment,
                """
                #version 120
                varying vec3 v_color;
                void main() {
                    gl_FragColor = vec4(v_color, 1.0);
                }
                """,
            )
            program.link()
            self._program = program

            buffer = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
            buffer.create()
            self._buffer = buffer
        except Exception as exc:  # pragma: no cover
            self.viewport_error.emit(str(exc))
            self._logger.exception("OpenGL initialization failed")

    def paintGL(self) -> None:
        funcs = self.context().functions()
        funcs.glClear(self._GL_COLOR_BUFFER_BIT | self._GL_DEPTH_BUFFER_BIT)
        if self._app_context is None or self._program is None or self._buffer is None:
            return

        mvp = self._build_view_projection_matrix()
        voxel_rows = self._app_context.current_project.voxels.to_list()
        if hasattr(funcs, "glPointSize"):
            funcs.glPointSize(8.0)
        if voxel_rows:
            funcs.glDisable(self._GL_DEPTH_TEST)
            voxel_point_vertices = array("f")
            for x, y, z, color_index in voxel_rows:
                color = self._PALETTE[color_index % len(self._PALETTE)]
                voxel_point_vertices.extend((float(x), float(y), float(z), color[0], color[1], color[2]))

            voxel_line_vertices = self._build_voxel_line_vertices(voxel_rows)
            self._draw_colored_vertices(funcs, voxel_line_vertices, self._GL_LINES, mvp)
            draw_count = self._draw_colored_vertices(funcs, voxel_point_vertices, self._GL_POINTS, mvp)
            funcs.glEnable(self._GL_DEPTH_TEST)
            if draw_count == 0:
                self._logger.warning("Voxel draw count was zero; rebuilding GL buffer.")
                self._buffer.destroy()
                self._buffer.create()
                self._draw_colored_vertices(funcs, voxel_line_vertices, self._GL_LINES, mvp)
                self._draw_colored_vertices(funcs, voxel_point_vertices, self._GL_POINTS, mvp)

        if self.debug_overlay_enabled:
            self._draw_debug_overlay(funcs, mvp, len(voxel_rows))

    def _draw_colored_vertices(self, funcs, vertex_data: array, mode: int, mvp: QMatrix4x4) -> int:
        if self._program is None or self._buffer is None or len(vertex_data) == 0:
            return 0

        self._buffer.bind()
        self._buffer.allocate(vertex_data.tobytes(), len(vertex_data) * 4)
        funcs.glBindBuffer(self._GL_ARRAY_BUFFER, self._buffer.bufferId())

        self._program.bind()
        self._program.setUniformValue("u_mvp", mvp)

        stride = 6 * 4
        position_location = self._program.attributeLocation("position")
        color_location = self._program.attributeLocation("color")
        self._program.enableAttributeArray(position_location)
        self._program.enableAttributeArray(color_location)
        funcs.glVertexAttribPointer(position_location, 3, self._GL_FLOAT, False, stride, c_void_p(0))
        funcs.glVertexAttribPointer(color_location, 3, self._GL_FLOAT, False, stride, c_void_p(3 * 4))
        count = len(vertex_data) // 6
        funcs.glDrawArrays(mode, 0, count)
        self._program.disableAttributeArray(position_location)
        self._program.disableAttributeArray(color_location)
        self._program.release()
        self._buffer.release()
        return count

    def _draw_debug_overlay(self, funcs, mvp: QMatrix4x4, voxel_count: int) -> None:
        line_vertices = array("f")

        axis_len = 20.0
        line_vertices.extend((0.0, 0.0, 0.0, 1.0, 0.2, 0.2, axis_len, 0.0, 0.0, 1.0, 0.2, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 1.0, 0.2, 0.0, axis_len, 0.0, 0.2, 1.0, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 0.5, 1.0, 0.0, 0.0, axis_len, 0.2, 0.5, 1.0))

        grid_min = -20
        grid_max = 20
        for i in range(grid_min, grid_max + 1):
            shade = 0.45 if i == 0 else 0.30
            line_vertices.extend((float(i), 0.0, float(grid_min), shade, shade, shade))
            line_vertices.extend((float(i), 0.0, float(grid_max), shade, shade, shade))
            line_vertices.extend((float(grid_min), 0.0, float(i), shade, shade, shade))
            line_vertices.extend((float(grid_max), 0.0, float(i), shade, shade, shade))

        self._draw_colored_vertices(funcs, line_vertices, self._GL_LINES, mvp)

        painter = QPainter(self)
        painter.setPen(QColor(230, 230, 230))
        painter.drawText(12, 20, f"Voxels: {voxel_count}")
        painter.drawText(12, 38, f"Yaw: {self.yaw_deg:.1f}  Pitch: {self.pitch_deg:.1f}  Dist: {self.distance:.1f}")
        painter.drawText(
            12,
            56,
            f"Target: {self.target.x():.2f} {self.target.y():.2f} {self.target.z():.2f}",
        )
        painter.end()

    def _build_voxel_line_vertices(self, voxel_rows: list[list[int]]) -> array:
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

    def mousePressEvent(self, event) -> None:
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            pos = event.position()
            self._last_mouse_pos = (pos.x(), pos.y())
        if event.button() == Qt.LeftButton:
            self._left_press_pos = event.position()
            self._left_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._last_mouse_pos is None:
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
                self.yaw_deg += dx * 0.4
                self.pitch_deg = self._clamp(self.pitch_deg + dy * 0.4, -89.0, 89.0)
                self.update()
        elif event.buttons() & Qt.RightButton:
            _, _, right, up = self._camera_vectors()
            pan_scale = self.distance * 0.0025
            offset = (right * (-dx * pan_scale)) + (up * (dy * pan_scale))
            self.target += offset
            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if not self._left_dragging:
                self._handle_left_click(event.position(), event.modifiers())
            self._left_press_pos = None
            self._left_dragging = False
        if event.button() in (Qt.LeftButton, Qt.RightButton):
            self._last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event) -> None:
        steps = event.angleDelta().y() / 120.0
        if steps != 0:
            self.distance = self._clamp(self.distance * (0.9 ** steps), 2.0, 200.0)
            self.update()
        super().wheelEvent(event)

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
        if self._app_context is None:
            return
        ray = self._screen_to_world_ray(pos.x(), pos.y())
        if ray is None:
            return
        origin, direction = ray
        if abs(direction.z()) < 1e-6:
            return

        t = -origin.z() / direction.z()
        if t <= 0.0:
            return

        hit = origin + (direction * t)
        x = int(round(hit.x()))
        y = int(round(hit.y()))
        z = 0
        temporary_erase = modifiers & Qt.ShiftModifier
        mode = self._app_context.voxel_tool_mode
        should_erase = temporary_erase or mode == self._app_context.TOOL_MODE_ERASE

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
