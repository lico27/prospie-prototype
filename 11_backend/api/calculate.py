from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
import sys
import os
from supabase import create_client

#add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scoring_logic import calculate_alignment_score

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
        Handles POST request to calculate alignment score for a funder-recipient pair.
        """

        pass

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
