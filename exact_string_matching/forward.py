from dataclasses import dataclass
from typing import List, Tuple
from common import prefix

def brute_force(t, w, n, m):
  i = 1
  while i <= n - m + 1:
    j = 0
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i = i + 1

def morris_pratt(t, w, n, m):
  B = prefix.prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - B[j], max(0, B[j])

def knuth_morris_pratt(t, w, n, m):
  sB = prefix.strong_prefix_suffix(w, m)
  i, j = 1, 0
  while i <= n - m + 1:
    while j < m and t[i + j] == w[j + 1]:
      j = j + 1
    if j == m:
      yield i
    i, j = i + j - sB[j], max(0, sB[j])

@dataclass
class _Hrp:
  period: int
  scope: Tuple[int, int]


def _preprocess_first_hrps(w, m, k, limit = 2):
  '''Compute list of first n k-Highly-Repeating-Prefixes (k-HRP).

  A prefix is k-HRP if it is basic period with at least k periods.
  '''
  period, j = 1, 0
  # TODO(krzysztof-turowski): migrate to yield
  hrps: List[_Hrp] = []
  while period + j < m:
    while period + j < m and w[j + 1] == w[period + j + 1]:
      j += 1
    prefix_len = period + j

    if period * k <= prefix_len:
      hrps.append(_Hrp(period=period, scope=(2 * period, prefix_len)))
      if len(hrps) == limit:
        return hrps

    hrp = next((h for h in hrps if 2 * h.scope[0] <= j <= h.scope[1]), None)
    if hrp is not None:
      period, j = period + hrp.period, j - hrp.period
    else:
      period, j = period + (j // k) + 1, 0
  return hrps

def _get_hrp1(w, m, k):
  hrps = _preprocess_first_hrps(w, m, k, limit=1)
  return hrps[0] if len(hrps) > 0 else None

def _get_hrp2(w, m, k):
  hrps = _preprocess_first_hrps(w, m, k, limit=2)
  return hrps[0] if len(hrps) > 1 else None

def _perfect_decomposition(w, m, k):
  '''Returns strings u, v and k-HRP of v,
  such that w = u*v and v has only one k-HRP
  '''
  j = 0
  hrp1, hrp2 = _get_hrp1(w, m, k), _get_hrp2(w, m, k)

  while hrp1 and hrp2:
    j += hrp1.period
    hrp1 = _get_hrp1(w[j:], m - j, k)
    if hrp1 and hrp1.period >= hrp2.period:
      hrp2 = _get_hrp2(w[j:], m - j, k)

  return w[:j+1], w[j:], j, m - j, hrp1


def _simple_text_search(t, v, n, m, hrp1: _Hrp, k):
  '''Iterates over every occurrence of pattern v in text t.

  Assumes v has only one k-HRP hrp1.
  '''
  position, j = 0, 0
  while position + m <= n:
    while j < m and v[j+1] == t[position + j + 1]:
      j += 1

    if j == m:
      yield position + 1

    if hrp1 and 2 * hrp1.scope[0] <= j <= hrp1.scope[1]:
      position, j = position + hrp1.period, j - hrp1.period
    else:
      position, j = position + (j // k) + 1, 0

def galil_seifaras(t, w, n, m):
  k = 4
  u, v, uLen, vLen, hrp1 = _perfect_decomposition(w, m, k)
  for i in _simple_text_search(t, v, n, vLen, hrp1, k):
    if i > uLen and u[1:] == t[i - uLen :i]:
      yield i - uLen

def crochemore(t, w, n, m):
  def next_maximal_suffix(w, n, i, j, k, p):
    while j + k <= n:
      if w[i + k] == w[j + k]:
        if k == p:
          j, k = j + p, 1
        else:
          k += 1
      elif w[i + k] > w[j + k]:
        j, k, p = j + k, 1, j + k - i
      else:
        i, j, k, p = j, i + 1, 1, 1
    return i, j, k, p

  t_pos, w_pos = 0, 1
  i, j, k, p = 0, 1, 1, 1
  while t_pos <= n - m:
    while w_pos <= m and t[t_pos + w_pos] == w[w_pos]:
      w_pos += 1

    if w_pos == m + 1:
      yield t_pos + 1

    if t_pos == n - m:
      return

    i, j, k, p = next_maximal_suffix(
      w[:w_pos] + t[t_pos + w_pos], w_pos, i, j, k, p)

    w_ew_prim = w[i + 1:w_pos] + t[t_pos + w_pos]
    if w_ew_prim[:p].endswith(w[1:i + 1]):
      t_pos, w_pos = t_pos + p, w_pos - p + 1
      if j - i > p:
        j = j - p
      else:
        i, j, k, p = 0, 1, 1, 1
    else:
      t_pos, w_pos = t_pos + max(i, min(w_pos - i, j)) + 1, 1
      i, j, k, p = 0, 1, 1, 1
