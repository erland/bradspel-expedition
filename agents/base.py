"""Agentgränssnitt."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Agent(ABC):
    id: str
    name: str

    @abstractmethod
    def strategy_config(self) -> dict:
        """Returnera beslutsprofilen som spelmotorn använder."""
        raise NotImplementedError
