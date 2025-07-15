from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
import time
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")

ALLOWED_EXTENSIONS = {'yaml', 'yml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def serve_frontend():
    return send_from_directory("static", "index.html")

@app.route('/validate', methods=['POST'])
def validate_yaml():
    # 🔹 1. Get skyUsername
    sky_username = request.form.get('skyUsername')
    if not sky_username:
        return jsonify({"message": "❌ skyUsername not provided."}), 400

    # 🔹 2. Build dynamic paths
    UPLOAD_FOLDER = fr"C:\Users\{sky_username}\GITHUB\ita-integration-hermes-spectral\.spectral"
    SPECTRAL_PATH = fr"C:\Users\{sky_username}\AppData\Roaming\npm\spectral.cmd"
    RULESET_PATH = os.path.join(UPLOAD_FOLDER, "spectral.yaml")

    # 🔹 3. Validate Spectral CLI and ruleset
    if not os.path.exists(SPECTRAL_PATH):
        return jsonify({"message": f"❌ Spectral CLI not found at: {SPECTRAL_PATH}"}), 500

    if not os.path.exists(RULESET_PATH):
        return jsonify({"message": f"❌ Ruleset not found at: {RULESET_PATH}"}), 500

    # 🔹 4. Handle file upload
    if 'yamlFile' not in request.files:
        return jsonify({"message": "❌ No file uploaded."}), 400

    file = request.files['yamlFile']
    if file.filename == '':
        return jsonify({"message": "❌ No selected file."}), 400

    if file and allowed_file(file.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        print(f"📂 Saving file: {file_path}")
        file.save(file_path)

        if not os.path.exists(file_path):
            return jsonify({"message": "❌ File upload failed!"}), 500

        try:
            # 🔹 5. Run Spectral command
            cmd = [SPECTRAL_PATH, "lint", file_path, "--ruleset", RULESET_PATH]
            print(f"▶️ Running command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

            print("📄 Spectral stdout:\n", result.stdout)
            print("⚠️ Spectral stderr:\n", result.stderr)

            output = result.stdout.strip() if result.stdout else "No output from Spectral."
            errors = result.stderr.strip() if result.stderr else "No errors/warnings."

            return jsonify({
                "message": f"✅ Validation Output:\n{output}\n\n❌ Errors/Warnings:\n{errors}"
            })

        except Exception as e:
            return jsonify({"message": f"❌ Error running Spectral: {str(e)}"}), 500

        finally:
            time.sleep(1)
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted file: {file_path}")
            except PermissionError:
                print(f"⚠️ Could not delete {file_path}. File might still be in use.")

    return jsonify({"message": "❌ Invalid file type. Please upload a YAML file."}), 400

if __name__ == '__main__':
    app.run(debug=True)
