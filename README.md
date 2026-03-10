# Brita Filter – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/lukaszkac/brita-filter?label=release&style=flat-square)](https://github.com/lukaszkac/brita-filter/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Monitor your Brita water filter life directly in Home Assistant – no cloud, no app, no hardware required.

![Brita Filter integration overview](docs/screenshot_integration.png)

## Features

- Tracks days since last filter replacement
- Shows remaining filter life as %
- Mirrors the physical pitcher display (25% steps)
- Status sensor: Good / Replace soon / Replace now!
- **One-click reset button** — mark filter as replaced directly from the HA UI
- `brita_filter.reset_filter` service to reset via automations
- Config flow – no YAML needed
- 🇬🇧 English / 🇵🇱 Polish translations
- Automation Blueprint for notifications included

## Screenshots

| Integration page | Entities | Configure options |
|:---:|:---:|:---:|
| ![Integration](docs/screenshot_integration.png) | ![Entities](docs/screenshot_entities.png) | ![Options](docs/screenshot_options.png) |

## Installation via HACS

1. In HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/lukaszkac/brita-filter` as **Integration**
3. Install **Brita Filter**
4. Restart Home Assistant
5. Settings → Integrations → Add → search **Brita Filter**

## Manual installation

Copy `custom_components/brita_filter/` to your HA `config/custom_components/` directory and restart.

## Configuration

After adding the integration you will be asked for:

| Field | Default | Description |
|---|---|---|
| Name | Brita Filter | Friendly name |
| Filter lifetime | 28 days | Recommended replacement interval |
| Last replaced | today | Date of last filter replacement |

Settings can be changed anytime via **Settings → Integrations → Brita Filter → Configure**.

## Entities

| Entity | Unit | Description |
|---|---|---|
| `sensor.brita_filter_days_since` | d | Days since last replacement |
| `sensor.brita_filter_remaining` | % | Remaining filter life |
| `sensor.brita_filter_status` | – | good / replace_soon / replace_now |
| `sensor.brita_filter_display_level` | – | Level matching physical display *(hidden by default)* |
| `button.brita_filter_reset` | – | Mark filter as replaced today |

## Replacing the filter

When you replace your filter, press the **Replace filter** button in the HA device page, or call the service:

```yaml
service: brita_filter.reset_filter
```

## Notifications (Blueprint)

The integration automatically installs an automation blueprint on first run.

Go to **Settings → Automations → Blueprints** and look for **Brita Filter – notifications**.

Or import it manually:

[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://raw.githubusercontent.com/lukaszkac/brita-filter/master/blueprints/automation/brita_filter_notifications.yaml)

**Configurable options:**
- Any notification service (mobile app, Telegram, email, persistent notification...)
- Toggle "Replace soon" notification on/off
- Toggle "Replace now!" notification on/off
- Optional daily morning reminder when filter is overdue
- Customizable reminder time

## License

MIT
