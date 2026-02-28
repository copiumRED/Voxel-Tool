from __future__ import annotations

from PySide6.QtOpenGLWidgets import QOpenGLWidget


class GLViewportWidget(QOpenGLWidget):
    _GL_COLOR_BUFFER_BIT = 0x00004000
    _GL_DEPTH_BUFFER_BIT = 0x00000100

    def initializeGL(self) -> None:
        funcs = self.context().functions()
        funcs.glClearColor(0.10, 0.12, 0.15, 1.0)

    def paintGL(self) -> None:
        funcs = self.context().functions()
        funcs.glClear(self._GL_COLOR_BUFFER_BIT | self._GL_DEPTH_BUFFER_BIT)
