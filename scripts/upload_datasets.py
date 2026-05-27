import json
from google.cloud import firestore
import os

def upload_datasets():
    # Initialize Firestore client
    db = firestore.Client()

    # Read endpoints.json
    with open('endpoints.json', 'r') as f:
        data = json.load(f)

    datasets = data['data']['allDatasets']['datasets']
    print(f"Found {len(datasets)} datasets. Starting upload...")

    batch = db.batch()
    collection_ref = db.collection('datasets')

    for dataset in datasets:
        # Use a slug-based ID if possible, otherwise let Firestore generate one
        doc_id = dataset.get('slug', '').strip('/').replace('/', '_')
        if not doc_id:
            doc_ref = collection_ref.document()
        else:
            doc_ref = collection_ref.document(doc_id)
        
        batch.set(doc_ref, dataset)

    # Commit the batch
    batch.commit()
    print("Successfully uploaded datasets to Firestore.")

if __name__ == "__main__":
    upload_datasets()
