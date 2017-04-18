import csv, pickle, numpy as np
from collections import Counter

from logistic import evaluate, predict
from features import bag_of_words, vectorise, apply_to_parts

#name, weeks, code_columns = 'wash', '12', range(8, 25)
#name, weeks, code_columns = 'delivery', '34', range(2, 19)
#name, weeks, code_columns = 'nutrition', '5', range(3, 13)
#name, weeks, code_columns = 'malaria', '67', range(2, 12)
name, weeks, code_columns = 'hiv_aids', '8', range(3, 18)


# Get the unlabelled data, excluding training set

msgs = []
training = []

with open('../data/mediaink_s03_9weeks_2002.xls', newline='') as f, open('../data/HIV_AIDS coding - Training data (NEW - 13.02.17)_final.csv', newline='') as trainingf:
    reader = list(csv.reader(f, delimiter='\t'))
    training_reader = list(csv.reader(trainingf))
    mids = [row[0] for row in training_reader]
    headings = reader[0]

    for row in reader:
        if row[4] in weeks and row[0] not in mids:
                msgs.append(row)


# Vectorise the data

with open('../data/{}_features.pkl'.format(name), 'rb') as f:
    feats = pickle.load(f)
feat_list = [x for x,_ in feats]
feat_dict = {x:i for i,x in enumerate(feat_list)}

featurise = apply_to_parts(bag_of_words, '&&&')
feat_vecs = vectorise([featurise(x[5]) for x in msgs], feat_dict)
# Load the classifiers and codes

with open('../data/{}_C1.pkl'.format(name), 'rb') as f:
    classifiers = pickle.load(f)

with open('../data/{}_codes.pkl'.format(name), 'rb') as f:
    codes = pickle.load(f)
code_names = [x for x,_ in codes]
print(code_names)
headings.extend(code_names)

# Make predictions

predictions = predict(classifiers, feat_vecs)
for i, m in enumerate(msgs):
    m.extend([1 if x else '' for x in predictions[i]])

"""
def add_training_messages_pairs():
    pair_indices = [(4, 5, 6), (7, 8, 9)]  # HIV/AIDS triples
    pair_names = [headings[i][:-1].strip() for i in code_cols[::3]]
    print('names: ', pair_names)

    # Find features and codes
    for row in reader:
        # Find codes
        row_code_set = set()
        for name, inds in zip(pair_names, pair_indices):
            # The code is recorded as a tuple (pair_name, value)
            # If a code is repeated, it is only counted once
            row_code_set |= {(name, row[i]) for i in inds if row[i] not in uncoded}
        code_sets.append(row_code_set)

"""
"""
training_messages = []
def add_training_messages(code_columns):
    for row in reader:
        if row[4] in weeks and row[0] in mids:
            for trow in training_reader:
                if row[0] == trow[0]:
                    row.extend([trow[c] for c in code_columns])
                    row.extend(['training'])
                    training_messages.append(row)

add_training_messages(code_columns)
"""

# Save the data with the predictions

with open('../data/{}_predictions_2002_final.csv'.format(name), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    writer.writerows(msgs)
    #writer.writerows(training_messages)
