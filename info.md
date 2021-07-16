[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987/)

## SAJ eSolar Sensor Component
This is a Custom Component for Home-Assistant (https://home-assistant.io) reads and displays sensor values from the SAJ eSolar private API.

NOTE: This component is build opon an none private API and can change/break at any time.
The component is build with 1 device to test with used in the Netherlands

## Installation

<!-- ### HACS - Recommended
- Have [HACS](https://hacs.xyz) installed, this will allow you to easily manage and track updates.
- Search for 'SAJ eSolar'.
- Click Install below the found integration.
- Configure using the configuration instructions below.
- Restart Home-Assistant. -->

### Manual
- Copy directory `custom_components/saj_esolar` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

sensor:
  - platform: saj_esolar
    username: aa@bb.cc
    password: abcd1234
    resources:
      - nowPower
      - runningState
      - todayElectricity
      - monthElectricity
      - yearElectricity
      - totalElectricity
      - todayGridIncome
      - income
      - lastUploadTime
      - totalPlantTreeNum
      - totalReduceCo2
      - todayAlarmNum
      - userType
      - type
      - status
      - plantuid
      - currency
      - address
      - isOnline
      - peakPower
```

Configuration variables:

- **username** (*Required*): E-mail address used on the eSolar Portal.
- **password** (*Required*): Password used on the eSolar Portal, we advice you to save it in your secret.yaml.
- **resources** (*Required*): This section tells the component which values to display.

## Screenshot

![alt text](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Home-Assistant-Sensors-SAJ-eSolar.png?raw=true "All Sensors")
![alt text](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Home-Assistant-History-SAJ-eSolar.png?raw=true "History Graph")

## Debugging

Add the relevant lines below to the `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.saj_esolar: debug
```

## Donation

Buy me a coffeee: <br />
[![Buymeacoffee](https://www.buymeacoffee.com/assets/img/bmc-meta-new/new/apple-icon-120x120.png)](https://www.buymeacoffee.com/djansen1987)

Paypal:<br />
[![Donate](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Paypal-Donate-QR-code.png?raw=true)](https://www.paypal.me/djansen1987)<br />
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987)
