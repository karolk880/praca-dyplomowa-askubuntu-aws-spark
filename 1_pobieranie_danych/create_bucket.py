#!/usr/bin/env python3
"""Utworzenie bucketu w Amazon S3.

Skrypt uruchamiany jednorazowo w środowisku AWS Cloud9. W utworzonym buckecie
zapisywane są surowe dane pobrane z API (pliki JSON) oraz wyniki analizy (pliki xlsx).

Wymagania: biblioteka boto3 (pip install boto3) oraz skonfigurowane uprawnienia AWS
(w Cloud9 są dostępne automatycznie).
"""

import boto3

# Nazwa bucketu - musi być unikalna w skali całego AWS
BUCKET_NAME = "bucket1-project-pw"

# Region, w którym powstanie bucket (dla regionu us-east-1 nie podaje się LocationConstraint)
REGION = "eu-central-1"

# Utworzenie klienta S3
s3_client = boto3.client("s3", region_name=REGION)

# Utworzenie bucketu
try:
    s3_client.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": REGION},
    )
    print(f"Utworzono bucket o nazwie: {BUCKET_NAME}")
except Exception as e:
    # Najczęstsza przyczyna błędu: bucket o tej nazwie już istnieje
    print(f"Błąd podczas tworzenia bucketu: {e}")
