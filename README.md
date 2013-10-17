heathstone_reddit_card_bot
==========================

Listens for card names in reddit.com/r/hearthstone comments and replies with
pictures and a link to the card.

= Files =
 - card_bot.py: The main bot. Runs forever once started. Uses PRAW (python reddit api wrapper).

 - cards.csv: File that contains the list of cards to look for. Contains name of
   card and link to card on hearthpwn.

 - generate_card_csv.py: Fetches list of cards from hearthpwn using beautiful soup.

 - util.py: Shared util functions (logging, etc).

= Source =
Source available at http://github.com/topher200/hearthstone_reddit_card_bot 
