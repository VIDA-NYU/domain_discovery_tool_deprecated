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
from subprocess import call
from subprocess import Popen
from subprocess import PIPE


from add_documents import add_document, extract_text, compute_index_entry, update_document

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
  print 'number of processes = ' + str(cpu_count())
  pool = Pool(processes=cpu_count()-1)
  print "Pool created"
  pool.map_async(download_one, urls, callback=finished) 
 
def download_one(given_url):
  src = "@empty@"
  try:
    url = given_url.strip()
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

    #Download thumbail
    call([environ['MEMEX_HOME']+"/phantomjs/bin/phantomjs", environ['MEMEX_HOME']+"/phantomjs/examples/rasterize.js", url, environ['MEMEX_HOME']+"/seed_crawler/seeds_generator/thumbnails/"+encode(url)+".png", "200px*300px", "0.20"])
    e = {
      "doc" : {
        "thumbnail": base64.b64encode(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/thumbnails/'+encode(url)+'.png')
      }
    }
    update_document(url, e)
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
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  
  download(inputfile, parallel=False)

if __name__=="__main__":
  main(sys.argv[1:])
