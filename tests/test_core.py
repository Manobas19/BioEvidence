import unittest
from unittest.mock import patch, Mock
import requests
from core import safe_url, normalize, discover, brief, demo, search

class CoreTests(unittest.TestCase):
    def test_rejects_unsafe_links_and_fake_ncbi_host(self):
        self.assertEqual(safe_url('javascript:alert(1)'), '')
        rows = [{'title': 'data', 'link': 'https://ncbi.nlm.nih.gov.evil.test/GSE12'}]
        self.assertEqual(normalize(rows, 'GEO', 'data'), [])

    def test_accessions_are_explicitly_unverified(self):
        rows = [{'title': 'GSE123 rice', 'link': 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123'}]
        r = normalize(rows, 'GEO', 'rice')[0]
        self.assertEqual(r['accession_candidates'], 'GSE123')
        self.assertIn('not reviewed', r['evidence_level'])

    @patch('core.requests.get')
    def test_request_error_never_exposes_key(self, get):
        get.side_effect = requests.RequestException('https://serpapi.com?api_key=SECRET')
        rows, error = search('SECRET', 'google', 'rice', 2020)
        self.assertEqual(rows, [])
        self.assertNotIn('SECRET', error)

    @patch('core.search')
    def test_partial_failure_preserves_success_and_provenance(self, search_mock):
        def answer(key, engine, query, year):
            return ([{'title': 'rice paper', 'link': 'https://example.org/paper'}], None) if engine == 'google_scholar' else ([], 'failure')
        search_mock.side_effect = answer
        result = discover('SECRET', 'rice', 2020, 'Laptop / browser only')
        self.assertEqual(len(result['records']), 1)
        self.assertEqual(len(result['errors']), 2)
        self.assertEqual(len(result['queries']), 3)
        self.assertNotIn('SECRET', str(result))

    @patch('core.requests.get')
    def test_malformed_response(self, get):
        get.return_value = Mock(status_code=200)
        get.return_value.json.return_value = {'organic_results': 'unexpected'}
        self.assertIsNotNone(search('key', 'google', 'rice', 2020)[1])

    def test_demo_export_keeps_synthetic_label(self):
        output = brief(demo('Laptop / browser only'), [])
        self.assertIn('SYNTHETIC DEMO', output)
        self.assertIn('not a systematic review', output)

if __name__ == '__main__':
    unittest.main()
