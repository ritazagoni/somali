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




if __name__ == "__main__":
    'example use:'
    features, codes, classifiers = train_on_file('malaria', 'C1', C=1)
    predictions = predict(classifiers, features)

