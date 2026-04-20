from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from dms2dec import dec2dms_func


# =========================
# ⚙️ CONFIGURATION
# =========================
MODE = "geo"  # options: "geo", "regions", "labels"

GEO_SELECTION = ["LFMD"]       # exact ICAO match
REGIONS_SELECTION = ["LFMD"]   # substring match unless REGIONS_EXACT_MATCH = True
LABELS_SELECTION = ["LFMD"]    # substring match unless LABELS_EXACT_MATCH = True

REGIONS_EXACT_MATCH = False
LABELS_EXACT_MATCH = False

DEBUG = False

SOURCE_DIR = Path("source")
OUTPUT_DIR = Path("output")

FIELD_ICAO = "icao"
FIELD_COLOR = "color"
FIELD_TEXT_LABEL = "text_label"


@dataclass
class ExportStats:
    target: str
    output_file: Path
    matches: int = 0
    edges: int = 0
    polygons: int = 0
    labels: int = 0
    skipped: int = 0


class Cli:
    @staticmethod
    def banner(mode: str, selections: Sequence[str], debug: bool) -> None:
        joined = ", ".join(selections) if selections else "(none)"
        print(f"\n🚀 Starting {mode.upper()} export")
        print(f"🎯 Targets: {joined}")
        print(f"🐞 Debug mode: {'ON' if debug else 'OFF'}")
        print("─" * 52)

    @staticmethod
    def info(message: str) -> None:
        print(f"ℹ️  {message}")

    @staticmethod
    def debug(message: str) -> None:
        if DEBUG:
            print(f"🐞 {message}")

    @staticmethod
    def warning(message: str) -> None:
        print(f"⚠️  {message}")

    @staticmethod
    def error(message: str) -> None:
        print(f"❌ {message}", file=sys.stderr)

    @staticmethod
    def success(stats: ExportStats, mode: str) -> None:
        print(f"\n✅ {mode.upper()} export complete for {stats.target}")
        print(f"📁 File: {stats.output_file}")
        print(f"🧭 Matches: {stats.matches}")
        if stats.polygons:
            print(f"🧩 Polygons: {stats.polygons}")
        if stats.edges:
            print(f"✏️  Edges: {stats.edges}")
        if stats.labels:
            print(f"🏷️  Labels: {stats.labels}")
        if stats.skipped:
            print(f"⚠️  Skipped: {stats.skipped}")
        print("✨ Done!\n")


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    Cli.debug(f"Ensured output directory exists: {path.resolve()}")


def load_geojson(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    Cli.debug(f"Loading GeoJSON from {path.resolve()}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    Cli.debug(f"Loaded {len(data.get('features', []))} features from {path.name}")
    return data


def safe_icao(feature: dict) -> str:
    return str(feature.get("properties", {}).get(FIELD_ICAO, "")).strip()


def safe_color(feature: dict, default: str = "WHITE") -> str:
    return str(feature.get("properties", {}).get(FIELD_COLOR, default)).strip() or default


def safe_text_label(feature: dict, default: str = "") -> str:
    return str(feature.get("properties", {}).get(FIELD_TEXT_LABEL, default)).strip()


def matches_selection(value: str, selection: str, exact: bool) -> bool:
    return value == selection if exact else selection in value


def dec2dms_pair(vertex: Sequence[float]) -> tuple[str, str]:
    dms_vertex = dec2dms_func(vertex)
    return dms_vertex[0], dms_vertex[1]


def iter_line_segments(ring: Sequence[Sequence[float]]) -> Iterable[list[Sequence[float]]]:
    if len(ring) < 2:
        return
    for index in range(len(ring) - 1):
        yield [ring[index], ring[index + 1]]


def normalize_geo_segments(coordinates: list) -> list[list[Sequence[float]]]:
    """
    Normalize polygon coordinates into two-point line segments.
    Supports common shape: [[[lon, lat], ...]]
    """
    if not coordinates:
        return []

    if len(coordinates) == 1 and isinstance(coordinates[0], list) and coordinates[0]:
        ring = coordinates[0]
        if isinstance(ring[0], (list, tuple)) and len(ring[0]) >= 2:
            return list(iter_line_segments(ring))

    if all(isinstance(edge, list) and len(edge) == 2 for edge in coordinates):
        return coordinates

    return []


def extract_region_vertices(coords: list) -> list[Sequence[float]]:
    """Return the first polygon ring from a typical MultiPolygon structure."""
    try:
        vertices = coords[0][0]
    except (IndexError, TypeError):
        return []
    return vertices if isinstance(vertices, list) else []


def export_geo(selections: Sequence[str], source_dir: Path, output_dir: Path) -> list[ExportStats]:
    geo = load_geojson(source_dir / "geo.geojson")
    results: list[ExportStats] = []

    for selection in selections:
        stats = ExportStats(
            target=selection,
            output_file=output_dir / f"geo_{selection.replace(' ', '_')}.txt",
        )
        Cli.debug(f"Processing GEO selection: {selection}")

        with stats.output_file.open("w", encoding="utf-8") as output:
            output.write(f"[GEO] {selection}\n")

            for idx, feature in enumerate(geo.get("features", [])):
                icao = safe_icao(feature)
                if icao != selection:
                    continue

                stats.matches += 1
                color = safe_color(feature)
                segments = normalize_geo_segments(feature.get("geometry", {}).get("coordinates", []))
                Cli.debug(f"GEO feature #{idx} '{icao}' yielded {len(segments)} segments")

                if not segments:
                    stats.skipped += 1
                    Cli.warning(f"Skipping GEO feature '{icao}' — invalid polygon structure")
                    continue

                for edge in segments:
                    start_lon, start_lat = dec2dms_pair(edge[0])
                    end_lon, end_lat = dec2dms_pair(edge[1])
                    output.write(f"{start_lat} {start_lon} {end_lat} {end_lon} {color}\n")
                    stats.edges += 1

        results.append(stats)
        Cli.success(stats, "geo")

    return results


def export_regions(
    selections: Sequence[str],
    source_dir: Path,
    output_dir: Path,
    exact: bool,
) -> list[ExportStats]:
    regions = load_geojson(source_dir / "regions.geojson")
    results: list[ExportStats] = []

    for selection in selections:
        stats = ExportStats(
            target=selection,
            output_file=output_dir / f"regions-{selection.replace(' ', '_')}.txt",
        )
        Cli.debug(f"Processing REGIONS selection: {selection} (exact={exact})")

        with stats.output_file.open("w", encoding="utf-8") as output:
            output.write(f"[REGIONS] {selection}\n")

            for idx, feature in enumerate(regions.get("features", [])):
                icao = safe_icao(feature)
                if not matches_selection(icao, selection, exact=exact):
                    continue

                vertices = extract_region_vertices(feature.get("geometry", {}).get("coordinates", []))
                Cli.debug(f"REGION feature #{idx} '{icao}' has {len(vertices)} raw vertices")

                if not vertices:
                    stats.skipped += 1
                    Cli.warning(f"Skipping region '{icao}' (feature #{idx}) — invalid coordinates")
                    continue

                dms_vertices = [dec2dms_pair(vertex) for vertex in vertices]
                if len(dms_vertices) > 1 and dms_vertices[0] == dms_vertices[-1]:
                    dms_vertices.pop()
                    Cli.debug(f"Removed duplicated closing vertex for region '{icao}'")

                if not dms_vertices:
                    stats.skipped += 1
                    Cli.warning(f"Skipping region '{icao}' (feature #{idx}) — empty vertex list")
                    continue

                color = safe_color(feature)
                output.write(f"{color}\n")
                first_lon, first_lat = dms_vertices[0]
                output.write(f"{first_lat} {first_lon} ;- {icao}\n")
                for lon, lat in dms_vertices[1:]:
                    output.write(f"{lat} {lon}\n")

                stats.matches += 1
                stats.polygons += 1
                stats.edges += len(dms_vertices)

        results.append(stats)
        Cli.success(stats, "regions")

    return results


def export_labels(
    selections: Sequence[str],
    source_dir: Path,
    output_dir: Path,
    exact: bool,
) -> list[ExportStats]:
    labels = load_geojson(source_dir / "labels.geojson")
    results: list[ExportStats] = []

    for selection in selections:
        stats = ExportStats(
            target=selection,
            output_file=output_dir / f"labels-{selection.replace(' ', '_')}.txt",
        )
        Cli.debug(f"Processing LABELS selection: {selection} (exact={exact})")

        with stats.output_file.open("w", encoding="utf-8") as output:
            output.write(f"[LABELS] {selection}\n")

            for idx, feature in enumerate(labels.get("features", [])):
                icao = safe_icao(feature)
                if not matches_selection(icao, selection, exact=exact):
                    continue

                vertex = feature.get("geometry", {}).get("coordinates")
                if not isinstance(vertex, (list, tuple)) or len(vertex) < 2:
                    stats.skipped += 1
                    Cli.warning(f"Skipping label '{icao}' (feature #{idx}) — invalid point coordinates")
                    continue

                lon, lat = dec2dms_pair(vertex)
                text_label = safe_text_label(feature)
                color = safe_color(feature)
                output.write(f"{lat} {lon} {text_label} {color}\n")

                stats.matches += 1
                stats.labels += 1
                Cli.debug(f"Wrote label '{text_label}' for ICAO '{icao}'")

        results.append(stats)
        Cli.success(stats, "labels")

    return results


def get_active_config() -> tuple[str, list[str], bool]:
    mode = MODE.lower().strip()

    if mode == "geo":
        return mode, list(GEO_SELECTION), True
    if mode == "regions":
        return mode, list(REGIONS_SELECTION), REGIONS_EXACT_MATCH
    if mode == "labels":
        return mode, list(LABELS_SELECTION), LABELS_EXACT_MATCH

    raise ValueError("MODE must be one of: 'geo', 'regions', 'labels'")


def main() -> int:
    try:
        mode, selections, exact = get_active_config()
        if not selections:
            Cli.warning("No selections configured. Nothing to export.")
            return 0

        ensure_output_dir(OUTPUT_DIR)
        Cli.banner(mode, selections, DEBUG)
        Cli.debug(f"Using source directory: {SOURCE_DIR.resolve()}")
        Cli.debug(f"Using output directory: {OUTPUT_DIR.resolve()}")

        if mode == "geo":
            export_geo(selections, SOURCE_DIR, OUTPUT_DIR)
        elif mode == "regions":
            export_regions(selections, SOURCE_DIR, OUTPUT_DIR, exact=exact)
        else:
            export_labels(selections, SOURCE_DIR, OUTPUT_DIR, exact=exact)

    except FileNotFoundError as exc:
        Cli.error(str(exc))
        return 1
    except json.JSONDecodeError as exc:
        Cli.error(f"Invalid JSON: {exc}")
        return 1
    except Exception as exc:
        Cli.error(f"Unexpected error: {exc}")
        if DEBUG:
            raise
        return 1

    print("🎉 Export finished successfully. Have fun!\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
