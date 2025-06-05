PiFaaS
PiFaaS is a lightweight Function-as-a-Service (FaaS) platform designed for the Raspberry Pi Zero. It lets you deploy, run, schedule, and log small scripts (Python, Bash, etc.) remotely via HTTP — perfect for edge automation and IoT projects.

Features
Run scripts on demand: POST /<function> executes your script with optional input payload

Schedule scripts: create/remove cron jobs via HTTP (POST /schedule/<function>, DELETE /schedule/<function>)

List schedules: GET /schedule returns all scheduled functions and their cron expressions

Logs: capture and retrieve function output logs (GET /logs/<function>)

No heavy dependencies: pure Python 3, minimal setup, runs on Raspberry Pi Zero

Getting Started
Prerequisites
Raspberry Pi Zero running a Linux OS (e.g., Raspberry Pi OS Lite)

Python 3 installed

Installation
Clone or copy the PiFaaS server script to your Pi Zero.

Create the required directories:

bash
Kopieren
Bearbeiten
mkdir functions logs
Make your function scripts executable and place them inside the functions/ directory:

bash
Kopieren
Bearbeiten
chmod +x functions/hello.py
Run the server:

bash
Kopieren
Bearbeiten
python3 pi_faas_server.py
The server listens on port 8080 by default.

Usage
Run a function
bash
Kopieren
Bearbeiten
curl -X POST http://<pi-ip>:8080/hello.py -d "optional input data"
Schedule a function
Schedule hello.py to run every 5 minutes:

bash
Kopieren
Bearbeiten
curl -X POST http://<pi-ip>:8080/schedule/hello.py -d "*/5 * * * *"
List scheduled functions
bash
Kopieren
Bearbeiten
curl http://<pi-ip>:8080/schedule
Remove a scheduled function
bash
Kopieren
Bearbeiten
curl -X DELETE http://<pi-ip>:8080/schedule/hello.py
Get function logs
bash
Kopieren
Bearbeiten
curl http://<pi-ip>:8080/logs/hello.py
Function Script Requirements
Scripts must be executable (chmod +x)

Place scripts in the functions/ directory

Scripts can be any executable (Python, shell, etc.)

Input payload (POST body) is passed to the script’s stdin

Security & Notes
This server does not implement authentication or encryption — only use on trusted/private networks.

Be mindful of what scripts you deploy to avoid security risks.

Cron jobs are managed per user — the server uses the current user's crontab.

Logs are stored in logs/<function>.log and append output with timestamps.

License
MIT License — feel free to adapt and use freely.