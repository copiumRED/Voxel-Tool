from __future__ import annotations

from array import array
from ctypes import c_void_p
from typing import TYPE_CHECKING

from PySide6.QtGui import QMatrix4x4, QVector3D
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShader, QOpenGLShaderProgram
from PySide6.QtOpenGLWidgets import QOpenGLWidget

if TYPE_CHECKING:
    from app.app_context import AppContext


class GLViewportWidget(QOpenGLWidget):
    _GL_COLOR_BUFFER_BIT = 0x00004000
    _GL_DEPTH_BUFFER_BIT = 0x00000100
    _GL_POINTS = 0x0000
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

    def set_context(self, ctx: "AppContext") -> None:
        self._app_context = ctx
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

        voxel_rows = self._app_context.current_project.voxels.to_list()
        if not voxel_rows:
            return

        vertex_data = array("f")
        for x, y, z, color_index in voxel_rows:
            color = self._PALETTE[color_index % len(self._PALETTE)]
            vertex_data.extend((float(x), float(y), float(z), color[0], color[1], color[2]))

        self._buffer.bind()
        self._buffer.allocate(vertex_data.tobytes(), len(vertex_data) * 4)
        funcs.glBindBuffer(self._GL_ARRAY_BUFFER, self._buffer.bufferId())

        width = max(1, self.width())
        height = max(1, self.height())
        mvp = QMatrix4x4()
        mvp.perspective(45.0, width / height, 0.1, 200.0)
        mvp.lookAt(QVector3D(14.0, 14.0, 14.0), QVector3D(0.0, 0.0, 0.0), QVector3D(0.0, 1.0, 0.0))

        self._program.bind()
        self._program.setUniformValue("u_mvp", mvp)

        stride = 6 * 4
        position_location = self._program.attributeLocation("position")
        color_location = self._program.attributeLocation("color")
        self._program.enableAttributeArray(position_location)
        self._program.enableAttributeArray(color_location)
        funcs.glVertexAttribPointer(position_location, 3, self._GL_FLOAT, False, stride, c_void_p(0))
        funcs.glVertexAttribPointer(color_location, 3, self._GL_FLOAT, False, stride, c_void_p(3 * 4))
        funcs.glDrawArrays(self._GL_POINTS, 0, len(voxel_rows))
        self._program.disableAttributeArray(position_location)
        self._program.disableAttributeArray(color_location)
        self._program.release()
        self._buffer.release()
