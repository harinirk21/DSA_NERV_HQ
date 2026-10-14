# Budget Traveller — Algorithm Analysis

## Problem Statement

Find the minimum-cost route from a source city to a destination city in a directed flight network. The route may contain at most `K` intermediate stops and may use at most `C` coupons. Each coupon halves the price of one flight.

## Algorithm

The solution uses Dijkstra's algorithm over an expanded state:

`(city, flights_taken, coupons_used)`

A city alone is insufficient to represent a search state: arriving at the same city with fewer flights or fewer coupons used can lead to a different set of future possibilities.

For each flight, the algorithm considers two transitions:

1. Pay the full ticket price.
2. If a coupon remains, pay half the ticket price using integer division.

The algorithm limits travel to `K + 1` flights and records parent states to reconstruct the route.

## Complexity Analysis

Let:

- `V` be the number of cities.
- `E` be the number of flights.
- `K` be the maximum number of intermediate stops.
- `C` be the number of available coupons.

There are at most `V × (K + 2) × (C + 1)` states, including the initial state with zero flights.

Each state considers its outgoing flights, with at most two transitions per flight.

Using a binary heap, the approximate upper-bound time complexity is:

`O(V × (K + 2) × (C + 1) + E × (K + 1) × (C + 1) × log(V × (K + 2) × (C + 1)))`

The space complexity is:

`O(V × (K + 2) × (C + 1) + E)`

These bounds describe the expanded-state search and its adjacency list. The algorithm is suitable when the stop and coupon limits are manageable.

## Sample Result

- Source: City 1
- Destination: City 5
- Maximum intermediate stops: 1
- Coupons available: 1
- Selected route: `1 → 3 → 5`
- Coupon applied to flight: `1 → 3`
- Total cost: `250`

## Correctness

Each expanded state represents a specific city, flight count, and coupon count. All flight prices are non-negative, including discounted prices. Dijkstra's algorithm therefore finds the minimum cost among valid expanded states. The flight limit prevents routes exceeding `K + 1` flights, and the coupon dimension prevents use of more than `C` coupons.

## Assumptions and Limitations

- Flight prices are non-negative integers.
- A coupon reduces a flight price to `floor(price / 2)`.
- Coupons can be used on any flight, with at most one coupon per flight.
- Flights are directed.
- The implementation returns one cheapest route when multiple routes tie.
- Large values of `K` and `C` increase the number of states and memory required.