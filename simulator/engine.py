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

def simulate(scenario_name, weapon_configs, target_configs):
    log = [f"--- Single Round Simulation for {scenario_name.replace('_', ' ').title()} ---"]

    weapons = [
        {
            "id": i,
            "type": w["type"],
            "damage": w["damage"],
            "range_km": w["range"],  
            "speed": w["speed"]  
        }
        for i, w in enumerate(weapon_configs)
    ]

    targets = [
        {
            "id": i,
            "type": t["type"],
            "armor": t["armor"],
            "speed": t["speed"],  
            "distance_km": t["distance"] 
        }
        for i, t in enumerate(target_configs)
    ]

    hp = [t["armor"] * 4 for t in targets]  # reduced from *10 to allow more neutralization
    assigned_targets = set()
    assignments = []

    for w in weapons:
        best_target = None
        best_score = -1
        for i, t in enumerate(targets):
            if hp[i] <= 0:
                continue  # already neutralized
            if t["distance_km"] > w["range_km"]:
                continue  # out of range

            range_modifier = max(0.5, 1 - t["distance_km"] / w["range_km"])
            effective_damage = w["damage"] * range_modifier
            score = effective_damage / (t["armor"] + 1)

            if score > best_score:
                best_score = score
                best_target = i

        if best_target is not None:
            t = targets[best_target]
            dist_km = t["distance_km"]
            range_modifier = max(0.5, 1 - dist_km / w["range_km"])
            effective_damage = w["damage"] * range_modifier
            hp[best_target] = max(0, hp[best_target] - effective_damage)

            result = (
                f"🔫 Weapon {w['id']} ({w['type']}) → Target {best_target} ({t['type']}) "
                f"| Distance: {dist_km:.1f} km | Damage: {effective_damage:.2f} | HP left: {hp[best_target]:.2f}"
            )
            result += " ✅ Neutralized" if hp[best_target] <= 0 else " ❌ Survived"

            log.append(result)
        else:
            log.append(f"🔫 Weapon {w['id']} ({w['type']}) → ❌ No valid target in range or already neutralized")


    return "\n".join(log), log
