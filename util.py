"""Shared util functions"""

import logging
import logging.handlers
import sys

def setup_logging(verbose):
  logging.root.setLevel(logging.NOTSET)

  if verbose:
    level = logging.DEBUG
  else:
    level = logging.INFO

  formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

  file_handler = logging.handlers.RotatingFileHandler("log")
  file_handler.setFormatter(formatter)
  file_handler.setLevel(logging.DEBUG)
  logging.root.addHandler(file_handler)

  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(formatter)
  console_handler.setLevel(level)
  logging.root.addHandler(console_handler)
