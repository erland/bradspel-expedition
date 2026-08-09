"""Gemensam spelmotor för Expedition.

Modulen kapslar den befintliga regelimplementeringen och ger alla agenter samma
spelplan, kortlekar, setup, handlingsekonomi och vinst-/förlustkontroller.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_rules_module(root: Path):
    path = root / "scripts/simulate_game.py"
    name = "_expedition_rules_runtime"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Kunde inte ladda regelmotorn.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class GameEngine:
    """Startar och kör ett spel med en valfri agentprofil."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.rules = _load_rules_module(self.root)

    def create_game(
        self,
        agent: Any,
        seed: int,
        characters: int = 2,
        scenario_id: str | None = None,
    ):
        """Skapa ett spelobjekt utan att köra det.

        Används av tester, framtida UI och scenarioevents som behöver läsa eller
        ändra runtime-state innan hela spelet körs.
        """
        strategy = agent.strategy_config()
        return self.rules.ExpeditionSimulation(
            self.root,
            strategy,
            seed,
            scenario_id=scenario_id,
            characters_per_game=characters,
        )

    def run_game(
        self,
        agent: Any,
        seed: int,
        characters: int = 2,
        scenario_id: str | None = None,
    ):
        return self.create_game(
            agent,
            seed,
            characters=characters,
            scenario_id=scenario_id,
        ).run()
