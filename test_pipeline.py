from program import Program
from pipeline import PipelineSimulator


program_lines = [

    "ADD R4, R1, R2",

    "BEQ R4, R3, TARGET",

    "SUB R5, R1, R2",

    "MUL R6, R1, R2",

    "TARGET:",

    "ADD R7, R4, R3"
]


program = Program(
    program_lines
)


simulator = PipelineSimulator(
    program,
    forwarding=True,
    shared_memory=False
)


# ==========================================
# INITIAL REGISTER VALUES
# ==========================================

simulator.set_register(
    "R1",
    10
)

simulator.set_register(
    "R2",
    20
)

simulator.set_register(
    "R3",
    30
)


print(
    "\n========== INITIAL PROGRAM =========="
)

program.print_program()


print(
    "\n========== INITIAL REGISTERS =========="
)

simulator.cpu.print_registers()


# ==========================================
# RUN SIMULATION
# ==========================================

simulator.run()


# ==========================================
# RESULTS
# ==========================================

simulator.print_timing_table()

simulator.print_execution_log()

simulator.print_hazard_report()


print(
    "\n========== FINAL REGISTERS =========="
)

simulator.cpu.print_registers()