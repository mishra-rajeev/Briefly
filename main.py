# importing libraries
from flask import Flask, render_template, request
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
import bs4 as BeautifulSoup
import urllib.request
import re


def article_content_generator(word):
    #word = "bollywood"
    Input_words = word.replace(' ', '_')
    makeurl = 'https://en.wikipedia.org/wiki/' + Input_words
    # fetching the content from the URL
    fetched_data = urllib.request.urlopen(makeurl)

    article_read = fetched_data.read()

    # parsing the URL content and storing in a variable
    article_parsed = BeautifulSoup.BeautifulSoup(article_read, 'html.parser')

    #returning <p> tags
    paragraphs = article_parsed.find_all('p')

    article_content = ''

    # looping through the paragraphs and adding them to the variable
    for p in paragraphs:
        article_content += p.text

    return article_content

def _create_dictionary_table(text_string) -> dict:

    # removing stop words
    stop_words = set(stopwords.words("english"))

    words = word_tokenize(text_string)

    # reducing words to their root form
    stem = PorterStemmer()

    # creating dictionary for the word frequency table
    frequency_table = dict()
    for wd in words:
        wd = stem.stem(wd)
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table


def _calculate_sentence_scores(sentences, frequency_table) -> dict:

    # algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:7] in sentence_weight:
                    sentence_weight[sentence[:7]
                                    ] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]
                                    ] = frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]
                                                        ] / sentence_wordcount_without_stop_words

    return sentence_weight

def _calculate_average_score(sentence_weight) -> int:

    # calculating the average score for the sentences
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]

    # getting sentence average value from source text
    average_score = (sum_values / len(sentence_weight))

    return average_score


def _get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1

    return article_summary

def _run_article_summary(article):

    article_content = article_content_generator(article)

    # creating a dictionary for the word frequency table
    frequency_table = _create_dictionary_table(article_content)

    # tokenizing the sentences
    sentences = sent_tokenize(article_content)

    # algorithm for scoring a sentence by its words
    sentence_scores = _calculate_sentence_scores(sentences, frequency_table)

    # getting the threshold
    threshold = _calculate_average_score(sentence_scores)

    # producing the summary
    article_summary = _get_article_summary(
        sentences, sentence_scores, 1.15 * threshold)

    return article_summary


app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/summarize")
def summarize():
    form_input = request.args.get('text')

    r = _run_article_summary(form_input)
    # Using regex to remove [alphanumaric] or [umaric]umaric] or[umaric][numaric][numaric]
    r = re.sub(r'(\[[0-9 a-z]\]|\[[0-9][0-9]\]|\[[0-9][0-9][0-9]\])', ' ', r)

    if r != '':
        return render_template('summarize.html', x=form_input, r=r, t='s')
    else:
        return render_template('summarize.html', x=form_input, r=r, t='l')


if __name__ == '__main__':
    app.run(debug=True)
