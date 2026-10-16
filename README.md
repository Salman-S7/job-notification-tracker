# 💼 Job Notification Tracker

A beginner-friendly **Python capstone project** that helps users discover job listings, filter opportunities, save interesting roles, and track job applications. Built with **Streamlit, SQLite, and Python**. Optional integration with the **Remotive remote-jobs API** brings in real remote listings.

> **Project status:** Working prototype for local, single-user testing. Sample listings are fictional. API access depends on the external provider and internet availability. Automatic background alerts and email notifications are **not** implemented.

## 📸 Application screenshots

We will add **real screenshots from the running application** here after the interface is tested locally.

| Screenshot to capture | What to show |
| --- | --- |
| Job Search Dashboard | Search inputs, counts and job cards after loading sample jobs |
| Job Details | An expanded job listing with its description and save action |
| Saved & Applications | Saved job with application status and notes |
| Live API Results (optional) | Real listings retrieved from Remotive, if the API is working |

**How to add screenshots (macOS):**

1. Run the app and open the local Streamlit URL in your browser.
2. Load sample jobs and arrange the screen as desired.
3. Press **Command + Shift + 4** and select the area to capture.
4. Name the images `dashboard.png`, `job-details.png`, `saved-jobs.png` (and optionally `api-results.png`).
5. Add the images to an `assets/screenshots/` folder in the repository.
6. Then replace this section with images using Markdown such as `![Job Search Dashboard](assets/screenshots/dashboard.png)`.

We intentionally do not show fabricated interface screenshots.

## ✨ Features

| Feature | Details |
| --- | --- |
| Role / keyword search | Searches job title, company and description |
| Location filter | Matches a location string (including 'Remote') |
| Experience filter | Fresher / Junior / Mid / Senior / Any; jobs with unspecified experience stay visible |
| Job cards | Shows title, company, description, location and job type |
| Apply link | Opens source job URL when provided |
| Saved jobs | Bookmark and unbookmark opportunities |
| Application tracker | Mark Saved, Applied, Interview, Rejected or Offer |
| Personal notes | Store a short note for each saved job |
| Local persistence | SQLite retains information across app restarts |
| New job indicator | Highlights jobs first discovered by this local app within 24 hours |
| Duplicate handling | Tracks jobs by unique external IDs |
| Offline demo mode | Uses bundled fictional job listings |
| Optional API integration | Manually fetches remote job listings from Remotive |

**Not included:** user login, email/push notifications, scheduled daily refresh, deployment, or matching resumes with AI.

## 🧰 Technology stack

- **Python**: filtering, data processing and business logic
- **Streamlit**: user interface, search controls, job cards and tracker
- **SQLite** via Python's `sqlite3`: persistent local storage
- **Requests**: fetching external jobs through HTTP
- **JSON**: local sample dataset and API responses
- **unittest**: basic automated checks

## 🧭 User journey

1. Open the Streamlit app.
2. Choose sample jobs or fetch remote listings manually.
3. Search for a role or keyword and optionally filter by location and experience.
4. Expand a job card to read the details.
5. Save promising roles.
6. Open **Saved & applications** to update status and notes.
7. Refresh listings later to discover jobs not seen before by this installation.

## 🏗️ Architecture

```text
               Streamlit UI (main.py)
                         |
            Python jobs module (jobs.py)
                  /             \
      Sample JSON or API      Filtering
                  \             /
             Normalized job records
                         |
             SQLite (database.py)
                /              \
             Jobs          Saved jobs
                              + status
                              + notes
```

The UI and database work with a **common job format**. Provider-specific field conversion is centralized in `normalize_job()`, so the API choice can be changed later without redesigning the entire application.

## 📁 Project structure

```text
job-notification-tracker/
├── main.py                # Streamlit interface
├── jobs.py                # Filtering, normalization, API client
├── database.py            # SQLite operations and persistence
├── data/
│   └── sample_jobs.json   # Fictional job listings for learning
├── tests/
│   └── test_core.py       # Automated checks
├── requirements.txt       # Streamlit and requests
├── .gitignore             # Local data and secrets exclusions
└── README.md              # Documentation
```

After starting the application, a local `job_tracker.sqlite3` file will be created. It is deliberately not committed to GitHub.

## 🚀 Install and run locally

### 1. Prerequisites

- **Python 3.10 or later** is recommended for current Streamlit releases.
- A terminal and a code editor such as VS Code.
- Internet connectivity for initial package installation.
- No API key is needed for sample-data mode.

Check your Python version:

```bash
python3 --version
```

> **macOS note:** Many Macs expose Python as `python3`, not `python`. If your Mac shows Python 3.9.6, install a newer Python version before using the latest Streamlit packages.

### 2. Clone the repository

```bash
git clone https://github.com/Salman-S7/job-notification-tracker.git
cd job-notification-tracker
```

### 3. Create a virtual environment (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, the equivalent commands are:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If you did not activate the virtual environment, use `python3 -m pip ...` on macOS instead.

### 5. Start the app

```bash
python -m streamlit run main.py
```

Visit **http://localhost:8501** or the local URL shown in your terminal.

Stop the application with **Ctrl + C** in the terminal.

## 🧪 Manual test checklist

- [ ] App starts without an exception
- [ ] **Load sample jobs** adds fictional listings
- [ ] Keyword search for `Python` returns matching roles
- [ ] Location filter for `Bengaluru` narrows results
- [ ] Experience filter changes visible results
- [ ] Saving a job places it in **Saved & applications**
- [ ] Updating a job to `Applied` persists after restart
- [ ] Notes persist after restarting the app
- [ ] Removing a saved job removes the bookmark
- [ ] Loading the same sample dataset again does not duplicate jobs
- [ ] Optional Remotive fetch succeeds with an internet connection

### Automated tests

From the project directory:

```bash
python -m unittest discover -s tests -v
```

Tests cover sample filtering, SQLite deduplication and tracking, and Remotive response normalization. They do **not** replace a manual UI test or guarantee the external API is reachable.

## 🌐 Real jobs API integration

**Current optional provider:** [Remotive](https://remotive.com/api/remote-jobs)

- The app fetches remote job listings, not comprehensive city-specific vacancies in India.
- Fetching is **manual**; no background process runs while the app is closed.
- The prototype limits successful refreshes to once every **6 hours**.
- External job availability, API terms and response fields may change.
- Jobs without an explicit experience level remain visible for all experience filters.
- The integration is deliberately replaceable; an India-focused jobs API is not finalized.

To add a different provider later, implement a fetch function in `jobs.py` and convert its response fields into the standard format returned by `normalize_job()`.

## 🗄️ Data model and persistence

The app creates three SQLite tables:

| Table | Purpose |
| --- | --- |
| `jobs` | Normalized listing details and the original first-seen time |
| `saved_jobs` | Saved opportunities, application statuses and notes |
| `settings` | Small app settings such as the last successful API refresh |

**New** means **newly discovered by this app** within the last 24 hours, not necessarily newly published by the employer. The unique `external_id` prevents repeated imports from creating duplicate listings.

To reset the demo completely, stop the app, delete `job_tracker.sqlite3`, then launch the app again.

## 🎓 Learning outcomes

This project is intended as the final build in a Python course. Learners progressively learn to:

1. Create interfaces using Streamlit widgets.
2. Connect UI actions to Python functions and understand Streamlit reruns.
3. Work with lists and dictionaries to filter structured data.
4. Connect Python to SQLite using `sqlite3`.
5. Read JSON, make HTTP requests, and handle API responses.
6. Split an application into manageable modules.
7. Track and update persistent data.
8. Test, debug and run a complete small application.

The course material will use **progressive LEARN lessons** rather than separate PRACTICE or HOMEWORK pages.

## ⚠️ Known limitations

- This is a **single-user local prototype**. It does not implement authentication or access control and should not be publicly deployed as a multi-user application.
- SQLite data is stored on the current machine; cloning the repository does not transfer the user's saved job history.
- Sample jobs and companies are fictional.
- Application status is manually updated; the app does not submit applications.
- Job listings may expire or contain inaccurate information.
- An optional API request can fail due to network errors, provider restrictions or service changes.
- Email alerts, push notifications, recurring scheduling, and automatic daily background searches are out of scope.
- External API integration has not been end-to-end verified in this environment.

## 🧩 Planned enhancements

- Test and select a provider with stronger Indian city coverage.
- Add genuine screenshots after completing local UI testing.
- Improve dashboard layout and accessibility.
- Add scheduling and alerts as a separate advanced enhancement.
- Add import/export only if required by course scope.

---

**Course project:** Job Notification Tracker · Python final capstone · Documentation and prototype subject to refinement after testing.
