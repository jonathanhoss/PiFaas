# PiFaaS

PiFaaS is a lightweight Function-as-a-Service (FaaS) platform designed with a low footprint in mind (e.g., Raspberry Pi Zero). It enables you to deploy, run, schedule, and log small scripts (Python, Bash, etc.) remotely over HTTP — perfect for edge automation and IoT projects.
---

## Features
* **Run scripts on demand**
  Execute any script via `POST /` with optional input payload.

* **Schedule scripts**
  Create and remove cron jobs remotely using HTTP endpoints (`POST /schedule/`, `DELETE /schedule/`).

* **List schedules**
  Retrieve all scheduled functions and their cron expressions via `GET /schedule`.

* **View logs**
  Capture and fetch function output logs with `GET /logs/`.

* **Minimal dependencies**
  Pure Python 3, no heavy dependencies, runs efficiently on Raspberry Pi Zero.

---

## Getting Started

### Prerequisites
* Linux OS
* Python 3 installed
* cron installed and running (for scheduling scripts)


### Installation
1. Clone or copy the `pi_faas_server.py` script to your Raspberry Pi Zero.
2. Create required directories:
   ```bash
   mkdir functions logs
   ```

3. Place your function scripts inside the `functions/` directory and make them executable:
   ```bash
   chmod +x functions/hello.py
   ```

4. Run the server:

   ```bash
   python3 pi_faas_server.py
   ```

The server listens on port **8080** by default.

---

## Usage
### Run a function
```bash
curl -X POST http://<pi-zero-ip>:8080/hello.py -d "optional input data"
```

### Schedule a function
Schedule `hello.py` to run every 5 minutes:
```bash
curl -X POST http://<pi-zero-ip>:8080/schedule/hello.py -d "*/5 * * * *"
```

### List scheduled functions
```bash
curl http://<pi-zero-ip>:8080/schedule
```

### Remove a scheduled function
```bash
curl -X DELETE http://<pi-zero-ip>:8080/schedule/hello.py
```

### Get function logs
```bash
curl http://<pi-zero-ip>:8080/logs/hello.py
```

---
## Function Script Requirements

* Scripts **must be executable** (`chmod +x`).
* Place scripts inside the `functions/` directory.
* Scripts can be any executable (Python, shell, etc.).
* Input payload (POST request body) is passed to the script’s **stdin**.

---

## Security & Notes
* This server **does not implement authentication or encryption** — only use on trusted or private networks.
* Be careful what scripts you deploy to avoid security risks.
* Cron jobs are managed per user using the current user’s crontab.
* Logs are stored in `logs/` with `.log` extension, appending output with timestamps.

---

## License

MIT License — feel free to adapt and use freely.