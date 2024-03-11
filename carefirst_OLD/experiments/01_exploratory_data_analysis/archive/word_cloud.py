from wordcloud import WordCloud
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# Read the text document
file_path = 'data/redcross_clean.pickle'

with open(file_path, 'rb') as f:
   df = pickle.load(f)

# Generate a word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(df['Filtered_Text_Combined']))

# Plot the word cloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
