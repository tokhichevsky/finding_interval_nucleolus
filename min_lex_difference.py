import numpy as np
from scipy import optimize

def get_dual_game(game: dict):
    coalitions = list(game.keys())
    dual_game = dict()
    for coalition in coalitions[:-1]:
        dual_game[coalition] = game[coalitions[-1]] - game["".join(sorted(set(coalitions[-1]) ^ set(coalition)))]
    dual_game[coalitions[-1]] = game[coalitions[-1]]
    return dual_game


def get_sum_game(game, dual_game):
    sum_game = dict()
    for coalition in game.keys():
        sum_game[coalition] = 0.5 * game[coalition] + 0.5 * dual_game[coalition]
    return sum_game


def get_excess_vector(x, coalitions, problem):
    result = []
    x_coalition = []
    for coalition in coalitions:
        sum = 0
        for player in coalition:
            sum += x[player - 1]
        x_coalition.append(sum)
    for value, payoff in zip(list(problem.values())[:-1], x_coalition[:-1]):
        result.append(value - payoff)
    return result


lower_game = {
    "1": 0,
    "2": 0,
    "12": 2,
    "3": 0,
    "13": 0,
    "23": 2,
    "123": 4,
    "4": 0,
    "14": 2,
    "24": 2,
    "124": 6,
    "34": 2,
    "134": 6,
    "234": 6,
    "1234": 10
}

upper_game = {
    "1": 0,
    "2": 0,
    "12": 2,
    "3": 0,
    "13": 0,
    "23": 2,
    "123": 4,
    "4": 0,
    "14": 2,
    "24": 2,
    "124": 6,
    "34": 2,
    "134": 6,
    "234": 6,
    "1234": 12
}
lower_game1 = {
    "1": 0,
    "2": 0,
    "12": 2,
    "3": 0,
    "13": 0,
    "23": 2,
    "123": 6
}

upper_game1 = {
    "1": 0,
    "2": 0,
    "12": 2,
    "3": 0,
    "13": 0,
    "23": 2,
    "123": 8
}


def find_nucleolus(lower_game: dict, upper_game: dict):
    players = list(map(lambda x: int(x), filter(lambda x: len(x) == 1, lower_game.keys())))
    coalitions = list(map(lambda coalition: list(map(lambda player: int(player), coalition)), lower_game.keys()))
    constraint_matrix = [[0] * (i - 1) + [-1] + [0] * (len(players) - i) + [0] * (i - 1) + [1] + [0] * (
            len(players) - i)
                         for i in players] \
                        + [[1] * len(players) + [0] * len(players)] + [[0] * len(players) + [1] * len(players)]
    lb = [0] * len(players) + [0] + [0]
    ub = [np.inf] * len(players) + [list(lower_game.values())[-1]] + [list(upper_game.values())[-1]]
    count = 0
    ans = None

    def lex_min(x, min):
        com = np.array(x) - np.array(min)
        sum = 0
        for i in com:
            if i <= 0:
                sum += i
            else:
                break
        if sum == 0:
            for i in com:
                if i >= 0:
                    sum += i
                else:
                    break
        return sum

    def get_func(lower_game: dict, upper_game: dict, coalitions, players, A, lb, ub):
        def func(x):
            nonlocal min_excess
            nonlocal count
            nonlocal ans
            lower_excess = get_excess_vector(x[:len(players)], coalitions, lower_game)
            upper_excess = get_excess_vector(x[len(players):], coalitions, upper_game)
            general_excess = sorted(lower_excess + upper_excess, reverse=True)
            if min_excess is not None:
                sum = lex_min(general_excess, min_excess)
                if sum < 0:
                    min_excess = general_excess
                    ans = x
                    count = count + sum
                    result = count
                else:
                    result = count + sum
            else:
                min_excess = general_excess
                result = count
            return result

        return func

    func = get_func(lower_game, upper_game, coalitions, players, constraint_matrix, lb, ub)

    min_excess = sorted(get_excess_vector([0] * len(players), coalitions, lower_game) \
                        + get_excess_vector([0] * len(players), coalitions, upper_game), reverse=True)

    constraint = optimize.LinearConstraint(constraint_matrix, lb, ub)

    res = optimize.minimize(func, np.array([0] * len(players) * 2), constraints=constraint,
                            bounds=[(0, None)] * 2 * len(players), method="SLSQP",
                            options={'maxiter': 10000, 'ftol': 1e-10, 'disp': False,
                                     'eps': 0.0001})
    return res["x"]


dual_lower_game = get_dual_game(lower_game1)
dual_upper_game = get_dual_game(upper_game1)

sum_lower_game = get_sum_game(lower_game1, dual_lower_game)
sum_upper_game = get_sum_game(upper_game1, dual_upper_game)

print(find_nucleolus(sum_lower_game, sum_upper_game))
print("---------------------------------------------")
# print(func(res["x"]))
# print(func(np.array([2, 2, 2, 4, 8 / 3, 8 / 3, 8 / 3, 4])))

# print(func(ans))
# print(check(res["x"]))

# print(ans)
# print(np.array(ans) - np.array(res["x"]))
# print(np.sum(res["x"][:4]))
# print(np.sum(res["x"][4:]))
# print(res)
