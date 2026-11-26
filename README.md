# Instruction Pipeline & Hazard Analysis Simulator

A configurable educational simulator for studying instruction pipelining, pipeline hazards, hazard-handling techniques, and pipeline performance in Computer Organization and Architecture (COA).

The simulator models a classic **5-stage instruction pipeline**:

```text
IF → ID → EX → MEM → WB
```

It supports instruction execution, RAW data hazard detection, pipeline stalls, data forwarding, load-use hazards, structural hazards, branch hazards, pipeline flushing, register and memory operations, and performance analysis through both a command-line interface and an interactive Tkinter GUI.

---

## Project Objective

The objective of this project is to design and implement a configurable instruction pipeline simulator that:

- Executes a sequence of instructions
- Simulates a 5-stage instruction pipeline
- Detects data, structural, and control hazards
- Applies basic hazard-handling techniques
- Supports data forwarding and pipeline stalling
- Handles taken and not-taken branches
- Visualizes pipeline execution cycle by cycle
- Evaluates pipeline performance using execution cycles, throughput, and speedup

---

## Key Features

### 5-Stage Instruction Pipeline

The simulator models:

| Stage | Name | Purpose |
|---|---|---|
| IF | Instruction Fetch | Fetches the next instruction |
| ID | Instruction Decode | Decodes instruction and identifies operands |
| EX | Execute | Performs ALU operations and resolves branches |
| MEM | Memory Access | Represents the memory-access stage |
| WB | Write Back | Represents completion/write-back stage |

---

## Supported Instructions

### Arithmetic Instructions

```text
ADD R1, R2, R3
SUB R1, R2, R3
MUL R1, R2, R3
```

Example:

```text
ADD R4, R1, R2
```

performs:

```text
R4 = R1 + R2
```

### Memory Instructions

```text
LOAD R1, 4(R2)
STORE R1, 4(R2)
```

Effective address:

```text
Address = Base Register + Offset
```

Example:

```text
LOAD R7, 4(R10)
```

uses:

```text
Address = R10 + 4
```

### Branch Instruction

```text
BEQ R1, R2, TARGET
```

The branch is taken when:

```text
R1 == R2
```

The simulator supports labels such as:

```text
BEQ R1, R2, TARGET

ADD R3, R4, R5

TARGET:
MUL R6, R7, R8
```

---

## Register File

The simulator provides 16 registers:

```text
R0 – R15
```

`R0` is maintained as a constant zero register.

Register values can be initialized from the CLI or GUI before running a simulation.

---

## Data Memory

A simulated data memory is provided for `LOAD` and `STORE` instructions.

Example:

```text
R10 = 100
R6  = 125

STORE R6, 4(R10)
```

stores:

```text
Memory[104] = 125
```

A later instruction:

```text
LOAD R7, 4(R10)
```

loads:

```text
R7 = 125
```

---

# Pipeline Hazards

## 1. Data Hazards

The simulator detects **RAW (Read After Write)** dependencies.

Example:

```text
ADD R1, R2, R3
SUB R4, R1, R5
```

`ADD` produces `R1`, while `SUB` requires `R1`.

Therefore:

```text
ADD → R1 → SUB
```

creates a RAW data hazard.

---

## Pipeline Stalling

When forwarding is disabled, dependent instructions wait until the required value becomes available according to the simulator's pipeline model.

Example timing:

```text
ADD R1,R2,R3    IF  ID  EX  MEM WB
SUB R4,R1,R5        IF  ID  ST  ST  EX  MEM WB
```

`ST` represents a pipeline stall.

---

## Data Forwarding

Data forwarding can be enabled or disabled.

### Forwarding OFF

Example result:

```text
Execution Cycles : 11
Data Hazards     : 2
Stall Cycles     : 4
```

### Forwarding ON

For the same arithmetic dependency sequence:

```text
Execution Cycles : 7
Data Hazards     : 2
Stall Cycles     : 0
```

The dependencies still exist, but forwarding removes unnecessary waiting for supported arithmetic dependencies.

---

## Load-Use Hazard

A load-use dependency requires special handling.

Example:

```text
LOAD R1, 0(R2)
ADD  R3, R1, R4
```

Even with forwarding enabled, the immediately dependent instruction requires one stall in the simulator model.

Example result:

```text
Execution Cycles : 8
Data Hazards     : 2
Stall Cycles     : 1
```

---

# Structural Hazards

The simulator supports two memory configurations.

### Separate Instruction and Data Memory

```text
Instruction Memory ≠ Data Memory
```

Instruction fetch and data-memory activity do not compete for one modeled memory resource.

### Shared Instruction/Data Memory

```text
Instruction Memory = Data Memory
```

When a `LOAD` or `STORE` occupies the memory resource while another instruction needs to be fetched, the simulator detects a structural conflict.

Example:

```text
MEM → needs shared memory
IF  → needs shared memory
```

Result:

```text
Structural Hazard
        ↓
Instruction Fetch Delayed
```

The GUI allows switching between the two configurations.

---

# Control Hazards

The simulator supports `BEQ` branch instructions.

Branches are resolved in the **EX stage**.

Example:

```text
ADD R4, R1, R2
BEQ R4, R3, TARGET
SUB R5, R1, R2
MUL R6, R1, R2

TARGET:
ADD R7, R4, R3
```

If:

```text
R4 == R3
```

the branch is taken.

Younger wrong-path instructions are flushed and the Program Counter is redirected to the target label.

Pipeline visualization uses:

```text
FL = Flushed Instruction
```

Example:

```text
SUB ...    IF  ID  FL
MUL ...        IF  FL
```

For a branch that is not taken, sequential execution continues and no flush penalty is applied.

---

# Performance Analysis

The simulator calculates several performance metrics.

## Execution Cycles

Total number of pipeline cycles required by the simulation.

## Throughput

```text
Throughput =
Executed Instructions / Pipeline Cycles
```

Unit:

```text
instructions/cycle
```

## Non-Pipelined Reference Cycles

For the educational comparison used by this project:

```text
Non-Pipelined Cycles =
Executed Instructions × 5
```

## Speedup

```text
Speedup =
Non-Pipelined Cycles / Pipelined Cycles
```

## Pipeline Efficiency

The simulator also reports a simplified pipeline-efficiency metric for supporting analysis.

---

# Graphical User Interface

The project includes an interactive GUI built using **Python Tkinter**.

Run:

```bash
python gui.py
```

The GUI provides:

- Program editor
- Initial register configuration
- Forwarding ON/OFF control
- Shared/separate memory configuration
- Built-in demonstration scenarios
- Cycle-by-cycle pipeline visualization
- Stall (`ST`) visualization
- Flush (`FL`) visualization
- Hazard analysis
- Performance metrics
- Final register state
- Data memory state
- Execution log

---

# Built-In Simulation Scenarios

The GUI includes the following scenarios:

### Full Demonstration

Demonstrates:

- Arithmetic execution
- Data dependencies
- Forwarding
- Branch taken
- Pipeline flushing
- Branch target execution
- STORE
- LOAD
- Performance analysis

### No Hazard

Demonstrates an ideal pipeline without dependency stalls.

### RAW Hazard

Demonstrates RAW dependencies and pipeline stalls.

This scenario can also be used to compare:

```text
Forwarding OFF
vs
Forwarding ON
```

### Load-Use Hazard

Demonstrates the one-cycle load-use stall with forwarding enabled.

### Structural Hazard

Demonstrates an IF/MEM resource conflict using shared instruction/data memory.

### Branch Taken

Demonstrates:

```text
Branch Taken
→ Wrong-path instructions flushed
→ PC redirected to target
```

### Branch Not Taken

Demonstrates sequential execution without a flush penalty.

---

# Example Full Demonstration

Initial register values:

```text
R1 = 10
R2 = 20
R3 = 30
R8 = 100
```

Program:

```text
ADD R4, R1, R2
BEQ R4, R3, TARGET
SUB R5, R1, R2
MUL R6, R1, R2

TARGET:
ADD R7, R4, R3
STORE R7, 0(R8)
LOAD R9, 0(R8)
```

Execution:

```text
R4 = 10 + 20 = 30
```

Branch:

```text
R4 == R3
30 == 30
```

Therefore:

```text
Branch Taken
```

`SUB` and `MUL` are flushed.

Then:

```text
R7 = R4 + R3
R7 = 60
```

Memory operation:

```text
Memory[100] = 60
```

Load:

```text
R9 = Memory[100]
R9 = 60
```

Example performance result:

```text
Pipeline Cycles : 11
Data Hazards    : 2
Control Hazards : 1
Control Penalty : 2
Throughput      : 0.455 instructions/cycle
Speedup         : 2.273x
```

---

# Project Architecture

```text
                     Program Input
                          │
                          ▼
                 ┌──────────────────┐
                 │  Program Loader  │
                 │ Labels / Targets │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │Instruction Parser│
                 └────────┬─────────┘
                          │
                          ▼
                    Program Counter
                          │
                          ▼
        ┌─────────────────────────────────┐
        │       5-Stage Pipeline          │
        │                                 │
        │ IF → ID → EX → MEM → WB         │
        └──────────────┬──────────────────┘
                       │
          ┌────────────┼─────────────┐
          │            │             │
          ▼            ▼             ▼
         ALU       Data Memory   Register File
          │
          ├── RAW Hazard Detection
          ├── Stalling
          ├── Data Forwarding
          ├── Structural Hazard Detection
          └── Branch Resolution / Flush
                       │
                       ▼
              Performance Analyzer
                       │
                       ▼
                  Tkinter GUI
```

---

# Project Structure

```text
COA-Pipeline-Simulator/
│
├── main.py
├── gui.py
│
├── instruction.py
├── parser.py
├── program.py
├── cpu.py
├── pipeline.py
├── hazard.py
├── performance.py
│
├── test_parser.py
├── test_pipeline.py
├── test_hazard.py
├── test_cpu.py
├── test_program.py
├── test_performance.py
├── test_all.py
│
├── README.md
└── .gitignore
```

---

# Installation

## Requirements

- Python 3
- Tkinter

No external Python package is required for the current simulator.

Check Python:

```bash
python --version
```

---

# Running the Project

## Graphical Interface

Recommended:

```bash
python gui.py
```

## Command-Line Interface

```bash
python main.py
```

---

# Running the Complete Test Suite

```bash
python test_all.py
```

Current regression-test result:

```text
Passed : 36
Failed : 0
Total  : 36

ALL TESTS PASSED - CORE SIMULATOR IS STABLE.
```

The test suite verifies:

- Instruction parsing
- Invalid-input rejection
- ADD execution
- SUB execution
- MUL execution
- LOAD
- STORE
- Zero register behavior
- Ideal pipeline timing
- RAW hazard detection
- Pipeline stalls
- Data forwarding
- Load-use hazard
- Structural hazard
- Branch taken
- Branch not taken
- Pipeline flushing
- Branch-target execution
- Performance analysis

---

# Technologies Used

- Python
- Tkinter
- Git
- GitHub
- Visual Studio Code

---

# COA Concepts Demonstrated

The project directly demonstrates concepts from Computer Organization and Architecture, including:

- Instruction formats
- CPU registers
- Arithmetic operations
- Instruction execution
- Program Counter
- Memory operations
- Instruction pipeline
- Pipeline stages
- Data dependency
- RAW hazards
- Pipeline stalls
- Data forwarding
- Structural/resource hazards
- Branch/control hazards
- Pipeline flushing
- Shared vs separate memory resources
- Throughput
- Pipeline speedup
- Performance analysis

The project is especially aligned with **instruction execution, memory organization, control flow, and pipelining/hazard concepts**.

---

# Simulation Assumptions and Limitations

This project is an **educational cycle-level simulator**, not a transistor-level or hardware-accurate processor emulator.

Important assumptions include:

- A simplified 5-stage pipeline model is used.
- The instruction set is intentionally small.
- Registers are limited to `R0–R15`.
- RAW dependencies are the primary modeled data hazard.
- Forwarding behavior is simplified for educational analysis.
- A load-use dependency requires one stall with forwarding.
- Structural hazards are demonstrated using a configurable shared-memory resource.
- `BEQ` branches are resolved in the EX stage.
- A taken branch flushes younger instructions already in the pipeline.
- Performance calculations use a simplified five-cycle-per-instruction non-pipelined reference model.
- CPU instruction semantics are simulated in software rather than at RTL, gate, or transistor level.

These assumptions keep the simulator focused on understanding pipeline behavior and performance rather than reproducing a specific commercial processor.

---

# Future Enhancements

Possible extensions include:

- Additional arithmetic and logical instructions
- More branch instructions
- WAR and WAW dependency analysis
- Configurable pipeline depth
- Branch prediction
- Multiple functional units
- Configurable cache behavior
- Advanced forwarding paths
- Step-by-step clock execution
- Animated datapath visualization
- Exporting simulation results
- Additional performance graphs

---

# Project

**Course:** Computer Organization and Architecture  
**Course Code:** CSEG1032  
**Project:** Instruction Pipeline and Hazard Analysis Simulator

The project was developed as an educational tool for analyzing instruction execution, pipeline hazards, hazard-handling techniques, and performance in a configurable processor pipeline.