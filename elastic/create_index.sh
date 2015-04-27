#!/bin/sh
if [ $# -eq 0 ]
then
    ELASTIC=http://localhost:9200
else
    ELASTIC=$1
fi

curl -s -XPUT "$ELASTIC/memex"; echo
#  -d '{
#     "index" : {
# 	"analysis":{
# 	    "analyzer":{
# 		"html" : {
# 	            "type" : "custom",
# 		    "tokenizer" : "standard",
#                     "filter" : ["lowercase" , "stop"],
#                     "char_filter" : ["html_strip"]
#                 }
#             }
# 	}
#     }
# }'
