import requests, re, base64
from urllib.parse import unquote, quote

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

def extract_links():
    resp = requests.get(URL, timeout=30)
    resp.raise_for_status()
    html = resp.text
    # ищем vless:// или полностью закодированный vless%3A%2F%2F
    patterns = [
        r'vless://[^\s"\'<>]+',
        r'vless%3A%2F%2F[^\s"\'<>]+'
    ]
    raw_links = set()
    for p in patterns:
        raw_links.update(re.findall(p, html))
    return raw_links

def process_link(raw):
    # если вся ссылка закодирована, декодируем полностью
    if raw.startswith('vless%3A%2F%2F'):
        decoded = unquote(raw)
        # после декодирования разделяем на base и name по '#'
        if '#' in decoded:
            base, name = decoded.split('#', 1)
        else:
            base, name = decoded, ''
        # base уже декодирован, но для валидности оставляем как есть (могли быть служебные символы)
        return base, name, True  # base уже в читаемом виде, но может требовать кодирования
    else:
        # обычная ссылка с закодированным именем
        if '#' in raw:
            base, name_encoded = raw.split('#', 1)
            name = unquote(name_encoded)
        else:
            base, name = raw, ''
        return base, name, False

def rename():
    links = []
    seen_countries = {}
    for raw in extract_links():
        base, name, decoded_full = process_link(raw)
        if not name:
            continue
        country_en = None
        for en, ru in COUNTRY_MAP.items():
            if en.lower() in name.lower():
                country_en = en
                break
        if country_en:
            ru_name = COUNTRY_MAP[country_en]
            idx = seen_countries.get(country_en, 0) + 1
            seen_countries[country_en] = idx
            new_name = f"{ru_name} #{idx}"
        else:
            new_name = name
        # собираем обратно: base как есть, имя кодируем
        # если ссылка была полностью закодирована, base уже декодирован, но это ок
        new_link = f"{base}#{quote(new_name)}"
        links.append(new_link)
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
    print(f"written {len(links)} links to {FILE}")

if __name__ == "__main__":
    main()
