import os
from sklearn.metrics import precision_recall_fscore_support
import pandas


def evaluate(pred, gold, code, filename, verbose=True):
    """
    Calculate the accuracy, precision, recall, and F1 score,
    for a set of predictions, compared to a gold standard
    :param pred: predictions of classifiers
    :param gold: gold standard annotations
    :param verbose: whether to print results (default True)
    :return: accuracy, precision, recall, F1 (each as an array)
    """

    precision, recall, fscore, support = precision_recall_fscore_support(gold, pred, average='binary')

    if verbose:
        print('Precision:', precision)
        print('Recall:', recall)
        print('F1:', fscore)
        print('annotated messages: ', int(gold.sum()))

    with open(os.path.join('../data', filename+'.txt'), 'a') as f:
        f.write('{}\n{}\n{}\n{}\n{}\n\n'.format('label: '+ code, 'Precision: ' + str(precision), 'Recall: ' +str(recall), 'F1: ' + str(fscore), 'verified messages: ' + str(int(gold.sum()))))


def get_prediction_and_gold_vector(prediction_filename, prediction_codename, gold_filename, gold_codename):
    gold_pd = pandas.read_csv(gold_filename)
    gold_pd.fillna(value=0, inplace=True)
    gold_pd = gold_pd.drop_duplicates(subset='ID')

    print(len(gold_pd))
    gold_ids = gold_pd['ID']
    prediction_pd = pandas.read_csv(prediction_filename)
    prediction_pd.fillna(value=0, inplace=True)
    prediction_pd = prediction_pd.drop_duplicates(subset='ID')
    predictions_verified = prediction_pd[
        (prediction_pd['ID'].isin(gold_ids)) & (prediction_pd['source'] == 'prediction')]

    # print('labeled messages verified: ', len(labeled_predictions), '\n')
    print('labeled messages verified: ', len(predictions_verified), '\n')

    # if training data was included in verification, exclude
    pred_ids = predictions_verified['ID']

    verified_to_check = gold_pd[gold_pd['ID'].isin(pred_ids)]

    # align dataframes
    predictions_verified.sort_values(by='ID', inplace=True)

    verified_to_check.sort_values(by='ID', inplace=True)

    # predictions_verified, verified_to_check = predictions_verified.align(verified_to_check, axis=1)

    # get just the predictions from full row
    # predictions_vector = labeled_predictions[prediction_codename]
    predictions_vector = predictions_verified[prediction_codename]
    # prediction_ids = set(labeled_predictions['ID'])
    golds_vector = verified_to_check[gold_codename]

    print('match: ', (predictions_vector == golds_vector).sum(), '\n')

    print('label:', gold_codename, '\n')

    return predictions_vector, golds_vector


if __name__ == "__main__":

    # Read code file
    with open(os.path.join('../data', 'malaria' + '_codes.txt')) as f:
        full_list = []
        for line in f:
            # Get the codes
            parts = line.split('\t')
            code = parts[0]


            predictions, golds = get_prediction_and_gold_vector('../data/malaria_predictions_0905.csv',
                                                                code,
                                                                '../data/malaria_verified_long.csv',
                                                                code)
            # get evaluation metrics
            evaluate(predictions, golds, code ,'malaria_evaluation')
