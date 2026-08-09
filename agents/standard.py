"""Standardagenter med olika spelstilar."""

from __future__ import annotations

from dataclasses import dataclass

from agents.base import Agent


@dataclass
class ConfiguredAgent(Agent):
    id: str
    name: str
    character_priority: list[str]
    parameters: dict

    def strategy_config(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "character_priority": list(self.character_priority),
            "parameters": dict(self.parameters),
        }


def build_agents() -> list[ConfiguredAgent]:
    return [
        ConfiguredAgent(
            "random_agent",
            "Slumpagent",
            [],
            {
                "random_action_probability": 1.0,
                "use_hidden_shortcuts": True,
                "collect_tools_target": 1,
                "heal_at_health": 1,
                "prioritize_objectives": False,
                "return_when_all_objectives_found": True,
            },
        ),
        ConfiguredAgent(
            "explorer_agent",
            "Utforskaragent",
            ["scout", "carrier", "engineer", "medic"],
            {
                "random_action_probability": 0.02,
                "use_hidden_shortcuts": False,
                "collect_tools_target": 1,
                "heal_at_health": 1,
                "prioritize_objectives": True,
                "return_when_all_objectives_found": True,
            },
        ),
        ConfiguredAgent(
            "adaptive_agent",
            "Adaptiv genvägsagent",
            ["scout", "engineer", "carrier", "medic"],
            {
                "random_action_probability": 0.01,
                "use_hidden_shortcuts": False,
                "adaptive_hidden_shortcuts": True,
                "hidden_shortcut_min_savings": 2,
                "hidden_shortcut_risk_penalty": 0,
                "collect_tools_target": 1,
                "heal_at_health": 1,
                "prioritize_objectives": True,
                "return_when_all_objectives_found": True,
            },
        ),
        ConfiguredAgent(
            "risk_agent",
            "Riskagent",
            ["scout", "engineer", "climber", "carrier"],
            {
                "random_action_probability": 0.02,
                "use_hidden_shortcuts": True,
                "collect_tools_target": 1,
                "heal_at_health": 1,
                "prioritize_objectives": True,
                "return_when_all_objectives_found": True,
            },
        ),
        ConfiguredAgent(
            "cautious_agent",
            "Försiktig agent",
            ["medic", "veteran", "carrier", "engineer"],
            {
                "random_action_probability": 0.01,
                "use_hidden_shortcuts": False,
                "collect_tools_target": 1,
                "heal_at_health": 2,
                "prioritize_objectives": True,
                "return_when_all_objectives_found": True,
            },
        ),
        ConfiguredAgent(
            "logistics_agent",
            "Logistikagent",
            ["carrier", "courier", "engineer", "medic"],
            {
                "random_action_probability": 0.01,
                "use_hidden_shortcuts": True,
                "collect_tools_target": 1,
                "heal_at_health": 1,
                "prioritize_objectives": True,
                "return_when_all_objectives_found": True,
                "prefer_capacity_equipment": True,
                "transfer_objectives_to_capacity": True,
            },
        ),
    ]
