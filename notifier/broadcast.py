import requests
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Broadcast a message to the notifier API")
    parser.add_argument('--component', required=True, help="The component to broadcast the message to")
    parser.add_argument('--proposal', help="The proposal ID (optional)")
    parser.add_argument('--message', help="The message to broadcast (optional, can be piped in)")
    parser.add_argument('--yes', action='store_true', help="Automatically confirm the broadcast message")

    args = parser.parse_args()

    component = args.component
    proposal_id = args.proposal
    message = args.message
    auto_confirm = args.yes

    # If message is not provided as an argument, read from stdin
    if not message:
        if not sys.stdin.isatty():
            print("Reading message from stdin (end with Ctrl-D):")
            lines = sys.stdin.read().splitlines()
            message = "\n".join(lines)
        else:
            print("Enter the message (end with Ctrl-D):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            message = "\n".join(lines)

    data = {
        "component": component,
        "message": message,
        "proposal_id": proposal_id if proposal_id else None
    }

    # Display preview
    print("\n--- Preview ---")
    print(f"Component: {component}")
    print(f"Message:\n{message}")
    if proposal_id:
        print(f"Proposal ID: {proposal_id}")
    else:
        print("Proposal ID: None")
    print("----------------\n")

    if auto_confirm:
        confirm = 'yes'
    else:
        confirm = input("Do you want to send this broadcast? (yes/no or y/n): ").strip().lower()

    if confirm in ['yes', 'y']:
        response = requests.post("http://localhost:5000/broadcast", json=data)
        if response.status_code == 200:
            print("Broadcast sent successfully")
        else:
            try:
                error_message = response.json()
            except requests.exceptions.JSONDecodeError:
                error_message = response.text
            print(f"Failed to send broadcast: {error_message}")
    else:
        print("Broadcast canceled")

if __name__ == "__main__":
    main()