#parallel_download.py
# thread_download.py

from multiprocessing import Pool
import sys
import urllib2
import socket
import traceback
import requests

from os import chdir, environ

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
    #handle = urllib2.urlopen(url)
    #src = handle.read()
    res = requests.get(url)
    src = res.text
    src = src.encode('utf-8')
    print "GOOD\t" + url
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

def startProcesses(inputfile, outputdir):
  #multiprocessing :
  urls = []
  with open(inputfile) as lines:
    urls = [(line,outputdir) for line in lines]
  print urls
  pool = Pool(processes=3)
  print "Pool created"
  #url = urls[0]
  #print url
  pool.map(download_one,urls) 
  pool.close()
  pool.join()
  print "processing complete."


def main(argv):
    if len(argv) != 2:
        print "Invalid arguments"
        print "python download.py inputfile outputdir"
        return
    #to sequentially download one by one, use download passing :
    #download(argv[0], argv[1])
    
    inputfile=argv[0]
    outputdir=argv[1]
    
    startProcesses(inputfile, outputdir)


if __name__=="__main__":
    main(sys.argv[1:])
