import os
import time
import hashlib
from datetime import datetime
import shutil

# ===== Configurări din variabile de mediu =====
BACKUP_INTERVAL = int(os.getenv("BACKUP_INTERVAL", 5))  # secunde
BACKUP_DIR = os.getenv("BACKUP_DIR", "backup")
LOG_FILE = "/data/system-state.log"

# ===== Asigură că directorul de backup există =====
if not os.path.exists(BACKUP_DIR):
    try:
        os.makedirs(BACKUP_DIR)
        print(f"[INFO] Directorul de backup a fost creat: {BACKUP_DIR}")
    except Exception as e:
        print(f"[ERROR] Nu s-a putut crea directorul de backup: {e}")
        BACKUP_DIR = "."  # fallback: backup în directorul curent

# ===== Funcție pentru calcul hash (pentru a detecta modificări) =====
def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"[ERROR] Nu s-a putut calcula hash-ul fișierului: {e}")
        return None

# ===== Main loop =====
def main():
    print(f"[INFO] Pornit backup monitor pentru {LOG_FILE}")
    print(f"[INFO] Interval backup: {BACKUP_INTERVAL} secunde")
    print(f"[INFO] Director backup: {BACKUP_DIR}")

    last_hash = file_hash(LOG_FILE)

    while True:
        try:
            time.sleep(BACKUP_INTERVAL)

            current_hash = file_hash(LOG_FILE)

            # Dacă fișierul nu există
            if current_hash is None:
                print(f"[WARN] Fișierul {LOG_FILE} nu există sau nu poate fi citit.")
                continue

            # Dacă s-a modificat, facem backup
            if current_hash != last_hash:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"system-state_{timestamp}.log"
                backup_path = os.path.join(BACKUP_DIR, backup_name)

                try:
                    shutil.copy2(LOG_FILE, backup_path)
                    print(f"[INFO] Backup efectuat: {backup_path}")
                    last_hash = current_hash
                except Exception as e:
                    print(f"[ERROR] Eroare la salvarea backup-ului: {e}")
            else:
                print(f"[INFO] Nicio modificare în {LOG_FILE}, nu se face backup.")

        except Exception as e:
            print(f"[ERROR] Eroare neașteptată în bucla principală: {e}")

# ===== Rulează scriptul =====
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Script oprit de utilizator.")
    except Exception as e:
        print(f"[FATAL] Scriptul a întâmpinat o eroare critică: {e}")
