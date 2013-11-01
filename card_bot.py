#!/usr/bin/env python
# Tested with python ver 2.7.3 on Windows 7
"""Hearthstone Card Bot

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

Source available at http://github.com/topher200/hearthstone_reddit_card_bot
"""

import anydbm
import csv
import logging
import os
import time
import praw

import util

VERSION = "v0.1"
USER_AGENT = ("Hearthstone Card Bot {} by /u/topher200. "
              "http://github.com:topher200/hearthstone_reddit_card_bot"
              .format(VERSION))
CARD_LIST_CSV = os.path.join(os.path.dirname(__file__), "cards.csv")
DATABASE_FILENAME = "test.db"


def parse_cards_csv():
  """Returns a dict of {card_name: link_to_card}"""
  card_dict = {}
  with open(CARD_LIST_CSV) as f:
    for line in csv.reader(f):
      card_dict[line[0]] = line[1]
  return card_dict


class CardBot(object):
  def __init__(self):
    self.cards_dict = parse_cards_csv()
    self.last_id_processed = None
    self.database = anydbm.open(DATABASE_FILENAME, "c")

  def find_cards_in_comment(self, comment):
    self.last_id_processed = comment.id
    found_cards = []
    for card_name in self.cards_dict:
      if card_name in comment.body:
        found_cards.append(card_name)
    logging.debug("Found {} cards in comment '{}': {}".format(
      len(found_cards), comment.body, found_cards))
    return found_cards

  def get_comments(self, subreddit):
    comments = subreddit.get_comments(place_holder=self.last_id_processed)
    return comments

  def we_have_already_replied(self, comment):
    return self.database.has_key(str(comment.id))

  def record_comment_as_processed(self, comment):
    self.database[str(comment.id)] = "Processed"

  def run(self):
    r = praw.Reddit(user_agent=USER_AGENT)
    r.login()
    hearthstone_subreddit = r.get_subreddit('hearthstone')
    while True:
      last_run_time = time.time()

      logging.info("Getting new comments")
      new_comments = self.get_comments(hearthstone_subreddit)

      logging.info("Printing found cards")
      for comment in new_comments:
        cards_found = self.find_cards_in_comment(comment)
        if not cards_found:
          continue
        if self.we_have_already_replied(comment):
          logging.debug("Skipping comment {}".format(comment))
          continue
        self.record_comment_as_processed(comment)
        for card in cards_found:
          logging.warning("Found card name {} in comment '{}'"
                          .format(card, comment.body))

      logging.info("Sleeping for 15 seconds between runs")
      while (time.time() - last_run_time) < 15:
        time.sleep(.5)


def main():
  util.setup_logging(verbose=True)
  logging.info("Starting card bot")
  card_bot = CardBot()
  card_bot.run()

  # TODO: figure out how to reply to comments


if __name__ == "__main__":
  main()
