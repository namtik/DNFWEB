from flask import Blueprint, request, render_template
from user.utils import (
    search_characters,
    get_character_info_by_id,
    parse_character_stats,
    get_local_item_image,
    get_character_set_name 
)
from user.damage_simulator import calculate_total_damage

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    chars = search_characters(request.form['nickname'], request.form['server'])
    return render_template('search.html', characters=chars)

@main.route('/select_character', methods=['POST'])
def select_character():
    cid = request.form['character_id']
    sid = request.form['server_id']
    if not cid or not sid:
        return "잘못된 요청입니다.",400

    char = get_character_info_by_id(cid, sid)
    equipment = char['left_slots'] + char['right_slots']
    fusion    = char['fusion_stones']
    enchant   = char['enchantments']

    for it in equipment:
        it['icon_url'] = get_local_item_image(it['itemId'])
    for it in fusion:
        it['icon_url'] = get_local_item_image(it['itemId'])
    for it in enchant:
        it['icon_url'] = get_local_item_image(it['itemId'])

    stats = parse_character_stats(equipment)
    skills = {
        "터뷸런트 럼블": {"coeff":94251,"cooldown":45.0},
        "바이올런트 스톰": { "coeff": 105636, "cooldown": 34.2 },
        "스파이럴 프레스": { "coeff": 105593, "cooldown": 33.6 },
        "스톰 웨이커":     { "coeff": 76082,  "cooldown": 38.3 },
        "질풍가도":       { "coeff": 91265,  "cooldown": 23.0 },
        "스톰 스트라이크": { "coeff": 86361,  "cooldown": 34.4 },
        "휘몰아치는 바람": { "coeff": 75063,  "cooldown": 19.1 },
        "칼날 바람":      { "coeff": 109587, "cooldown": 13.8 },
        "폭풍의 눈":      { "coeff": 84865,  "cooldown": 12.2 },
        "쌍쌍바람":       { "coeff": 108012, "cooldown": 10.7 },
        "윈드 블래스터":   { "coeff": 124296, "cooldown": 6.4 },
        "회오리 바람":    { "coeff": 113008, "cooldown": 6.4 },
        "대진공":        { "coeff": 83709,  "cooldown": 7.7 },
        "삭풍":         { "coeff": 110442, "cooldown": 5.4 },
        "소닉 무브":     { "coeff": 122226, "cooldown": 3.8 }
    }
    expect_damage, detail = calculate_total_damage(
        skills=skills,
        atk=stats["attack_power"],
        ele_mult=stats["ele_multiplier"],
        crit_mult=stats["crit_multiplier"],
        duration=40.0,
        cooldown_reduction=0.235
    )
    set_name = get_character_set_name(equipment)
    set_count = sum(1 for it in equipment
                    if it.get('setItemInfo', {}).get('itemSetName') == set_name)
    set_max = next(
        (it.get('setItemInfo', {}).get('maxCount', 0)
        for it in equipment
        if it.get('setItemInfo', {}).get('itemSetName') == set_name),
        0
    )

    print("DEBUG set_name:", set_name)
    print("DEBUG raw equipment setItemInfo:",
      [item.get("setItemInfo",{}).get("itemSetName") for item in equipment])

    return render_template('result.html',
        character=char,
        equipment=equipment,
        fusion_stones=fusion,
        enchantments=enchant,
        expect_damage=expect_damage,
        detail=detail,
        set_name=set_name,
        set_count=set_count,
        set_max=set_max
    )
