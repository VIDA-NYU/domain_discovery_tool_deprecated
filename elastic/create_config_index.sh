#!/bin/sh

./create_index.sh config
./put_mapping.sh config domains config.json
python load_config.py 


