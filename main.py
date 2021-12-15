#!/usr/bin/env python
from src import batch


def main():

    db_name = "aces_up_test.sqlite"
    # db_name = 'aces_up_production.sqlite'

    # Strategy generation
    USE_SUB_SETS = False
    PERMUTE = False
    # Console logging
    STRATEGY_PRINT_OUT = False
    GAME_PRINT_OUT = False

    batch.run(
        [db_name, USE_SUB_SETS, PERMUTE, STRATEGY_PRINT_OUT, GAME_PRINT_OUT]
    )


#  Main entry point
if __name__ == "__main__":
    main()
