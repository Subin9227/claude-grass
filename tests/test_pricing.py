import unittest

from claude_profile_stats.collector import (
    DEFAULT_PRICING_MODEL,
    MODEL_PRICING,
    _calculate_cost,
    _is_real_model,
    _resolve_pricing,
)


class PricingTests(unittest.TestCase):
    def test_known_models_exact(self):
        self.assertEqual(_resolve_pricing("claude-opus-4-8"), {"input": 5.0, "output": 25.0})
        self.assertEqual(_resolve_pricing("claude-sonnet-4-6"), {"input": 3.0, "output": 15.0})
        self.assertEqual(_resolve_pricing("claude-haiku-4-5"), {"input": 1.0, "output": 5.0})
        self.assertEqual(_resolve_pricing("claude-fable-5"), {"input": 10.0, "output": 50.0})

    def test_family_fallback_for_future_version(self):
        # An unseen future version should resolve by family, not collapse to Sonnet.
        self.assertEqual(_resolve_pricing("claude-opus-4-99"), {"input": 5.0, "output": 25.0})
        self.assertEqual(_resolve_pricing("claude-haiku-9"), {"input": 1.0, "output": 5.0})

    def test_unknown_defaults_to_sonnet(self):
        self.assertEqual(
            _resolve_pricing("totally-unknown-model"), MODEL_PRICING[DEFAULT_PRICING_MODEL]
        )
        self.assertEqual(_resolve_pricing(None), MODEL_PRICING[DEFAULT_PRICING_MODEL])

    def test_opus_costs_more_than_sonnet(self):
        # The original bug: Opus fell back to Sonnet pricing and undercounted cost.
        opus = _calculate_cost("claude-opus-4-8", 1_000_000, 1_000_000, 0, 0)
        sonnet = _calculate_cost("claude-sonnet-4-6", 1_000_000, 1_000_000, 0, 0)
        self.assertGreater(opus, sonnet)
        self.assertEqual(opus, 30.0)  # 1M in * $5 + 1M out * $25

    def test_cache_read_multiplier(self):
        # Cache reads are billed at 0.10x the input price.
        cost = _calculate_cost("claude-sonnet-4-6", 0, 0, 0, 1_000_000)
        self.assertAlmostEqual(cost, 0.3)  # 1M * $3 * 0.10

    def test_synthetic_models_filtered(self):
        self.assertFalse(_is_real_model("<synthetic>"))
        self.assertFalse(_is_real_model(None))
        self.assertFalse(_is_real_model(""))
        self.assertTrue(_is_real_model("claude-opus-4-8"))


if __name__ == "__main__":
    unittest.main()
