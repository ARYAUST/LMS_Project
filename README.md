# Northstar LMS Automation

A beginner-friendly Playwright + Python + Pytest project. It includes a small sample learning site and API so you can run the tests immediately without a school LMS account or an external server.

## What is included

- A sample LMS: register and log in, browse/search/filter courses, enroll, view progress, and edit a profile.
- JSON course API: list/get/create/replace/partially update/delete courses, with invalid input and missing-course responses.
- Playwright page objects in `pages/`, shared test data in `utils/test_data.py`, and shared browser/API fixtures in `conftest.py`.
- More than 15 UI test cases and at least 8 API test cases.
- Per-test temporary databases, so tests start with clean sample data and can run in parallel.
- Pytest HTML report, failure screenshots and traces, API exchange details, markers, retries, and xdist support.
- GitHub Actions workflow for pushes and pull requests.

## 1. Set up Python

Open a terminal in this project folder. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Install packages and the Chromium browser used by Playwright:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 2. Run the tests

```powershell
python -m pytest
```

The tests start their own local copy of the demo app. You do not need to start `app.py` separately. The HTML report is written to `reports/report.html`.

Run only a test group:

```powershell
python -m pytest tests/ui
python -m pytest tests/api
```

Run by marker, in parallel, and with one retry for failures:

```powershell
python -m pytest -m smoke
python -m pytest -m api
python -m pytest -n 2 --reruns 1
```

`smoke` is for essential flows, `regression` is for broader UI checks, and `api` marks API tests. Pytest-xdist's `-n 2` starts two workers; use `-n auto` to choose a worker count automatically.

## 3. Explore the sample LMS

To start the sample website yourself:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. The seeded student is:

- Email: `student@example.com`
- Password: `StudentPass123!`

The demo API is rooted at `/api/courses`. For example, `GET http://127.0.0.1:5000/api/courses` lists courses. API tests use Playwright's `APIRequestContext`, not browser-page fetches.

## 4. Find things in the project

- `app.py`: sample LMS pages and API endpoints.
- `templates/` and `static/`: the sample website's HTML and styling.
- `tests/ui/`: browser-based student workflow tests.
- `tests/api/`: direct API tests, including course CRUD and validation.
- `pages/`: reusable page objects that keep selectors and actions out of tests.
- `conftest.py`: browser, page, isolated sample-server, and API fixtures. Failed UI tests save a screenshot in `screenshots/` and a trace in `traces/`.
- `pytest.ini`: test discovery, HTML report, and marker names.
- `.github/workflows/playwright.yml`: continuous integration on pushes and pull requests.

In the HTML report, each API test includes an `API exchange` property with the method, URL, status, and response body. Failure artifacts are attached to the test report as properties too.

## 5. View a trace

Open a saved trace with:

```powershell
python -m playwright show-trace traces\<trace-file>.zip
```

Keep the zip artifact: the trace viewer can show actions, page snapshots, and network context around the failure.

## 6. GitHub Actions

Create a GitHub repository, then connect and push this project using the repository URL GitHub gives you:

```powershell
git init
git add .
git commit -m "Add LMS Playwright automation framework"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPOSITORY.git
git push -u origin main
```

The workflow installs Python dependencies and Chromium, runs tests in parallel with a retry, and uploads the HTML report, screenshots, and traces even when a test fails. A failing test makes the workflow fail.

## Learning notes

A **fixture** prepares something tests need, such as a browser page or API context. A **page object** gives a UI page a small set of reusable actions. **Parameterization** runs the same test with different input values. An **APIRequestContext** sends HTTP requests directly, without opening a browser page. Each test receives a temporary SQLite database, so one test's changes do not affect another test.

This sample app is for learning automation, not production use. It intentionally keeps authentication simple and does not provide production security, role-based admin access, or real course content. In an actual LMS project, point the page objects at the deployed app and configure the API base URL and credentials for the test environment.
