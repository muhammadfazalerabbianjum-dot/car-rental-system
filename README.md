# Car Rental System — a console application in a single Java file

A console project with no build tool, no database and no dependencies: one
992-line `CarRentalSystem.java`, plain `javac`/`java`, and JSON files on disk as
the store.

## Run it

```
javac CarRentalSystem.java
java CarRentalSystem
```

Any JDK on your PATH will do — the file uses only the standard library. The
admin password is in `Documentation and running/To run.txt`.

## What it does

Two flows behind one menu.

**Customer** — list the available fleet, search by model, rent a car with a date
range and a computed bill, return it, and read back their own rental history.

**Admin** (password-gated) — see every car including the rented ones, add a car,
edit a car, delete a car (refused while that car is out on rent), and generate a
report.

## Data files

| File | Holds |
| --- | --- |
| `cars.json` | The fleet: id, brand, model, type, colour, registration, year, seats, daily rate, availability |
| `rentals.json` | Rentals currently open |
| `rentalHistory.json` | Every rental that was returned |
| `report.txt` | Written by the admin report at runtime; generated, so not tracked |

Each file is read at startup and rewritten on change, so the app keeps its state
between runs. `SimpleJson` and `RentalJson` inside the class do the writing and
parsing by hand — no JSON library is used.

## Structure

Everything lives in `CarRentalSystem.java`: the `Car` and `Rental` model
classes, the JSON writers and parsers, input helpers that re-prompt instead of
crashing on bad input, and the menu functions — `userFlow`, `rentCar`,
`returnCar`, `showRentalHistory`, `adminFlow`, `addCar`, `editCar`, `deleteCar`,
`generateReport`.

Viewing only — see `LICENSE`.
