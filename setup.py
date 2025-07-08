import os
import subprocess
import sys
import setuptools
import shlex

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
    "linux-x86_64": "x64",
    "linux-aarch64": "ARM64",
}

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir}",
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DPYTHON_EXECUTABLE={sys.executable}"
        ]

        # Parse CMAKE_ARGS environment variable if it exists
        cmake_args_env = os.environ.get("CMAKE_ARGS")
        if cmake_args_env:
            # Parse the CMAKE_ARGS string and add to cmake_args
            parsed_args = shlex.split(cmake_args_env)
            cmake_args.extend(parsed_args)
            print(f"Added CMAKE_ARGS from environment: {parsed_args}")

        # Check for Conan toolchain file (alternative to vcpkg)
        conan_toolchain = os.path.join(self.build_temp, "conan_toolchain.cmake")
        if os.path.exists(conan_toolchain):
            cmake_args.append(f"-DCMAKE_TOOLCHAIN_FILE={conan_toolchain}")
            print(f"Using Conan toolchain: {conan_toolchain}")
        else:
            # Check for system-wide toolchain file
            cmake_toolchain = os.environ.get("CMAKE_TOOLCHAIN_FILE")
            if cmake_toolchain:
                cmake_args.append(f"-DCMAKE_TOOLCHAIN_FILE={cmake_toolchain}")
                print(f"Using CMAKE_TOOLCHAIN_FILE: {cmake_toolchain}")

        # Add platform-specific arguments
        if sys.platform.startswith("win"):
            # Windows-specific arguments
            if self.plat_name in PLAT_TO_CMAKE:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]
        elif sys.platform.startswith("linux"):
            # Linux-specific arguments
            cmake_args += ["-DCMAKE_SYSTEM_NAME=Linux"]
            # Set architecture if needed
            if self.plat_name == "linux-x86_64":
                cmake_args += ["-DCMAKE_SYSTEM_PROCESSOR=x86_64"]
            elif self.plat_name == "linux-aarch64":
                cmake_args += ["-DCMAKE_SYSTEM_PROCESSOR=aarch64"]
        else:
            raise RuntimeError(f"Unsupported platform: {self.plat_name}")

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Copy conan_toolchain.cmake to build directory if it exists in source
        source_conan_toolchain = os.path.join(ext.sourcedir, "conan_toolchain.cmake")
        if os.path.exists(source_conan_toolchain):
            import shutil
            shutil.copy2(source_conan_toolchain, conan_toolchain)
            print(f"Copied Conan toolchain to build directory")

        # Debug: Print all CMake arguments
        print(f"CMake arguments: {cmake_args}")

        # Run CMake commands
        subprocess.check_call([
            "cmake", ext.sourcedir
        ] + cmake_args, cwd=self.build_temp)

        subprocess.check_call([
            "cmake", "--build", ".", "--config", "Release", "--parallel", str(os.cpu_count() or 2)
        ], cwd=self.build_temp)

setup(
    name="grasp_pose_generator",
    author="AliReza Beigy",
    version="1.1.0",
    license="MIT",
    python_requires=">=3.9",
    platforms=["nt", "posix"],
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    author_email="alireza.beigy.rb@gmail.com",
    description="A binding of gpg using pybind11 and CMake",
    ext_modules=[CMakeExtension("grasp_pose_generator")],
    cmdclass={"build_ext": CMakeBuild},
)
