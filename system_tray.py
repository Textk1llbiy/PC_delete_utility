import pystray
from PIL import Image, ImageDraw
import threading
import os
import yaml
from datetime import datetime

# Create a simple icon
def create_icon():
    """Generate a simple system tray icon"""
    image = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(image)
    # Draw a simple cleaning icon (circle with lines)
    draw.ellipse([8, 8, 56, 56], fill='#4CAF50', outline='#333333', width=2)
    draw.rectangle([20, 28, 44, 36], fill='#333333')
    return image

class SystemTrayApp:
    def __init__(self, cwdir, cleanup_callback, get_stats_callback):
        """
        Initialize system tray app
        cwdir: current working directory
        cleanup_callback: function to call when "Run Cleanup" is clicked
        get_stats_callback: function to return current stats
        """
        self.cwdir = cwdir
        self.cleanup_callback = cleanup_callback
        self.get_stats_callback = get_stats_callback
        self.icon = None
        self.tray_thread = None
        
    def create_menu(self):
        """Create the system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("Run Cleanup Now", self.on_run_cleanup),
            pystray.MenuItem("View Statistics", self.on_view_stats),
            pystray.MenuItem("View Logs Folder", self.on_view_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_exit)
        )
    
    def on_run_cleanup(self, icon, item):
        """Handle Run Cleanup menu item"""
        # Run cleanup in a separate thread to avoid blocking
        cleanup_thread = threading.Thread(target=self.cleanup_callback, daemon=True)
        cleanup_thread.start()
        return True
    
    def on_view_stats(self, icon, item):
        """Display statistics in a simple message"""
        try:
            stats = self.get_stats_callback()
            message = f"""
PC Utils Statistics
{'='*40}
Total Deleted (All Time): {stats['total_deleted']}
Current Log File: {stats['current_log']}
Last Cleanup: {stats['last_cleanup']}
{'='*40}
            """
            icon.notify(message, "Statistics")
        except Exception as e:
            icon.notify(f"Error: {e}", "Error")
        return True
    
    def on_view_logs(self, icon, item):
        """Open the logs folder"""
        logs_path = os.path.join(self.cwdir, "Logs")
        if os.path.exists(logs_path):
            os.startfile(logs_path)
        else:
            icon.notify("Logs folder not found", "Error")
        return True
    
    def on_exit(self, icon, item):
        """Exit the application"""
        icon.stop()
        return True
    
    def run(self):
        """Start the system tray app"""
        icon_image = create_icon()
        self.icon = pystray.Icon(
            "PC_Utils",
            icon_image,
            menu=self.create_menu()
        )
        self.icon.run()
    
    def start_tray(self):
        """Start the tray in a separate thread so main scheduler can run"""
        self.tray_thread = threading.Thread(target=self.run, daemon=True)
        self.tray_thread.start()

def get_stats(cwdir):
    """Get current statistics from yaml files"""
    try:
        with open(os.path.join(cwdir, "Weekly_info.yaml"), "r") as f:
            weekly_data = yaml.safe_load(f)
        
        total_deleted = weekly_data.get("how_much_weight_deleted", 0)
        log_num = weekly_data.get("log_number", 0)
        
        # Convert bytes to human readable
        total_deleted_readable = human_readable_weight(total_deleted)
        
        return {
            "total_deleted": total_deleted_readable,
            "current_log": f"Log_File_{log_num}.txt",
            "last_cleanup": "Check logs for details"
        }
    except Exception as e:
        return {
            "total_deleted": "Error reading data",
            "current_log": "Error",
            "last_cleanup": str(e)
        }

def human_readable_weight(size, nd=2):
    """Convert bytes to human readable format"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.{nd}f} {unit}"
        size /= 1024
    return f"{size:.{nd}f} TB"
