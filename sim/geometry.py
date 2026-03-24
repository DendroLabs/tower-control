"""Geographic and vector math for ATC simulation.

Pure functions using standard library math. No external dependencies.
All distances in nautical miles, bearings in degrees, altitudes in feet.
"""

from __future__ import annotations

import math
from sim.types import LatLonAlt, Vector3D

# Constants
_NM_PER_DEG_LAT = 60.0  # 1 degree latitude ~ 60 nm
_EARTH_RADIUS_NM = 3440.065


def _deg2rad(d: float) -> float:
    return d * math.pi / 180.0


def _rad2deg(r: float) -> float:
    return r * 180.0 / math.pi


def distance_nm(a: LatLonAlt, b: LatLonAlt) -> float:
    """Haversine distance in nautical miles (horizontal only)."""
    lat1, lat2 = _deg2rad(a.latitude), _deg2rad(b.latitude)
    dlat = lat2 - lat1
    dlon = _deg2rad(b.longitude - a.longitude)
    h = (math.sin(dlat / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
    return 2 * _EARTH_RADIUS_NM * math.asin(math.sqrt(h))


def distance_3d_nm(a: LatLonAlt, b: LatLonAlt) -> float:
    """3D distance in nautical miles (horizontal + vertical)."""
    horiz = distance_nm(a, b)
    vert_nm = abs(a.altitude_ft - b.altitude_ft) / 6076.12  # ft to nm
    return math.sqrt(horiz ** 2 + vert_nm ** 2)


def bearing_deg(a: LatLonAlt, b: LatLonAlt) -> float:
    """True bearing from a to b in degrees [0, 360)."""
    lat1, lat2 = _deg2rad(a.latitude), _deg2rad(b.latitude)
    dlon = _deg2rad(b.longitude - a.longitude)
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    brg = _rad2deg(math.atan2(x, y))
    return brg % 360.0


def project_position(pos: LatLonAlt, vel: Vector3D, dt_sec: float) -> LatLonAlt:
    """Linear projection of position given velocity and time delta."""
    if dt_sec <= 0 or vel.ground_speed_kts == 0:
        alt = pos.altitude_ft + vel.vertical_rate_fpm * (dt_sec / 60.0)
        return LatLonAlt(pos.latitude, pos.longitude, alt)

    dist_nm = vel.ground_speed_kts * (dt_sec / 3600.0)
    hdg_rad = _deg2rad(vel.heading_deg)

    dlat_deg = (dist_nm * math.cos(hdg_rad)) / _NM_PER_DEG_LAT
    nm_per_deg_lon = _NM_PER_DEG_LAT * math.cos(_deg2rad(pos.latitude))
    dlon_deg = (dist_nm * math.sin(hdg_rad)) / nm_per_deg_lon if nm_per_deg_lon > 0.001 else 0.0

    new_alt = pos.altitude_ft + vel.vertical_rate_fpm * (dt_sec / 60.0)

    return LatLonAlt(
        pos.latitude + dlat_deg,
        pos.longitude + dlon_deg,
        new_alt,
    )


def closure_rate_kts(
    pos_a: LatLonAlt, vel_a: Vector3D,
    pos_b: LatLonAlt, vel_b: Vector3D,
) -> float:
    """Rate at which two entities approach each other (positive = closing)."""
    d_now = distance_nm(pos_a, pos_b)
    dt = 1.0  # 1-second projection
    pos_a2 = project_position(pos_a, vel_a, dt)
    pos_b2 = project_position(pos_b, vel_b, dt)
    d_next = distance_nm(pos_a2, pos_b2)
    # Convert nm/sec to kts (1 kt = 1 nm/hr)
    return (d_now - d_next) * 3600.0


def time_to_cpa(
    pos_a: LatLonAlt, vel_a: Vector3D,
    pos_b: LatLonAlt, vel_b: Vector3D,
    max_horizon_sec: float = 300.0,
    step_sec: float = 1.0,
) -> tuple[float, float]:
    """Time to Closest Point of Approach and CPA distance.

    Returns (time_sec, cpa_distance_nm). Uses iterative projection
    for simplicity (adequate for terminal-area distances).
    """
    min_dist = distance_nm(pos_a, pos_b)
    min_time = 0.0

    t = step_sec
    while t <= max_horizon_sec:
        pa = project_position(pos_a, vel_a, t)
        pb = project_position(pos_b, vel_b, t)
        d = distance_nm(pa, pb)
        if d < min_dist:
            min_dist = d
            min_time = t
        elif d > min_dist * 1.5 and min_time > 0:
            # Diverging significantly past CPA — stop early
            break
        t += step_sec

    return min_time, min_dist


def is_within_airspace(
    pos: LatLonAlt,
    center: LatLonAlt,
    radius_nm: float,
    floor_ft: float,
    ceiling_ft: float,
) -> bool:
    """Check if a position is within a cylindrical airspace volume."""
    horiz = distance_nm(pos, center)
    return (horiz <= radius_nm
            and pos.altitude_ft >= floor_ft
            and pos.altitude_ft <= ceiling_ft)


def distance_to_runway_threshold(
    pos: LatLonAlt,
    threshold: LatLonAlt,
    runway_heading: float,
) -> float:
    """Distance along the extended runway centerline to threshold, in nm.

    Positive = before threshold (on approach). Negative = past threshold.
    """
    d = distance_nm(pos, threshold)
    brg = bearing_deg(threshold, pos)
    # Angle between the bearing from threshold to aircraft and the
    # reciprocal of the runway heading (approach direction)
    approach_heading = (runway_heading + 180.0) % 360.0
    angle_diff = brg - approach_heading
    # Along-track component
    return d * math.cos(_deg2rad(angle_diff))
