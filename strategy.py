import game, cards, pprint
import enum
from itertools import permutations

# _______________________________________________________________________________________________________
#
# Reading methods                                
# _______________________________________________________________________________________________________

def get_strategies(rule_list, USE_SUB_SETS, PERMUTE):
    """ Return list of strategies (list of lists or permutation objects)
    """

    strategies = [] # a list of lists

    if not USE_SUB_SETS and not PERMUTE:    # just play games with given rule list

        strategies.append(rule_list) 

    elif not USE_SUB_SETS and PERMUTE:      # permute rules in list

        strategies = permutations(rule_list, len(rule_list))

    elif USE_SUB_SETS:
       
        sub_rule_list = []

        for i,_ in enumerate(rule_list):

            sub_rule_list = rule_list[0:i+1] # NOTE: don't use append here since it updates ALL sub sets

            if PERMUTE:
                perms = permutations(sub_rule_list, len(sub_rule_list))
                for p in perms: strategies.append(p)
            else:
                strategies.append(sub_rule_list) # [1,20,300] -> [ [1], [1,20], [1,20,300] ]

    return strategies

def get_rule_str(rule_nr):

    if rule_nr == 1:      rule_str = 'move_ace_from_highest_rank_sum'
    if rule_nr == 2:      rule_str = 'move_ace_suit_below'
    if rule_nr == 3:      rule_str = 'move_ace_from_smallest'
    if rule_nr == 4:      rule_str = 'move_ace_from_largest'
    if rule_nr == 5:      rule_str = 'move_first_ace'

    if rule_nr == 10:     rule_str = 'move_from_smallest_has_higher_in_suit_below'
    if rule_nr == 20:     rule_str = 'move_from_largest_has_higher_in_suit_below'
    
    if rule_nr == 100:    rule_str = 'move_highest_has_higher_in_suit_below'
    if rule_nr == 200:    rule_str = 'move_highest_card'
    if rule_nr == 300:    rule_str = 'move_highest_from_smallest'
    if rule_nr == 400:    rule_str = 'move_highest_from_largest'

    if rule_nr == 1000:   rule_str = 'move_from_highest_rank_sum'

    return rule_str

# _______________________________________________________________________________________________________
#
#  Rules class                              
# _______________________________________________________________________________________________________

class Rules(enum.Enum):

    move_ace_from_highest_rank_sum = 1
    move_ace_suit_below = 2
    move_ace_from_smallest = 3
    move_ace_from_largest = 4
    move_first_ace = 5

    move_from_smallest_has_higher_in_suit_below = 10
    move_from_largest_has_higher_in_suit_below = 20

    move_highest_has_higher_in_suit_below = 100
    move_highest_card = 200
    move_highest_from_smallest = 300
    move_highest_from_largest = 400

    move_from_highest_rank_sum = 1000


RULE_NAMES = {
    Rules.move_ace_from_highest_rank_sum: 'move_ace_from_highest_rank_sum',

}

# _______________________________________________________________________________________________________
#
#  Strategy class                                
# _______________________________________________________________________________________________________

class Strategy:

    def __init__(self, rule_list):
        self.rule_list = rule_list
        self._repr_cache = None
        self._str_cache = None

    # def __repr__(self):
    #     if not self._repr_cache: # TODO: have to iterate over rule_list to get all rule names
    #         self._repr_cache = 'Rule({}, {})'.format(Rules.rule_number, Rules.rule_number)
    #     return self._repr_cache

    # def __str__(self): # TODO: have to iterate over rule_list (rule_number) to get all rule names
    #     if not self._str_cache:
    #         self._str_cache = Rules[rule_number] + RULE_NAMES[rule_number]
    #     return self._str_cache


    def get_rule_funcs(self):
        """ Return move rule functions according to rule_list.
        """
        
        # TODO: use class Rules to match number with function?
        rule_funcs = []

        for rule_func in self.rule_list:

            if rule_func == 1:      rule_funcs.append(self.move_ace_from_highest_rank_sum)
            if rule_func == 2:      rule_funcs.append(self.move_ace_suit_below)
            if rule_func == 3:      rule_funcs.append(self.move_ace_from_smallest)
            if rule_func == 4:      rule_funcs.append(self.move_ace_from_largest)
            if rule_func == 5:      rule_funcs.append(self.move_first_ace)

            if rule_func == 10:     rule_funcs.append(self.move_from_smallest_has_higher_in_suit_below)
            if rule_func == 20:     rule_funcs.append(self.move_from_largest_has_higher_in_suit_below)
            
            if rule_func == 100:    rule_funcs.append(self.move_highest_has_higher_in_suit_below)
            if rule_func == 200:    rule_funcs.append(self.move_highest_card)
            if rule_func == 300:    rule_funcs.append(self.move_highest_from_smallest)
            if rule_func == 400:    rule_funcs.append(self.move_highest_from_largest)

            if rule_func == 1000:   rule_funcs.append(self.move_from_highest_rank_sum)

        return rule_funcs

    # _______________________________________________________________________________________________________
    #
    #  Rule functions                            
    # _______________________________________________________________________________________________________

    ### -------------- Group A --------------  ###

    def move_ace_from_highest_rank_sum(self, curr_game):
        """ Move ace from pile with highest card rank sum.
        """
        
        rule_can_move = False
        rule_str = 'move_ace_from_highest_rank_sum'
        max_sum = 0

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            temp_sum = temp_pile.sum_card_ranks()

            if (temp_pile.length() > 1 and
                temp_pile.last_is_ace() and
                temp_sum > max_sum
                ):

                max_sum = temp_pile.sum_card_ranks()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_ace_suit_below(self, curr_game):
        """ Move the first ace which has card of same suit below.
        """
        
        rule_can_move = False
        rule_str = 'move_ace_suit_below'
        
        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            if (temp_pile.length() > 1 and
                temp_pile.last_is_ace() and
                temp_pile.has_suit_below()):

                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_ace_from_smallest(self, curr_game):
        """ Move from the smallest pile with an ace.
        """
        
        rule_can_move = False
        rule_str = 'move_ace_from_smallest'
        min_pile_length = 100

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            if (temp_pile.last_is_ace() and
                1 < temp_pile.length() < min_pile_length):

                min_pile_length = temp_pile.length()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_ace_from_largest(self, curr_game):
        """ Move from the largest pile with an ace.
        """
        
        rule_can_move = False
        rule_str = 'move_ace_from_largest'
        max_pile_length = 1

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            if (temp_pile.length() > 1 and
                temp_pile.last_is_ace() and
                temp_pile.length() > max_pile_length):

                max_pile_length = temp_pile.length()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_first_ace(self, curr_game):
        """ Move first ace.
        """
        
        rule_can_move = False
        rule_str = 'move_first_ace'
        
        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            if (temp_pile.length() > 1 and
                temp_pile.last_is_ace()):

                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move


    ### -------------- Group B --------------  ###


    def move_from_smallest_has_higher_in_suit_below(self, curr_game):
        """  Move from smallest pile where card has a card of same suit below.
        """
        
        rule_can_move = False
        rule_str = 'move_from_smallest_has_higher_in_suit_below'
        min_pile_length = 100

        for i in range(len(curr_game.piles)):
            
            temp_pile = curr_game.piles[i]
            
            if (1 < temp_pile.length() < min_pile_length and
                temp_pile.below_is_higher() and
                temp_pile.has_suit_below()):

                min_pile_length = curr_game.piles[i].length()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_from_largest_has_higher_in_suit_below(self, curr_game):
        """ Move from largest pile where card has a card of same suit below.
        """

        rule_can_move = False
        rule_str = 'move_from_largest_has_higher_in_suit_below'
        max_pile_length = 1

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            if (temp_pile.length() > max_pile_length and
                temp_pile.below_is_higher() and
                temp_pile.has_suit_below()):

                max_pile_length = temp_pile.length()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move


    ### -------------- Group C --------------  ###


    def move_highest_has_higher_in_suit_below(self, curr_game):
        """ Move highest card from pile where card has a card of same suit below.
        """
        
        rule_can_move = False
        rule_str = 'move_highest_has_higher_in_suit_below'
        max_rank = cards.Rank(0) # JOKER

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]

            if (temp_pile.length() > 1 and
                temp_pile.last_card().rank > max_rank and
                temp_pile.has_suit_below()):

                max_rank = temp_pile.last_card().rank
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_highest_card(self, curr_game):
        """ Move (first) highest card from any pile.
        """
        
        rule_can_move = False
        rule_str = 'move_highest_card'
        max_rank = cards.Rank(0) # JOKER

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]

            if (temp_pile.length() > 1 and
                temp_pile.last_card().rank > max_rank
                ):

                max_rank = temp_pile.last_card().rank
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move

    def move_highest_from_smallest(self, curr_game):
        """ Move highest card from the smallest pile.
        """
        
        rule_can_move = False
        rule_str = 'move_highest_from_smallest'
        min_pile_length = 100
        max_rank = cards.Rank(0) # JOKER

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]

            if (1 < temp_pile.length() <= min_pile_length and
                temp_pile.last_card().rank > max_rank
                ):

                min_pile_length = temp_pile.length()
                max_rank = temp_pile.last_card().rank
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move
        
    def move_highest_from_largest(self, curr_game):
        """ Move highest card from the (first) largest pile.
        """
        
        rule_can_move = False
        rule_str = 'move_highest_from_largest'
        max_pile_length = 1
        max_rank = cards.Rank(0) # JOKER

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]

            if (temp_pile.length() > max_pile_length and
                temp_pile.last_card().rank > max_rank):

                max_pile_length = temp_pile.length()
                max_rank = temp_pile.last_card().rank
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move


    ### -------------- Group D --------------  ###


    def move_from_highest_rank_sum(self, curr_game):
        """ Move from pile with highest card rank sum.
        """
        
        rule_can_move = False
        rule_str = 'move_from_highest_rank_sum'
        max_sum = 0

        for i in range(len(curr_game.piles)):

            temp_pile = curr_game.piles[i]
            temp_sum = temp_pile.sum_card_ranks()
            
            if (temp_pile.length() > 1 and
                temp_sum > max_sum
                ):

                max_sum = temp_pile.sum_card_ranks()
                from_pile = temp_pile
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)
        
        return rule_can_move



# _______________________________________________________________________________________________________
#
#  Strategy rules                                 
# _______________________________________________________________________________________________________
#
# Group A
#  1: ACE_MAX                                     ace from pile with largest card sum;
#  2: ACE_HAS_SUIT_BELOW                          reveal card of same suit; NOTE doesn't guarantee a move
#  3: ACE_FROM_SMALLEST                           ace from smallest pile
#  4: ACE_FROM_LARGEST                            ace from largest pile
#  5: FIRST_ACE                                   ace from first pile
#
# Group B                                         NOTE: B-rules don't guarantee a move
#  10: FROM_SMALLEST_HAS_HIGHER_IN_SUIT_BELOW     reveal higher card of same suit from smallest pile
#  20: FROM_LARGEST_HAS_HIGHER_IN_SUIT_BELOW      reveal higher card of same suit from largest pile
#
# Group C                                         
#  100: HIGHEST_HAS_HIGHER_IN_SUIT_BELOW          highest card which reveals higher card of same suit; NOTE doesn't guarantee a move
#  200: HIGHEST_CARD                              highest card from any pile
#  300: HIGHEST_FROM_SMALLEST                     highest card from smallest pile
#  400: HIGHEST_FROM_LARGEST                      highest card from largest pile
#
# Group D                                         
#  1000: ANY_FROM_MAX_RANK_SUM                    any card from pile with largest card sum


# NOTE: Order of rules in list only matters if PERMUTE is set to False
# NOTE: Duplication of a rule doesn't change the strategy



# _______________________________________________________________________________________________________
#
#  Game options                                 
# _______________________________________________________________________________________________________
#
# Automate testing of various strategies
# Can be used in combination
#
# USE_SUB_SETS    = True      # True: run games for all subsets of rule list
#                             # [1,20,300] -> [ [1], [1,20], [1,20,300] ]
# PERMUTE         = True      # True: run games for all permutations of rules in rule list
#                             # [1,20,300] -> [ [1,20,300], [1,300,20], [300,1,20],
#                             #                  20,1,300], [20,300,1], [300,20,1] etc ]
#
#                             # if USE_SUB_SETS is True: permute all subsets of rule list
#
# For number_of_decks = 1 and n rules:
# 
# USE_SUB_SETS: True  -> n games
# PERMUTE: True       -> n! games
# Both: True          -> n! + (n-1)! + (n-2)! + ... + 1 games (e.g. 8 rules runs 45 512 games)
#

