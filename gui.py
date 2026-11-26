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
        self.root.minsize(1050, 650)

        # --------------------------------------------------
        # STATE VARIABLES
        # --------------------------------------------------

        self.forwarding_var = tk.BooleanVar(
            value=True
        )

        self.shared_memory_var = tk.BooleanVar(
            value=False
        )

        self.scenario_var = tk.StringVar(
            value="Full Demonstration"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        self.register_entries = {}

        self.summary_vars = {
            "cycles": tk.StringVar(value="--"),
            "data": tk.StringVar(value="--"),
            "structural": tk.StringVar(value="--"),
            "control": tk.StringVar(value="--"),
            "stalls": tk.StringVar(value="--"),
            "throughput": tk.StringVar(value="--"),
            "speedup": tk.StringVar(value="--")
        }

        self.configure_styles()

        self.create_interface()

        self.load_selected_scenario()

    # ======================================================
    # STYLE
    # ======================================================

    def configure_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 19, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "CardValue.TLabel",
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=7
        )

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Consolas", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold")
        )

    # ======================================================
    # COMPLETE INTERFACE
    # ======================================================

    def create_interface(self):

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        header = ttk.Frame(
            self.root
        )

        header.pack(
            fill=tk.X,
            padx=12,
            pady=(8, 2)
        )

        ttk.Label(
            header,
            text=(
                "INSTRUCTION PIPELINE & "
                "HAZARD ANALYSIS SIMULATOR"
            ),
            style="Title.TLabel"
        ).pack()

        ttk.Label(
            header,
            text=(
                "Configurable 5-Stage Pipeline"
                "   •   "
                "IF → ID → EX → MEM → WB"
            ),
            style="Subtitle.TLabel"
        ).pack(
            pady=(1, 3)
        )

        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------

        self.create_summary_cards()

        # --------------------------------------------------
        # FIXED TOOLBAR
        # --------------------------------------------------

        self.create_toolbar()

        # --------------------------------------------------
        # INPUT AREA
        # --------------------------------------------------

        input_container = ttk.Frame(
            self.root
        )

        input_container.pack(
            fill=tk.X,
            padx=12,
            pady=(4, 4)
        )

        input_container.columnconfigure(
            0,
            weight=3
        )

        input_container.columnconfigure(
            1,
            weight=2
        )

        self.create_program_panel(
            input_container
        )

        self.create_configuration_panel(
            input_container
        )

        # --------------------------------------------------
        # RESULTS
        # --------------------------------------------------

        result_container = ttk.Frame(
            self.root
        )

        result_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=12,
            pady=(2, 3)
        )

        self.create_results_section(
            result_container
        )

        # --------------------------------------------------
        # STATUS BAR
        # --------------------------------------------------

        status = ttk.Frame(
            self.root
        )

        status.pack(
            fill=tk.X,
            padx=12,
            pady=(1, 6)
        )

        ttk.Separator(
            status,
            orient=tk.HORIZONTAL
        ).pack(
            fill=tk.X,
            pady=(0, 3)
        )

        ttk.Label(
            status,
            text="Status:"
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            status,
            textvariable=self.status_var
        ).pack(
            side=tk.LEFT,
            padx=(5, 0)
        )

    # ======================================================
    # SUMMARY CARDS
    # ======================================================

    def create_summary_cards(self):

        frame = ttk.Frame(
            self.root
        )

        frame.pack(
            fill=tk.X,
            padx=12,
            pady=3
        )

        cards = [
            ("Cycles", "cycles"),
            ("Data Hazards", "data"),
            ("Structural", "structural"),
            ("Control", "control"),
            ("Stalls / Penalty", "stalls"),
            ("Throughput", "throughput"),
            ("Speedup", "speedup")
        ]

        for index, (
            title,
            key
        ) in enumerate(cards):

            frame.columnconfigure(
                index,
                weight=1
            )

            card = ttk.LabelFrame(
                frame,
                text=title
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=2
            )

            ttk.Label(
                card,
                textvariable=(
                    self.summary_vars[key]
                ),
                style="CardValue.TLabel",
                anchor="center"
            ).pack(
                fill=tk.BOTH,
                expand=True,
                padx=5,
                pady=4
            )

    # ======================================================
    # FIXED TOOLBAR
    # ======================================================

    def create_toolbar(self):

        toolbar = ttk.LabelFrame(
            self.root,
            text="Simulation Controls"
        )

        toolbar.pack(
            fill=tk.X,
            padx=12,
            pady=(4, 3)
        )

        left = ttk.Frame(
            toolbar
        )

        left.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=7,
            pady=5
        )

        ttk.Label(
            left,
            text="Scenario:"
        ).pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        self.scenario_box = ttk.Combobox(
            left,
            textvariable=self.scenario_var,
            state="readonly",
            width=23,
            values=[
                "Full Demonstration",
                "No Hazard",
                "RAW Hazard",
                "Load-Use Hazard",
                "Structural Hazard",
                "Branch Taken",
                "Branch Not Taken"
            ]
        )

        self.scenario_box.pack(
            side=tk.LEFT,
            padx=(0, 5)
        )

        ttk.Button(
            left,
            text="Load Scenario",
            command=(
                self.load_selected_scenario
            )
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        ttk.Button(
            left,
            text="Clear Program",
            command=self.clear_program
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        ttk.Button(
            left,
            text="Reset",
            command=self.reset_all
        ).pack(
            side=tk.LEFT,
            padx=3
        )

        ttk.Button(
            toolbar,
            text="▶  RUN SIMULATION",
            command=self.run_simulation,
            style="Action.TButton"
        ).pack(
            side=tk.RIGHT,
            padx=10,
            pady=5
        )

    # ======================================================
    # PROGRAM PANEL
    # ======================================================

    def create_program_panel(
        self,
        parent
    ):

        frame = ttk.LabelFrame(
            parent,
            text="Program Input"
        )

        frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 5)
        )

        self.program_text = tk.Text(
            frame,
            height=9,
            font=("Consolas", 11),
            wrap=tk.NONE
        )

        vertical = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=self.program_text.yview
        )

        horizontal = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL,
            command=self.program_text.xview
        )

        self.program_text.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        self.program_text.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(7, 0),
            pady=(7, 0)
        )

        vertical.grid(
            row=0,
            column=1,
            sticky="ns",
            pady=(7, 0)
        )

        horizontal.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(7, 0),
            pady=(0, 7)
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
    # CONFIGURATION PANEL
    # ======================================================

    def create_configuration_panel(
        self,
        parent
    ):

        right = ttk.Frame(
            parent
        )

        right.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0)
        )

        config = ttk.LabelFrame(
            right,
            text="Simulator Configuration"
        )

        config.pack(
            fill=tk.X,
            pady=(0, 4)
        )

        option_row = ttk.Frame(
            config
        )

        option_row.pack(
            fill=tk.X,
            padx=8,
            pady=4
        )

        ttk.Checkbutton(
            option_row,
            text="Data Forwarding",
            variable=self.forwarding_var
        ).pack(
            side=tk.LEFT,
            padx=(0, 18)
        )

        ttk.Checkbutton(
            option_row,
            text="Shared Instruction/Data Memory",
            variable=self.shared_memory_var
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            config,
            text=(
                "Branch: BEQ resolved in EX; "
                "taken branch flushes younger instructions."
            )
        ).pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        # --------------------------------------------------
        # REGISTER GRID
        # --------------------------------------------------

        registers = ttk.LabelFrame(
            right,
            text="Initial Register Values"
        )

        registers.pack(
            fill=tk.BOTH,
            expand=True
        )

        grid = ttk.Frame(
            registers
        )

        grid.pack(
            fill=tk.BOTH,
            expand=True,
            padx=6,
            pady=5
        )

        for i in range(16):

            row = i // 8

            item = i % 8

            column = item * 2

            register = f"R{i}"

            ttk.Label(
                grid,
                text=register
            ).grid(
                row=row,
                column=column,
                padx=(2, 1),
                pady=4
            )

            entry = ttk.Entry(
                grid,
                width=5
            )

            entry.grid(
                row=row,
                column=column + 1,
                padx=(0, 4),
                pady=4
            )

            entry.insert(
                0,
                "0"
            )

            self.register_entries[
                register
            ] = entry

    # ======================================================
    # RESULTS
    # ======================================================

    def create_results_section(
        self,
        parent
    ):

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
            text="Pipeline Visualization"
        )

        notebook.add(
            self.hazard_tab,
            text="Hazard Analysis"
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

        self.hazard_text = (
            self.create_text_tab(
                self.hazard_tab
            )
        )

        self.performance_text = (
            self.create_text_tab(
                self.performance_tab
            )
        )

        self.cpu_text = (
            self.create_text_tab(
                self.cpu_tab
            )
        )

        self.execution_text = (
            self.create_text_tab(
                self.execution_tab
            )
        )

    # ======================================================
    # PIPELINE TAB
    # ======================================================

    def create_pipeline_tab(self):

        legend = ttk.Frame(
            self.pipeline_tab
        )

        legend.pack(
            fill=tk.X,
            padx=7,
            pady=4
        )

        ttk.Label(
            legend,
            text=(
                "Legend: "
                "IF = Fetch   "
                "ID = Decode   "
                "EX = Execute   "
                "MEM = Memory   "
                "WB = Write Back   "
                "ST = Stall   "
                "FL = Flush"
            )
        ).pack(
            side=tk.LEFT
        )

        table = ttk.Frame(
            self.pipeline_tab
        )

        table.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.pipeline_tree = ttk.Treeview(
            table,
            show="headings"
        )

        vertical = ttk.Scrollbar(
            table,
            orient=tk.VERTICAL,
            command=(
                self.pipeline_tree.yview
            )
        )

        horizontal = ttk.Scrollbar(
            table,
            orient=tk.HORIZONTAL,
            command=(
                self.pipeline_tree.xview
            )
        )

        self.pipeline_tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        self.pipeline_tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table.rowconfigure(
            0,
            weight=1
        )

        table.columnconfigure(
            0,
            weight=1
        )

    # ======================================================
    # TEXT TAB
    # ======================================================

    def create_text_tab(
        self,
        parent
    ):

        frame = ttk.Frame(
            parent
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        text = tk.Text(
            frame,
            font=("Consolas", 11),
            wrap=tk.NONE
        )

        vertical = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=text.yview
        )

        horizontal = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL,
            command=text.xview
        )

        text.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        text.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal.grid(
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

        return text

    # ======================================================
    # SCENARIO DATA
    # ======================================================

    def scenario_data(
        self,
        name
    ):

        scenarios = {

            "Full Demonstration": {
                "program": [
                    "ADD R4, R1, R2",
                    "BEQ R4, R3, TARGET",
                    "SUB R5, R1, R2",
                    "MUL R6, R1, R2",
                    "TARGET:",
                    "ADD R7, R4, R3",
                    "STORE R7, 0(R8)",
                    "LOAD R9, 0(R8)"
                ],

                "registers": {
                    "R1": 10,
                    "R2": 20,
                    "R3": 30,
                    "R8": 100
                },

                "forwarding": True,
                "shared": False
            },

            "No Hazard": {
                "program": [
                    "ADD R1, R2, R3",
                    "SUB R4, R5, R6",
                    "MUL R7, R8, R9"
                ],

                "registers": {
                    "R2": 10,
                    "R3": 20,
                    "R5": 50,
                    "R6": 5,
                    "R8": 3,
                    "R9": 4
                },

                "forwarding": True,
                "shared": False
            },

            "RAW Hazard": {
                "program": [
                    "ADD R1, R2, R3",
                    "SUB R4, R1, R5",
                    "MUL R6, R4, R2"
                ],

                "registers": {
                    "R2": 10,
                    "R3": 20,
                    "R5": 5
                },

                "forwarding": False,
                "shared": False
            },

            "Load-Use Hazard": {
                "program": [
                    "LOAD R1, 0(R2)",
                    "ADD R3, R1, R4",
                    "SUB R5, R3, R6"
                ],

                "registers": {
                    "R2": 100,
                    "R4": 10,
                    "R6": 5
                },

                "forwarding": True,
                "shared": False
            },

            "Structural Hazard": {
                "program": [
                    "LOAD R1, 0(R2)",
                    "ADD R3, R4, R5",
                    "SUB R6, R7, R8",
                    "MUL R9, R10, R11",
                    "ADD R12, R13, R14",
                    "SUB R15, R3, R4"
                ],

                "registers": {
                    "R2": 100,
                    "R4": 10,
                    "R5": 20,
                    "R7": 30,
                    "R8": 5,
                    "R10": 2,
                    "R11": 3,
                    "R13": 7,
                    "R14": 8
                },

                "forwarding": True,
                "shared": True
            },

            "Branch Taken": {
                "program": [
                    "ADD R4, R1, R2",
                    "BEQ R4, R3, TARGET",
                    "SUB R5, R1, R2",
                    "MUL R6, R1, R2",
                    "TARGET:",
                    "ADD R7, R4, R3"
                ],

                "registers": {
                    "R1": 10,
                    "R2": 20,
                    "R3": 30
                },

                "forwarding": True,
                "shared": False
            },

            "Branch Not Taken": {
                "program": [
                    "BEQ R1, R2, TARGET",
                    "ADD R3, R4, R5",
                    "SUB R6, R7, R8",
                    "TARGET:",
                    "MUL R9, R10, R11"
                ],

                "registers": {
                    "R1": 10,
                    "R2": 20,
                    "R4": 4,
                    "R5": 5,
                    "R7": 20,
                    "R8": 3,
                    "R10": 2,
                    "R11": 6
                },

                "forwarding": True,
                "shared": False
            }
        }

        return scenarios[name]

    # ======================================================
    # LOAD SCENARIO
    # ======================================================

    def load_selected_scenario(
        self
    ):

        name = (
            self.scenario_var.get()
        )

        data = self.scenario_data(
            name
        )

        self.program_text.delete(
            "1.0",
            tk.END
        )

        self.program_text.insert(
            tk.END,
            "\n".join(
                data["program"]
            )
        )

        for register, entry in (
            self.register_entries.items()
        ):

            entry.delete(
                0,
                tk.END
            )

            value = (
                data["registers"].get(
                    register,
                    0
                )
            )

            entry.insert(
                0,
                str(value)
            )

        self.forwarding_var.set(
            data["forwarding"]
        )

        self.shared_memory_var.set(
            data["shared"]
        )

        self.clear_results()

        self.status_var.set(
            f"Scenario loaded: {name}"
        )

    # ======================================================
    # CLEAR / RESET
    # ======================================================

    def clear_program(
        self
    ):

        self.program_text.delete(
            "1.0",
            tk.END
        )

        self.clear_results()

        self.status_var.set(
            "Program cleared"
        )

    def reset_all(
        self
    ):

        self.scenario_var.set(
            "Full Demonstration"
        )

        self.load_selected_scenario()

        self.status_var.set(
            "Simulator reset"
        )

    def clear_results(
        self
    ):

        for item in (
            self.pipeline_tree.get_children()
        ):

            self.pipeline_tree.delete(
                item
            )

        for text in [
            self.hazard_text,
            self.performance_text,
            self.cpu_text,
            self.execution_text
        ]:

            text.delete(
                "1.0",
                tk.END
            )

        for variable in (
            self.summary_vars.values()
        ):

            variable.set("--")

    # ======================================================
    # REGISTER VALUES
    # ======================================================

    def load_register_values(
        self,
        simulator
    ):

        for register, entry in (
            self.register_entries.items()
        ):

            value_text = (
                entry.get().strip()
            )

            if value_text == "":
                value = 0

            else:

                try:

                    value = int(
                        value_text
                    )

                except ValueError:

                    raise ValueError(
                        f"Invalid integer "
                        f"value for "
                        f"{register}: "
                        f"{value_text}"
                    )

            simulator.set_register(
                register,
                value
            )

    # ======================================================
    # RUN SIMULATION
    # ======================================================

    def run_simulation(
        self
    ):

        try:

            self.status_var.set(
                "Running simulation..."
            )

            self.root.update_idletasks()

            text = (
                self.program_text.get(
                    "1.0",
                    tk.END
                )
            )

            lines = [
                line.strip()
                for line
                in text.splitlines()
                if line.strip()
            ]

            if not lines:

                raise ValueError(
                    "Program cannot be empty."
                )

            program = Program(
                lines
            )

            simulator = (
                PipelineSimulator(
                    program,
                    forwarding=(
                        self.forwarding_var.get()
                    ),
                    shared_memory=(
                        self.shared_memory_var.get()
                    )
                )
            )

            self.load_register_values(
                simulator
            )

            # Built-in memory for LOAD-use demo.
            if (
                self.scenario_var.get()
                == "Load-Use Hazard"
            ):

                simulator.set_memory(
                    100,
                    50
                )

            simulator.run()

            analyzer = (
                PerformanceAnalyzer(
                    simulator
                )
            )

            self.display_pipeline(
                simulator
            )

            self.display_hazards(
                simulator
            )

            self.display_performance(
                analyzer
            )

            self.display_cpu_state(
                simulator
            )

            self.display_execution_log(
                simulator
            )

            self.update_summary(
                analyzer
            )

            self.status_var.set(
                "Simulation completed successfully"
            )

        except Exception as error:

            self.status_var.set(
                "Simulation error"
            )

            messagebox.showerror(
                "Simulation Error",
                str(error)
            )

    # ======================================================
    # SUMMARY UPDATE
    # ======================================================

    def update_summary(
        self,
        analyzer
    ):

        r = analyzer.get_results()

        self.summary_vars[
            "cycles"
        ].set(
            str(r["cycles"])
        )

        self.summary_vars[
            "data"
        ].set(
            str(
                r["data_hazards"]
            )
        )

        self.summary_vars[
            "structural"
        ].set(
            str(
                r[
                    "structural_hazards"
                ]
            )
        )

        self.summary_vars[
            "control"
        ].set(
            str(
                r["control_hazards"]
            )
        )

        self.summary_vars[
            "stalls"
        ].set(
            str(
                r["total_penalty"]
            )
        )

        self.summary_vars[
            "throughput"
        ].set(
            f"{r['throughput']:.3f}"
        )

        self.summary_vars[
            "speedup"
        ].set(
            f"{r['speedup']:.3f}x"
        )

    # ======================================================
    # PIPELINE DISPLAY
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
                    width=55,
                    minwidth=50,
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

                value = ""

                if (
                    instruction
                    in simulator.flush_history[
                        index
                    ]
                ):

                    value = "FL"

                elif (
                    simulator.stall_history[
                        index
                    ]
                    is instruction
                ):

                    value = "ST"

                else:

                    for stage in (
                        simulator.STAGES
                    ):

                        if (
                            state[stage]
                            is instruction
                        ):

                            value = stage
                            break

                row.append(
                    value
                )

            self.pipeline_tree.insert(
                "",
                tk.END,
                values=row
            )

    # ======================================================
    # HAZARD DISPLAY
    # ======================================================

    def display_hazards(
        self,
        simulator
    ):

        self.hazard_text.delete(
            "1.0",
            tk.END
        )

        lines = [
            "========== HAZARD ANALYSIS ==========",
            "",
            f"Data Hazards       : "
            f"{len(simulator.data_hazards)}",
            f"Structural Hazards : "
            f"{len(simulator.structural_hazards)}",
            f"Control Hazards    : "
            f"{len(simulator.control_hazards)}",
            "",
            f"Data Stall Cycles  : "
            f"{simulator.data_stalls}",
            f"Structural Stalls  : "
            f"{simulator.structural_stalls}",
            f"Control Penalty    : "
            f"{simulator.control_penalty}",
            "",
            "---------- DATA HAZARDS ----------",
            ""
        ]

        if not simulator.data_hazards:

            lines.append(
                "No RAW data hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.data_hazards,
                start=1
            ):

                lines.extend([
                    f"Data Hazard {number}",
                    "Type     : RAW "
                    "(Read After Write)",
                    f"Producer : "
                    f"{hazard['producer']}",
                    f"Consumer : "
                    f"{hazard['consumer']}",
                    f"Register : "
                    f"{hazard['register']}",
                    ""
                ])

        lines.extend([
            "",
            "------- STRUCTURAL HAZARDS -------",
            ""
        ])

        if not simulator.structural_hazards:

            lines.append(
                "No structural hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.structural_hazards,
                start=1
            ):

                lines.extend([
                    f"Structural Hazard {number}",
                    f"Cycle    : "
                    f"{hazard['cycle']}",
                    "Resource : Shared Memory",
                    f"MEM uses : "
                    f"{hazard['memory_instruction']}",
                    "Effect   : "
                    "Instruction fetch delayed",
                    ""
                ])

        lines.extend([
            "",
            "--------- CONTROL HAZARDS --------",
            ""
        ])

        if not simulator.control_hazards:

            lines.append(
                "No control hazards detected."
            )

        else:

            for number, hazard in enumerate(
                simulator.control_hazards,
                start=1
            ):

                lines.extend([
                    f"Control Hazard {number}",
                    f"Branch  : "
                    f"{hazard['branch']}",
                    f"Taken   : "
                    f"{hazard['taken']}",
                    f"Target  : "
                    f"{hazard['target']}",
                    f"Flushed : "
                    f"{hazard['flushed']}"
                ])

                if (
                    hazard[
                        "flushed_instructions"
                    ]
                ):

                    lines.append(
                        "Flushed Instructions:"
                    )

                    for instruction in (
                        hazard[
                            "flushed_instructions"
                        ]
                    ):

                        lines.append(
                            f"  - {instruction}"
                        )

                lines.append("")

        self.hazard_text.insert(
            tk.END,
            "\n".join(lines)
        )

    # ======================================================
    # PERFORMANCE DISPLAY
    # ======================================================

    def display_performance(
        self,
        analyzer
    ):

        self.performance_text.delete(
            "1.0",
            tk.END
        )

        r = analyzer.get_results()

        lines = [
            "========== PERFORMANCE ANALYSIS ==========",
            "",
            f"Program Instructions       : "
            f"{r['instructions']}",
            f"Executed Instructions      : "
            f"{r['completed']}",
            f"Pipeline Execution Cycles  : "
            f"{r['cycles']}",
            "",
            f"Data Hazards               : "
            f"{r['data_hazards']}",
            f"Structural Hazards         : "
            f"{r['structural_hazards']}",
            f"Control Hazards            : "
            f"{r['control_hazards']}",
            "",
            f"Data Stall Cycles          : "
            f"{r['data_stalls']}",
            f"Structural Stall Cycles    : "
            f"{r['structural_stalls']}",
            f"Control Penalty            : "
            f"{r['control_penalty']}",
            f"Total Pipeline Penalty     : "
            f"{r['total_penalty']}",
            "",
            f"Throughput                 : "
            f"{r['throughput']:.3f} "
            "instructions/cycle",
            f"Non-Pipelined Cycles       : "
            f"{r['non_pipelined_cycles']}",
            f"Speedup                    : "
            f"{r['speedup']:.3f}x",
            f"Pipeline Efficiency        : "
            f"{r['efficiency']:.2f}%"
        ]

        self.performance_text.insert(
            tk.END,
            "\n".join(lines)
        )

    # ======================================================
    # CPU STATE
    # ======================================================

    def display_cpu_state(
        self,
        simulator
    ):

        self.cpu_text.delete(
            "1.0",
            tk.END
        )

        lines = [
            "========== FINAL REGISTER FILE ==========",
            ""
        ]

        for i in range(16):

            register = f"R{i}"

            lines.append(
                f"{register:<4} = "
                f"{simulator.cpu.registers[register]}"
            )

        lines.extend([
            "",
            "========== DATA MEMORY ==========",
            ""
        ])

        if not simulator.cpu.memory:

            lines.append(
                "Memory is empty."
            )

        else:

            for address in sorted(
                simulator.cpu.memory.keys()
            ):

                lines.append(
                    f"Address {address:<6} = "
                    f"{simulator.cpu.memory[address]}"
                )

        self.cpu_text.insert(
            tk.END,
            "\n".join(lines)
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

        lines = [
            "========== EXECUTION LOG ==========",
            ""
        ]

        if not simulator.execution_log:

            lines.append(
                "No instructions executed."
            )

        else:

            for entry in (
                simulator.execution_log
            ):

                lines.extend([
                    f"Cycle {entry['cycle']}",
                    f"Instruction : "
                    f"{entry['instruction']}",
                    f"Result      : "
                    f"{entry['result']}",
                    ""
                ])

        self.execution_text.insert(
            tk.END,
            "\n".join(lines)
        )


def main():

    root = tk.Tk()

    PipelineSimulatorGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()