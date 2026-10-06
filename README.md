# BioEvidence 🧬

**From scientific curiosity to a source-linked research starting point.**

A Python/Streamlit research discovery app built for the SerpApi India Hackathon 2026, Knowledge & Public Interest track. Intended users are biology students and early-career researchers planning projects with public data.

## The insight
Finding a paper is only the beginning. Students also need to locate usable data, compare methods, and decide what is feasible with available computing. BioEvidence brings paper discovery, dataset candidates, evidence review notes, and a research planning checklist into one workflow.

## Implemented
- Three concurrent SerpApi searches: Google Scholar, Google Search restricted to NCBI GEO, and Google Search restricted to NCBI SRA.
- Publication-year filtering for Scholar, duplicate-title removal within categories, and transparent keyword-overlap ranking.
- Source links, retrieval timestamps, query provenance, and explicitly unverified accession candidates.
- An editable paper-review table for methods, findings, and limitations.
- Resource-sensitive planning templates and Markdown/JSON downloads.
- Partial-failure handling with secret-safe error messages.
- Clearly labelled synthetic demonstration, usable without an API key.
- Unit and Streamlit UI smoke tests plus GitHub Actions checks.

## Run locally
Requires Python 3.11 or newer.

```bash
git clone https://github.com/Manobas19/BioEvidence.git
cd BioEvidence
python -m venv .venv
```

Activate on Linux/macOS:
```bash
source .venv/bin/activate
```

Or Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

Then:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. Enter your own [SerpApi key](https://serpapi.com/manage-api-key) in the password field, or choose **Explore synthetic demo**.

Optionally set the `SERPAPI_API_KEY` environment variable. `.env.example` is documentation only; `.env` files are not loaded automatically. Never commit real keys. Each search submission makes three requests; widget edits and downloads do not repeat searches. SerpApi caching and credit rules apply. Results and notes remain in the Streamlit session; download them before closing it.

## Demo walkthrough
1. Start with the synthetic demo to inspect the interface (it contains no real scientific claims).
2. Enter your key and search `Rice drought tolerance RNA-seq transcriptomics`.
3. Open paper links; inspect the original text before recording evidence.
4. Open GEO/SRA candidates and verify accession, organism, sample metadata, and data availability.
5. Record methods and limitations, then download the brief and JSON evidence package.

## Meaningful SerpApi usage
Search data supplies all live source candidates. Without SerpApi, only the synthetic interface demonstration is available. The app uses `engine=google_scholar` and `engine=google` through `https://serpapi.com/search.json`.

Official references:
- https://serpapi.com/google-scholar-api
- https://serpapi.com/search-api
- https://docs.streamlit.io/

## Architecture
`app.py` handles session state, forms, source browsing, evidence notes, and downloads. `core.py` performs concurrent API requests, normalizes results, filters dataset domains, ranks matches, and builds reports. Search keys are not included in reports. No LLM service is used in this MVP.

## Honest limitations
This is a discovery MVP, not a systematic review or automated research validation system. It reads search snippets, not full papers. Accession strings are candidates, not verified datasets. Keyword overlap is not scientific relevance, evidence quality, or confidence. GEO/SRA results may overlap. Search is limited to the first ten returned organic results per route; year filtering applies only to Scholar. Planning guidance is a template, not a validated dataset-specific protocol. Automated full-text extraction, contradiction detection, accession verification, and AI synthesis are future work.

Questions are sent to SerpApi. Do not enter private patient data. Before public hosting, configure authentication and per-user quotas for any shared API key. GitHub hosts the source; GitHub Pages cannot run a Python Streamlit backend.

## Validation
```bash
python -m unittest discover -s tests -v
```

Tests use mocks and synthetic data, never paid live searches. A real-key end-to-end check is still required before recording a hackathon demo.

## Hackathon submission checklist
- Add a real-search demo video and screenshots after validating with your own key.
- Include this public repository link in the organizer's submission form.
- Describe implemented features separately from future work.
- Confirm the organizer's current submission requirements and deadline.

Uploading this repository is not itself a submission to the hackathon organizer.
