# ESolar Greenheiss

This Home-Assistant (https://home-assistant.io) integration is a modification of the original from https://github.com/djansen1987/SAJeSolar. The reason for a fork is that SAJ has treated differently their official clients and clients of rebranded hardware (like Greenheiss). People with SAJ Branded hardware have been migrated to the "Elekeeper" platform leaving people with rebranded hardware in the legacy platform.

**NOTE:** This integration was heavily refactored and has been tested only by me. I dont have access to all supported hardware and little experience on this, so I would not consider this  stable yet.

If your monitoring portal is one of the following, this integration most likely will work for you:
 - Peimar: https://peimar-portal.saj-electric.com
 - GreenHeiss: https://inversores-style.greenheiss.com (which is a CNAME for https://greenheiss-portal.saj-electric.com)
 - SolarProfit: https://inversor.saj-electric.com/

 They are all basically the same portal with a different branding (credentials even work in any of them). If you know of a different one not listed here, please let me know.

If your inverter is branded as SAJ and your monitoring site is 'Elekeeper', this wont probably work.  check https://github.com/erelke/ha-esolar Instead


## **Notice**<br>
SAJ does not offer an official API for their legacy eSolar platform. This integration works by mimicking the requests done by their monitoring website and generating home assistant entities based on them.

As such, it is safe to assume this might break at any moment. That warning aside, the platform is quite legacy and hasnt really seen any change in several years.


# **Installation**

### **Manual**
- Copy directory `custom_components/esolar_greenheiss` to your `<config dir>/custom_components` directory.
- Restart Home Assistant
- Add an Integration and look for ESolar Greenheiss. Then follow the configuration steps.

# **Configuration**
- Go to Integrations and click "Add Integration"
- Look up for esolar Greenheiss and select it
- Fill out the following fields:
   - **Username & password**: Pretty self-explanatory
   - **Provider Domain**: The domain of your monitoring site. The default greenheiss one should work, but you can use your brand's domain if needed.
     
     If you change that, make sure to review the advanced section!
   - **Monitoring Hardware**: This integration currently should support the SEC Monitoring Module and the H1 Inverter. Choose the one you have. (AFAIK you cannot use both)
   - **Provider Path**: The path part of the URL used by your provider's site. Check your monitoring site  to verify it. 
     - Greenheiss uses _cloud_: https://greenheiss-portal.saj-electric.com/cloud
     - Peimar uses _portal_: https://peimar-portal.saj-electric.com/portal
   - **Use SSL**: for using https (I see no reason to uncheck this, but maybe there is one)
   - **Verify SSL**: Uncheck if your provider certificate is failing for HASS (Grenheiss.com certificate seems to be not trusted by HASS)

### **Migrating from saj_esolar**

 Note that this integration wont automatically import yaml files.

If you want to migrate from the original integration do the following:
 - Remove all configuration for the integration in your yaml files. Do not erase any entitiy
 - Install this integration into your HASS instance
 - Restart your instance
 - Setup the configuration. This integration's entities are named the same as the original so as long as you removed the original one before setting up this one, they should be 'adopted'.

 #### Notes on migrating

  - The migration is not exactly 1:1. I did some cleanup like replacing some entities that returned 'Y' or 'YES' into proper booleans. I also removed a couple of deprecated entities.
  - It is not longer possible to choose which entities you want. You'll get all entities available for the chosen hardware. I might allow to configure this in the future but for now it proved to difficult for me.
  - I removed a couple of entities considered deprecated because they were originally wrong.


### **Supported Entities**
Based on which hardware you have, you might have a different set of entities. For example, the SEC module is commonly used with R5 inverters which do not support batteries

#### Common Sensors

    nowPower
    runningState
    devOnlineNum
    todayElectricity
    monthElectricity
    yearElectricity
    totalElectricity
    todayGridIncome
    income
    lastUploadTime
    totalPlantTreeNum
    totalReduceCo2
    plantuid
    plantname
    currency
    address
    isOnline
    status
    peakPower
    systemPower
    pvElec
    useElec
    buyElec
    sellElec
    buyRate
    sellRate
    selfUseRate
    selfConsumedRate1
    selfConsumedRate2
    selfConsumedEnergy1
    selfConsumedEnergy2
    plantTreeNum
    reduceCo2

#### H1 Sensors

    totalBuyElec  # Energy -> Grid consumption
    totalConsumpElec
    totalSellElec  # Energy -> Return to grid
    chargeElec  # Energy -> Home Battery Storage -> Energy going in to the battery (kWh)
    dischargeElec  # Energy -> Home Battery Storage -> Energy coming out of the battery (kWh)
    isStorageAlarm
    batCapcity
    batCurr
    batEnergyPercent
    batteryDirection
    batteryPower
    gridDirection
    gridPower
    h1Online
    outPower
    outPutDirection
    pvDirection
    pvPower
    solarPower

#### SEC Module Sensors

    totalPvEnergy
    totalLoadEnergy  # Energy -> Grid consumption
    totalBuyEnergy
    totalSellEnergy  # Energy -> Return to grid
    gridLoadPower  # Power imported from the grid
    solarLoadPower  # Solar power being currently self-consumed
    homeLoadPower  # Total power being consumed by the plant (the home)
    exportPower  # Power being exported to the grid

<br>


## **Supported Devices:**
Following is the list originally compiled by @djansen1987. I currently have no way to test its current state after the elekeeper migration.

The only thing I can say is that you should be able to use the esolar monitoring site for this to work.

I keep this list for historic reasons and maybe to help people searching their hardware to find this integration.

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
#####  *AS1-3KS-5.1* (use h1 sensors)<br>

<br>

### **Greenheiss**<br>
#### GH-I 2M STYLE

<br>

## **Not Supported Devices:** *

### **Commercial Solar Inverter**
#####  *Suntrio Plus 25-60K* <br>

<br>

### **Storage Solar Inverter**<br>
#####  *B1-5.1-48* (not tested) <br>

# **Credits**

I would like to thank [@djansen1987](https://www.github.com/djansen1987) for having written the original integration. He put a lot of effort on it even when he did not have personal need for it.

Credits to [@cyberjunky](https://www.github.com/djansen1987) since seems to have inspired @djansen1987 on the first place
https://github.com/cyberjunky/home-assistant-toon_smartmeter/

