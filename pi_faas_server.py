from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess
import os
import urllib.parse
import json
import datetime

FUNCTIONS_DIR = "./functions"
LOGS_DIR = "./logs"
SCHEDULE_FILE = "./schedules.json"
CRON_TAG = "# FaaS PiZero"

# Ensure directories and files exist
os.makedirs(FUNCTIONS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({}, f)

def load_schedules():
    with open(SCHEDULE_FILE, "r") as f:
        return json.load(f)

def save_schedules(schedules):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, indent=2)

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/schedule":
            schedules = load_schedules()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(schedules).encode())
            return

        if self.path.startswith("/logs/"):
            func_name = self.path.replace("/logs/", "")
            log_file = os.path.join(LOGS_DIR, func_name + ".log")
            if not os.path.exists(log_file):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"No logs found for function")
                return

            with open(log_file, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        func_name = parsed.path.replace("/schedule/", "")
        if not func_name:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing script name")
            return

        try:
            current_cron = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            current_cron = ""

        filtered = "\n".join(
            line for line in current_cron.splitlines()
            if f"{CRON_TAG} {func_name}" not in line
        )

        updated_cron = filtered.strip() + "\n"
        if not updated_cron.endswith("\n"):
            updated_cron += "\n"

        proc = subprocess.run(["crontab", "-"], input=updated_cron.encode(), stderr=subprocess.PIPE)
        if proc.returncode != 0:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(proc.stderr or b"Failed to update crontab")
            return

        schedules = load_schedules()
        if func_name in schedules:
            del schedules[func_name]
            save_schedules(schedules)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Removed schedule")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        func_name = parsed.path.strip("/")

        if func_name.startswith("schedule/"):
            self.handle_schedule(func_name.replace("schedule/", ""))
            return

        script_path = os.path.join(FUNCTIONS_DIR, func_name)
        if not os.path.exists(script_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Function not found")
            return

        length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(length) if length > 0 else b""

        try:
            proc = subprocess.Popen([script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, _ = proc.communicate(input=payload)

            # Append output + timestamp to log file
            log_file = os.path.join(LOGS_DIR, f"{func_name}.log")
            with open(log_file, "a") as f:
                f.write(f"\n--- Run at {datetime.datetime.now().isoformat()} ---\n")
                f.write(output.decode(errors='replace'))
                f.write("\n")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(output)

        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(e.output)
        except PermissionError:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Permission denied (is the script executable?)")

    def handle_schedule(self, script_name):
        script_path = os.path.abspath(os.path.join(FUNCTIONS_DIR, script_name))
        if not os.path.exists(script_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Function not found for scheduling")
            return

        length = int(self.headers.get('Content-Length', 0))
        cron_expr = self.rfile.read(length).decode().strip()

        if not cron_expr or len(cron_expr.split()) < 5:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid cron expression")
            return

        cron_line = f"{cron_expr} {script_path} # {CRON_TAG} {script_name}"

        try:
            current_cron = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            current_cron = ""

        filtered = "\n".join(
            line for line in current_cron.splitlines()
            if f"{CRON_TAG} {script_name}" not in line
        )

        updated_cron = f"{filtered.strip()}\n{cron_line}\n"
        if not updated_cron.endswith("\n"):
            updated_cron += "\n"

        proc = subprocess.run(["crontab", "-"], input=updated_cron.encode(), stderr=subprocess.PIPE)
        if proc.returncode != 0:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(proc.stderr or b"Failed to update crontab")
            return

        schedules = load_schedules()
        schedules[script_name] = cron_expr
        save_schedules(schedules)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Cron job set")

httpd = HTTPServer(("0.0.0.0", 8080), Handler)
print("FaaS PiZero running on port 8080")
httpd.serve_forever()
