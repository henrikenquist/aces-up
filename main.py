#!/usr/bin/env python
from aces_up import main

#  Batch settings (see readme.txt)

db_name = 'aces_up_test.sqlite'
# db_name = 'aces_up_production.sqlite'

USE_SUB_SETS        = False
PERMUTE             = False
STRATEGY_PRINT_OUT  = False
GAME_PRINT_OUT      = False

#  Main entry point
main([db_name, USE_SUB_SETS, PERMUTE, STRATEGY_PRINT_OUT, GAME_PRINT_OUT])