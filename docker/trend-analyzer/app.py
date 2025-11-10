from flask import Flask, jsonify, request
import os
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/analyze', methods=['POST'])
def analyze():
    # Placeholder: in real app, fetch YouTube trends and publish to Pub/Sub / BigQuery
    data = request.json or {}
    return jsonify({'message': 'trend analysis simulated', 'received': data})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
