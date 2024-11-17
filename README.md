# Zetachain Community Notifier

Work in progress on making it pretty, but it works.

Artifacts for mac & linux (ubuntu) are stored in the github workflow runs.

## Setup

1. Clone the repository.
2. Install 
    - `brew install pre-commit` # for macOS
    - `pip install pre-commit` # for Linux
    - `uv` as per https://docs.astral.sh/uv/
    - `uv pip install -U pyinstaller` to create a standalone executables
3. Configure your API keys & Webhooks in `notifier/config.yaml`.

~~~yaml
avatar_url: "https://avatars.githubusercontent.com/u/86979844?s=200&v=4"
humanize_datetime: true

statuspages:
  - enabled: true
    name: "FrobergCo Status"
    api_key: "your_statuspage_api_key"
    page_id: "your_statuspage_page_id"
  - enabled: false
    name: "Zetachain Status"
    api_key: "customer2_statuspage_api_key"
    page_id: "customer2_statuspage_page_id"

customers:
  - enable: true
    name: "Danny's Crypto"
    groups: ["institutional", "mainnet", "testnet", "all"]
    discord:
      enabled: true
      webhook_url: "https://discord.com/api/webhooks/your_discord_webhook_url"
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/your_slack_webhook_url"
    telegram:
      enabled: true
      bot_token: "your_telegram_bot_token"
      chat_id: "@your_telegram_channel"  # or "your_chat_id"
    statuspage:
      enabled: false
      api_key: ""
      page_id: ""
  - enable: false
    name: "Zetachain SREs"
    groups: ["institutional", "mainnet", "testnet", "all"]
    discord:
      enabled: false
      webhook_url: ""
    slack:
      enabled: true
      webhook_url: "https://hooks.slack.com/services/your_slack_webhook_url"
    telegram:
      enabled: false
      bot_token: "customer2_telegram_bot_token"
      chat_id: "customer2_telegram_chat_id"
    statuspage:
      enabled: false
      api_key: "customer2_statuspage_api_key"
      page_id: "customer2_statuspage_page_id"
~~~

4. Run the main script to send notifications:

```sh
cd notifier
uv run main.py [--once|--watch] [--override-date-filter]
```

# Usage

~~~sh
usage: main.py [-h] [--override-date-filter] [--once] [--watch]

Notifier script for ZetaChain updates and proposals

optional arguments:
  -h, --help            show this help message and exit
  --override-date-filter
                        Override date filter and send the latest update and proposal regardless of date
  --once                Run the script once and exit
  --watch               Keep the script running and check for updates every 30 seconds
  --loglevel {debug,info,warning,error,critical}
                        Set the logging level
~~~

## Example Run

~~~
2024-11-17 11:42:46.724 | INFO     | __main__:<module>:214 - Starting notifier script
2024-11-17 11:42:46.724 | INFO     | __main__:load_sent_updates:34 - Loaded sent updates from pickle file
2024-11-17 11:42:47.060 | INFO     | __main__:fetch_status_updates:49 - Fetched status updates
2024-11-17 11:42:47.231 | INFO     | __main__:fetch_governance_proposals:77 - Fetched governance proposals
2024-11-17 11:42:47.234 | INFO     | __main__:main:181 - Override date filter: Sending the latest update and proposal regardless of date
2024-11-17 11:42:47.503 | INFO     | discord_notifier:send_discord_message:56 - Sent Discord message with status code 204
2024-11-17 11:42:47.504 | INFO     | __main__:notify_customer:133 - Sent Discord message to Danny's Crypto
2024-11-17 11:42:47.871 | INFO     | slack_notifier:send_slack_message:93 - Sent Slack message with status code 200
2024-11-17 11:42:47.872 | INFO     | __main__:notify_customer:138 - Sent Slack message to Danny's Crypto
2024-11-17 11:42:48.246 | INFO     | telegram_notifier:send_telegram_message:44 - Sent Telegram message with message_id 39
2024-11-17 11:42:48.248 | INFO     | __main__:notify_customer:143 - Sent Telegram message to Danny's Crypto
2024-11-17 11:42:48.248 | INFO     | __main__:main:192 - Notified Danny's Crypto about status update This is an example incident
2024-11-17 11:42:48.479 | INFO     | discord_notifier:send_discord_message:56 - Sent Discord message with status code 204
2024-11-17 11:42:48.479 | INFO     | __main__:notify_customer:153 - Sent Discord message to Danny's Crypto
2024-11-17 11:42:48.768 | INFO     | slack_notifier:send_slack_message:93 - Sent Slack message with status code 200
2024-11-17 11:42:48.769 | INFO     | __main__:notify_customer:158 - Sent Slack message to Danny's Crypto
2024-11-17 11:42:49.016 | INFO     | telegram_notifier:send_telegram_message:44 - Sent Telegram message with message_id 40
2024-11-17 11:42:49.020 | INFO     | __main__:notify_customer:163 - Sent Telegram message to Danny's Crypto
2024-11-17 11:42:49.020 | INFO     | __main__:main:200 - Notified Danny's Crypto about governance proposal v21 Upgrade
2024-11-17 11:42:49.021 | INFO     | __main__:save_sent_updates:42 - Saved sent updates to pickle file
2024-11-17 11:42:49.021 | INFO     | __main__:<module>:221 - Notifier script finished
~~~

## Examples

### Slack
![Governance Slack Example](assets/governance_slack.png)

### Discord
![Discord Example](assets/governance_discord.png)

### Telegram
![Telegram Example](assets/governance_telegram.png)

### Statuspage Incident Upstream
![Statuspage Incident Upstream Example](assets/status_upstream.png)

### Statuspage Discord
![Statuspage Discord Example](assets/status_discord.png)

## TODO:

- Create configurable templates for notifications
- Unpack more statuspage data with components
- Match customer tags with statuspage components