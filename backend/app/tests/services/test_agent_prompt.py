"""Unit tests for prompt editor agent_prompt helpers."""

from app.services.llm import LLMToolCall
from app.services.prompt_editor.agent_prompt import (
    add_line_numbers,
    apply_edits_progressively,
    apply_edits_to_prompt,
    get_prompt_line_count,
    parse_edit_prompt_tool_calls,
    validate_edits_against_line_count,
)


def test_add_line_numbers_empty() -> None:
    assert add_line_numbers("") == "1 | "


def test_add_line_numbers_multiline() -> None:
    assert add_line_numbers("a\nb") == "1 | a\n2 | b"


def test_get_prompt_line_count() -> None:
    assert get_prompt_line_count("") == 1
    assert get_prompt_line_count("one") == 1
    assert get_prompt_line_count("one\ntwo") == 2


def test_apply_edits_single_replace() -> None:
    p = "line1\nline2\nline3"
    out = apply_edits_to_prompt(p, [(2, 2, "NEW")])
    assert out == "line1\nNEW\nline3"


def test_apply_edits_multi_bottom_up() -> None:
    p = "a\nb\nc\nd"
    out = apply_edits_to_prompt(
        p,
        [
            (1, 1, "A2"),
            (3, 3, "C2"),
        ],
    )
    assert out == "A2\nb\nC2\nd"


def test_apply_edits_progressive() -> None:
    p = "a\nb\nc"
    edits = [(2, 2, "B2"), (1, 1, "A2")]
    snaps = apply_edits_progressively(p, edits)
    assert len(snaps) == 2
    assert snaps[0] == "A2\nb\nc"
    assert snaps[1] == "A2\nB2\nc"


def test_apply_edits_insert_after() -> None:
    p = "a\nb"
    out = apply_edits_to_prompt(p, [(2, 1, "inserted")])
    assert out == "a\nb\ninserted"


def test_parse_edit_prompt_tool_calls() -> None:
    calls = [
        LLMToolCall(
            id="1",
            function_name="edit_prompt",
            arguments={"start_line": 1, "end_line": 1, "new_content": "x"},
        ),
        LLMToolCall(id="2", function_name="other", arguments={}),
    ]
    edits = parse_edit_prompt_tool_calls(calls)
    assert edits == [(1, 1, "x")]


def test_validate_edits_against_line_count() -> None:
    p_lines = 3
    raw = [(1, 3, "ok"), (0, 1, "bad"), (5, 5, "bad2")]
    v = validate_edits_against_line_count(raw, p_lines)
    assert v == [(1, 3, "ok")]
