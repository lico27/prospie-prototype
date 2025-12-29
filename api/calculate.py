from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import sys
import os
from supabase import create_client

#add 11_backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '11_backend')))
from scoring_logic import calculate_alignment_score

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handles POST request to calculate alignment score for a funder-recipient pair.
        """

        # Handle CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # For now, just return a test response
        response = {
            'success': True,
            'message': 'Backend received your request',
            'score': 0.5  # Placeholder
        }

        self.wfile.write(json.dumps(response).encode())


        # try:
        #     # Parse request body
        #     content_length = int(self.headers['Content-Length'])
        #     post_data = self.rfile.read(content_length)
        #     request_data = json.loads(post_data.decode('utf-8'))

        #     user_data = request_data.get('user_data')
        #     funder_number = request_data.get('funder_number')

        #     if not user_data or not funder_number:
        #         self.wfile.write(json.dumps({
        #             'error': 'Missing user_data or funder_number'
        #         }).encode())
        #         return

        #     # Initialize model for embeddings
        #     model = SentenceTransformer('all-MiniLM-L6-v2')

        #     # Generate user embeddings
        #     user_name = user_data.get('user_name', '')
        #     user_activities = user_data.get('user_activities', '')
        #     user_objectives = user_data.get('user_objectives', '')

        #     # Generate name embedding
        #     user_name_em = model.encode(user_name).tolist() if user_name else None

        #     # Generate concatenated text embedding
        #     user_concat_text = f"{user_activities} {user_objectives}".strip()
        #     user_concat_em = model.encode(user_concat_text).tolist() if user_concat_text else None

        #     # Update user_data with embeddings
        #     user_data['user_name_em'] = user_name_em
        #     user_data['user_concat_em'] = user_concat_em

        #     # TODO: Fetch funder data and create pair_df
        #     # TODO: Run scoring logic
        #     # TODO: Return alignment score

        #     response = {
        #         'success': True,
        #         'message': 'Data received and embeddings generated',
        #         'user_data': user_data
        #     }

        #     self.wfile.write(json.dumps(response).encode())

        # except Exception as e:
        #     error_response = {
        #         'error': str(e)
        #     }
        #     self.wfile.write(json.dumps(error_response).encode())


    def do_OPTIONS(self):
        """
        Handles CORS preflight request.
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

#cors snippets adapted from Sharma (2025)
