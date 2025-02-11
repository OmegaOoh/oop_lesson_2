import csv
import os
import copy

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

cities = []
with open(os.path.join(__location__, 'Cities.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        cities.append(dict(r))

countries = []
with open(os.path.join(__location__, 'Countries.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        countries.append(dict(r))

players = []
with open(os.path.join(__location__, 'Players.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        players.append(dict(r))

teams = []
with open(os.path.join(__location__, 'Teams.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        teams.append(dict(r))

titanic = []
with open(os.path.join(__location__, 'Titanic.csv')) as f:
    rows = csv.DictReader(f)
    for r in rows:
        titanic.append(dict(r))


class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None


class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def __is_float(self, element):
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table

    def aggregate(self, function, aggregation_key):
        temps = []
        for item1 in self.table:
            if self.__is_float(item1[aggregation_key]):
                temps.append(float(item1[aggregation_key]))
            else:
                temps.append(item1[aggregation_key])
        return function(temps)

    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def pivot_table(self, keys_to_pivot_list, keys_to_aggregate_list, aggregate_func_list):

        # First create a list of unique values for each key
        unique_values_list = []
        for i in keys_to_pivot_list:
            temp_unique_val = []
            temp_table = self.select(i)
            for j in temp_table:
                if not j[i] in temp_unique_val:
                    temp_unique_val.append(j[i])
            unique_values_list.append(temp_unique_val)

        # Here is an example of of unique_values_list for
        # keys_to_pivot_list = ['embarked', 'gender', 'class']
        # unique_values_list =
        # [['Southampton', 'Cherbourg', 'Queenstown'], ['M', 'F'], ['3', '2','1']]
        # Get the combination of unique_values_list
        # You will make use of the function you implemented in Task 2

        import combination_gen
        comb_list = combination_gen.gen_comb_list(unique_values_list)

        # Example output:
        # [['Southampton', 'M', '3'],
        #  ['Cherbourg', 'M', '3'],
        #  ...
        #  ['Queenstown', 'F', '1']]

        # code that filters each combination
        table_list = []
        for i in comb_list:
            filtered_table = copy.deepcopy(self)
            for j in range(len(i)):
                filtered_table = filtered_table.filter(lambda x: x[keys_to_pivot_list[j]] == i[j])
            table_list.append(filtered_table)

        # for each filter table applies the relevant aggregate functions
        # to keys to aggregate
        # the aggregate functions is listed in aggregate_func_list
        # to keys to aggregate is listed in keys_to_aggregate_list
        pivot_table = []
        for i in range(len(table_list)):
            temp_list = []
            for j in range(len(keys_to_aggregate_list)):
                temp_table = table_list[i].aggregate(aggregate_func_list[j], keys_to_aggregate_list[j])
                temp_list.append(temp_table)
            pivot_table.append([comb_list[i], temp_list])
        # return a pivot table
        return pivot_table

    def __str__(self):
        return self.table_name + ':' + str(self.table)


table1 = Table('cities', cities)
table2 = Table('countries', countries)
table3 = Table('players', players)
table4 = Table('teams', teams)
table5 = Table('titanic', titanic)
my_DB = DB()
my_DB.insert(table1)
my_DB.insert(table2)
my_DB.insert(table3)
my_DB.insert(table4)
my_DB.insert(table5)
my_table1 = my_DB.search('cities')

# print("Test filter: only filtering out cities in Italy")
# my_table1_filtered = my_table1.filter(lambda x: x['country'] == 'Italy')
# print(my_table1_filtered)
# print()
#
# print("Test select: only displaying two fields, city and latitude, for cities in Italy")
# my_table1_selected = my_table1_filtered.select(['city', 'latitude'])
# print(my_table1_selected)
# print()
#
# print("Calculating the average temperature without using aggregate for cities in Italy")
# temps = []
# for item in my_table1_filtered.table:
#     temps.append(float(item['temperature']))
# print(sum(temps)/len(temps))
# print()
#
# print("Calculating the average temperature using aggregate for cities in Italy")
# print(my_table1_filtered.aggregate(lambda x: sum(x)/len(x), 'temperature'))
# print()
#
# print("Test join: finding cities in non-EU countries whose temperatures are below 5.0")
# my_table2 = my_DB.search('countries')
# my_table3 = my_table1.join(my_table2, 'country')
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'no').filter(lambda x: float(x['temperature']) < 5.0)
# print(my_table3_filtered.table)
# print()
# print("Selecting just three fields, city, country, and temperature")
# print(my_table3_filtered.select(['city', 'country', 'temperature']))
# print()
#
# print("Print the min and max temperatures for cities in EU that do not have coastlines")
# my_table3_filtered = my_table3.filter(lambda x: x['EU'] == 'yes').filter(lambda x: x['coastline'] == 'no')
# print("Min temp:", my_table3_filtered.aggregate(lambda x: min(x), 'temperature'))
# print("Max temp:", my_table3_filtered.aggregate(lambda x: max(x), 'temperature'))
# print()
#
# print("Print the min and max latitude for cities in every country")
# for item in my_table2.table:
#     my_table1_filtered = my_table1.filter(lambda x: x['country'] == item['country'])
#     if len(my_table1_filtered.table) >= 1:
#         print(item['country'], my_table1_filtered.aggregate(lambda x: min(x), 'latitude'), my_table1_filtered.aggregate(lambda x: max(x), 'latitude'))
# print()

# In teams with 'ia', minutes < 200 make > 100 passes
my_table4 = my_DB.search('players')
my_table4_filtered = (my_table4.filter(lambda x: 'ia' in x['team']).filter(lambda x: int(x['minutes']) < 200)
                      .filter(lambda x: int(x['passes']) > 100))
my_table4_filtered_selected = my_table4_filtered.select(['surname', 'team', 'position'])
print(my_table4_filtered_selected)
print()

# average of games played of team ranking < 10 and >= 10
my_table5 = my_DB.search('teams')
my_table5_filtered_top10 = my_table5.filter(lambda x: int(x['ranking']) < 10)
avg_games_top10 = my_table5_filtered_top10.aggregate(lambda x: sum(x) / len(x), 'games')

my_table5_filtered = my_table5.filter(lambda x: int(x['ranking']) >= 10)
avg_games_not_top10 = my_table5_filtered.aggregate(lambda x: sum(x) / len(x), 'games')
print(f"Games Played by Teams \nRanking < 10: {avg_games_top10:.4f} vs Ranking >= 10: {avg_games_not_top10:.4f}")
print()

# average passes made by forwards vs midfielders
my_table4_midfield = my_table4.filter(lambda x: x['position'] == 'midfielder')
avg_pass_midfielder = my_table4_midfield.aggregate(lambda x: sum(x) / len(x), 'passes')

my_table4_forward = my_table4.filter(lambda x: x['position'] == 'forward')
avg_pass_forward = my_table4_forward.aggregate(lambda x: sum(x) / len(x), 'passes')
print(f'Ball passes \nForwards: {avg_pass_forward:.4f} vs Midfielder: {avg_pass_midfielder:.4f}')
print()

my_table6 = my_DB.search('titanic')
# Average fare First Class vs Third class
my_table6_first_class = my_table6.filter(lambda x: x['class'] == '1')
first_class_avg = my_table6_first_class.aggregate(lambda x: sum(x) / len(x), 'fare')

my_table6_third_class = my_table6.filter(lambda x: x['class'] == '3')
third_class_avg = my_table6_third_class.aggregate(lambda x: sum(x) / len(x), 'fare')
print(f'Average Fare\nFirst Class: {first_class_avg:.4f} vs Third Class: {third_class_avg:.4f}')
print()

# Survival rate of Male vs Female passenger
my_table6_male = my_table6.filter(lambda x: x['gender'] == 'M')
male_total = len(my_table6_male.select('survived'))
male_survived = len(my_table6_male.filter(lambda x: x['survived'] == 'yes').select('survived'))
male_rate = male_survived / male_total * 100

my_table6_female = my_table6.filter(lambda x: x['gender'] == 'F')
female_total = len(my_table6_female.select('survived'))
female_survived = len(my_table6_female.filter(lambda x: x['survived'] == 'yes').select('survived'))
female_rate = female_survived / female_total * 100
print(f'Survival rate\nMale: {male_rate:.4f} % vs Female: {female_rate:.4f} %')
print()

# Find total male passenger embarked at Southampton
my_table6_m_stt = my_table6.filter(lambda x: x['gender'] == 'M')
my_table6_m_stt = my_table6_m_stt.filter(lambda x: x['embarked'] == 'Southampton')
passenger_num = len(my_table6_m_stt.select('surname'))
print(f'There are {passenger_num} male passenger embarked at Southampton')

# Test Code
table4 = Table('titanic', titanic)
my_DB.insert(table4)
my_table4 = my_DB.search('titanic')
my_pivot = my_table4.pivot_table(['embarked', 'gender', 'class'],
                                 ['fare', 'fare', 'fare', 'last'],
                                 [lambda x: min(x), lambda x: max(x), lambda x: sum(x) / len(x), lambda x: len(x)])
print(my_pivot)
print()

my_table7 = my_DB.search('players')
my_pivot2 = my_table7.pivot_table(['position'],
                                  ['passes', 'shots'],
                                  [lambda x: sum(x)/len(x), lambda x: sum(x)/len(x)])
print(my_pivot2)
print()
my_table8 = my_DB.search('countries')
my_table8 = my_table8.join(my_DB.search('cities'), 'country')
my_pivot3 = my_table8.pivot_table(['EU', 'coastline',],
                                  ['temperature', 'latitude', 'latitude'],
                                  [lambda x: sum(x)/len(x), lambda x: min(x), lambda x: max(x)])
print(my_pivot3)
print()
my_pivot4 = my_table4.pivot_table(['class', 'gender', 'survived'],
                                  ['survived', 'fare'],
                                  [lambda x: len(x), lambda x:sum(x)/len(x)])
print(my_pivot4)
print()

