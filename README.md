/r/Hearthstone's Card Bot
==========================

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

Bot's reddit page: http://www.reddit.com/user/HearthstoneCardBot/

Discussion of bot: http://www.reddit.com/r/hearthstone/comments/1ppjab/uhearthstonecardbot/

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

 - Run card_bot.py. It creates a database and a log file on startup. Future runs
   will use the same database and log file. The bot only responds to comments
   made AFTER it has started running.

Source
--------------
Source available at http://github.com/topher200/hearthstone_reddit_card_bot 

