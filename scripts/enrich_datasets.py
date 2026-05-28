import json
import requests
from google.cloud import firestore
import os
import time

BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"

def enrich_and_upload_datasets():
    # Initialize Firestore client
    db = firestore.Client()

    # Read endpoints.json
    with open('endpoints.json', 'r') as f:
        data = json.load(f)

    datasets = data['data']['allDatasets']['datasets']
    print(f"Found {len(datasets)} datasets. Starting enrichment and upload...")

    for i, dataset in enumerate(datasets):
        print(f"[{i+1}/{len(datasets)}] Processing dataset: {dataset['name']}")
        
        for api in dataset.get('apis', []):
            endpoint = api['endpoint']
            print(f"  Fetching schema for: {endpoint}")
            try:
                # Request 1 row to get metadata
                response = requests.get(f"{BASE_URL}{endpoint}", params={'page[size]': 1})
                response.raise_for_status()
                meta = response.json().get('meta', {})
                
                # Add schema information to the API object
                api['schema'] = {
                    'labels': meta.get('labels', {}),
                    'dataTypes': meta.get('dataTypes', {}),
                    'dataFormats': meta.get('dataFormats', {})
                }
                # Be nice to the API
                time.sleep(0.1)
            except Exception as e:
                print(f"  Error fetching schema for {endpoint}: {e}")

        # Upload enriched dataset to Firestore
        doc_id = dataset.get('slug', '').strip('/').replace('/', '_')
        if not doc_id:
            doc_ref = db.collection('datasets').document()
        else:
            doc_ref = db.collection('datasets').document(doc_id)
        
        doc_ref.set(dataset)
        print(f"  Successfully uploaded {dataset['name']} to Firestore.")

    print("Successfully completed enrichment and upload of all datasets.")

if __name__ == "__main__":
    enrich_and_upload_datasets()
