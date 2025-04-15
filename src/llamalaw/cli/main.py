"""
Command-line interface for LlamaLaw
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from llamalaw.analysis.analyzer import ContractAnalyzer
from llamalaw.models.analysis import AnalysisResult
from llamalaw.storage.repository import ContractRepository

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llamalaw.cli")


def setup_parser() -> argparse.ArgumentParser:
    """Set up command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="LlamaLaw - Legal contract analysis and management"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze a contract document"
    )
    analyze_parser.add_argument(
        "document", help="Path to document file or directory to analyze"
    )
    analyze_parser.add_argument(
        "--output", "-o", help="Output format (json, text, summary)", default="summary"
    )
    analyze_parser.add_argument(
        "--save", "-s", help="Save analysis results to repository", action="store_true"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List contracts in repository")
    list_parser.add_argument(
        "--type", "-t", help="Filter by document type", default=None
    )
    list_parser.add_argument(
        "--output", "-o", help="Output format (json, text, table)", default="table"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search for contracts in repository"
    )
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--output", "-o", help="Output format (json, text, table)", default="table"
    )

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a contract by ID")
    get_parser.add_argument("id", help="Contract ID")
    get_parser.add_argument(
        "--output", "-o", help="Output format (json, text, summary)", default="summary"
    )

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a contract by ID")
    delete_parser.add_argument("id", help="Contract ID")
    delete_parser.add_argument(
        "--force", "-f", help="Force deletion without confirmation", action="store_true"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show repository statistics")
    stats_parser.add_argument(
        "--output", "-o", help="Output format (json, text)", default="text"
    )

    return parser


def analyze_document(args: argparse.Namespace) -> int:
    """
    Analyze a contract document or directory of documents

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    document_path = Path(args.document)
    output_format = args.output
    save_to_repo = args.save

    analyzer = ContractAnalyzer()
    repository = None

    if save_to_repo:
        repository = ContractRepository()

    if document_path.is_file():
        # Analyze single document
        try:
            logger.info(f"Analyzing document: {document_path}")
            result = analyzer.analyze(document_path)

            # Output results
            output_result(result, output_format)

            # Save to repository if requested
            if repository:
                contract_id = repository.add(result)
                print(f"Saved to repository with ID: {contract_id}")

            return 0

        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return 1

    elif document_path.is_dir():
        # Analyze all documents in directory
        try:
            logger.info(f"Analyzing all documents in: {document_path}")
            results = analyzer.batch_analyze(document_path)

            print(f"Analyzed {len(results)} documents:")

            for i, result in enumerate(results):
                print(f"\nDocument {i+1}: {result.contract.filename or 'Unknown'}")
                output_result(result, output_format)

                # Save to repository if requested
                if repository:
                    contract_id = repository.add(result)
                    print(f"Saved to repository with ID: {contract_id}")

            return 0

        except Exception as e:
            logger.error(f"Error analyzing documents: {e}")
            return 1

    else:
        logger.error(f"Invalid path: {document_path}")
        return 1


def list_contracts(args: argparse.Namespace) -> int:
    """
    List contracts in repository

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    document_type = args.type
    output_format = args.output

    repository = ContractRepository()

    try:
        contracts = repository.list(document_type)

        if not contracts:
            print("No contracts found.")
            return 0

        if output_format == "json":
            # Output as JSON
            contract_data = [contract.dict() for contract in contracts]
            print(json.dumps(contract_data, indent=2))

        elif output_format == "table":
            # Output as table
            headers = ["ID", "Title", "Type", "Parties", "Effective Date", "Risks"]
            print_table(
                headers,
                [
                    [
                        contract.id,
                        contract.title,
                        contract.document_type,
                        ", ".join(p.name for p in contract.parties),
                        contract.dates.effective or "N/A",
                        len(contract.risks),
                    ]
                    for contract in contracts
                ],
            )

        else:
            # Output as text
            for contract in contracts:
                print(f"ID: {contract.id}")
                print(f"Title: {contract.title}")
                print(f"Type: {contract.document_type}")
                print(f"Parties: {', '.join(p.name for p in contract.parties)}")
                print(f"Effective Date: {contract.dates.effective or 'N/A'}")
                print(f"Risks: {len(contract.risks)}")
                print()

        return 0

    except Exception as e:
        logger.error(f"Error listing contracts: {e}")
        return 1


def search_contracts(args: argparse.Namespace) -> int:
    """
    Search for contracts in repository

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    query = args.query
    output_format = args.output

    repository = ContractRepository()

    try:
        contracts = repository.search(query)

        if not contracts:
            print(f"No contracts found matching '{query}'.")
            return 0

        if output_format == "json":
            # Output as JSON
            contract_data = [contract.dict() for contract in contracts]
            print(json.dumps(contract_data, indent=2))

        elif output_format == "table":
            # Output as table
            headers = ["ID", "Title", "Type", "Parties", "Effective Date"]
            print_table(
                headers,
                [
                    [
                        contract.id,
                        contract.title,
                        contract.document_type,
                        ", ".join(p.name for p in contract.parties),
                        contract.dates.effective or "N/A",
                    ]
                    for contract in contracts
                ],
            )

        else:
            # Output as text
            for contract in contracts:
                print(f"ID: {contract.id}")
                print(f"Title: {contract.title}")
                print(f"Type: {contract.document_type}")
                print(f"Parties: {', '.join(p.name for p in contract.parties)}")
                print(f"Effective Date: {contract.dates.effective or 'N/A'}")
                print()

        return 0

    except Exception as e:
        logger.error(f"Error searching contracts: {e}")
        return 1


def get_contract(args: argparse.Namespace) -> int:
    """
    Get a contract by ID

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    contract_id = args.id
    output_format = args.output

    repository = ContractRepository()

    try:
        contract = repository.get(contract_id)

        if not contract:
            print(f"Contract with ID '{contract_id}' not found.")
            return 1

        if output_format == "json":
            # Output as JSON
            print(json.dumps(contract.dict(), indent=2))

        elif output_format == "summary":
            # Output as summary
            print(f"Contract: {contract.title}")
            print(f"Type: {contract.document_type}")
            print(f"Parties: {', '.join(p.name for p in contract.parties)}")
            print(f"Effective Date: {contract.dates.effective or 'N/A'}")
            print(f"Termination Date: {contract.dates.termination or 'N/A'}")
            print(f"Clauses: {len(contract.clauses)}")
            print(f"Risks: {len(contract.risks)}")

            if contract.risks:
                print("\nRisks:")
                for risk in contract.risks:
                    print(f"  - {risk.description} ({risk.severity.upper()})")

        else:
            # Output as detailed text
            print(f"ID: {contract.id}")
            print(f"Title: {contract.title}")
            print(f"Type: {contract.document_type}")
            print(f"Filename: {contract.filename or 'N/A'}")
            print(f"Effective Date: {contract.dates.effective or 'N/A'}")
            print(f"Termination Date: {contract.dates.termination or 'N/A'}")

            print("\nParties:")
            for party in contract.parties:
                print(f"  - {party.name}")

            print("\nClauses:")
            for clause in contract.clauses:
                print(f"  - {clause.title} ({clause.type})")

            print("\nRisks:")
            for risk in contract.risks:
                print(f"  - {risk.description} ({risk.severity.upper()})")
                print(f"    Recommendation: {risk.recommendation}")

        return 0

    except Exception as e:
        logger.error(f"Error getting contract: {e}")
        return 1


def delete_contract(args: argparse.Namespace) -> int:
    """
    Delete a contract by ID

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    contract_id = args.id
    force = args.force

    repository = ContractRepository()

    try:
        # Check if contract exists
        contract = repository.get(contract_id)
        if not contract:
            print(f"Contract with ID '{contract_id}' not found.")
            return 1

        # Confirm deletion
        if not force:
            confirm = input(
                f"Are you sure you want to delete contract '{contract.title}'? (y/n): "
            )
            if confirm.lower() != "y":
                print("Deletion cancelled.")
                return 0

        # Delete contract
        success = repository.delete(contract_id)

        if success:
            print(f"Contract '{contract_id}' deleted successfully.")
            return 0
        else:
            print(f"Failed to delete contract '{contract_id}'.")
            return 1

    except Exception as e:
        logger.error(f"Error deleting contract: {e}")
        return 1


def show_stats(args: argparse.Namespace) -> int:
    """
    Show repository statistics

    Args:
        args: Command-line arguments

    Returns:
        int: Exit code
    """
    output_format = args.output

    repository = ContractRepository()

    try:
        stats = repository.get_stats()

        if output_format == "json":
            # Convert datetime objects to strings for JSON serialization
            for key, value in stats.items():
                if hasattr(value, "isoformat"):
                    stats[key] = value.isoformat()

            print(json.dumps(stats, indent=2))

        else:
            # Output as text
            print("Contract Repository Statistics")
            print(f"Total Contracts: {stats['total_contracts']}")

            if stats["contracts_by_type"]:
                print("\nContracts by Type:")
                for doc_type, count in stats["contracts_by_type"].items():
                    print(f"  - {doc_type}: {count}")

            print(f"\nAverage Risk Score: {stats['average_risk_score']:.1f}")

            if stats["first_contract_date"]:
                print(f"First Contract Date: {stats['first_contract_date']}")

            if stats["last_updated_date"]:
                print(f"Last Updated Date: {stats['last_updated_date']}")

        return 0

    except Exception as e:
        logger.error(f"Error getting repository statistics: {e}")
        return 1


def output_result(result: AnalysisResult, output_format: str) -> None:
    """
    Output analysis result in the specified format

    Args:
        result: Analysis result
        output_format: Output format (json, text, summary)
    """
    if output_format == "json":
        # Output as JSON
        print(json.dumps(result.dict(), indent=2))

    elif output_format == "summary":
        # Output as summary
        print(result.generate_summary())
        print(f"Document Type: {result.document_type}")
        print(f"Risks: {len(result.risks)}")

        # Risk summary by severity
        severity_counts = {}
        for risk in result.risks:
            severity = risk.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        if severity_counts:
            print("Risk Severity:")
            for severity, count in severity_counts.items():
                print(f"  - {severity.upper()}: {count}")

    else:
        # Output as detailed text
        contract = result.contract

        print(f"Title: {contract.title}")
        print(f"Document Type: {result.document_type}")
        print(f"Parties: {', '.join(p.name for p in contract.parties)}")
        print(f"Effective Date: {contract.dates.effective or 'N/A'}")
        print(f"Termination Date: {contract.dates.termination or 'N/A'}")

        print("\nClauses:")
        for clause in result.clauses[:5]:  # Show first 5 clauses
            print(f"  - {clause.title}")

        if len(result.clauses) > 5:
            print(f"  ... {len(result.clauses) - 5} more clauses")

        print("\nRisks:")
        for risk in result.risks:
            print(f"  - {risk.description} ({risk.severity.upper()})")
            print(f"    Recommendation: {risk.recommendation}")


def print_table(headers: List[str], rows: List[List[Any]]) -> None:
    """
    Print data as a formatted table

    Args:
        headers: Column headers
        rows: Table rows
    """
    # Convert all values to strings
    string_rows = [[str(cell) for cell in row] for row in rows]

    # Calculate column widths
    widths = [
        max(len(str(h)), max([len(row[i]) for row in string_rows], default=0))
        for i, h in enumerate(headers)
    ]

    # Print headers
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in string_rows:
        print(" | ".join(cell.ljust(w) for cell, w in zip(row, widths)))


def main() -> int:
    """
    Main entry point for CLI

    Returns:
        int: Exit code
    """
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    command_handlers = {
        "analyze": analyze_document,
        "list": list_contracts,
        "search": search_contracts,
        "get": get_contract,
        "delete": delete_contract,
        "stats": show_stats,
    }

    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
