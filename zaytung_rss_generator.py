import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

BASE_URL = "https://www.zaytung.com"
CATEGORIES = {
    "haber": "https://www.zaytung.com/tr/fake-news",
    "sondakika": "https://www.zaytung.com/tr/last-minute-news",
    "inceleme": "https://www.zaytung.com/tr/review",
    "roportaj": "https://www.zaytung.com/tr/interview"
}

def fetch_category_news(category_name, url):
    print(f"🔹 {category_name} haberleri çekiliyor...")
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}
response = requests.get(url, headers=headers)

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    haberler = soup.find_all('div', class_='haber', limit=10)
    news_list = []

    for haber in haberler:
        a_tag = haber.find('a')
        img_tag = haber.find('img')
        if a_tag:
            link = BASE_URL + a_tag['href']
            title = a_tag.get_text(strip=True)
            desc = haber.get_text(strip=True).replace(title, '')
            image_url = None
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
                if not image_url.startswith('http'):
                    image_url = BASE_URL + '/' + image_url.lstrip('/')
            news_list.append({
                'title': title,
                'link': link,
                'desc': desc if desc else title,
                'image': image_url
            })
    return news_list

def generate_rss_for_category(category_name, news_list):
    fg = FeedGenerator()
    fg.title(f'Zaytung {category_name.capitalize()} Haberler')
    fg.link(href=CATEGORIES[category_name])
    fg.description(f'Zaytung {category_name} haber akışı')
    fg.language('tr')

    for news in news_list:
        fe = fg.add_entry()
        fe.title(news['title'])
        fe.link(href=news['link'])
        desc = f"<p>{news['desc']}</p>"
        if news['image']:
            desc = f'<img src="{news["image"]}" alt="{news["title"]}"><br>' + desc
        fe.description(desc)
        fe.pubDate(datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0300'))

    filename = f'zaytung_{category_name}_rss.xml'
    fg.rss_file(filename)
    print(f"✅ {filename} oluşturuldu.")

if __name__ == '__main__':
    for category_name, url in CATEGORIES.items():
        news_list = fetch_category_news(category_name, url)
        generate_rss_for_category(category_name, news_list)
