import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
import json

from tqdm import tqdm

url = 'https://spb.hh.ru/'


def get_headers():
    return Headers(browser="firefox", os="win").generate()

def get_text(url):
    count = 0
    req = requests.get(url, headers=get_headers())
    while req.status_code != 200 or count > 2:
        req = requests.get(url, headers=get_headers())
        count += 1
    if req.status_code == 200:
        return req.text
    else:
        return "Нет соединения с сервером!"

def get_vakansy_hh(url):
    resp = get_text(url)
    soup = BeautifulSoup(resp, features = "html5lib")
    pattern = r"\s\d+\s\d+"
    description = soup.find('div', class_='g-user-content').text
    if soup.find('div', class_='g-user-content'):
        description = soup.find('div', class_='g-user-content').text
    else:
        description =''
    if "Django" in description and "Flask" in description:
        name_company = soup.find('span', class_='vacancy-company-name').text
        salary = soup.find('div', class_='vacancy-title').text
        salary =' -'.join(re.findall(pattern, salary)).strip()
        if soup.find('p', {'data-qa': 'vacancy-view-location'}):
            sity = soup.find('p', {'data-qa': 'vacancy-view-location'}).text
        elif soup.find('span', {'data-qa': 'vacancy-view-raw-address'}):
            sity = soup.find('span', {'data-qa': 'vacancy-view-raw-address'}).text.split(',')[0]
        else:
            sity = ''

        return {'link': url,
                'salary': salary,
                'name_company': name_company,
                'sity': sity
                }
def get_link_vakansy_hh(search_text):
    list_vacansy = []
    articles = f"{url}/search/vacancy?text={search_text}&area=1&area=2&items_on_page=20"
    count_pages = extract_max_page(articles) - 1
    count_pages = 10
    with tqdm(total=count_pages, desc="Processing") as pbar:
        for page in range(0, count_pages):
            link_item = f"{articles}&page={page}"
            html = get_text(link_item)
            soup = BeautifulSoup(html, features="html5lib")
            dev = soup.findAll('div', class_='vacancy-serp-item-body__main-info')
            for z in dev:
                link = z.find('a', class_='serp-item__title')['href']
                try:
                    vacansy = get_vakansy_hh(link)
                except:
                    vacansy = get_vakansy_hh(link)
                if vacansy:
                    list_vacansy.append(vacansy)
            pbar.update(1)
    return list_vacansy

def extract_max_page(URL):
    hh_request = requests.get(URL, headers=get_headers())
    hh_soup = BeautifulSoup(hh_request.text, 'html.parser')
    pages = []
    paginator = hh_soup.find_all("span", {'class': 'pager-item-not-in-short-range'})
    for page in paginator:
        pages.append(int(page.find('a').text))
    return pages[-1]

if __name__ == "__main__":
    json_file = get_link_vakansy_hh("python")
    with open('vacansy.json', 'w') as f:
        json.dump(json_file, f, indent=2, ensure_ascii=False)