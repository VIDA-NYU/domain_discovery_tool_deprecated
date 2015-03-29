#parallel_download.py
# thread_download.py

from multiprocessing import Pool, cpu_count
from datetime import datetime
import sys
import urllib2
import socket
import traceback
import requests

from add_documents import add_document, extract_text

from os import chdir, environ, getpid, system

#processes is the list of urls from the input link

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
  

def download(inputfile, outputdir, parallel=False):
  if parallel == True:
    print 'MULTIPROCESSING'
    startProcesses(inputfile, outputdir)
  else:
    with open(inputfile) as lines:
      for line in lines:
        download_one((line, outputdir))
        
def startProcesses( inputfile, outputdir):
  #multiprocessing :
  print 'START PROCESSES ', inputfile, ' ', outputdir
  urls = []
  with open(inputfile) as lines:
    urls = [(line,outputdir) for line in lines]
  print 'number of processes = ' + str(cpu_count())
  pool = Pool(processes=cpu_count())
  print "Pool created"
  pool.map_async(download_one, urls, callback=finished) 

def download_one((given_url, outputdir)):
  try:
    url = given_url.strip("\n")
    url = validate_url(url)
    res = requests.get(url)
    src = res.text
    print 'GOOD\t' + url + ', PID=' + str(getpid())
    doc = extract_text(src,url)
    query = ""
    with open('conf/queries.txt', 'r') as f:
      for line in f:
        query = line.strip();

    entry = {
      'url': url,
      'text': doc,
      'html': src,
      'query': query,
      'retrieved': datetime.now(),
    }
    entries = [entry]
    add_document(entries)
    
    encoded_url = encode(url)
    f = open(outputdir + "/" + encoded_url, "w")
    f.write(src)
    f.close()
  except urllib2.HTTPError, e:
    print 'HTTPERROR=' + str(e.code) + "\t" + url
  except socket.timeout, e:
    print 'TIMEOUT=' + str(e) + "\t" + url
  except:
    traceback.print_exc()
    print 'EXCEPTION' + "\t" + url

def finished(x):
  print "Processing ", str(getpid()), " is Complete.",x
  
def main(argv):
  if len(argv) != 2:
    print "Invalid arguments"
    print "python download.py inputfile outputdir"
    return
  inputfile=argv[0]
  outputdir=argv[1]
  
  startProcesses(inputfile, outputdir)

if __name__=="__main__":
  main(sys.argv[1:])
