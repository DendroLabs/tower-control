"""Class C airspace model and approach corridors — Section 28.1, 28.5.6.

Defines airspace boundaries, approach corridors, and the advisory/commitment
gate positions for the Approach Commitment Gate (ACG).
"""

from __future__ import annotations

from dataclasses import dataclass
from sim.types import LatLonAlt
from sim.geometry import distance_nm, distance_to_runway_threshold
from sim.airport.layout import AirportLayout, Runway


@dataclass
class AirspaceShelf:
    floor_ft: float
    ceiling_ft: float
    radius_nm: float


@dataclass
class ClassCAirspace:
    center: LatLonAlt
    inner_shelf: AirspaceShelf  # SFC-4000, 5nm
    outer_shelf: AirspaceShelf  # 1200-4000, 10nm

    def contains(self, pos: LatLonAlt) -> bool:
        d = distance_nm(pos, self.center)
        # Inner shelf: surface to ceiling, inner radius
        if (d <= self.inner_shelf.radius_nm
                and pos.altitude_ft >= self.inner_shelf.floor_ft
                and pos.altitude_ft <= self.inner_shelf.ceiling_ft):
            return True
        # Outer shelf: floor to ceiling, outer radius
        if (d <= self.outer_shelf.radius_nm
                and pos.altitude_ft >= self.outer_shelf.floor_ft
                and pos.altitude_ft <= self.outer_shelf.ceiling_ft):
            return True
        return False

    def shelf_for(self, pos: LatLonAlt) -> str | None:
        d = distance_nm(pos, self.center)
        if (d <= self.inner_shelf.radius_nm
                and pos.altitude_ft >= self.inner_shelf.floor_ft
                and pos.altitude_ft <= self.inner_shelf.ceiling_ft):
            return "inner"
        if (d <= self.outer_shelf.radius_nm
                and pos.altitude_ft >= self.outer_shelf.floor_ft
                and pos.altitude_ft <= self.outer_shelf.ceiling_ft):
            return "outer"
        return None


@dataclass
class ApproachCorridor:
    """Defines approach path and gate positions for a runway.

    Advisory gate (~5nm / FAF): early warning — XOFF signal.
    Commitment gate (~2nm): forcing function — no token = go-around.
    VFR commitment gate (~0.5nm): shorter for pattern traffic.
    """

    runway_id: str
    runway_heading: float
    threshold: LatLonAlt
    advisory_gate_nm: float = 5.0
    commitment_gate_nm: float = 2.0
    vfr_commitment_gate_nm: float = 0.5
    glideslope_deg: float = 3.0
    faf_nm: float = 5.0  # Final Approach Fix distance

    def distance_to_threshold(self, pos: LatLonAlt) -> float:
        """Distance along extended centerline to threshold, in nm."""
        return distance_to_runway_threshold(pos, self.threshold, self.runway_heading)

    def is_past_advisory_gate(self, pos: LatLonAlt) -> bool:
        """Has the aircraft passed the advisory gate (closer than advisory_gate_nm)?"""
        return self.distance_to_threshold(pos) <= self.advisory_gate_nm

    def is_past_commitment_gate(self, pos: LatLonAlt) -> bool:
        """Has the aircraft passed the commitment gate?"""
        return self.distance_to_threshold(pos) <= self.commitment_gate_nm

    def is_past_vfr_commitment_gate(self, pos: LatLonAlt) -> bool:
        return self.distance_to_threshold(pos) <= self.vfr_commitment_gate_nm


def build_approach_corridors(airport: AirportLayout) -> dict[str, ApproachCorridor]:
    """Build approach corridors for all runways in the airport layout."""
    corridors: dict[str, ApproachCorridor] = {}
    for rwy_id, rwy in airport.runways.items():
        corridors[rwy_id] = ApproachCorridor(
            runway_id=rwy_id,
            runway_heading=rwy.heading,
            threshold=rwy.threshold,
        )
    return corridors


def build_reference_airspace(airport: AirportLayout) -> ClassCAirspace:
    """Build Class C airspace for the reference airport."""
    return ClassCAirspace(
        center=airport.center,
        inner_shelf=AirspaceShelf(
            floor_ft=0.0,  # SFC
            ceiling_ft=4000.0 + airport.elevation_ft,
            radius_nm=5.0,
        ),
        outer_shelf=AirspaceShelf(
            floor_ft=1200.0 + airport.elevation_ft,
            ceiling_ft=4000.0 + airport.elevation_ft,
            radius_nm=10.0,
        ),
    )
