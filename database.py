"""Local SQLite repository for jobs, bookmarks, and API refresh history."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.environ.get('JOB_TRACKER_DB', str(Path(__file__).parent / 'job_tracker.sqlite3')))


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        with conn:
            yield conn
    finally:
        conn.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
          external_id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          company TEXT NOT NULL,
          location TEXT NOT NULL,
          job_type TEXT NOT NULL DEFAULT '',
          experience TEXT NOT NULL DEFAULT '',
          description TEXT NOT NULL DEFAULT '',
          url TEXT NOT NULL DEFAULT '',
          source TEXT NOT NULL DEFAULT '',
          posted_at TEXT NOT NULL DEFAULT '',
          first_seen TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS saved_jobs (
          external_id TEXT PRIMARY KEY REFERENCES jobs(external_id) ON DELETE CASCADE,
          status TEXT NOT NULL DEFAULT 'Saved' CHECK(status IN ('Saved','Applied','Interview','Rejected','Offer')),
          notes TEXT NOT NULL DEFAULT '',
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)


def import_jobs(jobs: list[dict]) -> int:
    """Insert unseen jobs; preserve original first_seen and user tracking data."""
    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    with connect() as conn:
        for job in jobs:
            cur = conn.execute("""
                INSERT OR IGNORE INTO jobs
                (external_id,title,company,location,job_type,experience,description,url,source,posted_at,first_seen)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (job['external_id'],job['title'],job['company'],job['location'],job['job_type'],
                  job['experience'],job['description'],job['url'],job['source'],job['posted_at'],now))
            inserted += cur.rowcount
            if cur.rowcount == 0:
                conn.execute("""UPDATE jobs SET title=?,company=?,location=?,job_type=?,experience=?,
                    description=?,url=?,source=?,posted_at=? WHERE external_id=?""",
                    (job['title'],job['company'],job['location'],job['job_type'],job['experience'],
                     job['description'],job['url'],job['source'],job['posted_at'],job['external_id']))
    return inserted


def get_jobs() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("""SELECT jobs.*, saved_jobs.status AS saved_status, saved_jobs.notes AS notes
            FROM jobs LEFT JOIN saved_jobs USING(external_id)
            ORDER BY jobs.first_seen DESC, jobs.external_id ASC""").fetchall()
    return [dict(row) for row in rows]


def get_saved_jobs() -> list[dict]:
    return [job for job in get_jobs() if job['saved_status'] is not None]


def save_job(external_id: str):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute('INSERT OR IGNORE INTO saved_jobs(external_id,status,notes,updated_at) VALUES (?,?,?,?)',
                     (external_id,'Saved','',now))


def remove_saved_job(external_id: str):
    with connect() as conn:
        conn.execute('DELETE FROM saved_jobs WHERE external_id=?', (external_id,))


def update_saved_job(external_id: str, status: str, notes: str = ''):
    if status not in {'Saved','Applied','Interview','Rejected','Offer'}:
        raise ValueError('Invalid application status')
    with connect() as conn:
        conn.execute('UPDATE saved_jobs SET status=?,notes=?,updated_at=? WHERE external_id=?',
                     (status,notes,datetime.now(timezone.utc).isoformat(),external_id))


def setting_get(key: str, default: str = '') -> str:
    with connect() as conn:
        row = conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    return row['value'] if row else default


def setting_set(key: str, value: str):
    with connect() as conn:
        conn.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key,value))
