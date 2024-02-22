import math

import numpy as np
import collections


def updateMatrix(mat):
    mat = np.array(mat)
    (m, n) = mat.shape
    dir = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    queue = collections.deque()
    res = np.full((m, n), 0 + 0j)
    for r in range(m):
        for c in range(n):
            if mat[r][c] == 0:
                res[r][c] = 0 + 0j
                queue.append((r, c))
            else:
                res[r][c] = -1 - 1j

    while queue:
        r, c = queue.popleft()
        for dr, dc in dir:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= m or nc < 0 or nc >= n or res[nr][nc] != -1 - 1j:
                continue
            res[nr][nc] = res[r][c] + dr + dc * 1j
            queue.append((nr, nc))
    new_res = np.zeros((m, n), dtype=float)
    for r in range(m):
        for c in range(n):
            new_res[r][c] = math.sqrt(np.real(res[r][c]) ** 2 + np.imag(res[r][c]) ** 2)
    return new_res
