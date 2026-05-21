from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ===== CẤU HÌNH =====
UPLOAD_FOLDER = os.path.join("static", "uploads")
VISIT_LOG_FILE = "visit_logs.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== DANH SÁCH EMAIL ĐƯỢC PHÉP =====
ALLOWED_EMAILS = [
    "y.2275106050559@vanlanguni.vn",
    "vy.2275106050556@vanlanguni.vn",
    "nhu.2375106052584@vanlanguni.vn",
    "thu.2475106050264@vanlanguni.vn",
    "my.2475106050141@vanlanguni.vn"
]


# ===== HÀM HỖ TRỢ =====
def read_visit_logs():
    if not os.path.exists(VISIT_LOG_FILE):
        return []
    try:
        with open(VISIT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def write_visit_logs(logs):
    with open(VISIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


# ===== ROUTE GIAO DIỆN =====
@app.route("/")
def home():
    return render_template("index.html")


# ===== LOG LỊCH SỬ TRUY CẬP =====
@app.route("/log-visit", methods=["POST"])
def log_visit():
    try:
        data = request.get_json()
        email = (data.get("email") or "").strip().lower()

        if not email:
            return jsonify({"success": False, "message": "Thiếu email"}), 400

        if email not in ALLOWED_EMAILS:
            return jsonify({"success": False, "message": "Email không hợp lệ"}), 403

        logs = read_visit_logs()
        logs.insert(0, {
            "email": email,
            "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        write_visit_logs(logs)

        return jsonify({"success": True})
    except Exception as e:
        print("Lỗi log_visit:", e)
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/get-logs", methods=["GET"])
def get_logs():
    try:
        logs = read_visit_logs()
        return jsonify(logs)
    except Exception as e:
        print("Lỗi get_logs:", e)
        return jsonify([]), 500


# ===== BÁO CÁO VỆ SINH =====
@app.route("/submit-clean-report", methods=["POST"])
def submit_clean_report():
    try:
        lab = request.form.get("lab", "").strip()
        tinh_trang = request.form.get("tinhTrang", "").strip()
        image = request.files.get("image")

        if not lab or not tinh_trang or not image:
            return jsonify({
                "success": False,
                "message": "Thiếu dữ liệu báo cáo."
            }), 400

        original_filename = secure_filename(image.filename)
        if not original_filename:
            original_filename = "image.jpg"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_{original_filename}"
        save_path = os.path.join(UPLOAD_FOLDER, new_filename)

        image.save(save_path)

        return jsonify({
            "success": True,
            "message": "Báo cáo đã được lưu thành công.",
            "file_path": f"/static/uploads/{new_filename}"
        })
    except Exception as e:
        print("Lỗi submit_clean_report:", e)
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)