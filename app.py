from flask import Flask, render_template, jsonify
import os
import speedtest

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-speedtest')
def run_speedtest():
    test = speedtest.Speedtest()
    down = round(test.download() / 10**6, 2)
    up = round(test.upload() / 10**6, 2)
    ping = test.results.ping
    return jsonify(download=down, upload=up, ping=ping)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
