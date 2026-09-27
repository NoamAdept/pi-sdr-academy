#include <iostream>
volatile int irq_flag = 0;
void pretend_isr() { irq_flag = 1; }
int main() {
  pretend_isr();
  std::cout << "irq=" << irq_flag << "\n";
}
