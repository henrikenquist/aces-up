import database, helpers
import pprint
import winsound

db_name = 'test_2021-11-02.sqlite'

#### Estimate number of games and total runtime
number_of_decks = 1000
rule_list       = [1,2,3, 10,20, 100, 1000]
PERMUTE         = True
USE_SUB_SETS    = True

n_games, runtime_sec, runtime_str = helpers.get_batch_estimates(db_name, number_of_decks, rule_list, PERMUTE, USE_SUB_SETS)
print('\n')
print(f'Number of games:    {n_games}')
print(f'Estimated runtime:  {runtime_str} ({round(runtime_sec)} s / {1000*runtime_sec/n_games:0.2f} ms)')
print('\n')
# soundfile = "C:/Windows/Media/chimes.wav"
# winsound.PlaySound(soundfile, winsound.SND_FILENAME|winsound.SND_ASYNC)
winsound.Beep(2000, 2000)


#### Get average runtime from DB
# print(database.get_avg_runtime(db_name))


#### Read solutions rule counts from DB
# rule_counts = database.get_rule_counts(db_name)
# print('\n')
# pprint.pprint(rule_counts)
# print(type(rule_counts))
# print('\n')
# pprint.pprint(dict(rule_counts).keys())
# pprint.pprint(dict(rule_counts).values())
# print(type(dict(rule_counts)),'\n')

