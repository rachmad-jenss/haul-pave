"""Unit tests for vehicle_registry."""

from __future__ import annotations

from haulpave.vehicle_registry import VehicleEntry, find_by_id, list_all


class TestListAll:
    def test_returns_four_vehicles(self) -> None:
        vehicles = list_all()
        assert len(vehicles) == 4

    def test_all_are_vehicle_entries(self) -> None:
        for v in list_all():
            assert isinstance(v, VehicleEntry)

    def test_expected_ids_present(self) -> None:
        ids = {v.id for v in list_all()}
        assert {"cat-797f", "cat-789d", "kom-960e", "cat-785d"} == ids

    def test_gvw_positive(self) -> None:
        for v in list_all():
            assert v.gvw_kn > 0, f"{v.id} gvw_kn must be positive"

    def test_axles_is_two(self) -> None:
        for v in list_all():
            assert v.axles == 2

    def test_vehicle_has_two_axle_groups(self) -> None:
        for v in list_all():
            assert len(v.vehicle.axle_groups) == 2, f"{v.id} must have 2 axle groups"

    def test_front_plus_rear_equals_gvw(self) -> None:
        """25/75 split must sum to gvw_kn within 1 kN rounding tolerance."""
        for entry in list_all():
            total = sum(ag.gross_load_kn for ag in entry.vehicle.axle_groups)
            assert abs(total - entry.gvw_kn) < 1.0, (
                f"{entry.id}: axle loads sum {total:.1f} != gvw_kn {entry.gvw_kn:.1f}"
            )

    def test_cat_797f_heaviest(self) -> None:
        by_id = {v.id: v for v in list_all()}
        assert by_id["cat-797f"].gvw_kn > by_id["cat-785d"].gvw_kn


class TestFindById:
    def test_known_id_returns_entry(self) -> None:
        entry = find_by_id("cat-797f")
        assert entry is not None
        assert entry.id == "cat-797f"

    def test_unknown_id_returns_none(self) -> None:
        assert find_by_id("nonexistent-truck") is None

    def test_all_ids_findable(self) -> None:
        for v in list_all():
            found = find_by_id(v.id)
            assert found is not None
            assert found.id == v.id
