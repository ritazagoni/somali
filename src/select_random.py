import pandas
import sys

# exclude Non-Relevant as code
name, code_colums = 'wash', list(range(14, 26))

predictions_df = pandas.read_csv(sys.argv[1])

# random sample of full size
predictions_df = predictions_df.sample(frac=1)


# select rows where any of codes is not empty
#rows_with_code = predictions_df[(predictions_df[code_colums].notnull().any(axis=1)) & (predictions_df['source'] == 'prediction')]
rows_with_code = predictions_df[predictions_df['source'] == 'prediction']

print(len(rows_with_code))

verification_set = rows_with_code[:1000]

columns = [0,1,5].extend(code_colums)

verification_set.to_csv('../data/' + name + '_s04_verification_random.csv', index=False, columns=columns)
