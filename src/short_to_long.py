import csv
import os


malaria_codes = ['Avoidance of water', 'Mosquito net', 'Mosquito spray', 'Cleanliness/hygiene/sanitation', 'Nutrition', 'Medical  wrong', 'Medication', 'Other', 'Food/Drink', 'Health Services', 'Water']
wash_codes_s02 = ['Unclean food and water', 'Lack of hygeine', 'Lack of sanitation/open defecation', 'Infection', 'Water/Weather', 'Types of Food', 'Other', 'Life-threatening', 'Dangerous (not life threatning)', 'Some type/durations are life-threatening', 'Some people/areas are at greater risk ', 'No harm/good', 'ORS', 'Health services']
wash_codes_s04 = ['Lack of Hygiene', 'Contaminated/Dirty Water', 'Contaminated/Dirty Water (slight misconception about cause of cholera)', 'Poor food preparation/eating practice', 'Type of Food', 'Germs', 'Poor Sanitation/Stool', 'Dirty Environment/Community', 'Poisoned/contaminated weather', 'Weather impacting on water', 'Other Misconceptions', 'Other (Enabler Rather than Cause)', 'Other (Hunger/Malnutrition)']

#with open('../data/WASH [NEW] - Training data 27.02.2017 ID.csv', 'r') as infile, open('../data/wash_training_long_1005.csv', 'w') as outfile:
#with open('../data/Malaria.xlsx - Rukaya - Training Data_1105.csv', 'r') as infile, open('../data/malaria_training_long_1105.csv', 'w') as outfile:
with open('../data/WASH S04E03 - Manual Coding.csv', 'r') as infile, open('../data/wash_s04_training_long_1505.csv', 'w') as outfile:
    reader = csv.DictReader(infile)
    columns = reader.fieldnames
    fieldnames = ['ID', 'phone', 'text'] + wash_codes_s04
    print(fieldnames)
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    for row in reader:
        for column in columns:
            if row[column] in wash_codes_s04:
                row[row[column]] = 1
        writer.writerow(row)



'''
def convert_rows(input_file, output_file, directory='../data', text_col=2, ignore_cols=(), uncoded=('', 'NM'), triples=False):

    msgs = []
    code_sets = []

    with open(os.path.join(directory, input_file + '.csv'), newline='') as f:
        # Process the file as a CSV file
        reader = csv.reader(f)

        # Find the headings (the first row of the file)
        headings = next(reader)
        # Restrict ourselves to a subset of columns (not containing text, and not ignored)
        code_cols = sorted(set(range(len(headings))) - {text_col} - set(ignore_cols))
        # Group columns in pairs
        pair_indices = list(zip(code_cols[::2], code_cols[1::2]))
        pair_names = [headings[i][:-1].strip() for i in code_cols[::2]]

        if triples:
            pair_indices = [(4, 5, 6), (7, 8, 9)]  # 3 reasons in HIV/AIDS data
            pair_names = [headings[i][:-1].strip() for i in code_cols[::3]]

        print('names: ', pair_names)

        # Find features and codes
        for row in reader:
            # Find words in message
            msgs.append(row[text_col])
            # Find codes
            row_code_set = set()
            for name, inds in zip(pair_names, pair_indices):
                # The code is recorded as a tuple (pair_name, value)
                # If a code is repeated, it is only counted once
                row_code_set |= {(name, row[i]) for i in inds if row[i] not in uncoded}
            code_sets.append(row_code_set)

        print(code_sets)


convert_rows('malaria_verified', 'malaria_verified_long', ignore_cols=[0,1,8,9])

'''
