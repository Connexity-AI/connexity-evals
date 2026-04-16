#!/usr/bin/env python3
"""End-to-end test for the Prompt Editor agent flow.

Simulates the full frontend workflow against a running backend:
  1. Login → create a platform agent → create a draft
  2. Create a prompt editor session (verifies base_prompt snapshot)
  3. Send chat messages via SSE and verify reasoning/edit/done events
  4. Verify that session.edited_prompt is updated in the DB after each turn
  5. Simulate a manual frontend edit and verify the agent sees the updated prompt
  6. Save the edited prompt via PUT /agents/{id}/draft
  7. Create a new session and verify it picks up the new draft prompt as base_prompt
  8. Multi-turn conversation: verify history accumulation and correct prompt versioning

Prerequisites:
  1. Backend running:  cd backend && uvicorn app.main:app --reload
  2. Database seeded:  cd backend && bash scripts/prestart.sh
  3. LLM keys configured in .env (OPENAI_API_KEY or ANTHROPIC_API_KEY)

Usage::

    cd backend && uv run python scripts/test_prompt_editor.py
    cd backend && uv run python scripts/test_prompt_editor.py --backend http://localhost:8000
"""

import argparse
import json
import sys
import time
import uuid
from typing import Any

import httpx
import httpx_sse

DEFAULT_BACKEND = "http://localhost:8000"
API_PREFIX = "/api/v1"

INITIAL_SYSTEM_PROMPT = """\
You are a helpful customer support agent for TechCorp.

Your responsibilities:
- Answer product questions
- Help with order status
- Process returns and refunds
- Escalate complex issues to human agents

Always be polite, professional, and concise."""

PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"
INFO = "\033[94mℹ\033[0m"

checks_passed = 0
checks_failed = 0


def check(condition: bool, description: str, detail: str = "") -> bool:
    global checks_passed, checks_failed
    if condition:
        checks_passed += 1
        print(f"  {PASS}  {description}")
    else:
        checks_failed += 1
        msg = f"  {FAIL}  {description}"
        if detail:
            msg += f"  —  {detail}"
        print(msg)
    return condition


def _api(base: str, path: str) -> str:
    return f"{base}{API_PREFIX}{path}"


def login(client: httpx.Client, base: str, email: str, password: str) -> None:
    r = client.post(
        _api(base, "/login/access-token"),
        data={"username": email, "password": password},
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    client.cookies.set("auth_cookie", token)
    print(f"\n[auth] Logged in as {email}")


def create_platform_agent(client: httpx.Client, base: str) -> dict[str, Any]:
    """Create a platform-mode agent with a known system prompt."""
    name = f"PromptEditor Test Agent {uuid.uuid4().hex[:6]}"
    r = client.post(
        _api(base, "/agents/"),
        json={
            "name": name,
            "description": "Auto-created by test_prompt_editor.py",
            "mode": "platform",
            "system_prompt": INITIAL_SYSTEM_PROMPT,
            "agent_model": "gpt-4o-mini",
            "agent_provider": "openai",
        },
    )
    r.raise_for_status()
    agent = r.json()
    print(f"[setup] Created platform agent: {agent['name']} ({agent['id']})")
    return agent


def update_agent_draft(
    client: httpx.Client, base: str, agent_id: str, system_prompt: str
) -> dict[str, Any]:
    """PUT /agents/{id}/draft to save the edited prompt (simulates frontend save)."""
    r = client.put(
        _api(base, f"/agents/{agent_id}/draft"),
        json={"system_prompt": system_prompt},
    )
    r.raise_for_status()
    return r.json()


def get_agent_draft(client: httpx.Client, base: str, agent_id: str) -> dict[str, Any]:
    r = client.get(_api(base, f"/agents/{agent_id}/draft"))
    r.raise_for_status()
    return r.json()


def create_session(
    client: httpx.Client, base: str, agent_id: str, title: str | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"agent_id": agent_id}
    if title:
        payload["title"] = title
    r = client.post(_api(base, "/prompt-editor/sessions/"), json=payload)
    r.raise_for_status()
    return r.json()


def get_session(client: httpx.Client, base: str, session_id: str) -> dict[str, Any]:
    r = client.get(_api(base, f"/prompt-editor/sessions/{session_id}"))
    r.raise_for_status()
    return r.json()


def list_messages(client: httpx.Client, base: str, session_id: str) -> dict[str, Any]:
    r = client.get(_api(base, f"/prompt-editor/sessions/{session_id}/messages"))
    r.raise_for_status()
    return r.json()


def stream_chat(
    client: httpx.Client,
    base: str,
    session_id: str,
    content: str,
    current_prompt: str,
) -> dict[str, list[dict[str, Any]]]:
    """Send a chat message and collect all SSE events by type.

    Returns a dict mapping event type → list of parsed data dicts.
    """
    url = _api(base, f"/prompt-editor/sessions/{session_id}/messages")
    events: dict[str, list[dict[str, Any]]] = {
        "status": [],
        "reasoning": [],
        "edit": [],
        "done": [],
        "error": [],
    }

    with client.stream(
        "POST",
        url,
        json={
            "content": content,
            "current_prompt": current_prompt,
        },
        timeout=120.0,
    ) as response:
        response.raise_for_status()
        for sse in httpx_sse.EventSource(response).iter_sse():
            data = json.loads(sse.data) if sse.data else {}
            event_type = sse.event
            if event_type not in events:
                events[event_type] = []
            events[event_type].append(data)

    return events


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run_test_1_session_creation(
    client: httpx.Client, base: str, agent: dict[str, Any]
) -> dict[str, Any]:
    """Test 1: Session creation snapshots the correct base_prompt."""
    print_section("Test 1: Session Creation & base_prompt Snapshot")

    pe_session = create_session(client, base, agent["id"], title="E2E Test Session")
    print(f"  {INFO}  Created session: {pe_session['id']}")

    check(
        pe_session["base_prompt"] == INITIAL_SYSTEM_PROMPT,
        "base_prompt matches agent's system_prompt",
        f"Expected {len(INITIAL_SYSTEM_PROMPT)} chars, got {len(pe_session.get('base_prompt') or '')} chars",
    )
    check(
        pe_session["edited_prompt"] is None,
        "edited_prompt is None on fresh session",
    )
    check(
        pe_session["status"] == "active",
        "Session status is 'active'",
    )
    check(
        pe_session["message_count"] == 0,
        "message_count is 0 on fresh session",
    )

    return pe_session


def run_test_2_first_chat_turn(
    client: httpx.Client, base: str, pe_session: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    """Test 2: First chat turn — SSE events, reasoning, edits, done payload."""
    print_section("Test 2: First Chat Turn (SSE Stream)")

    session_id = pe_session["id"]
    current_prompt = pe_session["base_prompt"]

    print(f"  {INFO}  Sending: 'Make this prompt more structured with clear sections'")
    t0 = time.time()
    events = stream_chat(
        client,
        base,
        session_id,
        content="Make this prompt more structured with clear sections and headers",
        current_prompt=current_prompt,
    )
    elapsed = time.time() - t0
    print(f"  {INFO}  Stream completed in {elapsed:.1f}s")

    # SSE event structure checks
    check(
        len(events["error"]) == 0,
        "No error events",
        f"Errors: {events['error']}" if events["error"] else "",
    )

    status_phases = [s["phase"] for s in events["status"]]
    check(
        "analyzing" in status_phases,
        "Got status 'analyzing' event",
    )
    check(
        "complete" in status_phases,
        "Got status 'complete' event",
    )

    check(
        len(events["reasoning"]) > 0,
        f"Got {len(events['reasoning'])} reasoning chunks",
    )

    reasoning_text = "".join(r.get("content", "") for r in events["reasoning"])
    check(
        len(reasoning_text) > 20,
        f"Reasoning text is non-trivial ({len(reasoning_text)} chars)",
    )
    print(f"  {INFO}  Reasoning preview: {reasoning_text[:120]}...")

    has_edits = len(events["edit"]) > 0
    if has_edits:
        check(
            "editing" in status_phases,
            "Got status 'editing' event (edits were made)",
        )
        for i, edit_evt in enumerate(events["edit"]):
            check(
                "edited_prompt" in edit_evt,
                f"Edit event [{i}] has 'edited_prompt' field",
            )
            check(
                edit_evt.get("edit_index") == i,
                f"Edit event [{i}] has correct edit_index={i}",
            )
            check(
                edit_evt.get("total_edits") == len(events["edit"]),
                f"Edit event [{i}] total_edits={len(events['edit'])}",
            )
    else:
        print(f"  {INFO}  Agent gave conversational response (no edits) — still valid")

    # Done event checks
    check(len(events["done"]) == 1, "Exactly one 'done' event")
    if events["done"]:
        done = events["done"][0]
        check(
            "message" in done,
            "Done event contains 'message'",
        )
        check(
            "edited_prompt" in done,
            "Done event contains 'edited_prompt'",
        )
        check(
            "base_prompt" in done,
            "Done event contains 'base_prompt'",
        )
        check(
            done["base_prompt"] == INITIAL_SYSTEM_PROMPT,
            "Done event base_prompt matches original",
        )
        if has_edits:
            final_edited = events["edit"][-1]["edited_prompt"]
            check(
                done["edited_prompt"] == final_edited,
                "Done edited_prompt matches last edit snapshot",
            )
            check(
                done["edited_prompt"] != INITIAL_SYSTEM_PROMPT,
                "Edited prompt differs from original (edits applied)",
            )
        msg = done["message"]
        check(msg.get("role") == "assistant", "Assistant message role is 'assistant'")
        check(len(msg.get("content", "")) > 0, "Assistant message has content")

    return events


def run_test_3_session_state_after_turn(
    client: httpx.Client,
    base: str,
    session_id: str,
    events: dict[str, list[dict[str, Any]]],
) -> None:
    """Test 3: After first turn, verify DB state is consistent."""
    print_section("Test 3: Session & Message State After First Turn")

    refreshed = get_session(client, base, session_id)

    has_edits = len(events["edit"]) > 0
    if has_edits:
        done = events["done"][0]
        check(
            refreshed["edited_prompt"] == done["edited_prompt"],
            "Session edited_prompt matches done event",
        )
    else:
        check(
            refreshed["edited_prompt"] is not None,
            "Session edited_prompt is set (even without edits, persists current_prompt)",
        )

    check(
        refreshed["base_prompt"] == INITIAL_SYSTEM_PROMPT,
        "Session base_prompt unchanged after turn",
    )

    msgs = list_messages(client, base, session_id)
    check(msgs["count"] == 2, f"2 messages after first turn (got {msgs['count']})")
    if len(msgs["data"]) >= 1:
        check(
            msgs["data"][0]["role"] == "user",
            "First message is user",
        )
    if len(msgs["data"]) >= 2:
        check(
            msgs["data"][1]["role"] == "assistant",
            "Second message is assistant",
        )


def run_test_4_manual_edit_then_chat(
    client: httpx.Client,
    base: str,
    session_id: str,
    events_turn1: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    """Test 4: Simulate a manual frontend edit, then send another message.

    The frontend sends current_prompt with its local edits — the backend should
    use that as the context for the agent and persist it.
    """
    print_section("Test 4: Manual Edit + Second Chat Turn")

    done_turn1 = events_turn1["done"][0] if events_turn1["done"] else None
    prompt_after_turn1 = (
        done_turn1["edited_prompt"] if done_turn1 else INITIAL_SYSTEM_PROMPT
    )

    manual_addition = "\n\n# Additional Policy\nAlways ask for order number before processing any return."
    manually_edited_prompt = prompt_after_turn1 + manual_addition
    print(f"  {INFO}  Simulating manual edit: appended {len(manual_addition)} chars")

    print(f"  {INFO}  Sending: 'Add a greeting template section'")
    t0 = time.time()
    events_turn2 = stream_chat(
        client,
        base,
        session_id,
        content="Add a greeting template section that the agent should use when starting conversations",
        current_prompt=manually_edited_prompt,
    )
    elapsed = time.time() - t0
    print(f"  {INFO}  Stream completed in {elapsed:.1f}s")

    check(
        len(events_turn2["error"]) == 0,
        "No error events in turn 2",
        f"Errors: {events_turn2['error']}" if events_turn2["error"] else "",
    )
    check(
        len(events_turn2["done"]) == 1,
        "Got 'done' event in turn 2",
    )

    if events_turn2["done"]:
        done2 = events_turn2["done"][0]
        check(
            done2["base_prompt"] == INITIAL_SYSTEM_PROMPT,
            "base_prompt still matches original across turns",
        )

        if events_turn2["edit"]:
            check(
                manual_addition.strip() in done2["edited_prompt"]
                or "order number" in done2["edited_prompt"].lower(),
                "Manual edit content preserved in final prompt (or agent incorporated it)",
            )

    # Verify message count grew
    msgs = list_messages(client, base, session_id)
    check(msgs["count"] == 4, f"4 messages after two turns (got {msgs['count']})")

    # Verify session state
    refreshed = get_session(client, base, session_id)
    if events_turn2["done"]:
        check(
            refreshed["edited_prompt"] == events_turn2["done"][0]["edited_prompt"],
            "Session edited_prompt updated to turn 2 result",
        )

    return events_turn2


def run_test_5_save_to_draft(
    client: httpx.Client,
    base: str,
    agent_id: str,
    session_id: str,
) -> str:
    """Test 5: Save the edited prompt to the agent draft (simulates frontend 'Save')."""
    print_section("Test 5: Save Edited Prompt to Agent Draft")

    refreshed = get_session(client, base, session_id)
    edited_prompt = refreshed["edited_prompt"]

    if not edited_prompt:
        print(f"  {INFO}  No edited_prompt to save — skipping draft update")
        return INITIAL_SYSTEM_PROMPT

    draft = update_agent_draft(client, base, agent_id, edited_prompt)
    check(
        draft["system_prompt"] == edited_prompt,
        "Draft system_prompt matches saved edited_prompt",
    )

    fetched_draft = get_agent_draft(client, base, agent_id)
    check(
        fetched_draft["system_prompt"] == edited_prompt,
        "GET draft confirms system_prompt persisted",
    )

    print(f"  {INFO}  Saved {len(edited_prompt)} chars to agent draft")
    return edited_prompt


def run_test_6_new_session_picks_up_draft(
    client: httpx.Client,
    base: str,
    agent_id: str,
    saved_prompt: str,
) -> None:
    """Test 6: A new session should snapshot the draft's system_prompt as base_prompt."""
    print_section("Test 6: New Session Snapshots Updated Draft")

    new_session = create_session(
        client, base, agent_id, title="Session after draft update"
    )
    print(f"  {INFO}  Created new session: {new_session['id']}")

    check(
        new_session["base_prompt"] == saved_prompt,
        "New session base_prompt matches saved draft prompt",
        f"Expected {len(saved_prompt)} chars, got {len(new_session.get('base_prompt') or '')} chars",
    )
    check(
        new_session["edited_prompt"] is None,
        "New session edited_prompt is None",
    )


def run_test_7_multi_turn_history(
    client: httpx.Client, base: str, agent_id: str
) -> None:
    """Test 7: Multi-turn conversation to verify history accumulation."""
    print_section("Test 7: Multi-Turn History Accumulation")

    pe_session = create_session(client, base, agent_id, title="Multi-turn test")
    session_id = pe_session["id"]
    current_prompt = pe_session["base_prompt"] or INITIAL_SYSTEM_PROMPT
    print(f"  {INFO}  Session: {session_id}")

    turn_prompts: list[str] = [current_prompt]

    messages_sequence = [
        "Can you review my prompt and tell me what could be improved?",
        "Good points. Now please add error handling guidelines.",
        "Make the tone slightly more friendly and approachable.",
    ]

    for turn_num, msg in enumerate(messages_sequence, 1):
        print(f"\n  {INFO}  Turn {turn_num}: '{msg[:60]}...'")
        t0 = time.time()
        events = stream_chat(
            client, base, session_id, content=msg, current_prompt=current_prompt
        )
        elapsed = time.time() - t0
        print(f"  {INFO}  Completed in {elapsed:.1f}s")

        check(
            len(events["error"]) == 0,
            f"Turn {turn_num}: No errors",
            f"{events['error']}" if events["error"] else "",
        )
        check(
            len(events["done"]) == 1,
            f"Turn {turn_num}: Got done event",
        )

        if events["done"]:
            done = events["done"][0]
            current_prompt = done["edited_prompt"]
            turn_prompts.append(current_prompt)

            check(
                done["base_prompt"] == pe_session["base_prompt"],
                f"Turn {turn_num}: base_prompt stable",
            )

    # After all turns, verify message count
    msgs = list_messages(client, base, session_id)
    expected_count = len(messages_sequence) * 2
    check(
        msgs["count"] == expected_count,
        f"Total messages: {expected_count} (got {msgs['count']})",
    )

    # Verify roles alternate user/assistant
    roles = [m["role"] for m in msgs["data"]]
    expected_roles = ["user", "assistant"] * len(messages_sequence)
    check(
        roles == expected_roles,
        "Message roles alternate user/assistant correctly",
        f"Got: {roles}",
    )

    # Verify session state
    final_session = get_session(client, base, session_id)
    check(
        final_session["edited_prompt"] == current_prompt,
        "Final session edited_prompt matches last turn result",
    )

    print(f"\n  {INFO}  Prompt evolution across {len(turn_prompts)} states:")
    for i, p in enumerate(turn_prompts):
        label = "initial" if i == 0 else f"after turn {i}"
        print(f"         [{label}] {len(p)} chars")


def run_test_8_archived_session_rejected(
    client: httpx.Client, base: str, agent_id: str
) -> None:
    """Test 8: Archived sessions reject new messages."""
    print_section("Test 8: Archived Session Rejects Chat")

    pe_session = create_session(client, base, agent_id, title="Archive test")
    session_id = pe_session["id"]

    r = client.patch(
        _api(base, f"/prompt-editor/sessions/{session_id}"),
        json={"status": "archived"},
    )
    r.raise_for_status()
    check(r.json()["status"] == "archived", "Session archived successfully")

    r = client.post(
        _api(base, f"/prompt-editor/sessions/{session_id}/messages"),
        json={"content": "This should fail", "current_prompt": "test"},
        headers={"Accept": "text/event-stream"},
    )
    check(
        r.status_code == 400,
        f"Chat to archived session returns 400 (got {r.status_code})",
    )


def run_test_9_presets(client: httpx.Client, base: str) -> None:
    """Test 9: Presets endpoint returns data."""
    print_section("Test 9: Presets Endpoint")

    r = client.get(_api(base, "/prompt-editor/presets"))
    r.raise_for_status()
    presets = r.json()
    check(len(presets) > 0, f"Got {len(presets)} presets")
    if presets:
        check(
            all("id" in p and "label" in p and "message" in p for p in presets),
            "All presets have id, label, message fields",
        )


def run_test_10_session_listing(client: httpx.Client, base: str, agent_id: str) -> None:
    """Test 10: List sessions filtered by agent_id."""
    print_section("Test 10: Session Listing & Filtering")

    r = client.get(
        _api(base, "/prompt-editor/sessions/"),
        params={"agent_id": agent_id, "limit": 100},
    )
    r.raise_for_status()
    payload = r.json()
    check(
        payload["count"] >= 1, f"At least 1 session for agent (got {payload['count']})"
    )

    for s in payload["data"]:
        check(
            s["agent_id"] == agent_id,
            f"Session {s['id'][:8]}... belongs to correct agent",
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="End-to-end test for the Prompt Editor agent flow."
    )
    parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND,
        help=f"Backend base URL (default: {DEFAULT_BACKEND})",
    )
    parser.add_argument(
        "--email",
        default="admin@example.com",
        help="Login email (default: admin@example.com)",
    )
    parser.add_argument(
        "--password",
        default="password",
        help="Login password (default: password)",
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip tests that require real LLM calls (tests 2, 4, 7)",
    )
    args = parser.parse_args()

    print(f"[config] Backend: {args.backend}")
    print(f"[config] Skip LLM: {args.skip_llm}")

    with httpx.Client(timeout=30.0) as client:
        login(client, args.backend, args.email, args.password)
        agent = create_platform_agent(client, args.backend)
        agent_id = agent["id"]

        # Test 1: Session creation
        pe_session = run_test_1_session_creation(client, args.backend, agent)

        if not args.skip_llm:
            # Test 2: First chat turn with real LLM
            events_turn1 = run_test_2_first_chat_turn(client, args.backend, pe_session)

            # Only continue to dependent tests if turn 1 succeeded (got a done event)
            turn1_ok = len(events_turn1.get("done", [])) == 1

            # Test 3: Verify DB state after turn
            run_test_3_session_state_after_turn(
                client, args.backend, pe_session["id"], events_turn1
            )

            if turn1_ok:
                # Test 4: Manual edit + second turn
                run_test_4_manual_edit_then_chat(
                    client, args.backend, pe_session["id"], events_turn1
                )

                # Test 5: Save to draft
                saved_prompt = run_test_5_save_to_draft(
                    client, args.backend, agent_id, pe_session["id"]
                )

                # Test 6: New session picks up draft
                run_test_6_new_session_picks_up_draft(
                    client, args.backend, agent_id, saved_prompt
                )
            else:
                print(
                    f"\n  {INFO}  Skipping tests 4-6 (turn 1 did not complete successfully)"
                )

            # Test 7: Multi-turn history (independent session)
            run_test_7_multi_turn_history(client, args.backend, agent_id)
        else:
            print(f"\n  {INFO}  Skipping LLM tests (--skip-llm)")

        # Test 8: Archived session rejection (no LLM needed)
        run_test_8_archived_session_rejected(client, args.backend, agent_id)

        # Test 9: Presets
        run_test_9_presets(client, args.backend)

        # Test 10: Session listing
        run_test_10_session_listing(client, args.backend, agent_id)

    # Summary
    print(f"\n{'='*60}")
    print("  SUMMARY")
    print(f"{'='*60}")
    total = checks_passed + checks_failed
    print(f"  Passed: {checks_passed}/{total}")
    print(f"  Failed: {checks_failed}/{total}")
    if checks_failed:
        print(f"\n  {FAIL}  {checks_failed} check(s) failed")
        return 1
    print(f"\n  {PASS}  All checks passed!")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n[interrupted]")
        raise SystemExit(130) from None
    except httpx.HTTPStatusError as exc:
        print(
            f"\n[error] HTTP {exc.response.status_code}: {exc.response.text}",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
