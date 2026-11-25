from parser import parse_instruction
from hazard import HazardDetector


program = [
    "ADD R1, R2, R3",
    "SUB R4, R1, R5",
    "MUL R6, R4, R2",
    "LOAD R7, 0(R6)",
    "ADD R8, R7, R9"
]


instructions = [
    parse_instruction(text)
    for text in program
]


hazards = HazardDetector.detect_data_hazards(instructions)


print("\n========== DATA HAZARD DETECTION ==========\n")


if not hazards:

    print("No data hazards detected.")

else:

    for number, hazard in enumerate(hazards, start=1):

        print(f"Hazard {number}")
        print("Type     :", hazard["type"])
        print("Producer :", hazard["producer"])
        print("Consumer :", hazard["consumer"])
        print("Register :", hazard["register"])

        print("-" * 50)


print("\nTotal Data Hazards:", len(hazards))