mkdir -p class
javac -cp .:libs/commons-codec-1.9.jar src/BingSearch.java -d class
javac -cp .:libs/boilerpipe-1.2.0.jar:libs/nekohtml-1.9.13.jar:libs/xerces-2.9.1.jar src/Extract.java -d class
