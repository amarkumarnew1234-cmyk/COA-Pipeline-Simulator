import tkinter as tk
from tkinter import ttk, messagebox

from program import Program
from pipeline import PipelineSimulator
from performance import PerformanceAnalyzer


class PipelineSimulatorGUI:

    def __init__(self, root):
        self.root = root

        self.root.title(
            "Instruction Pipeline & Hazard Analysis Simulator"
        )

        self.root.geometry("1450x850")
        self.root.minsize(1100, 700)

        self.forwarding_var = tk.BooleanVar(
            value=True
        )

        self.shared_memory_var = tk.BooleanVar(
            value=False
        )

        self.register_entries = {}

        self.create_interface()

        self.load_demo_program()

    # ======================================================
    # MAIN INTERFACE
    # ======================================================

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="INSTRUCTION PIPELINE & HAZARD ANALYSIS SIMULATOR",
            font=("Segoe UI", 18, "bold")
        )

        title.pack(
            pady=(12, 5)
        )

        subtitle = tk.Label(
            self.root,
            text=(
                "5-Stage Pipeline: "
                "IF → ID → EX → MEM → WB"
            ),
            font=("Segoe UI", 10)
        )

        subtitle.pack(
            pady=(0, 10)
        )

        main = ttk.PanedWindow(
            self.root,
            orient=tk.VERTICAL
        )

        main.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        top = ttk.Frame(main)

        bottom = ttk.Frame(main)

        main.add(
            top,
            weight=2
        )

        main.add(
            bottom,
            weight=3
        )

        self.create_top_section(top)

        self.create_bottom_section(bottom)

    # ======================================================
    # TOP SECTION
    # ======================================================

    def create_top_section(self, parent):

        parent.columnconfigure(
            0,
            weight=3
        )

        parent.columnconfigure(
            1,
            weight=2
        )

        # --------------------------------------------------
        # PROGRAM INPUT
        # --------------------------------------------------

        program_frame = ttk.LabelFrame(
            parent,
            text="Program Input"
        )

        program_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 5),
            pady=5
        )

        self.program_text = tk.Text(
            program_frame,
            height=12,
            font=("Consolas", 11)
        )

        self.program_text.pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=8
        )

        program_buttons = ttk.Frame(
            program_frame
        )

        program_buttons.pack(
            fill=tk.X,
            padx=8,
            pady=(0, 8)
        )

        ttk.Button(
            program_buttons,
            text="Load Demo Program",
            command=self.load_demo_program
        ).pack(
            side=tk.LEFT,
            padx=4
        )

        ttk.Button(
            program_buttons,
            text="Clear Program",
            command=self.clear_program
        ).pack(
            side=tk.LEFT,
            padx=4
        )

        ttk.Button(
            program_buttons,
            text="Run Simulation",
            command=self.run_simulation
        ).pack(
            side=tk.RIGHT,
            padx=4
        )

        # --------------------------------------------------
        # CONFIGURATION + REGISTERS
        # --------------------------------------------------

        right_frame = ttk.Frame(
            parent
        )

        right_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0),
            pady=5
        )

        config_frame = ttk.LabelFrame(
            right_frame,
            text="Configuration"
        )

        config_frame.pack(
            fill=tk.X,
            pady=(0, 5)
        )

        ttk.Checkbutton(
            config_frame,
            text="Enable Data Forwarding",
            variable=self.forwarding_var
        ).pack(
            anchor="w",
            padx=10,
            pady=6
        )

        ttk.Checkbutton(
            config_frame,
            text="Use Shared Instruction/Data Memory",
            variable=self.shared_memory_var
        ).pack(
            anchor="w",
            padx=10,
            pady=6
        )

        # --------------------------------------------------
        # REGISTER INPUTS
        # --------------------------------------------------

        registers_frame = ttk.LabelFrame(
            right_frame,
            text="Initial Register Values"
        )

        registers_frame.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(5, 0)
        )

        register_grid = ttk.Frame(
            registers_frame
        )

        register_grid.pack(
            fill=tk.BOTH,
            expand=True,
            padx=8,
            pady=8
        )

        for i in range(16):

            row = i // 4
            column = (i % 4) * 2

            register = f"R{i}"

            ttk.Label(
                register_grid,
                text=register
            ).grid(
                row=row,
                column=column,
                padx=(5, 2),
                pady=5
            )

            entry = ttk.Entry(
                register_grid,
                width=8
            )

            entry.grid(
                row=row,
                column=column + 1,
                padx=(0, 8),
                pady=5
            )

            entry.insert(
                0,
                "0"
            )

            self.register_entries[
                register
            ] = entry

    # ======================================================
    # BOTTOM SECTION
    # ======================================================

    def create_bottom_section(self, parent):

        notebook = ttk.Notebook(
            parent
        )

        notebook.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.pipeline_tab = ttk.Frame(
            notebook
        )

        self.hazard_tab = ttk.Frame(
            notebook
        )

        self.performance_tab = ttk.Frame(
            notebook
        )

        self.cpu_tab = ttk.Frame(
            notebook
        )

        self.execution_tab = ttk.Frame(
            notebook
        )

        notebook.add(
            self.pipeline_tab,
            text="Pipeline"
        )

        notebook.add(
            self.hazard_tab,
            text="Hazards"
        )

        notebook.add(
            self.performance_tab,
            text="Performance"
        )

        notebook.add(
            self.cpu_tab,
            text="CPU State"
        )

        notebook.add(
            self.execution_tab,
            text="Execution Log"
        )

        self.create_pipeline_tab()

        self.hazard_text = self.create_text_tab(
            self.hazard_tab
        )

        self.performance_text = self.create_text_tab(
            self.performance_tab
        )

        self.cpu_text = self.create_text_tab(
            self.cpu_tab
        )

        self.execution_text = self.create_text_tab(
            self.execution_tab
        )

    # ======================================================
    # PIPELINE TAB
    # ======================================================

    def create_pipeline_tab(self):

        frame = ttk.Frame(
            self.pipeline_tab
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.pipeline_tree = ttk.Treeview(
            frame,
            show="headings"
        )

        vertical_scroll = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=self.pipeline_tree.yview
        )

        horizontal_scroll = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL,
            command=self.pipeline_tree.xview
        )

        self.pipeline_tree.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set
        )

        self.pipeline_tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        frame.rowconfigure(
            0,
            weight=1
        )

        frame.columnconfigure(
            0,
            weight=1
        )

    # ======================================================
    # GENERIC TEXT TAB
    # ======================================================

    def create_text_tab(self, parent):

        text = tk.Text(
            parent,
            font=("Consolas", 11),
            wrap=tk.NONE
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient=tk.VERTICAL,
            command=text.yview
        )

        text.configure(
            yscrollcommand=scrollbar.set
        )

        text.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        return text

    # ======================================================
    # DEMO PROGRAM
    # ======================================================

    def load_demo_program(self):

        demo = """ADD R4, R1, R2
BEQ R4, R3, TARGET
SUB R5, R1, R2
MUL R6, R1, R2
TARGET:
ADD R7, R4, R3
STORE R7, 0(R8)
LOAD R9, 0(R8)"""

        self.program_text.delete(
            "1.0",
            tk.END
        )

        self.program_text.insert(
            tk.END,
            demo
        )

        demo_registers = {
            "R1": 10,
            "R2": 20,
            "R3": 30,
            "R8": 100
        }

        for register, entry in (
            self.register_entries.items()
        ):

            entry.delete(
                0,
                tk.END
            )

            entry.insert(
                0,
                str(
                    demo_registers.get(
                        register,
                        0
                    )
                )
            )

    # ======================================================
    # CLEAR PROGRAM
    # ======================================================

    def clear_program(self):

        self.program_text.delete(
            "1.0",
            tk.END
        )

    # ======================================================
    # READ REGISTER INPUTS
    # ======================================================

    def load_register_values(
        self,
        simulator
    ):

        for register, entry in (
            self.register_entries.items()
        ):

            text = entry.get().strip()

            if text == "":
                value = 0
            else:
                try:
                    value = int(text)

                except ValueError:

                    raise ValueError(
                        f"Invalid value for "
                        f"{register}: {text}"
                    )

            simulator.set_register(
                register,
                value
            )

    # ======================================================
    # RUN SIMULATION
    # ======================================================

    def run_simulation(self):

        try:

            program_text = (
                self.program_text.get(
                    "1.0",
                    tk.END
                )
            )

            lines = [
                line.strip()
                for line
                in program_text.splitlines()
                if line.strip()
            ]

            if not lines:

                raise ValueError(
                    "Program cannot be empty."
                )

            program = Program(
                lines
            )

            simulator = PipelineSimulator(
                program,
                forwarding=(
                    self.forwarding_var.get()
                ),
                shared_memory=(
                    self.shared_memory_var.get()
                )
            )

            self.load_register_values(
                simulator
            )

            simulator.run()

            analyzer = PerformanceAnalyzer(
                simulator
            )

            self.display_pipeline(
                simulator
            )

            self.display_hazards(
                simulator
            )

            self.display_performance(
                simulator,
                analyzer
            )

            self.display_cpu_state(
                simulator
            )

            self.display_execution_log(
                simulator
            )

            messagebox.showinfo(
                "Simulation Complete",
                "Pipeline simulation completed successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Simulation Error",
                str(error)
            )

    # ======================================================
    # DISPLAY PIPELINE
    # ======================================================

    def display_pipeline(
        self,
        simulator
    ):

        for item in (
            self.pipeline_tree.get_children()
        ):

            self.pipeline_tree.delete(
                item
            )

        cycles = len(
            simulator.history
        )

        columns = [
            "Instruction"
        ] + [
            f"C{i}"
            for i in range(
                1,
                cycles + 1
            )
        ]

        self.pipeline_tree[
            "columns"
        ] = columns

        for column in columns:

            self.pipeline_tree.heading(
                column,
                text=column
            )

            if column == "Instruction":

                self.pipeline_tree.column(
                    column,
                    width=220,
                    minwidth=180,
                    anchor="w"
                )

            else:

                self.pipeline_tree.column(
                    column,
                    width=60,
                    minwidth=55,
                    anchor="center"
                )

        for instruction in (
            simulator.instructions
        ):

            row = [
                str(instruction)
            ]

            for index, state in enumerate(
                simulator.history
            ):

                stage = ""

                if (
                    simulator.stall_history[
                        index
                    ]
                    is instruction
                ):

                    stage = "ST"

                else:

                    for stage_name in (
                        simulator.STAGES
                    ):

                        if (
                            state[stage_name]
                            is instruction
                        ):

                            stage = stage_name
                            break

                row.append(
                    stage
                )

            self.pipeline_tree.insert(
                "",
                tk.END,
                values=row
            )

    # ======================================================
    # DISPLAY HAZARDS
    # ======================================================

    def display_hazards(
        self,
        simulator
    ):

        self.hazard_text.delete(
            "1.0",
            tk.END
        )

        output = []

        output.append(
            "========== HAZARD ANALYSIS ==========\n"
        )

        output.append(
            f"Data Hazards       : "
            f"{len(simulator.data_hazards)}"
        )

        output.append(
            f"Structural Hazards : "
            f"{len(simulator.structural_hazards)}"
        )

        output.append(
            f"Control Hazards    : "
            f"{len(simulator.control_hazards)}"
        )

        output.append("")

        output.append(
            f"Data Stall Cycles  : "
            f"{simulator.data_stalls}"
        )

        output.append(
            f"Structural Stalls  : "
            f"{simulator.structural_stalls}"
        )

        output.append(
            f"Control Penalty    : "
            f"{simulator.control_penalty}"
        )

        output.append(
            "\n--- DATA HAZARDS ---\n"
        )

        if not simulator.data_hazards:

            output.append(
                "No data hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.data_hazards,
                start=1
            ):

                output.append(
                    f"Hazard {number}"
                )

                output.append(
                    f"Producer : "
                    f"{hazard['producer']}"
                )

                output.append(
                    f"Consumer : "
                    f"{hazard['consumer']}"
                )

                output.append(
                    f"Register : "
                    f"{hazard['register']}\n"
                )

        output.append(
            "\n--- STRUCTURAL HAZARDS ---\n"
        )

        if not simulator.structural_hazards:

            output.append(
                "No structural hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.structural_hazards,
                start=1
            ):

                output.append(
                    f"Hazard {number}"
                )

                output.append(
                    f"Cycle : "
                    f"{hazard['cycle']}"
                )

                output.append(
                    "Resource : Shared Memory"
                )

                output.append(
                    f"MEM instruction : "
                    f"{hazard['memory_instruction']}\n"
                )

        output.append(
            "\n--- CONTROL HAZARDS ---\n"
        )

        if not simulator.control_hazards:

            output.append(
                "No control hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.control_hazards,
                start=1
            ):

                output.append(
                    f"Branch {number}"
                )

                output.append(
                    f"Instruction : "
                    f"{hazard['branch']}"
                )

                output.append(
                    f"Taken       : "
                    f"{hazard['taken']}"
                )

                output.append(
                    f"Target      : "
                    f"{hazard['target']}"
                )

                output.append(
                    f"Flushed     : "
                    f"{hazard['flushed']}\n"
                )

        self.hazard_text.insert(
            tk.END,
            "\n".join(output)
        )

    # ======================================================
    # DISPLAY PERFORMANCE
    # ======================================================

    def display_performance(
        self,
        simulator,
        analyzer
    ):

        self.performance_text.delete(
            "1.0",
            tk.END
        )

        results = analyzer.get_results()

        output = f"""
========== PERFORMANCE ANALYSIS ==========

Program Instructions       : {results['instructions']}
Executed Instructions      : {results['completed']}
Pipeline Execution Cycles  : {results['cycles']}

Data Hazards               : {results['data_hazards']}
Structural Hazards         : {results['structural_hazards']}
Control Hazards            : {results['control_hazards']}

Data Stall Cycles          : {results['data_stalls']}
Structural Stall Cycles    : {results['structural_stalls']}
Control Penalty            : {results['control_penalty']}
Total Pipeline Penalty     : {results['total_penalty']}

Throughput                 : {results['throughput']:.3f} instructions/cycle
Non-Pipelined Cycles       : {results['non_pipelined_cycles']}
Speedup                    : {results['speedup']:.3f}x
Pipeline Efficiency        : {results['efficiency']:.2f}%
"""

        self.performance_text.insert(
            tk.END,
            output
        )

    # ======================================================
    # DISPLAY CPU
    # ======================================================

    def display_cpu_state(
        self,
        simulator
    ):

        self.cpu_text.delete(
            "1.0",
            tk.END
        )

        output = []

        output.append(
            "========== FINAL REGISTER FILE ==========\n"
        )

        for i in range(16):

            register = f"R{i}"

            output.append(
                f"{register:<4} = "
                f"{simulator.cpu.registers[register]}"
            )

        output.append(
            "\n========== DATA MEMORY ==========\n"
        )

        if not simulator.cpu.memory:

            output.append(
                "Memory is empty."
            )

        else:

            for address in sorted(
                simulator.cpu.memory
            ):

                output.append(
                    f"Address {address:<6} = "
                    f"{simulator.cpu.memory[address]}"
                )

        self.cpu_text.insert(
            tk.END,
            "\n".join(output)
        )

    # ======================================================
    # EXECUTION LOG
    # ======================================================

    def display_execution_log(
        self,
        simulator
    ):

        self.execution_text.delete(
            "1.0",
            tk.END
        )

        output = []

        output.append(
            "========== EXECUTION LOG ==========\n"
        )

        for entry in (
            simulator.execution_log
        ):

            output.append(
                f"Cycle {entry['cycle']}"
            )

            output.append(
                f"Instruction : "
                f"{entry['instruction']}"
            )

            output.append(
                f"Result      : "
                f"{entry['result']}"
            )

            output.append("")

        self.execution_text.insert(
            tk.END,
            "\n".join(output)
        )


def main():

    root = tk.Tk()

    PipelineSimulatorGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()