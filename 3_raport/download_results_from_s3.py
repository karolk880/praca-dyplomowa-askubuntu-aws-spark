#!/usr/bin/env python3
"""Pobranie wyników analizy z Amazon S3 na komputer lokalny.

Skrypt uruchamiany lokalnie, na komputerze z zainstalowanym Power BI Desktop.
Pobiera wszystkie pliki xlsx z bucketu do bieżącego folderu - z tych plików
korzysta raport w Power BI.

Wymagania: pip install boto3 oraz skonfigurowane dane dostępowe AWS (polecenie `aws configure`).
"""

import boto3

BUCKET_NAME = "bucket1-project-pw"

s3_client = boto3.client("s3")

# Lista obiektów zapisanych w buckecie
response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)

for obj in response.get("Contents", []):
    key = obj["Key"]
    # pobieramy tylko pliki z wynikami analizy (xlsx), pomijając surowe dane JSON
    if key.endswith(".xlsx"):
        s3_client.download_file(BUCKET_NAME, key, key)
        print(f"Pobrano: {key}")
