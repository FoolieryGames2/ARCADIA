"""Deterministic human-readable audit renderer for structured AAE calls."""

from __future__ import annotations

from arcadia.aa_runtime.serializer import SerializedAAECall


def render_aae_audit(prepared: SerializedAAECall) -> str:
    """Render the mandatory bracketed audit surface without creating a parser protocol."""

    call = prepared.call
    authority = call.authority_plane

    def lines(items: tuple[str, ...]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- none"

    specialist = "\n".join(
        (
            f"specialist: {authority.specialist}",
            f"recipe: {authority.recipe}",
            f"authority: {authority.authority_class}",
            "",
            "purpose:",
            authority.purpose,
            "",
            "input_origin:",
            authority.input_origin,
            "",
            "responsibilities:",
            lines(authority.responsibilities),
            "",
            "forbidden_responsibilities:",
            lines(authority.forbidden_responsibilities),
            "",
            "legal_authoritative_ref_namespaces:",
            lines(authority.legal_authoritative_ref_namespaces),
            "",
            "uncertainty_behavior:",
            authority.uncertainty_behavior,
        )
    )

    return "\n".join(
        (
            "<A.R.C.A.D.I.A_ADAPTER_CALL>",
            "",
            "[GLOBAL_AWARENESS]",
            authority.global_awareness,
            "",
            "[SPECIALIST_AWARENESS]",
            specialist,
            "",
            "[CALL_DATA]",
            prepared.canonical_call_data,
            "",
            "[RESPONSE_CONTRACT]",
            call.response_contract,
            "",
            "</A.R.C.A.D.I.A_ADAPTER_CALL>",
        )
    )
