# scripts/generate_content.py
import csv, sys
from datetime import date
from pathlib import Path
import anthropic
from scripts.utils import slugify, load_env

PROMPTS_DIR = Path(__file__).parent.parent / "templates" / "prompts"
MODEL = "claude-haiku-4-5-20251001"

def load_prompt_template(lang: str) -> str:
    path = PROMPTS_DIR / f"minecraft_{lang}.txt"
    if not path.exists():
        raise FileNotFoundError(f"No prompt template for lang='{lang}': {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lines if not l.startswith("#")).strip()

def build_frontmatter(title: str, slug: str, description: str, tags: list[str], date_str: str) -> str:
    tags_str = ", ".join(f'"{t}"' for t in tags)
    return f'---\ntitle: "{title}"\nslug: "{slug}"\ndate: {date_str}\ndescription: "{description}"\ntags: [{tags_str}]\ndraft: false\n---\n\n'

def generate_article(client: anthropic.Anthropic, keyword: str, lang: str) -> str:
    template = load_prompt_template(lang)
    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=[{
            "type": "text",
            "text": "You are an expert Minecraft guide writer. Write detailed, accurate, helpful content.",
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": template.replace("{keyword}", keyword)}],
    )
    return message.content[0].text

def save_article(content: str, slug: str, output_dir: str) -> Path:
    path = Path(output_dir) / f"{slug}.md"
    if path.exists():
        return path
    path.write_text(content, encoding="utf-8")
    return path

def run(keywords_csv: str, output_dir: str, lang: str, count: int = 10) -> int:
    client = anthropic.Anthropic(api_key=load_env())
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    existing = {p.stem for p in Path(output_dir).glob("*.md")}
    generated = 0

    with open(keywords_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if generated >= count:
                break
            keyword = row["keyword"]
            slug = slugify(keyword)
            if slug in existing:
                continue
            print(f"  Generating: {keyword}")
            body = generate_article(client, keyword, lang)
            tags = ["minecraft", "guide"] + [w for w in keyword.split() if len(w) > 4][:3]
            description = f"Complete guide about {keyword}." if lang == "en" else f"Guía completa sobre {keyword}."
            frontmatter = build_frontmatter(keyword.title(), slug, description, tags, str(date.today()))
            save_article(frontmatter + body, slug, output_dir)
            existing.add(slug)
            generated += 1
            print(f"    Saved: {slug}.md")
    return generated

if __name__ == "__main__":
    keywords_csv = sys.argv[1]
    output_dir  = sys.argv[2]
    lang        = sys.argv[3] if len(sys.argv) > 3 else "en"
    count       = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    n = run(keywords_csv, output_dir, lang, count)
    print(f"\nDone: {n} articles generated in {output_dir}")
