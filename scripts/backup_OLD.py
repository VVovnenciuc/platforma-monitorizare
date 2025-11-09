"""
Script de backup automat pentru fișierul system-state.log.
Monitorizează modificările fișierului și creează copii
cu timestamp în BACKUP_DIR.
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
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", "5"))  # secunde
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
LOG_FILE = "/data/system-state.log"
LOG_FILENAME = "backup.log"

# ===== Configurare logging =====
logger = logging.getLogger("backup_logger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(levelname)s] %(asctime)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

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


# ===== Asigură existența directorului de backup =====
if not os.path.exists(BACKUP_DIR):
    try:
        os.makedirs(BACKUP_DIR)
        logger.info("Directorul de backup a fost creat: %s", BACKUP_DIR)
    except OSError as e:
        logger.error("Nu s-a putut crea directorul de backup: %s", e)
        BACKUP_DIR = "."  # fallback: backup în directorul curent
        logger.info(
            "Backup-ul va fi făcut în directorul curent: %s", BACKUP_DIR
        )


# ===== Funcții =====
def file_hash(path: str) -> str | None:
    """Calculează hash-ul MD5 al fișierului.
    Returnează None dacă fișierul nu există.
    """
    try:
        with open(path, "rb") as file_obj:
            return hashlib.md5(file_obj.read()).hexdigest()
    except FileNotFoundError:
        return None
    except OSError as err:
        logger.error(
            "Nu s-a putut calcula hash-ul fișierului: %s: %s", path, err
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
    """
    Rulează bucla principală de monitorizare și backup al fișierului LOG_FILE.
    """
    logger.info("Pornit backup monitor pentru %s", LOG_FILE)
    logger.info("Interval backup: %d secunde", BACKUP_INTERVAL)
    logger.info("Director backup: %s", BACKUP_DIR)

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
