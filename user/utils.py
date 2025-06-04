# user/utils.py
import requests

API_KEY = "Tz46hw8cZQ0m4znC6r19sqrMM7L7BhCb"

def get_character_info(nickname, server='cain'):
    info_url = f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}?apikey={API_KEY}"
    info_res = requests.get(info_url).json()

    # 장비 정보
    equip_url = f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}/equip/equipment?apikey={API_KEY}"
    equip_res = requests.get(equip_url).json()

    left_order = ["무기", "상의", "하의", "머리어깨", "벨트", "신발"]
    right_order = ["보조장비", "마법석", "귀걸이", "반지", "목걸이", "칭호"]

    left_slots, right_slots = [], []

    for item in equip_res.get("equipment", []):
        simplified = {
            "enhancement": item.get("reinforce", 0),
            "slotName": item.get("slotName"),
            "icon_url": item.get("itemImageUrl")  # ← 아이콘 URL 추가
        }
        if simplified["slotName"] in left_order:
            left_slots.append(simplified)
        elif simplified["slotName"] in right_order:
            right_slots.append(simplified)

    return {
        "name": info_res.get("characterName"),
        "job_name": info_res.get("jobGrowName"),
        "server_id": server,
        "fame": info_res.get("fame", 0),
        "set_name": "임시 세트",
        "image_url": f"https://img-api.neople.co.kr/df/servers/{server}/characters/{character_id}?zoom=1",
        "left_slots": left_slots,
        "right_slots": right_slots
    }

def get_character_info_by_id(character_id, server):
    # 기본 정보
    info_url = f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}?apikey={API_KEY}"
    info_res = requests.get(info_url).json()

    # 장비 정보
    equip_url = f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}/equip/equipment?apikey={API_KEY}"
    equip_res = requests.get(equip_url).json()

    left_order = ["무기", "상의", "하의", "머리어깨", "벨트", "신발"]
    right_order = ["보조장비", "마법석", "귀걸이", "반지", "목걸이", "칭호"]

    left_slots, right_slots = [], []
    fusion_stones, enchantments = [], []
    set_counter = {}

    for item in equip_res.get("equipment", []):
        slot = item.get("slotName")

        # 세트이름 수집
        set_name = item.get("setItemInfo", {}).get("itemSetName")
        if set_name:
            set_counter[set_name] = set_counter.get(set_name, 0) + 1

        icon = item.get("itemImageUrl")

        basic_data = {
            "slotName": slot,
            "icon_url": icon,
            "enhancement": item.get("reinforce", 0)
        }

        # 장비 좌/우
        if slot in left_order:
            left_slots.append(basic_data)
        elif slot in right_order:
            right_slots.append(basic_data)

        # 융합석
        if "fusionInfo" in item:
            fusion = item["fusionInfo"]
            fusion_stones.append({
                "slotName": slot,
                "icon_url": fusion.get("itemImageUrl")
            })

        # 마부
        if "enchant" in item:
            enchant = item["enchant"]
            icon_url = enchant.get("status", [{}])[0].get("itemImageUrl", icon)
            enchantments.append({
                "slotName": slot,
                "icon_url": icon_url
            })

    most_common_set = max(set_counter, key=set_counter.get) if set_counter else "세트 없음"

    return {
        "name": info_res.get("characterName"),
        "job_name": info_res.get("jobGrowName"),
        "server_id": server,
        "fame": info_res.get("fame", 0),
        "set_name": most_common_set,
        "image_url": f"https://img-api.neople.co.kr/df/servers/{server}/characters/{character_id}?zoom=1",
        "left_slots": left_slots,
        "right_slots": right_slots,
        "fusion_stones": fusion_stones,
        "enchantments": enchantments
    }

def search_characters(nickname, server):
    servers = ["cain", "diregie", "siroco", "prey", "casillas", "hilder", "anton", "bakal"]
    targets = servers if server == "전체" else [server]

    results = []

    for s in targets:
        url = f"https://api.neople.co.kr/df/servers/{s}/characters?characterName={nickname}&apikey={API_KEY}&limit=3"
        res = requests.get(url)
        if res.status_code != 200:
            continue

        for row in res.json().get("rows", []):
            char_id = row["characterId"]

            equip_url = f"https://api.neople.co.kr/df/servers/{s}/characters/{char_id}/equip/equipment?apikey={API_KEY}"
            equip_res = requests.get(equip_url).json()
            equipment = equip_res.get("equipment", [])

            # 임시로 fusion/enchant에 같은 이미지 복사
            for e in equipment:
                e["fusionImageUrl"] = e.get("itemImageUrl")
                e["enchantImageUrl"] = e.get("itemImageUrl")

            row["equipment"] = equipment
            results.append(row)

    return results
