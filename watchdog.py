# Upgrades Watchdog v2.2
# ChihuahuaChain - https://github.com/ChihuahuaChain/UpgradesWatchdog
#
# License GNU General Public License v3.0
#
# https://choosealicense.com/licenses/gpl-3.0/
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PIL import ImageFont, Image, ImageDraw
from pycosmicwrap import CosmicWrap
from telegram.ext import Updater
from git.repo.base import Repo
from github import Github
from io import BytesIO
from time import sleep
import multiprocessing
import logging
import json
import os
import re

# CONFIGURATION

# GitHub Personal Access Token
github_token = "YOUR_GITHUB_TOKEN"

# Telegram Bot API Token
telegram_token = "YOUR_TELEGRAM_BOT_TOKEN"

# Comma separated Telegram chat_id, channels, groups to notify
telegram_notification = ["@CosmosUpgrades"]

# Comma separated supported chains
supported = ["chihuahua", "osmosis", "bitcanna"]

# Send images instead of text, cool eh?
use_image = True

# CONFIGURATION END

chains = []
queue = []
g = Github(github_token)
chain_registry = "https://github.com/cosmos/chain-registry"
telegram = Updater(token=telegram_token)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def font(var, size):
    if var == 'regular':
        return ImageFont.truetype(os.getcwd() + "/fonts/Montserrat-Regular.ttf", size)
    if var == 'bold':
        return ImageFont.truetype(os.getcwd() + "/fonts/Montserrat-Bold.ttf", size)


# Clone the chain-registry, if it's already there, update it.
def get_chain_data():
    global chains
    try:
        Repo.clone_from(chain_registry, (os.getcwd() + "/data/chain-registry"))
        logging.info("[!] Cloned https://github.com/cosmos/chain-registry into ./data")
    except:
        Repo(os.getcwd() + "/data/chain-registry").remotes.origin.pull()
        logging.info("[!] Updated chain-registry data")
    for dirs in os.listdir(os.getcwd() + "/data/chain-registry"):
        if dirs in supported:
            chains.append(dirs)


def check_chain(chain):
    global use_image
    with open(os.getcwd() + "/data/chain-registry/%s/chain.json" % chain, 'r') as chain_file:
        chain = json.load(chain_file)
    try:
        with open(os.getcwd() + '/data/cache/' + chain['chain_name'].lower() + '.json', 'r') as cache_file:
            cache = json.load(cache_file)
    except:
        cache = {"last_notified_proposal": 0,
                 "last_notified_release": "0"}
    try:
        with open(os.getcwd() + '/data/chain-registry/' + chain['chain_name'].lower() + '/assetlist.json', 'r') as assetlist:
            assetlist = json.load(assetlist)
        chain_logo = os.getcwd() + "/data/chain-registry/%s" % assetlist['assets'][0]['logo_URIs']['png'][62:]
    except KeyError:
        chain_logo = False

    try:
        for endpoint in chain['apis']['rest']:
            if "https" in endpoint['address']:
                logging.info("[?] (%s) Trying %s ..." % (chain['chain_name'].upper(), endpoint['address']))
                try:
                    connector = CosmicWrap(lcd=endpoint['address'], rpc='', denom='')
                    proposals = connector.query_proposals()
                    for proposal in proposals:
                        if int(cache['last_notified_proposal']) < int(proposal['proposal_id']):
                            if "SoftwareUpgradeProposal" in proposal['content']['@type'] \
                                    and proposal['status'] == "PROPOSAL_STATUS_VOTING_PERIOD":
                                upgrade_title = proposal['content']['title']
                                upgrade_name = proposal['content']['plan']['name']
                                upgrade_height = proposal['content']['plan']['height']
                                proposal_id = proposal['proposal_id']
                                for explorer in chain['explorers']:
                                    if "mintscan" in explorer['kind']:
                                        explorer_url = explorer['url']
                                        break
                                    else:
                                        explorer_url = explorer['url']
                                logging.info("[!] (%s) - Upgrade %s scheduled for block %s" %
                                             (chain['chain_name'].upper(),
                                              upgrade_name,
                                              upgrade_height))
                                message = "⚠️ <b>NEW SOFTWARE UPGRADE PROPOSAL</b>\n\n" \
                                          "<b>Chain:</b> %s\n" \
                                          "<b>Name:</b> %s\n" \
                                          "<b>Height: </b><a href='%s/blocks/%s'>%s</a>\n\n" \
                                          "🔗 <a href='%s/proposals/%s'>Check Proposal</a>\n" \
                                          % (chain["chain_name"], upgrade_name, explorer_url, upgrade_height,
                                             upgrade_height, explorer_url, proposal_id)

                                for chat_id in telegram_notification:
                                    try:
                                        if use_image is True:
                                            img = Image.new("RGB", (600, 350), (240, 240, 240))
                                            if chain_logo is not False:
                                                logo = Image.open(chain_logo).convert("RGBA")
                                                logo.thumbnail((120, 120))
                                                converted_logo = Image.new("RGBA", (120, 120), (240, 240, 240))
                                                converted_logo.paste(logo, (0, 0), logo)
                                                converted_logo.convert('RGB')
                                                img.paste(converted_logo, (20, 20))
                                            draw = ImageDraw.Draw(img)
                                            draw.text((160, 40), "New Upgrade Proposal",
                                                      (0, 0, 0), font=font('bold', 32))
                                            draw.text((120, 160), "Network: ", (0, 0, 0), font=font('regular', 26))
                                            draw.text((120, 210), "Name: ", (0, 0, 0), font=font('regular', 26))
                                            draw.text((120, 260), "Height: ", (0, 0, 0), font=font('regular', 26))
                                            draw.text((250, 160), chain['chain_name'].upper(), (0, 0, 0),
                                                      font=font('bold', 26))
                                            draw.text((250, 210), upgrade_name, (0, 0, 0),
                                                      font=font('bold', 26))
                                            draw.text((250, 260), upgrade_height, (0, 0, 0),
                                                      font=font('bold', 26))
                                            bio = BytesIO()
                                            bio.name = "output.jpeg"
                                            img.save(bio, "JPEG")
                                            bio.seek(0)
                                            caption = "🔗 <a href='%s/blocks/%s'>Check Upgrade Countdown</a>\n" \
                                                      "⏳ <a href='%s/proposals/%s'>Check GOV Proposal</a>" \
                                                      % (explorer_url, upgrade_height, explorer_url, proposal_id)
                                            telegram.bot.sendPhoto(chat_id=chat_id, photo=bio, caption=caption,
                                                                   parse_mode="HTML")
                                        else:
                                            telegram.bot.sendMessage(chat_id=chat_id,
                                                                     text=message,
                                                                     parse_mode='HTML',
                                                                     disable_web_page_preview=True)
                                        cache['last_notified_proposal'] = proposal_id
                                        with open(os.getcwd() + '/data/cache/' + chain['chain_name'].lower() + '.json',
                                                  'w') as cache_file:
                                            json.dump(cache, cache_file)
                                        sleep(.5)
                                    except Exception as e:
                                        logging.error("[X] Unable to send notification to %s. (%s)" % (chat_id, str(e)))

                    # Checking GitHub Repository
                    repository = g.get_repo(re.sub('.git', '', chain['codebase']['git_repo'][19:].rstrip("/")))
                    releases = repository.get_latest_release()
                    if releases.prerelease is False and cache['last_notified_release'] != releases.tag_name:
                        message = "⚠️<b> NEW GITHUB RELEASE</b>️\n\n" \
                                  "<b>Chain:</b> %s\n" \
                                  "<b>Version:</b> %s\n" \
                                  "<b>Release Date:</b> %s\n\n" \
                                  "🔗 <a href='%s'>Check Release on Github</a>" \
                                  % (chain['chain_name'], str(releases.tag_name),
                                     str(releases.published_at), str(releases.html_url))
                        for chat_id in telegram_notification:
                            try:
                                if use_image is True:
                                    img = Image.new("RGB", (600, 350), (240, 240, 240))
                                    if chain_logo is not False:
                                        logo = Image.open(chain_logo).convert("RGBA")
                                        logo.thumbnail((120, 120))
                                        converted_logo = Image.new("RGBA", (120, 120), (240, 240, 240))
                                        converted_logo.paste(logo, (0, 0), logo)
                                        converted_logo.convert('RGB')
                                        img.paste(converted_logo, (20, 20))
                                    draw = ImageDraw.Draw(img)
                                    draw.text((160, 40), "New GitHub Release",
                                              (0, 0, 0), font=font('bold', 38))
                                    draw.text((120, 160), "Network: ", (0, 0, 0), font=font('regular', 26))
                                    draw.text((120, 210), "Version: ", (0, 0, 0), font=font('regular', 26))
                                    draw.text((120, 260), "Released: ", (0, 0, 0), font=font('regular', 26))
                                    draw.text((250, 160), chain['chain_name'].upper(), (0, 0, 0), font=font('bold', 26))
                                    draw.text((250, 210), str(releases.tag_name), (0, 0, 0), font=font('bold', 26))
                                    draw.text((250, 260), str(releases.published_at) + " UTC", (0, 0, 0), font=font('bold', 26))
                                    bio = BytesIO()
                                    bio.name = "output.jpeg"
                                    img.save(bio, "JPEG")
                                    bio.seek(0)
                                    caption = "🔗 <a href='%s'>Check Release on Github</a>" % str(releases.html_url)
                                    telegram.bot.sendPhoto(chat_id=chat_id, photo=bio, caption=caption, parse_mode="HTML")
                                else:
                                    telegram.bot.sendMessage(chat_id=chat_id,
                                                             text=message,
                                                             parse_mode='HTML',
                                                             disable_web_page_preview=True)
                                sleep(.5)
                                cache['last_notified_release'] = str(releases.tag_name)
                                with open(os.getcwd() + '/data/cache/' + chain['chain_name'].lower() + '.json',
                                          'w') as cache_file:
                                    json.dump(cache, cache_file)
                            except Exception as e:
                                logging.error("[X] Unable to send notification to %s. (%s)" % (chat_id, str(e)))
                                print(str(e))
                        logging.info(
                            "[!] (%s) New version available: %s %s %s" % (
                                chain['chain_name'].upper(), releases.tag_name,
                                releases.published_at, releases.html_url))
                    break
                except Exception as e:
                    logging.error("[X] (%s) ERROR %s" % (chain['chain_name'].upper(), str(e)))
    except Exception as e:
        logging.error("[X] (%s) ERROR %s" % (chain['chain_name'].upper(), str(e)))


get_chain_data()

for chain in chains:
    queue.append(multiprocessing.Process(target=check_chain, args=[chain], daemon=True))

for process in queue:
    process.start()

for process in queue:
    process.join()

