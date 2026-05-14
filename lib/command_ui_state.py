"""Pure-Python helpers for Fusion command UI labels and placement decisions."""

from __future__ import annotations

from html import escape
from pathlib import Path


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


def build_runtime_details_html(bambu_path: Path | None, temp_dir: Path) -> str:
    """Build a small info block for the Fusion command dialog."""
    executable_text = (
        "\u81ea\u52a8\u68c0\u6d4b Bambu Studio" if bambu_path is None else str(bambu_path)
    )
    return (
        "<div><b>\u8f93\u51fa\u5e94\u7528\u7a0b\u5e8f</b>: Bambu Studio</div>"
        f"<div><b>\u53ef\u6267\u884c\u6587\u4ef6</b>: {escape(executable_text)}</div>"
        f"<div><b>\u4e34\u65f6\u5bfc\u51fa\u76ee\u5f55</b>: {escape(str(temp_dir))}</div>"
    )


def build_command_summary_html(selection_count: int, format_name: str) -> str:
    """Build a compact summary section for the command dialog."""
    selection_label = build_selection_label(selection_count)
    return (
        f"<div><b>\u5bf9\u8c61</b>: {escape(selection_label)}</div>"
        f"<div><b>\u683c\u5f0f</b>: {escape(format_name)}</div>"
    )
