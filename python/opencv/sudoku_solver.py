import copy

def check_for_digit(m, x, y, d):
    if d == 0:
        return True

    for i in range(0, 9):
        if m[i][x] == d:
            return False

        if m[y][i] == d:
            return False

        l = i / 3
        k = i % 3
        if m[int(y / 3) * 3 + l][int(x / 3) * 3 + k] == d:
            return False
    return True

def get_next_empty(m, x, y):
    x0 = x
    y0 = y
    while True:
        x = (x + 1)
        if x == 9:
            x = x % 9
            y = y + 1
        if y == 9:
            return x0, y0
        if m[y][x] == 0:
            break
    return x, y

def get_previous_empty(m, x, y):
    x0 = x
    y0 = y
    while True:
        x = (x - 1)
        if x == -1:
            x = 9 + x
            y = y - 1
        if y == -1:
            return x0, y0
        if m[y][x] == 0:
            break
    return x, y

def solve_sudoku(m):
    c = copy.deepcopy(m)
    x = -1
    y = 0
    x, y = get_next_empty(m, x, y)

    while True:
        d = c[y][x]

        digit_found = False
        for i in range(d + 1, 10):
            if check_for_digit(c, x, y, i):
                c[y][x] = i
                digit_found = True
                break

        if not digit_found:
            c[y][x] = 0
            xn, yn = get_previous_empty(m, x, y)
        else:
            xn, yn = get_next_empty(m, x, y)

        if xn == x and yn == y:
            break

        x = xn
        y = yn

    return c

def show(m):
    for i in range(0, 9):
        l = ""
        for j in range(0, 9):
            l += str(m[i][j]) + " "
        print l

# S = [
#     [8, 5, 0, 0, 0, 0, 0, 0, 2],
#     [1, 0, 4, 0, 7, 0, 0, 0, 3],
#     [6, 0, 0, 3, 0, 0, 0, 0, 0],

#     [2, 3, 0, 0, 5, 0, 8, 0, 1],
#     [0, 8, 0, 0, 3, 0, 0, 2, 0],
#     [4, 0, 1, 0, 9, 0, 0, 3, 6],

#     [0, 0, 0, 0, 0, 2, 0, 0, 5],
#     [3, 0, 0, 0, 6, 0, 2, 0, 9],
#     [5, 0, 0, 0, 0, 0, 0, 4, 7]
# ]

# S = [
#     [0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 0, 0, 9, 8, 0, 0],
#     [9, 2, 0, 7, 0, 0, 0, 0, 0],

#     [0, 0, 7, 2, 0, 8, 6, 5, 0],
#     [2, 8, 0, 6, 0, 0, 0, 0, 4],
#     [0, 0, 5, 0, 0, 0, 0, 3, 0],

#     [7, 0, 0, 4, 0, 0, 0, 0, 0],
#     [0, 5, 0, 0, 0, 6, 0, 0, 0],
#     [4, 0, 9, 0, 5, 0, 0, 1, 0]
# ]

# C = solve_sudoku(S)
# show(C)