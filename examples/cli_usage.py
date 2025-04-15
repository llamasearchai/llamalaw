#!/usr/bin/env python3
"""
LlamaLaw CLI Usage Example

This script demonstrates how to use the LlamaLaw CLI to analyze
contracts and manage the contract repository.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, silent=False):
    """Run a command and print its output"""
    if not silent:
        print(f"\n> {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not silent:
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    return result


def main():
    """Run the example"""
    print("LlamaLaw CLI Usage Example")
    print("==========================")

    # Ensure the example contract directory exists
    contracts_dir = Path(__file__).parent / "sample_contracts"
    os.makedirs(contracts_dir, exist_ok=True)

    # Create a sample NDA if it doesn't exist
    nda_path = contracts_dir / "sample_nda.txt"
    if not nda_path.exists():
        print("Creating sample NDA...")
        with open(nda_path, "w") as f:
            f.write(
                """CONFIDENTIALITY AGREEMENT

EFFECTIVE DATE: January 1, 2024

This Confidentiality Agreement (the "Agreement") is entered into by and between:

Alpha Corporation, a Delaware corporation ("Discloser"), and
Beta Enterprises LLC, a California limited liability company ("Recipient").

1. CONFIDENTIAL INFORMATION

For purposes of this Agreement, "Confidential Information" means any and all non-public information disclosed by Discloser to Recipient, including but not limited to technical data, trade secrets, know-how, research, product plans, products, services, customer lists, markets, software, developments, inventions, processes, formulas, technology, designs, drawings, engineering, marketing, finances, or other business information.

2. OBLIGATIONS OF RECIPIENT

Recipient shall:
a) Use the Confidential Information only for the purpose of evaluating a potential business relationship with Discloser.
b) Maintain the Confidential Information in strict confidence for a period of five (5) years from the date of disclosure.
c) Not disclose the Confidential Information to any third party without prior written consent of Discloser.
d) Limit access to Confidential Information to employees, agents, or representatives who have a need to know.
e) Protect the Confidential Information with the same degree of care used to protect its own confidential information.

3. EXCLUSIONS

The obligations under this Agreement do not apply to information that:
a) Was in Recipient's possession prior to disclosure by Discloser.
b) Is or becomes publicly available through no fault of Recipient.
c) Is rightfully received by Recipient from a third party without restriction.
d) Is independently developed by Recipient without use of the Confidential Information.
e) Is required to be disclosed by law or court order, provided Recipient gives Discloser prompt notice.

4. GOVERNING LAW

This Agreement shall be governed by the laws of the State of Delaware.

5. TERMINATION

This Agreement shall remain in effect until written notice of termination is provided by either party.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

Alpha Corporation
By: Jane Smith, CEO

Beta Enterprises LLC
By: John Doe, Managing Member
"""
            )

    # Display help
    run_command("llamalaw --help")

    # Analyze the sample NDA
    print("\nAnalyzing sample NDA...\n")
    run_command(f"llamalaw analyze {nda_path} --output summary --save")

    # List contracts in the repository
    print("\nListing all contracts in repository...\n")
    run_command("llamalaw list")

    # Filter contracts by type
    print("\nListing only non-disclosure agreements...\n")
    run_command("llamalaw list --type non-disclosure-agreement")

    # Search for contracts
    print("\nSearching for contracts with 'Alpha'...\n")
    run_command("llamalaw search Alpha")

    # Get contract details
    print("\nGetting contract details...\n")
    # The ID will be different each time, so we need to get it first
    result = run_command("llamalaw list --output json", silent=True)
    try:
        import json

        contracts = json.loads(result.stdout)
        if contracts:
            contract_id = contracts[0]["id"]
            run_command(f"llamalaw get {contract_id}")

            # Get contract risks
            print("\nGetting contract risks...\n")
            run_command(f"llamalaw get {contract_id} --output text")

            # Delete the contract
            print("\nDeleting the contract...\n")
            run_command(f"llamalaw delete {contract_id} --force")
    except Exception as e:
        print(f"Error processing contract: {e}")

    # Show repository statistics
    print("\nShowing repository statistics...\n")
    run_command("llamalaw stats")

    print("\nExample completed!")


if __name__ == "__main__":
    main()
