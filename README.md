/r/Hearthstone's Card Bot
==========================

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

Files
--------------
 - card_bot.py: The main bot. Runs forever once started. Uses PRAW (python reddit api wrapper).

 - cards.csv: File that contains the list of cards to look for. Contains name of
   card and link to card on hearthpwn.

 - generate_card_csv.py: Fetches list of cards from hearthpwn using beautiful soup.

 - logging_util.py: Logging util functions

Requirements for running
--------------
 - You must create a praw.ini with PRAW login information. See
   https://praw.readthedocs.org/en/latest/pages/configuration_files.html#example-praw-ini-file
   for an example.

Source
--------------
Source available at http://github.com/topher200/hearthstone_reddit_card_bot 

Links on reddit
--------------
Bot's comment page: http://www.reddit.com/user/HearthstoneCardBot/
Discussion on bot: http://www.reddit.com/r/hearthstone/comments/1ppjab/uhearthstonecardbot/

