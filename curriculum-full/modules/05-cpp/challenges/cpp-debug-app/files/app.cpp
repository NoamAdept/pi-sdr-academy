#include "app.hpp"
#include <algorithm>
void remove_negative(std::vector<int>& values){
    for(auto it=values.begin();it!=values.end();++it){
        if(*it<0) values.erase(it);
    }
}
double median(std::vector<int> values){
    remove_negative(values);
    if(values.empty()) return 0;
    std::sort(values.begin(),values.end());
    return values[values.size()/2];
}
