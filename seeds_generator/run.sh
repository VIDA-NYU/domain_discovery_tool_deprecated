sh compile.sh
java -cp .:class:libs/commons-codec-1.9.jar BingSearch
mkdir -p html
python src/download.py results.txt html
