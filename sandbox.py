import solution
import pprint

db_name = 'test_2021-11-01.sqlite'



## Read solutions rule counts from DB
rule_counts = solution.get_rule_counts(db_name)
pprint.pprint(rule_counts)
print(type(rule_counts))
print('\n')
pprint.pprint(dict(rule_counts).keys())
pprint.pprint(dict(rule_counts).values())
print(type(dict(rule_counts)))

