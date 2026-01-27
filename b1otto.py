import requests
from bs4 import BeautifulSoup

# رابط الصفحة التي تحتوي على القنوات
URL = "https://v5on.site/index.php?cat=29"

def main():
    resp = requests.get(URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.select("a.channel-card")  # كل رابط قناة

    lines = ["#EXTM3U\n"]

    for link in links:
        href = link.get("href")  # مثال: play.php?id=2541
        id_value = href.split("id=")[-1]

        name_tag = link.select_one(".card-info h4")
        name = name_tag.text.strip() if name_tag else f"Channel {id_value}"

        logo_tag = link.select_one(".card-thumbnail img")
        logo = logo_tag.get("src") if logo_tag else ""

        # صيغة M3U
        lines.append(f'#EXTINF:-1 tvg-id="{id_value}" tvg-name="{name}" tvg-logo="{logo}",{name}')
        lines.append(href)

    # كتابة الملف
    with open("b1otto.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("b1otto.m3u تم تحديث الملف بنجاح!")

if __name__ == "__main__":
    main()
