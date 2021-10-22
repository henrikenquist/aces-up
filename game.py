import cards, pile, strategy
from itertools import combinations
import time
import pprint                               # https://docs.python.org/3/library/pprint.html

class Game:
    """ Game class.
        Input: deck, rule_list
    """
    
    def __init__(self, deck, rule_list):

        # self.original_shuffled_deck = deck[:]
        self.stack = deck[:]    # copy, not reference; NOTE: the same deck is used for all strategies in aces_up main loop
        self.print_out = ''
        
        self.score = 0
        self.moves = []                     # (card, from_pile, to_pile, rule_str, move_count)
        self.rule_counts = {}               # {fcn_metod__name__: counts}

        self.strategy = strategy.Strategy(rule_list)
        self.rule_funcs = self.strategy.get_rule_funcs()

        self.piles = [ pile.Pile(0), pile.Pile(1), pile.Pile(2), pile.Pile(3) ]
        self.discard_pile = pile.Pile(4)
        self.DISCARD_INDEX = 4              # piles are numbered 0-3, with discard pile as 4
        self.JOKER = cards.Card(0,1)


    def play_game(self, game_nr, deck_nr, start_time, GAME_PRINT_OUT):
        """ Start one game.
        """

        self.print_out = GAME_PRINT_OUT

        while self.stack: # has cards left

            self.deal()         # and discard
            self.run_strategy() # and discard until cannot move again

            # TODO: fix recursive version
            # if RECURSIVE: self.move_rec()
            # else:         self.run_strategy()
        
        # Winning game stats (single game)
        #
        if self.has_won():

            print('-----------------------------------------------------------')
            print(f'Won game nr:    {game_nr}') 
            print(f'Deck nr:        {deck_nr}') 
            print(f'Strategy:       {self.strategy.rule_list}') 
            print(f'Runtime:        {time.time() - start_time:0.2f} s')
            pprint.pprint(self.get_rule_counts())
            print('-----------------------------------------------------------\n')

       
    def run_strategy(self):
        """ Move cards using current strategy (list of rules).
            
            1. Test rules in strategy priority list until one move is made.
            2. Discard all possible cards.
            3. Repeat from 1 until no move can be made.
        """
        
        while self.piles_ok():

            # test all rules in strategy until one move is made
            for i,move_rule_fcn in enumerate(self.rule_funcs):
                # if self.print_out: print(move_rule_fcn.__name__)

                card_is_moved = move_rule_fcn(self) # self here represents curr_game; used in strategy.py as curr_game

                if card_is_moved:

                    self.update_rule_counts(move_rule_fcn.__name__)  
                    break   # return to beginning of rule list (restart for-loop)
                            # i.e. a priority approach to the rule order: a 'strategy'

            if not card_is_moved: return
            # Break while loop if no rule in strategy can move (although a potential move using another rule is possible)


    def piles_ok(self):
        """ Return True if any empty piles and any pile has more than one card
        """

        piles_with_more_cards = [i for i,e, in enumerate(self.piles) if e.length() > 1]
     
        # if self.print_out: 
        #     if any(piles_with_more_cards) and any(self.empty_piles()):
        #         print('Possible piles:', piles_with_more_cards)
        #         print('Empty piles:', self.empty_piles())

        return len(piles_with_more_cards) > 0 and len(self.empty_piles()) > 0


    def move(self, from_pile, rule_str):
        """ Move card to first empty pile and then discard all possible cards.
        """

        slots = self.empty_piles()
        
        card_str = str(from_pile.last_card())
        from_pile_idx = from_pile.index
        to_pile_idx = slots[0]

        self.moves.append([card_str, from_pile_idx, to_pile_idx, rule_str, len(self.moves) + 1])
        self.piles[to_pile_idx].add_card(from_pile.pop_card())

        if self.print_out:
            print(f'RULE:   {rule_str}')
            print(f'CARD:   {card_str}')
            # print(f'FROM:   {from_pile_idx+1} ({from_pile_idx})')
            # print(f'TO:     {to_pile_idx+1} ({to_pile_idx})')
            self.print_current_cards()

        self.discard()


    # # Recursive version
    # def move_rec(self):
    #     ### --------------  Move: Recursive version --------------  ###
    #     ###
    #     ### TODO recursion doesn't work
    #     ### could be because rule_moved_card is referenced, not copied
    #     ### and altered in the move rule functions messing things up
    #     ### in the backtracking

    #     while self.piles_ok():
    #         for _,move_rule_fcn in enumerate(self.rule_funcs):
    #             if not self.piles_ok(): continue

    #             self.card_is_moved = False
    #             self.card_is_moved = move_rule_fcn()
    #             self.nr_fcn_calls += 1

    #         if self.card_is_moved:
    #             self.discard()
    #             self.nr_fcn_moves += 1
    #             old_piles = self.piles[:]   # copy, not reference!
    #             self.move_rec()                 # go deeper i.e. start over with same rule from the beginning
    #             self.piles = old_piles[:]   # backtrack: restore old state

    #     return


    def discard(self): 
        """ Discard all possible cards.
        """

        #
        # TODO: there has to be a more elegant version (which, eg doesn't need JOKERS)
        #
        # # Find high card for each suit
        # high_card_per_suit = dict(zip(self.deck.suit_labels,
        #                               [None] * self.num_piles))
        # https://github.com/jwnorman/aces-up/blob/master/idiots_delight.py


        while True: # has duplicate suit

            curr_cards = self.current_cards() # NOTE: don't mess with this since original index is needed!
            
            # check for suit duplicates, excluding duplicates
            # https://stackoverflow.com/questions/942543/operation-on-every-pair-of-element-in-a-list/37907649
            curr_suits = [e.suit for _,e in enumerate(curr_cards) if e]
            duplicate_suits = [i for i,e in enumerate(curr_suits) if e in curr_suits[:i]]

            if not any(duplicate_suits): break

            # replace [] with JOKER since itertools.combinations can't handle []
            # NOTE: needs the if-else at the beginning of the comprehension
            # https://stackoverflow.com/questions/4260280/if-else-in-a-list-comprehension
            curr_cards = [self.JOKER if not e else e for _,e in enumerate(curr_cards)]

            # Check all combinations of card comparisons (all cards in curr_cards!)
            # print(list(combinations(curr_cards, 2)))

            # NOTE: test zip version to avoid itertools.combinations
            # print(zip(curr_cards, curr_cards[1:] + curr_cards[:1]))
            # for a,b in zip(curr_cards, curr_cards[1:] + curr_cards[:1]):
            for a,b in [ e for _,e in enumerate(list(combinations(curr_cards, 2))) ]:

                if (not a or not b or               # not []
                    a in self.discard_pile.cards or # not already discarded
                    b in self.discard_pile.cards or
                    a.rank == self.JOKER.rank or      # not JOKER
                    b.rank == self.JOKER.rank
                ): continue

                if a.beats(b): # checks rank and suit
                    remove_card = b
                    pile_idx = curr_cards.index(b)
                    if self.print_out: print(a, 'beats', b)

                elif b.beats(a):
                    remove_card = a
                    pile_idx = curr_cards.index(a)
                    if self.print_out: print(b, 'beats', a)
                
                else:
                    pile_idx = -1
                    continue
        
                # print('Discarding from pile:', pile_idx)
                self.moves.append([remove_card, pile_idx, self.DISCARD_INDEX, len(self.moves) + 1]) # (card, from_pile, to_pile, rule_str, move_count)
                self.discard_pile.add_card(self.piles[pile_idx].pop_card())
                if self.print_out: self.print_current_cards()
        

    def deal(self):
        """ Deal new card to each pile and discard all possible cards.
        """
        # print('Cards left', len(self.stack))
        # print('Number of moves', len(self.moves))
        for to_pile in range(len(self.piles)):
            move_count = len(self.moves) + 1
            self.moves.append([self.stack[-1], -1, to_pile, 'deal_from_stack', move_count]) # -1 represents the stack
                            # (card, from_pile, to_pile, rule_str, move_count)
            self.piles[to_pile].add_card(self.stack.pop())

        if self.print_out: print('-----------------------------------------')
        if self.print_out: print('Dealing new cards') 
        if self.print_out: self.print_current_cards()
        if self.print_out: print('-----------------------------------------')

        self.discard()
        
        
    def current_cards(self):
        """ Return last card in each pile. Return [] for each empty pile.
        """
        
        # NOTE: # https://thispointer.com/how-to-create-and-initialize-a-list-of-lists-in-python/
        curr_cards = []
        
        for i in range(len(self.piles)):
            curr_cards.append(self.piles[i].last_card())
        
        return curr_cards


    def print_current_cards(self):
        """ Print last card and pile size for each pile.
        """
        
        for i in range(len(self.piles)):
            print(self.piles[i].last_card(), end = ' ')
        print('   Pile size:', end = ' ')

        for i in range(len(self.piles)):
            print(self.piles[i].length(), end = ' ')
        print('\r')


    def update_rule_counts(self, rule_name):
        """ Increment count for a rule move
        """
        # Increment value. Append rule if not in dictionary
        self.rule_counts[rule_name] = self.rule_counts.get(rule_name,0) + 1


    def get_rule_counts(self):
        """ Return rule counts.
        """
        return self.rule_counts


    def get_moves(self):
        """ Return card moves.
        """
        return self.moves

    
    def get_largest_pile(self, my_list): # largest_idx, largest_pile
        """ Return index and list for largest pile
        """
        return (max(enumerate(my_list), key = lambda tup: len(tup[1])))

       
    def get_deck(self):
        """ Return the original shuffled deck
        """
        return self.original_shuffled_deck


    def get_score(self):
        """ Return score (number of discarded cards).
            48 is a win
        """
        return self.discard_pile.length()


    def has_won(self):
        """ Return True if score is 48.
            Return False if score is not 48.
        """
        return self.get_score() == 48

    
    def empty_piles(self):
        """ Return index for all empty piles
        """
        # NOTE: don't use if [] since it returns [] for empty piles
        # NOTE: Using (if e) or (if e.length() == []) cause problems in other methods, eg piles_ok())
    
        return [i for i,e in enumerate(self.piles) if e.length() == 0]


    