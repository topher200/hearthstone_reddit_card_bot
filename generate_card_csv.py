"""Fetches latest card names and links from hearthpwn.

Outputs to cards.csv.
"""
import bs4
import collections
import csv
import httplib2
import logging

import logging_util

# These cards cause too many false positives
BANNED_CARD_LIST = [
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
  card_dict = collections.OrderedDict()
  http = httplib2.Http()
  _, response = http.request(url)
  for link in bs4.BeautifulSoup(response, parse_only=bs4.SoupStrainer('a')):
    if link.has_attr("href") and link.has_attr("data-id"):
      # The interal site link doesn't include the root url - we add it
      full_link = "http://www.hearthpwn.com{}".format(link['href'])
      card_dict[link.text] = full_link
  return card_dict


def main():
  logging_util.setup_logging(verbose=False, filename=None)
  logging.info("Starting generate_card_csv.py")

  # Grab the cards from each page. We're purposely grabbing from more pages than
  # exist. We're using a dict, so grabbing from pages more than once won't dupe
  # cards. We grab from abilities, minions and weapons since we don't want to
  # grab heros or hero powers
  card_dict = collections.OrderedDict()
  for page_num in range(0, 5):
    url = "http://www.hearthpwn.com/cards/ability?display=1&page={}".format(
      page_num)
    card_dict.update(get_cards_from_page(url))
  for page_num in range(0, 5):
    url = "http://www.hearthpwn.com/cards/minion?display=1&page={}".format(
      page_num)
    card_dict.update(get_cards_from_page(url))
  for page_num in range(0, 5):
    url = "http://www.hearthpwn.com/cards/weapon?display=1&page={}".format(
      page_num)
    card_dict.update(get_cards_from_page(url))
  logging.debug("card dict: {}".format(card_dict))

  logging.debug("removing banned cards")
  for card in BANNED_CARD_LIST:
    card_dict.pop(card)

  logging.info("writing cards to file")
  with open("cards.csv", 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    for card in card_dict:
      csv_writer.writerow([card, card_dict[card]])


if __name__ == "__main__":
  main()
