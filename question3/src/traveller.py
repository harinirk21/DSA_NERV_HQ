
import csv
import heapq
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "flights.csv"
OUTPUT_DIR = ROOT / "output"


def load_flights(filename):
    flights = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            source = int(row["source"])
            destination = int(row["destination"])
            price = int(row["price"])

            if price < 0:
                raise ValueError("Flight prices cannot be negative.")

            flights.append((source, destination, price))

    return flights


def cheapest_route(flights, source, destination, k, coupons):
    if k < 0 or coupons < 0:
        raise ValueError("K and C must be non-negative.")

    graph = {}

    for u, v, price in flights:
        graph.setdefault(u, []).append((v, price))

    # K intermediate stops means at most K + 1 flights.
    max_flights = k + 1

    # State: (city, flights_taken, coupons_used)
    start = (source, 0, 0)

    # Heap item: (total_cost, city, flights_taken, coupons_used)
    heap = [(0, source, 0, 0)]

    distance = {start: 0}
    parent = {start: None}

    final_state = None

    while heap:
        cost, city, flights_taken, coupons_used = heapq.heappop(heap)
        state = (city, flights_taken, coupons_used)

        if cost != distance.get(state):
            continue

        if city == destination:
            final_state = state
            break

        if flights_taken >= max_flights:
            continue

        for next_city, price in graph.get(city, []):

            # Option 1: pay the full flight price.
            next_state = (
                next_city,
                flights_taken + 1,
                coupons_used
            )
            next_cost = cost + price

            if next_cost < distance.get(next_state, float("inf")):
                distance[next_state] = next_cost
                parent[next_state] = (
                    state, city, next_city, price, False
                )

                heapq.heappush(
                    heap,
                    (
                        next_cost,
                        next_city,
                        flights_taken + 1,
                        coupons_used
                    )
                )

            # Option 2: use a coupon if one is available.
            if coupons_used < coupons:
                discounted_price = price // 2

                coupon_state = (
                    next_city,
                    flights_taken + 1,
                    coupons_used + 1
                )
                coupon_cost = cost + discounted_price

                if coupon_cost < distance.get(
                    coupon_state, float("inf")
                ):
                    distance[coupon_state] = coupon_cost
                    parent[coupon_state] = (
                        state, city, next_city, price, True
                    )

                    heapq.heappush(
                        heap,
                        (
                            coupon_cost,
                            next_city,
                            flights_taken + 1,
                            coupons_used + 1
                        )
                    )

    if final_state is None:
        print("No valid route exists under these constraints.")
        return None

    # Reconstruct the route from the parent information.
    route = []
    current = final_state

    while parent[current] is not None:
        previous, u, v, original_price, used_coupon = parent[current]

        paid = (
            original_price // 2
            if used_coupon
            else original_price
        )

        route.append({
            "source": u,
            "destination": v,
            "original_price": original_price,
            "coupon_used": "Yes" if used_coupon else "No",
            "paid": paid
        })

        current = previous

    route.reverse()

    total_cost = distance[final_state]
    coupons_used = sum(
        1 for flight in route
        if flight["coupon_used"] == "Yes"
    )

    print("\nCheapest total cost:", total_cost)
    print("Route:", source, end="")

    for flight in route:
        print(" ->", flight["destination"], end="")

    print()
    print("Flights taken:", len(route))
    print("Intermediate stops:", max(0, len(route) - 1))
    print("Coupons used:", coupons_used)

    # Export the chosen route.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "route.csv"

    with open(output_file, "w", newline="") as file:
        fieldnames = [
            "source",
            "destination",
            "original_price",
            "coupon_used",
            "paid"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(route)

    # Save a summary separately.
    summary_file = OUTPUT_DIR / "route_summary.csv"

    with open(summary_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "source",
            "destination",
            "max_intermediate_stops",
            "available_coupons",
            "flights_taken",
            "coupons_used",
            "total_cost"
        ])
        writer.writerow([
            source,
            destination,
            k,
            coupons,
            len(route),
            coupons_used,
            total_cost
        ])

    print("Route CSV:", output_file)
    print("Summary CSV:", summary_file)

    return {
        "cost": total_cost,
        "route": route,
        "flights_taken": len(route),
        "coupons_used": coupons_used
    }


if __name__ == "__main__":
    flights = load_flights(DATA_FILE)

    result = cheapest_route(
        flights=flights,
        source=1,
        destination=5,
        k=1,
        coupons=1
    )
