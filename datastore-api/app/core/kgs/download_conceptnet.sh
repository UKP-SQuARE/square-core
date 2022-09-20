# download ConceptNet
mkdir -p data/
mkdir -p data/cpnet/
wget -nc -P data/cpnet/ https://s3.amazonaws.com/conceptnet/downloads/2018/edges/conceptnet-assertions-5.6.0.csv.gz
cd data/cpnet/
yes n | gzip -d conceptnet-assertions-5.6.0.csv.gz