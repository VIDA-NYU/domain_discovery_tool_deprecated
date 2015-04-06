#parallel_download.py
# thread_download.py

from multiprocessing import Pool, cpu_count
from datetime import datetime
import sys
import urllib2
import socket
import traceback
import requests
import base64

from add_documents import add_document, extract_text, compute_index_entry

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
  
def get_downloaded_urls(inputfile):
  urls = []
  with open(inputfile, 'r') as f:
    urls = f.readlines
  urls = [url.strip() for url in urls]
  return urls

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
  pool = Pool(processes=cpu_count()-1)
  print "Pool created"
  pool.map_async(download_one, urls, callback=finished) 
 
def download_one((given_url, outputdir)):
  src = "@empty@"
  try:
    url = given_url.strip("\n")
    url = validate_url(url)
    #res = requests.get(url)

    e = compute_index_entry(url=url)
    if e:
      print 'GOOD\t' + e['url'] + ', PID=' + str(getpid())
    else:
      e = {
        'url': url,
        'html': base64.b64encode(src)
      }
    query = ""
    with open('conf/queries.txt', 'r') as f:
      for line in f:
        query = line.strip();
    e['query'] = query
    
    entries = [e]
    add_document(entries)
    src = base64.b64decode(e['html'])
    encoded_url = encode(e['url'])
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
  return e

def finished(x):
  print "Processing ", str(getpid()), " is Complete.",x
  
def main(argv):
  if len(argv) != 2:
    print "Invalid arguments"
    print "python download.py inputfile outputdir"
    return
  inputfile=argv[0]
  outputdir=argv[1]
  
  download(inputfile, outputdir, parallel=False)

if __name__=="__main__":
  main(sys.argv[1:])
