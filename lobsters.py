import json
import os

import tqdm
import tracery
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.nn import Classifier
from jinja2 import Template
import mf2py

LOBSTERSTOP_STORIES = "https://lobste.rs/"


def get_front_page() -> list:
    stories = mf2py.parse(url=LOBSTERSTOP_STORIES)

    return [story["properties"]["repost-of"][0]["properties"]["name"][0] for story in stories["items"]]

with open("stories.json", "w") as f:
    json.dump(get_front_page(), f)

with open("stories.json", "r") as f:
    stories = json.load(f)

nouns = []
adjectives = []
verbs = []
proper_nouns = []
years = []

tagger = SequenceTagger.load("flair/pos-english")
ner_tagger = Classifier.load("ner")

word_to_title = {}

for heading in tqdm.tqdm(stories):
    sentence = Sentence(heading)
    ner_tagger.predict(sentence)

    for entity in sentence.get_spans("ner"):
        word_to_title[entity.text.lower()] = heading

        heading = [w for w in heading.split(" ") if w.lower() != entity.text.lower()]
        heading = " ".join(heading)

    sentence = Sentence(heading)
    tagger.predict(sentence)

    for entity in sentence:
        if entity.text.isdigit() and len(entity.text) == 4:
            years.append(entity.text)
            continue

        if len(entity.text) < 2 or not entity.text.isalpha():
            continue

        if entity.tag in ["NN", "NNS"]:
            nouns.append(entity.text.lower())
        elif entity.tag in ["JJ", "JJR", "JJS"]:
            adjectives.append(entity.text.lower())
        elif entity.tag in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            verbs.append(entity.text.lower())
        else:
            continue

        word_to_title[entity.text.lower()] = heading

grammar = tracery.Grammar(
    {
        "origin": [
            "the #adjective# #noun# of #noun#",
            "for all the #adjective# #noun#",
            "my heart, #noun#",
            "my #noun# is #adjective#",
            "like a #noun# in the #noun#",
            "from #propernoun#, I learned #noun#",
            "a #adjective# #propernoun#",
            "be #adjective# and #adjective#",
            "in #years#, #noun#",
        ],
        "adjective": adjectives,
        "verb": verbs,
        "noun": nouns,
        "propernoun": proper_nouns + ["Lobste.rs"],
        "years": years,
    }
)

lobsters_poetry = [grammar.flatten("#origin#") for _ in range(len(stories))]

lobsters_poetry = list(set(lobsters_poetry))


poems = []

# if "a" then word that starts with a vowel, add an "n"
for title in lobsters_poetry:
    words = title.split(" ")
    if title.split(" ")[0].lower() == "a":
        if title.split(" ")[1][0].lower() in "aeiou":
            title = "an " + title[2:]
    poems.append(title)

poems = {title: {"title": title, "components": set()} for title in poems}

for title, poem in poems.items():
    for word in title.split(" "):
        if word.lower() in word_to_title:
            poem["components"].add(word_to_title[word.lower()])

for title, poem in poems.items():
    poem["components"] = list(poem["components"])

poems = list(poems.values())

with open("poetry.html", "r") as f:
    template = Template(f.read())

with open("index.html", "w") as f:
    f.write(template.render(posts=poems))

os.system("mv -f index.html /var/www/lobsterspoetry/")
