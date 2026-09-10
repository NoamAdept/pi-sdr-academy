#ifndef LIST_H
#define LIST_H
#include <stdbool.h>
#include <stddef.h>
struct node { int value; struct node *next; };
bool list_push_front(struct node **head, int value);
struct node *list_find(struct node *head, int value);
size_t list_length(const struct node *head);
void list_destroy(struct node **head);
#endif
