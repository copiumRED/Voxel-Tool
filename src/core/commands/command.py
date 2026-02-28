from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def do(self, ctx) -> None:
        pass

    @abstractmethod
    def undo(self, ctx) -> None:
        pass
