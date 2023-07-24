import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
import csv
import argparse


def get_url_from_user():
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    while True:
        url = input("Website URL: ")
        if re.match(pattern, url):
            return url
        print("Invalid URL format. Accepted format: http(s)://example.com")


def crawl(url, writer, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()

    try:
        resp = requests.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")
        print("Crawling:", url)

        path = url.replace(urlparse(url).scheme + '://' +
                           urlparse(url).netloc + '/', '/')
        size_in_kb = round(len(resp.content) / 1024)
        writer.writerow({'Path': path, 'Page size (KB)': size_in_kb})

        visited_urls.add(url)

        links = {
            urljoin(url, link['href'])
            for link in soup.find_all('a', href=True)
            if urlparse(urljoin(url, link['href'])).netloc == urlparse(url)
            .netloc and not urlparse((link['href'])).fragment
        }

        for link in links:
            if link not in visited_urls:
                crawl(link, writer, visited_urls)

    except requests.exceptions.RequestException as e:
        raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a website and save page sizes to csv.")
    parser.add_argument('url', type=str, nargs='?',
                        help='Website URL to crawl.')
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = get_url_from_user()

    file_name = 'crawled_pages_sizes.csv'

    with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Path', 'Page size (KB)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        try:
            crawl(url, writer)

            print("\n********************************************************")
            print("Crawling completed for URL:", url)
            print("Data saved to", file_name)
            print("********************************************************\n")

        except requests.exceptions.RequestException as e:
            print("Error fetching page:", e)
