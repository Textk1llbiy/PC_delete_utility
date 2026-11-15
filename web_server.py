from flask import Flask, jsonify, render_template
import yaml
import os
import shutil

app = Flask(__name__)
cwdir = os.path.dirname(os.path.abspath(__file__))

def get_disk_usage():
    """Get total disk space and free space on C: drive"""
    def get_disk_space(path):
        total, used, free = shutil.disk_usage(path)
        return total, used, free
    
    total, used, free = get_disk_space("C:\\")
    return {
        "total": total,
        "used": used,
        "free": free
    }

def get_weekly_data():
    """Read data from Weekly_info.yaml"""
    with open(os.path.join(cwdir, "Weekly_info.yaml"), "r") as f:
        return yaml.safe_load(f)

def human_readable_weight(size, nd=2):
    """Convert bytes to human readable format"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.{nd}f} {unit}"
        size /= 1024
    return f"{size:.{nd}f} TB"

@app.route("/")
def dashboard():
    """Serve the main dashboard page"""
    return render_template("dashboard.html")

@app.route("/api/stats")
def api_stats():
    """Return statistics as JSON"""
    disk_info = get_disk_usage()
    weekly_data = get_weekly_data()
    
    deleted_bytes = weekly_data.get("how_much_weight_deleted", 0)
    
    return jsonify({
        "total_storage": disk_info["total"],
        "used_storage": disk_info["used"],
        "free_storage": disk_info["free"],
        "deleted_all_time": deleted_bytes,
        "log_number": weekly_data.get("log_number", 0)
    })

if __name__ == "__main__":
    app.run(debug=False, port=5000)
