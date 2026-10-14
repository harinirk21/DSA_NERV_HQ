
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class Main {

    static final Path ROOT = Paths.get("").toAbsolutePath();
    static final Path DATA = ROOT.resolve("data");
    static final Path OUTPUT = ROOT.resolve("output");

    static final int CAPACITY = 3;

    static Map<Integer, String> courses = new LinkedHashMap<>();
    static Map<Integer, Set<Integer>> graph = new LinkedHashMap<>();

    static class Result {
        Map<Integer, Integer> assignment;
        int slots;
        double runtime;

        Result(Map<Integer, Integer> assignment,
               int slots, double runtime) {
            this.assignment = assignment;
            this.slots = slots;
            this.runtime = runtime;
        }
    }

    public static void main(String[] args) throws Exception {

        loadData();

        if (courses.isEmpty()) {
            System.out.println("No courses found.");
            return;
        }

        if (CAPACITY < 1) {
            throw new IllegalArgumentException(
                "Capacity must be at least 1."
            );
        }

        long start = System.nanoTime();
        Map<Integer, Integer> greedy = greedyDSatur();
        double greedyTime =
            (System.nanoTime() - start) / 1_000_000_000.0;

        int greedySlots = countSlots(greedy);

        start = System.nanoTime();
        Map<Integer, Integer> optimal =
            exactMinimum(greedySlots);
        double exactTime =
            (System.nanoTime() - start) / 1_000_000_000.0;

        int optimalSlots =
            optimal == null ? -1 : countSlots(optimal);

        display("DSatur Greedy Timetable", greedy);
        saveTimetable("greedy_timetable.csv", greedy);

        System.out.printf(
            "%nGreedy slots: %d%n", greedySlots
        );
        System.out.printf(
            "Greedy runtime: %.6f seconds%n", greedyTime
        );

        if (optimal != null) {
            display("Exact Timetable", optimal);
            saveTimetable("optimal_timetable.csv", optimal);

            System.out.println("Minimum slots: " + optimalSlots);
            System.out.println(
                "Optimality: Proven by completed exact search"
            );
            System.out.printf(
                "Exact runtime: %.6f seconds%n", exactTime
            );
        } else {
            System.out.println(
                "Exact search did not complete with a solution."
            );
        }

        saveComparison(
            greedySlots, greedyTime,
            optimalSlots, exactTime
        );

        System.out.println("\nCSV files saved in: " + OUTPUT);
    }

    static void loadData() throws IOException {

        try (BufferedReader br = Files.newBufferedReader(
                DATA.resolve("courses.csv"))) {

            String line = br.readLine(); // Skip header

            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",", 2);
                int id = Integer.parseInt(parts[0].trim());
                String name = parts[1].trim();

                courses.put(id, name);
                graph.put(id, new LinkedHashSet<>());
            }
        }

        try (BufferedReader br = Files.newBufferedReader(
                DATA.resolve("conflicts.csv"))) {

            br.readLine(); // Skip header
            String line;

            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                int u = Integer.parseInt(parts[0].trim());
                int v = Integer.parseInt(parts[1].trim());

                if (!graph.containsKey(u) ||
                    !graph.containsKey(v)) {
                    throw new IllegalArgumentException(
                        "Conflict references unknown course: " + line
                    );
                }

                if (u == v) {
                    throw new IllegalArgumentException(
                        "A course cannot conflict with itself."
                    );
                }

                graph.get(u).add(v);
                graph.get(v).add(u);
            }
        }
    }

    static int saturation(int course,
                          Map<Integer, Integer> assigned) {
        Set<Integer> colors = new HashSet<>();

        for (int neighbor : graph.get(course)) {
            if (assigned.containsKey(neighbor)) {
                colors.add(assigned.get(neighbor));
            }
        }

        return colors.size();
    }

    static int chooseDSatur(
            Map<Integer, Integer> assigned) {

        int best = -1;
        int bestSaturation = -1;
        int bestDegree = -1;

        for (int course : graph.keySet()) {
            if (assigned.containsKey(course)) {
                continue;
            }

            int sat = saturation(course, assigned);
            int degree = graph.get(course).size();

            if (sat > bestSaturation ||
                (sat == bestSaturation &&
                 degree > bestDegree)) {
                best = course;
                bestSaturation = sat;
                bestDegree = degree;
            }
        }

        return best;
    }

    static Map<Integer, Integer> greedyDSatur() {

        Map<Integer, Integer> assigned = new LinkedHashMap<>();
        int[] counts = new int[graph.size() + 1];

        while (assigned.size() < graph.size()) {

            int course = chooseDSatur(assigned);
            Set<Integer> forbidden = new HashSet<>();

            for (int neighbor : graph.get(course)) {
                if (assigned.containsKey(neighbor)) {
                    forbidden.add(assigned.get(neighbor));
                }
            }

            int slot = 0;

            while (slot < graph.size()) {
                if (!forbidden.contains(slot) &&
                    counts[slot] < CAPACITY) {
                    break;
                }
                slot++;
            }

            assigned.put(course, slot);
            counts[slot]++;
        }

        return assigned;
    }

    static Map<Integer, Integer> exactMinimum(
            int upperBound) {

        if (graph.isEmpty()) {
            return new LinkedHashMap<>();
        }

        int lowerBound = Math.max(
            1, (int) Math.ceil(
                (double) graph.size() / CAPACITY
            )
        );

        for (int k = lowerBound; k <= upperBound; k++) {
            Map<Integer, Integer> assigned =
                new LinkedHashMap<>();
            int[] counts = new int[k];

            if (backtrack(assigned, counts, k)) {
                return new LinkedHashMap<>(assigned);
            }
        }

        return null;
    }

    static boolean backtrack(
            Map<Integer, Integer> assigned,
            int[] counts, int k) {

        if (assigned.size() == graph.size()) {
            return true;
        }

        int course = chooseDSatur(assigned);
        Set<Integer> forbidden = new HashSet<>();

        for (int neighbor : graph.get(course)) {
            if (assigned.containsKey(neighbor)) {
                forbidden.add(assigned.get(neighbor));
            }
        }

        // Try only existing slots and the next unused slot.
        Set<Integer> used = new HashSet<>(assigned.values());
        int nextUnused = used.isEmpty()
            ? 0 : Collections.max(used) + 1;

        List<Integer> candidates = new ArrayList<>(used);
        Collections.sort(candidates);

        if (nextUnused < k) {
            candidates.add(nextUnused);
        }

        for (int slot : candidates) {
            if (forbidden.contains(slot)) {
                continue;
            }

            if (counts[slot] >= CAPACITY) {
                continue;
            }

            assigned.put(course, slot);
            counts[slot]++;

            if (backtrack(assigned, counts, k)) {
                return true;
            }

            assigned.remove(course);
            counts[slot]--;
        }

        return false;
    }

    static int countSlots(Map<Integer, Integer> assignment) {
        if (assignment.isEmpty()) {
            return 0;
        }

        return Collections.max(assignment.values()) + 1;
    }

    static void display(
            String title, Map<Integer, Integer> assignment) {

        System.out.println("\n" + title);
        System.out.println("-------------------------");

        for (int slot = 0; slot < countSlots(assignment); slot++) {
            List<String> exams = new ArrayList<>();

            for (int course : courses.keySet()) {
                if (assignment.get(course) != null &&
                    assignment.get(course) == slot) {
                    exams.add(courses.get(course));
                }
            }

            System.out.println(
                "Slot " + (slot + 1) + ": " +
                String.join(", ", exams)
            );
        }
    }

    static void saveTimetable(
            String filename,
            Map<Integer, Integer> assignment)
            throws IOException {

        Files.createDirectories(OUTPUT);
        Path path = OUTPUT.resolve(filename);

        try (BufferedWriter writer =
                Files.newBufferedWriter(path)) {

            writer.write("course_id,course_name,slot\n");

            for (int course : courses.keySet()) {
                writer.write(
                    course + "," +
                    courses.get(course) + "," +
                    (assignment.get(course) + 1) + "\n"
                );
            }
        }
    }

    static void saveComparison(
            int greedySlots, double greedyTime,
            int optimalSlots, double exactTime)
            throws IOException {

        Files.createDirectories(OUTPUT);

        try (BufferedWriter writer = Files.newBufferedWriter(
                OUTPUT.resolve("algorithm_comparison.csv"))) {

            writer.write(
                "algorithm,slots,runtime_seconds,optimality\n"
            );

            writer.write(
                "DSatur Greedy," + greedySlots + "," +
                greedyTime + ",Not guaranteed\n"
            );

            if (optimalSlots >= 0) {
                writer.write(
                    "Exact Backtracking," + optimalSlots + "," +
                    exactTime + ",Proven optimal\n"
                );
            }
        }
    }
}
    