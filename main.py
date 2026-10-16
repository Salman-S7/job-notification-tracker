"""Streamlit entry point. Start using: streamlit run main.py"""
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
import streamlit as st

from database import (init_db, import_jobs, get_jobs, get_saved_jobs, save_job,
                      remove_saved_job, update_saved_job, setting_get, setting_set)
from jobs import sample_jobs, normalize_job, filter_jobs, fetch_remotive_jobs

st.set_page_config(page_title='Job Notification Tracker', page_icon='💼', layout='wide')
init_db()

st.title('💼 Job Notification Tracker')
st.caption('Learn Python + Streamlit + SQLite + APIs with a working project.')

with st.sidebar:
    st.header('Data source')
    source = st.radio('Choose listings', ['Sample jobs (offline)', 'Remotive (remote jobs API)'])
    if source.startswith('Sample'):
        if st.button('Load sample jobs', use_container_width=True):
            count = import_jobs([normalize_job(job) for job in sample_jobs()])
            st.success(f'{count} new sample jobs added.')
    else:
        st.info('Remotive lists remote jobs. Not a city-specific India job API. Manual refresh only.')
        last = setting_get('remotive_last_fetch')
        allowed = True
        if last:
            try:
                elapsed = datetime.now(timezone.utc) - datetime.fromisoformat(last)
                allowed = elapsed >= timedelta(hours=6)
            except ValueError:
                pass
        if st.button('Fetch remote jobs', disabled=not allowed, use_container_width=True):
            with st.spinner('Retrieving remote jobs...'):
                try:
                    found = fetch_remotive_jobs()
                    count = import_jobs(found)
                    setting_set('remotive_last_fetch', datetime.now(timezone.utc).isoformat())
                    setting_set('latest_added', str(count))
                    st.success(f'Fetched {len(found)} listings; {count} newly discovered.')
                except Exception as exc:
                    st.error(f'Could not retrieve jobs: {exc}')
        if not allowed:
            st.caption('API refresh available six hours after the previous successful fetch.')
    st.divider()
    st.caption('Demo data is fictional. API results require internet access. Listings may expire.')

jobs = get_jobs()
all_tab, saved_tab, about_tab = st.tabs(['🔎 Find jobs', '📌 Saved & applications', 'ℹ️ About'])

with all_tab:
    a,b,c = st.columns([2,1,1])
    keyword = a.text_input('Role or keyword', placeholder='Python, backend, SQL...')
    location = b.text_input('Location', placeholder='Remote, Bengaluru...')
    experience = c.selectbox('Experience', ['Any', 'Fresher', 'Junior', 'Mid', 'Senior'])
    results = filter_jobs(jobs, keyword, location, experience)
    total_saved = len(get_saved_jobs())
    first, second, third = st.columns(3)
    first.metric('Listings in database', len(jobs))
    second.metric('Matching results', len(results))
    third.metric('Saved jobs', total_saved)
    st.caption('“New” means first discovered locally in the past 24 hours, not necessarily newly posted online.')
    if not jobs:
        st.info('Start by choosing “Load sample jobs” in the sidebar.')
    elif not results:
        st.warning('No jobs matched these filters. Try a broader search.')
    for job in results:
        try:
            seen = datetime.fromisoformat(job['first_seen'])
            is_new = datetime.now(timezone.utc) - seen < timedelta(hours=24)
        except (ValueError, TypeError):
            is_new = False
        title = f"{'🆕 ' if is_new else ''}{job['title']} — {job['company']}"
        with st.expander(title):
            st.write(f"📍 **{job['location']}** | **{job['experience']}** | {job['job_type']} | Source: {job['source']}")
            st.write(job['description'] or 'No description provided.')
            link = job['url']
            if link and urlparse(link).scheme in ('https','http'):
                st.link_button('Open application page ↗', link)
            if job['saved_status'] is None:
                if st.button('Save job', key=f"save_{job['external_id']}"):
                    save_job(job['external_id'])
                    st.rerun()
            else:
                st.success(f"Saved · {job['saved_status']}")

with saved_tab:
    saved = get_saved_jobs()
    if not saved:
        st.info('No saved jobs yet. Find an interesting opportunity and click “Save job”.')
    for job in saved:
        with st.container(border=True):
            st.subheader(f"{job['title']} — {job['company']}")
            st.caption(f"{job['location']} · {job['source']}")
            statuses = ['Saved','Applied','Interview','Rejected','Offer']
            state = st.selectbox('Application status', statuses,
                                 index=statuses.index(job['saved_status']), key=f"status_{job['external_id']}")
            notes = st.text_area('Your notes', value=job['notes'] or '', key=f"notes_{job['external_id']}")
            col1, col2 = st.columns(2)
            if col1.button('Update tracking', key=f"update_{job['external_id']}"):
                update_saved_job(job['external_id'], state, notes)
                st.success('Tracking updated.')
                st.rerun()
            if col2.button('Remove saved job', key=f"remove_{job['external_id']}"):
                remove_saved_job(job['external_id'])
                st.rerun()

with about_tab:
    st.markdown("""### How it works
1. Load fictional example listings or fetch remote jobs with the optional API.
2. Filter by keyword, location, and experience.
3. Save jobs and keep track of your application status in SQLite.
4. Fetch again later to discover jobs that are new to your local database.

**Important:** This is a single-user local learning application, not a background notification service. The API refresh is manually triggered. A scheduled email or push alert would require additional infrastructure. Remotive listings may not contain an explicit experience category; those jobs remain visible when filtering by experience. Sample listings are not real vacancies.
""")
