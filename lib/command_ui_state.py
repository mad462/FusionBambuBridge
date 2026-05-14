"""Pure-Python helpers for Fusion command UI labels and placement decisions."""

from __future__ import annotations

from html import escape


def choose_toolbar_panel_id(
    available_panel_ids: list[str],
    preferred_panel_ids: list[str],
) -> str | None:
    """Return the first preferred panel id that exists in the workspace."""
    available = set(available_panel_ids)
    for panel_id in preferred_panel_ids:
        if panel_id in available:
            return panel_id
    return None


def build_selection_label(selection_count: int) -> str:
    """Return a compact summary of the current command selection."""
    if selection_count <= 0:
        return "\u672a\u9009\u62e9\u5bf9\u8c61"
    if selection_count == 1:
        return "1 \u4e2a\u5bf9\u8c61\u5df2\u9009\u5b9a"
    return f"{selection_count} \u4e2a\u5bf9\u8c61\u5df2\u9009\u5b9a"


def build_command_summary_html(selection_count: int) -> str:
    """Build a compact summary section for the command dialog."""
    selection_label = build_selection_label(selection_count)
    return f"<div><b>\u5bf9\u8c61</b>: {escape(selection_label)}</div>"
