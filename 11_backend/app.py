from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from sentence_transformers import SentenceTransformer
from backend_pipeline import get_backend_data
from backend_utils import make_data_json_safe
from scoring_logic import calculate_alignment_score

#initialise
app = Flask(__name__)

#configure cors
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

#load model
model = SentenceTransformer("all-roberta-large-v1")

@app.route("/api/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "message": "prospie API is running"})

@app.route("/api/calculate", methods=["POST"])
def calculate():
    """
    Main calculation endpoint
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        user_data = data.get("userData", {})
        funder_number = data.get("funderNumber")

        if not funder_number:
            return jsonify({"error": "Funder number is required"}), 400

        #get backend data
        pair_df, grants_df, areas_df, hierarchies_df = get_backend_data(user_data, funder_number)

        #calculate score
        score, reasonings = calculate_alignment_score(pair_df, 0, grants_df, areas_df, hierarchies_df, model)

        #prepare response data
        response_data = {
            "success": True,
            "score": score,
            "user_data": user_data,
            "funder_number": funder_number,
            "reasonings": reasonings,
            "pair_data": pair_df.iloc[0].to_dict() if not pair_df.empty else {}
        }

        return jsonify(make_data_json_safe(response_data))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), 'success': False}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

#cors code adapted from Sharma (2025)