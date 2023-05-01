import random
from typing import Callable
from src import cards

# _________________________________________________
#  Strategy class
# _________________________________________________


class Strategy:
    def __init__(self, rule_list: list[int]):
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

    # _________________________________________________
    #
    # Read
    # _________________________________________________

    def get_rule_funcs(self) -> list[Callable]:
        """Return move rule functions according to rule_list."""

        # TODO: use class Rules to match number with function?
        rule_funcs = []

        for rule_func in self.rule_list:
            if rule_func == 0:
                rule_funcs.append(self.move_highest_card)

            if rule_func == 1:
                rule_funcs.append(self.move_highest_has_higher_in_suit_below)
            if rule_func == 2:
                rule_funcs.append(self.move_highest_from_highest_rank_sum)
            if rule_func == 3:
                rule_funcs.append(self.move_highest_from_smallest)
            if rule_func == 4:
                rule_funcs.append(self.move_highest_from_largest)

            if rule_func == 10:
                rule_funcs.append(self.move_lowest_has_higher_in_suit_below)
            if rule_func == 20:
                rule_funcs.append(self.move_lowest_from_highest_rank_sum)
            if rule_func == 30:
                rule_funcs.append(self.move_lowest_from_smallest)
            if rule_func == 40:
                rule_funcs.append(self.move_lowest_from_largest)

            if rule_func == 100:
                rule_funcs.append(self.move_ace_has_suit_below)
            if rule_func == 200:
                rule_funcs.append(self.move_ace_from_highest_rank_sum)
            if rule_func == 300:
                rule_funcs.append(self.move_ace_from_smallest)
            if rule_func == 400:
                rule_funcs.append(self.move_ace_from_largest)
            # if rule_func == 5:
            #     rule_funcs.append(self.move_first_ace)

            if rule_func == 1000:
                rule_funcs.append(self.move_from_random)

            # if rule_func == 10000:
            #     rule_funcs.append(self.move_from_smallest_has_higher_in_suit_below)
            # if rule_func == 20000:
            #     rule_funcs.append(self.move_from_largest_has_higher_in_suit_below)

        return rule_funcs

    # _________________________________________________
    #
    #  Move
    # _________________________________________________

    ### -------------- DEFAULT --------------  ###

    def move_highest_card(self, curr_game) -> bool:
        """Move (first) highest card from any pile."""

        rule_can_move = False
        rule_str = "move_highest_card"
        max_rank = cards.Rank(0)  # JOKER

        for _, pile_iter in enumerate(curr_game.piles):
            if pile_iter.length() > 1 and pile_iter.last_card().rank > max_rank:
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    ### -------------- HIGHEST --------------  ###

    def move_highest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move highest card from pile where card has a card of same suit below."""

        rule_can_move = False
        rule_str = "move_highest_has_higher_in_suit_below"
        max_rank = cards.Rank(0)  # JOKER

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_card().rank > max_rank
                and pile_iter.has_suit_below()
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_highest_from_highest_rank_sum(self, curr_game) -> bool:
        """Move from pile with highest card rank sum."""

        rule_can_move = False
        rule_str = "move_highest_from_highest_rank_sum"
        max_rank = cards.Rank(0)  # JOKER
        max_rank_sum = max(p.sum_card_ranks() for p in curr_game.piles)

        for _, pile_iter in enumerate(curr_game.piles):
            temp_sum = pile_iter.sum_card_ranks()

            if (
                pile_iter.length() > 1
                and temp_sum == max_rank_sum
                and pile_iter.last_card().rank > max_rank
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_highest_from_smallest(self, curr_game) -> bool:
        """Move highest card from the smallest pile."""

        rule_can_move = False
        rule_str = "move_highest_from_smallest"
        # min_pile_length = 100
        min_pile_length = min(p.length() for p in curr_game.piles)
        if min_pile_length < 2:
            min_pile_length = 2
        max_rank = cards.Rank(0)  # JOKER

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == min_pile_length
                and pile_iter.last_card().rank > max_rank
            ):
                min_pile_length = pile_iter.length()
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_highest_from_largest(self, curr_game) -> bool:
        """Move highest card from the (first) largest pile."""

        rule_can_move = False
        rule_str = "move_highest_from_largest"
        max_pile_length = max(p.length() for p in curr_game.piles)
        max_rank = cards.Rank(0)  # JOKER

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == max_pile_length
                and pile_iter.last_card().rank > max_rank
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    ### -------------- LOWEST --------------  ###
    def move_lowest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move lowest card from pile where card has a card of same suit below."""

        rule_can_move = False
        rule_str = "move_lowest_has_higher_in_suit_below"
        max_rank = cards.Rank(14)  # ACE

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_card().rank < max_rank
                and pile_iter.has_suit_below()
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_lowest_from_highest_rank_sum(self, curr_game) -> bool:
        """Move lowest card from pile with lowest card rank sum."""

        rule_can_move = False
        rule_str = "move_lowest_from_highest_rank_sum"
        max_rank = cards.Rank(14)  # ACE
        max_rank_sum = max(p.sum_card_ranks() for p in curr_game.piles)

        for _, pile_iter in enumerate(curr_game.piles):
            temp_sum = pile_iter.sum_card_ranks()

            if (
                pile_iter.length() > 1
                and temp_sum == max_rank_sum
                and pile_iter.last_card().rank < max_rank
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_lowest_from_smallest(self, curr_game) -> bool:
        """Move lowest card from the smallest pile."""

        rule_can_move = False
        rule_str = "move_lowest_from_smallest"
        min_pile_length = min(p.length() for p in curr_game.piles)
        if min_pile_length < 2:
            min_pile_length = 2
        max_rank = cards.Rank(14)  # ACE

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == min_pile_length
                and pile_iter.last_card().rank < max_rank
            ):
                min_pile_length = pile_iter.length()
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_lowest_from_largest(self, curr_game) -> bool:
        """Move lowest card from the (first) largest pile."""

        rule_can_move = False
        rule_str = "move_lowest_from_largest"
        max_pile_length = max(p.length() for p in curr_game.piles)
        max_rank = cards.Rank(14)  # ACE

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == max_pile_length
                and pile_iter.last_card().rank < max_rank
            ):
                max_rank = pile_iter.last_card().rank
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    ### -------------- ACE --------------  ###

    def move_ace_from_highest_rank_sum(self, curr_game) -> bool:
        """Move ace from pile with highest card rank sum."""

        rule_can_move = False
        rule_str = "move_ace_from_highest_rank_sum"
        max_sum = 0

        for _, pile_iter in enumerate(curr_game.piles):
            temp_sum = pile_iter.sum_card_ranks()

            if (
                pile_iter.length() > 1
                and pile_iter.last_is_ace()
                and temp_sum > max_sum
            ):
                max_sum = pile_iter.sum_card_ranks()
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_ace_has_suit_below(self, curr_game) -> bool:
        """Move the first ace which has card of same suit below."""

        rule_can_move = False
        rule_str = "move_ace_has_suit_below"

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_is_ace()
                and pile_iter.has_suit_below()
            ):
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_ace_from_smallest(self, curr_game) -> bool:
        """Move from the smallest pile with an ace."""

        rule_can_move = False
        rule_str = "move_ace_from_smallest"
        min_pile_length = 100

        for _, pile_iter in enumerate(curr_game.piles):
            if pile_iter.last_is_ace() and 1 < pile_iter.length() < min_pile_length:
                min_pile_length = pile_iter.length()
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_ace_from_largest(self, curr_game) -> bool:
        """Move from the largest pile with an ace."""

        rule_can_move = False
        rule_str = "move_ace_from_largest"
        max_pile_length = 1

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_is_ace()
                and pile_iter.length() > max_pile_length
            ):
                max_pile_length = pile_iter.length()
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_first_ace(self, curr_game) -> bool:
        """Move first ace."""

        rule_can_move = False
        rule_str = "move_first_ace"

        for _, pile_iter in enumerate(curr_game.piles):
            if pile_iter.length() > 1 and pile_iter.last_is_ace():
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    ### -------------- RANDOM --------------  ###

    def move_from_random(self, curr_game) -> bool:
        """Move from random pile"""

        rule_can_move = False
        rule_str = "move_from_random"
        candidates = [i for i, p in enumerate(curr_game.piles) if p.length() > 1]
        if candidates:
            rule_can_move = True
            from_pile = curr_game.piles[random.choice(candidates)]
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    ### -------------- NOT IN USE --------------  ###

    def move_from_smallest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move from smallest pile where card has a card of same suit below."""

        rule_can_move = False
        rule_str = "move_from_smallest_has_higher_in_suit_below"
        min_pile_length = 100

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() < min_pile_length
                and pile_iter.below_is_higher()
                and pile_iter.has_suit_below()
            ):
                min_pile_length = pile_iter.length()
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move

    def move_from_largest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move from largest pile where card has a card of same suit below."""

        rule_can_move = False
        rule_str = "move_from_largest_has_higher_in_suit_below"
        max_pile_length = 1

        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > max_pile_length
                and pile_iter.below_is_higher()
                and pile_iter.has_suit_below()
            ):
                max_pile_length = pile_iter.length()
                from_pile = pile_iter
                rule_can_move = True

        if rule_can_move:
            curr_game.move(from_pile, rule_str)

        return rule_can_move
