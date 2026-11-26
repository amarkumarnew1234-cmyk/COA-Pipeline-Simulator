from parser import parse_instruction


class Program:

    def __init__(self, lines):

        self.instructions = []
        self.labels = {}

        self._load(lines)

    def _load(self, lines):

        # ==========================================
        # PASS 1
        # Find labels and instruction positions
        # ==========================================

        instruction_index = 0

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # Ignore comments
            if line.startswith("#"):
                continue

            # Label definition
            if line.endswith(":"):

                label = line[:-1].strip().upper()

                if not label:
                    raise ValueError(
                        "Label cannot be empty."
                    )

                if label in self.labels:
                    raise ValueError(
                        f"Duplicate label: {label}"
                    )

                self.labels[label] = instruction_index

                continue

            instruction_index += 1

        # ==========================================
        # PASS 2
        # Parse actual instructions
        # ==========================================

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if line.endswith(":"):
                continue

            instruction = parse_instruction(line)

            self.instructions.append(
                instruction
            )

        # ==========================================
        # VALIDATE BRANCH TARGETS
        # ==========================================

        for instruction in self.instructions:

            if instruction.opcode == "BEQ":

                if instruction.label not in self.labels:

                    raise ValueError(
                        f"Undefined branch label: "
                        f"{instruction.label}"
                    )

    def get_target_index(self, label):

        label = label.upper()

        if label not in self.labels:

            raise ValueError(
                f"Unknown label: {label}"
            )

        return self.labels[label]

    def print_program(self):

        print(
            "\n========== PROGRAM ==========\n"
        )

        reverse_labels = {}

        for label, index in self.labels.items():

            reverse_labels.setdefault(
                index,
                []
            ).append(label)

        for index, instruction in enumerate(
            self.instructions
        ):

            if index in reverse_labels:

                for label in reverse_labels[index]:

                    print(
                        f"{label}:"
                    )

            print(
                f"{index:<3} {instruction}"
            )

        print(
            "\n========== LABEL TABLE ==========\n"
        )

        if not self.labels:

            print("No labels.")

        else:

            for label, index in self.labels.items():

                print(
                    f"{label:<15} -> "
                    f"Instruction {index}"
                )