from sklearn.feature_extraction.text import CountVectorizer
from nltk import corpus

class tf_vectorizer:
    
    def __init__(self, convert_to_ascii=False, max_features=1000):
        self.convert_to_ascii = convert_to_ascii
        self.count_vect = None
        self.max_features = max_features
        self.ENGLISH_STOPWORDS = corpus.stopwords.words('english')
        
    def vectorize(self, data):
        X_counts = None
    
        if self.count_vect is None:
            self.count_vect = CountVectorizer(stop_words=self.ENGLISH_STOPWORDS, preprocessor=self.preprocess, strip_accents='ascii', max_features=self.max_features)
            X_counts = self.count_vect.fit_transform(data)
        else:
            X_counts = self.count_vect.transform(data)

        return [X_counts, self.count_vect.get_feature_names()]

    def tf(self, data):
        return self.vectorize(data)

    def preprocess(self, text):
        # Remove unwanted chars and new lines
        text = text.lower().replace(","," ").replace("__"," ").replace("[","").replace("]","").replace("\text","").replace("(","").replace(")","")
        text = text.replace("\n"," ")

        if self.convert_to_ascii:
            # Convert to ascii
            ascii_text = []
            for x in text.split(" "):
                try:
                    ascii_text.append(x.encode('ascii', 'ignore'))
                except:
                    continue

            text = " ".join(ascii_text)

        preprocessed_text = " ".join([word.strip() for word in text.split(" ") if (word != "") and (self.isnumeric(word.strip()) == False) and ("http" not in word.strip()) and ("html" not in word.strip()) and (len(word.strip()) > 1)])
        
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

    
