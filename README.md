# Community Notifier

## Setup

1. Clone the repository.
2. Configure your API keys in `config.py`.

~~~python
# Avatar URL for the bot
avatar_url = "https://avatars.githubusercontent.com/u/86979844?s=200&v=4"
humanize_datetime = True

# These are datasources that the notifier will use to fetch data
statuspages = [
    {
        "enabled": True,  # Enable or disable the statuspage
        "name": "FrobergCo Status",  # Name of the statuspage
        "api_key": "your_statuspage_api_key",  # API key for the statuspage
        "page_id": "your_statuspage_page_id"  # Page ID for the statuspage
    },
    {
        "enabled": False,
        "name": "Zetachain Status",
        "api_key": "customer2_statuspage_api_key",
        "page_id": "customer2_statuspage_page_id"
    }  # Add more statuspages as needed
]

# These are customers that the notifier will send messages to
customers = [
    {
        "enable": True,  # Enable or disable the customer
        "name": "Danny's Crypto",
        "groups": ["institutional", "mainnet", "testnet", "all"],
        "discord": {
            "enabled": True,
            "webhook_url": "https://discord.com/api/webhooks/your_discord_webhook_url"
        },
        "slack": {
            "enabled": True,
            "webhook_url": "https://hooks.slack.com/services/your_slack_webhook_url"
        },
        "telegram": { # https://t.me/zetachain_notifier_bot
            "enabled": True,
            "bot_token": "your_telegram_bot_token",
            "chat_id": "@your_telegram_channel" # or "your_chat_id"
        },
        "statuspage": {
            "enabled": False,
            "api_key": "",
            "page_id": ""
        }
    },
    {
        "enable": False,
        "name": "Zetachain SREs",
        "groups": ["institutional", "mainnet", "testnet", "all"],
        "discord": {
            "enabled": False,
            "webhook_url": ""
        },
        "slack": {
            "enabled": False,
            "webhook_url": ""
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        },
        "statuspage": {
            "enabled": False,
            "api_key": "",
            "page_id": ""
        }
    }
]
~~~
## Usage

Run the main script to send notifications:

```sh
uv run main.py [--once|--watch]
```

## Examples

### Slack
![Governance Slack Example](assets/governance_slack.png)

### Discord
![Discord Example](assets/governance_discord.png)

### Telegram
![Telegram Example](assets/governance_telegram.png)
