# HomeAssistant
home assistant custom components
The HT&AirMonitor integration connects to home-assistant. HT&AirMonitor may be connected to a home Wi-Fi network and expose a REST API.

Configuration

To use the sensors in your installation, add the following to your configuration.yaml file:

# Example configuration.yaml entry
```yaml
# Example configuration.yaml entry
sensor:
  - platform: devicebit
    host: IP_ADDRESS
    name: your device name

CONFIGURATION VARIABLES

host
(string)(Required)
The IP address of your HT&AirMonitor system.

name
(string)(Required)


model
(string)(Optional): WTH8266/WTH3080/YNM3000
