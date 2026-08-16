"""Unit tests for router prompt construction."""

from app.router.prompts import build_router_system_prompt, build_router_user_prompt


def test_user_prompt_includes_optional_context_when_provided() -> None:
    prompt = build_router_user_prompt(
        "I paid yesterday but course is not active",
        user_type="student",
        student_id="stu_A",
        conversation_turn=1,
    )

    assert "I paid yesterday but course is not active" in prompt
    assert "user_type: student" in prompt
    assert "student_id: stu_A" in prompt
    assert "conversation_turn: 1" in prompt


def test_user_prompt_omits_context_when_not_provided() -> None:
    prompt = build_router_user_prompt("Can I get a refund?")

    assert "Can I get a refund?" in prompt
    assert "Context:" not in prompt


def test_system_prompt_lists_all_intents() -> None:
    prompt = build_router_system_prompt()

    assert "refund" in prompt
    assert "human_support" in prompt
    assert "unknown" in prompt
