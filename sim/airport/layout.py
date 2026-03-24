"""Airport physical model — Section 28.1 Facility Reference Model.

Class C airport with parallel runways 10L/28R and 10R/28L,
taxiways A-E, and terminal ramp.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from sim.types import LatLonAlt


@dataclass
class Runway:
    id: str
    reciprocal: str
    heading: float  # magnetic heading in degrees
    threshold: LatLonAlt
    end: LatLonAlt
    length_ft: float = 8000.0
    width_ft: float = 150.0


@dataclass
class Taxiway:
    id: str
    waypoints: list[LatLonAlt] = field(default_factory=list)
    crosses_runways: list[str] = field(default_factory=list)


@dataclass
class HoldShortLine:
    taxiway: str
    runway: str  # the runway ID this hold-short protects
    position: LatLonAlt


@dataclass
class AirportLayout:
    name: str
    icao: str
    center: LatLonAlt
    elevation_ft: float
    runways: dict[str, Runway] = field(default_factory=dict)
    taxiways: dict[str, Taxiway] = field(default_factory=dict)
    hold_short_lines: list[HoldShortLine] = field(default_factory=list)

    # Maps each runway ID to its physical runway pair (both directions share one lock)
    physical_runways: dict[str, str] = field(default_factory=dict)

    def get_runway(self, runway_id: str) -> Runway:
        return self.runways[runway_id]

    def get_physical_runway_id(self, runway_id: str) -> str:
        return self.physical_runways.get(runway_id, runway_id)

    def get_hold_short_lines_for_runway(self, runway_id: str) -> list[HoldShortLine]:
        phys = self.get_physical_runway_id(runway_id)
        return [
            h for h in self.hold_short_lines
            if self.get_physical_runway_id(h.runway) == phys
        ]


def build_reference_airport() -> AirportLayout:
    """Construct the Class C reference facility from Section 28.1.

    Runways: 10L/28R, 10R/28L (parallel, ~4,300ft separation)
    Taxiways: A (parallel 10L/28R), B (parallel 10R/28L), C/D/E (cross-field)
    Ramp: Terminal between A and B

    Using a fictional airport loosely placed for coordinate convenience.
    Runway heading 100/280 degrees.
    """
    # Airport reference point
    center = LatLonAlt(35.0, -80.0, 650.0)

    # Runway geometry: heading 100 degrees, ~8000ft long
    # 10L/28R is the north runway, 10R/28L is the south runway
    # 4,300ft separation ~ 0.012 degrees latitude

    # 10L threshold (west end of north runway)
    rwy_10l_threshold = LatLonAlt(35.006, -80.014, 650.0)
    rwy_10l_end = LatLonAlt(35.003, -79.986, 650.0)  # ~8000ft east

    # 28R threshold (east end of same physical runway)
    rwy_28r_threshold = LatLonAlt(35.003, -79.986, 650.0)
    rwy_28r_end = LatLonAlt(35.006, -80.014, 650.0)

    # 10R threshold (west end of south runway, ~4300ft south of 10L)
    rwy_10r_threshold = LatLonAlt(34.994, -80.014, 650.0)
    rwy_10r_end = LatLonAlt(34.991, -79.986, 650.0)

    # 28L threshold (east end of same physical runway)
    rwy_28l_threshold = LatLonAlt(34.991, -79.986, 650.0)
    rwy_28l_end = LatLonAlt(34.994, -80.014, 650.0)

    runways = {
        "10L": Runway("10L", "28R", 100.0, rwy_10l_threshold, rwy_10l_end),
        "28R": Runway("28R", "10L", 280.0, rwy_28r_threshold, rwy_28r_end),
        "10R": Runway("10R", "28L", 100.0, rwy_10r_threshold, rwy_10r_end),
        "28L": Runway("28L", "10R", 280.0, rwy_28l_threshold, rwy_28l_end),
    }

    # Physical runway mapping (both directions share one lock)
    physical_runways = {
        "10L": "10L/28R",
        "28R": "10L/28R",
        "10R": "10R/28L",
        "28L": "10R/28L",
    }

    # Taxiways
    # A: parallel to 10L/28R (north), B: parallel to 10R/28L (south)
    # C, D, E: cross-field connecting A and B (crossing both runways)
    ramp_center_lat = 35.000  # between the two runways

    taxiway_a = Taxiway("A", [
        LatLonAlt(35.007, -80.014, 650.0),
        LatLonAlt(35.007, -79.986, 650.0),
    ])
    taxiway_b = Taxiway("B", [
        LatLonAlt(34.993, -80.014, 650.0),
        LatLonAlt(34.993, -79.986, 650.0),
    ])
    taxiway_c = Taxiway("C", [
        LatLonAlt(35.007, -80.008, 650.0),
        LatLonAlt(34.993, -80.008, 650.0),
    ], crosses_runways=["10L", "28R", "10R", "28L"])
    taxiway_d = Taxiway("D", [
        LatLonAlt(35.007, -80.000, 650.0),
        LatLonAlt(34.993, -80.000, 650.0),
    ], crosses_runways=["10L", "28R", "10R", "28L"])
    taxiway_e = Taxiway("E", [
        LatLonAlt(35.007, -79.992, 650.0),
        LatLonAlt(34.993, -79.992, 650.0),
    ], crosses_runways=["10L", "28R", "10R", "28L"])

    taxiways = {tw.id: tw for tw in [taxiway_a, taxiway_b, taxiway_c, taxiway_d, taxiway_e]}

    # Hold-short lines: where cross-field taxiways meet each runway
    hold_short_lines = [
        # Taxiway C crossing 10L/28R (north runway)
        HoldShortLine("C", "10L", LatLonAlt(35.0055, -80.008, 650.0)),
        # Taxiway C crossing 10R/28L (south runway)
        HoldShortLine("C", "10R", LatLonAlt(34.9945, -80.008, 650.0)),
        # Taxiway D crossing 10L/28R
        HoldShortLine("D", "10L", LatLonAlt(35.0055, -80.000, 650.0)),
        # Taxiway D crossing 10R/28L
        HoldShortLine("D", "10R", LatLonAlt(34.9945, -80.000, 650.0)),
        # Taxiway E crossing 10L/28R
        HoldShortLine("E", "10L", LatLonAlt(35.0055, -79.992, 650.0)),
        # Taxiway E crossing 10R/28L
        HoldShortLine("E", "10R", LatLonAlt(34.9945, -79.992, 650.0)),
    ]

    return AirportLayout(
        name="Reference Class C",
        icao="KREF",
        center=center,
        elevation_ft=650.0,
        runways=runways,
        taxiways=taxiways,
        hold_short_lines=hold_short_lines,
        physical_runways=physical_runways,
    )
