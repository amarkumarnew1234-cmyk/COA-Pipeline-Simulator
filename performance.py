class PerformanceAnalyzer:

    def __init__(self, simulator):
        self.simulator = simulator

    def total_cycles(self):
        return len(
            self.simulator.history
        )

    def instruction_count(self):
        return len(
            self.simulator.instructions
        )

    def completed_instruction_count(self):
        return len(
            self.simulator.execution_log
        )

    def total_stalls(self):
        return (
            self.simulator.data_stalls
            + self.simulator.structural_stalls
            + self.simulator.control_penalty
        )

    def throughput(self):

        cycles = self.total_cycles()

        if cycles == 0:
            return 0

        return (
            self.completed_instruction_count()
            / cycles
        )

    def non_pipelined_cycles(self):
        """
        Simplified comparison model:

        Each instruction requires five stages
        without overlapping.

        Non-pipelined cycles =
        completed instructions x 5
        """

        return (
            self.completed_instruction_count()
            * 5
        )

    def speedup(self):

        pipelined_cycles = (
            self.total_cycles()
        )

        if pipelined_cycles == 0:
            return 0

        return (
            self.non_pipelined_cycles()
            / pipelined_cycles
        )

    def pipeline_efficiency(self):

        ideal_completed = (
            self.completed_instruction_count()
        )

        cycles = self.total_cycles()

        if cycles == 0:
            return 0

        return (
            ideal_completed
            / cycles
        ) * 100

    def get_results(self):

        return {
            "instructions":
                self.instruction_count(),

            "completed":
                self.completed_instruction_count(),

            "cycles":
                self.total_cycles(),

            "data_hazards":
                len(
                    self.simulator.data_hazards
                ),

            "structural_hazards":
                len(
                    self.simulator.structural_hazards
                ),

            "control_hazards":
                len(
                    self.simulator.control_hazards
                ),

            "data_stalls":
                self.simulator.data_stalls,

            "structural_stalls":
                self.simulator.structural_stalls,

            "control_penalty":
                self.simulator.control_penalty,

            "total_penalty":
                self.total_stalls(),

            "throughput":
                self.throughput(),

            "non_pipelined_cycles":
                self.non_pipelined_cycles(),

            "speedup":
                self.speedup(),

            "efficiency":
                self.pipeline_efficiency()
        }

    def print_report(self):

        results = self.get_results()

        print(
            "\n========== PERFORMANCE ANALYSIS ==========\n"
        )

        print(
            "Program Instructions       :",
            results["instructions"]
        )

        print(
            "Executed Instructions      :",
            results["completed"]
        )

        print(
            "Pipeline Execution Cycles  :",
            results["cycles"]
        )

        print()

        print(
            "Data Hazards               :",
            results["data_hazards"]
        )

        print(
            "Structural Hazards         :",
            results["structural_hazards"]
        )

        print(
            "Control Hazards            :",
            results["control_hazards"]
        )

        print()

        print(
            "Data Stall Cycles          :",
            results["data_stalls"]
        )

        print(
            "Structural Stall Cycles    :",
            results["structural_stalls"]
        )

        print(
            "Control Penalty            :",
            results["control_penalty"]
        )

        print(
            "Total Pipeline Penalty     :",
            results["total_penalty"]
        )

        print()

        print(
            "Throughput                 : "
            f"{results['throughput']:.3f} "
            "instructions/cycle"
        )

        print(
            "Non-Pipelined Cycles       :",
            results["non_pipelined_cycles"]
        )

        print(
            "Speedup                    : "
            f"{results['speedup']:.3f}x"
        )

        print(
            "Pipeline Efficiency        : "
            f"{results['efficiency']:.2f}%"
        )