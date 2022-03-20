attr_of_node = ['det', 'neg', 'auxpass', 'aux', 'auxpass']


class Node:
    def __init__(self, span):
        span.sort(key=lambda x: x.i)
        self.span = span
        self.attr_head = []
        self.basic_span = ""
        self.children_to_the_left = []
        self.children_to_the_right = []
        # self.kind = kind
        self.initialize_attr_and_basic_span()

    def initialize_attr_and_basic_span(self):
        basic_lst = []
        for token in self.span:
            if token.dep_ in attr_of_node:
                self.attr_head.append(token)
            else:
                basic_lst.append(token)
        idx = 0
        for token in basic_lst:
            if idx != 0:
                self.basic_span += " "
            self.basic_span += token.text
            idx += 1

    def add_children(self, child):
        if child.span[-1].i < self.span[-1].i:
            self.children_to_the_left.append(child)
        else:
            self.children_to_the_right.append(child)


class head_phrase:
    def __init__(self, name):
        self.head_phrase_name = name
        self.head_phrase_child_dict = {}
        self.sentence_and_node_to_head_phrase_child_dict = {}
        self.head__node_lst = []
        # self.nodes_lst = []
        # self.sentence_to_child = {}
        # self.kind = kind

    def add_new_node(self, node, sentence):
        self.head__node_lst.append((node, sentence))
        for child in node.children_to_the_right:
            self.head_phrase_child_dict[child.basic_span] = self.head_phrase_child_dict.get(child.basic_span, [])
            self.head_phrase_child_dict[child.basic_span].append(child)
            self.sentence_and_node_to_head_phrase_child_dict[
                (sentence, node)] = self.sentence_and_node_to_head_phrase_child_dict.get((sentence, node), [])
            self.sentence_and_node_to_head_phrase_child_dict[(sentence, node)].append(child)
