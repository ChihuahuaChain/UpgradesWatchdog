# UpgradesWatchdog 🐶
Cosmos Chains Upgrades Watchdog

_An interchain upgrades watchdog brought to you by [ChihuahuaChain](https://chihuahua.wtf)_

# Info
UpgradesWatchdog 🐶 makes it easier to follow any Software Upgrade Proposal and GitHub release of any Cosmos Blockchain.
The first iteration of UpgradesWatchdog it's a rushed, working, draft.
The bot uses the chain-registry data in order to search for new GitHub releases and scans Governance Voting Proposals to get SoftwareUpgrades info.

#### We are currently supporting and tracking the following networks on the [Official Telegram Channel](https://t.me/CosmosUpgrades) checking for updates every 1 hour.
- Akash
- Assetmantle
- Axelar
- Bandchain
- Bitcanna
- Bitsong
- Cerberus
- Chihuahua (obviously)
- Comdex
- Cosmos Hub
- Crescent
- Crypto.org
- Evmos
- Gravity-Bridge
- Injective
- Juno
- Omniflix Hub
- Osmosis
- Passage
- Persistence
- Secret Network
- Sentinel (DVPN)
- Stargaze
- Teritori
- Terra
- Terra 2
- Umee

If you need us to follow a specific network, feel free to open a PR

# Todo
This code is currently a draft and rushed in to "just work".
There is a lot more to add and polish, twitter? discord? The more, the better!
Some networks are giving us headache because they don't properly release software on GitHub or because of faulty endpoints.

- [x] v2.0b Private Testing
- [x] Release Source Code
- [ ] Better coding
- [ ] Add Twitter Notifications
- [ ] Add Discord Notifications


## Installation

- Clone the repository
```bash 
git clone https://github.com/ChihuahuaChain/UpgradesWatchdog
```
- Install dependencies
```bash 
cd UpgradesWatchdog\
pip3 install -m requirements.txt
```
- Edit the configuration variables on the watchdog.py
  - ```github_token = "YOUR_GITHUB_TOKEN"```
  - ```telegram_token = "TELEGRAM_BOT_TOKEN"```
  - ```telegram_notification = ["TELEGRAM_ID_1", "TELEGRAM_ID_2"]```
  - ```supported = ["chihuahua", "osmosis", "bitcanna"]```

- Launch it
  - ```python3 watchdog.py```

If you want to automatically run it at any given time, use crontab.

# Donate
We don't seek for donations, but you can say Thank You for our work by [delegating to our validators](https://delegate.chihuahua.wtf) and by [sharing this project on Twitter](https://twitter.com/intent/tweet?text=Check%20out%20%23pyCosmicWrap%20%F0%9F%8C%AF%20by%20%40ChihuahuaChain%20-%20A%20%23python%20wrapper%20for%20%40cosmos%20on%20https%3A//github.com/ChihuahuaChain/pyCosmicWrap%20%23HUAHUA%20%23Chihuahua%20%23WOOF%0A)

# License
ChihuahuaChain/UpgradesWatchdog is licensed under the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)