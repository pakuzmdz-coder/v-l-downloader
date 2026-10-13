import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)


@app.route("/api/download", methods=["POST"])
def download():
  data = request.get_json()
  url = data.get("url")

  if not url:
    return jsonify({"error": "Falta la URL"}), 400

  ydl_opts = {
      "format": "best[ext=mp4]/best",
      "socket_timeout": 30,
      "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
      "nocheckcertificate": True,
      "geo_bypass": True,
      "skip_download": True,  # Clave: solo extrae el enlace directo sin descargar en el servidor
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      # Obtenemos la URL de reproducción directa
      direct_url = info.get("url") or (
          info.get("formats")[-1].get("url") if info.get("formats") else None
      )

      if direct_url:
        return jsonify({"success": True, "direct_url": direct_url})
      else:
        return (
            jsonify({"error": "No se pudo obtener el enlace de descarga."}),
            500,
        )

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
