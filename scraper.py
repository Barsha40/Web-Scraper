
import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from datetime import datetime


URL = "https://news.ycombinator.com/"
USER_AGENT = "StudentWebScraper/1.0"


def check_robots_permission(url):
    """Check whether scraping is allowed by robots.txt."""

    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    try:
        response = requests.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=10
        )
        response.raise_for_status()

        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.text.splitlines())

        return parser.can_fetch(USER_AGENT, url)

    except requests.exceptions.RequestException as error:
        print("Could not check robots.txt:", error)
        return False


def scrape_headlines():

    if not check_robots_permission(URL):
        print("Scraping is not allowed or robots.txt could not be checked.")
        return

    # Small delay before fetching the webpage
    time.sleep(2)

    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find headline elements
        headline_elements = soup.find_all(
            "span", class_="titleline"
        )

        headlines = []

        for element in headline_elements:
            link = element.find("a")

            if link:
                title = link.get_text(strip=True)
                url = link.get("href", "")

                headlines.append({
                    "Headline": title,
                    "URL": url,
                    "Date": datetime.now().strftime("%Y-%m-%d")
                })

        if not headlines:
            print("No headlines found.")
            return

        # Save headlines to CSV
        with open(
            "headlines.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=["Headline", "URL", "Date"]
            )

            writer.writeheader()
            writer.writerows(headlines)

        print(f"\nSuccessfully scraped {len(headlines)} headlines!")
        print("Saved to headlines.csv")

        for item in headlines:
            print("-", item["Headline"])

    except requests.exceptions.RequestException as error:
        print("Network error:", error)


def main():
    print("===== WEB SCRAPER =====")
    scrape_headlines()


if __name__ == "__main__":
    main()
