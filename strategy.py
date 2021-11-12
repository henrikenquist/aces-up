import cards

# _______________________________________________________________________________________________________
#
#  Strategy class                                
# _______________________________________________________________________________________________________

class Strategy:

    def __init__(self, rule_list):
        self.rule_list   = rule_list
        self._repr_cache = None
        self._str_cache  = None

    # def __repr__(self):
    #     if not self._repr_cache: # TODO: have to iterate over rule_list to get all rule names
    #         self._repr_cache = 'Rule({}, {})'.format(Rules.rule_number, Rules.rule_number)
    #     return self._repr_cache

    # def __str__(self): # TODO: have to iterate over rule_list (rule_number) to get all rule names
    #     if not self._str_cache:
    #         self._str_cache = Rules[rule_number] + RULE_NAMES[rule_number]
    #     return self._str_cache

    # _______________________________________________________________________________________________________
    #
    # Read
    # _______________________________________________________________________________________________________

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
    #  Move
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
