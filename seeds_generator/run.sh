sh compile.sh
java -cp .:class:libs/commons-codec-1.9.jar BingSearch $1 $2 $3
mkdir -p html
python src/download.py results.txt html
