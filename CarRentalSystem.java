// ======================================================================
// CAR RENTAL SYSTEM – FINAL MERGED CODE (MAHEEN + ABDUL SALAM + FAZ)
// ======================================================================
// This is the complete, fully commented, error‑free Car Rental System.
// It combines:
//   - Maheen's car management (cars.json, admin CRUD, SimpleJson)
//   - Abdul Salam's user flow and rental management (rentals.json, rentalHistory.json)
//   - Faz's helper methods (safe input, car availability check, etc.)
// ======================================================================

// Import the class that handles input/output errors.
import java.io.IOException;
// Import the class that defines UTF‑8 character encoding.
import java.nio.charset.StandardCharsets;
// Import the class that reads/writes entire files easily.
import java.nio.file.Files;
// Import the class that represents a file path.
import java.nio.file.Path;
// Import the class for dates (year‑month‑day).
import java.time.LocalDate;
// Import the class for dynamic arrays (lists).
import java.util.ArrayList;
// Import the class for reading keyboard input.
import java.util.Scanner;

// The main class – all code lives inside here.
public class CarRentalSystem {

    // ==================== GLOBAL SCANNER ====================
    // One Scanner object for all keyboard input.
    static Scanner sc = new Scanner(System.in);
    // End of scanner declaration.

    // ==================== MAHEEN's PART – CAR DATA (JSON) ====================
    // Path to the cars.json file (in the current folder).
    static final Path CARS_FILE = Path.of("cars.json");
    // Admin access code (password).
    static final String ADMIN_ACCESS_CODE = "CRS2026";
    // List that holds all Car objects (the fleet).
    static ArrayList<Car> cars = new ArrayList<>();

    // ==================== ABDUL SALAM's PART – RENTAL DATA (JSON) ====================
    // List of active rentals (cars not yet returned).
    static ArrayList<Rental> rentals = new ArrayList<>();
    // List of past rentals (cars already returned).
    static ArrayList<Rental> rentalHistory = new ArrayList<>();
    // Path to the rentals.json file (active rentals).
    static final Path RENTALS_FILE = Path.of("rentals.json");
    // Path to the rentalHistory.json file (past rentals).
    static final Path HISTORY_FILE = Path.of("rentalHistory.json");

    // ==================== MAIN METHOD ====================
    // Program starts here.
    public static void main(String[] args) {
        // Load cars from cars.json (Maheen's method).
        loadCarsFromFile();
        // Load active rentals from rentals.json (Abdul's method).
        loadRentalsFromFile();
        // Load past rentals from rentalHistory.json (Abdul's method).
        loadHistoryFromFile();
        // Display the main menu and handle user/admin selection.
        mainMenu();
        // After the menu loop ends, print a goodbye message.
        System.out.println("\n  Thank you for using Car Rental System. Goodbye!\n");
    } // End of main method.

    // ==================== MAIN MENU (Faz / merged) ====================
    // Displays the main menu and processes user choice.
    static void mainMenu() {
        // Infinite loop; break when user chooses 0.
        while (true) {
            // Blank line for spacing.
            System.out.println("\n  Welcome to the Car Rental System");
            // Option 1.
            System.out.println("  1  User");
            // Option 2.
            System.out.println("  2  Admin");
            // Option 0.
            System.out.println("  0  Exit");
            // Prompt.
            System.out.print("  Choose: ");
            // Read choice as a trimmed string.
            String choice = sc.nextLine().trim();
            // If user chooses 1, go to user section.
            if (choice.equals("1")) {
                userFlow();               // Abdul's method.
            }
            // If user chooses 2, go to admin section.
            else if (choice.equals("2")) {
                adminFlow();              // Maheen's method.
            }
            // If user chooses 0, exit the loop.
            else if (choice.equals("0")) {
                break;
            }
            // Otherwise, invalid choice.
            else {
                System.out.println("  Invalid choice.");
            } // End of if-else.
        } // End of while loop.
    } // End of mainMenu method.

    // ==================== ABDUL SALAM's USER FLOW ====================
    // Starts the user section: ask for name.
    static void userFlow() {
        // Blank line.
        System.out.println();
        // Ask for name.
        System.out.print("  Enter your name: ");
        // Read name, trim spaces.
        String name = sc.nextLine().trim();
        // If name is empty, show error and return.
        if (name.isEmpty()) {
            System.out.println("  Name cannot be empty.");
            return;
        } // End of if.
        // Go to user menu with this name.
        userMenuLoop(name);
    } // End of userFlow.

    // Displays user menu and loops until user chooses 0 (Back).
    static void userMenuLoop(String name) {
        // Infinite loop.
        while (true) {
            // Blank line.
            System.out.println();
            // Menu title with customer name.
            System.out.println("  USER MENU  (" + name + ")");
            // Option 1.
            System.out.println("  1  View available cars");
            // Option 2.
            System.out.println("  2  Search by brand or model");
            // Option 3.
            System.out.println("  3  Rent a car");
            // Option 4.
            System.out.println("  4  Return a car");
            // Option 5.
            System.out.println("  5  My rental history");
            // Option 0.
            System.out.println("  0  Back");
            // Blank line.
            System.out.println();
            // Prompt.
            System.out.print("  Choice: ");
            // Read choice.
            String ch = sc.nextLine().trim();
            // If 0, break out of loop.
            if (ch.equals("0")) break;
            // If 1, show available cars.
            else if (ch.equals("1")) showAvailableCars();
            // If 2, search car by model.
            else if (ch.equals("2")) searchCarByModel();
            // If 3, rent a car.
            else if (ch.equals("3")) rentCar(name);
            // If 4, return a car.
            else if (ch.equals("4")) returnCar(name);
            // If 5, show rental history.
            else if (ch.equals("5")) showRentalHistory(name);
            // Otherwise, invalid.
            else System.out.println("  Invalid choice.");
        } // End of while.
    } // End of userMenuLoop.

    // Show only cars that are available (isAvailable == true).
    static void showAvailableCars() {
        // Blank line.
        System.out.println();
        // Flag to know if we found any.
        boolean found = false;
        // Print table header.
        System.out.printf("  %-6s %-10s %-12s %-10s %-6s %10s%n",
                "ID", "Brand", "Model", "Type", "Seats", "Rs/day");
        // Print a line of 60 dashes.
        System.out.println("  " + "-".repeat(60));
        // Loop through all cars.
        for (Car car : cars) {
            // If car is available...
            if (car.isAvailable) {
                // Print its details.
                System.out.printf("  %-6s %-10s %-12s %-10s %-6d %10.0f%n",
                        car.carId, car.brand, car.model,
                        car.type, car.seatingCapacity, car.rentPerDay);
                // Set flag to true.
                found = true;
            } // End of if.
        } // End of for.
        // If no car was found, print message.
        if (!found) System.out.println("  No cars available right now.");
        // Blank line.
        System.out.println();
    } // End of showAvailableCars.

    // Search cars by brand or model (partial match, case‑insensitive).
    static void searchCarByModel() {
        // Blank line.
        System.out.println();
        // Ask for keyword.
        System.out.print("  Enter brand or model: ");
        // Read keyword, trim, convert to lowercase.
        String kw = sc.nextLine().trim().toLowerCase();
        // If empty, error.
        if (kw.isEmpty()) {
            System.out.println("  Nothing entered.");
            return;
        } // End of if.
        // Flag for found matches.
        boolean found = false;
        // Print smaller table header.
        System.out.printf("  %-6s %-10s %-12s %10s %5s%n",
                "ID", "Brand", "Model", "Rs/day", "Avail");
        // Print 50 dashes.
        System.out.println("  " + "-".repeat(50));
        // Loop through all cars.
        for (Car car : cars) {
            // If brand or model contains the keyword...
            if (car.brand.toLowerCase().contains(kw)
                    || car.model.toLowerCase().contains(kw)) {
                // Print car details.
                System.out.printf("  %-6s %-10s %-12s %10.0f %5s%n",
                        car.carId, car.brand, car.model,
                        car.rentPerDay, car.isAvailable ? "Yes" : "No");
                found = true;
            } // End of if.
        } // End of for.
        // If none found, print message.
        if (!found) System.out.println("  No match for \"" + kw + "\".");
        // Blank line.
        System.out.println();
    } // End of searchCarByModel.

    // Find a Car object by its ID. Returns null if not found.
    static Car findCarById(String carId) {
        // Loop through all cars.
        for (Car car : cars) {
            // If IDs match (case‑insensitive), return the car.
            if (car.carId.equalsIgnoreCase(carId)) return car;
        } // End of for.
        // Not found.
        return null;
    } // End of findCarById.

    // Rent a car to the given customer.
    static void rentCar(String customerName) {
        // Blank line.
        System.out.println();
        // Show available cars first.
        showAvailableCars();
        // Ask for car ID.
        System.out.print("  Enter Car ID: ");
        String cid = sc.nextLine().trim();
        // Find the car.
        Car car = findCarById(cid);
        // If car not found, error.
        if (car == null) {
            System.out.println("  Car not found.");
            return;
        } // End of if.
        // If car not available, error.
        if (!car.isAvailable) {
            System.out.println("  That car is not available.");
            return;
        } // End of if.
        // Ask number of days (using helper readInt).
        int days = readInt("  How many days? ", 1, 365);
        // Generate unique rental ID (R001, R002, ...).
        String newId = "R" + String.format("%03d", rentals.size() + rentalHistory.size() + 1);
        // Get today's date.
        LocalDate startDate = LocalDate.now();
        // Calculate due date.
        LocalDate dueDate   = startDate.plusDays(days);
        // Calculate total cost.
        double totalCost    = days * car.rentPerDay;
        // Print booking summary.
        System.out.println();
        System.out.println("  Rental ID : " + newId);
        System.out.println("  Car       : " + car.brand + " " + car.model);
        System.out.println("  From      : " + startDate);
        System.out.println("  Due back  : " + dueDate);
        System.out.printf ("  Total     : Rs %.0f%n", totalCost);
        System.out.println();
        // Ask for confirmation.
        if (!readYesNo("  Confirm booking? (y/n): ")) {
            System.out.println("  Booking cancelled.");
            return;
        } // End of if.
        // Mark car as unavailable.
        car.isAvailable = false;
        // Create a new Rental object and add to active rentals list.
        rentals.add(new Rental(newId, cid, customerName, days, totalCost, startDate, dueDate));
        // Save cars.json.
        saveCarsQuiet();
        // Save rentals.json.
        saveRentalsQuiet();
        // Success message.
        System.out.println("  Done! Rental ID: " + newId + "  Return by: " + dueDate);
        System.out.println();
    } // End of rentCar.

    // Return a rented car.
    static void returnCar(String customerName) {
        // Blank line.
        System.out.println();
        // Collect this customer's active rentals.
        ArrayList<Rental> myRentals = new ArrayList<>();
        for (Rental r : rentals) {
            if (r.customerName.equalsIgnoreCase(customerName)) myRentals.add(r);
        } // End of for.
        // If none, error.
        if (myRentals.isEmpty()) {
            System.out.println("  No active rentals under \"" + customerName + "\".");
            return;
        } // End of if.
        // Show table of customer's active rentals.
        System.out.printf("  %-8s %-8s %-12s %10s%n",
                "Rental ID", "Car ID", "Due Date", "Cost Rs");
        System.out.println("  " + "-".repeat(44));
        for (Rental r : myRentals) {
            System.out.printf("  %-8s %-8s %-12s %10.0f%n",
                    r.rentalId, r.carId, r.dueDate, r.totalCost);
        } // End of for.
        System.out.println();
        // Ask for rental ID to return.
        System.out.print("  Enter Rental ID to return: ");
        String rid = sc.nextLine().trim();
        // Search in the full active list.
        Rental target = null;
        int targetIdx = -1;
        for (int i = 0; i < rentals.size(); i++) {
            Rental r = rentals.get(i);
            if (r.rentalId.equalsIgnoreCase(rid)
                    && r.customerName.equalsIgnoreCase(customerName)) {
                target = r;
                targetIdx = i;
                break;
            } // End of if.
        } // End of for.
        // If not found, error.
        if (target == null) {
            System.out.println("  Rental ID not found.");
            return;
        } // End of if.
        // Calculate late fee if returned after due date.
        LocalDate today = LocalDate.now();
        long lateDays = 0;
        double lateFee = 0;
        Car rentedCar = findCarById(target.carId);
        if (today.isAfter(target.dueDate)) {
            // Number of days between due date and today.
            lateDays = target.dueDate.until(today).getDays();
            // Late fee = late days × daily rate × 0.5.
            lateFee = lateDays * rentedCar.rentPerDay * 0.5;
        } // End of if.
        double finalCost = target.totalCost + lateFee;
        // Print return summary.
        System.out.println();
        System.out.println("  Due date    : " + target.dueDate);
        System.out.println("  Return date : " + today);
        if (lateDays > 0) {
            System.out.println("  Late days   : " + lateDays);
            System.out.printf ("  Late fee    : Rs %.0f%n", lateFee);
        } else {
            System.out.println("  Returned on time, no late fee.");
        } // End of if-else.
        System.out.printf("  Total paid  : Rs %.0f%n", finalCost);
        System.out.println();
        // Confirm return.
        if (!readYesNo("  Confirm return? (y/n): ")) {
            System.out.println("  Return cancelled.");
            return;
        } // End of if.
        // Update rental record.
        target.totalCost = finalCost;
        target.returnDate = today;
        // Move to history.
        rentalHistory.add(target);
        rentals.remove(targetIdx);
        // Mark car as available.
        if (rentedCar != null) rentedCar.isAvailable = true;
        // Save all changes.
        saveCarsQuiet();
        saveRentalsQuiet();
        saveHistoryQuiet();
        // Thank you message.
        System.out.println("  Car returned. Thanks, " + customerName + "!");
        System.out.println();
    } // End of returnCar.

    // Show rental history for a customer.
    static void showRentalHistory(String customerName) {
        // Blank line.
        System.out.println();
        boolean found = false;
        System.out.println("  History for: " + customerName);
        // Print table header.
        System.out.printf("  %-8s %-8s %-12s %-12s %10s%n",
                "Rental ID", "Car ID", "Due Date", "Returned", "Total Rs");
        System.out.println("  " + "-".repeat(56));
        // Loop through all past rentals.
        for (Rental r : rentalHistory) {
            if (r.customerName.equalsIgnoreCase(customerName)) {
                // Format return date or "N/A".
                String retDate = (r.returnDate != null) ? r.returnDate.toString() : "N/A";
                System.out.printf("  %-8s %-8s %-12s %-12s %10.0f%n",
                        r.rentalId, r.carId, r.dueDate, retDate, r.totalCost);
                found = true;
            } // End of if.
        } // End of for.
        if (!found) System.out.println("  No history found.");
        System.out.println();
    } // End of showRentalHistory.

    // Generate revenue report (total revenue, most rented car, counts) and save to report.txt.
    static void generateReport() {
        // Blank line.
        System.out.println();
        // If no past rentals, cannot report.
        if (rentalHistory.isEmpty()) {
            System.out.println("  No completed rentals yet.");
            return;
        } // End of if.
        // Calculate total revenue.
        double revenue = 0;
        for (Rental r : rentalHistory) {
            revenue += r.totalCost;
        } // End of for.
        // Find most rented car (by counting carId occurrences).
        String topCarId = "";
        int topCount = 0;
        for (Rental r : rentalHistory) {
            int count = 0;
            for (Rental r2 : rentalHistory) {
                if (r2.carId.equals(r.carId)) count++;
            } // End of inner for.
            if (count > topCount) {
                topCount = count;
                topCarId = r.carId;
            } // End of if.
        } // End of outer for.
        // Get model name of the most rented car.
        String topModel = topCarId;
        Car topCar = findCarById(topCarId);
        if (topCar != null) topModel = topCar.brand + " " + topCar.model;
        // Number of currently active rentals.
        int activeCount = rentals.size();
        // Print report to console.
        System.out.println("  ======= REVENUE REPORT =======");
        System.out.printf ("  Total Revenue   : Rs %.0f%n", revenue);
        System.out.println("  Most Rented     : " + topModel + " (" + topCount + " times)");
        System.out.println("  Active Rentals  : " + activeCount);
        System.out.println("  Past Rentals    : " + rentalHistory.size());
        System.out.println("  ==============================");
        System.out.println();
        // Save report to report.txt file.
        try {
            String txt =
                "Total Revenue   : Rs " + (int) revenue + "\n" +
                "Most Rented     : " + topModel + " (" + topCount + " times)\n" +
                "Active Rentals  : " + activeCount + "\n" +
                "Past Rentals    : " + rentalHistory.size() + "\n";
            Files.writeString(Path.of("report.txt"), txt, StandardCharsets.UTF_8);
            System.out.println("  Report saved to report.txt");
            System.out.println();
        } catch (IOException e) {
            System.out.println("  Could not save report: " + e.getMessage());
        } // End of try-catch.
    } // End of generateReport.

    // ==================== ABDUL SALAM's RENTAL FILE I/O (JSON) ====================
    // Load active rentals from rentals.json.
    static void loadRentalsFromFile() {
        try {
            // If file doesn't exist, skip.
            if (!Files.exists(RENTALS_FILE)) return;
            // Read whole JSON string.
            String json = Files.readString(RENTALS_FILE, StandardCharsets.UTF_8);
            // Parse into ArrayList<Rental>.
            rentals = RentalJson.parseRentals(json);
            System.out.println("  Loaded " + rentals.size() + " active rental(s).");
        } catch (IOException e) {
            System.out.println("  Could not read rentals.json.");
            rentals = new ArrayList<>();
        } // End of try-catch.
    } // End of loadRentalsFromFile.

    // Save active rentals to rentals.json.
    static void saveRentalsQuiet() {
        try {
            // Convert rentals list to JSON and write.
            Files.writeString(RENTALS_FILE, RentalJson.toJson(rentals), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("  Error saving rentals: " + e.getMessage());
        } // End of try-catch.
    } // End of saveRentalsQuiet.

    // Load past rentals from rentalHistory.json.
    static void loadHistoryFromFile() {
        try {
            if (!Files.exists(HISTORY_FILE)) return;
            String json = Files.readString(HISTORY_FILE, StandardCharsets.UTF_8);
            rentalHistory = RentalJson.parseRentals(json);
            System.out.println("  Loaded " + rentalHistory.size() + " past rental(s).");
        } catch (IOException e) {
            System.out.println("  Could not read rentalHistory.json.");
            rentalHistory = new ArrayList<>();
        } // End of try-catch.
    } // End of loadHistoryFromFile.

    // Save past rentals to rentalHistory.json.
    static void saveHistoryQuiet() {
        try {
            Files.writeString(HISTORY_FILE, RentalJson.toJson(rentalHistory), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("  Error saving history: " + e.getMessage());
        } // End of try-catch.
    } // End of saveHistoryQuiet.

    // ==================== FAZ's HELPER METHODS ====================
    // Safely read an integer between min and max. Repeats until valid.
    static int readInt(String prompt, int min, int max) {
        while (true) {
            System.out.print(prompt);
            String line = sc.nextLine().trim();
            try {
                int v = Integer.parseInt(line);
                if (v >= min && v <= max) return v;
            } catch (NumberFormatException e) { }
            System.out.println("  Enter a number between " + min + " and " + max + ".");
        } // End of while.
    } // End of readInt.

    // Read a yes/no answer. Returns true for y/yes, false for n/no.
    static boolean readYesNo(String prompt) {
        while (true) {
            System.out.print(prompt);
            String line = sc.nextLine().trim().toLowerCase();
            if (line.equals("y") || line.equals("yes")) return true;
            if (line.equals("n") || line.equals("no")) return false;
            System.out.println("  Answer y or n.");
        } // End of while.
    } // End of readYesNo.

    // Helper to read a double with validation (used in addCar/editCar).
    static double readDouble(String prompt, double min, double max) {
        while (true) {
            System.out.print(prompt);
            String line = sc.nextLine().trim();
            try {
                double v = Double.parseDouble(line);
                if (v >= min && v <= max) return v;
            } catch (NumberFormatException e) { }
            System.out.println("  Enter a valid number.");
        } // End of while.
    } // End of readDouble.

    // ==================== MAHEEN's ADMIN FLOW ====================
    // Handle admin login and then show admin menu.
    static void adminFlow() {
        System.out.print("  Enter admin access code: ");
        String code = sc.nextLine().trim();
        if (!code.equals(ADMIN_ACCESS_CODE)) {
            System.out.println("\n  Access denied.\n");
            return;
        } // End of if.
        System.out.println("\n  Welcome, Admin.\n");
        adminMenu();
    } // End of adminFlow.

    // Admin menu – loops until user chooses 0 (Back).
    static void adminMenu() {
        while (true) {
            System.out.println("\n  === ADMIN MENU ===");
            System.out.println("  1  View all cars");
            System.out.println("  2  Add a car");
            System.out.println("  3  Edit a car");
            System.out.println("  4  Delete a car");
            System.out.println("  5  Generate rental report");
            System.out.println("  0  Back to main menu");
            System.out.print("  Choose: ");
            String choice = sc.nextLine().trim();
            if (choice.equals("0")) break;
            else if (choice.equals("1")) viewAllCars();
            else if (choice.equals("2")) addCar();
            else if (choice.equals("3")) editCar();
            else if (choice.equals("4")) deleteCar();
            else if (choice.equals("5")) generateReport();
            else System.out.println("  Invalid choice.");
        } // End of while.
    } // End of adminMenu.

    // ==================== MAHEEN's CAR CRUD ====================
    // View all cars (including unavailable) in a formatted table.
    static void viewAllCars() {
        System.out.println("\n  Current Car List:\n");
        if (cars.isEmpty()) {
            System.out.println("  No cars.\n");
            return;
        } // End of if.
        // Print header.
        System.out.printf("  %-6s %-10s %-12s %-8s %-10s %-12s %-6s %-5s %-10s %s%n",
                "ID", "Brand", "Model", "Type", "Color", "Reg No", "Year", "Seats", "Rs/day", "Avail");
        // Loop through all cars.
        for (Car c : cars) {
            System.out.printf("  %-6s %-10s %-12s %-8s %-10s %-12s %-6d %-5d %-10.0f %s%n",
                    c.carId, c.brand, c.model, c.type, c.color, c.registrationNo,
                    c.year, c.seatingCapacity, c.rentPerDay, c.isAvailable ? "Yes" : "No");
        } // End of for.
        System.out.println();
    } // End of viewAllCars.

    // Add a new car.
    static void addCar() {
        System.out.print("  Car ID: ");
        String id = sc.nextLine().trim();
        if (findCarIndexById(id) >= 0) {
            System.out.println("  ID already exists.\n");
            return;
        } // End of if.
        System.out.print("  Brand: "); String brand = sc.nextLine().trim();
        System.out.print("  Model: "); String model = sc.nextLine().trim();
        System.out.print("  Type: "); String type = sc.nextLine().trim();
        System.out.print("  Color: "); String color = sc.nextLine().trim();
        System.out.print("  Registration No: "); String reg = sc.nextLine().trim();
        int year = readInt("  Year (1990-2030): ", 1990, 2030);
        int seats = readInt("  Seats (2-15): ", 2, 15);
        double rent = readDouble("  Rent per day (PKR): ", 0, 500000);
        boolean avail = readYesNo("  Available now? (y/n): ");
        cars.add(new Car(id, brand, model, type, color, reg, year, seats, rent, avail));
        saveCarsQuiet();
        System.out.println("  Car added.\n");
    } // End of addCar.

    // Edit an existing car (only if not currently rented).
    static void editCar() {
        System.out.print("  Enter Car ID to edit: ");
        String id = sc.nextLine().trim();
        int idx = findCarIndexById(id);
        if (idx < 0) {
            System.out.println("  Not found.\n");
            return;
        } // End of if.
        Car c = cars.get(idx);
        if (isCarCurrentlyRented(c.carId)) {
            System.out.println("  Cannot edit – car is currently rented.\n");
            return;
        } // End of if.
        System.out.println("\n  Current: " + c.carId + " | " + c.brand + " " + c.model);
        // Update each field if user enters something.
        System.out.print("  New brand (leave empty to keep): ");
        String brand = sc.nextLine().trim(); if (!brand.isEmpty()) c.brand = brand;
        System.out.print("  New model: "); String model = sc.nextLine().trim(); if (!model.isEmpty()) c.model = model;
        System.out.print("  New type: "); String type = sc.nextLine().trim(); if (!type.isEmpty()) c.type = type;
        System.out.print("  New color: "); String color = sc.nextLine().trim(); if (!color.isEmpty()) c.color = color;
        System.out.print("  New registration: "); String reg = sc.nextLine().trim(); if (!reg.isEmpty()) c.registrationNo = reg;
        c.year = readInt("  New year (" + c.year + "): ", 1990, 2030);
        c.seatingCapacity = readInt("  New seats (" + c.seatingCapacity + "): ", 2, 15);
        c.rentPerDay = readDouble("  New rent (" + (int)c.rentPerDay + "): ", 0, 500000);
        c.isAvailable = readYesNo("  Available? (y/n): ");
        saveCarsQuiet();
        System.out.println("  Car updated.\n");
    } // End of editCar.

    // Delete a car (only if not rented).
    static void deleteCar() {
        System.out.print("  Enter Car ID to delete: ");
        String id = sc.nextLine().trim();
        int idx = findCarIndexById(id);
        if (idx < 0) {
            System.out.println("  Not found.\n");
            return;
        } // End of if.
        Car c = cars.get(idx);
        if (isCarCurrentlyRented(c.carId)) {
            System.out.println("  Cannot delete – car is currently rented.\n");
            return;
        } // End of if.
        System.out.print("  Confirm delete (y/n): ");
        if (!sc.nextLine().trim().equalsIgnoreCase("y")) {
            System.out.println("  Cancelled.\n");
            return;
        } // End of if.
        cars.remove(idx);
        saveCarsQuiet();
        System.out.println("  Car deleted.\n");
    } // End of deleteCar.

    // Check if a car is currently rented (appears in active rentals list).
    static boolean isCarCurrentlyRented(String carId) {
        for (Rental r : rentals) {
            if (r.carId.equals(carId)) return true;
        } // End of for.
        return false;
    } // End of isCarCurrentlyRented.

    // Find index of a car by its ID (returns -1 if not found).
    static int findCarIndexById(String id) {
        for (int i = 0; i < cars.size(); i++) {
            if (cars.get(i).carId.equalsIgnoreCase(id)) return i;
        } // End of for.
        return -1;
    } // End of findCarIndexById.

    // ==================== MAHEEN's JSON FILE I/O FOR CARS ====================
    // Load cars from cars.json. If file missing, start with empty list.
    static void loadCarsFromFile() {
        try {
            if (!Files.exists(CARS_FILE)) {
                System.out.println("  cars.json not found. Starting with empty list.\n");
                return;
            } // End of if.
            String json = Files.readString(CARS_FILE, StandardCharsets.UTF_8);
            cars = SimpleJson.parseCars(json);
            System.out.println("  Loaded " + cars.size() + " car(s).\n");
        } catch (IOException e) {
            System.out.println("  Could not read cars.json.\n");
            cars = new ArrayList<>();
        } catch (Exception e) {
            System.out.println("  cars.json broken.\n");
            cars = new ArrayList<>();
        } // End of try-catch.
    } // End of loadCarsFromFile.

    // Save the current car list to cars.json.
    static void saveCarsQuiet() {
        try {
            Files.writeString(CARS_FILE, SimpleJson.toJson(cars), StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("  Error saving cars.json: " + e.getMessage());
        } // End of try-catch.
    } // End of saveCarsQuiet.

    // ==================== MAHEEN's Car CLASS ====================
    // Represents a car with all its properties.
    static class Car {
        String carId; String brand; String model; String type; String color;
        String registrationNo; int year; int seatingCapacity; double rentPerDay; boolean isAvailable;
        // Constructor – called when we create a new Car object.
        Car(String carId, String brand, String model, String type, String color,
            String registrationNo, int year, int seatingCapacity, double rentPerDay, boolean isAvailable) {
            this.carId = carId; this.brand = brand; this.model = model; this.type = type; this.color = color;
            this.registrationNo = registrationNo; this.year = year; this.seatingCapacity = seatingCapacity;
            this.rentPerDay = rentPerDay; this.isAvailable = isAvailable;
        } // End of constructor.
    } // End of Car class.

    // ==================== ABDUL SALAM's Rental CLASS ====================
    // Represents a rental transaction.
    static class Rental {
        String    rentalId;
        String    carId;
        String    customerName;
        int       days;
        double    totalCost;
        LocalDate startDate;
        LocalDate dueDate;
        LocalDate returnDate;   // null until returned.
        // Constructor.
        Rental(String rId, String cId, String cName,
               int numDays, double cost,
               LocalDate sDate, LocalDate dDate) {
            rentalId     = rId;
            carId        = cId;
            customerName = cName;
            days         = numDays;
            totalCost    = cost;
            startDate    = sDate;
            dueDate      = dDate;
            returnDate   = null;
        } // End of constructor.
        // Optional toString for debugging.
        public String toString() {
            return rentalId + " | " + carId + " | " + customerName
                 + " | Due: " + dueDate + " | Rs " + (int) totalCost;
        } // End of toString.
    } // End of Rental class.

    // ==================== MAHEEN's SimpleJson (for cars) ====================
    // Handles conversion between ArrayList<Car> and JSON.
    static class SimpleJson {
        // Convert a list of Car objects to a JSON string.
        static String toJson(ArrayList<Car> list) {
            StringBuilder sb = new StringBuilder("[\n");
            for (int i = 0; i < list.size(); i++) {
                Car c = list.get(i);
                sb.append("  {\n");
                sb.append("    \"carId\": \"").append(escape(c.carId)).append("\",\n");
                sb.append("    \"brand\": \"").append(escape(c.brand)).append("\",\n");
                sb.append("    \"model\": \"").append(escape(c.model)).append("\",\n");
                sb.append("    \"type\": \"").append(escape(c.type)).append("\",\n");
                sb.append("    \"color\": \"").append(escape(c.color)).append("\",\n");
                sb.append("    \"registrationNo\": \"").append(escape(c.registrationNo)).append("\",\n");
                sb.append("    \"year\": ").append(c.year).append(",\n");
                sb.append("    \"seatingCapacity\": ").append(c.seatingCapacity).append(",\n");
                sb.append("    \"rentPerDay\": ").append(c.rentPerDay).append(",\n");
                sb.append("    \"isAvailable\": ").append(c.isAvailable ? "true" : "false").append("\n");
                sb.append("  }");
                if (i != list.size() - 1) sb.append(",");
                sb.append("\n");
            } // End of for.
            sb.append("]\n");
            return sb.toString();
        } // End of toJson.

        // Parse a JSON string into an ArrayList<Car>.
        static ArrayList<Car> parseCars(String json) {
            ArrayList<Car> list = new ArrayList<>();
            if (json == null || json.trim().isEmpty() || json.trim().equals("[]")) return list;
            ArrayList<String> objects = splitObjects(json);
            for (String obj : objects) {
                String carId = getString(obj, "carId");
                if (carId.isEmpty()) continue;
                list.add(new Car(
                        carId,
                        getString(obj, "brand"),
                        getString(obj, "model"),
                        getString(obj, "type"),
                        getString(obj, "color"),
                        getString(obj, "registrationNo"),
                        getInt(obj, "year"),
                        getInt(obj, "seatingCapacity"),
                        getDouble(obj, "rentPerDay"),
                        getBoolean(obj, "isAvailable")
                ));
            } // End of for.
            return list;
        } // End of parseCars.

        // Split a JSON array into individual object strings (between { }).
        static ArrayList<String> splitObjects(String arrayJson) {
            ArrayList<String> objs = new ArrayList<>();
            boolean inString = false;
            int depth = 0;
            int start = -1;
            for (int i = 0; i < arrayJson.length(); i++) {
                char c = arrayJson.charAt(i);
                if (c == '"' && (i == 0 || arrayJson.charAt(i-1) != '\\')) inString = !inString;
                if (inString) continue;
                if (c == '{') {
                    if (depth == 0) start = i;
                    depth++;
                } else if (c == '}') {
                    depth--;
                    if (depth == 0 && start != -1) {
                        objs.add(arrayJson.substring(start, i+1));
                        start = -1;
                    }
                } // End of if-else.
            } // End of for.
            return objs;
        } // End of splitObjects.

        // Get string value for a given key from a JSON object.
        static String getString(String objJson, String key) {
            String pattern = "\"" + key + "\"";
            int keyPos = objJson.indexOf(pattern);
            if (keyPos == -1) return "";
            int colon = objJson.indexOf(":", keyPos);
            if (colon == -1) return "";
            int firstQuote = objJson.indexOf("\"", colon+1);
            if (firstQuote == -1) return "";
            int i = firstQuote+1;
            StringBuilder out = new StringBuilder();
            while (i < objJson.length()) {
                char c = objJson.charAt(i);
                if (c == '"' && objJson.charAt(i-1) != '\\') break;
                out.append(c);
                i++;
            } // End of while.
            return unescape(out.toString());
        } // End of getString.

        // Get integer value for a given key.
        static int getInt(String objJson, String key) {
            String pattern = "\"" + key + "\"";
            int keyPos = objJson.indexOf(pattern);
            if (keyPos == -1) return 0;
            int colon = objJson.indexOf(":", keyPos);
            if (colon == -1) return 0;
            int i = colon+1;
            while (i < objJson.length() && Character.isWhitespace(objJson.charAt(i))) i++;
            int start = i;
            while (i < objJson.length() && (Character.isDigit(objJson.charAt(i)) || objJson.charAt(i) == '-')) i++;
            try {
                return Integer.parseInt(objJson.substring(start, i).trim());
            } catch (Exception e) { return 0; }
        } // End of getInt.

        // Get double value for a given key.
        static double getDouble(String objJson, String key) {
            String pattern = "\"" + key + "\"";
            int keyPos = objJson.indexOf(pattern);
            if (keyPos == -1) return 0;
            int colon = objJson.indexOf(":", keyPos);
            if (colon == -1) return 0;
            int i = colon+1;
            while (i < objJson.length() && Character.isWhitespace(objJson.charAt(i))) i++;
            int start = i;
            while (i < objJson.length() && (Character.isDigit(objJson.charAt(i)) || objJson.charAt(i) == '-' || objJson.charAt(i) == '.')) i++;
            try {
                return Double.parseDouble(objJson.substring(start, i).trim());
            } catch (Exception e) { return 0; }
        } // End of getDouble.

        // Get boolean value for a given key.
        static boolean getBoolean(String objJson, String key) {
            String pattern = "\"" + key + "\"";
            int keyPos = objJson.indexOf(pattern);
            if (keyPos == -1) return false;
            int colon = objJson.indexOf(":", keyPos);
            if (colon == -1) return false;
            int i = colon+1;
            while (i < objJson.length() && Character.isWhitespace(objJson.charAt(i))) i++;
            if (objJson.regionMatches(i, "true", 0, 4)) return true;
            if (objJson.regionMatches(i, "false", 0, 5)) return false;
            return false;
        } // End of getBoolean.

        // Escape special characters for JSON (double quotes, backslashes, newlines).
        static String escape(String s) {
            if (s == null) return "";
            return s.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t");
        } // End of escape.

        // Unescape JSON string when reading.
        static String unescape(String s) {
            if (s == null) return "";
            return s.replace("\\n", "\n")
                    .replace("\\r", "\r")
                    .replace("\\t", "\t")
                    .replace("\\\"", "\"")
                    .replace("\\\\", "\\");
        } // End of unescape.
    } // End of SimpleJson class.

    // ==================== ABDUL SALAM's RentalJson (for rentals) ====================
    // Handles conversion between ArrayList<Rental> and JSON.
    static class RentalJson {
        // Convert a list of Rental objects to a JSON string.
        static String toJson(ArrayList<Rental> list) {
            StringBuilder sb = new StringBuilder();
            sb.append("[\n");
            for (int i = 0; i < list.size(); i++) {
                Rental r = list.get(i);
                sb.append("  {\n");
                sb.append("    \"rentalId\": \""     ).append(r.rentalId    ).append("\",\n");
                sb.append("    \"carId\": \""        ).append(r.carId       ).append("\",\n");
                sb.append("    \"customerName\": \"" ).append(SimpleJson.escape(r.customerName)).append("\",\n");
                sb.append("    \"days\": "           ).append(r.days        ).append(",\n");
                sb.append("    \"totalCost\": "      ).append(r.totalCost   ).append(",\n");
                sb.append("    \"startDate\": \""    ).append(r.startDate   ).append("\",\n");
                sb.append("    \"dueDate\": \""      ).append(r.dueDate     ).append("\",\n");
                sb.append("    \"returnDate\": \""   )
                  .append(r.returnDate != null ? r.returnDate.toString() : "")
                  .append("\"\n");
                sb.append("  }");
                if (i != list.size() - 1) sb.append(",");
                sb.append("\n");
            } // End of for.
            sb.append("]\n");
            return sb.toString();
        } // End of toJson.

        // Parse a JSON string into an ArrayList<Rental>.
        static ArrayList<Rental> parseRentals(String json) {
            ArrayList<Rental> list = new ArrayList<>();
            if (json == null || json.trim().isEmpty() || json.trim().equals("[]")) return list;
            ArrayList<String> objects = SimpleJson.splitObjects(json);
            for (String obj : objects) {
                String rId = SimpleJson.getString(obj, "rentalId");
                if (rId == null || rId.isEmpty()) continue;
                String cName     = SimpleJson.getString(obj, "customerName");
                String cId       = SimpleJson.getString(obj, "carId");
                int    numDays   = SimpleJson.getInt   (obj, "days");
                double cost      = SimpleJson.getDouble(obj, "totalCost");
                String startStr  = SimpleJson.getString(obj, "startDate");
                String dueStr    = SimpleJson.getString(obj, "dueDate");
                String returnStr = SimpleJson.getString(obj, "returnDate");
                LocalDate sDate = (startStr != null && !startStr.isEmpty())
                                  ? LocalDate.parse(startStr) : LocalDate.now();
                LocalDate dDate = (dueStr   != null && !dueStr.isEmpty())
                                  ? LocalDate.parse(dueStr)   : LocalDate.now();
                Rental r = new Rental(rId, cId, cName, numDays, cost, sDate, dDate);
                if (returnStr != null && !returnStr.isEmpty())
                    r.returnDate = LocalDate.parse(returnStr);
                list.add(r);
            } // End of for.
            return list;
        } // End of parseRentals.
    } // End of RentalJson class.
} // End of CarRentalSystem class.