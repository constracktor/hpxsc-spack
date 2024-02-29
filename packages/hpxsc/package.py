# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.error import SpackError
from spack.package import *


class Hpxsc(CMakePackage, CudaPackage, ROCmPackage):
    """HPX for Scientific Computing. It was
    implemented using high-level C++ libraries, specifically HPX and Kokkos,
    which allows its scalability and usage on different hardware platforms."""

    homepage = "https://github.com/constracktor/hpxsc-spack"
    url = "https://github.com/constracktor/"
    git = "https://github.com/constracktor/"

    maintainers("constracktor")

    # Development versions
    version("master", branch="master", submodules=True, preferred=True)
    # Official Github Releases
    # -> 0.1.0 Default release
    version("0.1.0", sha256="")
    
    # Patch minor issues depending on what version/variants we are using
 
    # All available variants:
    variant('sycl', default=False, when="@0.1.0:",
            description=("Build HPXSc with SYCL (also allows Kokkos"
                         " kernels to run with SYCL)"))
    
    variant('cuda', default=False, when="@0.1.0:",
            description=("Build HPXSc with CUDA support"))
    
    variant('rocm', default=False, when="@0.1.0:",
            description=("Build HPXSc with ROCm support"))
    
    variant('kokkos', default=False, when="@0.1.0:",
            description='Build HPX with kokkos based kernels')
    
    variant('kokkos_hpx_kernels', default=False, when='@0.1.0: +kokkos ',
            description=("Use HPX execution space for CPU Kokkos kernels"
                         " (instead of the Serial space)"))
    
    variant('simd_library', default='KOKKOS', when='@0.1.0: +kokkos',
            description=("Use either kokkos (for kokkos simd types) or std"
                         " (for std::experimental::simd types)"),
            values=('KOKKOS', 'STD'), multi=False)
    
    variant('simd_extension', default='DISCOVER', when='@0.1.0:',
            description=("Enforce specific SIMD extension or autoselect "
                         "(discover) appropriate one"),
            values=('DISCOVER', 'SCALAR', 'AVX', 'AVX512', 'NEON', 'SVE'),
            multi=False)
    
    variant('boost_multiprecision', default=False,
            description=("Use Boost.Multiprecision Instead of GCC "
                         "Quad-Precision Math Library"))
    
    variant('cxx20', default=False,
            description=("Compile HPXSc with c++20"))

    # Misc dependencies:
    #depends_on('cmake@3.27.4:', type='build')
    #depends_on('cuda', when='+cuda')
    #depends_on("dpcpp", when="+sycl")

    # Pick HPX version and cxxstd depending on octotiger version:
    depends_on('hpx@1.9.1: cxxstd=17', when='@0.1.0:')
    # Pick HPX GPU variants depending on octotiger's GPU variants:
    depends_on('hpx +cuda +async_cuda', when='+cuda')
    depends_on('hpx +rocm ', when='+rocm')
    depends_on('hpx -cuda -rocm', when='-cuda -rocm')
    depends_on("hpx +sycl ", when="+sycl")

    # Pick hpx-kokkos version that fits octotigers variant:
    depends_on('hpx-kokkos@0.4.0:', when='@0.1.0:+kokkos')
    # hpx-kokkos GPU variant
    depends_on("hpx-kokkos +sycl ", when="+sycl+kokkos")
    depends_on('hpx-kokkos +cuda', when='+kokkos +cuda')
    depends_on('hpx-kokkos -cuda', when='+kokkos -cuda')

    # Pick cppuddle version:
    depends_on('cppuddle@0.2.1: +hpx', when='@0.1.0:')

    # Pick Kokkos Version depending on Octotiger version:
    depends_on("kokkos@3.6.01: ", when="@0.1.0:+kokkos")
    depends_on("kokkos@4.1.00: +hpx ", when="+kokkos_hpx_kernels @0.1.0:")

    # Pick Kokkos execution spaces and GPU targets depending on the octotiger targets:
    kokkos_string = 'kokkos +serial +aggressive_vectorization '
    depends_on("kokkos +sycl ", when="+sycl+kokkos")
    depends_on(kokkos_string + ' -cuda -cuda_lambda -wrapper',
               when='+kokkos -cuda')
    depends_on(kokkos_string + ' +wrapper ', when='+kokkos +cuda %gcc')

    for sm_ in CudaPackage.cuda_arch_values:
        # This loop propgates the chosem cuda_arch to kokkos.
        depends_on(kokkos_string + ' +cuda +cuda_lambda cuda_arch={0}'.format(
            sm_), when='+kokkos +cuda cuda_arch={0}'.format(sm_))
        depends_on('hpx-kokkos +cuda cuda_arch={0}'.format(sm_),
                when='+kokkos +cuda cuda_arch={0}'.format(sm_))
        depends_on('hpx +cuda cuda_arch={0}'.format(sm_),
                when='+cuda cuda_arch={0}'.format(sm_))
    for gfx in ROCmPackage.amdgpu_targets:
        # This loop propgates the chosem amdgpu_target to hpx, kokkos and hpx-kokkos.
        depends_on(kokkos_string + ' +rocm amdgpu_target={0}'.format(gfx),
                   when='+kokkos +rocm amdgpu_target={0}'.format(gfx))
        depends_on('hpx +rocm amdgpu_target={0}'.format(gfx),
                   patches=['hpx_rocblas.patch'],
                   when='+rocm amdgpu_target={0}'.format(gfx))
        depends_on('hpx-kokkos@master +rocm amdgpu_target={0}'.format(gfx),
                   when='+kokkos +rocm amdgpu_target={0}'.format(gfx))

    # Known conflicts
    conflicts("+cuda", when="cuda_arch=none")
    conflicts("+kokkos_hpx_kernels", when="~kokkos")
    conflicts("simd_library=STD", when="%gcc@:10")
    conflicts("simd_library=STD", when="%clang")
    conflicts("simd_extension=SVE simd_library=STD", when="~cxx20")
    conflicts("+cuda", when="+rocm",
              msg="CUDA and ROCm are not compatible in HPXSc.")
    conflicts("+rocm", when="-kokkos",
              msg="ROCm support requires building with Kokkos for the correct arch flags.")

    build_directory = "spack-build"

    def cmake_args(self):
        spec, args = self.spec, []
        return args

    def check(self):
        if self.run_tests:
            # Redefine ctest to make sure -j parameter is dropped 
            # (No parallel tests allowed as HPX needs all cores for
            # each test)
            with working_dir(self.build_directory):
                ctest("--output-on-failure")

    # Not required due to adding setup_dependent environment in the dpcpp package
    # def setup_run_environment(self, env):
    #     if self.spec.satisfies("+sycl"):
    #         env.prepend_path("LD_LIBRARY_PATH", join_path(self.spec["dpcpp"].prefix, "lib"))

    # def setup_build_environment(self, env):
    #     if self.spec.satisfies("+sycl"):
    #         env.prepend_path("LD_LIBRARY_PATH", join_path(self.spec["dpcpp"].prefix, "lib"))
