import csv, pickle, os, numpy as np
from collections import Counter

from features import get_global_set, feature_list_and_dict, vectorise

def save(feat_bags, code_vecs, code_names, output_file, directory='../data'):
    """
    Save features and codes to file
    :param feat_bags: list of dict-like objects (supervised learning input)
    :param code_vecs: boolean numpy matrix of codes (supervised learning output)
    - rows correspond to elements in feat_bags
    - columns correspond to elements in code_names
    :param code_names: list of names of codes
    :param output_file: name of output file (without .pkl file extension)
    - as well as saving to example.pkl, also saves to:
    - example_features.pkl (list of names of features, with frequencies)
    - example_codes.pkl (list of names of codes, with frequencies)
    :param directory: directory of data files (default ../data)
    """
    N = len(feat_bags)
    K = len(code_names)
    
    if code_vecs.shape != (N,K):
        raise ValueError('Dimensions do not match')
    
    # Find the frequency of each code
    code_freq = code_vecs.sum(0)
    
    # Get the global set of features
    feat_set = get_global_set(feat_bags)
    feat_list, feat_dict = feature_list_and_dict(feat_set)
    # Convert messages to vectors
    feat_vecs = vectorise(feat_bags, feat_dict)
    # Find the document frequency of each feature
    feat_freq = (feat_vecs != 0).sum(0)

    # Save the features and codes to file,
    # as a list of names and frequencies
    
    feats = list(zip(feat_list, feat_freq))
    with open(os.path.join(directory, output_file+'_features.pkl'), 'wb') as f:
        pickle.dump(feats, f)
    
    codes = list(zip(code_names, code_freq))
    with open(os.path.join(directory, output_file+'_codes.pkl'), 'wb') as f:
        pickle.dump(codes, f)
    
    print('Codes:')
    print(*codes, sep='\n')
    
    with open(os.path.join(directory, output_file+'.pkl'), 'wb') as f:
        pickle.dump((feat_vecs, code_vecs), f)

def preprocess_long(input_file, output_file, extractor, directory='../data', text_col=0, ignore_cols=(), convert=bool):
    """
    Preprocess a csv file to feature vectors and binary codes,
    where the input data has a 0 or 1 for each code and message
    :param input_file: input file name (without .csv file extension)
    :param output_file: output file name (without .pkl file extension)
    :param extractor: function mapping strings to bags of features
    :param directory: directory of data files (default ../data)
    :param text_col: index of column containing text
    :param ignore_cols: indices of columns to ignore
    :param convert: function to convert codes strings (e.g. bool or int)
    """
    
    # Extract features and codes
    # We can vectorise the codes immediately, but for features, we first need a global list
    
    feat_bags = []
    code_vecs = []
    
    with open(os.path.join(directory, input_file+'.csv'), newline='') as f:
        # Process the file as a CSV file
        reader = csv.reader(f)
        # Find the headings (the first row of the file)
        headings = next(reader)
        # Restrict ourselves to a subset of columns (not containing text, and not ignored) 
        code_cols = sorted(set(range(len(headings))) - {text_col} - set(ignore_cols))
        code_names = [headings[i] for i in code_cols]
        # Iterate through data
        for row in reader:
            # Get the bag of features, and the vector of codes
            feat_bags.append(extractor(row[text_col]))
            code_vecs.append(np.array([convert(row[i]) for i in code_cols], dtype='bool'))
    
    # Convert the list of code vectors to a matrix
    code_vecs = np.array(code_vecs)
    # Save the information
    save(feat_bags, code_vecs, code_names, output_file, directory)

def preprocess_pairs(input_file, output_file, extractor, directory='../data', text_col=2, ignore_cols=(), uncoded=('', '')):
    """
    Preprocess a csv file to feature vectors and binary codes,
    where the input data has groups of codes,
    and each message has up to two codes from each group.
    Each group must take up exactly two columns.
    :param input_file: input file name (without .csv file extension)
    :param output_file: output file name (without .pkl file extension)
    :param extractor: function mapping strings to bags of features
    :param directory: directory of data files (default ../data)
    :param text_col: index of column containing text
    :param ignore_cols: indices of columns to ignore
    :param uncoded: strings to be interpreted as lacking a code
    """
    
    # Extract features and codes
    # We cannot vectorise these until we have a global list
    
    feat_bags = []
    code_sets = []
    
    with open(os.path.join(directory, input_file+'.csv'), newline='') as f:
        # Process the file as a CSV file
        reader = csv.reader(f)
        
        # Find the headings (the first row of the file)
        headings = next(reader)
        # Restrict ourselves to a subset of columns (not containing text, and not ignored) 
        code_cols = sorted(set(range(len(headings))) - {text_col} - set(ignore_cols))
        # Group columns in pairs
        pair_indices = list(zip(code_cols[::2], code_cols[1::2]))
        pair_indices = [(4,5,6), (7,8,9)] # HIV/AIDS triples
        pair_names = [headings[i][:-1].strip() for i in code_cols[::3]]
        print('names: ', pair_names)

        # Find features and codes
        for row in reader:
            # Find words in message
            feat_bags.append(extractor(row[text_col]))
            # Find codes
            row_code_set = set()
            for name, inds in zip(pair_names, pair_indices):
                # The code is recorded as a tuple (pair_name, value)
                # If a code is repeated, it is only counted once
                row_code_set |= {(name, row[i]) for i in inds if row[i] not in uncoded}
            code_sets.append(row_code_set)
    
    # Get the global set of codes, and convert to vectors
    
    codes = get_global_set(code_sets)
    K = len(codes)
    code_list, code_dict = feature_list_and_dict(codes)
    
    def vectorise_codes(set_of_codes):
        """
        Convert names of codes to a vector
        :param set_of_codes: set of code names
        :return: numpy array
        """
        vec = np.zeros(K, dtype='bool')
        for c in set_of_codes:
            vec[code_dict[c]] = True
        return vec
    
    code_vecs = np.array([vectorise_codes(x) for x in code_sets])

    
    # Save the information
    save(feat_bags, code_vecs, code_list, output_file, directory)


if __name__ == "__main__":
    from features import bag_of_words
    #preprocess_long('Malaria_long', 'malaria', bag_of_words, ignore_cols=[1,12], convert=bool)
    #preprocess_long('wash_original_long_corr', 'wash', bag_of_words, ignore_cols=[1,2,3,4,5,6,7], convert=bool)
    #preprocess_long('nutrition_original', 'nutrition', bag_of_words, ignore_cols=[1,2,14,15], convert=bool)
    #preprocess_long('ANC', 'delivery', bag_of_words, ignore_cols=[1], convert=int)
    preprocess_pairs('HIV_AIDS coding - Training data (NEW - 13.02.17)_final', 'hiv_aids', bag_of_words, ignore_cols=[0,1,3,10,11,12])