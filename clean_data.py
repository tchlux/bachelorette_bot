
import pandas as pd
d = pd.read_csv("bachelorette.csv")

# Get the unique seasons in which each label occurs.
label_frequency = {}
for season,label in zip(d["Season"],d["Label"]):
    label_frequency[label] = label_frequency.get(label,set()) | {season}

# Count the number of seasons that each label occurs in.
label_seasons = {s:len(l) for (s,l) in label_frequency.items()}

# Remove all the label entries that occur in fewer than 5 seasons.
labels_to_remove = {s for s in sorted(label_seasons)
                    if label_seasons[s] < 5}

# Get the rows that will be kept.
row_indices_to_keep = [i for i in range(len(d))
                       if d["Label"][i] not in labels_to_remove]

print(d)

clean_data = d.iloc[row_indices_to_keep]

print(clean_data)

for row in sorted(set(clean_data["Label"])):
    print(row)



# 
