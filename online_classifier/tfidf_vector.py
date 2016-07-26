from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from nltk import corpus

class tfidf_vectorizer:
    
    def __init__(self, convert_to_ascii=False):
        self.convert_to_ascii = convert_to_ascii
        self.count_vect = None
        self.tfidf_transformer = None
        self.ENGLISH_STOPWORDS = corpus.stopwords.words('english')
        
    def vectorize(self, data):
        X_counts = None
        X = None
    
        if self.count_vect is None:
            self.count_vect = CountVectorizer(stop_words=self.ENGLISH_STOPWORDS, preprocessor=self.preprocess, strip_accents='ascii')
            X_counts = self.count_vect.fit_transform(data)
        else:
            X_counts = self.count_vect.transform(data)
            
        if self.tfidf_transformer is None:
            self.tfidf_transformer = TfidfTransformer()
            X = self.tfidf_transformer.fit_transform(X_counts)
        else:
            X = self.tfidf_transformer.transform(X_counts)

        return [X, self.count_vect.get_feature_names()]

    def preprocess(self, text):
        # Remove unwanted chars and new lines
        text = text.lower().replace(","," ").replace("__"," ")
        text = text.replace("\n"," ")

        if self.convert_to_ascii:
            # Convert to ascii
            ascii_text = []
            for x in text.split(" "):
                try:
                    ascii_text.append(str(x))
                except:
                    continue

            text = " ".join(ascii_text)

        preprocessed_text = " ".join([word.strip() for word in text.split(" ") if (word != "") and (self.isnumeric(word) == False)])
        
        return preprocessed_text

    def isnumeric(self, s):
        # Check if string is a numeric
        try: 
            int(s.replace(".","").replace("-","").replace("+",""))
            return True
        except ValueError:
            try:
                long(s.replace(".","").replace("-","").replace("+",""))
                return True
            except ValueError:
                return False

    
