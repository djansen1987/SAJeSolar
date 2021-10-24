[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987/)

# **SAJ eSolar Sensor Component**
This is a Custom Component for Home-Assistant (https://home-assistant.io) reads and displays sensor values from the SAJ eSolar Portal private API.

NOTE: This component is built upon a none public API and can change/break at any time.
The component is built with 2 device to test with used in the Netherlands and Malaysia. Please go to the [Supported devides](#devices) part to see if your device is supported
#
<br><br>

# **Installation**

### **HACS - Recommended**
- Have [HACS](https://hacs.xyz) installed, this will allow you to easily manage and track updates.
- Search for 'SAJ eSolar'.
- Click Install below the found integration.
- Configure using the configuration instructions below.
- Restart Home-Assistant.
#
### **Manual**
- Copy directory `custom_components/saj_esolar` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.
#

##### **Note when updating from v1.0.0.4**
##### - resources are renamed in de configuration, replace old ones. applies when updating v1.0.0.4 -> 1.0.0.5
#
<br><br>

# **Usage**
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
      - totalElectricity # Energy -> Solar production
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
H1 Sensors:

```yaml
    sensors: h1
    resources:
      - nowPower
      - runningState
      - todayElectricity
      - monthElectricity
      - yearElectricity
      - totalElectricity # Energy -> Solar production
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

      - devOnlineNum
      - selfUseRate
      - totalBuyElec # Energy -> Grid consumption
      - totalConsumpElec
      - totalSellElec # Energy -> Return to grid
      - batCapcity
      - batCurr
      - batEnergyPercent
      - batteryDirection
      - batteryPower
      - gridDirection
      - gridPower
      - h1Online
      - outPower
      - outPutDirection
      - pvDirection
      - pvPower
      - solarPower
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
```


Saj Sec Module:

```yaml
    sensors: saj_sec # Optional will only work with SAJ Sec Module
    resources:
      - nowPower
      - runningState
      - todayElectricity
      - monthElectricity
      - yearElectricity
      - totalElectricity # Energy -> Solar production
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
      - totalLoadEnergy # Energy -> Grid consumption
      - totalBuyEnergy
      - totalSellEnergy # Energy -> Return to grid
```


**Configuration variables:**

- **username**   (*Required*): E-mail address used on the eSolar Portal.
- **password**   (*Required*): Password used on the eSolar Portal, we advise you to save it in your secret.yaml.
- **resources**  (*Required*): This section tells the component which values to display.
- **sensors**    (*Optional*): saj_sec / h1 # Optional will only work with SAJ Sec Module

#
<br><br>
# **Devices**

## **Supported Devices:**
<br>

### **solar Inverter:**

#####  *R5 -0.7-3K-S1*<br>
#####  *R5-3~8K-S2*<br>
#####  *R5-3-20K-T2*<br>
#####  *Sununo plus 4K-M-RD*<br>


<br>

### **eSolar Modules:**

#####  *eSolar SEC-module*<br>
#####  *eSolar WiFi- D*<br>
#####  *eSolar 4G*<br>
#####  *AOI3*<br>

<br>

### **Storage Solar Inverter**<br>
#####  *H1-3~6K-S2* <br>

<br>

## **Not Supported Devices:** *(create github discussion to request)*
<br>

### **Commercial Solar Inverter**
#####  *Suntrio Plus 25-60K* <br>

<br>

### **Storage Solar Inverter**<br>
#####  *AS1-3KS-5.1* (not tested) <br>
#####  *B1-5.1-48* (not tested) <br>

<br><br>
#
# **Screenshot**

![alt text](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Home-Assistant-Sensors-SAJ-eSolar.png?raw=true "All Sensors")
![alt text](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Home-Assistant-History-SAJ-eSolar.png?raw=true "History Graph")

<br><br>

# **Debugging**

Add the relevant lines below to the `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.saj_esolar: debug
```
<br><br>

# **Credits**

Credits to @cyberjunky. I got inspired by his source code which helped me a lot to creating this Custom Component.
https://github.com/cyberjunky/home-assistant-toon_smartmeter/
<br><br>

# **Donation**

Buy me a coffee: <br />
[![Buymeacoffee](https://www.buymeacoffee.com/assets/img/bmc-meta-new/new/apple-icon-120x120.png)](https://www.buymeacoffee.com/djansen1987)

PayPal:<br />
[![Donate](https://github.com/djansen1987/SAJeSolar/blob/main/screenshots/Paypal-Donate-QR-code.png?raw=true)](https://www.paypal.me/djansen1987)<br />
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/djansen1987)
