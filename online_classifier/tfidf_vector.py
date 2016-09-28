from sklearn.feature_extraction.text import TfidfTransformer
from nltk import corpus

class tfidf_vectorizer(tf_vectorizer):
    
    def __init__(self, convert_to_ascii=False):
        self.tfidf_transformer = None
        
    def tfidf(self, data):
        [X_counts, _] = self.vectorize(data)
        if self.tfidf_transformer is None:
            self.tfidf_transformer = TfidfTransformer()
            X = self.tfidf_transformer.fit_transform(X_counts)
        else:
            X = self.tfidf_transformer.transform(X_counts)

        return [X, self.count_vect.get_feature_names()]

