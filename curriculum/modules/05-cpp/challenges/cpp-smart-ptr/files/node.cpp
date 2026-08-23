#include "node.hpp"
#include <utility>
Node::Node(std::string name):name_(std::move(name)){}
Node* Node::add_child(std::string name){ /* TODO */ return nullptr; }
Node* Node::find(const std::string& name){ /* TODO */ return nullptr; }
const Node* Node::find(const std::string& name) const{ /* TODO */ return nullptr; }
