import unittest
import os
import json


class TestLiveOverlay(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_overlay_html_structure(self):
        html_path = os.path.join(self.base_dir, "www", "overlay.html")
        self.assertTrue(os.path.exists(html_path), "overlay.html should exist")

        with open(html_path) as f:
            content = f.read()

        # Transparent body check
        self.assertIn('class="obs-transparent"', content)
        # Lot card container
        self.assertIn('id="lot-card"', content)
        # Bidding indicators
        self.assertIn('id="start-bid"', content)
        self.assertIn('id="current-bid"', content)
        # Graded card badges
        self.assertIn('id="grade-badge"', content)
        # VIP banner
        self.assertIn('id="vip-banner"', content)
        # Viral PLG footer
        self.assertIn("Powered by", content)
        self.assertIn("whatnotelse.com", content)

    def test_overlay_css_styling(self):
        css_path = os.path.join(self.base_dir, "public", "css", "overlay.css")
        self.assertTrue(os.path.exists(css_path), "overlay.css should exist")

        with open(css_path) as f:
            css = f.read()

        # Transparent background requirement for OBS
        self.assertIn("background-color: transparent !important;", css)
        # Glassmorphism tokens
        self.assertIn("backdrop-filter:", css)
        self.assertIn("rgba(", css)
        # Pulse and animation keyframes
        self.assertIn("@keyframes pulse-glow", css)
        self.assertIn("@keyframes slide-in", css)

    def test_overlay_js_script(self):
        js_path = os.path.join(self.base_dir, "public", "js", "overlay.js")
        self.assertTrue(os.path.exists(js_path), "overlay.js should exist")

        with open(js_path) as f:
            js = f.read()

        # Endpoint polling check
        self.assertIn("whatnot_else.api.overlay.get_active_stream_telemetry", js)
        # Dynamic element binders
        self.assertIn("elCurrentBid", js)
        self.assertIn("elGradeBadge", js)
        self.assertIn("triggerVipAlert", js)
        self.assertIn("setInterval", js)


if __name__ == "__main__":
    unittest.main()
