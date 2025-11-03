from backup import BACKUP_INTERVAL  # importă variabila din backup.py

def test_backup_interval():
    assert BACKUP_INTERVAL > 0