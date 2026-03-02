#!/usr/bin/env python3
"""
Universal A/B Test Calculator

Statistical hypothesis testing tool for comparing control vs treatment groups.
Implements z-test for proportions, t-test for means, confidence intervals,
and effect size calculations using only Python stdlib.

WHY: Provides rigorous statistical validation for experiments without external dependencies.
WHY: Adapted from ASO A/B test planning to be universally applicable.
WHY: Class-based design allows reusable components across different test scenarios.
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

# WHY: Import cross-platform utilities for consistency
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import atomic_write_json  # type: ignore[import-not-found]  # noqa: E402
from thresholds import VERIFICATION  # type: ignore[import-not-found]  # noqa: E402


class ABTestCalculator:
    """
    Statistical calculator for A/B testing.

    WHY: Encapsulates all statistical operations in one reusable class.
    WHY: Maintains test parameters (alpha, power, MDE) as state for consistency.
    WHY: Separates concerns: calculation logic vs CLI interface.
    """

    def __init__(self) -> None:
        """
        Initialize calculator with default parameters from shared thresholds.

        WHY: Default alpha from VERIFICATION.STATISTICAL_ALPHA (industry standard 95% confidence).
        WHY: Default power from VERIFICATION.STATISTICAL_POWER (80% chance of detecting real effect).
        WHY: Default MDE from VERIFICATION.STATISTICAL_MDE (5% minimum detectable effect).
        """
        # WHY: Use shared thresholds for consistent defaults across all verification tools
        self.alpha: float = (
            VERIFICATION.STATISTICAL_ALPHA
        )  # Significance level (Type I error rate)
        self.power: float = (
            VERIFICATION.STATISTICAL_POWER
        )  # Statistical power (1 - Type II error rate)
        self.mde: float = VERIFICATION.STATISTICAL_MDE  # Minimum Detectable Effect
        self.results: dict[str, Any] = {}  # Store calculation results

    def set_parameters(
        self, alpha: float = 0.05, power: float = 0.80, mde: float = 0.05
    ) -> None:
        """
        Set statistical test parameters.

        WHY: Allows customization of test sensitivity and rigor.
        WHY: Validates parameters to prevent statistical errors.

        Args:
            alpha: Significance level (probability of false positive)
            power: Statistical power (probability of detecting true effect)
            mde: Minimum detectable effect (smallest meaningful difference)

        Raises:
            ValueError: If parameters are outside valid ranges
        """
        if not 0 < alpha < 1:
            raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
        if not 0 < power < 1:
            raise ValueError(f"Power must be between 0 and 1, got {power}")
        if not 0 < mde < 1:
            raise ValueError(f"MDE must be between 0 and 1, got {mde}")

        self.alpha = alpha
        self.power = power
        self.mde = mde

    def _z_score(self, confidence: float) -> float:
        """
        Calculate z-score for given confidence level using inverse normal CDF.

        WHY: Z-scores are fundamental to hypothesis testing but not in stdlib.
        WHY: Approximation using Taylor series is accurate enough for our purposes.

        Args:
            confidence: Confidence level (e.g., 0.95 for 95% confidence)

        Returns:
            Z-score corresponding to confidence level
        """
        # WHY: Common z-scores hardcoded for speed and accuracy
        z_scores = {
            0.80: 1.282,
            0.85: 1.440,
            0.90: 1.645,
            0.95: 1.960,
            0.975: 2.240,
            0.99: 2.576,
            0.995: 2.807,
        }

        if confidence in z_scores:
            return z_scores[confidence]

        # WHY: For non-standard confidence levels, use approximation
        # WHY: This is the Beasley-Springer-Moro algorithm approximation
        p = confidence
        if p > 0.5:
            p = 1 - p

        # WHY: Coefficients from Beasley-Springer-Moro approximation
        a = [2.50662823884, -18.61500062529, 41.39119773534, -25.44106049637]
        b = [-8.47351093090, 23.08336743743, -21.06224101826, 3.13082909833]
        c = [
            0.3374754822726147,
            0.9761690190917186,
            0.1607979714918209,
            0.0276438810333863,
            0.0038405729373609,
            0.0003951896511919,
            0.0000321767881768,
            0.0000002888167364,
            0.0000003960315187,
        ]

        y = p - 0.5
        r = y * y

        if abs(y) < 0.42:
            # WHY: Central region approximation
            z = (
                y
                * (((a[3] * r + a[2]) * r + a[1]) * r + a[0])
                / ((((b[3] * r + b[2]) * r + b[1]) * r + b[0]) * r + 1)
            )
        else:
            # WHY: Tail region approximation
            r = p if y < 0 else 1 - p
            r = math.log(-math.log(r))
            z = c[0]
            for i in range(1, len(c)):
                z += c[i] * (r**i)
            if y < 0:
                z = -z

        return abs(z) if confidence > 0.5 else z

    def _t_critical(self, df: int, alpha: float) -> float:
        """
        Approximate t-critical value for given degrees of freedom and alpha.

        WHY: T-distribution critical values needed for small samples but not in stdlib.
        WHY: For large df (>30), t-distribution converges to normal distribution.

        Args:
            df: Degrees of freedom
            alpha: Significance level

        Returns:
            Critical t-value
        """
        # WHY: For large samples, t-distribution ≈ normal distribution
        if df > 30:
            return self._z_score(1 - alpha / 2)

        # WHY: Hardcoded t-critical values for common df and alpha=0.05
        # WHY: Source: Standard t-distribution tables
        t_table = {
            1: 12.706,
            2: 4.303,
            3: 3.182,
            4: 2.776,
            5: 2.571,
            6: 2.447,
            7: 2.365,
            8: 2.306,
            9: 2.262,
            10: 2.228,
            11: 2.201,
            12: 2.179,
            13: 2.160,
            14: 2.145,
            15: 2.131,
            16: 2.120,
            17: 2.110,
            18: 2.101,
            19: 2.093,
            20: 2.086,
            21: 2.080,
            22: 2.074,
            23: 2.069,
            24: 2.064,
            25: 2.060,
            26: 2.056,
            27: 2.052,
            28: 2.048,
            29: 2.045,
            30: 2.042,
        }

        if abs(alpha - 0.05) < 0.001:  # WHY: alpha ≈ 0.05
            return t_table.get(df, self._z_score(1 - alpha / 2))

        # WHY: For other alpha values, use z-score approximation
        return self._z_score(1 - alpha / 2)

    def calculate_sample_size(self, baseline_rate: float) -> int:
        """
        Calculate required sample size per group for proportion test.

        WHY: Sample size determines test sensitivity and duration.
        WHY: Uses standard formula for comparing two proportions.

        Formula:
            n = 2 * ((Z_α/2 + Z_β)² * p * (1-p)) / MDE²

        Where:
            Z_α/2: Z-score for significance level (two-tailed)
            Z_β: Z-score for power (1 - β)
            p: Baseline proportion
            MDE: Minimum detectable effect

        Args:
            baseline_rate: Expected proportion in control group (0-1)

        Returns:
            Required sample size per group

        Raises:
            ValueError: If baseline_rate is outside valid range
        """
        if not 0 < baseline_rate < 1:
            raise ValueError(
                f"Baseline rate must be between 0 and 1, got {baseline_rate}"
            )

        # WHY: Two-tailed test requires alpha/2
        z_alpha = self._z_score(1 - self.alpha / 2)
        # WHY: Power is probability of detecting effect when it exists
        z_beta = self._z_score(self.power)

        # WHY: Pooled variance for two proportions
        p = baseline_rate
        variance = p * (1 - p)

        # WHY: Standard sample size formula for two-proportion z-test
        n = 2 * ((z_alpha + z_beta) ** 2) * variance / (self.mde**2)

        # WHY: Round up to ensure adequate power
        return math.ceil(n)

    def run_proportion_test(
        self, control: dict[str, Any], treatment: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Run z-test for comparing two proportions.

        WHY: Proportions (conversion rates, success rates) are common in A/B tests.
        WHY: Z-test is appropriate for large samples (n > 30) with proportions.

        Args:
            control: {"values": [successes], "n": total_trials}
            treatment: {"values": [successes], "n": total_trials}

        Returns:
            Dict with p_value, ci, effect_size, significant, recommendation

        Example:
            control = {"values": [120], "n": 1000}  # 12% conversion
            treatment = {"values": [150], "n": 1000}  # 15% conversion
        """
        # WHY: Extract raw counts from input format
        control_successes = sum(control["values"])
        control_n = control["n"]
        treatment_successes = sum(treatment["values"])
        treatment_n = treatment["n"]

        # WHY: Calculate sample proportions
        p1 = control_successes / control_n
        p2 = treatment_successes / treatment_n

        # WHY: Pooled proportion for z-test (assumes null hypothesis is true)
        p_pooled = (control_successes + treatment_successes) / (control_n + treatment_n)

        # WHY: Standard error under null hypothesis (no difference)
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / control_n + 1 / treatment_n))

        # WHY: Z-statistic measures difference in standard error units
        z_stat = (p2 - p1) / se if se > 0 else 0

        # WHY: Convert z-statistic to p-value (two-tailed test)
        p_value = self._z_to_p_value(z_stat)

        # WHY: Confidence interval shows range of plausible true differences
        ci = self._proportion_ci(p1, p2, control_n, treatment_n)

        # WHY: Effect size (difference in proportions) shows practical significance
        effect_size = p2 - p1

        # WHY: Cohen's h for proportions (standardized effect size)
        cohens_h = 2 * (math.asin(math.sqrt(p2)) - math.asin(math.sqrt(p1)))

        # WHY: Determine statistical significance
        significant = p_value < self.alpha

        # WHY: Store results for interpretation
        self.results = {
            "test_type": "proportion_test",
            "control_rate": p1,
            "treatment_rate": p2,
            "difference": effect_size,
            "z_statistic": z_stat,
            "p_value": p_value,
            "confidence_interval": ci,
            "cohens_h": cohens_h,
            "significant": significant,
            "alpha": self.alpha,
            "recommendation": self._make_recommendation(
                significant, effect_size, p_value
            ),
        }

        return self.results

    def run_mean_test(
        self, control: dict[str, Any], treatment: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Run t-test for comparing two means.

        WHY: Means (average time, revenue, engagement) are common metrics.
        WHY: T-test handles small samples and unknown population variance.

        Args:
            control: {"values": [v1, v2, ...], "n": count}
            treatment: {"values": [v1, v2, ...], "n": count}

        Returns:
            Dict with p_value, ci, effect_size, significant, recommendation
        """
        control_values = control["values"]
        treatment_values = treatment["values"]

        n1 = len(control_values)
        n2 = len(treatment_values)

        # WHY: Calculate sample means
        mean1 = sum(control_values) / n1
        mean2 = sum(treatment_values) / n2

        # WHY: Calculate sample variances (unbiased estimator uses n-1)
        var1 = sum((x - mean1) ** 2 for x in control_values) / (n1 - 1)
        var2 = sum((x - mean2) ** 2 for x in treatment_values) / (n2 - 1)

        # WHY: Pooled standard deviation (assumes equal variances)
        sp = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        # WHY: Standard error of difference between means
        se = sp * math.sqrt(1 / n1 + 1 / n2)

        # WHY: T-statistic measures difference in standard error units
        t_stat = (mean2 - mean1) / se if se > 0 else 0

        # WHY: Degrees of freedom for pooled t-test
        df = n1 + n2 - 2

        # WHY: Convert t-statistic to p-value
        p_value = self._t_to_p_value(t_stat, df)

        # WHY: Confidence interval for difference in means
        ci = self._mean_ci(mean1, mean2, se, df)

        # WHY: Effect size (difference in means)
        effect_size = mean2 - mean1

        # WHY: Cohen's d (standardized effect size)
        cohens_d = effect_size / sp if sp > 0 else 0

        # WHY: Determine statistical significance
        significant = p_value < self.alpha

        # WHY: Store results for interpretation
        self.results = {
            "test_type": "mean_test",
            "control_mean": mean1,
            "treatment_mean": mean2,
            "difference": effect_size,
            "t_statistic": t_stat,
            "degrees_of_freedom": df,
            "p_value": p_value,
            "confidence_interval": ci,
            "cohens_d": cohens_d,
            "significant": significant,
            "alpha": self.alpha,
            "recommendation": self._make_recommendation(
                significant, effect_size, p_value
            ),
        }

        return self.results

    def get_confidence_interval(
        self, data: dict[str, Any], confidence: float = 0.95
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for a single sample mean.

        WHY: Confidence intervals quantify uncertainty in estimates.
        WHY: Useful for understanding range of plausible values.

        Args:
            data: {"values": [v1, v2, ...], "n": count}
            confidence: Confidence level (e.g., 0.95 for 95% CI)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        values = data["values"]
        n = len(values)

        # WHY: Calculate sample mean
        mean = sum(values) / n

        # WHY: Calculate sample standard deviation
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = math.sqrt(variance)

        # WHY: Standard error of the mean
        se = std / math.sqrt(n)

        # WHY: Critical value depends on sample size
        df = n - 1
        if n > 30:
            # WHY: Large sample: use z-score
            critical = self._z_score(confidence)
        else:
            # WHY: Small sample: use t-score
            alpha = 1 - confidence
            critical = self._t_critical(df, alpha)

        # WHY: Margin of error
        margin = critical * se

        return (mean - margin, mean + margin)

    def _z_to_p_value(self, z: float) -> float:
        """
        Convert z-statistic to two-tailed p-value.

        WHY: P-value is probability of observing result if null hypothesis is true.
        WHY: Two-tailed test considers both directions of effect.

        Args:
            z: Z-statistic

        Returns:
            Two-tailed p-value
        """
        # WHY: Use complementary error function approximation
        # WHY: For normal distribution: P(Z > z) = 0.5 * erfc(z / √2)

        # WHY: Absolute value for two-tailed test
        z = abs(z)

        # WHY: Approximate cumulative normal distribution using polynomial
        # WHY: Abramowitz and Stegun approximation (max error 7.5e-8)
        t = 1.0 / (1.0 + 0.2316419 * z)
        d = 0.3989423 * math.exp(-z * z / 2.0)
        p = (
            d
            * t
            * (
                0.3193815
                + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))
            )
        )

        # WHY: Two-tailed p-value is twice one-tailed
        return 2.0 * p

    def _t_to_p_value(self, t: float, df: int) -> float:
        """
        Convert t-statistic to two-tailed p-value.

        WHY: T-distribution has heavier tails than normal for small samples.
        WHY: Approximates normal as df increases.

        Args:
            t: T-statistic
            df: Degrees of freedom

        Returns:
            Two-tailed p-value
        """
        # WHY: For large df, t-distribution ≈ normal
        if df > 30:
            return self._z_to_p_value(t)

        # WHY: Absolute value for two-tailed test
        t = abs(t)

        # WHY: Hill's approximation for t-distribution CDF
        # WHY: Accurate for practical purposes (error < 0.005)
        x = df / (df + t * t)

        # WHY: Incomplete beta function approximation
        p = 0.5 * self._beta_cdf(x, df / 2.0, 0.5)

        # WHY: Two-tailed p-value
        return 2.0 * p if p < 0.5 else 1.0

    def _beta_cdf(self, x: float, a: float, b: float) -> float:
        """
        Approximate cumulative distribution function of beta distribution.

        WHY: Beta CDF is used in t-distribution calculation.
        WHY: No stdlib implementation available.

        Args:
            x: Value at which to evaluate CDF
            a: First shape parameter
            b: Second shape parameter

        Returns:
            Approximate CDF value
        """
        # WHY: Simple approximation for t-test purposes
        # WHY: More accurate methods require gamma function
        if x <= 0:
            return 0.0
        if x >= 1:
            return 1.0

        # WHY: Use continued fraction approximation
        # WHY: Lentz's algorithm for incomplete beta function
        eps = 1e-10
        z = a + b
        c = 1.0
        d = 1.0 - z * x / (a + 1.0)
        if abs(d) < eps:
            d = eps
        d = 1.0 / d
        h = d

        for i in range(1, 100):
            m2 = 2 * i
            aa = i * (b - i) * x / ((a + m2 - 1.0) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < eps:
                d = eps
            c = 1.0 + aa / c
            if abs(c) < eps:
                c = eps
            d = 1.0 / d
            h *= d * c

            aa = -(a + i) * (z + i) * x / ((a + m2) * (a + m2 + 1.0))
            d = 1.0 + aa * d
            if abs(d) < eps:
                d = eps
            c = 1.0 + aa / c
            if abs(c) < eps:
                c = eps
            d = 1.0 / d
            delta = d * c
            h *= delta

            if abs(delta - 1.0) < eps:
                break

        return h

    def _proportion_ci(
        self, p1: float, p2: float, n1: int, n2: int
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for difference in proportions.

        WHY: Shows range of plausible true differences.
        WHY: Uses unpooled standard error (unlike test statistic).

        Args:
            p1: Control proportion
            p2: Treatment proportion
            n1: Control sample size
            n2: Treatment sample size

        Returns:
            Tuple of (lower_bound, upper_bound) for difference
        """
        # WHY: Difference in proportions
        diff = p2 - p1

        # WHY: Unpooled standard error (for CI, not test)
        se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)

        # WHY: Critical value for two-tailed test
        z = self._z_score(1 - self.alpha / 2)

        # WHY: Margin of error
        margin = z * se

        return (diff - margin, diff + margin)

    def _mean_ci(
        self, mean1: float, mean2: float, se: float, df: int
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for difference in means.

        WHY: Shows range of plausible true differences.
        WHY: Uses t-distribution for small samples.

        Args:
            mean1: Control mean
            mean2: Treatment mean
            se: Standard error of difference
            df: Degrees of freedom

        Returns:
            Tuple of (lower_bound, upper_bound) for difference
        """
        # WHY: Difference in means
        diff = mean2 - mean1

        # WHY: Critical t-value
        t = self._t_critical(df, self.alpha)

        # WHY: Margin of error
        margin = t * se

        return (diff - margin, diff + margin)

    def _make_recommendation(
        self, significant: bool, effect_size: float, p_value: float
    ) -> str:
        """
        Generate human-readable interpretation of results.

        WHY: Statistical significance alone doesn't imply practical importance.
        WHY: Must consider effect size and business context.

        Args:
            significant: Whether result is statistically significant
            effect_size: Magnitude of difference
            p_value: Probability under null hypothesis

        Returns:
            Recommendation string
        """
        if not significant:
            return (
                f"No statistically significant difference detected (p={p_value:.4f} > α={self.alpha}). "
                f"The observed difference of {effect_size:.4f} could be due to random variation. "
                f"Consider: (1) increasing sample size, (2) running test longer, or (3) accepting null hypothesis."
            )

        # WHY: Significant result requires effect size interpretation
        effect_interpretation = self._interpret_effect_size(effect_size)

        direction = "increase" if effect_size > 0 else "decrease"

        return (
            f"Statistically significant {direction} detected (p={p_value:.4f} < α={self.alpha}). "
            f"Effect size: {effect_size:.4f} ({effect_interpretation}). "
            f"Recommendation: Consider implementing treatment if effect is practically meaningful for your use case."
        )

    def _interpret_effect_size(self, effect: float) -> str:
        """
        Interpret effect size magnitude using Cohen's guidelines.

        WHY: Provides context for whether effect is practically meaningful.
        WHY: Cohen's benchmarks: small=0.2, medium=0.5, large=0.8 (for standardized effects).

        Args:
            effect: Effect size (raw or standardized)

        Returns:
            Interpretation string
        """
        # WHY: Use absolute value for magnitude
        abs_effect = abs(effect)

        # WHY: For proportions, use percentage point interpretation
        if "proportion_test" in str(self.results.get("test_type", "")):
            pct = abs_effect * 100
            if pct < 1:
                return f"very small ({pct:.2f} percentage points)"
            elif pct < 5:
                return f"small ({pct:.2f} percentage points)"
            elif pct < 10:
                return f"medium ({pct:.2f} percentage points)"
            else:
                return f"large ({pct:.2f} percentage points)"

        # WHY: For means, use Cohen's d benchmarks
        if abs_effect < 0.2:
            return "very small"
        elif abs_effect < 0.5:
            return "small"
        elif abs_effect < 0.8:
            return "medium"
        else:
            return "large"

    def interpret_results(self) -> str:
        """
        Generate comprehensive human-readable interpretation.

        WHY: Makes statistical results accessible to non-statisticians.
        WHY: Provides actionable insights, not just numbers.

        Returns:
            Multi-line interpretation string
        """
        if not self.results:
            return "No test results available. Run a test first."

        test_type = self.results["test_type"]

        if test_type == "proportion_test":
            return self._interpret_proportion_test()
        elif test_type == "mean_test":
            return self._interpret_mean_test()
        else:
            return "Unknown test type."

    def _interpret_proportion_test(self) -> str:
        """
        WHY: Tailored interpretation for proportion tests (conversion rates, etc.).
        """
        r = self.results

        interpretation = []
        interpretation.append("=" * 60)
        interpretation.append("A/B TEST RESULTS - PROPORTION TEST")
        interpretation.append("=" * 60)
        interpretation.append("")

        interpretation.append("SAMPLE STATISTICS:")
        interpretation.append(
            f"  Control rate:    {r['control_rate']:.4f} ({r['control_rate'] * 100:.2f}%)"
        )
        interpretation.append(
            f"  Treatment rate:  {r['treatment_rate']:.4f} ({r['treatment_rate'] * 100:.2f}%)"
        )
        interpretation.append(
            f"  Difference:      {r['difference']:.4f} ({r['difference'] * 100:.2f} percentage points)"
        )
        interpretation.append("")

        interpretation.append("STATISTICAL TEST:")
        interpretation.append(f"  Z-statistic:     {r['z_statistic']:.4f}")
        interpretation.append(f"  P-value:         {r['p_value']:.6f}")
        interpretation.append(f"  Significance:    α = {r['alpha']}")
        interpretation.append(
            f"  Result:          {'SIGNIFICANT' if r['significant'] else 'NOT SIGNIFICANT'}"
        )
        interpretation.append("")

        ci_lower, ci_upper = r["confidence_interval"]
        interpretation.append("CONFIDENCE INTERVAL (95%):")
        interpretation.append(f"  Difference:      [{ci_lower:.4f}, {ci_upper:.4f}]")
        interpretation.append(
            f"  Interpretation:  The true difference is likely between {ci_lower * 100:.2f}% and {ci_upper * 100:.2f}%"
        )
        interpretation.append("")

        interpretation.append("EFFECT SIZE:")
        interpretation.append(f"  Cohen's h:       {r['cohens_h']:.4f}")
        interpretation.append("")

        interpretation.append("RECOMMENDATION:")
        interpretation.append(f"  {r['recommendation']}")
        interpretation.append("")
        interpretation.append("=" * 60)

        return "\n".join(interpretation)

    def _interpret_mean_test(self) -> str:
        """
        WHY: Tailored interpretation for mean tests (revenue, time, etc.).
        """
        r = self.results

        interpretation = []
        interpretation.append("=" * 60)
        interpretation.append("A/B TEST RESULTS - MEAN TEST")
        interpretation.append("=" * 60)
        interpretation.append("")

        interpretation.append("SAMPLE STATISTICS:")
        interpretation.append(f"  Control mean:    {r['control_mean']:.4f}")
        interpretation.append(f"  Treatment mean:  {r['treatment_mean']:.4f}")
        interpretation.append(f"  Difference:      {r['difference']:.4f}")
        interpretation.append("")

        interpretation.append("STATISTICAL TEST:")
        interpretation.append(f"  T-statistic:     {r['t_statistic']:.4f}")
        interpretation.append(f"  Degrees of freedom: {r['degrees_of_freedom']}")
        interpretation.append(f"  P-value:         {r['p_value']:.6f}")
        interpretation.append(f"  Significance:    α = {r['alpha']}")
        interpretation.append(
            f"  Result:          {'SIGNIFICANT' if r['significant'] else 'NOT SIGNIFICANT'}"
        )
        interpretation.append("")

        ci_lower, ci_upper = r["confidence_interval"]
        interpretation.append("CONFIDENCE INTERVAL (95%):")
        interpretation.append(f"  Difference:      [{ci_lower:.4f}, {ci_upper:.4f}]")
        interpretation.append("")

        interpretation.append("EFFECT SIZE:")
        interpretation.append(f"  Cohen's d:       {r['cohens_d']:.4f}")
        interpretation.append("")

        interpretation.append("RECOMMENDATION:")
        interpretation.append(f"  {r['recommendation']}")
        interpretation.append("")
        interpretation.append("=" * 60)

        return "\n".join(interpretation)


def main() -> None:
    """
    CLI interface for A/B test calculator.

    WHY: Provides command-line access for scripting and automation.
    WHY: JSON I/O allows integration with other tools.
    """
    parser = argparse.ArgumentParser(
        description="Universal A/B Test Calculator - Statistical hypothesis testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Proportion test (conversion rates)
  python ab_test_calculator.py --control control.json --treatment treatment.json

  # Mean test with custom alpha
  python ab_test_calculator.py --control control.json --treatment treatment.json --alpha 0.01

  # Calculate sample size
  python ab_test_calculator.py --sample-size 0.12 --mde 0.05 --power 0.80

Input format (JSON):
  Proportions: {"values": [120], "n": 1000}  # 120 successes out of 1000 trials
  Means: {"values": [1.2, 1.5, 1.8, ...], "n": 100}  # List of observations
""",
    )

    # WHY: Input files
    parser.add_argument("--control", type=str, help="Path to control group JSON file")
    parser.add_argument(
        "--treatment", type=str, help="Path to treatment group JSON file"
    )

    # WHY: Test parameters
    parser.add_argument(
        "--alpha", type=float, default=0.05, help="Significance level (default: 0.05)"
    )
    parser.add_argument(
        "--power", type=float, default=0.80, help="Statistical power (default: 0.80)"
    )
    parser.add_argument(
        "--mde",
        type=float,
        default=0.05,
        help="Minimum detectable effect (default: 0.05)",
    )

    # WHY: Test type
    parser.add_argument(
        "--test-type",
        type=str,
        choices=["proportion", "mean", "auto"],
        default="auto",
        help="Type of test to run (default: auto-detect)",
    )

    # WHY: Output
    parser.add_argument(
        "--output", type=str, help="Path to output JSON file (optional)"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed interpretation"
    )

    # WHY: Sample size calculation
    parser.add_argument(
        "--sample-size",
        type=float,
        help="Calculate required sample size for given baseline rate",
    )

    args = parser.parse_args()

    # WHY: Initialize calculator
    calc = ABTestCalculator()
    calc.set_parameters(alpha=args.alpha, power=args.power, mde=args.mde)

    # WHY: Sample size calculation mode
    if args.sample_size is not None:
        try:
            n = calc.calculate_sample_size(args.sample_size)
            result = {
                "mode": "sample_size_calculation",
                "baseline_rate": args.sample_size,
                "alpha": args.alpha,
                "power": args.power,
                "mde": args.mde,
                "required_sample_size_per_group": n,
                "total_required_sample_size": 2 * n,
            }

            print(json.dumps(result, indent=2))

            if args.verbose:
                print(
                    f"\nTo detect a {args.mde * 100}% effect with {args.power * 100}% power:"
                )
                print(f"  Required sample size per group: {n:,}")
                print(f"  Total required sample size: {2 * n:,}")

            return
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # WHY: A/B test mode requires both control and treatment
    if not args.control or not args.treatment:
        parser.error("Both --control and --treatment are required for A/B testing")

    try:
        # WHY: Load input data
        with open(args.control, "r") as f:
            control = json.load(f)
        with open(args.treatment, "r") as f:
            treatment = json.load(f)

        # WHY: Auto-detect test type
        test_type = args.test_type
        if test_type == "auto":
            # WHY: Proportion test if values are single number (success count)
            if len(control["values"]) == 1 and len(treatment["values"]) == 1:
                test_type = "proportion"
            else:
                # WHY: Mean test if values are list of observations
                test_type = "mean"

        # WHY: Run appropriate test
        if test_type == "proportion":
            results = calc.run_proportion_test(control, treatment)
        else:
            results = calc.run_mean_test(control, treatment)

        # WHY: Save results if output path specified
        if args.output:
            # WHY: Use atomic write for safe file operations
            atomic_write_json(results, Path(args.output), indent=2)
        else:
            # WHY: Print to stdout if no output file
            print(json.dumps(results, indent=2))

        # WHY: Show interpretation if verbose
        if args.verbose:
            print("\n" + calc.interpret_results())

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required field in JSON - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
