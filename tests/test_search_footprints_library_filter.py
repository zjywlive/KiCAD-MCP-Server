"""search_footprints with a library filter must scan that library, not filter a
capped all-library result (which dropped matches from late table rows)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))
from commands.library import LibraryCommands, LibraryManager  # noqa: E402


def _manager(tmp_path: Path, n_early: int) -> LibraryManager:
    mgr = LibraryManager.__new__(LibraryManager)
    mgr.project_path = None
    mgr.footprint_cache = {}
    mgr.libraries = {}
    # Many early libraries full of matches, the target library last.
    for i in range(n_early):
        lib = tmp_path / f"Stock{i}.pretty"
        lib.mkdir()
        for j in range(5):
            (lib / f"QFN-16_stock{i}_{j}.kicad_mod").write_text("(footprint)")
        mgr.libraries[f"Stock{i}"] = str(lib)
    jlc = tmp_path / "JLC.pretty"
    jlc.mkdir()
    (jlc / "QFN-16_L3.0-W3.0-P0.50-BL-EP1.7.kicad_mod").write_text("(footprint)")
    mgr.libraries["JLC"] = str(jlc)
    return mgr


def test_library_filter_finds_match_in_last_library(tmp_path):
    cmds = LibraryCommands(_manager(tmp_path, n_early=50))
    result = cmds.search_footprints({"search_term": "QFN-16", "library": "JLC", "limit": 5})
    assert result["success"]
    assert [r["full_name"] for r in result["footprints"]] == [
        "JLC:QFN-16_L3.0-W3.0-P0.50-BL-EP1.7"
    ]


def test_library_filter_is_case_insensitive(tmp_path):
    cmds = LibraryCommands(_manager(tmp_path, n_early=2))
    result = cmds.search_footprints({"search_term": "QFN-16", "library": "jlc"})
    assert result["count"] == 1


def test_no_filter_still_searches_all_libraries(tmp_path):
    cmds = LibraryCommands(_manager(tmp_path, n_early=2))
    result = cmds.search_footprints({"search_term": "QFN-16", "limit": 100})
    assert result["count"] == 11
