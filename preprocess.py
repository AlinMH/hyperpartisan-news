import re

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from tqdm import tqdm

TRAINING_FILE = "data/articles-training-bypublisher-20181122/articles-training-bypublisher-20181122.xml"
VALIDATION_FILE = "data/articles-validation-bypublisher-20181122/articles-validation-bypublisher-20181122.xml"

FLAGS = re.MULTILINE | re.DOTALL


def re_sub(pattern, repl, text, flags=None):
    if flags is None:
        return re.sub(pattern, repl, text, flags=FLAGS)
    else:
        return re.sub(pattern, repl, text, flags=(FLAGS | flags))


def preprocess_data():
    preprocessed_dict = {}
    print("Loading data from xml")
    with open(TRAINING_FILE, "r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp, features="lxml")
        articles = soup.find_all('article')
        print("Number of articles: ", len(articles))

        for a in tqdm(articles):
            id, article = parse_xml(a)
            print(id)
            print(article)
            preprocessed_dict[id] = article
            break

    # print(preprocessed_dict)


def parse_xml(article):
    # get meta data
    id = article.get('id')
    date = article.get('published-at')
    title = article.get('title')

    # get external link info
    external_links, internal_count = [], 0
    for link in article.find_all('a'):
        if str(link.get('type')) == 'internal':
            internal_count += 1
        else:
            external_links.append(link.get('href'))

    # get actual text
    article_text = article.get_text()
    article_text = clean_txt(article_text)

    result = [id, {'date': date, 'title': title, 'internal': internal_count, 'external': external_links,
                   'article_text': article_text}]
    return result


def clean_txt(text,
              remove_stopwords=False,
              remove_nonalphanumeric=True,
              use_number_special_token=True,
              remove_numbers=False):
    text = text.lower()
    text = re.sub(r"-", " ", text)
    text = re.sub(r"[a-zA-Z]+\/[a-zA-Z]+", " ", text)
    text = re.sub(r"\n", " ", text)

    if use_number_special_token:
        text = re_sub(r"[-+]?[.\d]*[\d]+[:,.\d]*", "numberplaceholder", text)
    elif remove_numbers:
        text = re_sub(r"[-+]?[.\d]*[\d]+[:,.\d]*", "", text)

    if remove_stopwords:
        text = text.split()
        stops = set(stopwords.words("english"))
        text = [w for w in text if w not in stops]
        text = " ".join(text)

    # Remove URL
    text = re_sub(r"(http)\S+", "", text)
    text = re_sub(r"(www)\S+", "", text)
    text = re_sub(r"(href)\S+", "", text)
    # Remove multiple spaces
    text = re_sub(r"[ \s\t\n]+", " ", text)

    # remove repetition
    text = re_sub(r"([!?.]){2,}", r"\1", text)
    text = re_sub(r"\b(\S*?)(.)\2{2,}\b", r"\1\2", text)

    return text.strip()


preprocess_data()
