import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jobs import filter_jobs, normalize_job, sample_jobs


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        import database
        self.original_path = database.DB_PATH
        database.DB_PATH = Path(self.temp.name) / 'test.sqlite3'
        database.init_db()

    def tearDown(self):
        import database
        database.DB_PATH = self.original_path
        self.temp.cleanup()

    def test_sample_filtering(self):
        jobs = [normalize_job(job) for job in sample_jobs()]
        matches = filter_jobs(jobs, 'python', 'bengaluru', 'Fresher')
        self.assertEqual([j['external_id'] for j in matches], ['sample:101'])

    def test_new_job_detection_and_status_persistence(self):
        import database as db
        jobs = [normalize_job(job) for job in sample_jobs()]
        self.assertEqual(db.import_jobs(jobs), len(jobs))
        self.assertEqual(db.import_jobs(jobs), 0)
        before = db.get_jobs()[0]['first_seen']
        db.save_job('sample:101')
        db.update_saved_job('sample:101', 'Applied', 'Submitted yesterday')
        saved = db.get_saved_jobs()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]['saved_status'], 'Applied')
        self.assertEqual(saved[0]['notes'], 'Submitted yesterday')
        self.assertEqual(db.get_jobs()[0]['first_seen'], before)
        db.remove_saved_job('sample:101')
        self.assertEqual(len(db.get_saved_jobs()), 0)

    def test_remotive_normalization(self):
        result = normalize_job({'id': 99, 'title': 'Python Engineer', 'description': '<p>Hello <b>world</b></p>'}, 'remotive')
        self.assertEqual(result['external_id'], 'remotive:99')
        self.assertEqual(result['description'], 'Hello world')
        self.assertEqual(result['experience'], 'Not specified')


if __name__ == '__main__':
    unittest.main()
