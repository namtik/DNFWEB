
import math

def calculate_total_damage(skills, atk=100000, ele_mult=1.35, crit_mult=1.5, duration=40.0, cooldown_reduction=0.235):
    total_damage = 0.0
    rotation_detail = {}

    for name, data in skills.items():
        real_cd = data["cooldown"] * (1 - cooldown_reduction)
        if real_cd <= 0: continue

        times_cast = int(duration // real_cd)
        coeff = data["coeff"]
        damage_per_cast = atk * (coeff / 100) * ele_mult * crit_mult
        total_skill_damage = times_cast * damage_per_cast
        total_damage += total_skill_damage

        rotation_detail[name] = {
            "cooldown": round(real_cd, 2),
            "times_cast": times_cast,
            "damage": round(total_skill_damage)
        }

    return round(total_damage), rotation_detail
