import os
import time
import hashlib
from datetime import datetime
import shutil
import logging
import sys
from logging.handlers import RotatingFileHandler


# ===== Configurări din variabile de mediu =====
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 5))  # secunde
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
LOG_FILE = "/data/system-state.log"
LOG_FILENAME = 'backup.log'

# ===== Configurare logging: consolă + fișier =====
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# ===== RotatingFileHandler pentru log =====
rotating_handler = RotatingFileHandler(
    LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=10
)
rotating_handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(rotating_handler)

# ===== Asigură că directorul de backup există =====
if not os.path.exists(BACKUP_DIR):
    try:
        os.makedirs(BACKUP_DIR)
        logger.info(f"Directorul de backup a fost creat: {BACKUP_DIR}")
    except Exception as e:
        logger.error(f"Nu s-a putut crea directorul de backup: {e}")
        BACKUP_DIR = "."  # fallback: backup în directorul curent
        logger.info(f"Backup-ul va fi făcut în directorul curent: {BACKUP_DIR}")

# ===== Funcție pentru calcul hash (pentru a detecta modificări) =====
def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Nu s-a putut calcula hash-ul fișierului: {e}")
        return None

# ===== Main loop =====
def main():
    logger.info(f"Pornit backup monitor pentru {LOG_FILE}")
    logger.info(f"Interval backup: {BACKUP_INTERVAL} secunde")
    logger.info(f"Director backup: {BACKUP_DIR}")

    last_hash = file_hash(LOG_FILE)

    while True:
        try:
            time.sleep(BACKUP_INTERVAL)

            current_hash = file_hash(LOG_FILE)

            if current_hash is None:
                logger.warning(f"Fișierul {LOG_FILE} nu există sau nu poate fi citit.")
                # optional: last_hash = None
                continue

            if current_hash != last_hash:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"system-state_{timestamp}.log"
                backup_path = os.path.join(BACKUP_DIR, backup_name)

                try:
                    shutil.copy2(LOG_FILE, backup_path)
                    logger.info(f"Backup efectuat: {backup_path}")
                    last_hash = current_hash
                except Exception as e:
                    logger.error(f"Eroare la salvarea backup-ului: {e}")
            else:
                logger.info(f"Nicio modificare în {LOG_FILE}, nu se face backup.")

        except Exception as e:
            logger.error(f"Eroare neașteptată în bucla principală: {e}")

# ===== Rulează scriptul =====
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Script oprit de utilizator.")
    except Exception as e:
        logger.critical(f"Scriptul a întâmpinat o eroare critică: {e}")