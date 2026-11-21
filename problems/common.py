"""Common utilities and serialization for problem modules."""
import json
from pathlib import Path


def fr(x: float, n: int = 2) -> str:
    """Format floating point numbers into French representation."""
    return f"{x:,.{n}f}".replace(",", " ").replace(".", ",")


def save_problem(problem_data: dict, out_dir: Path) -> Path:
    """Save problem dictionary to standard JSON format."""
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = problem_data.get("id", 1)
    slug = problem_data.get("slug", "problem")
    file_path = out_dir / f"{idx:02d}-{slug}.json"
    file_path.write_text(json.dumps(problem_data, ensure_ascii=False, indent=1), encoding="utf-8")
    return file_path
