from packages.agents.context_policy import build_context


def test_recent_steps_context():
    history = [
        {"step_index": 0, "action": {"type": "goto"}, "result": {"ok": True}, "observation": {"url": "a"}},
        {"step_index": 1, "action": {"type": "click"}, "result": {"ok": False, "error_type": "wrong_target"}, "observation": {"url": "b"}},
    ]
    packet = build_context("recent_steps", "do task", history, recent_n=1)
    assert packet.source_step_count == 2
    assert "wrong_target" in packet.content

