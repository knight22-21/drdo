import random

# ------------------------ Weapon and Target Stats ------------------------

weapon_stats = {
    "missile": {"damage": 90, "cooldown": 2, "range": 700_000, "speed": (400*1e3)/3600},
    "drone": {"damage": 50, "cooldown": 1, "range": 900_000, "speed": (260*1e3)/3600},
    "artillery": {"damage": 110, "cooldown": 3, "range": 800_000, "speed": (100*1e3)/3600},
    "sam": {"damage": 70, "cooldown": 2, "range": 600_000, "speed": (450*1e3)/3600},
    "tankgun": {"damage": 60, "cooldown": 2, "range": 350_000, "speed": (120*1e3)/3600},
    "torpedo": {"damage": 130, "cooldown": 4, "range": 500_000, "speed": (90*1e3)/3600},
    "empdevice": {"damage": 40, "cooldown": 1, "range": 350_000, "speed": (500*1e3)/3600},
    "railgun": {"damage": 150, "cooldown": 4, "range": 1_000_000, "speed": (800*1e3)/3600},
    "flakgun": {"damage": 55, "cooldown": 1, "range": 400_000, "speed": (300*1e3)/3600},
    "antitankrocket": {"damage": 80, "cooldown": 2, "range": 300_000, "speed": (250*1e3)/3600}
}

target_stats = {
    "tank": {"armor": 40, "speed": (50*1e3)/3600},
    "infantry": {"armor": 10, "speed": (70*1e3)/3600},
    "radar": {"armor": 15, "speed": 0},
    "aircraft": {"armor": 25, "speed": (200*1e3)/3600},
    "truck": {"armor": 15, "speed": (60*1e3)/3600},
    "commandcenter": {"armor": 60, "speed": 0},
    "submarine": {"armor": 45, "speed": (30*1e3)/3600},
    "destroyer": {"armor": 50, "speed": (40*1e3)/3600},
    "supplyship": {"armor": 35, "speed": (25*1e3)/3600},
    "snipernest": {"armor": 20, "speed": 0},
    "supplydepot": {"armor": 30, "speed": 0},
    "electronicwarfareunit": {"armor": 30, "speed": 0}
}

# ------------------------ Scenario Definitions ------------------------

scenarios = {
    "urban_battlefield": {
        "available_weapons": ["artillery", "drone", "tankgun", "flakgun", "empdevice"],
        "available_targets": ["tank", "infantry", "radar", "snipernest", "supplydepot"]
    },
    "airfield_defense": {
        "available_weapons": ["missile", "sam", "drone", "flakgun", "railgun"],
        "available_targets": ["aircraft", "radar", "commandcenter", "infantry"]
    },
    "convoy_ambush": {
        "available_weapons": ["artillery", "drone", "missile", "antitankrocket", "tankgun"],
        "available_targets": ["truck", "tank", "commandcenter", "infantry"]
    },
    "mountain_warfare": {
        "available_weapons": ["artillery", "drone", "missile", "tankgun", "flakgun"],
        "available_targets": ["snipernest", "tank", "infantry", "radar", "supplydepot"]
    },
    "naval_battle": {
        "available_weapons": ["torpedo", "missile", "drone", "sam", "flakgun"],
        "available_targets": ["destroyer", "submarine", "aircraft", "radar", "supplyship"]
    },
    "desert_conflict": {
        "available_weapons": ["missile", "artillery", "drone", "sam", "tankgun"],
        "available_targets": ["tank", "infantry", "truck", "commandcenter", "radar"]
    },
    "jungle_ambush": {
        "available_weapons": ["drone", "missile", "artillery", "flakgun", "antitankrocket"],
        "available_targets": ["infantry", "snipernest", "commandcenter", "radar"]
    }
}

# ------------------------ Simulation Function ------------------------

def simulate(scenario_name, selected_weapons, selected_targets, max_rounds=500):
    weapons = [{"id": i, "type": w, "ready_in": 0} for i, w in enumerate(selected_weapons)]
    targets = [{"id": i, "type": t, "distance": random.randint(200_000, 800_000)} for i, t in enumerate(selected_targets)]
    hp = [target_stats[t["type"]]["armor"] * 10 for t in targets]

    log = []

    for round_num in range(1, max_rounds + 1):
        round_log = [f"--- Round {round_num} ---"]

        # Update distances
        for t in targets:
            t["distance"] = max(0, t["distance"] - target_stats[t["type"]]["speed"])

        # Threat and effectiveness
        threats = [(target_stats[t["type"]]["armor"] / max(t["distance"], 1)) + (200000 / (t["distance"]**2)) for t in targets]
        effects = [[0]*len(targets) for _ in weapons]

        for i, w in enumerate(weapons):
            ws = weapon_stats[w["type"]]
            for j, t in enumerate(targets):
                if t["distance"] > ws["range"]:
                    continue
                rm = max(0.1, 1 - t["distance"] / ws["range"])
                eff = (ws["damage"] * rm) / (target_stats[t["type"]]["armor"] + 1)
                effects[i][j] = min(1, eff / 2)

        assigns = [-1] * len(weapons)
        load = [0] * len(targets)

        for i, w in enumerate(weapons):
            if w["ready_in"] > 0:
                w["ready_in"] -= 1
                continue
            best, bs = -1, -1
            for j, t in enumerate(targets):
                if hp[j] <= 0 or load[j] >= 3 or t["distance"] > weapon_stats[w["type"]]["range"]:
                    continue
                sc = effects[i][j] * threats[j]
                if sc > bs:
                    best, bs = j, sc
            if best >= 0:
                assigns[i] = best
                load[best] += 1
                w["ready_in"] = weapon_stats[w["type"]]["cooldown"]

        for i, target_idx in enumerate(assigns):
            if target_idx < 0:
                round_log.append(f"Weapon {weapons[i]['id']} ({weapons[i]['type']}) idle/cooling")
                continue
            ws = weapon_stats[weapons[i]["type"]]
            dist = targets[target_idx]["distance"]
            rm = max(0.1, 1 - dist / ws["range"])
            dmg = ws["damage"] * rm
            hp[target_idx] = max(0, hp[target_idx] - dmg)
            round_log.append(
                f"Weapon {weapons[i]['id']} ({weapons[i]['type']}) → Target {target_idx} "
                f"({targets[target_idx]['type']}) | Damage: {dmg:.2f} | HP left: {hp[target_idx]:.2f}"
            )

        all_neutralized = True
        for idx, t in enumerate(targets):
            if hp[idx] <= 0:
                round_log.append(f"Target {idx} ({t['type']}): Neutralized")
            else:
                round_log.append(
                    f"Target {idx} ({t['type']}): HP={hp[idx]:.2f}, Distance={t['distance']:.2f}"
                )
                all_neutralized = False

        log.append("\n".join(round_log))

        if all_neutralized:
            log.append(f"\n✅ All targets neutralized in {round_num} rounds.")
            return "\n\n".join(log), [line for block in log for line in block.splitlines()]

    log.append("\n⚠️ Max rounds reached. Some targets remain.")
    return "\n\n".join(log), [line for block in log for line in block.splitlines()]