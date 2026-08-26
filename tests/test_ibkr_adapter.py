import unittest

from ibkr_adapter import IBKRAdapter, LiveTradingDisabled, OrderIntent


class IBKRAdapterTests(unittest.TestCase):
    def test_default_is_paper_only(self):
        result = IBKRAdapter().submit(OrderIntent("AAPL", "BUY", 1))
        self.assertEqual(result["status"], "PAPER_ONLY")

    def test_live_requires_explicit_gate(self):
        with self.assertRaises(LiveTradingDisabled):
            IBKRAdapter(live=True)

    def test_invalid_order_rejected(self):
        with self.assertRaises(ValueError):
            IBKRAdapter().submit(OrderIntent("AAPL", "BUY", 0))


if __name__ == "__main__":
    unittest.main()
