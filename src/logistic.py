import pickle, os, numpy as np
from sklearn import linear_model
from sklearn.metrics import precision_recall_fscore_support
import pandas

def train(features, codes, penalty='l1', C=1, keywords=None, keyword_strength=1, keyword_weight=1, weight_option='balanced', smoothing=0):
    """
    Train logistic regression classifiers,
    independently for each code
    :param features: input matrix, of shape [num_messages, num_features]
    :param codes: output matrix, of shape [num_messages, num_codes]
    :param penalty: type of regularisation ('l1' or 'l2')
    :param C: inverse of regularisation strength
    :param keywords: (optional) list of length num_codes, with each element being
        an iterable of indices of features which should be considered a keyword for that code
    :param keyword_strength: (default 1) value to give to the vector for each keyword feature
    :param keyword_weight: (default 1) weight to assign a keyword vector (relative to a normal message)
    :param weight_option: determine the total weight for each code across all messages. Options are:
        - 'balanced': total weight is the same for true and false
        - 'smoothed': total weight is the observed number, plus smoothing
    :param smoothing: (default 0, i.e. no smoothing) constant to add,
        to reweight frequencies of each code
    :return: list of classifiers
    """
    N, F = features.shape
    classifiers = []
    # Iterate through each code (i.e. each column of codes matrix)
    for i, code_i in enumerate(codes.transpose()):
        # If there are no training examples, return None for this code
        N_pos = code_i.sum()
        if N_pos == 0:
            classifiers.append(None)
            continue
        
        # Check if keywords were given
        if keywords is None:
            # If no keywords, leave matrices the same
            feat_mat = features
            code_vec = code_i
            N_key = 0
        else:
            # If given, add the keywords as additional messages
            indices = keywords[i]
            N_key = len(indices)
            # Treat each keyword feature as a separate message
            key_features = np.zeros((N_key, F))
            for j, j_ind in enumerate(indices):
                # Set the strength of the feature as asked for
                key_features[j, j_ind] = keyword_strength
            key_codes = np.ones(N_key, dtype='bool')
            # Extend the feature and code arrays
            feat_mat = np.concatenate((features, key_features))
            code_vec = np.concatenate((code_i, key_codes))
        
        # Weight classes as asked for
        if weight_option == 'balanced':
            class_weight = 'balanced'
        elif weight_option == 'smoothed':
            N_neg = N - N_pos
            class_weight = {True: (N_pos + smoothing) / (N_pos + N_key*keyword_weight),
                            False: (N_neg + smoothing) / N_neg}
        else:
            raise ValueError('weight option not recognised')
        
        # Weight keyword examples as asked for
        if keyword_weight == 1:
            sample_weight = None
        else:
            sample_weight = np.ones(N+N_key)
            sample_weight[N:] = keyword_weight
        
        # Initialise a logistic regression model
        model = linear_model.LogisticRegression(penalty=penalty, C=C, class_weight=class_weight)
        
        # Train the model
        model.fit(feat_mat, code_vec, sample_weight=sample_weight)
        
        classifiers.append(model)
    
    return classifiers


def train_on_file(input_name, output_suffix=None, directory='../data', keyword_file=None, **kwargs):
    """
    Train logistic regression classifiers on a file 
    :param input_name: name of input file (without .pkl file extension)
    :param output_suffix: string to append to name of output file
    (if none is given, no file is saved)
    :param directory: directory of data files (default ../data)
    :param keyword_file: name of keyword file
    :param **kwargs: additional keyward arguments will be passed to train
    :return: features, codes, classifiers
    """
    # Load features and codes
    with open(os.path.join(directory, input_name+'.pkl'), 'rb') as f:
        features, codes = pickle.load(f)
    # If keyword file given, get keywords
    if keyword_file is not None:
        with open(os.path.join(directory, keyword_file+'.pkl'), 'rb') as f:
            keywords = pickle.load(f)
        kwargs['keywords'] = keywords
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
    # true positives
    n_true_correct = (correct * gold).sum(0)
    #print(n_true_correct)
    n_false_correct = (correct * (1-gold)).sum(0)
    # false negatives
    n_true_wrong = ((1-correct) * gold).sum(0)
    # false positives
    n_false_wrong = ((1-correct) * (1-gold)).sum(0)
    #n_false_wrong = (correct * (1-gold)).sum(0)

    # Accuracy: proportion correct, out of all messages
    accuracy = n_correct / pred.shape[0]
    # Precision: proportion correct, out of those predicted to have a code
    #precision = n_true_correct / (n_true_correct + n_false_wrong)
    # Recall: proportion correct, out of those annotated with a code
    #recall = n_true_correct / (n_true_correct + n_true_wrong)
    # F1: harmonic mean of precision and recall
    #f1 = 2 * precision * recall / (precision + recall)

    '''
    if verbose:
        # Print results
        print('Accuracy:', accuracy)
        print('Precision:', precision)
        print('Recall:', recall)
        print('F1:', f1)
    '''
    
    #return accuracy, precision, recall, f1

    precision, recall, fscore, support = precision_recall_fscore_support(gold, pred, average='binary')

    if verbose:
        print('Precision:', precision)
        print('Recall:', recall)
        print('F1:', fscore)
        print('annotated messages: ', int(gold.sum()))

def get_prediction_and_gold_vector(prediction_filename, prediction_codename, gold_filename, gold_codename):
    gold_pd = pandas.read_csv(gold_filename)
    gold_pd.fillna(value=0, inplace=True)
    gold_pd = gold_pd.drop_duplicates(subset='ID')
    # only those messages which were annotated with a code
    #gold_pd = gold_pd.loc[gold_pd[gold_codename]==1]
    print(len(gold_pd))
    gold_ids = gold_pd['ID']
    #print('nr of messages verified', len(gold_ids))
    prediction_pd = pandas.read_csv(prediction_filename)
    prediction_pd.fillna(value=0, inplace=True)
    prediction_pd = prediction_pd.drop_duplicates(subset='ID')
    predictions_verified = prediction_pd[(prediction_pd['ID'].isin(gold_ids)) & (prediction_pd['source'] == 'prediction')]

    # consider only messages which have a code
    #labeled_predictions = predictions_verified.loc[predictions_verified[prediction_codename]==1]

    #print('labeled messages verified: ', len(labeled_predictions), '\n')
    print('labeled messages verified: ', len(predictions_verified), '\n')

    # if training data was included in verification, exclude
    pred_ids = predictions_verified['ID']

    verified_to_check = gold_pd[gold_pd['ID'].isin(pred_ids)]

    # align dataframes

    predictions_verified.sort_values(by='ID', inplace=True)

    verified_to_check.sort_values(by='ID', inplace=True)

    #predictions_verified, verified_to_check = predictions_verified.align(verified_to_check, axis=1)

    # get just the predictions from full row
    #predictions_vector = labeled_predictions[prediction_codename]
    predictions_vector = predictions_verified[prediction_codename]
    #prediction_ids = set(labeled_predictions['ID'])
    golds_vector = verified_to_check[gold_codename]

    print('match: ', (predictions_vector==golds_vector).sum(), '\n')


    print('label:', gold_codename, '\n')

    return predictions_vector, golds_vector




if __name__ == "__main__":
    'example use:'
    features, codes, classifiers = train_on_file('malaria', 'C1', C=1)
    predictions = predict(classifiers, features)

    '''
    'evaluation:'
    #evaluation: get predicted and blind verified codes

    predictions, golds = get_prediction_and_gold_vector('../data/malaria_predictions_0905.csv',
                                                        'Health Services',
                                                        '../data/malaria_verified_long.csv',
                                                        'Health Services')
    #get evaluation metrics
    evaluate(predictions, golds)
    '''