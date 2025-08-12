from flask import Flask, request, jsonify
from clickhouse_driver import Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_clickhouse_client():
    return Client(host='localhost')

@app.route('/track', methods=['POST'])
def track_event():
    try:
        data = request.get_json()
        print("Received payload:", data)

        if not data:
            return jsonify({"status": "error", "message": "Empty or invalid JSON"}), 400

        event_type = data.get('type')
        payload = data.get('data', {})

        if not isinstance(payload, dict):
            return jsonify({"status": "error", "message": "Payload must be a JSON object"}), 400

        page_url = payload.get('url', '')
        session_id = payload.get('session_id', 'unknown-session')
        user_agent = request.headers.get('User-Agent', '')

        if not event_type:
            return jsonify({"status": "error", "message": "Missing event type"}), 400

        # Create a new client for this request (thread-safe)
        client = get_clickhouse_client()

        client.execute(
            "INSERT INTO analytics.events (event_type, page_url, user_agent, session_id) VALUES",
            [(event_type, page_url, user_agent, session_id)]
        )

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error inserting into ClickHouse:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
