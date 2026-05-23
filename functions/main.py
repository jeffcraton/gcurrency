import functions_framework
from google.cloud import firestore
import requests
from datetime import datetime
import os

# Initialize Firestore client
db = firestore.Client()

@functions_framework.http
def fetch_currency_prices(request):
    """
    HTTP Cloud Function that fetches currency exchange rates and stores them in Firestore.
    """
    try:
        # Fetch rates from Frankfurter API (Free, no key required)
        response = requests.get("https://api.frankfurter.app/latest?from=USD")
        response.raise_for_status()
        data = response.json()

        base = data.get('base')
        date = data.get('date')
        rates = data.get('rates')
        timestamp = datetime.utcnow()

        # Batch write to Firestore
        batch = db.batch()
        
        for currency, rate in rates.items():
            # Collection: currencies, Document: {currency_code}, Sub-collection: history
            history_ref = db.collection('currencies').document(currency).collection('history').document()
            batch.set(history_ref, {
                'rate': float(rate),
                'base': base,
                'timestamp': timestamp,
                'date_string': date
            })
            
            # Also update the latest rate in the main document
            currency_ref = db.collection('currencies').document(currency)
            batch.set(currency_ref, {
                'latest_rate': float(rate),
                'base': base,
                'last_updated': timestamp
            }, merge=True)

        batch.commit()
        print(f"Successfully updated {len(rates)} currencies in Firestore.")
        return f"Successfully updated {len(rates)} currencies.", 200

    except Exception as e:
        print(f"Error fetching currency prices: {e}")
        return f"Error: {e}", 500
