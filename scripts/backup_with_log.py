import os
import time
import hashlib
from datetime import datetime
import shutil
import sys

# ===== Setare fișier backup.log în același folder cu scriptul =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_LOG_PATH = os.path.join(SCRIPT_DIR, "backup.log")

# ===== Funcție centrală de logare =====
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{level}] {timestamp} - {message}"
    print(full_message)
    try:
        with open(BACKUP_LOG_PATH, "a") as log_file:
            log_file.write(full_message + "\n")
    except Exception as e:
        print(f"[ERROR] Nu s-a putut scrie în backup.log: {e}", file=sys.stderr)

# ===== Configurări din variabile de mediu =====
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 5))  # secunde
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
LOG_FILE = "system-state.log"

# ===== Asigură că directorul de backup există =====
if not os.path.exists(BACKUP_DIR):
    try:
        os.makedirs(BACKUP_DIR)
        log(f"Directorul de backup a fost creat: {BACKUP_DIR}")
    except Exception as e:
        log(f"Nu s-a putut crea directorul de backup: {e}", "ERROR")
        BACKUP_DIR = "."  # fallback: backup în directorul curent

# ===== Funcție pentru calcul hash (pentru a detecta modificări) =====
def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        log(f"Nu s-a putut calcula hash-ul fișierului: {e}", "ERROR")
        return None

# ===== Main loop =====
def main():
    log(f"Pornit backup monitor pentru {LOG_FILE}")
    log(f"Interval backup: {BACKUP_INTERVAL} secunde")
    log(f"Director backup: {BACKUP_DIR}")

    last_hash = file_hash(LOG_FILE)

    while True:
        try:
            time.sleep(BACKUP_INTERVAL)

            current_hash = file_hash(LOG_FILE)

            if current_hash is None:
                log(f"Fișierul {LOG_FILE} nu există sau nu poate fi citit.", "WARN")
                continue

            if current_hash != last_hash:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"system-state_{timestamp}.log"
                backup_path = os.path.join(BACKUP_DIR, backup_name)

                try:
                    shutil.copy2(LOG_FILE, backup_path)
                    log(f"Backup efectuat: {backup_path}")
                    last_hash = current_hash
                except Exception as e:
                    log(f"Eroare la salvarea backup-ului: {e}", "ERROR")
            else:
                log(f"Nicio modificare în {LOG_FILE}, nu se face backup.")
        except Exception as e:
            log(f"Eroare neașteptată în bucla principală: {e}", "ERROR")

# ===== Rulează scriptul =====
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Script oprit de utilizator.", "INFO")
    except Exception as e:
        log(f"Scriptul a întâmpinat o eroare critică: {e}", "FATAL")
