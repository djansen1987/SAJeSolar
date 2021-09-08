[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987/)

## SAJ eSolar Sensor Component
This is a Custom Component for Home-Assistant (https://home-assistant.io) reads and displays sensor values from the SAJ eSolar Portal private API.

NOTE: This component is built upon a none private API and can change/break at any time.
The component is built with 2 device to test with used in the Netherlands

## Installation

### HACS - Recommended
- Have [HACS](https://hacs.xyz) installed, this will allow you to easily manage and track updates.
- Search for 'SAJ eSolar'.
- Click Install below the found integration.
- Configure using the configuration instructions below.
- Restart Home-Assistant.

### Manual
- Copy directory `custom_components/saj_esolar` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Note when updating
 - resources are renamed in de configuration, replace old ones. applies when updating v1.0.0.4 -> 1.0.0.5

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
      - status
      - plantuid
      - currency
      - address
      - isOnline
      - peakPower
```

If you have a Saj Sec module add the following config under platform:

```yaml
    sensors: saj_sec # Optional will only work with SAJ Sec Module
```  

<!-- The device_id can be found on the SAJ portal under "Load Monitorring" (Currently have not found a api the outputs the serial numbers, there for it need to be added manualy)
![alt text](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/SAJ-Portal-Sec-Module-Serial-Number.png?raw=true "Sec Serial Number") -->


Optional sensors when using an Saj Sec Module:

```yaml
      - pvElec
      - useElec
      - buyElec
      - sellElec
      - buyRate
      - sellRate
      - selfConsumedRate1
      - selfConsumedRate2
      - selfConsumedEnergy1
      - selfConsumedEnergy2
      - plantTreeNum
      - reduceCo2
      - totalGridPower
      - totalLoadPower
      - totalPvgenPower
      - totalPvEnergy
      - totalLoadEnergy
      - totalBuyEnergy
      - totalSellEnergy
```


Configuration variables:

- **username**   (*Required*): E-mail address used on the eSolar Portal.
- **password**   (*Required*): Password used on the eSolar Portal, we advise you to save it in your secret.yaml.
- **resources**  (*Required*): This section tells the component which values to display.
- **sensors**    (*Optional*): saj_sec # Optional will only work with SAJ Sec Module
<!-- - **device_id**: (*Optional*): M123456789234567 # Optional will only work with SAJ Sec Module -->

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
## Credits

Credits to @cyberjunky. I got inspired by his source code which helped me a lot to create my first Custom Component.
https://github.com/cyberjunky/home-assistant-toon_smartmeter/

## Donation

Buy me a coffee: <br />
[![Buymeacoffee](https://www.buymeacoffee.com/assets/img/bmc-meta-new/new/apple-icon-120x120.png)](https://www.buymeacoffee.com/djansen1987)

PayPal:<br />
[![Donate](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Paypal-Donate-QR-code.png?raw=true)](https://www.paypal.me/djansen1987)<br />
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987)
