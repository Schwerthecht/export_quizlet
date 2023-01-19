import os.path
import sys

import bs4
import requests
from easygui import buttonbox, enterbox, msgbox, fileopenbox
import re


def use_regex(input_text):
    pattern = re.compile(r"https:\/\/quizlet\.com\/\w+\/\d+\/[a-z0-9-]+\/", re.IGNORECASE)
    return pattern.match(input_text)


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
    lang_separator = enterbox(
        "Enter a language separator (example: \"Hi;Hallo\" -> ; is the language separator)\nuse \\t for tab, "
        "\\n for new line",
        "Language Separator", ";")
    cancel_if_none(lang_separator)

    word_separator = enterbox(
        "Enter a word separator (example: \"hi;hallo$you;du\" -> $ is the word separator)\nuse \\t for tab, "
        "\\n for new line",
        "Language Separator", "\\n")
    cancel_if_none(word_separator)

    lang_separator = lang_separator.replace("\\t", "\t").replace("\\n", "\n")
    word_separator = word_separator.replace("\\t", "\t").replace("\\n", "\n")


# --- get requests --- #
res = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

soup = bs4.BeautifulSoup(res.text, 'html.parser')
lang_1_html = soup.find_all('span', class_='TermText notranslate lang-en')
lang_2_html = soup.find_all('span', class_='TermText notranslate lang-de')

lang_1 = [word.text for word in lang_1_html]
lang_2 = [word.text for word in lang_2_html]

dictionary = dict(zip(lang_1, lang_2))

# --- write to file --- #
with open(file, "w", encoding="utf-8") as f:
    if output_format == "txt (choose separators)":
        for word in dictionary:
            f.write(word + lang_separator + dictionary[word] + word_separator)
    elif output_format == "txt (Anki)":
        for word in dictionary:
            f.write(word + ";" + dictionary[word] + "\n")
    elif output_format == "JSON":
        f.write(str(dictionary))
f.close()

msgbox("Done", "Success")
