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

from os import environ

from add_documents import add_document

from os import chdir, environ, getpid, system

#processes is the list of urls from the input link

THUMBNAIL_DIMENSIONS = "100px*130px"
THUMBNAIL_ZOOM = "0.20"

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

def download(inputfile, parallel=False):
  if parallel == True:
    print 'MULTIPROCESSING'
    startProcesses(inputfile)
  else:
    with open(inputfile) as lines:
      for line in lines:
        download_one((line))
        
def startProcesses( inputfile):
  #multiprocessing :
  print 'START PROCESSES ', inputfile
  urls = []
  with open(inputfile) as lines:
    urls = [line for line in lines]

  num_processes = cpu_count()-1
  if len(urls) < cpu_count()-1:
    num_processes = len(urls)

  print 'number of processes = ' + str(num_processes)
  pool = Pool(processes=num_processes)
  print "Pool created"
  pool.map_async(download_one, urls, callback=lambda x:finished(x,"Finished Processing")) 
 
def download_one(given_url):
  src = "@empty@"
  try:
    url = given_url.strip()
    url = validate_url(url)

    from add_documents import compute_index_entry
    e = compute_index_entry(url=url, extractType='boilerpipe')

    if e:
      print '\nGOOD\t' + e['url'] + ', PID=' + str(getpid())
    else:
      e = {
        'url': url,
        'html': base64.b64encode(src)
      }
    
    query = ""
    with open(environ['MEMEX_HOME'] + '/seed_crawler/seeds_generator/conf/queries.txt', 'r') as f:
      for line in f:
        query = line.strip();
    e['query'] = query
    
    entries = [e]
    add_document(entries)

  except urllib2.HTTPError, ex:
    print 'HTTPERROR=' + str(ex.code) + "\t" + url
  except socket.timeout, ex:
    print 'TIMEOUT=' + str(ex) + "\t" + url
  except:
    traceback.print_exc()
    print 'EXCEPTION' + "\t" + url
  return e

def finished(x, ctx):
  print ctx , str(getpid())
  
def main(argv):
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  
  download(inputfile, parallel=True)

if __name__=="__main__":
  main(sys.argv[1:])
