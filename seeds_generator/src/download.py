#parallel_download.py
# thread_download.py

from multiprocessing import Pool
import sys
import urllib2
import socket
import traceback
import requests

from os import chdir, environ, getpid

#processes is the list of urls from the input link
    
def encode(url):
  return urllib2.quote(url).replace("/", "%2F")

def decode(url):
  return urllib2.unquote(url).replace("%2F", "/")

def validate_url(url):
    s = url[:4]
    if s == "http":
        return url
    else:
        url = "http://" + url
        return url

def download_one((given_url, outputdir)):
  try:
    url = given_url.strip("\n")
    url = validate_url(url)
    res = requests.get(url)
    src = res.text
    src = src.encode('utf-8')
    print 'GOOD\t' + url + ', PID=' + str(getpid())
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

def finished:
  print "processing complete."

def download(inputfile, outputdir, parallel=False):
  if parallel == True:
    pool = Pool(1)
    pool.apply_async(start_processes,(inputfile, outputdir),callback=finished)
  else:
    with open(inputfile) as lines:
      for line in lines:
        download_one((line, outputdir))

def startProcesses(inputfile, outputdir):
  #multiprocessing :
  urls = []
  with open(inputfile) as lines:
    urls = [(line,outputdir) for line in lines]
  print urls
  pool = Pool(processes=3)
  print "Pool created"
  pool.map(download_one,urls) 
  pool.close()
  pool.join()
  
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
