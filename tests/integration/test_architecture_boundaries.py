"""AC-10: the real application package respects every boundary rule."""

from tests.architecture_rules import all_violations, build_app_graph


def test_app_has_no_boundary_violations() -> None:
    assert all_violations(build_app_graph()) == []
