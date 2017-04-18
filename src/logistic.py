import pickle, os, numpy as np
from sklearn import linear_model
import pandas

def train(features, codes, penalty='l1', C=1):
    """
    Train logistic regression classifiers,
    independently for each code 
    :param features: input matrix
    :param codes: output matrix
    :param penalty: type of regularisation (l1 or l2)
    :param C: inverse of regularisation strength
    :return: list of classifiers
    """
    classifiers = []
    # Iterate throgh each code (i.e. each column of codes matrix)
    for code_i in codes.transpose():
        # Define a logistic regression model for each code
        model = linear_model.LogisticRegression(
            penalty=penalty,
            C=C)
        # (Could use class_weight to make positive instances more important...)
        
        if code_i.sum() > 1:  # Make sure there is more than one training example
            # Train the model
            model.fit(features, code_i)
            
            classifiers.append(model)
        
        else:
            classifiers.append(None)
    
    return classifiers


def train_on_file(input_name, output_suffix=None, directory='../data', **kwargs):
    """
    Train logistic regression classifiers on a file 
    :param input_name: name of input file (without .pkl file extension)
    :param output_suffix: string to append to name of output file
    (if none is given, no file is saved)
    :param directory: directory of data files (default ../data)
    :param **kwargs: additional keyward arguments will be passed to train
    :return: features, codes, classifiers
    """
    # Load features and codes
    with open(os.path.join(directory, input_name+'.pkl'), 'rb') as f:
        features, codes = pickle.load(f)
    # Train model
    classifiers = train(features, codes, **kwargs)
    # Save model
    if output_suffix:
        with open(os.path.join(directory, '{}_{}.pkl'.format(input_name, output_suffix)), 'wb') as f:
            pickle.dump(classifiers, f)
    #print(features, codes, classifiers)
    return features, codes, classifiers


def predict(classifiers, messages):
    """
    Apply a number of classifiers to a number of messages,
    returning the most likely result for each classfier ond message
    :param classifiers: classifier or list of classifiers
    :param messages: feature vectors (as a matrix)
    :return: array of predictions
    """
    # If more than one classifier is given, apply each
    if isinstance(classifiers, list):
        # Get the predictions from each classifier, giving zeros when a classifier is None
        predictions = [c.predict(messages) if c is not None else np.zeros(len(messages)) for c in classifiers]
        # Transpose so that the shape is (n_datapoints, n_classifiers)

        return np.array(predictions, dtype='bool').transpose()
    else:
        return classifiers.predict(messages)

def predict_prob(classifiers, messages):
    """
    Apply a number of classifiers to a number of messages,
    returning the probability of predicting each code for each message
    :param classifiers: classifier or list of classifiers
    :param messages: feature vectors (as a matrix)
    :return: array of probabilities
    """
    # If more than one classifier is given, apply each
    if isinstance(classifiers, list):
        # Get the prediction probabilities from each classifier
        # c.predict_proba returns probabilities for [False, True]
        # taking [:,1] will just give us probability of True
        prob = [c.predict_proba(messages)[:,1] if c is not None else np.zeros(len(messages)) for c in classifiers]
        # Transpose so that the shape is (n_datapoints, n_classifiers)
        return np.array(prob).transpose()
    else:
        return classifiers.predict_proba(messages)[:,1]


def evaluate(pred, gold, verbose=True):
    """
    Calculate the accuracy, precision, recall, and F1 score,
    for a set of predictions, compared to a gold standard 
    :param pred: predictions of classifiers
    :param gold: gold standard annotations
    :param verbose: whether to print results (default True)
    :return: accuracy, precision, recall, F1 (each as an array)
    """
    # Check which predictions are correct
    correct = (pred == gold)
    n_correct = correct.sum(0)
    
    # Calculate different types of mistake 
    n_true_correct = (correct * gold).sum(0)
    n_false_correct = (correct * (1-gold)).sum(0)
    n_true_wrong = ((1-correct) * gold).sum(0)
    n_false_wrong = ((1-correct) * (1-gold)).sum(0)
    
    # Accuracy: proportion correct, out of all messages
    accuracy = n_correct / pred.shape[0]
    # Precision: proportion correct, out of those predicted to have a code
    precision = n_true_correct / (n_true_correct + n_false_wrong)
    # Recall: proportion correct, out of those annotated with a code
    recall = n_true_correct / (n_true_correct + n_true_wrong)
    # F1: harmonic mean of precision and recall
    f1 = 2 * precision * recall / (precision + recall)

    if verbose:
        # Print results
        print('Accuracy:', accuracy)
        print('Precision:', precision)
        print('Recall:', recall)
        print('F1:', f1)

    
    return accuracy, precision, recall, f1


def get_prediction_and_gold_vector(prediction_filename, prediction_codename, gold_filename, gold_codename):
    gold_pd = pandas.read_csv(gold_filename)
    gold_pd = gold_pd.drop_duplicates(subset='Message ID')
    #golds = gold_pd.loc[gold_pd[gold_codename]==1] #no: where out of these ids ml gave 1 - get that subset from gold
    gold_ids = gold_pd['Message ID']
    #print('nr of messages verified', len(gold_ids))
    prediction_pd = pandas.read_csv(prediction_filename)
    predictions_verified = prediction_pd[prediction_pd['ID'].isin(gold_ids)]
    print('label: ', gold_codename)

    predictions_to_evaluate = predictions_verified.loc[predictions_verified[prediction_codename]==1]
    print('labeled messages verified: ', len(predictions_to_evaluate), '\n')
    predictions_vector = predictions_to_evaluate[prediction_codename]
    prediction_ids = set(predictions_to_evaluate['ID'])
    golds = gold_pd[gold_pd['Message ID'].isin(prediction_ids)]
    golds_vector = golds[gold_codename]
    return predictions_vector, golds_vector




if __name__ == "__main__":
    'example use:'
    #features, codes, classifiers = train_on_file('hiv_aids', 'C1', C=1)
    #predictions = predict(classifiers, features)

    #evaluation: get predicted and blind verified codes
    predictions, golds = get_prediction_and_gold_vector('../data/hiv_aids_predictions.csv', "('Reason for  Lack of Acceptance', 'HIV/AIDS can spread easily')",
                                                        '../data/hiv_aids_verification_long.csv', "HIV/AIDS can spread easily")
    #get evaluation metrics
    evaluate(predictions, golds)
