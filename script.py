import re, base64
from urllib.parse import quote, unquote
from playwright.sync_api import sync_playwright

URL = "https://tiagorrg.github.io/vless-checker/"
FILE = "subscription.txt"

COUNTRY_MAP = {
    "Germany": "Германия", "Netherlands": "Нидерланды", "United States": "США",
    "United Kingdom": "Великобритания", "France": "Франция", "Sweden": "Швеция",
    "Switzerland": "Швейцария", "Canada": "Канада", "Japan": "Япония",
    "Singapore": "Сингапур", "Spain": "Испания", "Italy": "Италия",
    "Poland": "Польша", "Finland": "Финляндия", "Norway": "Норвегия",
    "Denmark": "Дания", "Austria": "Австрия", "Belgium": "Бельгия",
    "Turkey": "Турция", "Ukraine": "Украина", "Latvia": "Латвия",
    "Lithuania": "Литва", "Estonia": "Эстония", "Czech Republic": "Чехия",
    "Romania": "Румыния", "Hungary": "Венгрия", "Bulgaria": "Болгария",
    "Greece": "Греция", "Portugal": "Португалия", "Ireland": "Ирландия",
    "Slovakia": "Словакия", "Slovenia": "Словения", "Croatia": "Хорватия",
    "Luxembourg": "Люксембург", "Iceland": "Исландия", "Malta": "Мальта",
    "Cyprus": "Кипр", "Israel": "Израиль", "United Arab Emirates": "ОАЭ",
    "Brazil": "Бразилия", "Mexico": "Мексика", "Argentina": "Аргентина",
    "Chile": "Чили", "Colombia": "Колумбия", "South Korea": "Южная Корея",
    "Hong Kong": "Гонконг", "Taiwan": "Тайвань", "Australia": "Австралия",
    "New Zealand": "Новая Зеландия", "India": "Индия", "Russia": "Россия",
    "Kazakhstan": "Казахстан", "Serbia": "Сербия", "Moldova": "Молдова",
    "Georgia": "Грузия", "Armenia": "Армения", "Azerbaijan": "Азербайджан",
    "Uzbekistan": "Узбекистан", "Kyrgyzstan": "Киргизия", "Tajikistan": "Таджикистан",
    "Turkmenistan": "Туркмения", "Belarus": "Беларусь",
}

def extract_links_rendered():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        html = page.content()
        browser.close()
    raw_links = set()
    patterns = [r'vless://[^\s"\'<>]+', r'vless%3A%2F%2F[^\s"\'<>]+']
    for pat in patterns:
        raw_links.update(re.findall(pat, html))
    return raw_links

def process_link(raw):
    if raw.startswith("vless%3A%2F%2F"):
        decoded = unquote(raw)
        if "#" in decoded:
            base, name = decoded.split("#", 1)
        else:
            base, name = decoded, ""
        return base, name
    else:
        if "#" in raw:
            base, name_enc = raw.split("#", 1)
            name = unquote(name_enc)
        else:
            base, name = raw, ""
        return base, name

def rename():
    links = []
    seen = {}
    for raw in extract_links_rendered():
        base, name = process_link(raw)
        if not name:
            continue
        country_en = None
        for en, ru in COUNTRY_MAP.items():
            if en.lower() in name.lower():
                country_en = en
                break
        if country_en:
            ru_name = COUNTRY_MAP[country_en]
            idx = seen.get(country_en, 0) + 1
            seen[country_en] = idx
            new_name = f"{ru_name} #{idx}"
        else:
            new_name = name
        links.append(f"{base}#{quote(new_name)}")
    return links

def main():
    links = rename()
    if not links:
        print("no links found")
        return
    content = "\n".join(links)
    encoded = base64.b64encode(content.encode()).decode()
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(encoded)
    print(f"written {len(links)} links")

if __name__ == "__main__":
    main()
