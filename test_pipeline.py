from parser import parse_instruction
from pipeline import PipelineSimulator


program = [
    "ADD R1, R2, R3",
    "SUB R4, R1, R5",
    "MUL R6, R4, R2"
]


def create_instructions():

    return [
        parse_instruction(text)
        for text in program
    ]


# ==========================================
# TEST 1: FORWARDING OFF
# ==========================================

instructions_without_forwarding = (
    create_instructions()
)

simulator_without_forwarding = (
    PipelineSimulator(
        instructions_without_forwarding,
        forwarding=False
    )
)

simulator_without_forwarding.run()

print(
    "\n\n========================================"
)
print(
    "       TEST 1: FORWARDING OFF"
)
print(
    "========================================"
)

simulator_without_forwarding.print_timing_table()

simulator_without_forwarding.print_hazard_report()


# ==========================================
# TEST 2: FORWARDING ON
# ==========================================

instructions_with_forwarding = (
    create_instructions()
)

simulator_with_forwarding = (
    PipelineSimulator(
        instructions_with_forwarding,
        forwarding=True
    )
)

simulator_with_forwarding.run()

print(
    "\n\n========================================"
)
print(
    "        TEST 2: FORWARDING ON"
)
print(
    "========================================"
)

simulator_with_forwarding.print_timing_table()

simulator_with_forwarding.print_hazard_report()


# ==========================================
# COMPARISON
# ==========================================

cycles_without = len(
    simulator_without_forwarding.history
)

cycles_with = len(
    simulator_with_forwarding.history
)

stalls_without = (
    simulator_without_forwarding.total_stalls
)

stalls_with = (
    simulator_with_forwarding.total_stalls
)


print(
    "\n\n========== FORWARDING COMPARISON ==========\n"
)

print(
    f"{'Parameter':<25}"
    f"{'OFF':<12}"
    f"{'ON':<12}"
)

print("-" * 49)

print(
    f"{'Execution Cycles':<25}"
    f"{cycles_without:<12}"
    f"{cycles_with:<12}"
)

print(
    f"{'Stall Cycles':<25}"
    f"{stalls_without:<12}"
    f"{stalls_with:<12}"
)

print(
    f"{'Data Hazards':<25}"
    f"{len(simulator_without_forwarding.data_hazards):<12}"
    f"{len(simulator_with_forwarding.data_hazards):<12}"
)