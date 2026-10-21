"""Thin wrapper around the Claude API. Falls back to a stub in dry-run mode."""
import os


def ask(system: str, user: str, model: str, max_tokens: int = 3000, dry_run: bool = False) -> str:
    if dry_run or not os.environ.get("ANTHROPIC_API_KEY"):
        return f"[DRY RUN - no API call]\nSystem: {system[:80]}...\nInput chars: {len(user)}"
    import anthropic

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
