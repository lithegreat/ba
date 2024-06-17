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