import csv, pickle, numpy as np
#from collections import Counter

from logistic import predict
from features import bag_of_words, vectorise, apply_to_parts

name, weeks, code_columns = 'wash', '12', range(3, 17)
#name, weeks, code_columns = 'delivery', '34', range(2, 19)
#name, weeks, code_columns = 'nutrition', '5', range(3, 13)
#name, weeks, code_columns = 'malaria', '67', range(3, 14)
#name, weeks, code_columns = 'hiv_aids', '8', range(3, 18)





# Get the unlabelled data, excluding training set

msgs = []
training = []


with open('../data/messages_beliefs_s02_full_1804.csv', newline='') as f, open('../data/wash_training_long_1005.csv', newline='') as trainingf:
#with open('../data/malaria_full.csv', newline='') as f, open('../data/malaria_training_long_1105.csv', newline='') as trainingf:
    reader = list(csv.reader(f)) #, delimiter='\t'))
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
headings.extend(['source'])

# Make predictions

predictions = predict(classifiers, feat_vecs)
for i, m in enumerate(msgs):
    m.extend([1 if x else '' for x in predictions[i]])
    m.extend(['prediction'])


seen_messages = set()
training_messages = []

def add_training_messages(code_columns):
    for row in reader[1:]:
        if row[0] in mids:
            for trow in training_reader:
                if row[0] == trow[0]:
                    if row[0] in seen_messages:
                        continue
                    seen_messages.add(row[0])
                    row.extend([trow[c] for c in code_columns])
                    row.extend(['training'])
                    training_messages.append(row)

add_training_messages(code_columns)

# Print overall counts for each code

all_messages = msgs + training_messages

#print([sum(message[column] for message in all_messages for column in code_columns)])


for i, column in enumerate(code_columns):
    print(column)
    print(code_names[i])

    print(code_names[i] + ': ' + str(sum(message[column] for message in all_messages)))

# Save the data with the predictions

with open('../data/{}_predictions_1505.csv'.format(name), 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    writer.writerows(msgs)
    writer.writerows(training_messages)
