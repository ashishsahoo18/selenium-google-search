"""History export formats."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def export_history(records: list[dict], destination: Path, kind: str) -> Path:
    """Export records to JSON, CSV, XLSX, or PDF."""
    kind = kind.lower()
    if kind == "json":
        destination.write_text(json.dumps(records, indent=2), encoding="utf-8")
    elif kind == "csv":
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=records[0].keys() if records else ["id"])
            writer.writeheader(); writer.writerows(records)
    elif kind == "xlsx":
        import pandas as pd
        pd.DataFrame(records).to_excel(destination, index=False)
    elif kind == "pdf":
        styles = getSampleStyleSheet(); story = []
        for record in records:
            story += [Paragraph(f"{record['created_at']} — {record['engine']}: {record['original_query']}", styles["BodyText"]), Spacer(1, 6)]
        SimpleDocTemplate(str(destination), pagesize=letter).build(story)
    else:
        raise ValueError(f"Unsupported format: {kind}")
    return destination
