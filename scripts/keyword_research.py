# scripts/keyword_research.py
import csv, sys
from pathlib import Path
from scripts.minecraft_data import fetch_items, fetch_enchantments, fetch_biomes, fetch_mobs

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "keywords"

def load_templates(lang: str) -> list[str]:
    path = TEMPLATES_DIR / f"minecraft_{lang}.txt"
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]

def generate_keywords(templates, items, enchantments, biomes, mobs) -> list[str]:
    keywords = set()
    mapping = {"{item}": items, "{enchantment}": enchantments,
               "{biome}": biomes, "{mob}": mobs}
    for template in templates:
        for placeholder, values in mapping.items():
            if placeholder in template:
                for v in values:
                    keywords.add(template.replace(placeholder, v))
    return sorted(keywords)

def save_keywords(keywords: list[str], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword"])
        for kw in keywords:
            writer.writerow([kw])

def run(lang: str, output_path: str) -> int:
    templates = load_templates(lang)
    keywords = generate_keywords(
        templates,
        fetch_items(), fetch_enchantments(), fetch_biomes(), fetch_mobs()
    )
    save_keywords(keywords, output_path)
    return len(keywords)

if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    output = sys.argv[2] if len(sys.argv) > 2 else f"keywords_minecraft_{lang}.csv"
    count = run(lang, output)
    print(f"Generated {count} keywords -> {output}")
