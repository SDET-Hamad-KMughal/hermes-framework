"""Command-line interface for HERMES."""

import argparse

from hermes import __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the HERMES command-line parser."""
    parser = argparse.ArgumentParser(
        prog="hermes",
        description=(
            "HERMES: Hypothesis-driven Exploration through Reasoning "
            "for Modeling and Executing Semantic Workflows."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"HERMES {__version__}",
    )
    return parser


def main() -> None:
    """Run the HERMES command-line interface."""


