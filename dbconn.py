import os
import bcrypt
import pymysql as sql
import streamlit as st


def _cfg():
    try:
        return dict(st.secrets["mysql"])
    except Exception:
        pass
    if os.environ.get("TA_DB_HOST"):
        return {
            "host": os.environ["TA_DB_HOST"],
            "port": int(os.environ.get("TA_DB_PORT", 3306)),
            "user": os.environ.get("TA_DB_USER", "root"),
            "password": os.environ.get("TA_DB_PASSWORD", ""),
            "database": os.environ.get("TA_DB_NAME", "ta_fitness"),
        }
    raise RuntimeError(
        "Database settings not found. Add a [mysql] section to the app's Secrets "
        "(Streamlit Cloud: Manage app > Settings > Secrets) or to .streamlit/secrets.toml."
    )


def get_db():
    """One place for the DB connection (credentials come from .streamlit/secrets.toml)."""
    cfg = _cfg()
    ca_pem = cfg.pop("ssl_ca", None)  # Aiven: paste the contents of its ca.pem in secrets
    if cfg.pop("ssl", False) or ca_pem:  # hosted MySQL requires TLS
        if ca_pem:
            import hashlib, tempfile
            path = os.path.join(tempfile.gettempdir(), "ta_ca_" + hashlib.md5(ca_pem.encode()).hexdigest() + ".pem")
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write(ca_pem)
            cfg["ssl"] = {"ca": path}
        else:
            import certifi
            cfg["ssl"] = {"ca": certifi.where()}
    return sql.connect(cursorclass=sql.cursors.DictCursor, **cfg)


def hash_password(plain):
    return bcrypt.hashpw(str(plain).encode(), bcrypt.gensalt()).decode()


def check_password(plain, stored):
    if not stored:
        return False
    try:
        return bcrypt.checkpw(str(plain).encode(), str(stored).encode())
    except ValueError:
        return False



MAX_FAILURES = 5
LOCK_MINUTES = 5


def lockout_remaining(smt, key):
    """Minutes left on a lockout for this login key, or 0 if not locked."""
    from datetime import datetime
    smt.execute("SELECT locked_until FROM login_attempts WHERE login_key=%s", (key,))
    row = smt.fetchone()
    if row and row["locked_until"] and row["locked_until"] > datetime.now():
        return max(1, int((row["locked_until"] - datetime.now()).total_seconds() // 60) + 1)
    return 0


def record_failure(smt, key):
    smt.execute(
        "INSERT INTO login_attempts (login_key, failures) VALUES (%s, 1) "
        "ON DUPLICATE KEY UPDATE failures = IF(locked_until IS NOT NULL AND locked_until <= NOW(), 1, failures + 1), "
        "locked_until = IF(failures >= %s, NOW() + INTERVAL %s MINUTE, NULL)",
        (key, MAX_FAILURES, LOCK_MINUTES),
    )


def clear_failures(smt, key):
    smt.execute("DELETE FROM login_attempts WHERE login_key=%s", (key,))
