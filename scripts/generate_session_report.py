#!/usr/bin/env python3
"""Generera rå sessionslogg och läsbar Markdown-rapport från simulatorn."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_simulator(root: Path):
    path = root / "scripts" / "simulate_game.py"
    spec = importlib.util.spec_from_file_location("expedition_session_simulator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Kunde inte ladda simulatorn: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SessionTraceMixin:
    """Spårning ovanpå simulatorn utan att ändra spelmotorns upplösningsordning."""

    def init_trace(self) -> None:
        rules = load_yaml(self.root / "data/rules.yaml")
        self.action_names = {
            "move": rules["actions"]["move"]["name"],
            "explore": rules["actions"]["explore"]["name"],
            "take_tool": rules["actions"]["gather"]["name"],
            "recover": rules["actions"]["rest"]["name"],
            "transfer": rules["actions"]["assist"]["name"],
            "use_equipment": rules["actions"]["use_item"]["name"],
            "unlock_road": rules["actions"]["unlock_road"]["name"],
            "pickup": rules["actions"]["pick_up_item"]["name"],
            "install_module": rules["actions"]["activate_objective"]["name"],
            "deposit_objective": "Lämna målobjekt",
        }
        self.trace: list[dict[str, Any]] = []
        self._buffer: list[dict[str, Any]] | None = None
        self._actor = None
        self._reason = ""
        self._logged_round = None
        self._location_names = {
            item["id"]: item.get("name", item["id"]) for item in self.board["locations"]
        }
        self._character_names = {
            item["id"]: item.get("name", item["id"])
            for item in self.character_data["characters"]
        }
        self._objective_names = {
            item["id"]: item.get("name", item["id"])
            for item in self.objective_data["objectives"]
        }
        self._equipment_names = {
            item["id"]: item.get("name", item["id"])
            for item in self.equipment_data["equipment"]
        }

    def cname(self, char) -> str:
        return self._character_names.get(char.id, char.id)

    def lname(self, location_id: str) -> str:
        return self._location_names.get(location_id, location_id)

    def oname(self, objective_id: str) -> str:
        return self._objective_names.get(objective_id, objective_id)

    def ename(self, equipment_id: str) -> str:
        return self._equipment_names.get(equipment_id, equipment_id)

    def emit(
        self,
        event_type: str,
        text: str,
        *,
        action_id: str | None = None,
        reason: str | None = None,
        possible_inefficiency: bool = False,
    ) -> None:
        event = {
            "round": self.round,
            "activation": self.activation_serial,
            "actor_id": self._actor.id if self._actor else None,
            "event_type": event_type,
            "action_id": action_id,
            "action_name": self.action_names.get(action_id) if action_id else None,
            "text": text,
            "reason": reason,
            "possible_inefficiency": possible_inefficiency,
        }
        if self._buffer is not None:
            self._buffer.append(event)
        else:
            self.trace.append(event)

    def explain_intention(self, char) -> str:
        if self.mission_type == "deliver_items" and char.objectives:
            return "Karaktären bär ett målobjekt och prioriterar återfärd till Baslägret."
        if (
            self.mission_type == "place_items_at_tagged_locations"
            and char.objectives
            and char.location in self.repair_sites
            and char.location not in self.repaired_sites
        ):
            return "Målobjektet är framme vid en oaktiverad målplats."
        if char.location in self.location_assignment and char.location not in self.revealed_locations:
            return "Platsen är okänd och utforskas för att hitta målobjekt eller scenarioplatser."
        if char.objectives:
            target = self.target_for(char)
            return f"Karaktären bär ett målobjekt och går mot {self.lname(target)}."
        target = self.nearest_unexplored(char)
        if target:
            return f"Strategin väljer närmaste okända plats: {self.lname(target)}."
        return "Karaktären söker den närmaste återstående uppgiften."

    def strategic_action(self, char):
        self._reason = self.explain_intention(char)
        return super().strategic_action(char)

    def activate(self, char) -> None:
        if not char.active or self.defeat():
            return
        if self._logged_round != self.round:
            if self._logged_round is not None:
                self.emit(
                    "upkeep",
                    f"Uthållighetsfasen har minskat uthålligheten till {self.endurance}.",
                )
            self._logged_round = self.round
            self.emit("round_start", f"Runda {self.round} börjar med {self.endurance} uthållighet.")
        self._actor = char
        self.emit(
            "activation_start",
            f"{self.cname(char)} börjar på {self.lname(char.location)} med "
            f"{char.tools} verktyg, {len(char.objectives)} målobjekt och "
            f"{char.health_remaining} hälsa.",
        )
        super().activate(char)
        self.emit(
            "activation_end",
            f"{self.cname(char)} avslutar på {self.lname(char.location)}. "
            f"Uthållighet: {self.endurance}.",
        )
        self._actor = None

    def move_action(self, char, target):
        before = char.location
        tools_before = char.tools
        endurance_before = self.endurance
        cost = super().move_action(char, target)
        if cost:
            if char.location != before:
                text = f"{self.cname(char)} flyttar {self.lname(before)} → {self.lname(char.location)}."
                inefficient = False
            else:
                text = (
                    f"{self.cname(char)} använder en handling mot {self.lname(target)}, "
                    "men byter inte plats."
                )
                inefficient = True
            details = []
            if char.tools < tools_before:
                details.append("ett verktyg används")
            if self.endurance < endurance_before:
                details.append(f"uthållighet −{endurance_before - self.endurance}")
            if details:
                text += " " + "; ".join(details) + "."
            self.emit(
                "action",
                text,
                action_id="move",
                reason=self._reason,
                possible_inefficiency=inefficient,
            )
        return cost

    def take_tool(self, char):
        result = super().take_tool(char)
        if result:
            self.emit(
                "action",
                f"{self.cname(char)} tar ett verktyg och har nu {char.tools}.",
                action_id="take_tool",
                reason=self._reason,
            )
        return result

    def draw_objective(self, char) -> None:
        objective_id = self.objective_deck[-1]["id"] if self.objective_deck else None
        parent_buffer = self._buffer
        children: list[dict[str, Any]] = []
        self._buffer = children
        super().draw_objective(char)
        self._buffer = parent_buffer
        if objective_id:
            where = "bärs direkt" if objective_id in char.objectives else "läggs på marken"
            self.emit(
                "card",
                f"Målobjektet **{self.oname(objective_id)}** dras och {where}.",
            )
        for child in children:
            if self._buffer is not None:
                self._buffer.append(child)
            else:
                self.trace.append(child)

    def draw_equipment(self, char) -> None:
        equipment_id = self.equipment_deck[-1]["id"] if self.equipment_deck else None
        super().draw_equipment(char)
        if equipment_id:
            where = "tas upp direkt" if equipment_id in char.equipment else "läggs på marken"
            self.emit("card", f"Utrustningen **{self.ename(equipment_id)}** dras och {where}.")

    def explore(self, char):
        if char.location not in self.location_assignment or char.location in self.revealed_locations:
            return False
        card = self.location_assignment[char.location]
        endurance_before = self.endurance
        damage_before = char.damage
        tools_before = char.tools
        found_before = self.objectives_found

        parent_buffer = self._buffer
        children: list[dict[str, Any]] = []
        self._buffer = children
        result = super().explore(char)
        self._buffer = parent_buffer

        if result:
            changes = []
            # Scenariohändelser kan ändra uthållighet under utforskningen. Beskriv därför
            # inte hela nettot som platskortets egen effekt när en underhändelse finns.
            child_endurance_delta = sum(
                int(event.get("endurance_delta", 0)) for event in children
            )
            own_endurance_after = self.endurance - child_endurance_delta
            if own_endurance_after != endurance_before:
                changes.append(f"uthållighet {endurance_before} → {own_endurance_after}")
            if char.damage != damage_before:
                changes.append(f"skada {damage_before} → {char.damage}")
            if char.tools != tools_before:
                changes.append(f"verktyg {tools_before} → {char.tools}")
            if self.objectives_found > found_before:
                changes.append("ett målobjekt hittas")
            effect_text = "; ".join(changes) if changes else "ingen omedelbar resursförändring"
            self.emit(
                "action",
                f"{self.cname(char)} utforskar {self.lname(char.location)} och vänder "
                f"**{card.get('name', card.get('id'))}**: {effect_text}.",
                action_id="explore",
                reason=self._reason,
            )
            for child in children:
                if self._buffer is not None:
                    self._buffer.append(child)
                else:
                    self.trace.append(child)
        return result

    def pickup_ground(self, char):
        objective_before = list(self.ground_objectives[char.location])
        equipment_before = list(self.ground_equipment[char.location])
        result = super().pickup_ground(char)
        if result:
            if len(self.ground_objectives[char.location]) < len(objective_before):
                text = (
                    f"{self.cname(char)} plockar upp målobjektet "
                    f"**{self.oname(objective_before[-1])}**."
                )
            elif len(self.ground_equipment[char.location]) < len(equipment_before):
                text = f"{self.cname(char)} plockar upp **{self.ename(equipment_before[-1])}**."
            else:
                text = f"{self.cname(char)} plockar upp ett verktyg."
            self.emit("action", text, action_id="pickup", reason=self._reason)
        return result

    def transfer_if_useful(self, char):
        before = len(self.transfer_log)
        result = super().transfer_if_useful(char)
        for entry in self.transfer_log[before:]:
            receiver = next(item for item in self.characters if item.id == entry["receiver"])
            if entry["kind"] == "objective":
                item_name = f"målobjektet **{self.oname(entry['item_id'])}**"
            elif entry["kind"] == "equipment":
                item_name = f"utrustningen **{self.ename(entry['item_id'])}**"
            else:
                item_name = "ett verktyg"
            self.emit(
                "action",
                f"{self.cname(char)} överför {item_name} till {self.cname(receiver)}.",
                action_id="transfer",
                reason=self._reason,
            )
        return result

    def install_module(self, char):
        before = set(self.repaired_sites)
        objective_id = char.objectives[-1] if char.objectives else None
        parent_buffer = self._buffer
        children: list[dict[str, Any]] = []
        self._buffer = children
        result = super().install_module(char)
        self._buffer = parent_buffer
        new_sites = self.repaired_sites - before
        if result is not None and new_sites:
            site = next(iter(new_sites))
            self.emit(
                "action",
                f"{self.cname(char)} aktiverar målobjektet **{self.oname(objective_id)}** "
                f"vid {self.lname(site)}. Progress: {len(self.repaired_sites)}/"
                f"{self.mission_completion['required']}.",
                action_id="install_module",
                reason=self._reason,
            )
        for child in children:
            if self._buffer is not None:
                self._buffer.append(child)
            else:
                self.trace.append(child)
        return result

    def deposit_objectives(self, char) -> None:
        delivered = list(char.objectives) if char.location == self.base else []
        before = len(self.objectives_at_base)
        parent_buffer = self._buffer
        children: list[dict[str, Any]] = []
        self._buffer = children
        super().deposit_objectives(char)
        self._buffer = parent_buffer
        if delivered and len(self.objectives_at_base) > before:
            names = ", ".join(f"**{self.oname(item)}**" for item in delivered)
            self.emit(
                "action",
                f"{self.cname(char)} lämnar målobjektet {names} i Baslägret. "
                f"Progress: {len(self.objectives_at_base)}/"
                f"{self.mission_completion['required']}.",
                action_id="deposit_objective",
                reason="Målobjektet har nått sin destination.",
            )
        for child in children:
            if self._buffer is not None:
                self._buffer.append(child)
            else:
                self.trace.append(child)

    def process_scenario_event_milestones(self, event, **kwargs):
        before = len(self.scenario_event_log)
        result = super().process_scenario_event_milestones(event, **kwargs)
        for entry in self.scenario_event_log[before:]:
            card = self.scenario_event_cards.get(entry["card_id"], {})
            name = card.get("name", entry["card_id"])
            delta = entry.get("endurance_delta", 0)
            if delta:
                effect = f"uthålligheten ändras med {delta:+d}"
            else:
                effect = "kartläget förändras"
            record = {
                "round": self.round,
                "activation": self.activation_serial,
                "actor_id": self._actor.id if self._actor else None,
                "event_type": "scenario_event",
                "action_id": None,
                "action_name": None,
                "text": f"Scenariohändelsen **{name}** löses ut: {effect}.",
                "reason": f"Utlöst av {event}.",
                "possible_inefficiency": False,
                "endurance_delta": delta,
            }
            if self._buffer is not None:
                self._buffer.append(record)
            else:
                self.trace.append(record)
        return result


def build_trace_class(module):
    return type(
        "SessionTraceSimulation",
        (SessionTraceMixin, module.ExpeditionSimulation),
        {"__init__": lambda self, *a, **kw: (
            module.ExpeditionSimulation.__init__(self, *a, **kw),
            self.init_trace(),
        )[-1]},
    )


def render_markdown(game, result, strategy_name: str) -> str:
    lines = [
        f"# Vinnande spelsession – {game.scenario['name']}",
        "",
        "> Detta är en deterministisk simulatorkörning. Tankarna är agentens "
        "beslutsmotiveringar, inte en riktig spelares ord.",
        "",
        "## Testdata",
        "",
        f"- Scenario: **{game.scenario['name']}**",
        f"- Karaktärer: **{', '.join(game.cname(c) for c in game.characters)}**",
        f"- Strategi: **{strategy_name}**",
        f"- Seed: **{game.seed}**",
        f"- Startuthållighet: **{result.starting_endurance}**",
        f"- Resultat: **{'Vinst' if result.result == 'win' else 'Förlust'} i runda {result.rounds}**",
        f"- Uthållighet vid slut: **{max(0, result.final_endurance)}**",
        "",
        "## Spelsession, drag för drag",
        "",
    ]
    current_round = None
    for event in game.trace:
        if event["round"] != current_round:
            current_round = event["round"]
            lines += [f"## Runda {current_round}", ""]
        event_type = event["event_type"]
        if event_type == "round_start":
            lines.append(f"**Rundstart:** {event['text']}")
        elif event_type == "upkeep":
            lines.append(f"**Uthållighetsfas:** {event['text']}")
        elif event_type == "activation_start":
            lines += ["", f"### {event['text'].split(' börjar')[0]}", "", event["text"]]
        elif event_type == "activation_end":
            lines.append(f"**Aktiveringen slutar:** {event['text']}")
        elif event_type == "action":
            label = event["action_name"] or "Handling"
            lines.append(f"- **{label}:** {event['text']}")
            if event.get("reason"):
                lines.append(f"  - *Agentens tanke:* {event['reason']}")
            if event.get("possible_inefficiency"):
                lines.append("  - **Möjlig agentineffektivitet:** handlingen gav inget platsbyte.")
        elif event_type == "card":
            lines.append(f"- **Kort:** {event['text']}")
        elif event_type == "scenario_event":
            lines.append(f"- **Scenariohändelse:** {event['text']}")
    lines += [
        "",
        "## Teknisk notering",
        "",
        "Den läsbara rapporten presenterar övergripande handling före kort och "
        "scenariohändelser som handlingen utlöser. Råloggen sparar samma "
        "händelser med tekniska id:n och visningsnamn.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--characters", type=int, default=2)
    parser.add_argument("--strategy", default="nearest_unknown")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    module = load_simulator(root)
    config = load_yaml(root / "data/simulation.yaml")
    strategy = next(item for item in config["strategies"] if item["id"] == args.strategy)
    trace_class = build_trace_class(module)
    game = trace_class(root, strategy, args.seed, args.scenario, args.characters)
    result = game.run()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.output_dir / "session-raw.json"
    report_path = args.output_dir / "session-report.md"
    raw_path.write_text(
        json.dumps(
            {
                "scenario": args.scenario,
                "characters": args.characters,
                "strategy": args.strategy,
                "seed": args.seed,
                "result": result.result,
                "events": game.trace,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_markdown(game, result, strategy["name"]), encoding="utf-8")
    print(report_path)
    print(raw_path)


if __name__ == "__main__":
    main()
