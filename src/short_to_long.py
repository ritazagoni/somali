import csv

malaria_codes = ['Avoidance of water', 'Mosquito net', 'Mosquito spray', 'Cleanliness/hygiene/sanitation', 'Nutrition', 'Medical  wrong', 'Medication', 'Other', 'Food/Drink', 'Health Services', 'Water']
wash_codes_s02 = ['Unclean food and water', 'Lack of hygeine', 'Lack of sanitation/open defecation', 'Infection', 'Water/Weather', 'Types of Food', 'Other', 'Life-threatening', 'Dangerous (not life threatning)', 'Some type/durations are life-threatening', 'Some people/areas are at greater risk ', 'No harm/good', 'ORS', 'Health services']
wash_codes_s04 = ['Lack of Hygiene', 'Contaminated/Dirty Water', 'Contaminated/Dirty Water (slight misconception about cause of cholera)', 'Poor food preparation/eating practice', 'Type of Food', 'Germs', 'Poor Sanitation/Stool', 'Dirty Environment/Community', 'Poisoned/contaminated weather', 'Weather impacting on water', 'Other Misconceptions', 'Other (Enabler Rather than Cause)', 'Other (Hunger/Malnutrition)', 'Non-Relevant']

#with open('../data/WASH [NEW] - Training data 27.02.2017 ID.csv', 'r') as infile, open('../data/wash_training_long_1005.csv', 'w') as outfile:
#with open('../data/Malaria.xlsx - Rukaya - Training Data_1105.csv', 'r') as infile, open('../data/malaria_training_long_1105.csv', 'w') as outfile:
with open('../data/WASH S04E03 - Manual Coding.csv', 'r') as infile, open('../data/wash_s04_training_long_1705.csv', 'w') as outfile:

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


