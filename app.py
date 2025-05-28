from flask import Flask, request, jsonify
import requests
import validators
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def is_valid_url(url):
    return validators.url(url)

def trace_redirects(url):
    session = requests.Session()
    try:
        response = session.get(url, allow_redirects=True, timeout=10)
        return response.url, response.text
    except requests.exceptions.RequestException:
        return None, None

def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return [a['href'] for a in soup.find_all('a', href=True)]

def is_tracking_url(url):
    keywords = ['track', 'spy', 'log', 'ads', 'click', 'redirect']
    return any(word in url.lower() for word in keywords)

@app.route('/analyze', methods=['GET'])
def analyze_url():
    url = request.args.get('url')
    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400

    final_url, html = trace_redirects(url)
    if not final_url:
        return jsonify({"error": "Could not trace the URL"}), 500

    links = extract_links(html)
    suspicious_links = [l for l in links if is_tracking_url(l)]

    return jsonify({
        "input_url": url,
        "final_url": final_url,
        "is_suspicious": is_tracking_url(final_url),
        "total_links": len(links),
        "suspicious_links": suspicious_links
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 81))
    app.run(host="0.0.0.0", port=port)
