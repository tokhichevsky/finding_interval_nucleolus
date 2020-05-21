from functools import reduce

from scipy.optimize import linprog

# !!! ИГРЫ ЗАДАЮТСЯ В ФОРМАТЕ СЛОВАРЯ, ВЫИГРЫШ ГРАНД КОАЛИЦИИ ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ !!!

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


def get_players_from_str_coalition(coalition: str):
    return list(map(lambda x: int(x), coalition))


def get_A_row(coalition, players_num: int):
    num_coalition = get_players_from_str_coalition(coalition)
    result = [0] * players_num
    for player in num_coalition:
        result[player - 1] = -1
    return result


def get_A_eq_row(coalition_set: set, player: str):
    result = [0] * len(coalition_set)
    for i, coalition in enumerate(coalition_set):
        if player in coalition:
            result[i] = 1
    return result


def is_balanced_coalition_set(coalition_set: set, players: set):
    c = [1] * len(coalition_set)
    A_eq = [get_A_eq_row(coalition_set, player) for player in players]
    b_eq = [1] * len(players)
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, method="revised simplex", bounds=[(0, 1)] * len(coalition_set))
    return result["success"] and 0 not in result["x"]


def get_balanced_coalitions(game: dict):
    coalitions = list(game.keys())[:-1]
    players = set(map(lambda x: x, filter(lambda x: len(x) == 1, game.keys())))

    coalition_sets = [{coalition} for coalition in coalitions]
    print(coalition_sets)
    checking_coalition_sets = coalition_sets.copy()
    while len(checking_coalition_sets[0]) != (2 ** len(players) - 2):
        print(list(checking_coalition_sets))
        new_checking_coalition_sets = list()
        for coalition_set in checking_coalition_sets:
            for coalition in coalitions:
                new_coalition_set = coalition_set | {coalition}
                if new_coalition_set not in coalition_sets:
                    coalition_sets.append(new_coalition_set)
                    new_checking_coalition_sets.append(new_coalition_set)
        checking_coalition_sets = new_checking_coalition_sets.copy()
    print(coalition_sets)

    player_full_coalition_sets = list()
    for coalition_set in coalition_sets:
        if reduce(lambda x, y: x | set(y), coalition_set, set()) == players:
            player_full_coalition_sets.append(coalition_set)
    print(player_full_coalition_sets)

    balanced_coalition_sets = list()
    for coalition_set in player_full_coalition_sets:
        if is_balanced_coalition_set(coalition_set, players):
            balanced_coalition_sets.append(coalition_set)
    print(balanced_coalition_sets)

    weakly_balanced_coalition_sets = list()
    for coalition_set in balanced_coalition_sets:
        is_weakly_balanced = True
        for another_coalition_set in balanced_coalition_sets:
            if coalition_set != another_coalition_set and coalition_set.issuperset(another_coalition_set):
                is_weakly_balanced = False
                break
        if is_weakly_balanced:
            weakly_balanced_coalition_sets.append(coalition_set)

    return weakly_balanced_coalition_sets


b = get_balanced_coalitions(lower_game)

result = r""

for i, bcoal in enumerate(b):
    row = r""
    for coal in bcoal:
        row += r"$\{" + ",".join(list(coal)) + r"\}$"
        if coal != list(bcoal)[-1]:
            row += ", "
    row += r""
    result += row
    if (i + 1) % 2 != 0:
        result += " & "
    else:
        result += r"\\" + "\n"

print(result)
