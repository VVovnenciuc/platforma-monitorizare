"""
Script de backup automat pentru fișierul system-state.log.
Monitorizează modificările fișierului și creează copii cu timestamp
în BACKUP_DIR (implicit /data/backup).
"""

import os
import time
import hashlib
from datetime import datetime
import shutil
import logging
import sys
from logging.handlers import RotatingFileHandler

# ===== Configurări din variabile de mediu =====
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", "5"))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(os.getcwd(), "data"))
LOG_FILE = os.path.join(DATA_DIR, "system-state.log")
BACKUP_DIR = os.getenv("BACKUP_DIR", os.path.join(DATA_DIR, "backup"))
LOG_FILENAME = os.path.join(DATA_DIR, "backup.log")     # log pentru backup


# ===== Configurare logging =====
logger = logging.getLogger("backup_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(levelname)s] %(asctime)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

rotating_handler = RotatingFileHandler(
    LOG_FILENAME, maxBytes=5 * 1024 * 1024, backupCount=10
)
rotating_handler.setFormatter(formatter)

# Resetăm handlerii pentru a evita dublarea logurilor
logger.handlers.clear()
logger.addHandler(console_handler)
logger.addHandler(rotating_handler)


# ===== Asigură existența directoarelor =====
for d in [DATA_DIR, BACKUP_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
        logger.info("Verificat/creat directorul: %s", d)
    except OSError as e:
        logger.error("Nu s-a putut crea directorul %s: %s", d, e)
        sys.exit(1)

logger.info("Rulează ca utilizator: %s", os.getenv("USER", "unknown"))


# ====== Funcții ======
def file_hash(path: str) -> str | None:
    """Calculează hash-ul MD5 al fișierului."""
    try:
        with open(path, "rb") as file_obj:
            return hashlib.md5(file_obj.read()).hexdigest()
    except FileNotFoundError:
        return None
    except OSError as err:
        logger.error(
            "Nu s-a putut calcula hash-ul fișierului %s: %s", path, err
            )
        return None


def backup_file(src_path: str, dest_dir: str) -> None:
    """Copiază fișierul sursă în directorul de backup cu timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"system-state_{timestamp}.log"
    backup_path = os.path.join(dest_dir, backup_name)
    try:
        shutil.copy2(src_path, backup_path)
        logger.info("Backup efectuat: %s", backup_path)
    except OSError as err2:
        logger.error("Eroare la salvarea backup-ului: %s", err2)


# ===== Loop principal =====
def main() -> None:
    """Bucla principală de backup al fișierului system-state.log."""
    logger.info("Pornit backup monitor pentru %s", LOG_FILE)
    logger.info("Interval backup: %d secunde", BACKUP_INTERVAL)
    logger.info("Director backup: %s", BACKUP_DIR)

    # Așteaptă până apare fișierul system-state.log
    while not os.path.exists(LOG_FILE):
        logger.warning("Aștept apariția fișierului %s...", LOG_FILE)
        time.sleep(3)

    last_hash = file_hash(LOG_FILE)

    while True:
        try:
            time.sleep(BACKUP_INTERVAL)
            current_hash = file_hash(LOG_FILE)

            if current_hash is None:
                logger.warning(
                    "Fișierul %s nu există sau nu poate fi citit.", LOG_FILE
                    )
                continue

            if current_hash != last_hash:
                backup_file(LOG_FILE, BACKUP_DIR)
                last_hash = current_hash
            else:
                logger.info(
                    "Nicio modificare în %s, nu se face backup.", LOG_FILE
                    )

        except KeyboardInterrupt:
            logger.info("Script oprit de utilizator.")
            break
        except OSError as err3:
            logger.error("Eroare neașteptată în bucla principală: %s", err3)


if __name__ == "__main__":
    main()
