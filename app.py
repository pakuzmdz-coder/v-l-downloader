import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route("/api/download", methods=["POST"])
def download():
  data = request.get_json()
  url = data.get("url")

  if not url:
    return jsonify({"error": "Falta la URL"}), 400

  ydl_opts = {
      "format": "best",
      "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
      "socket_timeout": 15,
  }

  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      filename = ydl.prepare_filename(info)
      # Retornamos la URL completa del archivo procesado
      return jsonify(
          {"success": True, "filename": os.path.basename(filename)}
      )
  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route("/api/file/<filename>", methods=["GET"])
def get_file(filename):
  file_path = os.path.join(DOWNLOAD_DIR, filename)
  if os.path.exists(file_path):
    return send_file(file_path, as_attachment=True)
  return jsonify({"error": "Archivo no encontrado"}), 404


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)