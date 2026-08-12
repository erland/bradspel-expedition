# Regel-täckningsmatris – Expedition

## Syfte

Matrisen kopplar grundregler och centrala scenarioregler till strukturerade YAML-källor, spelmotor, simulator och automatiska tester. Den visar vad simulatorn faktiskt kan följa och vad som fortfarande kräver fysisk kontroll.

## Statusnyckel

| Status | Betydelse |
|---|---|
| **Full** | Strukturerad källa, motor-/simulatorstöd och relevant automatiskt test finns. |
| **Delvis** | Regeln är implementerad men saknar direkt test eller använder begränsad agentheuristik. |
| **Presentationslager** | Fysisk representation som avsiktligt inte påverkar simulatorstatus. |
| **Ej automatiserad** | Kräver visuell kontroll, fysisk setup eller blindtest. |

## Sammanfattning

- Full täckning: **8**
- Delvis täckning: **21**
- Presentationslager: **1**
- Ej automatiserad: **2**
- Totalt kartlagda regler: **32**

## Viktig slutsats

Simulatorn är synkad med YAML för kärnflödet, dynamiska vägar, målprogression och scenariohändelse. Den är däremot inte en fullständig mänsklig spelarmodell. De största kvarvarande tekniska luckorna är direkta tester för uthållighetsfas, vinst/förlust, dolda vägutfall, inventariegränser och utrustningskort. Fysisk setup, komponentläsbarhet och blindtestbarhet ligger avsiktligt utanför simulatorn.

## Matris

| ID | Regelområde | YAML-källa | Motor/simulator | Tester | Status | Kommentar |
|---|---|---|---|---|---|---|
| `scenario_authority` | **Scenario**<br>Scenarioarket anger mål, startuthållighet, startutrustning och progression och har företräde framför grundregler. | `data/scenarios.yaml`<br>`data/scenarios/*/scenario.yaml` | `GameEngine.__init__`<br>`GameEngine._verify_content_sets` | — | **Delvis** | Scenario-YAML används av motorn, men företrädesregeln i fri text verifieras inte automatiskt. |
| `endurance_setup` | **Uthållighet**<br>Startuthållighet hämtas från valt scenario och spelarantal. | `data/scenarios/*/scenario.yaml` | `GameEngine.__init__` | `tests/test_simulator_alignment.py` | **Delvis** | Implementerat, men saknar ett direkt test per scenario och spelarantal. |
| `endurance_round_loss` | **Uthållighet**<br>Gruppen förlorar 1 uthållighet i slutet av varje runda. | `data/rules.yaml#round.endurance_phase` | `GameEngine.run` | — | **Delvis** | Simuleras, men saknar direkt enhetstest. |
| `endurance_zero_defeat` | **Vinst och förlust**<br>Gruppen förlorar när den sista uthållighetsmarkören tas bort. | `data/rules.yaml#defeat` | `GameEngine.defeat` | — | **Delvis** | Simuleras, men saknar direkt enhetstest. |
| `all_incapacitated_defeat` | **Vinst och förlust**<br>Gruppen förlorar om alla karaktärer är utslagna. | `data/rules.yaml#defeat`<br>`data/characters.yaml` | `GameEngine.defeat`<br>`GameEngine.apply_damage` | — | **Delvis** | Implementerat utan direkt test av gruppförlusten. |
| `character_activation` | **Rundordning**<br>Varje aktiv karaktär aktiveras en gång och får två handlingar. | `data/rules.yaml#round.player_phase` | `GameEngine.activate` | — | **Delvis** | Agenten följer tvåhandlingsekonomin; fysisk kortrotation är inte simulerad. |
| `fixed_activation_order` | **Rundordning**<br>Karaktärerna aktiveras i fast ordning. | `data/rules.yaml#round.player_phase.actor_order` | `GameEngine.run` | — | **Delvis** | Fast intern listordning används, men ordningen mot fysisk medurs placering testas inte. |
| `move_action` | **Handlingar**<br>Flytta kostar 1 handling och kräver en traverserbar angränsande väg. | `data/rules.yaml#actions.move`<br>`data/board.yaml` | `GameEngine.move_action`<br>`GameEngine.is_connection_traversable`<br>`GameEngine.shortest_path` | `tests/test_dynamic_connections_runtime.py::test_closed_connection_is_not_used_by_pathfinding`<br>`tests/test_dynamic_connections_runtime.py::test_open_connection_is_used_immediately` | **Full** | Täcks av runtime- och pathfindingtester. |
| `hidden_road_resolution` | **Vägar**<br>En dold D-väg avslöjas före rörelsen och kan bli Öppen, Hinder eller Händelse. | `data/rules.yaml#actions.move`<br>`data/road-markers.yaml` | `GameEngine.move_action`<br>`GameEngine.draw_travel` | — | **Delvis** | Implementerat men saknar direkt test för alla tre utfall. |
| `obstacle_removal` | **Handlingar**<br>Ett Hinder tas bort med 1 handling och 1 verktyg. | `data/rules.yaml#actions.unlock_road`<br>`data/road-markers.yaml` | `GameEngine.strategic_action` | — | **Delvis** | Agentheuristik hanterar hinder, men regelns exakta kostnadsflöde saknar direkt test. |
| `v_route_closed_default` | **Vägar**<br>V1–V4 är stängda från start och kan inte användas. | `data/board.yaml` | `GameEngine.__init__`<br>`GameEngine.is_connection_traversable` | `tests/test_dynamic_connections_runtime.py::test_scenario_connections_start_closed`<br>`tests/test_dynamic_connections_runtime.py::test_closed_connection_is_not_used_by_pathfinding` | **Full** | Fullt testat. |
| `open_connection_progression` | **Vägar**<br>Scenarioeffekt kan öppna en V-väg omedelbart och göra den dubbelriktat traverserbar. | `data/scenarios/*/scenario.yaml`<br>`data/board.yaml` | `GameEngine.open_connection`<br>`GameEngine._apply_progression_effect` | `tests/test_dynamic_connections_runtime.py::test_open_connection_is_used_immediately`<br>`tests/test_progression_events.py::test_first_completed_objective_opens_connection` | **Full** | Fysisk Öppen-markör är presentationslager. |
| `close_connection_event` | **Scenariohändelse**<br>Ett scenariohändelse kan stänga en namngiven väg omedelbart. | `data/scenario-events/*.yaml` | `GameEngine.close_connection`<br>`GameEngine.process_scenario_event_milestones` | `tests/test_simulator_alignment.py::test_event_log_contains_balance_fields` | **Delvis** | Effekten och loggningen testas; exakt pathfinding efter eventstängning saknar direkt test. |
| `explore_action` | **Handlingar**<br>Utforska kostar 1 handling, avslöjar platskortet och löser dess effekt. | `data/rules.yaml#actions.explore`<br>`data/scenarios/*/locations.yaml` | `GameEngine.explore` | — | **Delvis** | Implementerat, men saknar direkt test för handlingskostnad och effektordning. |
| `location_tile_presentation` | **Platsbrickor**<br>Efter utforskning placeras platsbrickan med samma id som platskortet. | `data/rules.yaml#actions.explore` | — | — | **Presentationslager** | Avsiktligt presentationslager; påverkar inte spelstatus eller simulator. |
| `gather_tool` | **Handlingar**<br>Hämta verktyg kostar 1 handling i Förrådet och kräver ledigt utrymme. | `data/rules.yaml#actions.gather` | `GameEngine.take_tool` | — | **Delvis** | Implementerat utan direkt test. |
| `rest_heal` | **Handlingar**<br>Återhämta kostar 1 handling i Baslägret och läker 1 hälsa. | `data/rules.yaml#actions.rest` | `GameEngine.strategic_action` | — | **Delvis** | Agenten kan använda återhämtning; separat regeltest saknas. |
| `inventory_capacity` | **Ryggsäck**<br>Buret innehåll får inte överskrida karaktärens ryggsäckskapacitet. | `data/rules.yaml#character_state.inventory`<br>`data/inventory.yaml`<br>`data/characters.yaml` | `GameEngine.capacity`<br>`GameEngine.occupied`<br>`GameEngine.can_fit`<br>`GameEngine.drop_for_space` | — | **Delvis** | Implementerat men saknar gränsvärdestester. |
| `transfer_inventory` | **Handlingar**<br>Överföra kostar 1 handling mellan karaktärer på samma plats och respekterar kapacitet. | `data/rules.yaml#actions.assist` | `GameEngine.transfer_if_useful` | — | **Delvis** | Simulatorn använder en strategisk heuristik, inte hela det mänskliga valrummet. |
| `equipment_use` | **Handlingar**<br>Utrustningskortet anger om användningen kräver 1 handling eller ingen handling; engångsutrustning kasseras först när effekten används. | `data/rules.yaml#actions.use_item`<br>`data/base/equipment.yaml`<br>`data/scenarios/*/equipment.yaml` | `GameEngine.use_equipment`<br>`GameEngine.equipment_action_cost`<br>`GameEngine.consume_equipment` | — | **Delvis** | Stödet är kortspecifikt och inte komplett verifierat för varje utrustning. |
| `objective_pickup` | **Målobjekt**<br>Plocka upp kostar 1 handling och kräver tillräckligt ryggsäcksutrymme. | `data/rules.yaml#actions.pick_up_item`<br>`data/scenarios/*/objectives.yaml` | `GameEngine.pickup_ground`<br>`GameEngine.can_fit` | — | **Delvis** | Implementerat utan direkt test. |
| `objective_drop` | **Målobjekt**<br>Att lämna buret innehåll kostar 0 handlingar; scenariot avgör om målet slutförs. | `data/rules.yaml#actions.drop_item`<br>`data/scenarios/*/scenario.yaml` | `GameEngine.deposit_objectives` | `tests/test_progression_events.py::test_first_completed_objective_opens_connection` | **Delvis** | Leveransflödet testas indirekt via progression. |
| `objective_install` | **Målobjekt**<br>Att aktivera ett målobjekt kostar 1 handling på giltig destination. | `data/scenarios/*/scenario.yaml`<br>`data/scenarios/*/objectives.yaml` | `GameEngine.install_module` | `tests/test_scenario_event_milestones.py::test_objective_activated_is_generic_trigger` | **Full** | Generisk objective_activated-trigger används. |
| `objective_completion` | **Målobjekt**<br>Scenario-YAML avgör destination, slutförandetyp och antal mål som krävs. | `data/scenarios/*/scenario.yaml` | `GameEngine.mission_progress`<br>`GameEngine.victory` | — | **Delvis** | Tvärfilsvalidatorn kontrollerar målreferenser och antal; direkt vinsttest saknas. |
| `progression_events` | **Scenariohändelseens ordning**<br>Progression löses efter uppdaterad spelstatus och före scenariohändelse. | `data/rules.yaml#scenario_event_architecture.resolution_order`<br>`data/scenarios/*/scenario.yaml` | `GameEngine.deposit_objectives`<br>`GameEngine.install_module`<br>`GameEngine.process_progression_event` | `tests/test_progression_events.py` | **Full** | Flera progressionstyper och engångsutlösning testas. |
| `scenario_milestones` | **Scenariohändelse**<br>Låsta milstolpetriggers utlöser fasta engångsevent. | `data/rules.yaml#scenario_event_architecture`<br>`data/scenarios/*/scenario.yaml`<br>`data/scenario-events/*.yaml` | `GameEngine._trigger_matches`<br>`GameEngine.process_scenario_event_milestones` | `tests/test_scenario_event_milestones.py` | **Full** | objective_found och objective_activated testas; location_explored och all_objectives_completed saknar direkta tester. |
| `scenario_event_immediate` | **Scenariohändelse**<br>Scenariohändelse löses omedelbart och får endast använda låsta effekter. | `data/rules.yaml#scenario_event_architecture`<br>`data/scenario-events/*.yaml` | `GameEngine.process_scenario_event_milestones`<br>`GameEngine._apply_progression_effect` | `tests/test_scenario_event_milestones.py`<br>`tests/test_simulator_alignment.py` | **Full** | Effekterna loggas och kan slås av/på i experiment. |
| `scenario_event_toggle` | **Simulator**<br>Scenariohändelse kan slås av i seed-matchade experiment utan att övriga regler ändras. | `data/simulation.yaml` | `GameEngine.__init__` | `tests/test_simulator_alignment.py::test_scenario_events_can_be_disabled` | **Full** | Analysfunktion, inte en fysisk spelregel. |
| `victory_condition` | **Vinst och förlust**<br>Gruppen vinner när scenariots vinstvillkor är uppfyllt och minst en karaktär är aktiv. | `data/rules.yaml#victory`<br>`data/scenarios/*/scenario.yaml` | `GameEngine.victory` | — | **Delvis** | Implementerat utan direkt test för båda scenarierna. |
| `travel_events` | **Vägar**<br>En vägmarkör med Händelse drar och löser en färdhändelse omedelbart. | `data/road-markers.yaml`<br>`data/base/travel-events.yaml`<br>`data/scenarios/*/travel-events.yaml` | `GameEngine.draw_travel`<br>`GameEngine.resolve_travel_event` | — | **Delvis** | Effekter stöds, men alla kortkombinationer är inte testade. |
| `physical_setup` | **Förberedelser**<br>Fysiska kort, brickor, markörer och lekar placeras enligt regelbok och scenarioark. | `data/project.yaml`<br>`data/scenarios/*/scenario.yaml`<br>`data/print-layouts/*.yaml` | — | — | **Ej automatiserad** | Avsiktligt utanför simulatorn; kräver fysisk setupkontroll och blindtest. |
| `component_readability` | **Komponenter**<br>Id:n, namn och statusmarkörer ska vara läsbara och matcha källorna. | `data/board.yaml`<br>`data/location-tiles.yaml`<br>`data/road-markers.yaml` | — | — | **Ej automatiserad** | Kräver visuell preflight och fysisk testutskrift. |

## Prioriterade automatiseringsluckor

1. Lägg direkta tester för uthållighetsförlust, slut på uthållighet och alla karaktärer utslagna.
2. Testa samtliga dolda vägutfall: Öppen, Hinder och Händelse.
3. Lägg gränsvärdestester för ryggsäckskapacitet, överföring och målplockning.
4. Lägg scenariovisa vinsttester för Station Nordanvind och Ökenreläet.
5. Lägg tester för `location_explored` och `all_objectives_completed`.
6. Skapa kortspecifika tester för utrustning och färdhändelser som påverkar motorstatus.

## Avsiktligt utanför simulatorn

- fysisk setup och sortering
- platsbrickans visuella placering
- markörers läsbarhet och passform
- regelmissförstånd och glömska
- diskussion, downtime och dominant spelare
- upplevd spänning, berättelse och omspelbarhet

## Underhållsregel

Varje ny eller ändrad spelregel ska uppdatera `data/rule-coverage.yaml`. En regel får inte markeras som **Full** utan minst en relevant automatisk testreferens. Matrisen ska valideras i strict build.

