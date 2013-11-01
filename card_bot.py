#!/usr/bin/env python
# Tested with python ver 2.7.3 on Windows 7
"""Hearthstone Card Bot

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

Source available at http://github.com/topher200/hearthstone_reddit_card_bot
"""

from __future__ import unicode_literals

import anydbm
import csv
import logging
import os
import praw
import sys
import time

import logging_util

VERSION = "v0.1"
USER_AGENT = ("Hearthstone Card Bot {} by /u/topher200. "
              "http://github.com:topher200/hearthstone_reddit_card_bot"
              .format(VERSION))
CARD_LIST_CSV_FILENAME = os.path.join(os.path.dirname(__file__), "cards.csv")
DATABASE_FILENAME = "processed_cards.db"
# As recommended by reddit api docs
SLEEP_TIME_BETWEEN_RUNS = 30  # seconds


def parse_cards_csv():
  """Returns a dict of {card_name: link_to_card}"""
  card_dict = {}
  with open(CARD_LIST_CSV_FILENAME) as f:
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
    try:
      comments = subreddit.get_comments(place_holder=self.last_id_processed)
    except praw.errors.APIException:
      logging.warning("Error on get_comments: {},{}".
                      format(sys.exc_info()[0], (sys.exc_info()[1])))
      return []
    # Take out comments by me
    comments_from_everyone_else = [c for c in comments
                                   if c.author.name != u'HearthstoneCardBot']
    return comments_from_everyone_else

  def we_have_already_replied(self, comment):
    return self.database.has_key(str(comment.id))

  def record_comment_as_processed(self, comment):
    self.database[str(comment.id)] = "Processed"

  def _submission_card_hash(self, card_name, submission):
    # We add a hash key of submission_id and card to the database as a key
    return str("sub{}_card{}".format(submission.id, card_name))

  def we_already_posted_card_in_submission(self, card_name, submission):
    hash = self._submission_card_hash(card_name, submission)
    return self.database.has_key(hash)

  def record_posting_card_to_submission(self, card_name, submission):
    hash = self._submission_card_hash(card_name, submission)
    self.database[hash] = "Posted"

  def reply_to_comment(self, comment, cards_found):
    # Cull cards we've already posted. Record that we're posting new ones
    cards_to_post = []
    for card_name in cards_found:
      if self.we_already_posted_card_in_submission(card_name,
                                                   comment.submission):
        logging.info("Skipping {} since we already posted it in {}"
                     .format(card_name, comment.submission))
      else:
        self.record_posting_card_to_submission(card_name, comment.submission)
        cards_to_post.append(card_name)

    # Create reply text
    card_reply_texts = []
    for card_name in cards_found:
      card_reply_texts.append("[{}]({})".format(
        card_name, self.cards_dict[card_name]))
    reply = " | ".join(card_reply_texts)

    # Post reply to reddit
    try:
      comment.reply(reply)
    except praw.errors.APIException:
      logging.warning("Error on reply: {},{}".
                      format(sys.exc_info()[0], (sys.exc_info()[1])))

  def run(self):
    r = praw.Reddit(user_agent=USER_AGENT)
    r.login()
    hearthstone_subreddit = r.get_subreddit('hearthstone')

    logging.debug("Querying for latest comment id")
    for comment in self.get_comments(hearthstone_subreddit):
      self.last_id_processed = comment.id

    while True:
      last_run_time = time.time()

      logging.debug("Getting new comments")
      new_comments = self.get_comments(hearthstone_subreddit)

      logging.debug("Printing found cards")
      for comment in new_comments:
        cards_found = self.find_cards_in_comment(comment)
        if not cards_found:
          continue
        if self.we_have_already_replied(comment):
          logging.debug("Already replied to comment {}".format(comment))
          continue

        logging.info("Responding to comment {}".format(comment))
        self.record_comment_as_processed(comment)
        self.reply_to_comment(comment, cards_found)

      logging.debug("Sleeping for {} seconds between runs".
                    format(SLEEP_TIME_BETWEEN_RUNS))
      while (time.time() - last_run_time) < SLEEP_TIME_BETWEEN_RUNS:
        time.sleep(.5)


def main():
  logging_util.setup_logging(verbose=False)
  logging.info("Starting card bot")
  card_bot = CardBot()
  card_bot.run()


if __name__ == "__main__":
  main()
