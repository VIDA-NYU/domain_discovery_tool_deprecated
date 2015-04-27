import sys
from os import environ, chdir, path
from subprocess import call
import base64
from add_documents import update_document
import urllib2

THUMBNAIL_DIMENSIONS = "100px*130px"
THUMBNAIL_ZOOM = "0.20"

def encode(url):
  return urllib2.quote(url).replace("/","%2F").replace('%','')

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
  pool.map_async(download_thumnail, urls, callback=lambda x:finished_thumbnail(x,"Finished Processing")) 

def download_thumbnail(url, download = True, updatedb=True):
  #Download thumbail
  print 'Downloading thumbnail for ', url
  chdir(environ['MEMEX_HOME'] + "/phantomjs/")
  comm = "bin/phantomjs"
  paramJs = environ['MEMEX_HOME'] + "/phantomjs/examples/rasterize.js"
  imageFileName = encode(url)+".png"
  imageFilePath = environ['MEMEX_HOME'] + "/seed_crawler/seeds_generator/thumbnails/"
  paramImg = imageFilePath + imageFileName

  if download:
    call([comm, paramJs, url, paramImg, THUMBNAIL_DIMENSIONS, THUMBNAIL_ZOOM])

  if not path.exists(paramImg):
    imageFileName = "default_thumbnail.jpeg"
    paramImg = imageFilePath + imageFileName

  if updatedb:
    with open(paramImg, 'rb') as img:
      e = {
        "doc": {
          "thumbnail_name": imageFileName,
          "thumbnail": base64.b64encode(img.read())
        }
      }
      update_document(url, e)
      print "updated thumbnail for ", url
  
def download_thumbnails(inputfile, parallel=False, download=True, updatedb=True):
  if parallel:
    startProcesses(inputfile)
  else:
    with open(inputfile,'r') as f:
      for url in f:
        download_thumbnail(url.strip(), download, updatedb)

def main(argv):
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  download_thumbnails(inputfile, download=True, updatedb=True)

if __name__=="__main__":
  main(sys.argv[1:])
