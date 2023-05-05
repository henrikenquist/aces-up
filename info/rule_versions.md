# Aces Up - Rule versioning

## Want more rules in your life?

Implement one marked by \* below using the existing code in `strategy.py`. That's easy.

... or be creative and invent one of your own!

Don't forget to send me a pull request when you're done 😄

| < v2 | v2.3 | v2.4 | v2.x | description (* not implemented yet)                      |
| ---- | ---- | ---- | ---- | -------------------------------------------------------- |
| -    | -    | -    |      | ace (from random pile if more than one) *                |
| 1    | 200  | 200  |      | ace from pile with largest card sum                      |
| 3    | 300  | 300  |      | ace from smallest pile                                   |
| 4    | 400  | 400  |      | ace from largest pile                                    |
| -    | -    | -    |      | highest card has ace below *                             |
| 200  | 0    | 0    |      | highest card from any pile                               |
| 1000 | 2    | 2    |      | highest card from pile with largest card sum             |
| -    | 3    | 3    |      | highest card from smallest pile                          |
| -    | 4    | 4    |      | highest card from largest pile                           |
| -    | -    | -    |      | lowest card has ace below *                              |
| -    | -    | -    |      | lowest card  (from random pile if more than one) *       |
| -    | 20   | 20   |      | lowest card from pile with largest card sum              |
| -    | 30   | 30   |      | lowest card from smallest pile                           |
| -    | 40   | 40   |      | lowest card from largest pile                            |
| 2    | 100  | 100  |      | ace with card of same suit below                         |
| -    | -    | -    |      | highest card has ace of same suit below *                |
| 100  | 1    | 1    |      | highest card with card of same suit below                |
| -    | -    | -    |      | lowest card has ace of same suit below *                 |
| -    | 10   | 10   |      | lowest card with card of same suit below                 |
| -    | -    | -    |      | highest card over a certain rank, otherwise no move *    |
| 10   | -    | 800  |      | from smallest pile with a higher card of same suit below |
| -    | -    | 810  |      | from smallest pile with a lower card of same suit below  |
| 20   | -    | 900  |      | from largest pile with higher card of same suit below    |
| -    | -    | 910  |      | from largest pile with lower card of same suit below     |
| -    | 1000 | 1000 |      | from random pile                                         |
|      |      |      |      |                                                          |

Regarding the naming convention: Yes, it's not perfect - but it works!

## An alternative

An idea I had, tried, and abandoned since I had to make the fundamentals work first.

-> Name rules according to the chaining concept "card-pile-suit":

An example (might be messed up due to editing above, but you get the idea)
"move the highest possible card from one of the smallest piles" = 220
"move an ace if it has a card of same suit below" = 101
"move random card" = 400
"move card from one of the smallest piles if it has a card of same suit below" = 021

first digit:	card type		0 (not specified), 1 (ace), 2 (highest), 3 (lowest), 4 (random)
second digit:	pile type		0 (not specified), 1 (largest), 2 (smallest), 3 (max card sum), 4 (random)
third digit:	suit below		0 (not specified), 1 (suit below)

It is then possible to tag new concepts x and y to the end of the rule code: 203xy

How to present this to the user? A complete table? Messy!
