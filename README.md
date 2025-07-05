# Grasp Pose Generator

**Grasp Pose Generator** is a Python package that provides bindings for the C++ Grasp Pose Generator (GPG), enabling the creation of grasp candidates for 3D point clouds. This tool is essential for robotic manipulation tasks, allowing robots to determine feasible grasping positions on objects represented by point clouds.

## Features

- Generate 6-DOF grasp poses for 2-finger grippers.
- Evaluate grasp candidates for antipodal properties using geometric conditions.
- Seamless integration with Python for easy incorporation into robotic pipelines.

## Installation

To install the `grasp_pose-generator` package, use pip:

```bash
pip install grasp-pose-generator
```

### Steps

1. Install [Vcpkg](https://github.com/microsoft/vcpkg) and configure it on your system.
2. Clone the [Pybind11](https://github.com/pybind/pybind11) repository into a `dependencies` directory in your project root:

   ```bash
   mkdir dependencies
   cd dependencies
   git clone https://github.com/pybind/pybind11.git
   ```
3. Install the package:

   ```bash
   pip install .
   ```

This process will compile the C++ code using the Vcpkg dependencies and the Pybind11 bindings.

## Usage

Here's a basic example demonstrating how to generate grasp poses for a given point cloud:

```python
import numpy as np
import grasp_pose_generator as gpg

# Generate a random point cloud (replace with your actual point cloud data)
points = np.random.rand(3000, 3)  # n x 3 numpy array

# Parameters
num_samples = 10000
show_grasp = False
gripper_config_file = "path/to/gripper_params.cfg"  # Replace with the path to your gripper configuration file

# Generate grasps
grasps = gpg.generate_grasps(points, num_samples, show_grasp, gripper_config_file)

# Convert grasps to transformation matrices
pose_list = []
for grasp in grasps:
    pose = np.eye(4)
    pose[:3, 0] = grasp.get_grasp_approach()
    pose[:3, 1] = grasp.get_grasp_binormal()
    pose[:3, 2] = grasp.get_grasp_axis()
    pose[:3, 3] = grasp.get_grasp_bottom()
    pose_list.append(pose)
```

Ensure that you have a valid gripper configuration file. An example configuration file can be found in the [gripper_params.cfg](https://github.com/AliRezaBeigy/grasp_pose_generator/blob/master/example/gripper_params.cfg).

## Example with a Simple Box

To visualize grasp generation on a simple box, you can run the provided example script:

```bash
python example/example.py
```

Press `R` during the visualization to see the generated grasp poses.

## Build

To build the `grasp-pose-generator` package from source, follow these steps:

### Prerequisites
- Python 3.6 or later
- [Vcpkg](https://github.com/microsoft/vcpkg) installed and configured
- CMake 3.20 or later
- A C++ compiler (e.g., MSVC for Windows)
- Dependencies: Eigen3, PCL (with VTK), Boost (installed via Vcpkg)

### Steps

1. Install [Vcpkg](https://github.com/microsoft/vcpkg) and configure it on your system. For Windows, use the `x64-windows` triplet to install dependencies:
   ```bash
   vcpkg install eigen3:x64-windows pcl[vtk]:x64-windows boost-thread:x64-windows
   ```
   Set the `VCPKG_TOOLCHAIN_FILE` environment variable:
   ```bash
   set VCPKG_TOOLCHAIN_FILE=C:\path\to\vcpkg\scripts\buildsystems\vcpkg.cmake
   ```

2. Clone the [Pybind11](https://github.com/pybind/pybind11) repository into a `dependencies` directory in your project root:
   ```bash
   mkdir dependencies
   cd dependencies
   git clone https://github.com/pybind/pybind11.git
   cd ..
   ```

3. Install build tools:
   ```bash
   pip install build
   ```

4. Build the package:
   ```bash
   python -m build
   ```

5. Install the package locally to test:
   ```bash
   pip install dist\*
   ```

This process will compile the C++ code using Vcpkg dependencies and Pybind11 bindings, generating a wheel compatible with your Python version.

## License

This project is licensed under the MIT License.

## Acknowledgments

This package is an improved and extended version of the original [pyGPG](https://github.com/lianghongzhuo/pygpg) by Hongzhuo Liang. The core grasp generation functionality is based on the [Grasp Pose Generator (GPG)](https://github.com/atenpas/gpg) by Andreas ten Pas.
