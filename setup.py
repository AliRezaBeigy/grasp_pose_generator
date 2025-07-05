import os
import subprocess
import sys
import setuptools

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

        # Get the Vcpkg toolchain path from an environment variable
        vcpkg_toolchain = os.environ.get("VCPKG_TOOLCHAIN_FILE")
        if not vcpkg_toolchain:
            raise RuntimeError("The VCPKG_TOOLCHAIN_FILE environment variable is not set.")

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir}",
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_toolchain}",
            f"-DPYTHON_EXECUTABLE={sys.executable}"
        ]

        # Add platform-specific arguments
        if self.plat_name in PLAT_TO_CMAKE:
            cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]
        elif sys.platform.startswith("linux"):
            cmake_args += ["-DCMAKE_SYSTEM_NAME=Linux"]
        else:
            raise RuntimeError(f"Unsupported platform: {self.plat_name}")

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Run CMake commands
        subprocess.check_call([
            "cmake", ext.sourcedir
        ] + cmake_args, cwd=self.build_temp)

        subprocess.check_call([
            "cmake", "--build", ".", "--config", "Release"
        ], cwd=self.build_temp)

setup(
    name="grasp_pose_generator",
    author="AliReza Beigy",
    version="1.0.1",
    license="MIT",
    python_requires=">=3.6",
    platforms=["nt", "posix"],
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    author_email="alireza.beigy.rb@gmail.com",
    description="A binding of gpg using pybind11 and CMake",
    ext_modules=[CMakeExtension("grasp_pose_generator")],
    cmdclass={"build_ext": CMakeBuild},
)
