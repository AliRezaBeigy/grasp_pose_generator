cmake_minimum_required(VERSION 3.20)
project(grasp_pose_generator)
set(CMAKE_BUILD_TYPE Release)

find_package(OpenMP REQUIRED)
set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include_directories(${EIGEN3_INCLUDE_DIR})

find_package(PCL CONFIG REQUIRED)

find_package(Boost COMPONENTS thread REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
link_directories(${Boost_LIBRARY_DIRS})

set(PYBIND11_PYTHON_VERSION 3.11)
add_subdirectory(dependencies/pybind11)

file(GLOB GPG_SRC
    src/gpg/*.cpp
)

include_directories(include)

pybind11_add_module(grasp_pose_generator src/py_generate_grasp_from_gpg.cpp ${GPG_SRC})

target_link_libraries(grasp_pose_generator PRIVATE ${Boost_LIBRARIES} ${PCL_LIBRARIES} ${EIGEN3_LIBRARIES} OpenMP::OpenMP_CXX)