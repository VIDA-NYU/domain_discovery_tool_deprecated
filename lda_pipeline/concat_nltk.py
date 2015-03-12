import sys
from os import walk
import re
import nltk

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))
NON_ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - ENGLISH_STOPWORDS
 
STOPWORDS_DICT = {}
for lang in nltk.corpus.stopwords.fileids():
 STOPWORDS_DICT[lang] = set(nltk.corpus.stopwords.words(lang))
 
def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in STOPWORDS_DICT.items()), key = lambda x: x[1])[0]
 
 
def is_english(text):
    text = text.lower()
    words = set(nltk.wordpunct_tokenize(text))
    return len(words & ENGLISH_STOPWORDS) > len(words & NON_ENGLISH_STOPWORDS)

def valid_words(text):
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(text)
    filtered = [w for w in words if (not w.lower() in ENGLISH_STOPWORDS and len(w) > 2)]
    return " ".join(filtered)
'''
KEY = re.compile("sex|woman|labor|slave|prostitution|organ|child|traffic|force")
def check_key_terms(content):
  content = content.lower()
  if KEY.search(content):
    content = content.replace("\n", " ")
    return content
  else:
    return ""
'''

def get_all_files(dirname):
  print "Loading all filenames"
  files = []
  for [path, dirnames, filenames] in walk(dirname):
      for filename in filenames:
        files.append(path + "/" + filename)
  print "Done loading filenes", len(files)
  return files

output = open(sys.argv[1], "w")
len_count = 0 #Count number of documents have less than 100 characters
count = 0
#for file in files:
for content in sys.stdin:
 if (count % 1000) == 0:
  print "all count:\t" + str(count) + "\tless-100 count:\t" + str(len_count) 
 count += 1
 content = content.strip("\n")
 url, text = content.split("\t")
 text = valid_words(text)
 #if len(text) > 100:
 # len_count += 1
 output.write(url + ";" + text + "\n")
output.close()
