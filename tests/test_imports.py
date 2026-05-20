"""Smoke tests: verify the package is importable and version is set."""


def test_package_importable() -> None:
    import haulpave  # noqa: F401


def test_version_is_set() -> None:
    import haulpave

    assert isinstance(haulpave.__version__, str)
    assert len(haulpave.__version__) > 0


def test_subpackages_importable() -> None:
    import haulpave.analysis  # noqa: F401
    import haulpave.design  # noqa: F401
    import haulpave.economics  # noqa: F401
    import haulpave.material_library  # noqa: F401
    import haulpave.models  # noqa: F401
    import haulpave.reporting  # noqa: F401
    import haulpave.traffic  # noqa: F401
    import haulpave.utils  # noqa: F401
    import haulpave.vehicle_registry  # noqa: F401
