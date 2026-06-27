from packages.eval_observatory.metrics import compute_metrics


def test_compute_metrics():
    metrics = compute_metrics(
        [
            {
                "passed": True,
                "total_steps": 3,
                "failure_label": "passed",
                "estimated_cost_usd": 0.1,
                "agent_type": "rule",
                "tags": ["adversarial", "risk:prompt_injection"],
            },
            {
                "passed": False,
                "total_steps": 5,
                "failure_label": "wrong_target",
                "estimated_cost_usd": 0.2,
                "agent_type": "llm",
                "tags": ["adversarial", "risk:wrong_target_click"],
            },
        ]
    )
    assert metrics["total"] == 2
    assert metrics["passed"] == 1
    assert metrics["success_rate"] == 0.5
    assert metrics["failure_counts"]["wrong_target"] == 1
    assert metrics["risk_counts"]["prompt_injection"] == 1
    assert metrics["agent_counts"]["rule"] == 1
