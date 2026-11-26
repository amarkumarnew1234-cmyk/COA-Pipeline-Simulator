from parser import parse_instruction
from program import Program
from pipeline import PipelineSimulator
from cpu import CPU
from performance import PerformanceAnalyzer


passed = 0
failed = 0


def check(name, condition):
    global passed, failed

    if condition:
        print(f"[PASS] {name}")
        passed += 1
    else:
        print(f"[FAIL] {name}")
        failed += 1


print("\n" + "=" * 65)
print("        COA PIPELINE SIMULATOR - COMPLETE TEST SUITE")
print("=" * 65)


# ============================================================
# TEST 1 - PARSER
# ============================================================

print("\n--- TEST 1: INSTRUCTION PARSER ---")

instruction = parse_instruction(
    "ADD R1, R2, R3"
)

check(
    "ADD opcode parsed",
    instruction.opcode == "ADD"
)

check(
    "Destination register parsed",
    instruction.destination == "R1"
)

check(
    "Source registers parsed",
    instruction.source1 == "R2"
    and instruction.source2 == "R3"
)


# ============================================================
# TEST 2 - INVALID INSTRUCTION
# ============================================================

print("\n--- TEST 2: INPUT VALIDATION ---")

try:
    parse_instruction(
        "ADD R20, R1, R2"
    )

    check(
        "Invalid register rejected",
        False
    )

except ValueError:

    check(
        "Invalid register rejected",
        True
    )


# ============================================================
# TEST 3 - ALU
# ============================================================

print("\n--- TEST 3: ALU EXECUTION ---")

cpu = CPU()

cpu.set_register("R1", 10)
cpu.set_register("R2", 20)
cpu.set_register("R3", 5)

cpu.execute(
    parse_instruction(
        "ADD R4, R1, R2"
    )
)

cpu.execute(
    parse_instruction(
        "SUB R5, R4, R3"
    )
)

cpu.execute(
    parse_instruction(
        "MUL R6, R5, R3"
    )
)

check(
    "ADD execution",
    cpu.get_register("R4") == 30
)

check(
    "SUB execution",
    cpu.get_register("R5") == 25
)

check(
    "MUL execution",
    cpu.get_register("R6") == 125
)


# ============================================================
# TEST 4 - MEMORY
# ============================================================

print("\n--- TEST 4: LOAD / STORE ---")

cpu.set_register("R10", 100)

cpu.execute(
    parse_instruction(
        "STORE R6, 4(R10)"
    )
)

cpu.execute(
    parse_instruction(
        "LOAD R7, 4(R10)"
    )
)

check(
    "STORE writes correct memory value",
    cpu.get_memory(104) == 125
)

check(
    "LOAD reads correct memory value",
    cpu.get_register("R7") == 125
)


# ============================================================
# TEST 5 - R0
# ============================================================

print("\n--- TEST 5: ZERO REGISTER ---")

cpu.set_register(
    "R0",
    999
)

check(
    "R0 remains zero",
    cpu.get_register("R0") == 0
)


# ============================================================
# TEST 6 - IDEAL PIPELINE
# ============================================================

print("\n--- TEST 6: IDEAL PIPELINE ---")

program = Program([
    "ADD R1, R2, R3",
    "SUB R4, R5, R6",
    "MUL R7, R8, R9"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)

simulator.run()

check(
    "3 instructions complete in 7 ideal cycles",
    len(simulator.history) == 7
)

check(
    "Ideal pipeline has zero data stalls",
    simulator.data_stalls == 0
)


# ============================================================
# TEST 7 - RAW WITHOUT FORWARDING
# ============================================================

print(
    "\n--- TEST 7: RAW HAZARD WITHOUT FORWARDING ---"
)

program = Program([
    "ADD R1, R2, R3",
    "SUB R4, R1, R5",
    "MUL R6, R4, R2"
])

simulator = PipelineSimulator(
    program,
    forwarding=False,
    shared_memory=False
)

simulator.run()

check(
    "Two RAW hazards detected",
    len(simulator.data_hazards) == 2
)

check(
    "Four stalls without forwarding",
    simulator.data_stalls == 4
)

check(
    "Execution requires 11 cycles",
    len(simulator.history) == 11
)


# ============================================================
# TEST 8 - RAW WITH FORWARDING
# ============================================================

print(
    "\n--- TEST 8: RAW HAZARD WITH FORWARDING ---"
)

program = Program([
    "ADD R1, R2, R3",
    "SUB R4, R1, R5",
    "MUL R6, R4, R2"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)

simulator.run()

check(
    "Dependencies still detected",
    len(simulator.data_hazards) == 2
)

check(
    "Arithmetic forwarding removes stalls",
    simulator.data_stalls == 0
)

check(
    "Forwarded execution takes 7 cycles",
    len(simulator.history) == 7
)


# ============================================================
# TEST 9 - LOAD-USE HAZARD
# ============================================================

print(
    "\n--- TEST 9: LOAD-USE HAZARD ---"
)

program = Program([
    "LOAD R1, 0(R2)",
    "ADD R3, R1, R4",
    "SUB R5, R3, R6"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)

simulator.set_register(
    "R2",
    100
)

simulator.set_memory(
    100,
    50
)

simulator.run()

check(
    "LOAD-use dependency detected",
    len(simulator.data_hazards) >= 1
)

check(
    "LOAD-use requires one stall",
    simulator.data_stalls == 1
)

check(
    "LOAD-use program takes 8 cycles",
    len(simulator.history) == 8
)


# ============================================================
# TEST 10 - STRUCTURAL HAZARD
# ============================================================

print(
    "\n--- TEST 10: STRUCTURAL HAZARD ---"
)

program = Program([
    "LOAD R1, 0(R2)",
    "ADD R3, R4, R5",
    "SUB R6, R7, R8",
    "MUL R9, R10, R11",
    "ADD R12, R13, R14",
    "SUB R15, R3, R4"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=True
)

simulator.run()

check(
    "Shared memory conflict detected",
    len(simulator.structural_hazards) == 1
)

check(
    "Structural conflict causes one stall",
    simulator.structural_stalls == 1
)


# ============================================================
# TEST 11 - BRANCH TAKEN
# ============================================================

print(
    "\n--- TEST 11: BRANCH TAKEN ---"
)

program = Program([
    "ADD R4, R1, R2",
    "BEQ R4, R3, TARGET",
    "SUB R5, R1, R2",
    "MUL R6, R1, R2",
    "TARGET:",
    "ADD R7, R4, R3"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)

simulator.set_register("R1", 10)
simulator.set_register("R2", 20)
simulator.set_register("R3", 30)

simulator.run()

check(
    "Branch taken detected",
    len(simulator.control_hazards) == 1
    and simulator.control_hazards[0]["taken"]
)

check(
    "Two wrong-path instructions flushed",
    simulator.control_penalty == 2
)

check(
    "Wrong-path SUB not executed",
    simulator.cpu.get_register("R5") == 0
)

check(
    "Wrong-path MUL not executed",
    simulator.cpu.get_register("R6") == 0
)

check(
    "Branch target executed",
    simulator.cpu.get_register("R7") == 60
)


# ============================================================
# TEST 12 - BRANCH NOT TAKEN
# ============================================================

print(
    "\n--- TEST 12: BRANCH NOT TAKEN ---"
)

program = Program([
    "BEQ R1, R2, TARGET",
    "ADD R3, R4, R5",
    "SUB R6, R7, R8",
    "TARGET:",
    "MUL R9, R10, R11"
])

simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)

simulator.set_register("R1", 10)
simulator.set_register("R2", 20)

simulator.set_register("R4", 4)
simulator.set_register("R5", 5)

simulator.set_register("R7", 20)
simulator.set_register("R8", 3)

simulator.set_register("R10", 2)
simulator.set_register("R11", 6)

simulator.run()

check(
    "Branch correctly not taken",
    len(simulator.control_hazards) == 1
    and not simulator.control_hazards[0]["taken"]
)

check(
    "No flush penalty for not-taken branch",
    simulator.control_penalty == 0
)

check(
    "Sequential ADD executes",
    simulator.cpu.get_register("R3") == 9
)

check(
    "Sequential SUB executes",
    simulator.cpu.get_register("R6") == 17
)

check(
    "Later MUL executes",
    simulator.cpu.get_register("R9") == 12
)


# ============================================================
# TEST 13 - PERFORMANCE ANALYZER
# ============================================================

print(
    "\n--- TEST 13: PERFORMANCE ANALYZER ---"
)

analyzer = PerformanceAnalyzer(
    simulator
)

results = analyzer.get_results()

check(
    "Execution cycles are positive",
    results["cycles"] > 0
)

check(
    "Throughput is positive",
    results["throughput"] > 0
)

check(
    "Speedup is positive",
    results["speedup"] > 0
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 65)
print("                    FINAL TEST RESULT")
print("=" * 65)

print(
    f"\nPassed : {passed}"
)

print(
    f"Failed : {failed}"
)

print(
    f"Total  : {passed + failed}"
)

if failed == 0:

    print(
        "\nALL TESTS PASSED - CORE SIMULATOR IS STABLE."
    )

else:

    print(
        "\nSOME TESTS FAILED - FIX REQUIRED BEFORE GUI."
    )

print("=" * 65)