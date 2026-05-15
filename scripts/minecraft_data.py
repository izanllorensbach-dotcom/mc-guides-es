# scripts/minecraft_data.py
import json, requests
from pathlib import Path

BASE = "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data"
ENDPOINTS = {
    "items":        f"{BASE}/pc/1.21.1/items.json",
    "blocks":       f"{BASE}/pc/1.21.1/blocks.json",
    "enchantments": f"{BASE}/pc/1.21.1/enchantments.json",
    "biomes":       f"{BASE}/pc/1.20.5/biomes.json",
    "entities":     f"{BASE}/pc/1.20.5/entities.json",
}
CACHE_DIR = Path(__file__).parent.parent / "data"

def load_data(resource: str) -> list:
    CACHE_DIR.mkdir(exist_ok=True)
    cache = CACHE_DIR / f"{resource}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    resp = requests.get(ENDPOINTS[resource])
    resp.raise_for_status()
    data = resp.json()
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def fetch_items() -> list[str]:
    return [x["displayName"] for x in load_data("items") if "displayName" in x]

def fetch_enchantments() -> list[str]:
    return [x["displayName"] for x in load_data("enchantments") if "displayName" in x]

def fetch_biomes() -> list[str]:
    return [x["displayName"] for x in load_data("biomes") if "displayName" in x]

def fetch_mobs() -> list[str]:
    return [x["displayName"] for x in load_data("entities") if "displayName" in x]
