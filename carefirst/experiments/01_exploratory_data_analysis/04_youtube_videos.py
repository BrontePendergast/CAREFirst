import json
import pandas as pd
 
# Opening JSON file
f = open('../../data/youtube_videos/Med-Instr-Hierarchical/train.json')
vids_train = json.load(f)

print(f"Total number of medical videos: {len(vids_train)}")

first_aid = []

# collect first aid videos
for vid in vids_train:
    if "FIRST AID" in vid["level_1_category_labels"]:
        first_aid.append(vid)

print(f"Total number of first aid videos: {len(first_aid)}")

# for EDA purposes, select one category only
df = pd.DataFrame(first_aid)
df['category'] = df['level_2_category_labels'].apply(lambda row: row[0])

# export counts for graph
df['category'].value_counts()
