import pandas as pd
import nltk
from nltk import FreqDist
import matplotlib.pyplot as plt
import spacy
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
import pickle

def stats(o, file_path = 'data/redcross_clean.pickle'):

    # Read the text document
    with open(file_path, 'rb') as f:
        df = pickle.load(f)

    # Basic statistics
    print("Number of rows:", len(df), file=o)
    print("Number of unique values:", df['Text'].nunique(), file=o)

    # Text length analysis
    df['Text_Length'] = df['Text'].apply(len)
    print("Maximum text length:", df['Text_Length'].max(), file=o)
    print("Minimum text length:", df['Text_Length'].min(), file=o)
    print("Average text length:", df['Text_Length'].mean(), file=o)

    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")

    # Analyze sentences
    df['Sentences'] = df['Text'].apply(lambda text: [str(sent) for sent in nlp(text).sents])

    # Sentence-level statistics
    df['Num_Sentences'] = df['Sentences'].apply(len)
    print("Average number of sentences:", df['Num_Sentences'].mean(), file=o)



# apply to redcross
with open("data/redcross_stats.txt", "a") as o:
    stats(o, file_path = 'data/redcross_clean.pickle')

# apply to ifrc
with open("data/ifrc_stats.txt", "a") as o:
    stats(o, file_path = 'data/ifrc_clean.pickle')