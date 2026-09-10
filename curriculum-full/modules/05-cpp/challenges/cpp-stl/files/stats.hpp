#pragma once
#include <cstddef>
#include <map>
#include <vector>
std::vector<int> sorted_unique(const std::vector<int>& values);
double mean(const std::vector<int>& values);
std::map<int,std::size_t> histogram(const std::vector<int>& values);
