#!/usr/bin/env python3
"""Kontrollerad samarbets-ablationsstudie för Expedition."""

import argparse
import csv
import importlib.util
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import yaml


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_simulator(root):
    path = root / "scripts/simulate_game.py"
    name = "_expedition_simulator_for_ablation"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Kunde inte ladda designsimulatorn.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def shortest_open_distance(sim, start, target, char):
    if start == target:
        return 0
    path = sim.shortest_path(start, {target}, False, char)
    return len(path) if path else 999


class CooperativeSimulationMixin:
    cooperation_mode = None

    def initialize_cooperation(self, mode):
        self.cooperation_mode = mode
        self.assigned_targets = {}
        self.round_reserved_targets = set()
        self.coop_metrics = Counter()

    def coordinated_target(self, char):
        candidates = set(self.scenario["setup"]["location_slots"]) - self.revealed_locations
        if not candidates:
            return None

        current = self.assigned_targets.get(char.id)
        if current in candidates:
            return current

        ranked = []
        allow_hidden = bool(self.params.get("use_hidden_shortcuts", False))
        for target in candidates:
            path = self.shortest_path(char.location, {target}, allow_hidden, char)
            if not path and target != char.location:
                path = self.shortest_path(char.location, {target}, False, char)
            if path or target == char.location:
                ranked.append((len(path), target))
        if not ranked:
            return None
        ranked.sort()

        if self.cooperation_mode["coordinate_destinations"]:
            for _, target in ranked:
                if target not in self.round_reserved_targets:
                    self.assigned_targets[char.id] = target
                    self.round_reserved_targets.add(target)
                    self.coop_metrics["coordinated_assignments"] += 1
                    return target

        target = ranked[0][1]
        if target in self.round_reserved_targets:
            self.coop_metrics["duplicate_destinations"] += 1
        self.round_reserved_targets.add(target)
        self.assigned_targets[char.id] = target
        return target

    def target_for(self, char):
        if char.objectives:
            return self.base

        ground_targets = {
            location for location, cards in self.ground_objectives.items() if cards
        }
        if self.objectives_found >= self.objective_data["deck"]["required_for_victory"]:
            if ground_targets:
                ranked = []
                for loc in ground_targets:
                    path = self.shortest_path(
                        char.location,
                        {loc},
                        bool(self.params.get("use_hidden_shortcuts", False)),
                        char,
                    )
                    if path or loc == char.location:
                        ranked.append((len(path), loc))
                if ranked:
                    ranked.sort()
                    return ranked[0][1]
            return self.base

        target = self.coordinated_target(char)
        return target or self.base

    def transfer_if_useful(self, char):
        if not self.cooperation_mode["allow_transfers"]:
            return False

        others = [
            other for other in self.characters
            if other is not char and other.active and other.location == char.location
        ]
        if not others or not char.objectives:
            return False

        giver_distance = shortest_open_distance(self, char.location, self.base, char)
        candidates = []
        for other in others:
            if self.free_capacity(other) < 2:
                continue
            receiver_distance = shortest_open_distance(self, other.location, self.base, other)
            capacity_gain = self.free_capacity(other) - self.free_capacity(char)
            score = capacity_gain + (giver_distance - receiver_distance)
            if other.id == "carrier":
                score += 2
            if other.id == "courier":
                score += 1
            candidates.append((score, other))

        if not candidates:
            return False
        candidates.sort(key=lambda item: item[0], reverse=True)
        score, receiver = candidates[0]
        if score <= 0 and self.free_capacity(char) >= 2:
            return False

        receiver.objectives.append(char.objectives.pop())
        self.metrics["transfers"] += 1
        self.coop_metrics["objective_transfers"] += 1
        if self.cooperation_mode["transfer_action_cost"] == 0 or char.id == "courier":
            self.coop_metrics["free_transfers"] += 1
        else:
            self.coop_metrics["transfer_actions"] += 1
        return True

    def strategic_action(self, char):
        self.deposit_objectives(char)

        transferred = self.transfer_if_useful(char)
        if transferred:
            if self.cooperation_mode["transfer_action_cost"] == 0 or char.id == "courier":
                # Fortsätt till en riktig handling; överföringen var gratis.
                pass
            else:
                self.actions["transfer"] += 1
                return 1

        if self.pickup_ground(char):
            return 1
        if self.use_equipment(char):
            return 1

        heal_threshold = self.params.get("heal_at_health", 1)
        if char.health_remaining <= heal_threshold:
            if char.location == self.base:
                char.damage = max(0, char.damage - 1)
                self.actions["recover"] += 1
                return 1
            return self.move_action(char, self.base)

        tool_target = self.params.get("collect_tools_target", 1)
        if char.tools < tool_target and self.supply_tools > 0 and self.objectives_found < 3:
            if char.location == self.supply and self.take_tool(char):
                return 1
            if char.location == self.base or self.round <= 2:
                spent = self.move_action(char, self.supply)
                if spent:
                    return spent

        if char.location in self.location_assignment and char.location not in self.revealed_locations:
            self.assigned_targets.pop(char.id, None)
            return 1 if self.explore(char) else 0

        target = self.target_for(char)
        if target == char.location:
            if self.pickup_ground(char):
                return 1
            return 0
        return self.move_action(char, target)

    def run(self):
        result = "loss"
        while self.round <= self.maximum_rounds:
            self.round_reserved_targets = set()
            for char in self.characters:
                self.activate(char)
                if self.victory():
                    result = "win"
                    self.end_reason = "objectives_returned"
                    break
                if self.defeat():
                    self.end_reason = "all_incapacitated" if self.endurance > 0 else "endurance"
                    break
            if result == "win" or self.defeat():
                break

            if self.victory():
                result = "win"
                self.end_reason = "objectives_returned"
                break

            self.endurance -= self.scenario["endurance_phase"]["loss_each_round"]

            if self.defeat():
                self.end_reason = "endurance" if self.endurance <= 0 else "all_incapacitated"
                break
            self.round += 1

        if not self.end_reason:
            self.end_reason = "maximum_rounds"

        base_result = self.GameResultClass(
            strategy=self.strategy["id"],
            seed=self.seed,
            result=result,
            rounds=self.round,
            final_endurance=self.endurance,
            objectives_found=self.objectives_found,
            objectives_returned=len(self.objectives_at_base),
            total_damage=sum(c.damage for c in self.characters),
            incapacitations=sum(not c.active for c in self.characters),
            hidden_roads_tested=self.metrics["hidden_roads_tested"],
            blocked_roads_found=self.metrics["blocked_roads_found"],
            travel_events=self.metrics["travel_events"],
            tools_taken=self.metrics["tools_taken"],
            tools_spent=self.metrics["tools_spent"],
            capacity_failures=self.metrics["capacity_failures"],
            items_dropped=self.metrics["items_dropped"],
            transfers=self.metrics["transfers"],
            equipment_drawn=self.metrics["equipment_drawn"],
            equipment_used=self.metrics["equipment_used"],
            action_counts=dict(self.actions),
            characters=[c.id for c in self.characters],
            end_reason=self.end_reason,
            scenario_id=self.scenario["id"],
            base_profile_id=self.base_profile["id"],
            location_set_id=self.content_sets["locations"],
            objective_set_id=self.content_sets["objectives"],
            character_count=self.sim_data["characters_per_game"],
            starting_endurance=self.scenario["setup"]["endurance_by_character_count"][
                str(self.sim_data["characters_per_game"])
            ],
            starting_tools=self.starting_tools,
        )
        return base_result, dict(self.coop_metrics)


def create_simulation_class(module):
    class CooperationSimulation(CooperativeSimulationMixin, module.ExpeditionSimulation):
        GameResultClass = module.GameResult

        def __init__(self, root, strategy, seed, mode, character_count):
            super().__init__(
                root,
                strategy,
                seed,
                characters_per_game=character_count,
            )
            self.initialize_cooperation(mode)

    return CooperationSimulation


def aggregate_cell(results, coop_rows):
    wins = [r for r in results if r.result == "win"]
    return {
        "runs": len(results),
        "wins": len(wins),
        "win_rate": len(wins) / len(results) if results else 0,
        "mean_rounds": statistics.fmean(r.rounds for r in results),
        "mean_final_endurance": statistics.fmean(r.final_endurance for r in results),
        "mean_objectives_returned": statistics.fmean(r.objectives_returned for r in results),
        "mean_capacity_failures": statistics.fmean(r.capacity_failures for r in results),
        "mean_items_dropped": statistics.fmean(r.items_dropped for r in results),
        "mean_transfers": statistics.fmean(r.transfers for r in results),
        "mean_duplicate_destinations": statistics.fmean(
            row.get("duplicate_destinations", 0) for row in coop_rows
        ),
        "mean_coordinated_assignments": statistics.fmean(
            row.get("coordinated_assignments", 0) for row in coop_rows
        ),
        "mean_transfer_actions": statistics.fmean(
            row.get("transfer_actions", 0) for row in coop_rows
        ),
        "mean_free_transfers": statistics.fmean(
            row.get("free_transfers", 0) for row in coop_rows
        ),
        "end_reasons": dict(Counter(r.end_reason for r in results)),
    }


def write_reports(root, cfg, cells, raw_rows):
    out_dir = root / cfg["study"]["output_directory"]
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "summary.json").write_text(
        json.dumps(
            {
                "status": "simulation_hypothesis_not_physical_playtest",
                "study": cfg["study"],
                "scenario": {
                    "id": raw_rows[0]["scenario_id"] if raw_rows else "",
                    "base_profile": raw_rows[0]["base_profile_id"] if raw_rows else "",
                    "location_set": raw_rows[0]["location_set_id"] if raw_rows else "",
                    "objective_set": raw_rows[0]["objective_set_id"] if raw_rows else "",
                },
                "modes": cfg["modes"],
                "cells": cells,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    columns = [
        "characters", "strategy", "strategy_name", "mode", "mode_name",
        "runs", "wins", "win_rate", "mean_rounds", "mean_final_endurance",
        "mean_objectives_returned", "mean_capacity_failures",
        "mean_items_dropped", "mean_transfers",
        "mean_duplicate_destinations", "mean_coordinated_assignments",
        "mean_transfer_actions", "mean_free_transfers",
    ]
    with (out_dir / "cooperation-comparison.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for cell in cells:
            writer.writerow({key: cell.get(key) for key in columns})

    raw_columns = [
        "scenario_id", "base_profile_id", "location_set_id", "objective_set_id",
        "characters", "starting_endurance", "starting_tools",
        "strategy", "mode", "seed", "result", "rounds",
        "final_endurance", "objectives_returned", "capacity_failures",
        "items_dropped", "transfers", "duplicate_destinations",
        "coordinated_assignments", "transfer_actions", "free_transfers",
        "end_reason",
    ]
    with (out_dir / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_columns)
        writer.writeheader()
        writer.writerows(raw_rows)

    lines = [
        "# Samarbets-ablationsstudie",
        "",
        "> Resultaten är hypoteser från en förenklad simulator. De mäter inte mänsklig kommunikation eller spelglädje.",
        "",
        f"- Körningar per cell: **{cfg['study']['runs_per_cell']}**",
        f"- Grundseed: `{cfg['study']['base_seed']}`",
        f"- Karaktärsantal: {', '.join(map(str, cfg['study']['character_counts']))}",
        "",
        "## Genomsnittlig vinstgrad över strategier",
        "",
        "| Karaktärer | Individuellt | Samordnade mål | Fullt samarbete | Gratis överföring |",
        "|---:|---:|---:|---:|---:|",
    ]
    mode_ids = [mode["id"] for mode in cfg["modes"]]
    for count in cfg["study"]["character_counts"]:
        values = {}
        for mode_id in mode_ids:
            subset = [
                cell["win_rate"] for cell in cells
                if cell["characters"] == count and cell["mode"] == mode_id
            ]
            values[mode_id] = statistics.fmean(subset)
        lines.append(
            f"| {count} | {values['individual']:.1%} | "
            f"{values['route_coordination']:.1%} | "
            f"{values['full_cooperation']:.1%} | "
            f"{values['free_transfer']:.1%} |"
        )

    lines += ["", "## Samarbetsvärde", ""]
    for count in cfg["study"]["character_counts"]:
        individual = statistics.fmean(
            cell["win_rate"] for cell in cells
            if cell["characters"] == count and cell["mode"] == "individual"
        )
        route = statistics.fmean(
            cell["win_rate"] for cell in cells
            if cell["characters"] == count and cell["mode"] == "route_coordination"
        )
        full = statistics.fmean(
            cell["win_rate"] for cell in cells
            if cell["characters"] == count and cell["mode"] == "full_cooperation"
        )
        free = statistics.fmean(
            cell["win_rate"] for cell in cells
            if cell["characters"] == count and cell["mode"] == "free_transfer"
        )
        lines += [
            f"### {count} karaktärer",
            "",
            f"- Ruttkoordination: **{route-individual:+.1%}** jämfört med individuellt.",
            f"- Fullt samarbete: **{full-individual:+.1%}** jämfört med individuellt.",
            f"- Gratis överföring: **{free-full:+.1%}** jämfört med normal överföringskostnad.",
            "",
        ]

    lines += [
        "## Tolkning",
        "",
        "- Ruttkoordination isolerar värdet av att undvika dubblerade destinationer.",
        "- Fullt samarbete lägger till överföring av målobjekt vid möten.",
        "- Gratis överföring visar om normal handlingskostnad gör samarbete för dyrt.",
        "- Små eller negativa skillnader betyder inte automatiskt att samarbete är dåligt; agentens möteslogik kan fortfarande vara för enkel.",
        "",
        "## Begränsningar",
        "",
        "- Karaktärerna kommunicerar perfekt och omedelbart.",
        "- Möten planeras bara genom enkla heuristiker.",
        "- Utrustning och verktyg överförs inte lika avancerat som målobjekt.",
        "- Sociala samarbetsvärden, diskussion och alfa-spelare simuleras inte.",
    ]
    (out_dir / "cooperation-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--runs", type=int, help="Körningar per cell.")
    args = parser.parse_args()

    root = args.root.resolve()
    cfg = load_yaml(root / "data/cooperation-ablation.yaml")
    if args.runs:
        cfg["study"]["runs_per_cell"] = args.runs

    sim_cfg = load_yaml(root / "data/simulation.yaml")
    strategies_by_id = {s["id"]: s for s in sim_cfg["strategies"]}
    module = load_simulator(root)
    SimulationClass = create_simulation_class(module)

    cells = []
    raw_rows = []
    runs = cfg["study"]["runs_per_cell"]
    base_seed = cfg["study"]["base_seed"]

    for characters in cfg["study"]["character_counts"]:
        for strategy_index, strategy_id in enumerate(cfg["study"]["strategies"]):
            strategy = strategies_by_id[strategy_id]
            for mode in cfg["modes"]:
                results = []
                coop_rows = []
                for run_index in range(runs):
                    seed = base_seed + characters * 100000 + strategy_index * 10000 + run_index
                    simulation = SimulationClass(
                        root, strategy, seed, mode, characters
                    )
                    result, coop = simulation.run()
                    results.append(result)
                    coop_rows.append(coop)
                    raw_rows.append({
                        "scenario_id": result.scenario_id,
                        "base_profile_id": result.base_profile_id,
                        "location_set_id": result.location_set_id,
                        "objective_set_id": result.objective_set_id,
                        "characters": characters,
                        "starting_endurance": result.starting_endurance,
                        "starting_tools": result.starting_tools,
                        "strategy": strategy_id,
                        "mode": mode["id"],
                        "seed": seed,
                        "result": result.result,
                        "rounds": result.rounds,
                        "final_endurance": result.final_endurance,
                        "objectives_returned": result.objectives_returned,
                        "capacity_failures": result.capacity_failures,
                        "items_dropped": result.items_dropped,
                        "transfers": result.transfers,
                        "duplicate_destinations": coop.get("duplicate_destinations", 0),
                        "coordinated_assignments": coop.get("coordinated_assignments", 0),
                        "transfer_actions": coop.get("transfer_actions", 0),
                        "free_transfers": coop.get("free_transfers", 0),
                        "end_reason": result.end_reason,
                    })
                cell = aggregate_cell(results, coop_rows)
                cell.update({
                    "characters": characters,
                    "strategy": strategy_id,
                    "strategy_name": strategy["name"],
                    "mode": mode["id"],
                    "mode_name": mode["name"],
                })
                cells.append(cell)
                print(
                    f"{characters} karaktärer · {strategy_id} · {mode['id']}: "
                    f"{cell['win_rate']:.1%}"
                )

    write_reports(root, cfg, cells, raw_rows)
    print(f"Rapporter: {cfg['study']['output_directory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
