import download

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

def download_thumbnail(url):
    #Download thumbail
    comm = environ['MEMEX_HOME'] + "/phantomjs/bin/phantomjs"
    paramJs = environ['MEMEX_HOME'] + "/phantomjs/examples/rasterize.js"
    paramImg = environ['MEMEX_HOME'] + "/seed_crawler/seeds_generator/thumbnails/" + encode(url)+".png"
    call([comm, paramJs, url, paramImg, THUMBNAIL_DIMENSIONS, THUMBNAIL_ZOOM])
    e = {
      "script": "ctx._source.thumbnail = thumbnail",
      "params": {
        "thumbnail": base64.b64encode(environ['MEMEX_HOME']+'/seed_crawler/seeds_generator/thumbnails/'+encode(url)+'.png')
      }
    }
    update_document(url, e)

def download_thumbnails(inputFile):
    startProcesses(inputFile)

def main(argv):
  if len(argv) != 1:
    print "Invalid arguments"
    print "python download.py inputfile"
    return
  inputfile=argv[0]
  
  download_thumbnails(inputfile)

if __name__=="__main__":
  main(sys.argv[1:])
