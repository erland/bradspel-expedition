#!/usr/bin/env python3
"""Kör och jämför alla aktiva Expedition-scenarier med samma agenter och seeds."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT_DEFAULT = Path(__file__).resolve().parents[1]
if str(ROOT_DEFAULT) not in sys.path:
    sys.path.insert(0, str(ROOT_DEFAULT))

from agents.standard import build_agents
from engine.game_engine import GameEngine


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def aggregate(scenario_id, scenario_name, agent, characters, results):
    wins = [r for r in results if r.result == "win"]
    win_rate = len(wins) / len(results) if results else 0
    se = math.sqrt(win_rate * (1 - win_rate) / len(results)) if results else 0
    return {
        "scenario": scenario_id,
        "scenario_name": scenario_name,
        "agent": agent.id,
        "agent_name": agent.name,
        "characters": characters,
        "runs": len(results),
        "wins": len(wins),
        "win_rate": win_rate,
        "ci_low": max(0, win_rate - 1.96 * se),
        "ci_high": min(1, win_rate + 1.96 * se),
        "mean_rounds": statistics.fmean(r.rounds for r in results),
        "mean_win_rounds": statistics.fmean(r.rounds for r in wins) if wins else None,
        "mean_final_endurance": statistics.fmean(r.final_endurance for r in results),
        "mean_mission_progress": statistics.fmean(r.objectives_returned for r in results),
        "mean_damage": statistics.fmean(r.total_damage for r in results),
        "mean_capacity_failures": statistics.fmean(r.capacity_failures for r in results),
        "mean_tools_taken": statistics.fmean(r.tools_taken for r in results),
        "end_reasons": dict(Counter(r.end_reason for r in results)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--seed", type=int, default=139000)
    parser.add_argument("--characters", type=int, nargs="+", default=[2, 3, 4])
    parser.add_argument("--scenario", action="append", help="Begränsa till scenario-id.")
    args = parser.parse_args()

    root = args.root.resolve()
    scenario_index = load_yaml(root / "data/scenarios.yaml")["scenarios"]
    selected_ids = set(args.scenario or [s["id"] for s in scenario_index])
    scenarios = [s for s in scenario_index if s["id"] in selected_ids]
    if not scenarios:
        raise ValueError("Inga giltiga scenarier valda.")

    out = root / "output/simulation/scenario-comparison"
    out.mkdir(parents=True, exist_ok=True)
    engine = GameEngine(root)
    agents = build_agents()
    summaries = []
    raw = []

    for scenario in scenarios:
        for characters in args.characters:
            for agent in agents:
                results = []
                for run_index in range(args.runs):
                    # Samma seed för samma spelarantal och run-index i alla scenarier och agenter.
                    seed = args.seed + characters * 100_000 + run_index
                    result = engine.run_game(
                        agent, seed, characters, scenario_id=scenario["id"]
                    )
                    results.append(result)
                    raw.append({
                        "scenario": scenario["id"],
                        "scenario_name": scenario["name"],
                        "agent": agent.id,
                        "agent_name": agent.name,
                        "characters": characters,
                        "seed": seed,
                        "starting_endurance": result.starting_endurance,
                        "starting_tools": result.starting_tools,
                        "result": result.result,
                        "rounds": result.rounds,
                        "final_endurance": result.final_endurance,
                        "mission_progress": result.objectives_returned,
                        "objectives_found": result.objectives_found,
                        "damage": result.total_damage,
                        "capacity_failures": result.capacity_failures,
                        "tools_taken": result.tools_taken,
                        "end_reason": result.end_reason,
                    })
                row = aggregate(scenario["id"], scenario["name"], agent, characters, results)
                summaries.append(row)
                print(
                    f"{scenario['name']} · {characters} karaktärer · {agent.name}: "
                    f"{row['win_rate']:.1%}"
                )

    structured_ids = {a.id for a in agents if "random" not in a.id}
    profiles = []
    for scenario in scenarios:
        for characters in args.characters:
            subset = [
                row for row in summaries
                if row["scenario"] == scenario["id"]
                and row["characters"] == characters
                and row["agent"] in structured_ids
            ]
            total_runs = sum(row["runs"] for row in subset)
            total_wins = sum(row["wins"] for row in subset)
            p = total_wins / total_runs if total_runs else 0
            se = math.sqrt(p * (1-p) / total_runs) if total_runs else 0
            profiles.append({
                "scenario": scenario["id"],
                "scenario_name": scenario["name"],
                "characters": characters,
                "runs": total_runs,
                "wins": total_wins,
                "win_rate": p,
                "ci_low": max(0, p - 1.96 * se),
                "ci_high": min(1, p + 1.96 * se),
                "mean_rounds": statistics.fmean(r["mean_rounds"] for r in subset),
                "mean_final_endurance": statistics.fmean(r["mean_final_endurance"] for r in subset),
                "mean_mission_progress": statistics.fmean(r["mean_mission_progress"] for r in subset),
            })

    payload = {
        "status": "scenario_comparison_hypothesis",
        "runs_per_cell": args.runs,
        "base_seed": args.seed,
        "same_seeds_across_scenarios": True,
        "scenarios": [{"id": s["id"], "name": s["name"]} for s in scenarios],
        "characters": args.characters,
        "summaries": summaries,
        "structured_agent_profiles": profiles,
    }
    (out / "summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with (out / "scenario-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        cols = [
            "scenario", "scenario_name", "agent", "agent_name", "characters",
            "runs", "wins", "win_rate", "ci_low", "ci_high", "mean_rounds",
            "mean_win_rounds", "mean_final_endurance", "mean_mission_progress",
            "mean_damage", "mean_capacity_failures", "mean_tools_taken",
        ]
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        writer.writerows({k: row.get(k) for k in cols} for row in summaries)

    with (out / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(raw[0].keys()))
        writer.writeheader()
        writer.writerows(raw)

    lines = [
        "# Scenariojämförelse",
        "",
        "> Båda scenarierna körs med samma spelmotor, agenttyper, spelarantal och seedserie.",
        "> Resultaten är simulatorhypoteser och inte fysiska speltest.",
        "",
        f"- Körningar per scenario/agent/spelarantal: **{args.runs}**",
        f"- Totalt antal spel: **{len(raw)}**",
        f"- Grundseed: `{args.seed}`",
        "",
        "## Strukturerade agenter",
        "",
        "| Scenario | Karaktärer | Vinstgrad | 95 % intervall | Rundor | Slututhållighet | Uppdragsframsteg |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in profiles:
        lines.append(
            f"| {row['scenario_name']} | {row['characters']} | {row['win_rate']:.1%} | "
            f"{row['ci_low']:.1%}–{row['ci_high']:.1%} | {row['mean_rounds']:.2f} | "
            f"{row['mean_final_endurance']:.2f} | {row['mean_mission_progress']:.2f} |"
        )

    lines += ["", "## Vinstgrad per agent", ""]
    for scenario in scenarios:
        lines += [
            f"### {scenario['name']}", "",
            "| Agent | 2 karaktärer | 3 karaktärer | 4 karaktärer |",
            "|---|---:|---:|---:|",
        ]
        for agent in agents:
            values = {
                row["characters"]: row["win_rate"]
                for row in summaries
                if row["scenario"] == scenario["id"] and row["agent"] == agent.id
            }
            lines.append(
                f"| {agent.name} | {values.get(2,0):.1%} | "
                f"{values.get(3,0):.1%} | {values.get(4,0):.1%} |"
            )
        lines.append("")

    lines += [
        "## Arkitektursignal", "",
        "- Scenarierna väljs via scenarioindexet och laddar egna kortset.",
        "- Samma agentkod kan lösa både hemtransport och installation på kartan.",
        "- Skillnader i resultat kan därför jämföras utan manuella filbyten.",
        "- Del 4 bör använda resultatet för att avgöra vilka mekaniker som ska formaliseras i den generella datamodellen.",
    ]
    (out / "scenario-comparison-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
