"""Generate publication-ready LaTeX evaluation tables."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read rows from a CSV file."""

    if not path.exists():
        raise FileNotFoundError(
            f"evaluation table not found: {path}"
        )

    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        return list(csv.DictReader(handle))


def escape_latex(value: object) -> str:
    """Escape common LaTeX special characters."""

    text = str(value)

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }

    for source, replacement in replacements.items():
        text = text.replace(source, replacement)

    return text


def format_decimal(
    value: str | float | int,
    digits: int = 3,
) -> str:
    """Format a numeric value safely."""

    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return escape_latex(value)


def format_percentage(
    value: str | float | int,
) -> str:
    """Format a ratio as a percentage."""

    try:
        return f"{float(value) * 100:.1f}\\%"
    except (TypeError, ValueError):
        return escape_latex(value)


def generate_group_table(
    rows: list[dict[str, str]],
) -> str:
    """Generate the experiment-group summary table."""

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Execution and anomaly results by experiment group.}",
        r"\label{tab:group-results}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        (
            r"Group & Runs & Success & Anomalies & "
            r"Anomaly Rate & Mean Divergence \\"
        ),
        r"\midrule",
    ]

    for row in rows:
        lines.append(
            "{} & {} & {} & {} & {} & {} \\\\".format(
                escape_latex(row["group"]),
                row["record_count"],
                format_percentage(
                    row["execution_success_rate"]
                ),
                row["anomaly_count"],
                format_percentage(row["anomaly_rate"]),
                format_decimal(
                    row["mean_divergence_score"]
                ),
            )
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
        ]
    )

    return "\n".join(lines)


def generate_workflow_table(
    rows: list[dict[str, str]],
) -> str:
    """Generate the workflow-level summary table."""

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Mutation results by benchmark workflow.}",
        r"\label{tab:workflow-results}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        (
            r"Workflow & Mutations & Anomalies & "
            r"Anomaly Rate & Mean Time (s) \\"
        ),
        r"\midrule",
    ]

    for row in rows:
        lines.append(
            "{} & {} & {} & {} & {} \\\\".format(
                escape_latex(row["workflow_id"]),
                row["mutation_record_count"],
                row["anomaly_count"],
                format_percentage(row["anomaly_rate"]),
                format_decimal(
                    row["mean_duration_seconds"]
                ),
            )
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
        ]
    )

    return "\n".join(lines)


def generate_strategy_table(
    rows: list[dict[str, str]],
) -> str:
    """Generate the mutation-strategy summary table."""

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{Effectiveness of workflow mutation strategies.}",
        r"\label{tab:strategy-results}",
        r"\resizebox{\columnwidth}{!}{%",
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        (
            r"Group & Strategy & Runs & Success & "
            r"Anomaly Rate & Divergence \\"
        ),
        r"\midrule",
    ]

    for row in rows:
        lines.append(
            "{} & {} & {} & {} & {} & {} \\\\".format(
                escape_latex(row["group"]),
                escape_latex(row["mutation_strategy"]),
                row["record_count"],
                format_percentage(
                    row["execution_success_rate"]
                ),
                format_percentage(row["anomaly_rate"]),
                format_decimal(
                    row["mean_divergence_score"]
                ),
            )
        )

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        default="evaluation/tables",
    )
    parser.add_argument(
        "--output-dir",
        default="evaluation/tables/latex",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    group_table = generate_group_table(
        read_csv(input_dir / "group_summary.csv")
    )
    workflow_table = generate_workflow_table(
        read_csv(input_dir / "workflow_summary.csv")
    )
    strategy_table = generate_strategy_table(
        read_csv(
            input_dir
            / "mutation_strategy_summary.csv"
        )
    )

    outputs = {
        "group_summary.tex": group_table,
        "workflow_summary.tex": workflow_table,
        "mutation_strategy_summary.tex": strategy_table,
    }

    for filename, content in outputs.items():
        path = output_dir / filename
        path.write_text(
            content + "\n",
            encoding="utf-8",
        )
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
