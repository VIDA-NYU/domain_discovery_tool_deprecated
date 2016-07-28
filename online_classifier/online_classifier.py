from sklearn import linear_model
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

import numpy as np

class OnlineClassifier:

    def __init__(self):
        self.clf = None
        self.count_vect = None
        self.tfidf_transformer = None
        
    def vectorize(self, train, test=[]):
        if self.count_vect is None:
            self.count_vect = CountVectorizer()
            X_train_counts = self.count_vect.fit_transform(train)
        else:
            X_train_counts = self.count_vect.transform(train)
        if test:
            X_test_counts = self.count_vect.transform(test)
        else:
            X_test_counts = None

        if self.tfidf_transformer is None:
            self.tfidf_transformer = TfidfTransformer()
            X_train = self.tfidf_transformer.fit_transform(X_train_counts)
        else:
            X_train = self.tfidf_transformer.fit_transform(X_train_counts)
        if X_test_counts != None:
            X_test = self.tfidf_transformer.transform(X_test_counts)
        else:
            X_test = None

        return [X_train, X_test]

    
    def fit(self, X, Y):
        clf = linear_model.SGDClassifier(n_iter=1)
        try:
            clf.fit(X, Y)
        except ValueError as verr:
            print("Value error: {0}".format(verr))
            return None
        self.clf = clf
        return clf

    def partialFit(self, X, Y):
        if self.clf is None:
            self.fit(X, Y)
        else:
            self.clf.partial_fit(X,Y)
        return self.clf
    
    def calibrate(self, clf, X, Y):
        sigmoid = CalibratedClassifierCV(clf, cv=2, method='sigmoid')
        sigmoid.fit(X,Y)
        return sigmoid

    def calibrateScore(self, sigmoid, X, Y):
        return sigmoid.score(X,Y)

    def predictClass(self, X, Y, clf, sigmoid):
        for i in range(0,10):
            for val in (sigmoid.predict_proba(X[i])*100):
                print Y[i], clf.predict(X[i]), "%.2f" % val[0], "%.2f" % val[1]


    def classify(self, train, train_labels, test, test_labels, partial=False):
        [X_train, X_test] = self.vectorize(train, test)
        if partial:
            clf = self.partialFit(X_train, train_labels)
        else:
            clf = self.fit(X_train, train_labels)
        sigmoid = self.calibrate(clf, X_train, train_labels)
        self.predictClass(X_test, test_labels, clf, sigmoid)
        
        
