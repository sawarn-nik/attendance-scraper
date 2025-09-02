from flask import Flask, jsonify
from main import get_all_attendance

app = Flask(__name__)

@app.route('/api')
def api_attendance():
    return jsonify(get_all_attendance())

@app.route('/')
def home():
    data = get_all_attendance()
    html = "<h1>Your Attendance</h1><table border='1' cellpadding='5'><tr><th>Course</th><th>Total</th><th>Present</th><th>Absent</th><th>%</th></tr>"
    for course, info in data.items():
        html += f"<tr><td>{course}</td><td>{info['total_classes']}</td><td>{info['present']}</td><td>{info['absent']}</td><td>{info['percentage']}%</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)