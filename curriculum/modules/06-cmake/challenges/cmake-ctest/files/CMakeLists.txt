cmake_minimum_required(VERSION 3.16)
project(ctest_lab LANGUAGES CXX)
add_library(calc calc.cpp)
add_executable(calc_tests tests.cpp)
target_link_libraries(calc_tests PRIVATE calc)
# TODO: enable testing and register calc_tests as a test named addition
