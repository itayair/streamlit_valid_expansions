class Node:
    def __init__(self, span):
        span.sort(key=lambda x: x.i)
        self.span = span
        self.children_to_the_left = []
        self.children_to_the_right = []

    def add_children(self, child):
        if child.span[-1].i < self.span[-1].i:
            self.children_to_the_left.append(child)
        else:
            self.children_to_the_right.append(child)
