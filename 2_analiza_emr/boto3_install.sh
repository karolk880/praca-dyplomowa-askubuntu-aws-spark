#!/bin/bash -xe
# Bootstrap action klastra Amazon EMR.
# Skrypt wgrywa się do bucketu S3 i wskazuje przy tworzeniu klastra (Bootstrap actions).
# Uruchamia się na każdej maszynie klastra i instaluje biblioteki Pythona potrzebne
# w notebooku analiza_askubuntu.ipynb:
#   boto3      - komunikacja z Amazon S3
#   matplotlib - wykresy
#   pandas     - konwersja wyników ze Spark DataFrame (toPandas) i zapis do Excela
#   nltk       - stemming słów w tytułach pytań (pytanie h)
#   XlsxWriter - zapis wyników w formacie xlsx (dla Power BI)
#   pyarrow    - szybsza konwersja Spark DataFrame -> pandas
sudo pip3 install boto3 matplotlib pandas nltk XlsxWriter pyarrow
