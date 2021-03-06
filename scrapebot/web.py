import pendulum
import requests
import traceback
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pendulum import datetime, from_format


@dataclass
class PressRelease:
    """Class for keeping track of a particular press release"""

    title: str
    pubdate: datetime
    content: str
    link: str
    relevant: bool = False


def get_press_releases(config, min_date_string, relevant_title_phrases):
    try:
        min_date = from_format(min_date_string, "YYYY-MM-DD")
        press_release_list = []
        url = config["url"]
        pubdate_format = config["pubdateFormat"]
        content_tag = config["contentTag"]
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features="xml")  # "html.parser")
        items = soup.findAll("item")
        # print(items[0])
        # print(items[0].pubDate.text)
        # return
        for item in items:
            pubdate = from_format(item.pubDate.text, pubdate_format)
            if pubdate < min_date:
                break
            # print(pubdate, item.link)
            content = item.find(content_tag).get_text()
            press_release_list.append(
                PressRelease(
                    title=item.title.text,
                    pubdate=pubdate,
                    content=content,
                    link=item.link.text,
                    relevant=False,
                )
            )
            # print(item.description.text)
        return filter_for_relevant_press_releases(
            press_release_list, relevant_title_phrases
        )
    except Exception as e:
        print("get_press_releases() failed. Exception: ")
        print(e)
        traceback.print_exc()


def filter_for_relevant_press_releases(press_release_list, relevant_title_phrases):
    for pr in press_release_list:
        for phrase in relevant_title_phrases:
            if phrase.lower() in pr.title.lower():
                pr.relevant = True
                break  # As long as one phrase was found we mark the PR as selected and stop
    return press_release_list


if __name__ == "__main__":
    prs = get_press_releases(
        "https://news.mt.gov/Home/rss/category/24469/governors-office",
        "2020-11-01",
        ["covid", "pandemic"],
    )
    for pr in prs:
        print(pr.pubdate, pr.relevant, pr.title)
