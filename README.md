## HPXSc-Spack

This repository contains the [Spack](https://github.com/spack/spack#-spack) package for the [HPX](https://github.com/STEllAR-GROUP/hpx) code. 
Additionally, the repository also includes new/modified/updated spack packages of software HPX can depend on.

The repository is forked from the [Octo-Tiger](https://github.com/G-071/octotiger-spack) spack package.

### Package features:

- Supports all CPU/GPU backends of HPX (Kokkos, CUDA, HIP, SYCL)
- Supports distributed builds (with the HPX networking backends tcp, mpi or lci)

### List of added/modified packages:

- Added CPPuddle package
- Modified HPX package by adding a SYCL variant (depends on dpcpp; tested on NVIDIA/AMD GPUs)
- Modified HPX package by adding a LCI parcelport variant to have an additional networking backend available
- Modified HPX-Kokkos package by adding SYCL variant, adding variants for the future types and exposing the hpx-kokkos tests to spack
- Modified Kokkos package by adding an use_unsupported_sycl_arch variant (which allows using the SYCL execution space on non-Intel GPU). Also includes a patch for the kokkos CMakeLists which allows using this on AMDGPUs (not just NVIDIA)
- Modified dpcpp package by using the package.py from the [this spack PR](https://github.com/spack/spack/pull/38981) that's updating (not merged as of yet) and by attempting to fix the library/linking issue in dependent packages

### Repo installation:

```sh
# spack install
git clone --depth=100 --branch=releases/v0.20 https://github.com/spack/spack.git /path/to/spack
cd /path/to/spack
. share/spack/setup-env.sh
# spack repo install
git clone https://github.com/constrackor/hpxsc-spack.git /path/to/hpxsc-spack
spack repo add /path/to/hpxsc-spack
# use system packages
spack compiler find # search currently loaded compilers
spack external find cuda # replace cuda by desired packages or leave blank
# Check package availability and its variants:
spack info hpxsc
```

### Usage examples (Rewrite)
- Basic Octo-Tiger installation:
```sh
# Basic octotiger installation
spack install --fresh --test=root octotiger~cuda~kokkos
# octotiger install with specific compiler/cuda versions and run octotiger tests
spack install --fresh --test=root octotiger+cuda+kokkos%gcc@11^cuda@11.8.89^cmake@3.26.4^kokkos@3.7.00 cuda_arch=75
# Use one of the installs
spack load octotiger~cuda~kokkos
octotiger --help

```
- Octo-Tiger CUDA/Kokkos dev build (RTX 2060):
```sh
module load cuda/11.8
spack external find cuda # finds cuda@11.8.89 in this example...
# Get fresh src dir
git clone https://github.com/STEllAR-GROUP/octotiger
cd octotiger
# Setup development shell with all dependencies (drops user into the build process right after cmake)
spack dev-build --fresh --drop-in bash --until cmake --test=root octotiger+cuda+kokkos cuda_arch=75 @master%gcc@11^cuda@11.8.89
cd spack_build_id #exact dir name ist printed by the last command
# Use with usual edit-make-test cycle after editing the src directory...
make -j16
ctest --output-on-failure
./octotiger --help

```
- Octo-Tiger HIP/Kokkos dev build (MI100):
```sh
module load rocm/5.4.6
spack compiler find # should find rocmcc@5.4.6
spack external find hip llvm-amdgpu hsa-rocr-dev # other erquired 5.4.6 packges from the rocm module
git clone https://github.com/STEllAR-GROUP/octotiger
cd octotiger
# long, manual spec for dev build:
spack dev-build --drop-in bash --until cmake --test=root octotiger+rocm+kokkos amdgpu_target=gfx908@master%rocmcc@5.4.6 ^asio@1.16.0^hpx max_cpu_count=128 amdgpu_target=gfx908 ^hip@5.4.6 ^llvm-amdgpu@5.4.6^kokkos amdg
pu_target=gfx908 ^hpx-kokkos amdgpu_target=gfx908
# new alternative (octotiger package now internally propgates the amdgpu_target to hpx, kokkos and hpx-kokkos, enabling this shorter version):
spack dev-build --drop-in bash --until cmake --test=root octotiger+rocm+kokkos amdgpu_target=gfx908@master%rocmcc@5.4.6 ^asio@1.16.0^hpx max_cpu_count=128 ^hip@5.4.6 ^llvm-amdgpu@5.4.6
cd spack_build_id #exact dir name ist printed by the last command
# Use with usual edit-make-test cycle after editing the src directory...
make -j32
ctest --output-on-failure
```

- Octo-Tiger SYCL/Kokkos dev build (V100):
```sh
module load cuda/12
git clone https://github.com/STEllAR-GROUP/octotiger
cd octotiger
spack dev-build --fresh --drop-in bash --until cmake --test=root octotiger@master -cuda -rocm +sycl %gcc@10 ^kokkos use_unsupported_sycl_arch=70 ^hpx sycl_target_arch=70 ^cppuddle
cd spack_build_id #exact dir name ist printed by the last command
# Needed without the libs fix in the dpcpp package
#export LD_LIBRARY_PATH="$(spack find -l --paths dpcpp | tail -n1 | awk '{ print $3 }')/lib":${LD_LIBRARY_PATH}
# Use with usual edit-make-test cycle after editing the src directory...
make -j32
ctest --output-on-failure
```
