from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from google.cloud import firestore
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'a-very-secret-key')

# Initialize Firestore client
db = firestore.Client()

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # In a real app with Firebase Auth, this would be handled on the frontend
        # For this demo, we'll simulate a login or just let them in if they provide a 'token'
        token = request.form.get('token')
        if token:
            session['user'] = 'demo-user'
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/currencies')
def get_currencies():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    currencies = []
    docs = db.collection('currencies').stream()
    for doc in docs:
        currencies.append(doc.id)
    return jsonify(sorted(currencies))

@app.route('/api/history/<currency>')
def get_history(currency):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    history = []
    # Fetch last 30 entries
    docs = db.collection('currencies').document(currency).collection('history') \
             .order_by('timestamp', direction=firestore.Query.DESCENDING).limit(30).stream()
    
    for doc in docs:
        data = doc.to_dict()
        history.append({
            'rate': data['rate'],
            'timestamp': data['timestamp'].isoformat(),
            'date': data.get('date_string', '')
        })
    
    # Return in chronological order for charting
    return jsonify(history[::-1])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
