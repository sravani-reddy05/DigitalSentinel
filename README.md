# DigitalSentinel
DigitalSentinel is a Flask and SQLite application for reviewing possible brand
impersonation indicators. Results are heuristic review signals, not proof of
fraud. Social profiles and app listings are entered manually; the project does
not scrape or claim live platform data.

## Run locally (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open <http://127.0.0.1:5000>. The app initializes SQLite and inserts five
fictional sample companies on startup. Select a company on the dashboard and
choose **Social scan** or **App scan** to open the corresponding screen.

## Optional Groq assistant

Add `GROQ_API_KEY=your_key_here` to `.env` and restart Flask. The key stays on
the server and is never shown in the UI. Without a key, the assistant uses a
small local fallback. Set `GROQ_MODEL` if you want a different supported model.

Set `SECRET_KEY` to a long random value for deployment. Keep `.env` private.

## Languages and URL reputation

Use the language menu for English, Hindi, or Telugu.
Voice recognition follows the assistant language selection when the browser
supports that recognition language. Groq replies are asked to use the selected
language; the no-key fallback has translated built-in guidance.

Set `VIRUSTOTAL_API_KEY` and/or `SAFE_BROWSING_API_KEY` in `.env` and restart
Flask. Submitted social profile and app listing URLs then query configured
reputation providers with timeouts. Provider quotas and terms apply. Profiles
and app-store listings are not fetched; their name/description scoring remains
a heuristic on entered text. Register each brand and upload its approved logo
on the brand card; social profile photos and app icons can then be compared to
that reference using a basic visual similarity signal.

## Data and demo mode

The default database is `data/digitalsentinel.db`. To disable automatic demo
seed data, set `SEED_DEMO_DATA=false`. To reinsert the fictional examples, run
`python -m database.seed_data`. Existing records are not deleted by seeding.

Social and app analysis use manually entered details and local heuristics.
URL reputation checks can be performed through the configured provider keys.
Live social monitoring and live store listing lookup are not implemented. No
findings should be treated as confirmed without human review.

## Deploy on Render

The included `render.yaml` configures a Gunicorn web service and a persistent
disk for the SQLite database and uploaded brand logos. In Render, create a new
Blueprint from this repository and apply the `render.yaml` configuration. The
Blueprint generates `SECRET_KEY` and disables demo data by default. Add
`GROQ_API_KEY`, `VIRUSTOTAL_API_KEY`, and/or `SAFE_BROWSING_API_KEY` through
the Render dashboard only if those integrations are needed; never put secret
values in `render.yaml` or source control.

The persistent disk requires a paid Render instance. The deployed app currently
does not provide user authentication or authorization; do not expose
investigation data publicly until access controls are added. Static
dependencies currently use public CDNs.
