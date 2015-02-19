sh compile.sh
mkdir -p data
LDADATA="data/lda_input.csv"
#java -cp .:class/:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract ../seeds_generator/html/ 
java -cp .:class/:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract ../seeds_generator/html/  | python concat_nltk.py $LDADATA
#echo "Done Preproccessing"
#echo "Running LDA..."
#java -jar lib/tmt-0.4.0.jar ht.scala
