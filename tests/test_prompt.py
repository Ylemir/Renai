from renai.prompt import SYSTEM_PROMPT, USER_PROMPT


def test_system_prompt_not_empty():
    """Test that SYSTEM_PROMPT is defined and not empty."""
    assert SYSTEM_PROMPT
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT.strip()) > 0


def test_user_prompt_not_empty():
    """Test that USER_PROMPT is defined and not empty."""
    assert USER_PROMPT
    assert isinstance(USER_PROMPT, str)
    assert len(USER_PROMPT.strip()) > 0


def test_system_prompt_contains_rules():
    """Test that SYSTEM_PROMPT contains expected naming rules."""
    assert "文件名" in SYSTEM_PROMPT or "filename" in SYSTEM_PROMPT.lower()


def test_user_prompt_asks_for_filename():
    """Test that USER_PROMPT asks for filename generation."""
    assert "文件名" in USER_PROMPT or "filename" in USER_PROMPT.lower()
