import pandas as pd
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import re

nltk.download('stopwords')
nltk.download('punkt')

def data_preparation(file_path = '../../data/guidelines/redcross_guidelines.pickle', output_path = 'data/redcross_clean.pickle'):
    
    # Read the text document
    with open(file_path, 'rb') as f:
        docs = pickle.load(f)
    
    doc_list = [{"Text": doc.page_content,
                "Source": doc.metadata["source"],
                "Page": doc.metadata["page"]} for doc in docs]
    
    df = pd.DataFrame(doc_list)
    
    # Tokenize
    df['Tokens'] = df['Text'].apply(word_tokenize)
    
    # stopwords and punctuation lists
    stop_words = set(stopwords.words('english'))
    punctuation_list = [punc for punc in string.punctuation]
    
    # remove from text
    df['Filtered_Text'] = df['Tokens'].apply(lambda tokens: [word for word in tokens if (word.lower() not in stop_words and word.lower() not in punctuation_list)])
    df['Filtered_Text_Combined'] = df['Filtered_Text'].apply(lambda word_list: ' '.join(word_list))
    
    # store output
    with open(output_path, 'wb') as f:
        pickle.dump(df, f)
    print("Data preparation has been stored: " + output_path)
    
    return df


#########################################
# Red Cross clean and contents
#########################################

redcross = data_preparation(file_path = '../../data/guidelines/redcross_guidelines.pickle', 
                            output_path = 'data/redcross_clean.pickle')

# contents
rc_content = '......'.join(redcross["Text"][1:6])
rc_content = rc_content.replace("\n", '.')
rc_content = re.sub('\.+', '|', rc_content)
rc_content = re.sub('\|[0-9]+\|', '', rc_content)
rc_content = re.sub('[0-9]{2,}', '', rc_content).split('|')

# store text output as pickle
with open('data/redcross_content.pickle', 'wb') as f:
    pickle.dump(rc_content, f)


#########################################
# IFRC clean and contents
#########################################
    
ifrc = data_preparation(file_path = '../../data/guidelines/ifrc_guidelines.pickle', 
                        output_path = 'data/ifrc_clean.pickle')

# contents
import re

ifrc_content = '.'.join(ifrc["Text"][4:6])
ifrc_content = ifrc_content.replace("\n", '.')
ifrc_content = re.sub('\.+', '|', ifrc_content)
ifrc_content = re.sub('\x08', ' ', ifrc_content)
ifrc_content = re.sub('[0-9]{2,}', '', ifrc_content).split('|')
ifrc_content = [re.sub('\s+$', '', item) for item in ifrc_content]

# store text output as pickle
with open('data/ifrc_content.pickle', 'wb') as f:
    pickle.dump(ifrc_content, f)

