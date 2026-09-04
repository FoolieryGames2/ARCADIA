from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from arcadia.aa_runtime import (
    CONTEXT_PROJECTION_VERSION,
    CandidateFailure,
    ContextProjectionError,
    ProjectionCandidate,
    ProjectionStanding,
    project_aae_context,
)
from arcadia.contracts.aae.registry import AAE_REGISTRY_PRE_V1, get_contract
from arcadia.contracts.schemas.r0.scope_proposal import (
    SCOPE_PROPOSAL_INPUT_SCHEMA,
    SCOPE_PROPOSAL_OUTPUT_SCHEMA,
)
from arcadia.contracts.schemas.r0.scope_validation import (
    SCOPE_VALIDATION_INPUT_SCHEMA,
    SCOPE_VALIDATION_OUTPUT_SCHEMA,
)
from arcadia.core.canonical_json import JsonValue, strict_json_loads
from arcadia.core.hashing import sha256_canonical_json
from arcadia.settings import (
    BudgetClass,
    ResolvedTuningProfile,
    SettingsSnapshot,
    SettingsStatus,
    TuningLimits,
    load_aae_settings,
)

ROOT = Path(__file__).resolve().parents[3]


def _call_data(prompt: str) -> dict[str, JsonValue]:
    return {
        "conversation_uuid": "CONV-001",
        "current_transcript_metadata": {
            "completed_exchange_count": 10,
            "continuation_state": {
                "reason_code": None,
                "source_turn_uuid": None,
                "status": "NONE",
            },
            "transcript_commit_seq": 10,
        },
        "host_policy_limits": {
            "max_contiguous_lookback_exchanges": 20,
            "max_scope_expansion_cycles": 3,
            "max_targeted_candidate_turns_per_search": 8,
            "max_total_injected_history_tokens": 4096,
        },
        "mode": "SCOPE_PROPOSAL",
        "raw_user_prompt": prompt,
        "turn_uuid": "TURN-S1",
    }


def _settings(
    *,
    profile_id: str = "settings.scope_proposal.pre1",
    specialist_mode_id: str = "SCOPE_PROPOSAL",
    **overrides: int | None,
) -> SettingsSnapshot:
    values: dict[str, int | None] = {
        "context_headroom_tokens": 64,
        "max_array_items": 64,
        "max_input_tokens": 900,
        "max_nesting_depth": 5,
        "max_output_tokens": 100,
        "max_repair_attempts": 1,
        "max_source_excerpt_chars": 1000,
        "max_string_chars": 1000,
    }
    values.update(overrides)
    resolved = ResolvedTuningProfile(
        settings_id="TEST-SETTINGS",
        settings_status=SettingsStatus.PRE_VERSION,
        profile_id=profile_id,
        specialist_mode_id=specialist_mode_id,
        budget_class=BudgetClass.SMALL,
        limits=TuningLimits(**values),
    )
    return SettingsSnapshot(
        resolved=resolved,
        settings_hash=sha256_canonical_json(resolved.to_value()),
    )


def _candidate(candidate_id: str, rank: int, prompt: str) -> ProjectionCandidate:
    return ProjectionCandidate(
        candidate_id=candidate_id,
        policy_id="projection.scope_proposal.pre1",
        rank=rank,
        data_plane=_call_data(prompt),
    )


def _project(
    candidates: tuple[ProjectionCandidate, ...],
    *,
    settings: SettingsSnapshot | None = None,
    context_window_tokens: int = 1200,
    token_counts: dict[str, int] | None = None,
):
    counts = token_counts or {}

    def counter(messages) -> int:
        return counts.get(messages[1].content, 100)

    return project_aae_context(
        get_contract("SCOPE_PROPOSAL"),
        candidates=candidates,
        input_schema=SCOPE_PROPOSAL_INPUT_SCHEMA,
        output_schema=SCOPE_PROPOSAL_OUTPUT_SCHEMA,
        settings=settings or _settings(max_input_tokens=10_000),
        context_window_tokens=context_window_tokens,
        count_tokens=counter,
    )


def test_first_whole_candidate_that_fits_is_selected_without_mutation() -> None:
    full = _candidate("FULL", 0, "x" * 200)
    reduced = replace(
        _candidate("REDUCED", 1, "minimum sufficient"),
        omitted_item_refs=("OPTIONAL_HISTORY_1",),
    )
    original_full = full.data_plane.copy()

    # Count by the complete canonical user message, not an estimated character ratio.
    probe_full = _project((full,), settings=_settings(max_input_tokens=10_000))
    assert probe_full.selected_call is not None
    full_message = probe_full.selected_call.messages[1].content
    probe_reduced = _project(
        (replace(reduced, rank=0),), settings=_settings(max_input_tokens=10_000)
    )
    assert probe_reduced.selected_call is not None
    reduced_message = probe_reduced.selected_call.messages[1].content
    result = _project(
        (reduced, full),
        settings=_settings(max_input_tokens=200),
        token_counts={full_message: 201, reduced_message: 150},
    )

    assert result.standing is ProjectionStanding.SELECTED
    assert result.dispatchable is True
    assert result.evidence.selected_candidate_id == "REDUCED"
    assert result.selected_call is not None
    assert result.selected_call.call.data_plane == reduced.data_plane
    assert full.data_plane == original_full
    assert result.evidence.evaluations[0].failures == (CandidateFailure.MAX_INPUT_TOKENS,)
    assert result.evidence.evaluations[1].fits is True
    assert result.evidence_hash.value.startswith("sha256:")


def test_no_candidate_fit_returns_explicit_exhaustion_without_dispatchable_call() -> None:
    result = _project(
        (_candidate("FULL", 0, "still complete"),),
        settings=_settings(max_input_tokens=10),
    )

    assert result.standing is ProjectionStanding.BUDGET_EXHAUSTED
    assert result.dispatchable is False
    assert result.selected_call is None
    assert CandidateFailure.MAX_INPUT_TOKENS in result.evidence.evaluations[0].failures


def test_context_window_reserves_output_and_headroom() -> None:
    candidate = _candidate("FULL", 0, "complete")
    probe = _project((candidate,), settings=_settings(max_input_tokens=10_000))
    assert probe.selected_call is not None
    message = probe.selected_call.messages[1].content
    result = _project(
        (candidate,),
        settings=_settings(max_input_tokens=500, max_output_tokens=100, context_headroom_tokens=50),
        context_window_tokens=249,
        token_counts={message: 100},
    )

    assert result.standing is ProjectionStanding.BUDGET_EXHAUSTED
    assert result.evidence.evaluations[0].failures == (CandidateFailure.CONTEXT_WINDOW_TOKENS,)


def test_unresolved_settings_are_explicit_and_never_treated_as_unlimited() -> None:
    result = _project(
        (_candidate("FULL", 0, "complete"),),
        settings=_settings(max_input_tokens=None),
    )

    assert result.standing is ProjectionStanding.SETTINGS_INCOMPLETE
    assert result.dispatchable is False
    assert result.evidence.missing_limit_names == ("max_input_tokens",)
    assert result.evidence.evaluations == ()


def test_checked_in_pre1_settings_fail_before_token_count_or_candidate_selection() -> None:
    settings = load_aae_settings(ROOT / "configs" / "aae_tuning.pre1.toml").snapshot(
        "settings.scope_proposal.pre1"
    )

    def forbidden_counter(_messages) -> int:
        raise AssertionError("incomplete settings reached the exact token counter")

    result = project_aae_context(
        get_contract("SCOPE_PROPOSAL"),
        candidates=(_candidate("FULL", 0, "complete"),),
        input_schema=SCOPE_PROPOSAL_INPUT_SCHEMA,
        output_schema=SCOPE_PROPOSAL_OUTPUT_SCHEMA,
        settings=settings,
        context_window_tokens=2048,
        count_tokens=forbidden_counter,
    )

    assert result.standing is ProjectionStanding.SETTINGS_INCOMPLETE
    assert set(result.evidence.missing_limit_names) == {
        "context_headroom_tokens",
        "max_input_tokens",
        "max_nesting_depth",
        "max_output_tokens",
        "max_source_excerpt_chars",
    }


@pytest.mark.parametrize(
    ("setting", "value", "failure"),
    [
        ("max_string_chars", 3, CandidateFailure.MAX_STRING_CHARS),
        ("max_nesting_depth", 2, CandidateFailure.MAX_NESTING_DEPTH),
        ("max_source_excerpt_chars", 3, CandidateFailure.MAX_SOURCE_EXCERPT_CHARS),
    ],
)
def test_structural_limits_fail_whole_candidate_instead_of_truncating(
    setting: str, value: int, failure: CandidateFailure
) -> None:
    candidate = _candidate("FULL", 0, "complete")
    if setting == "max_source_excerpt_chars":
        candidate = replace(candidate, source_excerpt_chars=(4,))
    result = _project(
        (candidate,),
        settings=_settings(max_input_tokens=10_000, **{setting: value}),
    )

    assert result.standing is ProjectionStanding.BUDGET_EXHAUSTED
    assert failure in result.evidence.evaluations[0].failures
    assert result.selected_call is None


def test_array_limit_rejects_complete_real_transcript_candidate_without_slicing() -> None:
    def turn(index: int) -> dict[str, JsonValue]:
        return {
            "final_response": f"response {index}",
            "final_response_hash": "sha256:" + f"{index + 10:064x}",
            "turn_index": index,
            "turn_uuid": f"TURN-{index}",
            "user_message": f"message {index}",
            "user_message_hash": "sha256:" + f"{index + 20:064x}",
        }

    data: dict[str, JsonValue] = {
        "conversation_uuid": "CONV-001",
        "frozen_retrieved_turns": [turn(1), turn(2)],
        "host_policy_limits": {
            "max_total_injected_history_tokens": 4096,
            "remaining_expansion_cycles": 1,
        },
        "mode": "SCOPE_VALIDATION",
        "raw_user_prompt": "What did I mean?",
        "turn_uuid": "TURN-CURRENT",
    }
    candidate = ProjectionCandidate(
        candidate_id="FULL",
        policy_id="projection.scope_validation.pre1",
        rank=0,
        data_plane=data,
    )
    result = project_aae_context(
        get_contract("SCOPE_VALIDATION"),
        candidates=(candidate,),
        input_schema=SCOPE_VALIDATION_INPUT_SCHEMA,
        output_schema=SCOPE_VALIDATION_OUTPUT_SCHEMA,
        settings=_settings(
            profile_id="settings.scope_validation.pre1",
            specialist_mode_id="SCOPE_VALIDATION",
            max_array_items=1,
            max_input_tokens=10_000,
        ),
        context_window_tokens=1200,
        count_tokens=lambda _messages: 100,
    )

    assert result.standing is ProjectionStanding.BUDGET_EXHAUSTED
    assert result.evidence.evaluations[0].failures == (CandidateFailure.MAX_ARRAY_ITEMS,)
    assert len(data["frozen_retrieved_turns"]) == 2


def test_candidate_policy_and_priority_are_fail_closed() -> None:
    wrong_policy = replace(_candidate("FULL", 0, "complete"), policy_id="projection.other")
    with pytest.raises(ContextProjectionError, match="policy"):
        _project((wrong_policy,))
    with pytest.raises(ContextProjectionError, match="contiguous"):
        _project((_candidate("FULL", 1, "complete"),))


def test_token_counter_must_return_exact_nonnegative_integer() -> None:
    with pytest.raises(ContextProjectionError, match="token counter"):
        project_aae_context(
            get_contract("SCOPE_PROPOSAL"),
            candidates=(_candidate("FULL", 0, "complete"),),
            input_schema=SCOPE_PROPOSAL_INPUT_SCHEMA,
            output_schema=SCOPE_PROPOSAL_OUTPUT_SCHEMA,
            settings=_settings(max_input_tokens=10_000),
            context_window_tokens=1200,
            count_tokens=lambda _messages: True,
        )


def test_projection_manifest_matches_all_registry_policy_identities() -> None:
    manifest = strict_json_loads(
        (ROOT / "manifests" / "aae_context_projection_pre1.json").read_text(encoding="utf-8")
    )
    assert type(manifest) is dict
    assert manifest["projection_algorithm_version"] == CONTEXT_PROJECTION_VERSION
    assert manifest["dispatch_enabled"] is False
    assert manifest["silent_truncation_forbidden"] is True
    assert manifest["modes"] == {
        mode: contract.context_projection_policy_id
        for mode, contract in sorted(AAE_REGISTRY_PRE_V1.items())
    }
