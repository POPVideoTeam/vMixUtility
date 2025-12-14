import os
import shutil
from datetime import datetime, timedelta

BACKUP_PREFIX = "vMixBackup_"
BACKUP_TS_FMT = "%Y-%m-%d_%H-%M-%S"

import os
import shutil
from datetime import datetime, timedelta

BACKUP_PREFIX = "vMixBackup_"
TIMESTAMP_FMT = "%Y-%m-%d_%H-%M-%S"


def run_backup(config):
    src = config["backup"]["source"]
    dst_root = config["backup"]["target"]
    prune_days = int(config["backup"].get("prune_after_days", 183))

    if not src or not dst_root:
        raise ValueError("Source and target folders must be set")

    if not os.path.isdir(src):
        raise ValueError(f"Source folder does not exist: {src}")

    os.makedirs(dst_root, exist_ok=True)

    timestamp = datetime.now().strftime(TIMESTAMP_FMT)
    backup_dir = os.path.join(dst_root, f"{BACKUP_PREFIX}{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    # --- COPY ONLY .vmix FILES ---
    copied = 0
    for name in os.listdir(src):
        if not name.lower().endswith(".vmix"):
            continue

        src_file = os.path.join(src, name)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, backup_dir)
            copied += 1

    if copied == 0:
        raise RuntimeError("No .vmix files found to back up")

    # --- PRUNE OLD BACKUPS ---
    prune_backups_by_age(dst_root, prune_days)


def prune_backups_by_age(dst_root, prune_days):
    cutoff = datetime.now() - timedelta(days=prune_days)

    for name in os.listdir(dst_root):
        full_path = os.path.join(dst_root, name)

        if not os.path.isdir(full_path):
            continue
        if not name.startswith(BACKUP_PREFIX):
            continue

        try:
            ts = name[len(BACKUP_PREFIX):]
            backup_time = datetime.strptime(ts, TIMESTAMP_FMT)
        except ValueError:
            backup_time = datetime.fromtimestamp(
                os.path.getmtime(full_path)
            )

        if backup_time < cutoff:
            shutil.rmtree(full_path)



def _parse_backup_datetime(folder_name: str):
    # folder_name like: vMixBackup_2025-12-13_18-45-02
    if not folder_name.startswith(BACKUP_PREFIX):
        return None
    ts = folder_name[len(BACKUP_PREFIX):]
    try:
        return datetime.strptime(ts, BACKUP_TS_FMT)
    except ValueError:
        return None


def prune_backups_by_age(dst_root: str, max_age_days: int):
    cutoff = datetime.now() - timedelta(days=max_age_days)

    for name in os.listdir(dst_root):
        full = os.path.join(dst_root, name)
        if not os.path.isdir(full) or not name.startswith(BACKUP_PREFIX):
            continue

        dt = _parse_backup_datetime(name)
        if dt is None:
            # Fallback: use folder modified time if name doesn't parse
            dt = datetime.fromtimestamp(os.path.getmtime(full))

        if dt < cutoff:
            shutil.rmtree(full)
