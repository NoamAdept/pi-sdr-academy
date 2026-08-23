#pragma once
#include <memory>
#include <string>
#include <vector>
class Node {
public:
    explicit Node(std::string name);
    Node* add_child(std::string name);
    Node* find(const std::string& name);
    const Node* find(const std::string& name) const;
    const std::string& name() const { return name_; }
    std::size_t child_count() const { return children_.size(); }
private:
    std::string name_;
    std::vector<std::unique_ptr<Node>> children_;
};
