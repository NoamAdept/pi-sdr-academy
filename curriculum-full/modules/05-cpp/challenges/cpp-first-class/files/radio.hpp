#pragma once
#include <string>
class Radio {
public:
    Radio(std::string name, long frequency);
    bool tune(long frequency);
    const std::string& name() const;
    long frequency() const;
private:
    std::string name_;
    long frequency_;
};
