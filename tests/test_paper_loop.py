import unittest

from ai_trading_agent.paper_loop import ReplayConfig, run_replay


class PaperLoopTests(unittest.TestCase):
    def test_replay_is_deterministic_and_finite_by_default(self):
        config = ReplayConfig(starting_cash=10_000.0)
        first = run_replay("sample_prices.csv", config)
        second = run_replay("sample_prices.csv", config)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)

    def test_negative_interval_rejected(self):
        with self.assertRaises(ValueError):
            ReplayConfig(interval_seconds=-1).validate()


if __name__ == "__main__":
    unittest.main()
