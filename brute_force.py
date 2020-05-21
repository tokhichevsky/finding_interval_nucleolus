import numpy as np

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


def get_players(game: dict) -> list:
    """
    Получает список игроков игры game
    :param game: Игра в виде словаря
    :return: Список игроков
    """
    return list(map(lambda x: int(x), filter(lambda x: len(x) == 1, game.keys())))


def get_coalitions(game: dict):
    return list(map(lambda coalition: list(map(lambda player: int(player), coalition)), game.keys()))


def get_excess_vector(x, coalitions, game):
    result = []
    x_coalition = []
    for coalition in coalitions:
        sum = 0
        for player in coalition:
            sum += x[player - 1]
        x_coalition.append(sum)
    for value, payoff in zip(list(game.values())[:-1], x_coalition[:-1]):
        result.append(value - payoff)
    return result


def get_sorted_interval_excess(lower_game: dict, upper_game: dict, x: list, y: list):
    coalitions = get_coalitions(lower_game)
    return sorted(get_excess_vector(x, coalitions, lower_game)
                  + get_excess_vector(y, coalitions, upper_game),
                  reverse=True)


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


def find_nucleolus(lower_game: dict, upper_game: dict, x: list = None, y: list = None, eps: float = 1, alpha: float = 1,
                   iters: int = 3):
    players = get_players(lower_game)
    if x is None:
        x = [0] * len(players)
    if y is None:
        y = [0] * len(players)

    def lower_recursive_while(x: list, y: list, player: int = 1, eps: float = 1,
                              alpha: float = 1, iters: int = 3,
                              min_excess: list = None, solution: list = None, local_alpha=None, local_iters=None,
                              local_winner=1, old_x: list = None, upper_nucleolus: list = None):
        super_global_min_excess_counter = 0
        global_min_excess_counter = 0
        local_min_excess_counter = 0
        if old_x is None:
            if player == 1:
                old_x = x.copy()
            else:
                old_x = [0] * len(players)
        if local_alpha is None:
            local_alpha = alpha
        if local_iters is None:
            local_iters = iters
        if solution is None:
            solution = [0] * len(players) * 2
        while sum(x) <= list(lower_game.values())[-1]:
            if player == len(players):

                if upper_nucleolus is None or not np.all(
                        np.array(x) <= np.array(upper_nucleolus)) or min_excess is None:
                    solution, min_excess, new_local_min_excess_counter = upper_recursive_while(
                        x, y, 1, eps, alpha, iters, min_excess, solution)
                    if solution[:len(players)] == [0] * len(players):
                        upper_nucleolus = solution[len(players):].copy()
                    local_min_excess_counter += new_local_min_excess_counter
                    global_min_excess_counter += new_local_min_excess_counter
                    super_global_min_excess_counter += new_local_min_excess_counter
                elif upper_nucleolus is not None and np.all(np.array(x) <= np.array(upper_nucleolus)):
                    excess = get_sorted_interval_excess(lower_game, upper_game, x, upper_nucleolus)
                    if excess < min_excess:
                        min_excess = excess.copy()
                        solution = x.copy() + upper_nucleolus.copy()
                        local_min_excess_counter += 1
                        global_min_excess_counter += 1
                        super_global_min_excess_counter += 1
                        print("excess", min_excess)
                        print("lower solution", solution, "player", player)
                        print("alpha", local_alpha, "iters", local_iters)
                        print()
            else:
                solution, min_excess, new_local_min_excess_counter, upper_nucleolus = lower_recursive_while(
                    x, y, player + 1, eps, alpha, iters, min_excess, solution, local_alpha, local_iters, local_winner,
                    old_x, upper_nucleolus)
                local_min_excess_counter += new_local_min_excess_counter
                global_min_excess_counter += new_local_min_excess_counter
                super_global_min_excess_counter += new_local_min_excess_counter

            if local_min_excess_counter == 0:
                if global_min_excess_counter != 0:
                    local_winner = player
                    if local_iters > 1:
                        x[player - 1:] = [
                            max(solution[:len(players)][player - 1] - (player - local_winner) * eps * local_alpha, 0)
                            for player in players[player - 1:]]
                        old_x = x.copy()
                        local_alpha /= 10
                        local_iters -= 1
                        global_min_excess_counter = 0
                    else:
                        break
                elif old_x[player - 1] + (player - local_winner + 2) * eps * local_alpha * 10 <= x[player - 1]:
                    local_alpha = min(alpha, local_alpha * 10)
                    local_iters = min(iters, local_iters + 1)

            local_min_excess_counter = 0
            x[player:] = old_x[player:].copy()
            x[player - 1] = round(x[player - 1] + eps * local_alpha, iters)
        if player == 1:
            return solution
        else:
            return solution, min_excess, super_global_min_excess_counter, upper_nucleolus

    def upper_recursive_while(x: list, y: list, player: int = 1, eps: float = 1, alpha: float = 1, iters: int = 3,
                              min_excess: list = None, solution: list = None, local_alpha=None, local_iters=None,
                              local_winner=1, old_y: list = None):

        super_global_min_excess_counter = 0
        global_min_excess_counter = 0
        local_min_excess_counter = 0
        if old_y is None:
            old_y = x.copy()
        if local_alpha is None:
            local_alpha = alpha
        if local_iters is None:
            local_iters = iters
        if max(y) == 0:
            y = x.copy()
        while sum(y) <= list(upper_game.values())[-1] \
                and x[player - 1] <= y[player - 1]:
            excess = get_sorted_interval_excess(lower_game, upper_game, x, y)
            if min_excess is None or excess < min_excess:
                min_excess = excess.copy()
                solution = x.copy() + y.copy()

                local_min_excess_counter += 1
                global_min_excess_counter += 1
                super_global_min_excess_counter += 1
                print("excess", min_excess)
                print("upper solution", solution, "player", player)
                print("alpha", local_alpha, "iters", local_iters)
                print()

            if player < len(players):
                solution, min_excess, new_local_min_excess_counter = upper_recursive_while(
                    x, y, player + 1, eps, alpha, iters, min_excess, solution, local_alpha, local_iters, local_winner,
                    old_y)
                local_min_excess_counter += new_local_min_excess_counter
                global_min_excess_counter += new_local_min_excess_counter
                super_global_min_excess_counter += new_local_min_excess_counter

            if local_min_excess_counter == 0:
                if global_min_excess_counter != 0:
                    local_winner = player
                    if local_iters > 1:
                        y[player - 1:] = [
                            max(solution[len(players):][player - 1] - (player - local_winner + 1) * eps * local_alpha,
                                0, x[player - 1]) for player in players[player - 1:]]
                        old_y = y.copy()
                        local_alpha /= 10
                        local_iters -= 1
                        global_min_excess_counter = 0
                    else:
                        break
                elif old_y[player - 1] + (player - local_winner + 2) * eps * local_alpha * 10 <= y[player - 1]:
                    local_alpha = min(alpha, local_alpha * 10)
                    local_iters = min(iters, local_iters + 1)

            local_min_excess_counter = 0
            y[player:] = old_y[player:].copy()
            y[player - 1] = round(y[player - 1] + eps * local_alpha, iters)
        return solution, min_excess, super_global_min_excess_counter

    return lower_recursive_while(x, y, eps=eps, alpha=alpha, iters=iters)


dual_lower_game = get_dual_game(lower_game)
dual_upper_game = get_dual_game(upper_game)

sum_lower_game = get_sum_game(lower_game, dual_lower_game)
sum_upper_game = get_sum_game(upper_game, dual_upper_game)

print(find_nucleolus(sum_lower_game, sum_upper_game))
