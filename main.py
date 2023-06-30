import json
import os.path
import sys

import bs4
import cloudscraper as cloudscraper
from easygui import buttonbox, enterbox, msgbox, fileopenbox
import re


def use_regex(input_text):
    pattern = re.compile(r"https:\/\/quizlet\.com\/\w+\/\d+\/[a-z\d-]+\/", re.IGNORECASE)
    pattern2 = re.compile(r"https:\/\/quizlet.com\/\d+\/[a-z\d-]+\/", re.IGNORECASE)
    return pattern.match(input_text) or pattern2.match(input_text)


def cancel_if_none(element):
    if element is None:
        msgbox("Cancelled", "Error")
        sys.exit()


# --- GUI/User Input --- #
url = enterbox("Enter a URL to a Quizlet Set", "Quizlet URL")

cancel_if_none(url)

while not use_regex(url):
    msgbox("Invalid URL", "Error")
    url = enterbox("Enter a URL to a Quizlet Set", "Quizlet URL")
    cancel_if_none(url)

file = fileopenbox("Choose a file to open", "Open File", os.path.dirname(__file__) + "\\export.txt", "*.txt", multiple=False)
cancel_if_none(file)

output_format = buttonbox("Choose an output format", "Output Format", ["txt (choose separators)", "txt (Anki)", "JSON"])
cancel_if_none(output_format)

if output_format == "txt (choose separators)":
    word_definition_separator = enterbox(
        "Enter a word-definition separator (example: \"Hi;Hallo\" -> ; is the word-definition separator)\nuse \\t for "
        "tab, \\n for new line Word Definition Separator", ";")
    cancel_if_none(word_definition_separator)

    word_nextword_seperator = enterbox(
        "Enter a word-nextword separator (example: \"hi;hallo$you;du\" -> $ is the word-nextword separator)\nuse \\t "
        "for tab, \\n for new line Word Nextword Separator", "\\n")
    cancel_if_none(word_nextword_seperator)

    word_definition_separator = word_definition_separator.replace("\\t", "\t").replace("\\n", "\n")
    word_nextword_seperator = word_nextword_seperator.replace("\\t", "\t").replace("\\n", "\n")


# --- get requests --- #
scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
content = scraper.get(url)

soup = bs4.BeautifulSoup(content.text, 'html.parser')
outer_json = soup.find('script', {"id": "__NEXT_DATA__"}).text
inner_json = json.loads(json.loads(outer_json)["props"]["pageProps"]["dehydratedReduxStateKey"])["setPage"]["termIdToTermsMap"]

words = [value['word'] for key, value in inner_json.items()]
definitions = [value['definition'] for key, value in inner_json.items()]


dictionary = dict(zip(words, definitions))

# --- write to file --- #
with open(file, "w", encoding="utf-8") as f:
    if output_format == "txt (choose separators)":
        for word in dictionary:
            f.write(word + word_definition_separator + dictionary[word] + word_nextword_seperator)
    elif output_format == "txt (Anki)":
        for word in dictionary:
            f.write(word + ";" + dictionary[word] + "\n")
    elif output_format == "JSON":
        f.write(str(dictionary))
f.close()

msgbox("Done", "Success")
