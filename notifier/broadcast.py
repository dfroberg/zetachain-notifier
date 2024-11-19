import requests
import sys

def main():
    component = input("Enter the component: ")
    print("Enter the message (end with Ctrl-D):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    message = "\n".join(lines)
    proposal_id = input("Enter the proposal ID (optional): ")

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