from program import Program
from pipeline import PipelineSimulator
from performance import PerformanceAnalyzer


def print_title():
    print("\n" + "=" * 62)
    print("     INSTRUCTION PIPELINE & HAZARD ANALYSIS SIMULATOR")
    print("=" * 62)


def print_configuration(forwarding, shared_memory):
    print("\n========== SIMULATOR CONFIGURATION ==========\n")

    print(
        "Forwarding       :",
        "ON" if forwarding else "OFF"
    )

    print(
        "Memory Model     :",
        "Shared" if shared_memory else "Separate"
    )

    print(
        "Pipeline Stages  : IF -> ID -> EX -> MEM -> WB"
    )

    print(
        "Branch Handling  : BEQ resolved in EX"
    )


def get_yes_no(message, default=True):
    while True:

        default_text = "Y/n" if default else "y/N"

        answer = input(
            f"{message} [{default_text}]: "
        ).strip().lower()

        if answer == "":
            return default

        if answer in {"y", "yes"}:
            return True

        if answer in {"n", "no"}:
            return False

        print("Please enter y or n.")


def configure_simulator():
    print("\n========== CONFIGURATION ==========\n")

    forwarding = get_yes_no(
        "Enable data forwarding?",
        True
    )

    shared_memory = get_yes_no(
        "Use shared instruction/data memory?",
        False
    )

    return forwarding, shared_memory


def initialize_demo_registers(simulator):
    simulator.set_register("R1", 10)
    simulator.set_register("R2", 20)
    simulator.set_register("R3", 30)
    simulator.set_register("R8", 100)


def demonstration_program():
    return [
        "ADD R4, R1, R2",
        "BEQ R4, R3, TARGET",
        "SUB R5, R1, R2",
        "MUL R6, R1, R2",
        "TARGET:",
        "ADD R7, R4, R3",
        "STORE R7, 0(R8)",
        "LOAD R9, 0(R8)"
    ]


def read_custom_program():
    print("\n========== ENTER CUSTOM PROGRAM ==========\n")

    print("Supported instructions:")
    print("  ADD R1, R2, R3")
    print("  SUB R1, R2, R3")
    print("  MUL R1, R2, R3")
    print("  LOAD R1, 4(R2)")
    print("  STORE R1, 4(R2)")
    print("  BEQ R1, R2, LABEL")
    print()
    print("Labels:")
    print("  LOOP:")
    print()
    print("Enter one instruction/label per line.")
    print("Type RUN on a new line when finished.\n")

    lines = []

    while True:
        text = input(f"{len(lines) + 1}> ").strip()

        if text.upper() == "RUN":
            break

        if not text:
            continue

        lines.append(text)

    if not lines:
        raise ValueError(
            "Program cannot be empty."
        )

    return lines


def initialize_custom_registers(simulator):
    print("\n========== INITIAL REGISTER VALUES ==========\n")

    print(
        "Enter register values as R1=10."
    )

    print(
        "Press Enter without typing anything when finished."
    )

    print(
        "Registers not entered will remain 0.\n"
    )

    while True:
        text = input("Register: ").strip()

        if text == "":
            break

        try:
            register, value = text.split("=")

            register = register.strip().upper()
            value = int(value.strip())

            if register not in simulator.cpu.registers:
                print(
                    "Invalid register. Use R0 to R15."
                )
                continue

            simulator.set_register(
                register,
                value
            )

        except ValueError:
            print(
                "Invalid format. Example: R1=10"
            )


def run_simulation(
    program_lines,
    forwarding,
    shared_memory,
    demo=False
):
    try:
        program = Program(
            program_lines
        )

        simulator = PipelineSimulator(
            program,
            forwarding=forwarding,
            shared_memory=shared_memory
        )

        if demo:
            initialize_demo_registers(
                simulator
            )
        else:
            initialize_custom_registers(
                simulator
            )

        print("\n========== PROGRAM TO EXECUTE ==========")

        program.print_program()

        print("\n========== INITIAL CPU STATE ==========")

        simulator.cpu.print_registers()

        simulator.run()

        simulator.print_timing_table()

        simulator.print_execution_log()

        simulator.print_hazard_report()

        analyzer = PerformanceAnalyzer(
            simulator
        )

        analyzer.print_report()

        print("\n========== FINAL CPU STATE ==========")

        simulator.cpu.print_registers()

        simulator.cpu.print_memory()

        print(
            "\nSimulation completed successfully."
        )

    except ValueError as error:
        print(
            "\nSIMULATION ERROR:",
            error
        )


def main():
    forwarding = True
    shared_memory = False

    while True:
        print_title()

        print("\n1. Run Demonstration Program")
        print("2. Enter Custom Program")
        print("3. Configure Simulator")
        print("4. View Current Configuration")
        print("5. Exit")

        choice = input(
            "\nSelect an option: "
        ).strip()

        if choice == "1":
            run_simulation(
                demonstration_program(),
                forwarding,
                shared_memory,
                demo=True
            )

            input(
                "\nPress Enter to return to menu..."
            )

        elif choice == "2":
            try:
                lines = read_custom_program()

                run_simulation(
                    lines,
                    forwarding,
                    shared_memory,
                    demo=False
                )

            except ValueError as error:
                print(
                    "\nERROR:",
                    error
                )

            input(
                "\nPress Enter to return to menu..."
            )

        elif choice == "3":
            forwarding, shared_memory = (
                configure_simulator()
            )

            print(
                "\nConfiguration updated."
            )

        elif choice == "4":
            print_configuration(
                forwarding,
                shared_memory
            )

            input(
                "\nPress Enter to return to menu..."
            )

        elif choice == "5":
            print(
                "\nSimulator closed."
            )
            break

        else:
            print(
                "\nInvalid option. Please select 1 to 5."
            )


if __name__ == "__main__":
    main()