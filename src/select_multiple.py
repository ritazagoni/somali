import csv, pickle, numpy as np
from collections import Counter

from features import bag_of_words, vectorise, apply_to_parts
from active import score_by_uncertainty, top_N

#name, weeks = 'wash', '12'
#name, weeks = 'delivery', '34'
#name, weeks = 'nutrition', '5'
name, weeks = 'malaria', '67'


# Get the unlabelled data

msgs = []
with open('../data/malaria_full.csv', newline='') as f, open('../data/malaria_training_long_0905.csv', newline='') as trainingf:
    reader = list(csv.reader(f))
    headings = reader[0]

    training_reader = list(csv.reader(trainingf))
    mids = [row[0] for row in training_reader]
    
    for row in reader:
        if row[4] in weeks and row[0] not in mids:
            msgs.append(row)

# Vectorise the data

with open('../data/{}_features.pkl'.format(name), 'rb') as f:
    feats = pickle.load(f)
feat_list = [x for x,_ in feats]
feat_dict = {x:i for i,x in enumerate(feat_list)}

featurise = apply_to_parts(bag_of_words, '<$$$>')
feat_vecs = vectorise([featurise(x[4]) for x in msgs], feat_dict)

# Load the classifiers and codes

with open('../data/{}_C1.pkl'.format(name), 'rb') as f:
    classifiers = pickle.load(f)

with open('../data/{}_codes.pkl'.format(name), 'rb') as f:
    codes = pickle.load(f)
code_names = [x for x,_ in codes]
#headings.extend(code_names)

# Choose which datapoints to annotate next

scores = score_by_uncertainty(feat_vecs, classifiers)
top = top_N(scores, 10000)

# Save the data with the predictions

with open('../data/{}_top10000.csv'.format(name), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    writer.writerows([msgs[i] for i in top])
