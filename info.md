The **ESolar Greenheiss** integration allows you to monitor your solar energy production and consumption data directly in Home Assistant using your [SAJ ESolar](https://www.saj-electric.com/) account.

## Features

- View real-time solar power generation
- Track daily, monthly, and total energy production
- Monitor grid import/export balance
- Access plant and inverter information
- Works with multiple plants (if your account provides them)

## Requirements

- A valid **SAJ ESolar** account
- Internet access to connect to the ESolar web portal

## Setup

1. Go to **Settings > Devices & Services** in Home Assistant.
2. Click **Add Integration** and search for **ESolar Greenheiss**.
3. Fill out the following fields:
   - **Username & password**: Pretty self-explanatory
   - **Provider Domain**: The domain of your monitoring site. The default greenheiss one should work, but you can use your brand's domain if needed.
     
     If you change that, make sure to review the advanced section!
   - **Monitoring Hardware**: This integration currently should support the SEC Monitoring Module and the H1 Inverter. Choose the one you have. (AFAIK you cannot use both)
   - **Provider Path**: The path part of the URL used by your provider's site. Check your monitoring site  to verify it. 
     - Greenheiss uses _cloud_: https://greenheiss-portal.saj-electric.com/cloud
     - Peimar uses _portal_: https://peimar-portal.saj-electric.com/portal
   - **Use SSL**: for using https (I see no reason to uncheck this, but maybe there is one)
   - **Verify SSL**: Uncheck if your provider certificate is failing for HASS (Grenheiss.com certificate seems to be not trusted by HASS)