import itertools
from copy import deepcopy


def bruteforce(problem, cities):
    print("city list length is: {}".format(len(cities)))
    print("cities is: {}".format(cities))
    tempCities = deepcopy(cities)
    staticItem = tempCities.popitem()
    print("staticItem is {}".format(staticItem))
    print("tempCity length is: {}".format(len(tempCities)))
    print("tempCity is: {}".format(tempCities))

    best_fitness = 10000000
    best_key = None

    print("tempCities length is: {}".format(len(tempCities)))
    print("city keys are: {}".format(cities.keys()))
    allPermutations = itertools.permutations(tempCities.keys())
    for i in allPermutations:
        newtup = i + (staticItem[0],)
        fitness = problem.energy(newtup)
        if(fitness < best_fitness):
            best_fitness = fitness
            best_key = newtup

        # print "option {}".format(newtup)
    return best_fitness, best_key


def test_answer():
    import sys
    sys.path.append("/home/vagrant/traveling-sailor")
    sys.path.append("../traveling-sailor")
    import traveling_sailor

    cities = {
    'New York City': (40.72, 74.00),
    'Los Angeles': (34.05, 118.25),
    'Chicago': (41.88, 87.63),
    'Houston': (29.77, 95.38),
    'Phoenix': (33.45, 112.07),
    'Philadelphia': (39.95, 75.17),
    'San Antonio': (29.53, 98.47),
    # 'Dallas': (32.78, 96.80),
    # 'San Diego': (32.78, 117.15),
    # 'San Jose': (37.30, 121.87),
    # 'Detroit': (42.33, 83.05),
    # 'San Francisco': (37.78, 122.42),
    # 'Jacksonville': (30.32, 81.70),
    # 'Indianapolis': (39.78, 86.15),
    'Austin': (30.27, 97.77),
    'Columbus': (39.98, 82.98),
    'Fort Worth': (32.75, 97.33),
    'Charlotte': (35.23, 80.85),
    'Memphis': (35.12, 89.97),
    'Baltimore': (39.28, 76.62)
    }


    tsp = traveling_sailor.TSPSA(cities, None)
    import time
    brute_start = int(round(time.time() * 1000))
    best_distance, best_solution = bruteforce(tsp,cities)
    brute_end = int(round(time.time() * 1000))

    anneal_start = int(round(time.time() * 1000))
    tsp.copy_strategy = "slice"
    auto_schedule = tsp.auto(minutes=0.001)
    tsp.set_schedule(auto_schedule)
    good_distance, good_solution = tsp.anneal()
    anneal_end = int(round(time.time() * 1000))

    print("best solution is {} with key {}".format(best_distance,best_solution))
    print("good solution is {} with key {}".format(good_distance,good_solution))
    print("brute took: {}".format(brute_end - brute_start))
    print("anneal took: {}".format(anneal_end - anneal_start))


    #print("good solution is {} with key {}".format(good_distance,good_solution))
    #assert anneal(1000,0.2,cities.keys(),50000,problem) == 0
    assert best_solution > good_solution


if __name__ == "__main__":
    test_answer()
