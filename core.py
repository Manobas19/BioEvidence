"""Search discovery and transparent research-brief generation."""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests

STOP = set('the a an of in on to and or for with using i want study research'.split())

def safe_url(value):
    if not isinstance(value, str):
        return ''
    try:
        p = urlparse(value)
        return value if p.scheme in ('http', 'https') and p.hostname and not p.username else ''
    except ValueError:
        return ''

def match_score(question, text):
    q = set(re.findall(r'[a-z0-9]+', question.lower())) - STOP
    t = set(re.findall(r'[a-z0-9]+', text.lower()))
    return round(100 * len(q & t) / max(1, len(q)))

def search(key, engine, query, year):
    params = dict(api_key=key, engine=engine, q=query, hl='en')
    if engine == 'google_scholar':
        params.update(num=10, as_ylo=year)
    else:
        params['gl'] = 'in'
    try:
        response = requests.get('https://serpapi.com/search.json', params=params, timeout=(10, 40))
        if response.status_code != 200:
            return [], f'HTTP {response.status_code}: check credentials, credits, or retry later.'
        data = response.json()
        if not isinstance(data, dict) or data.get('error'):
            return [], 'Search unavailable; check API key, credits, and query.'
        rows = data.get('organic_results', [])
        if not isinstance(rows, list):
            return [], 'Unexpected search response.'
        return rows[:10], None
    except (requests.RequestException, ValueError):
        # Request exception messages can contain the secret in the request URL.
        return [], 'Connection timed out or returned an invalid response.'

def normalize(rows, kind, question):
    records = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        title = str(r.get('title') or 'Untitled')
        snippet = str(r.get('snippet') or '')
        url = safe_url(r.get('link'))
        if kind != 'Paper':
            host = urlparse(url).hostname or ''
            if host != 'ncbi.nlm.nih.gov' and not host.endswith('.ncbi.nlm.nih.gov'):
                continue
        publication = r.get('publication_info')
        publication = publication if isinstance(publication, dict) else {}
        accessions = sorted(set(re.findall(r'\b(?:GSE\d+|SRP\d+|SRR\d+|PRJNA\d+)\b', title+' '+snippet+' '+url, re.I)))
        records.append(dict(kind=kind, title=title, snippet=snippet, url=url,
                            publication=str(publication.get('summary') or ''),
                            accession_candidates=', '.join(accessions),
                            keyword_match=match_score(question, title+' '+snippet),
                            evidence_level='Search snippet only; original source not reviewed'))
    return records

def deduplicate(records):
    seen, result = set(), []
    for r in records:
        key = (r['kind'], re.sub(r'\W+', '', r['title'].lower()) or r['url'])
        if key not in seen:
            seen.add(key)
            result.append(r)
    result.sort(key=lambda r: r['keyword_match'], reverse=True)
    for i, r in enumerate(result, 1):
        r['id'] = f'S{i}'
    return result

def discover(key, question, year, resources):
    jobs = [('Paper', 'google_scholar', question),
            ('GEO', 'google', question+' site:ncbi.nlm.nih.gov/geo/query/acc.cgi'),
            ('SRA', 'google', question+' site:ncbi.nlm.nih.gov/sra')]
    records, errors = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(search, key, engine, query, year) for _, engine, query in jobs]
        for (kind, _, _), future in zip(jobs, futures):
            rows, error = future.result()
            records.extend(normalize(rows, kind, question))
            if error:
                errors.append(f'{kind}: {error}')
    return dict(question=question, resources=resources, year=year, mode='Live search',
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                records=deduplicate(records), errors=errors,
                queries=[dict(engine=e, query=q) for _, e, q in jobs])

def plan(resources):
    return [
        'Read the original papers; record study design, methods, findings, and limitations.',
        'Verify accession candidates on NCBI; inspect organism, tissue, treatment, controls, and biological replicates.',
        ('Prefer a suitable processed count matrix or small subset; check Galaxy quotas before selecting raw reads.'
         if resources == 'Laptop / browser only' else
         'Estimate disk and memory requirements before choosing a raw-read workflow.'),
        'Define the comparison and check confounding variables before analysis.',
        'Choose methods appropriate to the verified data type and study design.',
        'Record software versions, parameters, exclusions, and reproducible commands.',
        'Check proposed extensions against a broader literature review; missing search hits do not establish novelty.'
    ]

def brief(bundle, notes):
    lines = ['# BioEvidence research brief', '', f"Mode: {bundle['mode']}",
             f"Question: {bundle['question']}", f"Retrieved: {bundle['retrieved_at']}",
             f"Resources: {bundle['resources']}", f"Scholar year filter: {bundle['year']}", '',
             '## Scope', 'Discovery report, not a systematic review. Snippets and accession candidates are unverified. '
             'Keyword match is not evidence quality. Planning guidance is a template, not a validated protocol.', '',
             '## Planning checklist']
    lines += [f'{i}. {s}' for i, s in enumerate(plan(bundle['resources']), 1)]
    lines += ['', '## Sources']
    for r in bundle['records']:
        lines += ['', f"### [{r['id']}] {r['title']}", f"Type: {r['kind']}",
                  f"URL: {r['url'] or 'Unavailable'}", f"Publication: {r['publication'] or 'Not supplied'}",
                  f"Evidence: {r['evidence_level']}", f"Excerpt: {r['snippet'] or 'Not supplied'}",
                  f"Accession candidates: {r['accession_candidates'] or 'None found'}"]
    lines += ['', '## User-entered review notes']
    for row in notes:
        lines += ['', f"### {row['Source']}"] + [f'{k}: {v}' for k, v in row.items() if k != 'Source']
    lines += ['', '## Search provenance']
    lines += [f"- {q['engine']}: {q['query']}" for q in bundle['queries']]
    lines += ['', '## Search errors'] + (bundle['errors'] or ['None recorded.'])
    return '\n'.join(lines)

def demo(resources):
    # Intentionally synthetic: never use these as scientific evidence.
    return dict(question='Illustrative plant transcriptomics project', resources=resources,
                year=2020, mode='SYNTHETIC DEMO — not live search or research evidence',
                retrieved_at='Not applicable: synthetic fixture', errors=[], queries=[],
                records=[dict(id='S1', kind='Paper', title='SYNTHETIC example: plant stress study',
                              snippet='Illustrative placeholder for a search excerpt. No scientific findings are asserted.',
                              url='', publication='Synthetic example; not a real paper', accession_candidates='',
                              keyword_match=0, evidence_level='Synthetic fixture; not evidence')])
