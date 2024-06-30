from g4f.client import Client
from g4f.Provider import Bing
import json
from g4f.cookies import set_cookies
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Image, Spacer
from reportlab.lib.units import inch
import requests
import threading
from pexels_api import API
from flask import Flask, request, jsonify
import random
from cool import main, create_ebook_pdf

app = Flask(__name__)

@app.route("/api/create", methods=["POST"])
def create_ebook():
    prompt = request.args.get("prompt")
    ebook = main(prompt)
    url = create_ebook_pdf(ebook)
    return jsonify({ "url": url })

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
