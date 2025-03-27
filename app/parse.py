import csv
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def from_csv_row(cls, row: list[str]) -> "Quote":
        text, author, tags_str = row
        tags = tags_str.split(", ") if tags_str else []
        return cls(text, author, tags)


def get_quotes() -> list[Quote]:
    quotes = []
    page = 1

    while True:
        url = urljoin(BASE_URL, f"page/{page}/")
        response = requests.get(url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        page_quotes = soup.find_all("div", class_="quote")

        if not page_quotes:
            break

        for quote in page_quotes:
            text = quote.find("span", class_="text").get_text(strip=True)
            author = quote.find("small", class_="author").get_text(strip=True)
            tags = [
                tag.get_text(strip=True) for tag in quote.find_all(
                    "a", class_="tag"
                )
            ]
            quotes.append(Quote(text, author, tags))

        page += 1
        time.sleep(1)

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
