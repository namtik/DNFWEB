import os
import requests
from flask import current_app, url_for

API_KEY            = "Tz46hw8cZQ0m4znC6r19sqrMM7L7BhCb"
API_ITEM_DETAIL_URL = "https://api.neople.co.kr/df/items/{item_id}"
API_ITEM_IMAGE_URL  = "https://img-api.neople.co.kr/df/items/{item_id}"

def get_local_item_image(item_id):
    """item_id 기반으로 static/items/{item_id}.png 에 캐시 후 URL 반환"""
    if not item_id:
        return url_for('static', filename='default.png')
    static_dir = os.path.join(current_app.static_folder, "items")
    os.makedirs(static_dir, exist_ok=True)
    file_path = os.path.join(static_dir, f"{item_id}.png")
    url_path  = url_for('static', filename=f"items/{item_id}.png")
    if not os.path.exists(file_path):
        resp = requests.get(API_ITEM_IMAGE_URL.format(item_id=item_id), params={"apikey": API_KEY})
        if resp.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(resp.content)
        else:
            return url_for('static', filename='default.png')
    return url_path

def search_characters(nickname, server):
    servers = ["cain","diregie","siroco","prey","casillas","hilder","anton","bakal"]
    targets = servers if server=="전체" else [server]
    results = []
    for s in targets:
        res = requests.get(
            f"https://api.neople.co.kr/df/servers/{s}/characters",
            params={"characterName": nickname, "apikey": API_KEY, "limit": 3}
        )
        if res.status_code != 200:
            continue
        for row in res.json().get("rows", []):
            equip_res = requests.get(
                f"https://api.neople.co.kr/df/servers/{s}/characters/{row['characterId']}/equip/equipment",
                params={"apikey": API_KEY}
            )
            row["equipment"] = equip_res.json().get("equipment", []) if equip_res.status_code == 200 else []
            results.append(row)
    return results

def get_character_set_name(equipment):
    """
    장비 리스트를 순회하며 setItemInfo.itemSetName 이 없으면
    /df/items/{itemId} 상세 조회로 보강한 뒤 최빈 세트명을 반환.
    """
    counts = {}
    for item in equipment:
        si = item.get("setItemInfo") or {}
        name = si.get("itemSetName")
        if not name:
            # 잘못된 도메인 제거: 데이터 API로 호출해야 setItemInfo가 들어있음
            detail_res = requests.get(
                API_ITEM_DETAIL_URL.format(item_id=item.get("itemId")),
                params={"apikey": API_KEY}
            )
            if detail_res.status_code == 200:
                detail = detail_res.json().get("item", {})  # wrap under "item"
                si = detail.get("setItemInfo") or {}
                name = si.get("itemSetName")
        if name:
            counts[name] = counts.get(name, 0) + 1
    return max(counts, key=counts.get) if counts else "세트 없음"

def get_character_info_by_id(character_id, server):
    SERVER_KR = {
        "cain":"카인","diregie":"디레지에","siroco":"시로코","prey":"프레이",
        "casillas":"카시야스","hilder":"힐더","anton":"안톤","bakal":"바칼"
    }
    server_name_kr = SERVER_KR.get(server, server)

    info_res = requests.get(
        f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}",
        params={"apikey": API_KEY}
    ).json()

    equip_res = requests.get(
        f"https://api.neople.co.kr/df/servers/{server}/characters/{character_id}/equip/equipment",
        params={"apikey": API_KEY}
    )
    raw_equip = equip_res.json().get("equipment", []) if equip_res.status_code == 200 else []

    left_order  = ["무기","상의","하의","머리어깨","벨트","신발"]
    right_order = ["보조장비","마법석","목걸이","반지","귀걸이","팔찌","칭호"]

    left_slots, right_slots = [], []
    fusion_stones, enchantments = [], []

    for item in raw_equip:
        slot = item.get("slotName")
        basic = {
            "slotName":    slot,
            "itemId":      item.get("itemId"),
            "icon_url":    item.get("itemImageUrl"),
            "itemName":    item.get("itemName"),
            "enhancement": item.get("reinforce", 0),
            "itemStatus":  item.get("itemStatus", {}),
            "setItemInfo": item.get("setItemInfo") or {}
        }
        if slot in left_order:
            left_slots.append(basic)
        elif slot in right_order:
            right_slots.append(basic)

        fusion = item.get("fusionInfo", {})
        if fusion.get("itemId"):
            fusion_stones.append({
                "slotName": slot,
                "itemId":   fusion["itemId"],
                "icon_url": fusion.get("itemImageUrl") or basic["icon_url"],
                "itemName": fusion.get("itemName")
            })

        enchant = item.get("enchant", {})
        if enchant.get("itemId"):
            enchantments.append({
                "slotName": slot,
                "itemId":   enchant.get("itemId"),
                "icon_url": enchant.get("itemImageUrl") or basic["icon_url"],
                "itemName": enchant.get("itemName")
            })

    set_name = get_character_set_name(raw_equip)

    return {
        "name":          info_res.get("characterName"),
        "jobName":       info_res.get("jobGrowName"),
        "server_id":     server,
        "server_name":   server_name_kr,
        "fame":          info_res.get("fame", 0),
        "set_name":      set_name,
        "image_url":     f"https://img-api.neople.co.kr/df/servers/{server}/characters/{character_id}?zoom=1",
        "left_slots":    left_slots,
        "right_slots":   right_slots,
        "fusion_stones": fusion_stones,
        "enchantments":  enchantments
    }

def parse_character_stats(equipment_list):
    attack_power = 0
    for item in equipment_list:
        if "무기" in item["slotName"]:
            stats = item.get("itemStatus", {})
            attack_power = max(
                stats.get("물리 공격력", 0),
                stats.get("마법 공격력", 0),
                stats.get("독립 공격력", 0)
            )
            break
    return {"attack_power": attack_power, "ele_multiplier": 1.0, "crit_multiplier": 1.5}
