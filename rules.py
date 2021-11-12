import enum

# _______________________________________________________________________________________________________
#
#  Rules class (NB: not in use currently; see TODO in strategy.py)                 
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

RULE_NAMES = {
    Rules.move_ace_from_highest_rank_sum: 'move_ace_from_highest_rank_sum',

}

