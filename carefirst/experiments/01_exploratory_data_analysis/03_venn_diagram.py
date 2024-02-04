import pickle
from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from matplotlib_venn_wordcloud import venn2_wordcloud

# Read the redcross content
with open('data/redcross_content.pickle', 'rb') as f:
    rc_content = pickle.load(f)

# Read the redcross content
with open('data/ifrc_content.pickle', 'rb') as f:
    ifrc_content = pickle.load(f)

#########################################
# Venn diagram of content overlap
#########################################

list1 = set(rc_content) 

# read in chatgpts mapping of similar content
with open('data/chatgpt_mapping.txt') as f:
    # Read the contents of the file into a variable
    matching_dict = f.read()

matching_dict = eval(matching_dict)

list2 = []

for i in ifrc_content:
    try:
        list2.append(matching_dict[i])
        print("Updated name")
    except:
        list2.append(i)
        print("Kept previous name")

list2 = set(list2)

# numeric venn diagram
venn_diagram = venn2([list1, list2], set_labels=('Red Cross', 'Internation First Aid, Resuscitation, and Education'))
plt.show()

# wordcloud venn diagram
venn2_wordcloud([list1, list2])

plt.show()