import unittest

from risk_config import RiskConfig


class RiskConfigTests(unittest.TestCase):
    def test_order_within_limit(self):
        RiskConfig(max_position_value=1000).validate_order_value(999)

    def test_order_over_limit(self):
        with self.assertRaises(ValueError):
            RiskConfig(max_position_value=1000).validate_order_value(1001)


if __name__ == "__main__":
    unittest.main()
