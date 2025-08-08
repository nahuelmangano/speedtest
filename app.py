from flask import Flask, render_template, jsonify
import speedtest
import os

app = Flask(__name__)

@app.route("/")
def index():
    # Página principal portfolio
    return render_template("index.html")

@app.route("/tortugas")
def tortugas_page():
    return render_template("tortuga.html")
@app.route("/perlin")
def perlin_page():
    return render_template("rperlin.html")

@app.route("/speedtest")
def speedtest_page():
    return render_template("speedtest.html")

@app.route("/run-speedtest")
def run_speedtest():
    try:
        test = speedtest.Speedtest()
        download = round(test.download() / 10**6, 2)
        upload = round(test.upload() / 10**6, 2)
        ping = test.results.ping
        return jsonify({
            "download": download,
            "upload": upload,
            "ping": ping
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
