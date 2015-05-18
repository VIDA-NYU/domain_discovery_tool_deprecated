import urllib2
import sys
from os import environ

from subprocess import Popen, PIPE, STDOUT

def encode( url):
  return urllib2.quote(url).replace("/", "%2F")

def decode( url):
  return urllib2.unquote(url).replace("%2F", "/")

def validate_url( url):
  s = url[:4]
  if s == "http":
    return url
  else:
    url = "http://" + url
  return url
  
def get_downloaded_urls(inputfile):
  urls = []
  with open(inputfile, 'r') as f:
    urls = f.readlines
  urls = [url.strip() for url in urls]
  return urls

def download(inputfile, parallel=False, cb=None):
  query = ""
  with open('conf/queries.txt', 'r') as f:
    for line in f:
      query = line.strip();

  comm = "java -cp target/seeds_generator-1.0-SNAPSHOT-jar-with-dependencies.jar Download " + inputfile + ' "' + query +'"';
  p=Popen(comm, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
  output, errors = p.communicate()
  print output
  if not (errors == None):
    print '*' * 80, '\n\n\n'  
    print errors
  
def main(argv):
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  
  download(inputfile)

if __name__=="__main__":
  main(sys.argv[1:])
