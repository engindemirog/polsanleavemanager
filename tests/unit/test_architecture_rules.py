"""AC-10: each boundary rule catches its violation and lets legitimate imports through."""

import grimp

from tests.architecture_rules import (
    Violation,
    cross_module_internal_imports,
    domain_framework_imports,
    shared_imports_module,
)


def _graph(*imports: tuple[str, str]) -> grimp.ImportGraph:
    graph = grimp.ImportGraph()
    for importer, imported in imports:
        for module in (importer, imported):
            if module not in graph.modules:
                graph.add_module(module)
        graph.add_import(importer=importer, imported=imported)
    return graph


def test_cross_module_import_of_internal_package_is_a_violation() -> None:
    graph = _graph(("app.modules.leave.service", "app.modules.balances.repository"))

    assert cross_module_internal_imports(graph) == [
        Violation(
            "cross-module-internal",
            "app.modules.leave.service",
            "app.modules.balances.repository",
        )
    ]


def test_cross_module_import_of_package_root_is_a_violation() -> None:
    graph = _graph(("app.modules.leave.service", "app.modules.balances"))

    assert len(cross_module_internal_imports(graph)) == 1


def test_cross_module_import_of_public_facade_is_allowed() -> None:
    graph = _graph(("app.modules.leave.service", "app.modules.balances.public"))

    assert cross_module_internal_imports(graph) == []


def test_import_within_the_same_module_is_allowed() -> None:
    graph = _graph(("app.modules.leave.service", "app.modules.leave.repository"))

    assert cross_module_internal_imports(graph) == []


def test_domain_importing_framework_package_is_a_violation() -> None:
    graph = _graph(
        ("app.modules.leave.domain.rules", "fastapi"),
        ("app.modules.leave.domain", "sqlalchemy.orm"),
        ("app.modules.leave.domain.rules", "starlette"),
        ("app.modules.leave.domain.rules", "httpx"),
    )

    assert {v.imported for v in domain_framework_imports(graph)} == {
        "fastapi",
        "sqlalchemy.orm",
        "starlette",
        "httpx",
    }


def test_non_domain_layer_may_import_framework_packages() -> None:
    graph = _graph(
        ("app.modules.leave.api", "fastapi"),
        ("app.modules.leave.repository", "sqlalchemy"),
    )

    assert domain_framework_imports(graph) == []


def test_domain_importing_standard_library_is_allowed() -> None:
    graph = _graph(("app.modules.leave.domain.rules", "decimal"))

    assert domain_framework_imports(graph) == []


def test_shared_importing_a_module_is_a_violation() -> None:
    graph = _graph(("app.shared.errors", "app.modules.leave.public"))

    assert shared_imports_module(graph) == [
        Violation("shared-imports-module", "app.shared.errors", "app.modules.leave.public")
    ]


def test_module_importing_shared_is_allowed() -> None:
    graph = _graph(("app.modules.leave.domain.rules", "app.shared.errors"))

    assert shared_imports_module(graph) == []
