#!/bin/bash

BLD_DIR=`pwd`

SRC_DIR=$RECIPE_DIR/..
pushd $SRC_DIR

mkdir -vp ${PREFIX}/lib/ddt/bin;
mkdir -vp ${PREFIX}/lib/ddt/elastic;
mkdir -vp ${PREFIX}/lib/ddt/models;
mkdir -vp ${PREFIX}/lib/ddt/nltk_data
mkdir -vp ${PREFIX}/lib/ddt/ranking;
mkdir -vp ${PREFIX}/lib/ddt/lda_pipeline;
mkdir -vp ${PREFIX}/lib/ddt/seeds_generator;
mkdir -vp ${PREFIX}/lib/ddt/vis;
mkdir -vp ${PREFIX}/lib/ddt/vis/html;

pushd seeds_generator
mvn compile assembly:single
popd

python -m nltk.downloader -d ${PREFIX}/lib/ddt/nltk_data stopwords brown

cp -av elastic/* ${PREFIX}/lib/ddt/elastic
cp -av lda_pipeline/* ${PREFIX}/lib/ddt/lda_pipeline
cp -av models/* ${PREFIX}/lib/ddt/models
cp -av ranking/* ${PREFIX}/lib/ddt/ranking
cp -av seeds_generator/* ${PREFIX}/lib/ddt/seeds_generator

# hardcode here, let conda fix this on install
sed "s#tools.staticdir.root = .#tools.staticdir.root = ${PREFIX}/lib/ddt/vis/html#g" vis/config.conf-in > ${PREFIX}/lib/ddt/vis/config.conf

cp -av vis/* ${PREFIX}/lib/ddt/vis

cp -av bin/ddt ${PREFIX}/bin/ddt
chmod +x ${PREFIX}/bin/ddt

# ugly, but DDT hardcodes the location of word2vec here
pushd ${PREFIX}/lib/ddt/ranking
ln -s ../../../data/D_cbow_pdw_8B.pkl ./D_cbow_pdw_8B.pkl
