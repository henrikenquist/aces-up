import random
import inspect
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

            if rule_func == 800:
                rule_funcs.append(self.move_from_smallest_has_higher_in_suit_below)
            if rule_func == 810:
                rule_funcs.append(self.move_from_smallest_has_lower_in_suit_below)
            if rule_func == 900:
                rule_funcs.append(self.move_from_largest_has_higher_in_suit_below)
            if rule_func == 910:
                rule_funcs.append(self.move_from_largest_has_lower_in_suit_below)

            if rule_func == 1000:
                rule_funcs.append(self.move_from_random)

        return rule_funcs

    # _________________________________________________
    #
    #  Move
    # _________________________________________________

    ### -------------- DEFAULT --------------  ###

    def move_highest_card(self, curr_game) -> bool:
        """Move (first) highest card from any pile."""

        from_pile = None
        max_rank = cards.Rank(0)  # JOKER
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_card.rank > max_rank
            ):
                from_pile = pile_iter
                max_rank = pile_iter.last_card.rank

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    ### -------------- HIGHEST --------------  ###

    def move_highest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move highest card from pile where card has a card of same suit below."""

        from_pile = None
        max_rank = cards.Rank(0)  # JOKER
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_card.rank > max_rank
                and pile_iter.has_suit_below()
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_highest_from_highest_rank_sum(self, curr_game) -> bool:
        """Move from pile with highest card rank sum."""

        from_pile = None
        max_rank = cards.Rank(0)  # JOKER
        max_rank_sum = max(p.sum_card_ranks() for p in curr_game.piles)
        for _, pile_iter in enumerate(curr_game.piles):
            temp_sum = pile_iter.sum_card_ranks()

            if (
                pile_iter.length() > 1
                and temp_sum == max_rank_sum
                and pile_iter.last_card.rank > max_rank
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_highest_from_smallest(self, curr_game) -> bool:
        """Move highest card from the smallest pile."""

        from_pile = None
        min_pile_length = min(p.length() for p in curr_game.piles)
        if min_pile_length < 2:
            return False
        max_rank = cards.Rank(0)  # JOKER
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == min_pile_length
                and pile_iter.last_card.rank > max_rank
            ):
                min_pile_length = pile_iter.length()
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_highest_from_largest(self, curr_game) -> bool:
        """Move highest card from the (first) largest pile."""

        from_pile = None
        max_pile_length = max(p.length() for p in curr_game.piles)
        max_rank = cards.Rank(0)  # JOKER
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == max_pile_length
                and pile_iter.last_card.rank > max_rank
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    ### -------------- LOWEST --------------  ###

    def move_lowest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move lowest card from pile where card has a card of same suit below."""

        from_pile = None
        max_rank = cards.Rank(14)  # ACE
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_card.rank < max_rank
                and pile_iter.has_suit_below()
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_lowest_from_highest_rank_sum(self, curr_game) -> bool:
        """Move lowest card from pile with lowest card rank sum."""

        from_pile = None
        max_rank = cards.Rank(14)  # ACE
        max_rank_sum = max(p.sum_card_ranks() for p in curr_game.piles)
        for _, pile_iter in enumerate(curr_game.piles):
            temp_sum = pile_iter.sum_card_ranks()

            if (
                pile_iter.length() > 1
                and temp_sum == max_rank_sum
                and pile_iter.last_card.rank < max_rank
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_lowest_from_smallest(self, curr_game) -> bool:
        """Move lowest card from the smallest pile."""

        from_pile = None
        min_pile_length = min(p.length() for p in curr_game.piles)
        if min_pile_length < 2:
            return False
        max_rank = cards.Rank(14)  # ACE
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() == min_pile_length
                and pile_iter.last_card.rank < max_rank
            ):
                min_pile_length = pile_iter.length()
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_lowest_from_largest(self, curr_game) -> bool:
        """Move lowest card from the (first) largest pile."""

        from_pile = None
        max_pile_length, _ = curr_game.max_pile_length
        max_rank = cards.Rank(14)  # ACE
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() == max_pile_length
                and pile_iter.last_card.rank < max_rank
            ):
                max_rank = pile_iter.last_card.rank
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    ### -------------- ACE --------------  ###

    def move_ace_from_highest_rank_sum(self, curr_game) -> bool:
        """Move ace from pile with highest card rank sum."""

        from_pile = None
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

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_ace_has_suit_below(self, curr_game) -> bool:
        """Move the first ace which has card of same suit below."""

        from_pile = None
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_is_ace()
                and pile_iter.has_suit_below()
            ):
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_ace_from_smallest(self, curr_game) -> bool:
        """Move from the smallest pile with an ace."""

        from_pile = None
        min_pile_length = 100
        for _, pile_iter in enumerate(curr_game.piles):
            if pile_iter.last_is_ace() and 1 < pile_iter.length() < min_pile_length:
                min_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_ace_from_largest(self, curr_game) -> bool:
        """Move from the largest pile with an ace."""

        from_pile = None
        max_pile_length = 1
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > 1
                and pile_iter.last_is_ace()
                and pile_iter.length() > max_pile_length
            ):
                max_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_first_ace(self, curr_game) -> bool:
        """Move first ace."""

        from_pile = None
        for _, pile_iter in enumerate(curr_game.piles):
            if pile_iter.length() > 1 and pile_iter.last_is_ace():
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    ### -------------- RANDOM --------------  ###

    def move_from_random(self, curr_game) -> bool:
        """Move from random pile"""

        from_pile = None
        candidates = [i for i, p in enumerate(curr_game.piles) if p.length() > 1]
        if candidates:
            from_pile = curr_game.piles[random.choice(candidates)]

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    ### -------------- PILE SIZE AND SUIT BELOW --------------  ###

    def move_from_smallest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move from smallest pile where card has a higher card of same suit below."""

        from_pile = None
        min_pile_length = 100
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() < min_pile_length
                and pile_iter.below_is_higher()
                and pile_iter.has_suit_below()
            ):
                min_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_from_smallest_has_lower_in_suit_below(self, curr_game) -> bool:
        """Move from smallest pile where card has a lower card of same suit below."""

        from_pile = None
        min_pile_length = 100
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                1 < pile_iter.length() < min_pile_length
                and pile_iter.below_is_lower()
                and pile_iter.has_suit_below()
            ):
                min_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_from_largest_has_higher_in_suit_below(self, curr_game) -> bool:
        """Move from largest pile where card has a higher card of same suit below."""

        from_pile = None
        max_pile_length = 1
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > max_pile_length
                and pile_iter.below_is_higher()
                and pile_iter.has_suit_below()
            ):
                max_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True

    def move_from_largest_has_lower_in_suit_below(self, curr_game) -> bool:
        """Move from largest pile where card has a lower card of same suit below."""

        from_pile = None
        max_pile_length = 1
        for _, pile_iter in enumerate(curr_game.piles):
            if (
                pile_iter.length() > max_pile_length
                and pile_iter.below_is_lower()
                and pile_iter.has_suit_below()
            ):
                max_pile_length = pile_iter.length()
                from_pile = pile_iter

        if from_pile is None:
            return False
        curr_game.move(from_pile, inspect.currentframe().f_code.co_name)
        return True
