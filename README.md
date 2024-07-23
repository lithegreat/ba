# [Porting OpenASIP Custom Operations to CoreDSL Syntax](<reference/BA.pdf>)

## BA of Hengsheng Li

The goal of this project is to evaluate the large pool of custom operations supported by the
OpenASIP2.0 Co-Design toolchain on our instruction set simulator (ISS) named ETISS using the
CoreDSL ecosystem.
### Steps:

- [X] 1. Literature Research
- [X] 2. Familiarize with involved tools (OpenASIP, CoreDSL, CoreDSL)
- [X] 3. Collect list of all custom OpenASIP operations
- [ ] 4. Develop methodology for translating the custom OpenASIP operations to the CoreDSL syntax
- [ ] 5. Generate ETISS architectures using the new instructions
- [ ] 6. Evaluate/Test/Benchmark the custom operations
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

## CoreDSL -> M2-ISA-R -> ETISS -> RISC-V step by step flow
``` shell
# ARCH=rv32imc_zicsr
# ABI=ilp32
ARCH=rv32gc
ABI=ilp32d
ETISS_ARCH=RV32IMACFD
PROG=hello_world

# Clone Repos
# test -d etiss || git clone git@github.com:tum-ei-eda/etiss.git
test -d etiss || git clone git@github.com:wysiwyng/etiss.git --branch coverage
test -d etiss_riscv_examples || git clone git@github.com:tum-ei-eda/etiss_riscv_examples.git --branch master
test -d etiss_arch_riscv || git clone git@github.com:tum-ei-eda/etiss_arch_riscv.git --recursive --branch coredsl_exceptions
test -d M2-ISA-R || git clone git@github.com:tum-ei-eda/M2-ISA-R.git --branch coredsl2

# Setup GCC
DOWNLOAD_GCC=1
if [[ "$DOWNLOAD_GCC" == "1" ]]
then
    RISCV_GCC_PREFIX=$(pwd)/${ARCH}_${ABI}
    test -f ${ARCH}_$ABI.tar.xz && rm ${ARCH}_${ABI}.tar.xz
    wget https://syncandshare.lrz.de/dl/fiWBtDLWz17RBc1Yd4VDW7/GCC/default/2023.11.27/Ubuntu/20.04/${ARCH}_${ABI}.tar.xz
    mkdir -p ${ARCH}_${ABI}
    tar xf ${ARCH}_${ABI}.tar.xz -C ${ARCH}_${ABI}
    rm ${ARCH}_${ABI}.tar.xz
else
    RISCV_GCC_PREFIX=/usr/local/research/projects/SystemDesign/tools/riscv/gcc/no-multilib/${ARCH}_${ABI}
fi
RISCV_GCC_NAME=riscv32-unknown-elf
test -f $RISCV_GCC_PREFIX/bin/$RISCV_GCC_NAME-gcc || echo "riscv gcc installation missing!"
echo $RISCV_GCC_PREFIX/bin/$RISCV_GCC_NAME
export PATH=$RISCV_GCC_PREFIX/bin/:$PATH

# Setup ETISS
mkdir -p etiss/build
cd etiss/build
cmake -DCMAKE_INSTALL_PREFIX=$(pwd)/install ..
make -j$(nproc) install
cd -

# Setup Target SW
# Prerequisite: install riscv64-unknown-elf-gcc
mkdir -p etiss_riscv_examples/build
cd etiss_riscv_examples/build
cmake -DCMAKE_TOOLCHAIN_FILE=$(pwd)/../rv32gc-toolchain.cmake -DCMAKE_INSTALL_PREFIX=$(pwd)/install -DRISCV_ARCH=$ARCH -DRISCV_ABI=$ABI -DRISCV_TOOLCHAIN_PREFIX=$RISCV_GCC_PREFIX -DRISCV_TOOLCHAIN_BASENAME=$RISCV_GCC_NAME ..
make -j$(nproc) install
cd -

# Test Simulation of example program
./etiss/build/bin/bare_etiss_processor -ietiss_riscv_examples/build/install/ini/$PROG.ini --arch.cpu=$ETISS_ARCH

# Setup M2-ISA-R
cd M2-ISA-R
virtualenv -p python3.8 venv  # Alternative (requires `apt install python3-venv`): python3 -m venv venv
source venv/bin/activate
pip install -e .
cd -

# Run M2-ISA-R
python -m m2isar.frontends.coredsl2.parser etiss_arch_riscv/top.core_desc  # Generate M2-ISA-R Metamodel
python -m m2isar.backends.etiss.writer etiss_arch_riscv/gen_model/top.m2isarmodel --separate --static-scalars  # Generate ETISS Architectures

# Patch ETISS Architectures
cp -r etiss_arch_riscv/gen_output/top/* etiss/ArchImpl/
cd etiss
git status
git restore ArchImpl/RV32IMACFD/RV32IMACFDArchSpecificImp.cpp  # These changes should not be applied!
git restore ArchImpl/RV64IMACFD/RV64IMACFDArchSpecificImp.cpp  # These changes should not be applied!
git add --all
git commit -m 'update etiss architectures'
cd -

# Rebuild ETISS
cmake -S etiss -B etiss/build
cmake --build etiss/build -j$(nproc)
cmake --install etiss/build

# Test if Simulation still works
./etiss/build/bin/bare_etiss_processor -ietiss_riscv_examples/build/install/ini/$PROG.ini --arch.cpu=$ETISS_ARCH

# Further notes:
# To compile for a different arch/abi: `-DRISCV_ARCH=rv32im -DRISCV_ABI=ilp32`
# Change ETISS settings (cpu_arch, jit,...), edit etiss_riscv_examples/elffile.ini.in and rebuild target sw
# When adding new ETISS cores, make sure to replace placeholder functions in RV*ArchSpecificImp.cpp with proper ones.
```