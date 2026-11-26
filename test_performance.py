from program import Program
from pipeline import PipelineSimulator
from performance import PerformanceAnalyzer


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


# Initial registers

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


# Run pipeline

simulator.run()


# Analyze performance

analyzer = PerformanceAnalyzer(
    simulator
)


simulator.print_timing_table()

simulator.print_hazard_report()

analyzer.print_report()