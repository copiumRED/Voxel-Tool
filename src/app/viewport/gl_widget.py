from __future__ import annotations

from array import array
from ctypes import c_void_p
from math import cos, radians, sin
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QMatrix4x4, QPainter, QVector3D
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram
from PySide6.QtOpenGLWidgets import QOpenGLWidget

if TYPE_CHECKING:
    from app.app_context import AppContext


class GLViewportWidget(QOpenGLWidget):
    _GL_COLOR_BUFFER_BIT = 0x00004000
    _GL_DEPTH_BUFFER_BIT = 0x00000100
    _GL_POINTS = 0x0000
    _GL_LINES = 0x0001
    _GL_FLOAT = 0x1406
    _GL_DEPTH_TEST = 0x0B71
    _GL_ARRAY_BUFFER = 0x8892

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
        self._app_context: AppContext | None = None
        self._program: QOpenGLShaderProgram | None = None
        self._buffer: QOpenGLBuffer | None = None
        self.debug_overlay_enabled = True
        self.yaw_deg = 45.0
        self.pitch_deg = -30.0
        self.distance = 25.0
        self.target = QVector3D(0.0, 0.0, 0.0)
        self._last_mouse_pos: tuple[float, float] | None = None

    def set_context(self, ctx: "AppContext") -> None:
        self._app_context = ctx
        self.frame_to_voxels()
        self.update()

    def frame_to_voxels(self) -> None:
        if self._app_context is None:
            return

        voxel_rows = self._app_context.current_project.voxels.to_list()
        if not voxel_rows:
            self.yaw_deg = 45.0
            self.pitch_deg = -30.0
            self.distance = 25.0
            self.target = QVector3D(0.0, 0.0, 0.0)
            self.update()
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
        funcs = self.context().functions()
        funcs.glClearColor(0.10, 0.12, 0.15, 1.0)
        funcs.glEnable(self._GL_DEPTH_TEST)

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
                gl_PointSize = 8.0;
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

    def paintGL(self) -> None:
        funcs = self.context().functions()
        funcs.glClear(self._GL_COLOR_BUFFER_BIT | self._GL_DEPTH_BUFFER_BIT)
        if self._app_context is None or self._program is None or self._buffer is None:
            return

        width = max(1, self.width())
        height = max(1, self.height())
        mvp = QMatrix4x4()
        mvp.perspective(45.0, width / height, 0.1, 200.0)
        yaw = radians(self.yaw_deg)
        pitch = radians(self.pitch_deg)
        eye = QVector3D(
            self.target.x() + self.distance * cos(pitch) * cos(yaw),
            self.target.y() + self.distance * sin(pitch),
            self.target.z() + self.distance * cos(pitch) * sin(yaw),
        )
        mvp.lookAt(eye, self.target, QVector3D(0.0, 1.0, 0.0))

        voxel_rows = self._app_context.current_project.voxels.to_list()
        if voxel_rows:
            voxel_vertices = array("f")
            for x, y, z, color_index in voxel_rows:
                color = self._PALETTE[color_index % len(self._PALETTE)]
                voxel_vertices.extend((float(x), float(y), float(z), color[0], color[1], color[2]))
            self._draw_colored_vertices(funcs, voxel_vertices, self._GL_POINTS, mvp)

        if self.debug_overlay_enabled:
            self._draw_debug_overlay(funcs, mvp, len(voxel_rows))

    def _draw_colored_vertices(self, funcs, vertex_data: array, mode: int, mvp: QMatrix4x4) -> None:
        if self._program is None or self._buffer is None or len(vertex_data) == 0:
            return

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
        funcs.glDrawArrays(mode, 0, len(vertex_data) // 6)
        self._program.disableAttributeArray(position_location)
        self._program.disableAttributeArray(color_location)
        self._program.release()
        self._buffer.release()

    def _draw_debug_overlay(self, funcs, mvp: QMatrix4x4, voxel_count: int) -> None:
        line_vertices = array("f")

        # Axes
        axis_len = 6.0
        line_vertices.extend((0.0, 0.0, 0.0, 1.0, 0.2, 0.2, axis_len, 0.0, 0.0, 1.0, 0.2, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 1.0, 0.2, 0.0, axis_len, 0.0, 0.2, 1.0, 0.2))
        line_vertices.extend((0.0, 0.0, 0.0, 0.2, 0.5, 1.0, 0.0, 0.0, axis_len, 0.2, 0.5, 1.0))

        # Ground grid on XZ plane
        grid_min = -10
        grid_max = 10
        for i in range(grid_min, grid_max + 1):
            shade = 0.35 if i == 0 else 0.22
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

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            pos = event.position()
            self._last_mouse_pos = (pos.x(), pos.y())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._last_mouse_pos is None or not (event.buttons() & Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
        pos = event.position()
        dx = pos.x() - self._last_mouse_pos[0]
        dy = pos.y() - self._last_mouse_pos[1]
        self._last_mouse_pos = (pos.x(), pos.y())

        self.yaw_deg += dx * 0.4
        self.pitch_deg = self._clamp(self.pitch_deg + dy * 0.4, -89.0, 89.0)
        self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
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
