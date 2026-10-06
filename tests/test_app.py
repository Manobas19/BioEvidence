import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_demo_and_exports_render(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
        self.assertFalse(app.exception)
        next(b for b in app.button if b.label == 'Explore synthetic demo').click().run()
        self.assertFalse(app.exception)
        self.assertIn('SYNTHETIC', app.session_state['bundle']['mode'])
        self.assertEqual(len(app.get('download_button')), 2)

    def test_missing_key_does_not_search(self):
        with patch.dict('os.environ', {'SERPAPI_API_KEY': ''}):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
            next(b for b in app.button if b.label == 'Search papers and datasets').click().run()
            self.assertTrue(app.error)
            self.assertFalse(app.exception)
