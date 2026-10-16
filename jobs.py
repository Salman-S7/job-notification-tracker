"""Job normalisation, filtering and optional remote listings provider."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAMPLE_FILE = Path(__file__).parent / 'data' / 'sample_jobs.json'


def sample_jobs() -> list[dict]:
    with SAMPLE_FILE.open(encoding='utf-8') as file:
        return json.load(file)


def normalize_job(raw: dict[str, Any], source: str = 'sample') -> dict[str, str]:
    """Map supported provider payloads into the app's common data model."""
    if source == 'remotive':
        return {
            'external_id': f"remotive:{raw['id']}",
            'title': str(raw.get('title') or 'Untitled role'),
            'company': str(raw.get('company_name') or 'Unknown company'),
            'location': str(raw.get('candidate_required_location') or 'Remote'),
            'job_type': str(raw.get('job_type') or 'Not specified'),
            'experience': 'Not specified',
            'description': strip_html(str(raw.get('description') or ''))[:3500],
            'url': str(raw.get('url') or ''),
            'source': 'Remotive',
            'posted_at': str(raw.get('publication_date') or ''),
        }
    return {
        'external_id': str(raw['external_id']),
        'title': str(raw.get('title') or 'Untitled role'),
        'company': str(raw.get('company') or 'Unknown company'),
        'location': str(raw.get('location') or 'Not specified'),
        'job_type': str(raw.get('job_type') or 'Not specified'),
        'experience': str(raw.get('experience') or 'Not specified'),
        'description': str(raw.get('description') or ''),
        'url': str(raw.get('url') or ''),
        'source': str(raw.get('source') or 'Sample'),
        'posted_at': str(raw.get('posted_at') or ''),
    }


def strip_html(content: str) -> str:
    from html.parser import HTMLParser
    class TextOnly(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    parser = TextOnly()
    parser.feed(content)
    return ' '.join(' '.join(parser.parts).split())


def filter_jobs(jobs: list[dict], keyword: str = '', location: str = '', experience: str = 'Any') -> list[dict]:
    """Case-insensitive search; unknown experience remains eligible."""
    keyword, location = keyword.strip().casefold(), location.strip().casefold()
    matches = []
    for job in jobs:
        searchable = ' '.join(str(job.get(k, '')) for k in ('title', 'company', 'description')).casefold()
        job_location = str(job.get('location', '')).casefold()
        exp = str(job.get('experience', 'Not specified')).casefold()
        exp_match = experience == 'Any' or exp in ('not specified', 'any', '') or experience.casefold() in exp
        if (not keyword or keyword in searchable) and (not location or location in job_location) and exp_match:
            matches.append(job)
    return matches


def fetch_remotive_jobs(search: str = '', limit: int = 100, timeout: int = 15) -> list[dict]:
    """Fetch Remotive remote listings. Must be called manually and sparingly."""
    import requests
    response = requests.get(
        'https://remotive.com/api/remote-jobs',
        params={'search': search.strip()} if search.strip() else None,
        timeout=timeout,
        headers={'User-Agent': 'JobTrackerLearningProject/1.0'},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get('jobs'), list):
        raise ValueError('Unexpected API response format')
    return [normalize_job(j, 'remotive') for j in payload['jobs'][:limit] if isinstance(j, dict) and 'id' in j]
