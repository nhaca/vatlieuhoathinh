from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = 'users.json'
FILES_DIR = 'files'
MAX_DOWNLOADS = 3

# Tạo file nếu chưa tồn tại
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip().lower()
    password = data.get('password', '').strip()

    users = load_users()
    for user in users:
        if user['username'].lower() == username and user['password'] == password:
            return jsonify({
                "status": "success",
                "unlimited": user.get("unlimited", False),
                "downloads": user.get("downloads", 0)
            })

    return jsonify({"status": "error", "message": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

@app.route('/download_fla', methods=['GET'])
def download_fla():
    username = request.args.get('username', '').strip().lower()
    users = load_users()
    for user in users:
        if user['username'].lower() == username:
            if not user.get("unlimited", False):
                if user.get("downloads", 0) >= MAX_DOWNLOADS:
                    return jsonify({"status": "error", "message": "Bạn đã vượt quá số lượt tải cho phép!"}), 403
                user['downloads'] = user.get("downloads", 0) + 1
                save_users(users)

            file_path = os.path.join(FILES_DIR, 'kiem_khach.fla')
            if not os.path.exists(file_path):
                return jsonify({"status": "error", "message": "File không tồn tại."}), 404
            return send_from_directory(FILES_DIR, 'kiem_khach.fla', as_attachment=True)

    return jsonify({"status": "error", "message": "Tài khoản không hợp lệ."}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
