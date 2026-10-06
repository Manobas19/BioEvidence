"""Run: python live_test.py. Makes three SerpApi requests using your credits.

Reads SERPAPI_API_KEY or prompts privately in your terminal. Never prints the key.
Exit codes: 0 = all routes returned candidates, 1 = errors, 2 = incomplete results.
"""
import argparse
import getpass
import os
import sys
from core import discover, brief


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='rice drought RNA-seq')
    args = parser.parse_args()
    if len(args.query.strip()) < 8:
        print('Enter a more specific query.')
        return 2
    key = os.getenv('SERPAPI_API_KEY', '').strip()
    if not key:
        if not sys.stdin.isatty():
            print('No key configured. Run in an interactive terminal for a private prompt.')
            return 2
        key = getpass.getpass('SerpApi API key (hidden): ').strip()
    if not key:
        print('No key supplied; no requests made.')
        return 2
    print('Starting three live SerpApi requests (account credits may apply)…')
    result = discover(key, args.query.strip(), 2020, 'Laptop / browser only')
    missing = []
    for kind in ('Paper', 'GEO', 'SRA'):
        count = sum(r['kind'] == kind for r in result['records'])
        print(f'{kind}: {count} candidates')
        if not count:
            missing.append(kind)
    for error in result['errors']:
        print('ERROR:', error)
    report = brief(result, [])
    assert '## Search provenance' in report
    assert len(result['queries']) == 3
    print('Research brief generation: OK')
    if result['errors']:
        print('FAIL: one or more live searches failed.')
        return 1
    if missing:
        print('INCOMPLETE: requests completed but some routes had no candidates. Try broader keywords.')
        return 2
    print('PASS: all three routes returned candidates and report generation succeeded.')
    print('This confirms integration, not scientific validity. Review the sources in the app.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
