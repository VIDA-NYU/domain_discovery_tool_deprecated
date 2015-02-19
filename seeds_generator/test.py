from subprocess import call
from subprocess import Popen
from subprocess import PIPE
import download

#p=Popen("java -cp .:class:libs/commons-codec-1.9.jar BingSearch -t 5",shell=True,stdout=PIPE)
#output, errors = p.communicate()
#print output
#print errors
call(["rm", "-rf", "html"])
call(["mkdir", "-p", "html"])
#download.download("results.txt","html")


