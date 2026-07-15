import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_html(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке: {e}")
        return None

def get_all_quotes(_base_url):
    page = 1
    max_page = 20
    all_quotes = []

    while True:
        url = f"{_base_url}page/{page}/"
        html = get_html(url)
        if html is None:
            print('Не удалось загрузить страницу, остановка.')
            break
        print(f'Парсим. Страница {page}')
        quotes = parse_quotes(html)
        if not quotes:
            print(f"Страница {page} пустая, цитаты закончились")
            break
        for quote in quotes:
            quote_final = quote.find('span', class_='text')
            all_quotes.append(quote)
            print(quote_final.text.strip())
        page+=1
        if page >=max_page:
            break
        time.sleep(2)
    print(f"Всего собрано: {len(all_quotes)} цитат")
    return all_quotes

def parse_quotes(html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        quotes = soup.find_all('div', class_='quote')
        return quotes
    except FileNotFoundError:
        print("Файл quotes.toscrape.html не найден")
        return []
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

def save_json(quotes):
    try:
        data = {
                'quotes.toscrape': []
            }

        for quote in quotes:
            quote_final = quote.find('span', class_='text')
            author = quote.find('small', class_='author')

            tags = quote.find_all('a', class_='tag')
            tags_list = [tag.text for tag in tags]

            if quote_final and author:
                data['quotes.toscrape'].append({
                    'text': quote_final.text.strip(),
                    'author': author.text.strip(),
                    'tags': tags_list
                })
            else: 
                print("Пропущена цитата: не найден текст или автор")

            print(f'{quote_final.text.strip()}\nАвтор: {author.text.strip()}\n')

        with open('quotes.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Данные сохранены в файл quotes.json. Всего цитат: {len(data['quotes.toscrape'])}")

    except PermissionError:
        print("Нет прав на запись файла")
    except OSError as e:
        print(f"Ошибка при записи файла: {e}")

def save_as_csv(quotes):
    try:
        with open('quotes_csv.csv', 'w', encoding='utf-8', newline='')as f:
            writer = csv.writer(f)
            writer.writerow(['Цитата', 'Автор', 'Теги' ])

            for quote in quotes:
                quote_final = quote.find('span', class_='text')
                author = quote.find('small', class_='author')

                tags = quote.find_all('a', class_='tag')
                tags_list = [tag.text for tag in tags]
                writer.writerow([quote_final.text.strip(), author.text.strip(), ', '.join(tags_list)])
        print('Задачи экспортированы в quotes_csv.csv')
    except PermissionError:
        print("Нет прав на запись файла")

def sort_by_tag():
    with open('quotes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        quotes = data['quotes.toscrape']
        all_tags = []
        for quote in quotes:
            tags = quote['tags']
            all_tags.extend(tags)
        unique_tags = sorted(set(all_tags))
        print(unique_tags)

        for tag in unique_tags:
            quotes_with_tag = [quote for quote in quotes if tag in quote['tags']]
            print(f"\n{tag}:")
            for quote in quotes_with_tag:
                print(f"   • {quote['text']} — {quote['author']}")


def main():
        url = 'https://quotes.toscrape.com/'
        quotes = get_all_quotes(url) 
        if quotes is None:
            print("Не удалось загрузить страницу, программа завершена")
            return
        if not quotes:
            print("Не удалось собрать цитаты, программа завершена")
            return
        time.sleep(1)
        answer = input('Хотите ли вы экспортировать цитаты? \nY/N\n').upper()
        if answer == 'Y':
            answer_about_export = input('Принято, в каком формате вы хотите экспортировать?\n==Варианты==\n1 - CSV\n2 - JSON\n')
            if answer_about_export == '1':
                time.sleep(1)
                save_as_csv(quotes)
            elif answer_about_export == '2':
                time.sleep(1)
                save_json(quotes)
            else:
                print('Нет такого варианта ответа, попробуйте снова')
            answer_about_sort = input('Нужно ли сортировать все цитаты по тегам?\nВНИМАНИЕ! Для данной операции потребуется экспортировать JSON\nY/N\n').upper()
            if answer_about_sort == 'Y':
                is_file_exist = os.path.exists('quotes.json')
                if is_file_exist == True:
                    time.sleep(1)
                    sort_by_tag()
                elif is_file_exist == False:
                    print('Создаём файл JSON..')
                    time.sleep(1)
                    save_json(quotes)
                    sort_by_tag()
                else: 
                    print('Нет такого варианта ответа, попробуйте снова')
            elif answer_about_sort == 'N':
                print('Принято\nПрограмма завершена')
            else:
                print('Нет такого варианта ответа, попробуйте снова')

main()
