#!/usr/bin/env python3
"""Jämför separata agentklasser mot samma spelmotor."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[1]
if str(ROOT_DEFAULT) not in sys.path:
    sys.path.insert(0, str(ROOT_DEFAULT))

from agents.standard import build_agents
from engine.game_engine import GameEngine


def aggregate(agent, character_count, results):
    wins = [r for r in results if r.result == "win"]
    return {
        "agent": agent.id,
        "agent_name": agent.name,
        "characters": character_count,
        "runs": len(results),
        "wins": len(wins),
        "win_rate": len(wins) / len(results),
        "mean_rounds": statistics.fmean(r.rounds for r in results),
        "mean_win_rounds": statistics.fmean(r.rounds for r in wins) if wins else None,
        "mean_final_endurance": statistics.fmean(r.final_endurance for r in results),
        "mean_objectives_found": statistics.fmean(r.objectives_found for r in results),
        "mean_objectives_returned": statistics.fmean(r.objectives_returned for r in results),
        "mean_damage": statistics.fmean(r.total_damage for r in results),
        "mean_capacity_failures": statistics.fmean(r.capacity_failures for r in results),
        "mean_hidden_roads_tested": statistics.fmean(r.hidden_roads_tested for r in results),
        "mean_adaptive_hidden_choices": statistics.fmean(r.adaptive_hidden_choices for r in results),
        "mean_tools_taken": statistics.fmean(r.tools_taken for r in results),
        "end_reasons": dict(Counter(r.end_reason for r in results)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=34000)
    parser.add_argument("--characters", type=int, nargs="+", default=[2, 3, 4])
    args = parser.parse_args()

    root = args.root.resolve()
    out = root / "output/simulation/agent-engine-comparison"
    out.mkdir(parents=True, exist_ok=True)

    engine = GameEngine(root)
    agents = build_agents()
    summaries = []
    raw = []

    for character_count in args.characters:
        for agent_index, agent in enumerate(agents):
            results = []
            for run_index in range(args.runs):
                # Samma seedserie mellan agenter inom samma spelarprofil.
                seed = args.seed + character_count * 100000 + run_index
                result = engine.run_game(agent, seed, character_count)
                results.append(result)
                raw.append({
                    "scenario_id": result.scenario_id,
                    "base_profile_id": result.base_profile_id,
                    "location_set_id": result.location_set_id,
                    "objective_set_id": result.objective_set_id,
                    "characters": character_count,
                    "starting_endurance": result.starting_endurance,
                    "starting_tools": result.starting_tools,
                    "agent": agent.id,
                    "seed": seed,
                    "result": result.result,
                    "rounds": result.rounds,
                    "final_endurance": result.final_endurance,
                    "objectives_found": result.objectives_found,
                    "objectives_returned": result.objectives_returned,
                    "damage": result.total_damage,
                    "capacity_failures": result.capacity_failures,
                    "hidden_roads_tested": result.hidden_roads_tested,
                    "adaptive_hidden_choices": result.adaptive_hidden_choices,
                    "tools_taken": result.tools_taken,
                    "end_reason": result.end_reason,
                })
            summary = aggregate(agent, character_count, results)
            summaries.append(summary)
            print(
                f"{character_count} karaktärer · {agent.name}: "
                f"{summary['win_rate']:.1%}"
            )

    (out / "summary.json").write_text(
        json.dumps(
            {
                "status": "shared_engine_agent_comparison",
                "runs_per_cell": args.runs,
                "base_seed": args.seed,
                "engine": "engine/game_engine.py",
                "agents": "agents/standard.py",
                "scenario": {
                    "id": raw[0]["scenario_id"] if raw else "",
                    "base_profile": raw[0]["base_profile_id"] if raw else "",
                    "location_set": raw[0]["location_set_id"] if raw else "",
                    "objective_set": raw[0]["objective_set_id"] if raw else "",
                },
                "summaries": summaries,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    columns = [
        "characters", "agent", "agent_name", "runs", "wins", "win_rate",
        "mean_rounds", "mean_win_rounds", "mean_final_endurance",
        "mean_objectives_found", "mean_objectives_returned", "mean_damage",
        "mean_capacity_failures", "mean_hidden_roads_tested",
        "mean_adaptive_hidden_choices", "mean_tools_taken",
    ]
    with (out / "agent-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in columns} for row in summaries)

    with (out / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(raw[0].keys()))
        writer.writeheader()
        writer.writerows(raw)

    lines = [
        "# Agentjämförelse med gemensam spelmotor",
        "",
        "> Alla agenttyper kör samma scenariostyrda spelmotor, YAML-data, kortpooler, spelplan och regelimplementation. Endast beslutsprofilen skiljer.",
        "",
        f"- Körningar per cell: **{args.runs}**",
        f"- Grundseed: `{args.seed}`",
        "",
        "| Agent | 2 karaktärer | 3 karaktärer | 4 karaktärer |",
        "|---|---:|---:|---:|",
    ]
    for agent in agents:
        vals = {
            row["characters"]: row["win_rate"]
            for row in summaries if row["agent"] == agent.id
        }
        lines.append(
            f"| {agent.name} | {vals.get(2, 0):.1%} | "
            f"{vals.get(3, 0):.1%} | {vals.get(4, 0):.1%} |"
        )

    lines += [
        "",
        "## Vad arkitekturen visar",
        "",
        "- Skillnader mellan raderna kommer från agenternas beslut, inte från olika regler.",
        "- Samma seedserie gör setup och slump jämförbar mellan agenter.",
        "- Simulatorn använder samma kortmängder, vägmarkörer, platskort och karaktärsdata som projektets YAML.",
        "- Den gemensamma motorn tolkar fortfarande vissa regler i Python och är inte en fullständig digital kopia av mänskligt spel.",
        "",
        "## Begränsningar",
        "",
        "- Agenterna använder fortfarande heuristiska profiler.",
        "- Avancerad gemensam planering och framtida mötesplanering är begränsad.",
        "- Mänsklig kommunikation, misstag, lästid och fysisk hantering simuleras inte.",
    ]
    (out / "agent-comparison-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
