#!/usr/bin/env python3
"""Seed-matchade experiment för dynamiska förbindelser.

Rapporten är ett hypotesunderlag och ersätter inte fysiska speltester.
"""

from __future__ import annotations
import argparse, csv, json, statistics, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.standard import build_agents
from engine.game_engine import GameEngine

VARIANTS = {
    "none": [],
    "v1_after_1": [{"id":"open_v1_after_1","trigger":{"event":"objective_completed","count":1},"effects":[{"action":"open_connection","connection_id":"route_v1"}]}],
    "v2_after_1": [{"id":"open_v2_after_1","trigger":{"event":"objective_completed","count":1},"effects":[{"action":"open_connection","connection_id":"route_v2"}]}],
    "v1_then_v2": [
        {"id":"open_v1_after_1","trigger":{"event":"objective_completed","count":1},"effects":[{"action":"open_connection","connection_id":"route_v1"}]},
        {"id":"open_v2_after_2","trigger":{"event":"objective_completed","count":2},"effects":[{"action":"open_connection","connection_id":"route_v2"}]},
    ],
    "choose_after_1": [{"id":"choose_after_1","trigger":{"event":"objective_completed","count":1},"effects":[{"action":"choose_connection","choose":1,"from":["route_v1","route_v2","route_v3"]}]}],
    "choose_after_1_and_2": [
        {"id":"choose_after_1","trigger":{"event":"objective_completed","count":1},"effects":[{"action":"choose_connection","choose":1,"from":["route_v1","route_v2","route_v3"]}]},
        {"id":"choose_after_2","trigger":{"event":"objective_completed","count":2},"effects":[{"action":"choose_connection","choose":1,"from":["route_v1","route_v2","route_v3"]}]},
    ],
    "v4_after_objective_activation_1": [{"id":"open_v4_after_objective_activation_1","trigger":{"event":"objective_activated","count":1},"effects":[{"action":"open_connection","connection_id":"route_v4"}]}],
}

def run_game(engine, agent, seed, scenario, endurance, variant, tie, scenario_events):
    game = engine.create_game(agent, seed, characters=2, scenario_id=scenario)
    game.scenario_events_enabled = scenario_events == "on"
    game.params["exploration_tie_breaker"] = tie
    # Rebuild deterministic rank because game initialization already consumed config.
    ids = sorted(loc["id"] for loc in game.board["locations"])
    if tie == "right":
        ids.reverse()
    elif tie == "random":
        game.rng.shuffle(ids)
    game.node_tie_rank = {node_id:i for i,node_id in enumerate(ids)}
    game.progression_events = VARIANTS[variant]
    game.endurance = endurance
    result = game.run()
    return {
        "variant": variant, "scenario_events": scenario_events,
        "tie_breaker": tie, "agent": agent.id, "seed": seed,
        "scenario": scenario, "starting_endurance": endurance,
        "result": result.result, "win": int(result.result=="win"), "rounds": result.rounds,
        "final_endurance": result.final_endurance,
        "moves": result.action_counts.get("move",0),
        "objectives_completed": result.objectives_returned,
        "progression_events_fired": result.progression_events_fired,
        "connection_uses": json.dumps(result.connection_uses or {}, sort_keys=True),
        "connection_open_rounds": json.dumps(result.connection_open_rounds or {}, sort_keys=True),
        "total_dynamic_uses": sum((result.connection_uses or {}).values()),
        "scenario_events_resolved": result.scenario_events_resolved,
        "scenario_event_cards": json.dumps(result.scenario_event_cards, ensure_ascii=False),
        "scenario_event_rounds": json.dumps(result.scenario_event_rounds),
        "scenario_event_endurance_delta": result.scenario_event_endurance_delta,
        "connections_closed_by_events": json.dumps(result.connections_closed_by_events),
        "connections_opened_by_events": json.dumps(result.connections_opened_by_events),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--runs",type=int,default=100)
    ap.add_argument("--seed",type=int,default=49000)
    ap.add_argument("--scenario",default="station_nordanvind")
    ap.add_argument("--endurance",type=int,nargs="+",default=[13,12,11,10,9])
    ap.add_argument("--variants",nargs="+",default=list(VARIANTS))
    ap.add_argument("--tie-breakers",nargs="+",default=["left","right","random"])
    ap.add_argument(
        "--scenario-events",
        nargs="+",
        choices=["on", "off"],
        default=["on", "off"],
        help="Kör seed-matchade celler med scenarioevent aktiva och/eller avstängda.",
    )
    args=ap.parse_args()
    engine=GameEngine(args.root.resolve())
    agents=[a for a in build_agents() if a.id!="random_agent"]
    rows=[]
    for endurance in args.endurance:
      for tie in args.tie_breakers:
       for variant in args.variants:
        for scenario_events in args.scenario_events:
         for agent in agents:
          for i in range(args.runs):
           seed=args.seed+i
           rows.append(run_game(
               engine, agent, seed, args.scenario, endurance, variant, tie,
               scenario_events,
           ))
    out=args.root/"output/simulation/dynamic-connections"
    out.mkdir(parents=True,exist_ok=True)
    cols=list(rows[0])
    with (out/"runs.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    groups={}
    for r in rows:
        groups.setdefault((
            r["starting_endurance"], r["tie_breaker"], r["variant"],
            r["scenario_events"],
        ), []).append(r)
    summary=[]
    for (endurance,tie,variant,scenario_events),rs in groups.items():
        wins=sum(r["win"] for r in rs)
        summary.append({
          "starting_endurance":endurance,"tie_breaker":tie,"variant":variant,
          "scenario_events":scenario_events,"runs":len(rs),
          "wins":wins,"win_rate":wins/len(rs),
          "mean_rounds":statistics.fmean(r["rounds"] for r in rs),
          "median_rounds":statistics.median(r["rounds"] for r in rs),
          "mean_moves":statistics.fmean(r["moves"] for r in rs),
          "mean_dynamic_uses":statistics.fmean(r["total_dynamic_uses"] for r in rs),
          "games_using_dynamic_connection":sum(r["total_dynamic_uses"]>0 for r in rs)/len(rs),
          "mean_final_endurance":statistics.fmean(r["final_endurance"] for r in rs),
          "mean_scenario_events_resolved":statistics.fmean(
              r["scenario_events_resolved"] for r in rs
          ),
          "mean_scenario_event_endurance_delta":statistics.fmean(
              r["scenario_event_endurance_delta"] for r in rs
          ),
          "games_with_closed_connection_event":sum(
              r["connections_closed_by_events"] != "[]" for r in rs
          ) / len(rs),
        })
    with (out/"summary.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    (out/"summary.json").write_text(json.dumps({"status":"simulation_hypothesis_not_physical_playtest","rows":summary},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    md=["# Dynamiska förbindelser – simuleringsmatris","","> Hypotesunderlag; inte fysiskt speltest.","",
        f"- Körningar per agent/cell: **{args.runs}**",f"- Agenter per cell: **{len(agents)}**","",
        "| Uthållighet | Tie-breaker | Variant | Scenarioevent | Vinst | Rundor | Rörelser | Event | Event Δ uth. |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|"]
    for s in sorted(summary,key=lambda x:(
        -x["starting_endurance"],x["tie_breaker"],x["variant"],x["scenario_events"]
    )):
        md.append(
            f'| {s["starting_endurance"]} | {s["tie_breaker"]} | '
            f'{s["variant"]} | {s["scenario_events"]} | {s["win_rate"]:.1%} | '
            f'{s["mean_rounds"]:.2f} | {s["mean_moves"]:.2f} | '
            f'{s["mean_scenario_events_resolved"]:.2f} | '
            f'{s["mean_scenario_event_endurance_delta"]:.2f} |'
        )
    (out/"report.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(f"Skrev {len(rows)} körningar till {out}")
if __name__=="__main__":
    main()
