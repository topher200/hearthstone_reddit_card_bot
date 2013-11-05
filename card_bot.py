#!/usr/bin/env python
# Tested with python ver 2.7.3 on Windows 7
"""Hearthstone Card Bot

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

Source available at http://github.com/topher200/hearthstone_reddit_card_bot
"""

from __future__ import unicode_literals

import anydbm
import argparse
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


class Card(object):
  def __init__(self, name, card_page_link, image_link):
    self.name = name
    self.card_page_link = card_page_link
    self.image_link = image_link

  def superscripted_name(self):
    # Add superscript after teach space
    name = self.name.replace(" ", " ^")
    # Add a superscript to the front of the text
    return "^{}".format(name)

  def generate_markdown_formatted_link(self):
    """Create a reddit-ready link with card text and image link"""
    return "[{}]({})^\([img]({})\)" .format(
      self.superscripted_name(), self.card_page_link, self.image_link)


def parse_cards_csv():
  """Returns a list of Cards"""
  cards = []
  with open(CARD_LIST_CSV_FILENAME) as f:
    for line in csv.reader(f):
      cards.append(Card(line[0], line[1], line[2]))
  return cards


class CardBot(object):
  def __init__(self, subreddit):
    self.cards = parse_cards_csv()
    self.last_id_processed = None
    self.database = anydbm.open(DATABASE_FILENAME, "c")
    self.subreddit = subreddit

  def find_cards_in_comment(self, comment):
    self.last_id_processed = comment.id
    found_cards = []
    for card in self.cards:
      if card.name in comment.body:
        found_cards.append(card)
    logging.debug("Found {} cards in comment '{}': {}".format(
      len(found_cards), comment.body, [c.name for c in found_cards]))
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

  def _submission_card_hash(self, card, submission):
    # We add a hash key of submission_id and card_name to the database as a key
    return str("sub{}_card{}".format(submission.id, card.name))

  def we_already_posted_card_in_submission(self, card, submission):
    hash = self._submission_card_hash(card, submission)
    return self.database.has_key(hash)

  def record_posting_card_to_submission(self, card, submission):
    hash = self._submission_card_hash(card, submission)
    self.database[hash] = "Posted"

  def reply_to_comment(self, comment, cards_found):
    # Cull cards we've already posted. Record that we're posting the new ones
    cards_to_post = []
    for card in cards_found:
      if self.we_already_posted_card_in_submission(card, comment.submission):
        logging.info("Skipping '{}' since we already posted it in {}"
                     .format(card.name, comment.submission))
      else:
        self.record_posting_card_to_submission(card, comment.submission)
        cards_to_post.append(card)
    if len(cards_to_post) == 0:
      logging.info("No need to post: already got all the cards!")
      return

    # Create reply text
    card_texts = []
    for card in cards_found:
      card_texts.append(card.generate_markdown_formatted_link())
    reply = " ^| ".join(card_texts)

    # Post reply to reddit
    try:
      comment.reply(reply)
    except praw.errors.APIException:
      logging.warning("Error on reply: {},{}".
                      format(sys.exc_info()[0], (sys.exc_info()[1])))

  def run(self):
    r = praw.Reddit(user_agent=USER_AGENT)
    r.login()
    hearthstone_subreddit = r.get_subreddit(self.subreddit)

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
          logging.debug("Already replied to comment '{}'".format(comment))
          continue

        logging.info("Responding to comment '{}'".format(comment))
        self.record_comment_as_processed(comment)
        self.reply_to_comment(comment, cards_found)

      logging.debug("Sleeping for {} seconds between runs".
                    format(SLEEP_TIME_BETWEEN_RUNS))
      while (time.time() - last_run_time) < SLEEP_TIME_BETWEEN_RUNS:
        time.sleep(.5)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--test', action='store_true',
                      help="Monitor /r/test instead of /r/hearthstone")
  parser.add_argument('-v', '--verbose', action='store_true',
                      help="Output debug logs")
  args = parser.parse_args()

  logging_util.setup_logging(verbose=args.verbose, filename="log")
  logging.info("Starting card bot")

  if args.test:
    subreddit = "test"
  else:
    subreddit = "hearthstone"
  logging.debug("Monitoring /r/{}".format(subreddit))

  card_bot = CardBot(subreddit)
  card_bot.run()


if __name__ == "__main__":
  main()
