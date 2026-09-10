cmake_minimum_required(VERSION 3.16)
project(dep_debug LANGUAGES CXX)
add_library(signal signal.cpp)
target_include_directories(signal PUBLIC include)
add_executable(dep_app main.cpp)
target_link_libraries(dep_app PRIVATE signals)
# TODO: repair source path, include path, and linked target name
