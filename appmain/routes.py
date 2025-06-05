# appmain/routes.py
from flask import Blueprint, request, render_template
from user.utils import get_character_info_by_id, get_character_info
import requests
from user.utils import search_characters

main = Blueprint('main', __name__)

API_KEY = "Tz46hw8cZQ0m4znC6r19sqrMM7L7BhCb"

@main.route('/')
def index():
    return render_template('index.html')


@main.route("/search", methods=["POST"])
def search():
    nickname = request.form.get("nickname")
    server = request.form.get("server")

    results = search_characters(nickname, server)

    characters = []
    for char in results:
        equipment_icons = {}
        fusion_icons = {}
        enchant_icons = {}

        for item in char.get("equipment", []):
            slot = item["slotName"]
            equipment_icons[slot] = item.get("itemImageUrl", "")
            fusion_icons[slot] = item.get("fusionImageUrl", "")
            enchant_icons[slot] = item.get("enchantImageUrl", "")

        characters.append({
            "id": char["characterId"],
            "name": char["characterName"],
            "server": char["serverId"],
            "job": char["jobGrowName"],
            "fame": char.get("fame", 0),
            "adventure_name": char.get("adventureName", "-"),
            "image_url": f"https://img-api.neople.co.kr/df/servers/{char['serverId']}/characters/{char['characterId']}?zoom=1",
            "equipment_icons": equipment_icons,
            "fusion_icons": fusion_icons,
            "enchant_icons": enchant_icons,
        })

    return render_template("search.html", characters=characters)
    
@main.route("/select_character", methods=["POST"])
def select_character():
    character_id = request.form["character_id"]
    server_id = request.form["server_id"]

    character = get_character_info_by_id(character_id, server_id)

    return render_template("result.html", character=character)

@app.route('/result')
def result():
    character_id = request.args.get('character_id')
    server_id = request.args.get('server_id')

    character_data = get_character_info_by_id(character_id, server_id)

    return render_template('result.html', character=character_data)

