import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


@app.route("/api/download", methods=["POST"])
def download():
  data = request.get_json()
  url = data.get("url")

  if not url:
    return jsonify({"error": "Falta la URL"}), 400

  try:
    # Usamos una API pública de extracción directa para evitar bloqueos de IP en datacenters
    api_url = "https://co.wuk.sh/api/json"
    payload = {"url": url, "vquality": "720"}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    res_data = response.json()

    if res_data.get("status") == "stream" or res_data.get("url"):
      download_link = res_data.get("url") or res_data.get("picker")[0].get(
          "url"
      )
      return jsonify({"success": True, "direct_url": download_link})
    else:
      return (
          jsonify({
              "error": (
                  "No se pudo procesar el enlace. Prueba con otro video."
              )
          }),
          500,
      )

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
