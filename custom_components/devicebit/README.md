---
title: "devicebit"
description: "Instructions on how to integrate DEVICEBIT sensor within Home Assistant."
logo: devicebit-logo.png
ha_category:
  - Sensor
  - Environment
  - Climate
ha_release: 0.104
ha_iot_class: Local Polling
---

`devicebit` provides real-time reading of Temperature & Humidity monitoring (WTH3080, WTH8266) and air monitor (WPM8266,YNM3000) products from [DEVICEBIT](http://www.lwkits.com/) over Wi-Fi.

## Configuration

To use this sensor in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: devicebit
    host: IP_ADDRESS_OF_HOST
    name: DEVICE_NAME
```

{% configuration %}
host:
  description: The IP address of your devicebit.
  required: true
  type: string
port:
  description: port of your devicebit
  required: false
  default: 80
  type: integer
name:
  description: Name for the sensor entity in Home Assistant.
  required: true
  type: string
{% endconfiguration %}

## Sensors

Sensors available in the library: 
 - Temperature & Humidity monitoring products(WTH3080, WTH8266).

| name               | Unit | Description                                           |
|--------------------|------|:-----------------------------------------------------------------------------|
| wth3080_temperature   | °C    | Temperature.                                     |
| wth3080_humidity      |  %    | Humidity.                                        |

 - Air Monitor products (WPM8266,YNM3000).

| name               | Unit | Description                                           |
|--------------------|------|:-----------------------------------------------------------------------------|
| ynm3000_temperature   | °C    | Temperature.                                     |
| ynm3000_humidity      |  %    | Humidity.                                        |
| ynm3000_pm25   | ug/m3 | PM25.                                     |
| ynm3000_aqi     |       | AQI.                                        |
| ynm3000_hcho   | mg/m3 | HCHO.                                     |
| ynm3000_co2      |  ppm  | CO2.                                        |
