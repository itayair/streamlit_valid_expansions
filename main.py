import spacy
import csv
from spacy import displacy
import utils as ut
import valid_deps
from pybart.api import *



nlp = spacy.load("en_ud_model_sm")
used_for_examples = open('./csv/examples_used_for.csv', encoding="utf8")
output_file = './examples_used_for.txt'
csv_reader_used_for_examples = csv.reader(used_for_examples)
header = next(csv_reader_used_for_examples)
examples_to_visualize = []
counter = 0
sub_np_final_lst_collection = []
for row in csv_reader_used_for_examples:
    if counter > 200:
        break
    sentence_dep_graph = nlp(row[13])
    head_word_index = int(row[5])
    next_catch_word_index = int(row[7])
    noun_phrase, head_word_in_np_index, boundary_np_to_the_left = ut.get_np_boundary(head_word_index, sentence_dep_graph)
    if noun_phrase is None:
        continue
    if boundary_np_to_the_left > 20:
        continue
    examples_to_visualize.append(noun_phrase)
    all_valid_sub_np = valid_deps.get_all_valid_sub_np(noun_phrase[head_word_in_np_index], boundary_np_to_the_left, head_word_index)
    sub_np_final_lst = []
    sub_np_final_lst, root = ut.from_lst_to_sequence(sub_np_final_lst, all_valid_sub_np, [], None)
    new_format_all_valid_sub_np = ut.get_all_options(root)
    sub_np_final_lst_special = ut.from_lst_to_sequence_special(new_format_all_valid_sub_np, [])
    valid_expansion_results = set()
    for sub_np in sub_np_final_lst_special:
        valid_expansion_results.add(ut.list_of_nodes_to_span(sub_np, noun_phrase[head_word_in_np_index]))
    for sub_np in sub_np_final_lst:
        sub_np.sort(key=lambda x: x.i)
    sub_np_final_lst_collection.append(sub_np_final_lst)
    counter += 1
print(counter)
# for dep_type in valid_deps.dep_type_in_sequential:
#     print(dep_type)
ut.write_to_file_dict_counter(sub_np_final_lst_collection, output_file)
# doc = nlp("This is a sentence.")
# doc2 = nlp("My name is Itay Yair.")
displacy.serve(examples_to_visualize, style="dep", port=5000)

