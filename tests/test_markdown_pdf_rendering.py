from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_playtest_docs",
    ROOT / "scripts" / "generate_playtest_docs.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_inline_markdown_is_converted_to_reportlab_tags():
    rendered = MOD.inline_markdown("Detta är **viktigt**, *kursivt* och `kod`.")
    assert "<b>viktigt</b>" in rendered
    assert "<i>kursivt</i>" in rendered
    assert '<font name="Courier">kod</font>' in rendered
    assert "**" not in rendered
