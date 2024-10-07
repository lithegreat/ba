# [Porting OpenASIP Custom Operations to CoreDSL Syntax](<reference/BA.pdf>)

## BA of Hengsheng Li

The goal of this project is to evaluate the large pool of custom operations supported by the
OpenASIP2.0 Co-Design toolchain on our instruction set simulator (ISS) named ETISS using the
CoreDSL ecosystem.
### Steps:

- [X] 1. Literature Research
- [X] 2. Familiarize with involved tools (OpenASIP, CoreDSL, CoreDSL)
- [X] 3. Collect list of all custom OpenASIP operations
- [X] 4. Develop methodology for translating the custom OpenASIP operations to the CoreDSL syntax
- [X] 5. Generate ETISS architectures using the new instructions
- [X] 6. Evaluate/Test/Benchmark the custom operations
- [ ] 7. Optional: Allow ETISS to be used as OpenASIP2.0 target architecture.

#### week 1-4:
- literature (openasip papers and previous work regarding operation set customization and TTA vs. operational triggering)
- learn how to use opensip (Open ASIP Tour), setup M2-ISA-R to convert coredsl2 files into etiss patches, compile and run programs with etiss simulator

#### week 5-10:
- implementation (sketch + proof of concept first, then coding)

#### week 11-12:
- buffer

#### week 13-16:
- testing
- evaluation
- experiments

#### week 17-20:
- writing thesis
- prepare slides

### Related Literature/Tools:
- [Extended Abstract: A Flexible Simulation Environment for RISC-V](<reference/Reference Paper/2023-06-07-Karsten-EMRICH-abstract.pdf>)
- [The Extendable Translating Instruction Set Simulator (ETISS) interlinked with an MDA Framework for fast RISC Prototyping](<reference/Reference Paper/The_extendable_translating_instruction_set_simulat.pdf>)
- https://github.com/tum-ei-eda/etiss
- https://github.com/Minres/CoreDSL/wiki/CoreDSL-2-programmer's-manual
- http://openasip.org/release_2_0.html
- [OpenASIP 2.0: Co-Design Toolset for RISC-V Application-Specific Instruction-Set Processors](<reference/Reference Paper/OpenASIP_RISC_V_ASAP_2022_.pdf>)
- https://github.com/cpc/openasip