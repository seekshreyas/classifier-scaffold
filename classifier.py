#! /usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Benchmark different classifiers

Classifiers tried:

- Naive Bayes
- Random Forest
- SVM
    - linear
    - kernelized
"""
from __future__ import division
import sys
import pandas as pd
import numpy as np
from optparse import OptionParser
from sklearn import metrics, preprocessing
from sklearn import svm, naive_bayes, neighbors, tree
from sklearn.ensemble import AdaBoostClassifier



def getUserInput(models):
    """
    Get User Input
    """
    optionparser = OptionParser(add_help_option=False, epilog="multiline")

    optionparser.add_option('-c', '--classifier', dest='classifier', default="all")
    optionparser.add_option('-s', '--sample', dest='sample', default="all")
    optionparser.add_option('-h', '--help', dest='help', action='store_true',
                  help='show this help message and exit')
    optionparser.add_option('-f', '--file', dest='file')


    (option, args) = optionparser.parse_args()

    if option.help:
        print optionparser.print_help()
        print __doc__
        print "Supported Classifier Models:"


        # print models
        for index, key in enumerate(models):
            print "%2s % 20s" % (index, key)

        print "Default option: 'all'\n"

        print "To run the program, provide app features file path"
        print "Usage: --file='path.to.appData'"

        sys.exit()


    if not option.file:
        return optionparser.error('Data File path not provided.\n Usage: --file="path.to.data"')


    return {
        'classifier' : option.classifier,
        'file': option.file,
        'sample' : option.sample
    }





def loadAppData(datafile):
    """
    Data File added
    {
        'fair' : False,
        'unfair': True
    }
    """
    df = pd.read_csv(datafile)

    ## Remove the unnamed column as not sure
    # cols = set(df.columns)
    # cols.remove('Unnamed: 7')
    # df = df[list(cols)]

    ## Convert appLabel to boolean: True for 'unfair'
    df['label'] = df['label'].map(lambda x: x=='unfair')

    return df


def trimDf(df):
    """
    Trim the dataframe provided
    Remove features that we don't think are helping
    """
    cols = set(df.columns)

    cols.remove('feat3') # bug in our feature extraction code
    cols.remove('feat8') # considered only free apps


    return df[list(cols)]




def prepareSplitClassifier(df, models, choice):
    """
    Classify the apps for equal splits
    """


    def classificationOutput(clf, X, Y):
        """
        Fit the model and print the classification results
        - confusion_matrix
        - avg scores etc
        """
        n_samples = 36

        print "\n\nClassifier: \n %s" % (clf)
        print "#" * 79
        # classifier_gnb = naive_bayes.GaussianNB() # initiating the classifier

        clf.fit(X[:n_samples], Y[:n_samples]) # train on first n_samples and test on last 10

        expected = Y[n_samples:]
        predicted = clf.predict(X[n_samples:])
        print("Classification report:\n%s\n" % (metrics.classification_report(expected, predicted)))
        print("\nConfusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))




    def splitclassify(cDf):
        """
        Given the dataframe combined with equal fair and unfair apps,
        classify them
        """
        cDf = cDf.reindex(np.random.permutation(cDf.index)) # shuffle the dataframe
        featCols = set(cDf.columns)
        featCols.remove('label')

        features = cDf[list(featCols)].astype('float')

        ## Scale the features to a common range
        min_max_scaler = preprocessing.MinMaxScaler()
        X = min_max_scaler.fit_transform(features.values)

        Y = cDf['label'].values


        if choice == 'all':
            for key in models:
                classifier = models[key]
                classificationOutput(classifier, X, Y)
        else:
            if choice in models:
                classifier = models[choice]
                classificationOutput(classifier, X, Y)
            else:
                print "Incorrect Choice"



    fairDf = df[df['label'] == False]
    unfairDf = df[df['label'] == True]


    # calculate total possible splits of fair data frame relatie to
    # size of unfair dataframe
    splits = len(fairDf) // len(unfairDf)

    for i in range(splits):
        clDf = fairDf[i : i+len(unfairDf)].append(unfairDf)

        # print fairDf.values, unfairDf.values
        print "Classifying %d th split of fair  with unfair " % (i)
        print "-" * 79
        splitclassify(clDf)
        print "\n\n"




def performClassification(clf, featVector, labelVector, fold=4):
    """
    Perform Classification
    """

    (numrow, numcol) = featVector.shape

    foldsize = int(numrow//fold)

    print "FoldSize: %s" % (foldsize)

    for i in range(fold):
        X_test = featVector[i*foldsize:(i+1)*foldsize]
        Y_test = labelVector[i*foldsize:(i+1)*foldsize]

        X_train = np.concatenate((featVector[:i*foldsize], featVector[(i+1)*foldsize:]))
        Y_train = np.concatenate((labelVector[:i*foldsize], labelVector[(i+1)*foldsize:]))

        print " X_train: %s, Y_train: %s, X_test: %s, Y_test: %s" % (X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)

        print "#### Classifier: \n %s" % (clf)


        clf.fit(X_train, Y_train) # train on first n_samples and test on last 10

        expected = Y_test
        predicted = clf.predict(X_test)
        print "Classification report:\n%s\n" % metrics.classification_report(expected, predicted)
        print "\nConfusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted)




def allClassifier(cDf, models, modelchoice):
    """
    Classifier for all apps
    """

    print "Data Size: %s, \t Model Choice: %s" % (cDf.shape, modelchoice)

    cDf = cDf.reindex(np.random.permutation(cDf.index)) # shuffle the dataframe
    featCols = set(cDf.columns)
    featCols.remove('label')

    features = cDf[list(featCols)].astype('float')

    ## Scale the features to a common range
    min_max_scaler = preprocessing.MinMaxScaler()
    featVector = min_max_scaler.fit_transform(features.values) #scaled feature vector

    labelVector = cDf['label'].values #label vector


    if modelchoice == 'all':
        for key in models:
            if key != 'svm-nl':
                classifier = models[key]
                performClassification(classifier, featVector, labelVector)
    else:
        if modelchoice in models and modelchoice != 'svm-nl':
            classifier = models[choice]
            performClassification(classifier, featVector, labelVector)
        else:
            print "Incorrect Choice"






def main():

    # Supported classifier models
    n_neighbors = 3
    models = {
        'nb' : naive_bayes.GaussianNB(),
        'svm-l' : svm.SVC(),
        'svm-nl' : svm.NuSVC(),
        'tree' : tree.DecisionTreeClassifier(),
        'forest': AdaBoostClassifier(tree.DecisionTreeClassifier(max_depth=1),algorithm="SAMME",n_estimators=200),
        'knn-uniform' : neighbors.KNeighborsClassifier(n_neighbors, weights='uniform'),
        'knn-distance' : neighbors.KNeighborsClassifier(n_neighbors, weights='distance')
    }

    userInput = getUserInput(models)
    appDf = loadAppData(userInput['file'])
    appDf = trimDf(appDf)

    if userInput['sample'] == 'all':
        allClassifier(appDf, models, userInput['classifier'])
    else:
        prepareSplitClassifier(appDf, models, userInput['classifier'])




if __name__ == '__main__':
    main()
