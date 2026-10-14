#!/usr/bin/env python3
"""
Closest Pair of Points: Brute-Force O(n^2) vs Divide-and-Conquer O(n log n)
===========================================================================

Usage (VS Code terminal):
    pip install matplotlib
    python closest_pair.py                 # then type N and press Enter
    echo 200 | python closest_pair.py      # N from stdin
    python closest_pair.py --mode int --range 50 --seed 1     # integer points (many ties/duplicates)
    python closest_pair.py --animate 24    # animate recursive split/merge on 24 points
    python closest_pair.py --test          # corner-case + randomized agreement tests (no plots)
    python closest_pair.py --no-plot       # text output only
    python closest_pair.py --save          # also save PNG files

Output (stdout):
    Line 1: Brute-Force        -> distance (6 dp) and the two points
    Line 2: Divide-and-Conquer -> distance (6 dp) and the two points
    Line 3: execution times in ms
(The agreement check is reported on stderr so stdout keeps the 3-line format.)
"""
import sys
import math
import time
import random
import heapq
import argparse


# ----------------------------------------------------------------------------
# Core helpers
# ----------------------------------------------------------------------------
def dist2(p, q):
    """Squared Euclidean distance (avoids sqrt in hot loops, preserves ordering)."""
    dx = p[0] - q[0]
    dy = p[1] - q[1]
    return dx * dx + dy * dy


def fmt_pt(p):
    f = lambda v: str(v) if isinstance(v, int) else f"{v:.4f}"
    return f"({f(p[0])}, {f(p[1])})"


# ----------------------------------------------------------------------------
# Algorithm 1: Brute force  -- O(n^2) time, O(1) extra space
# ----------------------------------------------------------------------------
def brute_force(pts):
    """Returns (distance, p, q) or None if fewer than 2 points."""
    n = len(pts)
    if n < 2:
        return None
    best = math.inf
    bp = bq = None
    for i in range(n - 1):
        pi = pts[i]
        for j in range(i + 1, n):
            d = dist2(pi, pts[j])
            if d < best:
                best, bp, bq = d, pi, pts[j]
    return math.sqrt(best), bp, bq


# ----------------------------------------------------------------------------
# Algorithm 2: Divide and conquer -- O(n log n) time, O(n) space
# ----------------------------------------------------------------------------
def closest_dc(pts, trace=None):
    """
    Returns (distance, p, q, info) or None if fewer than 2 points.
    info = {'midx': x of the top-level dividing line, 'd': final distance}
    trace (optional list) receives events used by the animation:
        ('base',  lo, hi, depth, best)
        ('split', lo, hi, depth, midx)
        ('merge', lo, hi, depth, midx, best, strip_points)
    """
    if len(pts) < 2:
        return None
    px = sorted(pts)                       # sorted by x (ties by y): done once, O(n log n)
    info = {}
    key_y = lambda p: p[1]

    def rec(lo, hi, depth):
        n = hi - lo
        # ---- base case: 2 or 3 points -> brute force
        if n <= 3:
            best = (math.inf, None, None)
            for i in range(lo, hi - 1):
                for j in range(i + 1, hi):
                    d = dist2(px[i], px[j])
                    if d < best[0]:
                        best = (d, px[i], px[j])
            ys = sorted(px[lo:hi], key=key_y)
            if trace is not None:
                trace.append(("base", lo, hi, depth, best))
            if depth == 0:
                info.update(midx=px[(lo + hi) // 2][0], d=math.sqrt(best[0]))
            return best, ys

        # ---- divide (by INDEX, so many equal x values cannot unbalance it)
        mid = (lo + hi) // 2
        midx = px[mid][0]
        if trace is not None:
            trace.append(("split", lo, hi, depth, midx))

        # ---- conquer
        bl, yl = rec(lo, mid, depth + 1)
        br, yr = rec(mid, hi, depth + 1)
        best = bl if bl[0] <= br[0] else br

        # ---- merge the two y-sorted halves in O(n) (this is what removes the extra log n)
        ys = list(heapq.merge(yl, yr, key=key_y))

        # ---- combine: look only at the strip |x - midx| < d, scanned in y order
        strip = [p for p in ys if (p[0] - midx) ** 2 < best[0]]
        for i in range(len(strip)):
            pi = strip[i]
            j = i + 1
            # at most ~7 iterations by the packing argument
            while j < len(strip) and (strip[j][1] - pi[1]) ** 2 < best[0]:
                d = dist2(pi, strip[j])
                if d < best[0]:
                    best = (d, pi, strip[j])
                j += 1
        if trace is not None:
            trace.append(("merge", lo, hi, depth, midx, best, list(strip)))
        if depth == 0:
            info.update(midx=midx, d=math.sqrt(best[0]))
        return best, ys

    best, _ = rec(0, len(px), 0)
    return math.sqrt(best[0]), best[1], best[2], info


# ----------------------------------------------------------------------------
# Point generation, timing, verification
# ----------------------------------------------------------------------------
def gen_points(n, mode="float", rng_range=1000, rng=random):
    if mode == "int":
        return [(rng.randint(0, rng_range), rng.randint(0, rng_range)) for _ in range(n)]
    return [(rng.uniform(0, rng_range), rng.uniform(0, rng_range)) for _ in range(n)]


def timed(fn, *a, repeat=1):
    best = math.inf
    out = None
    for _ in range(repeat):
        t = time.perf_counter()
        out = fn(*a)
        best = min(best, (time.perf_counter() - t) * 1000.0)
    return out, best


def agree(d1, d2):
    return math.isclose(d1, d2, rel_tol=1e-9, abs_tol=1e-12)


# ----------------------------------------------------------------------------
# Tests: corner cases + randomized cross-check
# ----------------------------------------------------------------------------
def run_tests(verbose=True):
    cases = {
        "N = 0": [],
        "N = 1": [(3, 4)],
        "N = 2": [(0, 0), (3, 4)],
        "N = 3": [(0, 0), (10, 10), (1, 1)],
        "two duplicates": [(5, 5), (1, 1), (5, 5), (9, 2)],
        "all identical": [(2, 2)] * 10,
        "collinear horizontal (same y)": [(x, 7) for x in (0, 10, 3, 4.5, 20, 21, 50)],
        "collinear vertical (same x)": [(7, y) for y in (0, 10, 3, 4.5, 20, 21, 50)],
        "collinear diagonal": [(i, i) for i in (0, 5, 9, 10, 11, 30)],
        "same x, many y (unbalanced-split trap)": [(1, y) for y in range(0, 40, 3)] + [(1, 13.5)],
        "closest pair straddles dividing line": [(0, 0), (1, 5), (4.9, 3), (5.1, 3), (9, 1), (10, 8)],
        "negative / mixed coordinates": [(-5, -5), (-4.5, -5), (3, 9), (-1, 2), (7, -8)],
        "float + int mix": [(1, 2.5), (1.0, 2.5000001), (9, 9), (0, 0)],
        "grid (many equal distances)": [(x, y) for x in range(6) for y in range(6)],
    }
    ok = True
    for name, pts in cases.items():
        b = brute_force(pts)
        c = closest_dc(pts)
        if b is None or c is None:
            good = (b is None and c is None)
            res = "both report 'no pair' (N<2)"
        else:
            good = agree(b[0], c[0])
            res = f"BF={b[0]:.6f}  DC={c[0]:.6f}"
        ok &= good
        if verbose:
            print(f"[{'PASS' if good else 'FAIL'}] {name:<42} {res}")

    # randomized: small ranges force duplicates, ties, shared x / y, collinearity
    rng = random.Random(12345)
    trials = 0
    for _ in range(3000):
        n = rng.randint(2, 60)
        r = rng.choice([3, 10, 100, 10_000])
        mode = rng.choice(["int", "float"])
        pts = gen_points(n, mode, r, rng)
        trials += 1
        if not agree(brute_force(pts)[0], closest_dc(pts)[0]):
            ok = False
            print("[FAIL] random mismatch on", pts)
            break
    for n in (500, 1000, 2000):
        pts = gen_points(n, "float", 1000, rng)
        trials += 1
        ok &= agree(brute_force(pts)[0], closest_dc(pts)[0])
    if verbose:
        print(f"[{'PASS' if ok else 'FAIL'}] {trials} randomized trials: both algorithms agree on min distance")
        print("ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
    return ok


# ----------------------------------------------------------------------------
# Performance study
# ----------------------------------------------------------------------------
def performance_study(mode="float", rng_range=1000, seed=0,
                      sizes=(100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200),
                      bf_max=3200):
    rng = random.Random(seed)
    rows = []
    print("\n  N      Brute(ms)   D&C(ms)   speed-up   agree")
    for n in sizes:
        pts = gen_points(n, mode, rng_range, rng)
        rep = 3 if n <= 800 else 1
        c, tc = timed(closest_dc, pts, repeat=rep)
        if n <= bf_max:
            b, tb = timed(brute_force, pts, repeat=rep)
            ag = agree(b[0], c[0])
            print(f"{n:>6} {tb:>11.2f} {tc:>10.2f} {tb / tc:>9.1f}x   {'yes' if ag else 'NO'}")
        else:
            tb, ag = None, None
            print(f"{n:>6} {'(skipped)':>11} {tc:>10.2f}")
        rows.append((n, tb, tc))
    return rows


# ----------------------------------------------------------------------------
# Visualisation
# ----------------------------------------------------------------------------
def plot_main(pts, bf, dc, info, save=False):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 7))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    midx, d = info["midx"], info["d"]

    ax.axvspan(midx - d, midx + d, color="gold", alpha=0.25, label=f"strip (width 2d = {2 * d:.4f})")
    ax.axvline(midx, color="purple", ls="--", lw=1.5, label=f"dividing line x = {midx:.3f}")
    ax.scatter(xs, ys, s=14, c="steelblue", zorder=2, label=f"points (N={len(pts)})")
    instrip = [p for p in pts if abs(p[0] - midx) < d]
    if instrip:
        ax.scatter([p[0] for p in instrip], [p[1] for p in instrip], s=22,
                   c="orange", zorder=3, label="points inside strip")

    # brute force: thick translucent red; D&C: thinner green on top (visible even if same pair)
    ax.plot([bf[1][0], bf[2][0]], [bf[1][1], bf[2][1]], color="red", lw=7, alpha=0.35,
            solid_capstyle="round", zorder=4, label=f"Brute-Force pair d={bf[0]:.6f}")
    ax.scatter([bf[1][0], bf[2][0]], [bf[1][1], bf[2][1]], s=110, facecolors="none",
               edgecolors="red", lw=2, zorder=5)
    ax.plot([dc[1][0], dc[2][0]], [dc[1][1], dc[2][1]], color="green", lw=2, zorder=6,
            label=f"Divide&Conquer pair d={dc[0]:.6f}")
    ax.scatter([dc[1][0], dc[2][0]], [dc[1][1], dc[2][1]], s=45, c="green", zorder=7)

    ax.set_title("Closest pair of points")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    if save:
        fig.savefig("closest_pair_points.png", dpi=150)


def plot_perf(rows, save=False):
    import matplotlib.pyplot as plt
    ns = [r[0] for r in rows]
    bn = [r[0] for r in rows if r[1] is not None]
    bt = [r[1] for r in rows if r[1] is not None]
    ct = [r[2] for r in rows]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5))

    a1.plot(bn, bt, "o-", color="red", label="Brute-Force  O(n²)")
    a1.plot(ns, ct, "s-", color="green", label="Divide & Conquer  O(n log n)")
    a1.set_xlabel("N")
    a1.set_ylabel("time (ms)")
    a1.set_title("Running time vs N (linear scale)")
    a1.legend()
    a1.grid(alpha=0.3)

    a2.loglog(bn, bt, "o-", color="red", label="Brute-Force")
    a2.loglog(ns, ct, "s-", color="green", label="Divide & Conquer")
    if bn:   # reference curves anchored at the first measured point
        n0, t0 = bn[0], bt[0]
        a2.loglog(ns, [t0 * (n / n0) ** 2 for n in ns], "r:", alpha=0.5, label="~ n² reference")
        c0 = ct[0]
        a2.loglog(ns, [c0 * (n * math.log2(n)) / (ns[0] * math.log2(ns[0])) for n in ns],
                  "g:", alpha=0.5, label="~ n log n reference")
    a2.set_xlabel("N (log)")
    a2.set_ylabel("time ms (log)")
    a2.set_title("Log-log: slope 2 vs ~1")
    a2.legend()
    a2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    if save:
        fig.savefig("closest_pair_runtime.png", dpi=150)


def animate(pts, interval=900, save=False):
    """Step-by-step animation of the recursion (split -> base -> merge)."""
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    trace = []
    res = closest_dc(pts, trace)
    px = sorted(pts)
    xs, ys = [p[0] for p in px], [p[1] for p in px]
    cmap = plt.get_cmap("tab10")
    pad = 0.05 * (max(xs) - min(xs) + 1)

    fig, ax = plt.subplots(figsize=(9, 6.5))

    def draw(k):
        ax.clear()
        ev = trace[k]
        kind, lo, hi, depth = ev[0], ev[1], ev[2], ev[3]
        ax.scatter(xs, ys, s=25, c="lightgray", zorder=1)
        seg = px[lo:hi]
        ax.scatter([p[0] for p in seg], [p[1] for p in seg], s=45, color=cmap(depth % 10), zorder=2)
        if kind == "split":
            ax.axvline(ev[4], color="purple", ls="--")
            msg = f"SPLIT  points[{lo}:{hi}] at x = {ev[4]:.2f}  (depth {depth})"
        elif kind == "base":
            _, _, _, _, (d2, p, q) = ev
            ax.plot([p[0], q[0]], [p[1], q[1]], "r-", lw=2)
            msg = f"BASE CASE  points[{lo}:{hi}] brute force -> d = {math.sqrt(d2):.3f}"
        else:
            _, _, _, _, midx, (d2, p, q), strip = ev
            d = math.sqrt(d2)
            ax.axvline(midx, color="purple", ls="--")
            ax.axvspan(midx - d, midx + d, color="gold", alpha=0.3)
            if strip:
                ax.scatter([s[0] for s in strip], [s[1] for s in strip], s=70, facecolors="none",
                           edgecolors="orange", lw=2, zorder=3)
            ax.plot([p[0], q[0]], [p[1], q[1]], "g-", lw=3)
            msg = (f"MERGE  points[{lo}:{hi}]  best d = {d:.3f}  "
                   f"(strip has {len(strip)} pts, width 2d)")
        ax.set_title(f"Step {k + 1}/{len(trace)}: {msg}", fontsize=10)
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.grid(alpha=0.2)

    anim = FuncAnimation(fig, draw, frames=len(trace), interval=interval, repeat=True)
    if save:
        try:
            anim.save("closest_pair_animation.gif", writer="pillow", fps=1)
        except Exception as e:  # pillow missing, etc.
            print("Could not save GIF:", e, file=sys.stderr)
    return anim   # keep a reference so it is not garbage collected


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Closest pair: brute force vs divide and conquer")
    ap.add_argument("--mode", choices=["float", "int"], default="float", help="coordinate type")
    ap.add_argument("--range", type=int, default=1000, help="coordinates drawn from [0, range]")
    ap.add_argument("--seed", type=int, default=None, help="random seed (reproducible runs)")
    ap.add_argument("--no-plot", action="store_true", help="skip all plots / performance study")
    ap.add_argument("--no-perf", action="store_true", help="skip the running-time study")
    ap.add_argument("--animate", type=int, metavar="M", default=0,
                    help="animate recursion on M random points (e.g. 24)")
    ap.add_argument("--save", action="store_true", help="save figures as PNG/GIF")
    ap.add_argument("--test", action="store_true", help="run corner-case and randomized tests, then exit")
    args = ap.parse_args()

    if args.test:
        sys.exit(0 if run_tests() else 1)

    if args.seed is not None:
        random.seed(args.seed)

    # ---- read N from standard input
    try:
        print("Enter N:", file=sys.stderr, end=" ", flush=True)
        n = int(sys.stdin.readline().strip())
    except ValueError:
        print("Invalid input: N must be an integer.")
        return
    if n < 2:
        print(f"N = {n}: need at least 2 points; closest pair is undefined.")
        return

    pts = gen_points(n, args.mode, args.range)

    b, tb = timed(brute_force, pts)
    c, tc = timed(closest_dc, pts)

    print(f"Brute-Force: {b[0]:.6f} {fmt_pt(b[1])} {fmt_pt(b[2])}")
    print(f"Divide-and-Conquer: {c[0]:.6f} {fmt_pt(c[1])} {fmt_pt(c[2])}")
    print(f"Time (ms): Brute-Force = {tb:.3f}, Divide-and-Conquer = {tc:.3f}")
    print("Verification: " + ("both algorithms AGREE on the minimum distance"
                              if agree(b[0], c[0]) else "MISMATCH!  (bug)"), file=sys.stderr)

    if args.no_plot:
        return

    import matplotlib.pyplot as plt
    plot_main(pts, b, c[:3], c[3], save=args.save)
    if not args.no_perf:
        rows = performance_study(args.mode, args.range, seed=args.seed or 0)
        plot_perf(rows, save=args.save)
    anim = animate(gen_points(args.animate, args.mode, args.range), save=args.save) if args.animate >= 2 else None
    plt.show()


if __name__ == "__main__":
    main()
