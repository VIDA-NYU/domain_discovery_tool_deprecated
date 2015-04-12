import download
import sys
from os import environ, chdir, path
from subprocess import call
import base64
from add_documents import update_document

THUMBNAIL_DIMENSIONS = "100px*130px"
THUMBNAIL_ZOOM = "0.20"

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

def download_thumbnail(url, updatedb=True):
  #Download thumbail
  print 'Downloading thumnail for ', url
  chdir(environ['MEMEX_HOME'] + "/phantomjs/")
  comm = "bin/phantomjs"
  paramJs = environ['MEMEX_HOME'] + "/phantomjs/examples/rasterize.js"
  paramImg = environ['MEMEX_HOME'] + "/seed_crawler/seeds_generator/thumbnails/" + download.encode(url)+".png"
  call([comm, paramJs, url, paramImg, THUMBNAIL_DIMENSIONS, THUMBNAIL_ZOOM])

  if updatedb:
    if path.exists(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/thumbnails/'+download.encode(url)+'.png'):
      with open(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/thumbnails/'+download.encode(url)+'.png', 'rb') as img:
        e = {
          "doc": {
            "thumbnail": base64.b64encode(img.read())
          }
        }
        update_document(url, e)
        print "updated thumbnail for ", url
    else:
      print "No thumbnail downloaded"
  
def download_thumbnails(inputfile, parallel=False, updatedb=True):
  if parallel:
    startProcesses(inputfile)
  else:
    with open(inputfile,'r') as f:
      for url in f:
        download_thumbnail(url.strip(), updatedb)

def main(argv):
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  download_thumbnails(inputfile, updatedb=False)

if __name__=="__main__":
  main(sys.argv[1:])
