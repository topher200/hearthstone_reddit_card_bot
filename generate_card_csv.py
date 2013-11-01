"""Fetches latest card names and links from hearthpwn.

Outputs to cards.csv.
"""
import bs4
import collections
import csv
import httplib2
import logging

import util

BANNED_CARD_LIST = [
  "Blizzard",
  ]

def get_cards_from_page(url):
  logging.info("getting cards from {}".format(url))
  card_dict = collections.OrderedDict()
  http = httplib2.Http()
  _, response = http.request(url)
  for link in bs4.BeautifulSoup(response, parse_only=bs4.SoupStrainer('a')):
    if link.has_attr("href") and link.has_attr("data-id"):
      card_dict[link.text] = link['href']
  return card_dict


def main():
  util.setup_logging(verbose=False)
  logging.info("Starting generate_card_csv.py")

  # Grab the cards from each page. We're purposely grabbing from more pages
  # than exist. We're using a dict, so grabbing from pages more than once
  # won't dupe cards.
  card_dict = collections.OrderedDict()
  for page_num in range(0, 10):
    url = "http://www.hearthpwn.com/cards?display=1&page={}".format(page_num)
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
