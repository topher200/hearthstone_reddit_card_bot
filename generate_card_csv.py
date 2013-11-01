"""Fetches latest card names and links from hearthpwn.

Outputs to cards.csv.
"""
import bs4
import collections
import csv
import httplib2
import logging

import card_bot
import logging_util

# These cards cause too many false positives
BANNED_CARD_LIST = [
  "Archmage",
  "Bananas",
  "Blizzard",
  "Boar",
  "Silence",
  "Charge",
  "Chicken",
  "Claw",
  "DEBUG",
  "Defender",
  "Dream",
  "Dispel",
  "Execute",
  "Flare",
  "Frog",
  "Gnoll",
  "Hyena",
  "Imp",
  "Misdirection",
  "Rampage",
  "Rooted",
  "Sheep",
  "Slam",
  "Swipe",
  "The Coin",
  "Windfury",
  ]


def get_cards_from_page(url):
  logging.info("getting cards from {}".format(url))
  card_dict = {}
  http = httplib2.Http()
  _, response = http.request(url)
  for tr in bs4.BeautifulSoup(response).find_all("tr"):
    td = tr.find('td', {'class': "visual-details-cell"})
    if not td:
      continue
    # The interal site link doesn't include the root url - we add it
    full_link = "http://www.hearthpwn.com{}".format(td.a['href'])
    card_name = td.a.text
    card_dict[card_name] = card_bot.Card(card_name, full_link)
  return card_dict


def main():
  logging_util.setup_logging(verbose=True, filename=None)
  logging.info("Starting generate_card_csv.py")

  # Grab the cards from each page. We're purposely grabbing from more pages than
  # exist. We're using a dict, so grabbing from pages more than once won't dupe
  # cards. We grab from abilities, minions and weapons since we don't want to
  # grab heros or hero powers
  card_dict = {}
  def run_for_card_type(card_type):
    for page_num in range(0, 5):
      url = "http://www.hearthpwn.com/cards/{}?display=2&page={}".format(
        card_type, page_num)
      card_dict.update(get_cards_from_page(url))
  run_for_card_type("ability")
  run_for_card_type("minion")
  run_for_card_type("weapon")
  logging.debug("card dict: {}".format(card_dict))

  if card_dict == {}:
    logging.error("Getting cards failed!")
    return

  logging.debug("removing banned cards")
  for card_name in BANNED_CARD_LIST:
    try:
      card_dict.pop(card_name)
    except KeyError:
      pass

  logging.info("writing cards to file")
  with open("cards.csv", 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    for card in card_dict.values():
      csv_writer.writerow([card.name, card.link])


if __name__ == "__main__":
  main()
