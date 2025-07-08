cmake_minimum_required(VERSION 3.20)
project(grasp_pose_generator)
set(CMAKE_BUILD_TYPE Release)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if we have explicit Python paths provided (from manylinux environment)
if(DEFINED Python3_EXECUTABLE AND DEFINED Python3_INCLUDE_DIRS AND DEFINED Python3_LIBRARIES)
    # Use explicitly provided Python paths - skip find_package to avoid conflicts
    message(STATUS "Using explicitly provided Python3 paths (skipping find_package):")
    message(STATUS "  Python3_EXECUTABLE: ${Python3_EXECUTABLE}")
    message(STATUS "  Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
    message(STATUS "  Python3_LIBRARIES: ${Python3_LIBRARIES}")

    # Set Python3_FOUND to indicate we have Python
    set(Python3_FOUND TRUE)

    # Create the imported targets manually
    if(Python3_LIBRARIES AND NOT Python3_LIBRARIES STREQUAL "")
        add_library(Python3::Python SHARED IMPORTED)
        set_target_properties(Python3::Python PROPERTIES
            IMPORTED_LOCATION ${Python3_LIBRARIES}
            INTERFACE_INCLUDE_DIRECTORIES ${Python3_INCLUDE_DIRS}
        )
    else()
        # For modern Python builds, create a dummy target
        add_library(Python3::Python INTERFACE IMPORTED)
        set_target_properties(Python3::Python PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES ${Python3_INCLUDE_DIRS}
        )
    endif()

    add_library(Python3::Module INTERFACE IMPORTED)
    set_target_properties(Python3::Module PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES ${Python3_INCLUDE_DIRS}
    )

    # Set the _Python variable for pybind11
    set(_Python "Python3")

    # Define the python3_add_library command that pybind11 needs
    function(python3_add_library target_name)
        cmake_parse_arguments(PARSE_ARGV 1 ARG "STATIC;SHARED;MODULE" "" "")

        if(ARG_STATIC)
            set(lib_type STATIC)
        elseif(ARG_SHARED)
            set(lib_type SHARED)
        else()
            set(lib_type MODULE)
        endif()

        add_library(${target_name} ${lib_type} ${ARG_UNPARSED_ARGUMENTS})

        # Set properties for Python module
        if(lib_type STREQUAL "MODULE")
            set_target_properties(${target_name} PROPERTIES
                PREFIX ""
                SUFFIX ".so"
            )
        endif()

        # Link to Python and set include directories
        if(Python3_LIBRARIES AND NOT Python3_LIBRARIES STREQUAL "")
            target_link_libraries(${target_name} PRIVATE Python3::Python)
        endif()
        target_include_directories(${target_name} PRIVATE ${Python3_INCLUDE_DIRS})
    endfunction()
else()
    # Fall back to standard Python3 finding for local development
    find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
    set(_Python "Python3")
endif()

find_package(OpenMP REQUIRED)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Try to find dependencies using different approaches
# 1. First try Conan (if conan_toolchain.cmake exists)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/conan_toolchain.cmake")
    message(STATUS "Using Conan dependencies")
    include(${CMAKE_CURRENT_SOURCE_DIR}/conan_toolchain.cmake)
    find_package(PCL REQUIRED)
    find_package(Boost REQUIRED COMPONENTS thread)
    find_package(Eigen3 REQUIRED)
    set(EIGEN3_INCLUDE_DIR ${Eigen3_INCLUDE_DIRS})
    set(EIGEN3_LIBRARIES ${Eigen3_LIBRARIES})
# 2. Try standard system package finding (for Homebrew on macOS, system packages on Linux)
else()
    message(STATUS "Using system dependencies")
    find_package(PCL CONFIG REQUIRED)
    find_package(Boost COMPONENTS thread REQUIRED)
    find_package(Eigen3 REQUIRED)

    # Handle different Eigen3 variable names
    if(NOT DEFINED EIGEN3_INCLUDE_DIR)
        if(DEFINED Eigen3_INCLUDE_DIRS)
            set(EIGEN3_INCLUDE_DIR ${Eigen3_INCLUDE_DIRS})
        elseif(DEFINED EIGEN3_INCLUDE_DIRS)
            set(EIGEN3_INCLUDE_DIR ${EIGEN3_INCLUDE_DIRS})
        endif()
    endif()
endif()

include_directories(${EIGEN3_INCLUDE_DIR})
include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})

# Add pybind11 subdirectory AFTER Python is configured
add_subdirectory(dependencies/pybind11)

file(GLOB GPG_SRC
    src/gpg/*.cpp
)

include_directories(include)

pybind11_add_module(grasp_pose_generator src/py_generate_grasp_from_gpg.cpp ${GPG_SRC})

target_link_libraries(grasp_pose_generator PRIVATE ${Boost_LIBRARIES} ${PCL_LIBRARIES} ${EIGEN3_LIBRARIES} OpenMP::OpenMP_CXX Python3::Module)
