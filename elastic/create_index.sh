curl -XPUT "$1/memex"; echo
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
