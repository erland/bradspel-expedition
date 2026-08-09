#!/usr/bin/env python3
"""Monte Carlo-designsimulator för Expedition.

Simulatorn tolkar den aktuella spelmodellen tillräckligt noggrant för att
jämföra strategier och kontrollera lösbarhet. Den är inte en generell
regelmotor och ersätter inte fysiska speltest.
"""

import argparse
import csv
import heapq
import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@dataclass
class CharacterState:
    id: str
    health_max: int
    capacity_base: int
    location: str
    damage: int = 0
    tools: int = 0
    equipment: list[str] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    next_move_cost: int = 1
    cancel_next_travel_event: bool = False
    cancel_next_travel_endurance: bool = False
    install_discount: int = 0
    climber_used: bool = False
    scout_peek_round: int = 0
    technician_use_round: int = 0
    courier_transfer_activation: int = 0

    @property
    def active(self) -> bool:
        return self.damage < self.health_max

    @property
    def health_remaining(self) -> int:
        return max(0, self.health_max - self.damage)


@dataclass
class GameResult:
    strategy: str
    seed: int
    result: str
    rounds: int
    final_endurance: int
    objectives_found: int
    objectives_returned: int
    total_damage: int
    incapacitations: int
    hidden_roads_tested: int
    adaptive_hidden_choices: int
    blocked_roads_found: int
    travel_events: int
    tools_taken: int
    tools_spent: int
    capacity_failures: int
    items_dropped: int
    transfers: int
    equipment_drawn: int
    equipment_used: int
    action_counts: dict[str, int]
    characters: list[str]
    end_reason: str
    scenario_id: str = ""
    base_profile_id: str = ""
    location_set_id: str = ""
    objective_set_id: str = ""
    character_count: int = 0
    starting_endurance: int = 0
    starting_tools: int = 0
    connection_uses: dict[str, int] | None = None
    connection_open_rounds: dict[str, int] | None = None
    progression_events_fired: int = 0
    scenario_events_resolved: int = 0
    scenario_event_cards: list[str] = field(default_factory=list)
    scenario_event_rounds: list[int] = field(default_factory=list)
    scenario_event_endurance_delta: int = 0
    connections_closed_by_events: list[str] = field(default_factory=list)
    connections_opened_by_events: list[str] = field(default_factory=list)
    scenario_event_log: list[dict[str, Any]] = field(default_factory=list)


class ExpeditionSimulation:
    def __init__(self, root: Path, strategy: dict[str, Any], seed: int, scenario_id: str | None = None, characters_per_game: int | None = None):
        self.root = root
        self.strategy = strategy
        self.params = strategy["parameters"]
        self.seed = seed
        self.rng = random.Random(seed)

        self.board = load_yaml(root / "data/board.yaml")
        self.scenarios = load_yaml(root / "data/scenarios.yaml")
        self.sim_data = load_yaml(root / "data/simulation.yaml")["simulation"]
        if scenario_id is not None:
            self.sim_data["scenario_id"] = scenario_id
        if characters_per_game is not None:
            self.sim_data["characters_per_game"] = characters_per_game

        self.scenario = next(
            s for s in self.scenarios["scenarios"]
            if s["id"] == self.sim_data["scenario_id"]
        )
        self.scenario_pack = load_yaml(
            root / self.scenario["scenario_pack"]
        )["scenario_pack"]
        self.scenario_event_cards: dict[str, dict[str, Any]] = {}
        scenario_event_cfg = self.scenario_pack.get("scenario_events")
        if scenario_event_cfg:
            event_deck = load_yaml(root / scenario_event_cfg["source"])["scenario_event_deck"]
            if event_deck["id"] != scenario_event_cfg["deck_id"]:
                raise ValueError("Scenariohändelselekens id matchar inte scenariofilen.")
            self.scenario_event_cards = {
                card["id"]: card for card in event_deck["cards"]
            }
        self.base_profiles = load_yaml(root / "data/base-profiles.yaml")
        self.base_profile = next(
            profile for profile in self.base_profiles["base_profiles"]
            if profile["id"] == self.scenario_pack["base_profile"]
        )

        scenario_sources = self.scenario_pack["content"]["sources"]
        base_sources = self.base_profile["sources"]
        composition = self.scenario_pack["content"]["deck_composition"]
        self.locations_data = load_yaml(root / scenario_sources["locations"])
        self.objective_data = load_yaml(root / scenario_sources["objectives"])

        self.equipment_data = (
            load_yaml(root / base_sources["equipment"])
            if composition["equipment"] != "scenario_only"
            else {"equipment": []}
        )
        if composition["equipment"] in {"scenario_only", "base_plus_scenario"}:
            extra = load_yaml(root / scenario_sources["equipment"])
            self.equipment_data["equipment"].extend(extra["equipment"])

        self.travel_data = (
            load_yaml(root / base_sources["travel_events"])
            if composition["travel_events"] != "scenario_only"
            else {"cards": []}
        )
        if composition["travel_events"] in {"scenario_only", "base_plus_scenario"}:
            extra = load_yaml(root / scenario_sources["travel_events"])
            self.travel_data["cards"].extend(extra["cards"])
        self.character_data = load_yaml(root / base_sources["characters"])
        self.road_data = load_yaml(root / base_sources["road_markers"])

        self.content_sets = self.scenario_pack["content"]["scenario_sets"]
        self._verify_content_sets()
        self.maximum_rounds = self.sim_data["maximum_rounds"]
        self.base = self.scenario["setup"]["starting_location"]
        self.supply = "supply_depot"

        self.location_cards = self._expanded(self.locations_data["locations"])
        self.rng.shuffle(self.location_cards)
        slots = list(self.scenario["setup"]["location_slots"])
        self.location_assignment = dict(zip(slots, self.location_cards))
        self.revealed_locations: set[str] = set()

        self.objective_deck = self._expanded(self.objective_data["objectives"])
        self.rng.shuffle(self.objective_deck)
        self.equipment_deck = self._expanded(self.equipment_data["equipment"])
        self.rng.shuffle(self.equipment_deck)
        self.travel_deck = self._expanded(self.travel_data["cards"])
        self.rng.shuffle(self.travel_deck)
        self.travel_discard: list[dict[str, Any]] = []

        marker_results: list[str] = []
        marker_pool = self.scenario["setup"]["hidden_road_marker_pool"]
        for result in ("open", "blocked", "travel_event"):
            marker_results.extend([result] * int(marker_pool.get(result, 0)))
        self.rng.shuffle(marker_results)
        hidden_ids = list(self.scenario["setup"]["hidden_roads"])
        if len(marker_results) < len(hidden_ids):
            raise ValueError(
                "Scenariots dolda vägbrickepool innehåller färre brickor "
                "än antalet listade dolda vägar."
            )
        self.road_marker = dict(zip(hidden_ids, marker_results[:len(hidden_ids)]))
        self.known_hidden_roads: dict[str, str] = {}

        self.connections = {c["id"]: c for c in self.board["connections"]}
        self.connection_states: dict[str, str] = {
            connection_id: connection.get("default_state", "open")
            for connection_id, connection in self.connections.items()
        }
        self.node_states: dict[str, str] = {
            node["id"]: node.get("default_state", "open")
            for node in self.board["locations"]
        }
        self.node_occupants: dict[str, list[str]] = defaultdict(list)
        # Scenario-setup är fortsatt auktoritativ för vilka befintliga vägar
        # som får dolda brickor. Aliaset road_state behålls tills övrig kod
        # migrerats till det generella namnet.
        for road_id in hidden_ids:
            if road_id not in self.connection_states:
                raise ValueError(f"Scenario refererar till okänd dold väg: {road_id}")
            self.connection_states[road_id] = "hidden"
        self.road_state = self.connection_states

        # Adjacency innehåller all fysisk geometri. Traverserbarhet avgörs
        # dynamiskt av connection_states i pathfinding och rörelse.
        self.open_adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for connection in self.board["connections"]:
            self.open_adjacency[connection["from"]].append(
                (connection["to"], connection["id"])
            )
            self.open_adjacency[connection["to"]].append(
                (connection["from"], connection["id"])
            )

        selected = self._select_characters()
        self.characters = [
            CharacterState(
                id=c["id"],
                health_max=c["health"],
                capacity_base=c["backpack_capacity"],
                location=self.base,
            )
            for c in selected
        ]

        self.round = self.scenario["setup"].get("starting_round", 1)
        self.endurance = self.scenario["setup"]["endurance_by_character_count"][str(self.sim_data["characters_per_game"])]
        self.supply_tools = self.scenario["setup"]["supply_depot_tools"]
        self.ground_equipment: dict[str, list[str]] = defaultdict(list)
        self.ground_objectives: dict[str, list[str]] = defaultdict(list)
        self.ground_tools: dict[str, int] = defaultdict(int)
        self.starting_tools = 0
        self._apply_starting_tools()
        self.objectives_found = 0
        self.objectives_at_base: list[str] = []
        self.repair_sites: set[str] = set()
        self.repaired_sites: set[str] = set()
        self.mission_completion = self.scenario_pack["mission"]["completion"]
        self.mission_type = self.mission_completion["type"]
        self.metrics = Counter()
        self.actions = Counter()
        self.end_reason = ""
        self.activation_serial = 0
        self.progression_events = list(self.scenario_pack.get("progression_events", []))
        self.scenario_event_milestones = list(
            self.scenario_pack.get("scenario_events", {}).get("milestones", [])
        )
        self.fired_scenario_event_milestones: set[str] = set()
        self.scenario_event_log: list[dict[str, Any]] = []
        self.scenario_events_enabled = True
        self.fired_progression_events: set[str] = set()
        self.progression_log: list[dict[str, Any]] = []
        self.completed_objective_ids: set[str] = set()
        self.connection_uses: Counter[str] = Counter()
        self.connection_open_rounds: dict[str, int] = {}
        self.transfer_used_activations: set[int] = set()
        self.last_item_transfer: dict[tuple[str, str], tuple[int, str, str]] = {}
        self.transfer_log: list[dict[str, Any]] = []
        tie_mode = self.params.get("exploration_tie_breaker", "left")
        node_ids = sorted(self.board["locations"], key=lambda n: n["id"])
        ids = [node["id"] for node in node_ids]
        if tie_mode == "right":
            ids = list(reversed(ids))
        elif tie_mode == "random":
            self.rng.shuffle(ids)
        self.node_tie_rank = {node_id: rank for rank, node_id in enumerate(ids)}

        self.equipment_by_id = {
            item["id"]: item for item in self.equipment_data["equipment"]
        }
        self.objective_by_id = {
            item["id"]: item for item in self.objective_data["objectives"]
        }
        self.actions_per_activation = self.character_data.get("defaults", {}).get(
            "actions_per_round", 2
        )
        self.current_actions_remaining = self.actions_per_activation

    VALID_CONNECTION_STATES = {"open", "hidden", "closed", "sealed", "blocked"}
    VALID_NODE_STATES = {"open", "blocked"}

    def get_node_state(self, node_id: str) -> str:
        if node_id not in self.node_states:
            raise KeyError(f"Okänd nod: {node_id}")
        return self.node_states[node_id]

    def set_node_state(self, node_id: str, state: str) -> None:
        if state not in self.VALID_NODE_STATES:
            raise ValueError(f"Ogiltigt nodtillstånd: {state}")
        node = next((n for n in self.board["locations"] if n["id"] == node_id), None)
        if node is None:
            raise KeyError(f"Okänd nod: {node_id}")
        if node.get("node_role", "location") != "transit":
            raise ValueError(f"Endast transitnoder kan ändra nodtillstånd: {node_id}")
        self.node_states[node_id] = state

    def spawn_entity(self, entity_id: str, node_id: str) -> None:
        node = next((n for n in self.board["locations"] if n["id"] == node_id), None)
        if node is None:
            raise KeyError(f"Okänd nod: {node_id}")
        if not node.get("occupiable", True):
            raise ValueError(f"Noden kan inte innehålla entiteter: {node_id}")
        self.node_occupants[node_id].append(entity_id)

    def get_connection_state(self, connection_id: str) -> str:
        """Returnera aktuellt runtime-tillstånd för en förbindelse."""
        if connection_id not in self.connection_states:
            raise KeyError(f"Okänd förbindelse: {connection_id}")
        return self.connection_states[connection_id]

    def is_connection_traversable(self, connection_id: str) -> bool:
        """Öppen, dold och reparerbart blockerad väg kan ingå i pathfinding."""
        return self.get_connection_state(connection_id) in {
            "open",
            "hidden",
            "blocked",
        }

    def set_connection_state(self, connection_id: str, state: str) -> None:
        """Sätt runtime-tillstånd med enkel övergångsvalidering."""
        if state not in self.VALID_CONNECTION_STATES:
            raise ValueError(f"Ogiltigt förbindelsetillstånd: {state}")
        current = self.get_connection_state(connection_id)
        allowed = {
            "open": {"open", "blocked", "closed"},
            "hidden": {"hidden", "open", "blocked", "closed"},
            "closed": {"closed", "open", "sealed"},
            "sealed": {"sealed"},
            "blocked": {"blocked", "open", "closed"},
        }
        if state not in allowed[current]:
            raise ValueError(
                f"Ogiltig tillståndsövergång för {connection_id}: "
                f"{current} -> {state}"
            )
        self.connection_states[connection_id] = state

    def open_connection(self, connection_id: str) -> bool:
        """Öppna en stängd/dold/blockerad förbindelse.

        Returnerar True när tillståndet ändrades och False om vägen redan var
        öppen. Scenariohändelser kopplas in i nästa plansteg.
        """
        current = self.get_connection_state(connection_id)
        if current == "open":
            return False
        if current == "sealed":
            raise ValueError(f"Förseglad förbindelse kan inte öppnas: {connection_id}")
        self.set_connection_state(connection_id, "open")
        self.metrics["connections_opened"] += 1
        self.connection_open_rounds.setdefault(connection_id, self.round)
        return True

    def close_connection(self, connection_id: str) -> bool:
        """Stäng en förbindelse och gör den icke-traverserbar."""
        current = self.get_connection_state(connection_id)
        if current == "closed":
            return False
        if current == "sealed":
            raise ValueError(f"Förseglad förbindelse kan inte stängas om: {connection_id}")
        self.set_connection_state(connection_id, "closed")
        self.metrics["connections_closed"] += 1
        return True

    def seal_connection(self, connection_id: str) -> bool:
        """Försegla en ännu stängd scenarioväg."""
        current = self.get_connection_state(connection_id)
        if current == "sealed":
            return False
        self.set_connection_state(connection_id, "sealed")
        self.metrics["connections_sealed"] += 1
        return True

    @staticmethod
    def _expanded(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for item in items:
            result.extend([dict(item)] * item.get("count", 1))
        return result

    def _verify_content_sets(self) -> None:
        expected_locations = self.content_sets["locations"]
        expected_objectives = self.content_sets["objectives"]
        actual_locations = self.locations_data["location_deck"]["id"]
        actual_objectives = self.objective_data["deck"]["id"]
        if actual_locations != expected_locations:
            raise ValueError(
                f"Scenario {self.scenario['id']} kräver platsleken "
                f"{expected_locations}, men laddad fil innehåller {actual_locations}."
            )
        if actual_objectives != expected_objectives:
            raise ValueError(
                f"Scenario {self.scenario['id']} kräver målleken "
                f"{expected_objectives}, men laddad fil innehåller {actual_objectives}."
            )

    def _apply_starting_tools(self) -> None:
        count = self.scenario["setup"].get(
            "starting_tools_by_character_count", {}
        ).get(str(self.sim_data["characters_per_game"]), 0)
        if count <= 0 or not self.characters:
            self.starting_tools = 0
            return
        # Deterministisk och reproducerbar fördelning. Första karaktären i
        # den valda aktiveringsordningen får första verktyget.
        for index in range(count):
            receiver = self.characters[index % len(self.characters)]
            if self.can_fit(receiver, 1):
                receiver.tools += 1
            else:
                self.ground_tools[self.base] += 1
        self.starting_tools = count

    def _select_characters(self) -> list[dict[str, Any]]:
        all_chars = list(self.character_data["characters"])
        by_id = {c["id"]: c for c in all_chars}
        count = self.sim_data["characters_per_game"]
        selection = self.character_data["selection"]
        if count == 2:
            draw_count = selection["two_players"]["draw"]
        elif count == 3:
            draw_count = selection["three_players"]["draw"]
        elif count == 4:
            draw_count = selection["four_players"]["draw"]
        else:
            draw_count = selection["solo"]["draw"]

        pool_ids = [c["id"] for c in all_chars]
        self.rng.shuffle(pool_ids)
        drawn_ids = pool_ids[:draw_count]
        priority = [
            cid for cid in self.strategy.get("character_priority", [])
            if cid in drawn_ids
        ]
        selected_ids = priority[:count]
        remaining = [cid for cid in drawn_ids if cid not in selected_ids]
        self.rng.shuffle(remaining)
        selected_ids.extend(remaining[: count - len(selected_ids)])
        self.metrics_character_draw = {
            "drawn": drawn_ids,
            "selected": selected_ids,
        }
        return [by_id[cid] for cid in selected_ids]

    def capacity(self, char: CharacterState) -> int:
        bonus = 2 if "large_backpack" in char.equipment else 0
        return char.capacity_base + bonus

    def occupied(self, char: CharacterState) -> int:
        tool_slots = char.tools
        if "tool_belt" in char.equipment and tool_slots > 0:
            tool_slots -= 1
        equipment_slots = sum(self.equipment_by_id[e]["slots"] for e in char.equipment)
        objective_slots = sum(
            self.objective_by_id[objective_id]["slots"]
            for objective_id in char.objectives
        )
        return tool_slots + equipment_slots + objective_slots

    def free_capacity(self, char: CharacterState) -> int:
        return self.capacity(char) - self.occupied(char)

    def objective_slots(self, objective_id: str) -> int:
        return int(self.objective_by_id[objective_id]["slots"])

    def can_pay_actions(self, cost: int) -> bool:
        return cost <= self.current_actions_remaining

    def choose_pay_tool_or_damage(self, char: CharacterState, damage: int) -> str:
        """Agentval som följer spelarens faktiska valmöjlighet.

        Verktyget sparas när det är det sista och karaktären tål skadan.
        Strategiparametern ``pay_tool_health_threshold`` kan göra agenten mer
        eller mindre försiktig.
        """
        if char.tools <= 0:
            return "damage"
        threshold = int(self.params.get("pay_tool_health_threshold", 1))
        if char.health_remaining <= threshold:
            return "tool"
        if char.tools == 1:
            return "damage"
        return "tool"

    def can_fit(self, char: CharacterState, slots: int) -> bool:
        return self.free_capacity(char) >= slots

    def drop_for_space(self, char: CharacterState, slots: int) -> bool:
        if self.can_fit(char, slots):
            return True
        if not self.params.get("prioritize_objectives", False):
            return False

        # Drop least essential carried content, never an objective.
        priority = ["map_scanner", "climbing_rope", "medical_kit", "extra_supplies", "tool_belt"]
        for equipment_id in priority:
            if equipment_id in char.equipment:
                char.equipment.remove(equipment_id)
                self.ground_equipment[char.location].append(equipment_id)
                self.metrics["items_dropped"] += 1
                if self.can_fit(char, slots):
                    return True
        while char.tools > 0 and not self.can_fit(char, slots):
            char.tools -= 1
            self.ground_tools[char.location] += 1
            self.metrics["items_dropped"] += 1
        return self.can_fit(char, slots)

    def adjacent_hidden_roads(self, char: CharacterState) -> list[str]:
        return [
            road_id for _, road_id in self.open_adjacency[char.location]
            if self.road_state.get(road_id) == "hidden"
        ]

    def peek_roads(self, road_ids: list[str]) -> None:
        for road_id in road_ids:
            if self.road_state.get(road_id) == "hidden":
                self.known_hidden_roads[road_id] = self.road_marker[road_id]
                self.metrics["roads_peeked"] += 1

    def use_scout_ability(self, char: CharacterState) -> None:
        if char.id != "scout" or char.scout_peek_round == self.round:
            return
        candidates = self.adjacent_hidden_roads(char)
        if candidates:
            self.peek_roads([candidates[0]])
            char.scout_peek_round = self.round
            self.metrics["scout_peeks"] += 1

    def shortest_path(
        self,
        start: str,
        targets: set[str],
        allow_hidden: bool,
        char: CharacterState,
    ) -> list[tuple[str, str]]:
        if start in targets:
            return []
        queue: list[tuple[int, int, str, list[tuple[str, str]]]] = [(0, self.node_tie_rank.get(start, 0), start, [])]
        best = {start: 0}
        while queue:
            cost, _, node, path = heapq.heappop(queue)
            if node in targets:
                return path
            if cost != best.get(node):
                continue
            for neighbor, road_id in self.open_adjacency[node]:
                if self.get_node_state(neighbor) == "blocked":
                    continue
                state = self.get_connection_state(road_id)
                if not self.is_connection_traversable(road_id):
                    continue
                known_result = self.known_hidden_roads.get(road_id)
                if state == "hidden" and known_result == "blocked" and char.tools <= 0:
                    continue
                if state == "blocked":
                    if char.tools <= 0:
                        continue
                    edge_cost = 2  # unlock + move, engineer handled during resolution
                elif state == "hidden":
                    if not allow_hidden:
                        continue
                    edge_cost = 1
                else:
                    edge_cost = 1
                new_cost = cost + edge_cost
                if new_cost < best.get(neighbor, 10**9):
                    best[neighbor] = new_cost
                    heapq.heappush(
                        queue,
                        (new_cost, self.node_tie_rank.get(neighbor, 0), neighbor, path + [(neighbor, road_id)]),
                    )
        return []

    def path_action_cost(
        self,
        path: list[tuple[str, str]],
        char: CharacterState,
    ) -> int:
        """Beräkna ungefärlig handlingskostnad för en redan vald väg."""
        cost = 0
        for _, road_id in path:
            state = self.get_connection_state(road_id)
            if state == "blocked":
                if char.tools <= 0:
                    return 10**9
                cost += 2
            else:
                cost += 1
        return cost

    def adaptive_hidden_allowed(
        self,
        start: str,
        target: str,
        char: CharacterState,
    ) -> bool:
        """Välj dold väg endast när den ger tillräcklig tidsvinst.

        Okända dolda vägar behandlas som möjliga men riskfyllda. Agentprofilen
        styr minsta besparing i handlingar och en valfri riskpremie.
        """
        if not self.params.get("adaptive_hidden_shortcuts", False):
            return bool(self.params.get("use_hidden_shortcuts", False))

        safe_path = self.shortest_path(start, {target}, False, char)
        risky_path = self.shortest_path(start, {target}, True, char)
        if not risky_path:
            return False
        if not safe_path:
            return True

        safe_cost = self.path_action_cost(safe_path, char)
        risky_cost = self.path_action_cost(risky_path, char)
        hidden_edges = sum(
            self.get_connection_state(road_id) == "hidden"
            for _, road_id in risky_path
        )
        risk_penalty = int(self.params.get("hidden_shortcut_risk_penalty", 0))
        effective_risky_cost = risky_cost + hidden_edges * risk_penalty
        min_savings = int(self.params.get("hidden_shortcut_min_savings", 2))
        return safe_cost - effective_risky_cost >= min_savings

    def nearest_unexplored(self, char: CharacterState) -> str | None:
        candidates = set(self.scenario["setup"]["location_slots"]) - self.revealed_locations
        if not candidates:
            return None
        ranked: list[tuple[int, str]] = []
        for target in candidates:
            allow_hidden = self.adaptive_hidden_allowed(
                char.location, target, char
            )
            path = self.shortest_path(char.location, {target}, allow_hidden, char)
            if target == char.location:
                distance = 0
            elif path:
                distance = self.path_action_cost(path, char)
            else:
                fallback = self.shortest_path(char.location, {target}, False, char)
                if not fallback:
                    continue
                distance = self.path_action_cost(fallback, char) + 3
            ranked.append((distance, target))
        if not ranked:
            return None
        ranked.sort()
        return ranked[0][1]

    def draw_travel(self) -> dict[str, Any]:
        if not self.travel_deck:
            self.travel_deck = self.travel_discard
            self.travel_discard = []
            self.rng.shuffle(self.travel_deck)
        card = self.travel_deck.pop()
        self.travel_discard.append(card)
        return card

    def apply_damage(self, char: CharacterState, amount: int, travel: bool = False) -> None:
        if travel and char.id == "climber" and not char.climber_used:
            char.climber_used = True
            return
        char.damage = min(char.health_max, char.damage + amount)

    def resolve_travel_event(self, char: CharacterState) -> None:
        self.metrics["travel_events"] += 1
        card = self.draw_travel()

        # Klätterrep är frivillig utrustning utan handlingskostnad. Simulatoragenten
        # använder det när den aktuella färdhändelsen har en negativ effekt.
        if "climbing_rope" in char.equipment and card.get("effect"):
            harmful = any(
                effect.get("action") in {
                    "damage", "lose_endurance", "lose_carried_content",
                    "lose_resource", "close_connection"
                }
                for effect in card["effect"]
            )
            if harmful:
                self.consume_equipment(char, "climbing_rope")
                return

        for effect in card["effect"]:
            if self.defeat():
                break
            action = effect["action"]
            if action == "damage":
                self.apply_damage(char, effect["amount"], travel=True)
            elif action == "lose_endurance":
                amount = effect["amount"]
                if "water_reserve" in char.equipment and amount > 0:
                    amount = max(0, amount - 1)
                    self.consume_equipment(char, "water_reserve")
                    self.metrics["water_reserve_prevented"] += 1
                self.endurance -= amount
            elif action == "lose_carried_content":
                if char.equipment:
                    lost = self.rng.choice(char.equipment)
                    char.equipment.remove(lost)
                    self.ground_equipment[char.location].append(lost)
                    self.metrics["items_dropped"] += 1
                elif char.tools:
                    char.tools -= 1
                    self.ground_tools[char.location] += 1
                    self.metrics["items_dropped"] += 1
            elif action == "next_move_cost":
                char.next_move_cost = effect["amount"]

    def move_action(self, char: CharacterState, target: str) -> int:
        allow_hidden = self.adaptive_hidden_allowed(
            char.location, target, char
        )
        path = self.shortest_path(char.location, {target}, allow_hidden, char)
        if allow_hidden and any(
            self.get_connection_state(road_id) == "hidden"
            for _, road_id in path
        ):
            self.metrics["adaptive_hidden_choices"] += 1
        if not path:
            path = self.shortest_path(char.location, {target}, False, char)
        if not path:
            return 0

        neighbor, road_id = path[0]
        state = self.road_state.get(road_id, "open")

        if state == "blocked":
            if char.tools <= 0:
                return 0
            char.tools -= 1
            self.metrics["tools_spent"] += 1
            self.set_connection_state(road_id, "open")
            self.actions["unlock_road"] += 1
            if char.id != "engineer":
                return 1
            state = "open"

        move_cost = char.next_move_cost
        if move_cost > 1:
            if not self.can_pay_actions(move_cost):
                return 0
            char.next_move_cost = 1
            self.actions["move"] += 1
            return move_cost

        self.actions["move"] += 1
        if state == "hidden":
            self.metrics["hidden_roads_tested"] += 1
            result = self.road_marker[road_id]
            if result == "blocked":
                self.set_connection_state(road_id, "blocked")
                self.metrics["blocked_roads_found"] += 1
                return 1
            if result == "travel_event":
                self.set_connection_state(road_id, "open")
                self.resolve_travel_event(char)
                if char.active:
                    char.location = neighbor
                return 1
            self.set_connection_state(road_id, "open")

        char.location = neighbor
        connection = self.connections.get(road_id, {})
        if connection.get("category") == "scenario":
            self.connection_uses[road_id] += 1
        return 1

    def take_tool(self, char: CharacterState) -> bool:
        if char.location != self.supply or self.supply_tools <= 0:
            return False
        if not self.can_fit(char, 1):
            self.metrics["capacity_failures"] += 1
            return False
        char.tools += 1
        self.supply_tools -= 1
        self.metrics["tools_taken"] += 1
        self.actions["take_tool"] += 1
        return True

    def draw_equipment(self, char: CharacterState) -> None:
        if not self.equipment_deck:
            return
        equipment = self.equipment_deck.pop()
        self.metrics["equipment_drawn"] += 1
        slots = equipment["slots"]
        if self.can_fit(char, slots):
            char.equipment.append(equipment["id"])
            return
        self.metrics["capacity_failures"] += 1
        self.ground_equipment[char.location].append(equipment["id"])

    def draw_objective(self, char: CharacterState) -> None:
        if not self.objective_deck:
            return
        objective = self.objective_deck.pop()
        self.objectives_found += 1
        self.process_scenario_event_milestones(
            "objective_found", objective_id=objective["id"]
        )
        if not self.drop_for_space(char, objective["slots"]):
            self.metrics["capacity_failures"] += 1
            self.ground_objectives[char.location].append(objective["id"])
            return
        char.objectives.append(objective["id"])

    def explore(self, char: CharacterState) -> bool:
        if char.location not in self.location_assignment:
            return False
        if char.location in self.revealed_locations:
            return False
        self.revealed_locations.add(char.location)
        self.actions["explore"] += 1
        card = self.location_assignment[char.location]
        for effect in card["on_reveal"]:
            if self.defeat():
                break
            action = effect["action"]
            if action in {"increase_track", "lose_endurance"}:
                self.endurance -= effect["amount"]
            elif action == "damage":
                self.apply_damage(char, effect["amount"])
            elif action == "heal":
                char.damage = max(0, char.damage - effect["amount"])
            elif action == "choice_pay_or_damage":
                choice = self.choose_pay_tool_or_damage(char, effect["damage"])
                self.metrics[f"choice_pay_or_damage_{choice}"] += 1
                if choice == "tool":
                    char.tools -= 1
                    self.metrics["tools_spent"] += 1
                else:
                    self.apply_damage(char, effect["damage"])
            elif action == "draw_objective_card":
                self.draw_objective(char)
            elif action == "draw_equipment_card":
                self.draw_equipment(char)
            elif action == "mark_repair_site":
                self.repair_sites.add(char.location)
        self.process_progression_event("location_explored", location_id=char.location)
        self.process_scenario_event_milestones("location_explored", location_id=char.location)
        return True

    def pickup_ground(self, char: CharacterState) -> bool:
        if self.ground_objectives[char.location]:
            objective_id = self.ground_objectives[char.location][-1]
            slots = self.objective_slots(objective_id)
            if self.drop_for_space(char, slots):
                char.objectives.append(self.ground_objectives[char.location].pop())
                self.actions["pickup"] += 1
                return True
            self.metrics["capacity_failures"] += 1
        if self.ground_equipment[char.location]:
            equipment_id = self.ground_equipment[char.location][-1]
            slots = self.equipment_by_id[equipment_id]["slots"]
            if self.can_fit(char, slots):
                char.equipment.append(self.ground_equipment[char.location].pop())
                self.actions["pickup"] += 1
                return True
        if self.ground_tools[char.location] and self.can_fit(char, 1):
            self.ground_tools[char.location] -= 1
            char.tools += 1
            self.actions["pickup"] += 1
            return True
        return False

    def _trigger_matches(
        self,
        trigger: dict[str, Any],
        event: str,
        *,
        objective_id: str | None = None,
        location_id: str | None = None,
    ) -> bool:
        if trigger.get("event") != event:
            return False
        if "count" in trigger:
            if event == "objective_found":
                current_count = self.objectives_found
            elif event in {"objective_completed", "objective_activated"}:
                current_count = self.mission_progress()
            else:
                current_count = self.metrics.get(f"event_count:{event}", 0)
            if current_count < trigger["count"]:
                return False
        if "objective_id" in trigger and trigger["objective_id"] != objective_id:
            return False
        if "location_id" in trigger and trigger["location_id"] != location_id:
            return False
        return True

    def _valid_choice_connections(self, effect: dict[str, Any]) -> list[str]:
        candidates = effect.get("from", [])
        return [
            connection_id
            for connection_id in candidates
            if connection_id in self.connection_states
            and self.get_connection_state(connection_id) == "closed"
        ]

    def resolve_connection_choice(
        self,
        candidates: list[str],
        choose: int = 1,
    ) -> list[str]:
        """Välj de förbindelser som ger störst aktuell minskning av resavstånd.

        Bedömningen använder publik runtime-information: karaktärernas positioner,
        kända mål på marken, outforskade platser och uppdragsdestinationer.
        Dolda kort eller vägbrickor avslöjas inte.
        """
        if choose <= 0:
            return []
        targets = set(self.scenario["setup"]["location_slots"]) - self.revealed_locations
        targets.update(loc for loc, cards in self.ground_objectives.items() if cards)
        if self.mission_type == "deliver_items":
            targets.add(self.base)
        else:
            targets.update(self.repair_sites - self.repaired_sites)
        origins = [char.location for char in self.characters if char.active]
        if not targets or not origins:
            return candidates[:choose]

        def total_distance() -> int:
            total = 0
            probe = self.characters[0]
            for origin in origins:
                path = self.shortest_path(origin, targets, False, probe)
                total += len(path) if path or origin in targets else 999
            return total

        baseline = total_distance()
        scored = []
        for connection_id in candidates:
            original = self.connection_states[connection_id]
            self.connection_states[connection_id] = "open"
            score = baseline - total_distance()
            self.connection_states[connection_id] = original
            scored.append((score, connection_id))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [connection_id for _, connection_id in scored[:choose]]

    def _apply_progression_effect(self, effect: dict[str, Any]) -> list[str]:
        action = effect["action"]
        changed: list[str] = []
        if action == "open_connection":
            connection_id = effect["connection_id"]
            if self.open_connection(connection_id):
                changed.append(connection_id)
        elif action == "seal_connection":
            connection_id = effect["connection_id"]
            if self.seal_connection(connection_id):
                changed.append(connection_id)
        elif action == "close_connection":
            connection_id = effect["connection_id"]
            if self.close_connection(connection_id):
                changed.append(connection_id)
        elif action == "modify_endurance":
            amount = int(effect.get("amount", 0))
            maximum = self.scenario["setup"]["endurance_by_character_count"][
                str(self.sim_data["characters_per_game"])
            ]
            self.endurance = max(0, min(maximum, self.endurance + amount))
            self.metrics["scenario_event_endurance_delta"] += amount
        elif action == "choose_connection":
            choose = effect.get("choose", 1)
            candidates = self._valid_choice_connections(effect)
            for connection_id in self.resolve_connection_choice(candidates, choose):
                if self.open_connection(connection_id):
                    changed.append(connection_id)
        else:
            raise ValueError(f"Okänd progressionseffekt: {action}")
        return changed

    def process_scenario_event_milestones(
        self,
        event: str,
        *,
        objective_id: str | None = None,
        location_id: str | None = None,
    ) -> list[str]:
        if not self.scenario_events_enabled:
            return []
        changed: list[str] = []
        for milestone in self.scenario_event_milestones:
            milestone_id = milestone["id"]
            if milestone_id in self.fired_scenario_event_milestones:
                continue
            if not self._trigger_matches(
                milestone["trigger"], event, objective_id=objective_id, location_id=location_id
            ):
                continue
            card_id = milestone["resolve"]["card_id"]
            card = self.scenario_event_cards.get(card_id)
            if card is None:
                raise ValueError(f"Okänt scenariohändelsekort: {card_id}")
            card_changes: list[str] = []
            opened_connections: list[str] = []
            closed_connections: list[str] = []
            endurance_before = self.endurance
            for effect in card.get("effects", []):
                if self.defeat():
                    break
                action = effect["action"]
                effect_changes = self._apply_progression_effect(effect)
                card_changes.extend(effect_changes)
                if action == "open_connection":
                    opened_connections.extend(effect_changes)
                elif action == "close_connection":
                    closed_connections.extend(effect_changes)
            endurance_delta = self.endurance - endurance_before
            self.fired_scenario_event_milestones.add(milestone_id)
            log_entry = {
                "milestone_id": milestone_id,
                "card_id": card_id,
                "trigger_event": event,
                "objective_id": objective_id,
                "location_id": location_id,
                "round": self.round,
                "changed_connections": card_changes,
                "opened_connections": opened_connections,
                "closed_connections": closed_connections,
                "endurance_delta": endurance_delta,
                "public": milestone.get("public", False),
            }
            self.scenario_event_log.append(log_entry)
            self.metrics["scenario_events_resolved"] += 1
            changed.extend(card_changes)
        return changed

    def process_progression_event(
        self,
        event: str,
        *,
        objective_id: str | None = None,
        location_id: str | None = None,
    ) -> list[str]:
        opened_or_changed: list[str] = []
        for definition in self.progression_events:
            event_id = definition["id"]
            if event_id in self.fired_progression_events:
                continue
            if not self._trigger_matches(
                definition["trigger"],
                event,
                objective_id=objective_id,
                location_id=location_id,
            ):
                continue
            changed: list[str] = []
            for effect in definition.get("effects", []):
                changed.extend(self._apply_progression_effect(effect))
            self.fired_progression_events.add(event_id)
            self.progression_log.append({
                "event_id": event_id,
                "trigger_event": event,
                "objective_id": objective_id,
                "location_id": location_id,
                "round": self.round,
                "changed_connections": changed,
                "narrative": definition.get("narrative", ""),
            })
            self.metrics["progression_events_fired"] += 1
            opened_or_changed.extend(changed)
        return opened_or_changed

    def process_all_objectives_completed_if_needed(self) -> None:
        if self.mission_progress() < self.mission_completion.get("required", 0):
            return
        self.process_progression_event("all_objectives_completed")
        self.process_scenario_event_milestones("all_objectives_completed")

    def emit_custom_event(self, event_id: str) -> list[str]:
        return self.process_progression_event(
            "custom_event",
            objective_id=event_id,
        )

    def deposit_objectives(self, char: CharacterState) -> None:
        if (
            self.mission_type == "deliver_items"
            and char.location == self.mission_completion["destination_location"]
            and char.objectives
        ):
            delivered = list(char.objectives)
            self.objectives_at_base.extend(delivered)
            char.objectives.clear()
            for objective_id in delivered:
                self.completed_objective_ids.add(objective_id)
                self.process_progression_event(
                    "objective_completed",
                    objective_id=objective_id,
                )
                self.process_scenario_event_milestones(
                    "objective_completed",
                    objective_id=objective_id,
                )
                self.process_all_objectives_completed_if_needed()

    def install_module(self, char: CharacterState) -> int | None:
        if (
            self.mission_type == "place_items_at_tagged_locations"
            and char.location in self.repair_sites
            and char.location not in self.repaired_sites
            and char.objectives
        ):
            diagnostic_available = "diagnostic_tool" in char.equipment
            cost = 0 if diagnostic_available else 1
            if not self.can_pay_actions(cost):
                return None

            completed_objective_id = char.objectives[-1]
            if diagnostic_available:
                self.consume_equipment(char, "diagnostic_tool")
                self.metrics["diagnostic_tool_triggered"] += 1
            if self.mission_completion.get("consume_item", True):
                char.objectives.pop()
            self.repaired_sites.add(char.location)
            self.completed_objective_ids.add(completed_objective_id)
            self.actions[self.mission_completion["action_id"]] += 1
            self.process_progression_event(
                "objective_completed",
                objective_id=completed_objective_id,
            )
            self.process_scenario_event_milestones(
                "objective_completed",
                objective_id=completed_objective_id,
            )
            self.process_progression_event(
                "objective_activated",
                objective_id=completed_objective_id,
            )
            self.process_scenario_event_milestones(
                "objective_activated",
                objective_id=completed_objective_id,
            )
            self.process_all_objectives_completed_if_needed()
            return cost
        return None

    def equipment_action_cost(self, char: CharacterState, equipment_id: str) -> int:
        card = self.equipment_by_id[equipment_id]
        cost = card.get("use", {}).get("cost_actions", 0)
        if (
            cost == 1
            and card.get("kind") == "consumable"
            and char.id == "technician"
            and char.technician_use_round != self.round
        ):
            return 0
        return cost

    def consume_equipment(self, char: CharacterState, equipment_id: str) -> None:
        card = self.equipment_by_id[equipment_id]
        if card.get("use", {}).get("discard_after_use", False):
            char.equipment.remove(equipment_id)
        self.metrics["equipment_used"] += 1
        self.actions["use_equipment"] += 1

    def use_equipment(self, char: CharacterState) -> int | None:
        candidates = list(char.equipment)
        for equipment_id in candidates:
            card = self.equipment_by_id[equipment_id]
            use = card.get("use")
            if not use:
                continue
            timing = use.get("timing", "during_activation")
            if timing != "during_activation":
                continue

            cost = self.equipment_action_cost(char, equipment_id)
            if not self.can_pay_actions(cost):
                continue

            effects = use.get("effect", [])
            should_use = False
            for effect in effects:
                action = effect["action"]
                if action == "heal":
                    targets = [
                        target for target in self.characters
                        if target.active and target.location == char.location and target.damage > 0
                    ]
                    if targets:
                        target = max(targets, key=lambda item: item.damage)
                        amount = effect["amount"] + (1 if char.id == "medic" else 0)
                        target.damage = max(0, target.damage - amount)
                        self.metrics["medical_kit_other_target"] += int(target is not char)
                        should_use = True
                elif action == "gain_endurance" and self.endurance <= 7:
                    maximum = self.scenario["setup"]["endurance_by_character_count"][
                        str(self.sim_data["characters_per_game"])
                    ]
                    self.endurance = min(maximum, self.endurance + effect["amount"])
                    should_use = True
                elif action == "peek_hidden_roads":
                    hidden = [
                        road_id for road_id, state in self.road_state.items()
                        if state == "hidden" and road_id not in self.known_hidden_roads
                    ]
                    if hidden:
                        self.peek_roads(hidden[: effect.get("amount", 1)])
                        should_use = True
            if should_use:
                base_cost = card.get("use", {}).get("cost_actions", 0)
                if (
                    cost == 0
                    and base_cost == 1
                    and char.id == "technician"
                    and char.technician_use_round != self.round
                ):
                    char.technician_use_round = self.round
                    self.metrics["technician_free_uses"] += 1
                self.consume_equipment(char, equipment_id)
                return cost
        return None

    def objective_destination(self, char: CharacterState) -> str | None:
        if self.mission_type == "deliver_items":
            return self.mission_completion["destination_location"]
        candidates = self.repair_sites - self.repaired_sites
        ranked = []
        for location in candidates:
            path = self.shortest_path(
                char.location,
                {location},
                bool(self.params.get("use_hidden_shortcuts", False)),
                char,
            )
            if path or location == char.location:
                ranked.append((len(path), location))
        return min(ranked)[1] if ranked else None

    def distance_to(self, char: CharacterState, destination: str | None) -> int:
        if destination is None:
            return 10_000
        if char.location == destination:
            return 0
        path = self.shortest_path(
            char.location,
            {destination},
            bool(self.params.get("use_hidden_shortcuts", False)),
            char,
        )
        return len(path) if path else 10_000

    def carrier_score(self, char: CharacterState) -> int:
        """Stabil värdering av vem som är bäst lämpad att bära målobjekt."""
        role_bonus = {
            "carrier": 3,
            "courier": 1,
        }.get(char.id, 0)
        return char.capacity_base + role_bonus

    def recently_reversed_transfer(
        self,
        kind: str,
        item_id: str,
        giver: CharacterState,
        receiver: CharacterState,
    ) -> bool:
        previous = self.last_item_transfer.get((kind, item_id))
        if previous is None:
            return False
        previous_round, previous_giver, previous_receiver = previous
        return (
            previous_round >= self.round - 1
            and previous_giver == receiver.id
            and previous_receiver == giver.id
        )

    def record_transfer(
        self,
        kind: str,
        item_id: str,
        giver: CharacterState,
        receiver: CharacterState,
        reason: str,
    ) -> None:
        self.last_item_transfer[(kind, item_id)] = (
            self.round,
            giver.id,
            receiver.id,
        )
        self.transfer_log.append(
            {
                "round": self.round,
                "activation": self.activation_serial,
                "kind": kind,
                "item_id": item_id,
                "giver": giver.id,
                "receiver": receiver.id,
                "reason": reason,
            }
        )
        self.metrics[f"transfer_reason_{reason}"] += 1

    def transfer_if_useful(self, char: CharacterState) -> int | None:
        """Gör bara överföringar med en tydlig logistisk förbättring."""
        if self.activation_serial in self.transfer_used_activations:
            return None

        others = [
            other
            for other in self.characters
            if other is not char
            and other.active
            and other.location == char.location
        ]
        if not others:
            return None

        free_transfer = (
            char.id == "courier"
            and char.courier_transfer_activation != self.activation_serial
        )
        cost = 0 if free_transfer else 1
        if not self.can_pay_actions(cost):
            return None

        moves: list[tuple[str, str, CharacterState, str]] = []

        # Målobjekt överförs endast till en karaktär som är strikt närmare
        # destinationen. Detta förhindrar kapacitetsbaserad ping-pong.
        for objective_id in list(char.objectives):
            destination = self.objective_destination(char)
            giver_distance = self.distance_to(char, destination)
            candidates = []
            for receiver in others:
                slots = self.objective_slots(objective_id)
                if not self.can_fit(receiver, slots):
                    continue
                if self.recently_reversed_transfer(
                    "objective", objective_id, char, receiver
                ):
                    continue
                receiver_distance = self.distance_to(receiver, destination)
                closer = receiver_distance < giver_distance
                better_carrier = (
                    receiver_distance == giver_distance
                    and self.carrier_score(receiver) >= self.carrier_score(char) + 2
                )
                if closer or better_carrier:
                    candidates.append(
                        (
                            receiver_distance,
                            -self.carrier_score(receiver),
                            receiver,
                            "closer_to_destination" if closer else "better_carrier",
                        )
                    )
            if candidates:
                _, _, receiver, reason = min(
                    candidates,
                    key=lambda value: (value[0], value[1], value[2].id),
                )
                moves.append(("objective", objective_id, receiver, reason))
                if not free_transfer:
                    break

        # Verktyg flyttas bara från ett tydligt överskott till en karaktär
        # som bär målobjekt och saknar verktyg. Agenten flyttar aldrig sista
        # verktyget utan detta konkreta behov.
        if free_transfer or not moves:
            tool_target = int(self.params.get("collect_tools_target", 1))
            if char.tools > tool_target:
                candidates = [
                    receiver
                    for receiver in others
                    if receiver.objectives
                    and receiver.tools < tool_target
                    and self.can_fit(receiver, 1)
                    and not self.recently_reversed_transfer(
                        "tool", "tool", char, receiver
                    )
                ]
                if candidates:
                    receiver = min(
                        candidates,
                        key=lambda item: self.free_capacity(item),
                        default=None,
                    )
                    if receiver is not None:
                        moves.append(("tool", "tool", receiver, "objective_carrier_need"))

        # Medicinväska flyttas bara till en skadad lagkamrat om bäraren själv
        # inte behöver den. Övrig utrustning behålls av sin nuvarande bärare.
        if free_transfer or not moves:
            if "medical_kit" in char.equipment and char.damage == 0:
                candidates = [
                    receiver
                    for receiver in others
                    if receiver.damage > 0
                    and self.can_fit(
                        receiver,
                        self.equipment_by_id["medical_kit"]["slots"],
                    )
                    and not self.recently_reversed_transfer(
                        "equipment", "medical_kit", char, receiver
                    )
                ]
                if candidates:
                    receiver = max(candidates, key=lambda item: item.damage)
                    moves.append(
                        ("equipment", "medical_kit", receiver, "healing_need")
                    )

        if not moves:
            return None

        transferred = 0
        for kind, item_id, receiver, reason in moves:
            if kind == "objective":
                char.objectives.remove(item_id)
                receiver.objectives.append(item_id)
            elif kind == "tool":
                char.tools -= 1
                receiver.tools += 1
            elif kind == "equipment":
                char.equipment.remove(item_id)
                receiver.equipment.append(item_id)
            else:
                continue
            self.record_transfer(kind, item_id, char, receiver, reason)
            transferred += 1
            if not free_transfer:
                break

        if not transferred:
            return None

        self.transfer_used_activations.add(self.activation_serial)
        self.metrics["transfers"] += transferred
        self.actions["transfer"] += 1
        if free_transfer:
            char.courier_transfer_activation = self.activation_serial
            self.metrics["courier_free_transfers"] += 1
        return cost

    def target_for(self, char: CharacterState) -> str:
        if char.objectives and self.mission_type == "place_items_at_tagged_locations":
            candidates = self.repair_sites - self.repaired_sites
            if candidates:
                ranked = []
                for loc in candidates:
                    path = self.shortest_path(char.location, {loc}, bool(self.params.get("use_hidden_shortcuts", False)), char)
                    if path or loc == char.location:
                        ranked.append((len(path), loc))
                if ranked:
                    return min(ranked)[1]
        if char.objectives:
            return self.base

        ground_targets = {
            location for location, cards in self.ground_objectives.items() if cards
        }
        if self.objectives_found >= self.objective_data["deck"]["required_for_victory"]:
            if ground_targets:
                path_lengths = []
                for loc in ground_targets:
                    path = self.shortest_path(
                        char.location, {loc},
                        bool(self.params.get("use_hidden_shortcuts", False)), char
                    )
                    if path or loc == char.location:
                        path_lengths.append((len(path), loc))
                if path_lengths:
                    return min(path_lengths)[1]
            return self.base

        unknown = self.nearest_unexplored(char)
        if unknown:
            return unknown
        return self.base

    def random_action(self, char: CharacterState) -> int:
        legal: list[str] = ["move"]
        if self.mission_type == "place_items_at_tagged_locations" and char.objectives and char.location in self.repair_sites and char.location not in self.repaired_sites:
            legal.append("install")
        if char.location in self.location_assignment and char.location not in self.revealed_locations:
            legal.append("explore")
        if char.location == self.supply and self.supply_tools and self.can_fit(char, 1):
            legal.append("tool")
        if char.location == self.base and char.damage:
            legal.append("heal")
        if (
            self.ground_objectives[char.location]
            or self.ground_equipment[char.location]
            or self.ground_tools[char.location]
        ):
            legal.append("pickup")
        action = self.rng.choice(legal)
        if action == "install":
            cost = self.install_module(char)
            return 0 if cost is None else cost
        if action == "explore":
            return 1 if self.explore(char) else 0
        if action == "tool":
            return 1 if self.take_tool(char) else 0
        if action == "heal":
            char.damage = max(0, char.damage - 1)
            self.actions["recover"] += 1
            return 1
        if action == "pickup":
            return 1 if self.pickup_ground(char) else 0

        neighbors = [
            (neighbor, road_id)
            for neighbor, road_id in self.open_adjacency[char.location]
            if self.is_connection_traversable(road_id)
        ]
        if not neighbors:
            return 0
        neighbor, _ = self.rng.choice(neighbors)
        return self.move_action(char, neighbor)

    def strategic_action(self, char: CharacterState) -> int:
        self.deposit_objectives(char)
        install_cost = self.install_module(char)
        if install_cost is not None:
            return install_cost
        transfer_cost = self.transfer_if_useful(char)
        if transfer_cost is not None:
            return transfer_cost
        if self.pickup_ground(char):
            return 1
        equipment_cost = self.use_equipment(char)
        if equipment_cost is not None:
            return equipment_cost

        heal_threshold = self.params.get("heal_at_health", 1)
        if char.health_remaining <= heal_threshold:
            if char.location == self.base:
                char.damage = max(0, char.damage - 1)
                self.actions["recover"] += 1
                return 1
            return self.move_action(char, self.base)

        tool_target = self.params.get("collect_tools_target", 1)
        if (
            char.tools < tool_target
            and self.supply_tools > 0
            and self.objectives_found < 3
        ):
            if char.location == self.supply:
                if self.take_tool(char):
                    return 1
            elif char.location == self.base or self.round <= 2:
                spent = self.move_action(char, self.supply)
                if spent:
                    return spent

        if char.location in self.location_assignment and char.location not in self.revealed_locations:
            return 1 if self.explore(char) else 0

        target = self.target_for(char)
        if target == char.location:
            if self.pickup_ground(char):
                return 1
            return 0
        return self.move_action(char, target)

    def activate(self, char: CharacterState) -> None:
        if not char.active or self.defeat():
            return
        self.activation_serial += 1
        self.use_scout_ability(char)
        actions_remaining = self.actions_per_activation
        self.current_actions_remaining = actions_remaining
        safety = 0
        while (
            actions_remaining > 0
            and char.active
            and not self.defeat()
            and safety < 8
        ):
            safety += 1
            self.current_actions_remaining = actions_remaining
            if self.strategy["id"] == "random" or (
                self.rng.random() < self.params.get("random_action_probability", 0)
            ):
                cost = self.random_action(char)
            else:
                cost = self.strategic_action(char)
            if cost is None or cost < 0:
                break
            if cost > actions_remaining:
                raise AssertionError(
                    f"Simulatorn försökte betala {cost} handlingar med "
                    f"{actions_remaining} kvar."
                )
            if cost == 0:
                self.deposit_objectives(char)
                if self.defeat():
                    break
                continue
            actions_remaining -= cost
            self.current_actions_remaining = actions_remaining
            self.deposit_objectives(char)
            if self.defeat():
                break
        self.current_actions_remaining = 0

    def mission_progress(self) -> int:
        if self.mission_type == "place_items_at_tagged_locations":
            return len(self.repaired_sites)
        return len(self.objectives_at_base)

    def victory(self) -> bool:
        completed = self.mission_progress()
        return completed >= self.mission_completion["required"] and any(c.active for c in self.characters)

    def defeat(self) -> bool:
        return self.endurance <= self.scenario["defeat"]["endurance_reaches"] or not any(
            c.active for c in self.characters
        )

    def run(self) -> GameResult:
        result = "loss"
        while self.round <= self.maximum_rounds:
            # Player phase: fixed order.
            for char in self.characters:
                self.activate(char)
                if self.defeat():
                    self.end_reason = "all_incapacitated" if self.endurance > 0 else "endurance"
                    break
                if self.victory():
                    result = "win"
                    self.end_reason = "mission_completed"
                    break
            if result == "win" or self.defeat():
                break

            # Underhåll följt av uthållighetsförlust i rundslutet.
            if self.victory():
                result = "win"
                self.end_reason = "mission_completed"
                break

            self.endurance -= self.scenario["endurance_phase"]["loss_each_round"]

            if self.defeat():
                self.end_reason = "endurance" if self.endurance <= 0 else "all_incapacitated"
                break
            self.round += 1

        if not self.end_reason:
            self.end_reason = "maximum_rounds"

        return GameResult(
            strategy=self.strategy["id"],
            seed=self.seed,
            result=result,
            rounds=self.round,
            final_endurance=self.endurance,
            objectives_found=self.objectives_found,
            objectives_returned=self.mission_progress(),
            total_damage=sum(c.damage for c in self.characters),
            incapacitations=sum(not c.active for c in self.characters),
            hidden_roads_tested=self.metrics["hidden_roads_tested"],
            adaptive_hidden_choices=self.metrics["adaptive_hidden_choices"],
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
            connection_uses=dict(self.connection_uses),
            connection_open_rounds=dict(self.connection_open_rounds),
            progression_events_fired=self.metrics["progression_events_fired"],
            scenario_events_resolved=self.metrics["scenario_events_resolved"],
            scenario_event_cards=[entry["card_id"] for entry in self.scenario_event_log],
            scenario_event_rounds=[entry["round"] for entry in self.scenario_event_log],
            scenario_event_endurance_delta=sum(
                entry.get("endurance_delta", 0) for entry in self.scenario_event_log
            ),
            connections_closed_by_events=[
                connection_id
                for entry in self.scenario_event_log
                for connection_id in entry.get("closed_connections", [])
            ],
            connections_opened_by_events=[
                connection_id
                for entry in self.scenario_event_log
                for connection_id in entry.get("opened_connections", [])
            ],
            scenario_event_log=list(self.scenario_event_log),
        )


def aggregate(results: list[GameResult], strategy_meta: dict[str, Any]) -> dict[str, Any]:
    wins = [r for r in results if r.result == "win"]
    metric_names = [
        "rounds", "final_endurance", "objectives_found", "objectives_returned",
        "total_damage", "incapacitations", "hidden_roads_tested",
        "adaptive_hidden_choices",
        "blocked_roads_found", "travel_events", "tools_taken", "tools_spent",
        "capacity_failures", "items_dropped", "transfers",
        "equipment_drawn", "equipment_used", "scenario_events_resolved",
        "scenario_event_endurance_delta",
    ]
    summary: dict[str, Any] = {
        "strategy": strategy_meta["id"],
        "name": strategy_meta["name"],
        "runs": len(results),
        "wins": len(wins),
        "win_rate": len(wins) / len(results) if results else 0,
        "end_reasons": dict(Counter(r.end_reason for r in results)),
        "character_pairs": dict(Counter("+".join(r.characters) for r in results)),
    }
    for metric in metric_names:
        values = [getattr(r, metric) for r in results]
        summary[f"mean_{metric}"] = statistics.fmean(values) if values else 0
    summary["mean_win_rounds"] = (
        statistics.fmean(r.rounds for r in wins) if wins else None
    )
    actions: Counter[str] = Counter()
    for result in results:
        actions.update(result.action_counts)
    summary["mean_actions"] = {
        action: count / len(results) for action, count in sorted(actions.items())
    }
    return summary


def write_reports(
    root: Path,
    config: dict[str, Any],
    summaries: list[dict[str, Any]],
    raw_results: list[GameResult],
) -> None:
    out_dir = root / config["simulation"]["output_directory"]
    out_dir.mkdir(parents=True, exist_ok=True)

    json_data = {
        "status": "simulation_hypothesis_not_physical_playtest",
        "scenario": {
            "id": raw_results[0].scenario_id if raw_results else config["simulation"]["scenario_id"],
            "base_profile": raw_results[0].base_profile_id if raw_results else "",
            "location_set": raw_results[0].location_set_id if raw_results else "",
            "objective_set": raw_results[0].objective_set_id if raw_results else "",
        },
        "simulation": config["simulation"],
        "strategies": summaries,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(json_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    columns = [
        "strategy", "name", "runs", "wins", "win_rate", "mean_rounds",
        "mean_win_rounds", "mean_final_endurance", "mean_objectives_found",
        "mean_objectives_returned", "mean_total_damage",
        "mean_hidden_roads_tested", "mean_travel_events", "mean_tools_taken",
        "mean_tools_spent", "mean_capacity_failures", "mean_items_dropped",
        "mean_transfers", "mean_equipment_drawn", "mean_equipment_used",
        "mean_scenario_events_resolved", "mean_scenario_event_endurance_delta",
    ]
    with (out_dir / "strategy-comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for summary in summaries:
            writer.writerow({column: summary.get(column) for column in columns})

    raw_columns = [
        "scenario_id", "base_profile_id", "location_set_id", "objective_set_id",
        "character_count", "starting_endurance", "starting_tools",
        "strategy", "seed", "result", "rounds", "final_endurance",
        "objectives_found", "objectives_returned", "total_damage",
        "incapacitations", "hidden_roads_tested", "blocked_roads_found",
        "travel_events", "tools_taken", "tools_spent", "capacity_failures",
        "items_dropped", "transfers", "equipment_drawn", "equipment_used",
        "scenario_events_resolved", "scenario_event_cards", "scenario_event_rounds",
        "scenario_event_endurance_delta", "connections_closed_by_events",
        "connections_opened_by_events", "scenario_event_log",
        "characters", "end_reason",
    ]
    with (out_dir / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=raw_columns)
        writer.writeheader()
        for result in raw_results:
            row = {column: getattr(result, column) for column in raw_columns}
            row["characters"] = "+".join(result.characters)
            for field_name in (
                "scenario_event_cards",
                "scenario_event_rounds",
                "connections_closed_by_events",
                "connections_opened_by_events",
                "scenario_event_log",
            ):
                row[field_name] = json.dumps(getattr(result, field_name), ensure_ascii=False, sort_keys=True)
            writer.writerow(row)

    ranked = sorted(summaries, key=lambda s: s["win_rate"], reverse=True)
    lines = [
        "# Simuleringsrapport",
        "",
        "> Resultaten är designhypoteser från en förenklad agentmodell, inte facit eller fysiska speltest.",
        "",
        f"- Körningar per strategi: **{summaries[0]['runs'] if summaries else 0}**",
        f"- Strategier: **{len(summaries)}**",
        f"- Grundseed: `{config['simulation']['base_seed']}`",
        "",
        "## Strategijämförelse",
        "",
        "| Strategi | Vinst | Rundor | Uthållighet | Mål hem | Kapacitetsproblem | Genvägar testade |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for s in ranked:
        lines.append(
            f"| {s['name']} | {s['win_rate']:.1%} | "
            f"{s['mean_rounds']:.2f} | {s['mean_final_endurance']:.2f} | "
            f"{s['mean_objectives_returned']:.2f} | "
            f"{s['mean_capacity_failures']:.2f} | "
            f"{s['mean_hidden_roads_tested']:.2f} |"
        )

    lines += [
        "",
        "## Tolkning",
        "",
    ]
    if ranked:
        best = ranked[0]
        random_summary = next((s for s in summaries if s["strategy"] == "random"), None)
        lines.append(
            f"- Högst observerad vinstgrad: **{best['name']} ({best['win_rate']:.1%})**."
        )
        if random_summary:
            lines.append(
                f"- Slumpmässig baslinje vann **{random_summary['win_rate']:.1%}**."
            )
        if best["win_rate"] < 0.25:
            lines.append(
                "- Även bästa agenten vinner sällan; spelet kan vara strukturellt för svårt eller agenten för svag."
            )
        elif best["win_rate"] > 0.85:
            lines.append(
                "- Bästa agenten vinner mycket ofta; spelet kan vara för lätt för systematiskt spel."
            )
        else:
            lines.append(
                "- Bästa agentens vinstgrad ligger i ett användbart intervall för fortsatt fysisk prövning."
            )

    lines += [
        "",
        "## Simulatorns förenklingar",
        "",
        "- Två karaktärer används i varje omgång.",
        "- Karaktärsurval följer strategins prioriteringslista.",
        "- Beslut tas omedelbart med perfekt regelkunskap.",
        "- Mål lämnas automatiskt i Baslägret vid ankomst.",
        "- Överföring simuleras främst av den logistiska strategin.",
        "- Vissa förmågor approximeras eller lämnas utan aktiv användning.",
        "- Mänsklig kommunikation, lästid, glömda regler och komponentfriktion simuleras inte.",
        "",
        "## Rekommenderad användning",
        "",
        "Jämför relativa skillnader mellan strategier och leta efter omöjliga eller triviala mönster. "
        "Ändra högst ett fåtal värden åt gången och kör om med samma seeds.",
    ]
    (out_dir / "simulation-report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--runs", type=int, help="Körningar per strategi.")
    parser.add_argument("--strategy", action="append", help="Begränsa till strategi-id.")
    parser.add_argument("--seed", type=int, help="Åsidosätt grundseed.")
    parser.add_argument("--scenario", help="Åsidosätt scenario-id.")
    args = parser.parse_args()

    root = args.root.resolve()
    config = load_yaml(root / "data/simulation.yaml")
    sim_cfg = config["simulation"]
    runs = args.runs or sim_cfg["default_runs_per_strategy"]
    base_seed = args.seed if args.seed is not None else sim_cfg["base_seed"]
    selected = set(args.strategy or [s["id"] for s in config["strategies"]])
    strategies = [s for s in config["strategies"] if s["id"] in selected]
    if not strategies:
        raise ValueError("Ingen giltig strategi vald.")

    all_results: list[GameResult] = []
    summaries: list[dict[str, Any]] = []
    for strategy_index, strategy in enumerate(strategies):
        results = []
        for run_index in range(runs):
            seed = base_seed + strategy_index * 1_000_000 + run_index
            result = ExpeditionSimulation(root, strategy, seed, scenario_id=args.scenario).run()
            results.append(result)
        all_results.extend(results)
        summary = aggregate(results, strategy)
        summaries.append(summary)
        print(
            f"{strategy['id']}: {summary['win_rate']:.1%} vinst "
            f"över {runs} körningar"
        )

    write_reports(root, config, summaries, all_results)
    print(f"Rapporter: {sim_cfg['output_directory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
