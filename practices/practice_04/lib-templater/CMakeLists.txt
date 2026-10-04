cmake_minimum_required(VERSION 3.20)

project(
    __PROJECT_NAME__
    VERSION 0.1.0
    LANGUAGES CXX
)

# CXX Standart setters
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# CMake setters
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# CMake build flags
option(BUILD_TESTS "Build tests" ON)
option(BUILD_BIN "Build binary targets" ON)
option(ENABLE_INSTALL "Enable install rules" ON)

# Enable dependence (link outsider libs)
include(cmake/dependencies.cmake)

add_subdirectory(src)

if(BUILD_BIN)
    add_subdirectory(bin)
endif()

if(BUILD_TESTS)
    include(CTest)
    enable_testing()
    add_subdirectory(tests)
endif()

if(ENABLE_INSTALL)
    include(cmake/install-rules.cmake)
endif()
