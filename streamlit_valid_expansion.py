import streamlit as st
import spacy
from spacy import displacy
import pandas as pd
from PIL import Image
import utils as ut
import valid_deps
import pip

SPACY_MODEL_NAMES = ["en_core_sci_sm", "en_core_sci_md", "en_core_sci_lg"]
NER_MODEL_NAMES = ["en_ner_craft_md", "en_ner_jnlpba_md", "en_ner_bc5cdr_md", "en_ner_bionlp13cg_md"]
DEFAULT_TEXT = "Used in select mask models , this new material improves upon silicone used for three decades in mask skirts with improved light transmission and much greater resistance to discoloration."
HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
st.set_page_config(layout="wide")


# def install(package):
#     if hasattr(pip, 'main'):
#         pip.main(['install', package])
#     else:
#         pip._internal.main(['install', package])
#
# # Example
# if __name__ == '__main__':
#     install("https://storage.googleapis.com/en_ud_model/en_ud_model_sm-2.0.0.tar.gz")
@st.cache(allow_output_mutation=True)
def load_model():
    nlp = spacy.load("en_ud_model_sm")
    return nlp


noun_tags_lst = ['NN', 'NNS', 'WP', 'PRP', 'NNP', 'NNPS']


# @st.cache(allow_output_mutation=True)
def get_noun_in_sentence(sentence_dep_graph):
    noun_lst = []
    for token in sentence_dep_graph:
        if token.tag_ in noun_tags_lst:
            noun_lst.append(token)
    return noun_lst


# @st.cache(allow_output_mutation=True)
def process_text(head_word_index, text, nlp):
    # nlp = spacy.load("en_ud_model_sm")
    sent_dep_graph = nlp(text)
    noun_phrase, head_word_in_np_index, boundary_np_to_the_left = ut.get_np_boundary(head_word_index,
                                                                                     sent_dep_graph)
    all_valid_sub_np = valid_deps.get_all_valid_sub_np(noun_phrase[head_word_in_np_index], boundary_np_to_the_left, head_word_index)
    sub_np_final_lst = []
    sub_np_final_lst, root = ut.from_lst_to_sequence(sub_np_final_lst, all_valid_sub_np, [], None)
    for sub_np in sub_np_final_lst:
        sub_np.sort(key=lambda x: x.i)
    valid_expansion_results = set()
    for tokens in sub_np_final_lst:
        span = ut.get_tokens_as_span(tokens)
        valid_expansion_results.add(span)
    if noun_phrase[0].tag_ in ['IN', 'TO']:
        noun_phrase = noun_phrase[1:]
    return list(valid_expansion_results), noun_phrase, root


key_for_special_item = 0



st.title("Valid expansions in Noun phrase")

st.header("Enter a sentence:")
text = st.text_area("", DEFAULT_TEXT)
nlp = load_model()
sentence_dep_graph = nlp(text)
noun_lst = get_noun_in_sentence(sentence_dep_graph)
attrs = ["valid expansion"]

st.header("Choose Noun to get all the valid expansions:")
buttons = []
word_to_noun_token = {}
idx = 1
button_to_noun_token = {}
c = st.columns(int(len(noun_lst) / 5) + 1)
if "sentence" not in st.session_state:
    st.session_state.sentence = text
if "options" not in st.session_state:
    st.session_state.options = []

if st.session_state.sentence != text:
    st.legacy_caching.clear_cache()
    st.session_state.sentence = text

for noun in noun_lst:
    noun_button = str(idx) + ": " + noun.text
    buttons.append((c[int((idx - 1) / 5)].button(noun_button), noun))
    word_to_noun_token[noun_button] = noun
    idx += 1
noun_phrase = None
button_to_expand = []
root_node = None
for button, noun in buttons:
    if button:
        st.session_state.noun_to_expand = noun
        st.session_state.expanded_nodes = None
        st.session_state.has_root = True
if "noun_to_expand" in st.session_state:
    st.header(st.session_state.noun_to_expand.text)
    valid_expansion_results, noun_phrase, root = process_text(st.session_state.noun_to_expand.i, text, nlp)
    df = pd.DataFrame(valid_expansion_results, columns=attrs)
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.dataframe(df)
    root_node = root

if ("expanded_nodes" not in st.session_state or st.session_state.expanded_nodes is None) and root_node:
    if "has_root" in st.session_state:
        if st.session_state.has_root:
            st.session_state.expanded_nodes = [root_node]
if "expanded_nodes" in st.session_state and st.session_state.expanded_nodes is not None:
    format_to_write_sent = []
    c_to_expanded_noun = st.container()
    expanded_noun = []
    st.session_state.expanded_nodes.sort(key=lambda x: x.span[-1].i)
    for item in st.session_state.expanded_nodes:
        if item.children_to_the_left == [] and item.children_to_the_right == []:
            expanded_noun.extend(item.span)
            continue
        temp = []
        temp.append(("current",item))
        # format_to_write_sent.append()
        if item.children_to_the_left:
            temp.append(("left", item.children_to_the_left))
            # format_to_write_sent.append()
        if item.children_to_the_right:
            temp.append(("right", item.children_to_the_right))
            # format_to_write_sent.append()
        format_to_write_sent.append(temp)
    if format_to_write_sent:
        st.subheader("Select expansions to the right or to the left for specific span")
        c_expansion = st.columns(len(format_to_write_sent))
    idx = 0
    buttons_to_expand_noun = []
    for items in format_to_write_sent:
        for kind, item in items:
            if kind == "left":
                buttons_to_expand_noun.append(
                    (c_expansion[idx].button(kind, key=str(key_for_special_item)), item))
                key_for_special_item += 1
            if kind == "right":
                buttons_to_expand_noun.append(
                    (c_expansion[idx].button(kind, key=str(key_for_special_item)), item))
                key_for_special_item += 1
            if kind == "current":
                span = ut.get_tokens_as_span_simple(item.span)
                c_expansion[idx].write(span)
                expanded_noun.extend(item.span)
        idx += 1
    # create_button_to_expand(buttons_to_expand_noun)
    c_to_expanded_noun.header("Expanded noun manually")
    expanded_noun.sort(key=lambda x: x.i)
    col1, col2, col3 = c_to_expanded_noun.columns(3)
    col2.subheader(ut.get_tokens_as_span_simple(expanded_noun))
    # st.markdown("<h1 style='text-align: center; color: red;'>Some title</h1>", unsafe_allow_html=True)
    buttons_to_expand = []
    expansion_dict_for_multiselect = {}
    expansion_lst_for_multiselect = []
    for button_to_expand_noun, items in buttons_to_expand_noun:
        if button_to_expand_noun:
            for node in items:
                # placeholder = st.empty()
                # buttons_to_expand.append((st.button(ut.get_tokens_as_span_simple(node.span), key=str(key_for_special_item)), node, items))
                expansion_dict_for_multiselect[ut.get_tokens_as_span_simple(node.span)] = (node, items)
                expansion_lst_for_multiselect.append(ut.get_tokens_as_span_simple(node.span))
                key_for_special_item += 1
            st.session_state.options = expansion_lst_for_multiselect
            st.session_state.expansion_dict_for_multiselect = expansion_dict_for_multiselect
    # options = []
    # if expansion_lst_for_multiselect:
    if format_to_write_sent:
        options = st.multiselect(
            'What are your expansions',
            st.session_state.options,
            st.session_state.options)
        if options:
            st.session_state.options = options
        if st.button("Submit your expansions"):
            for option_to_expand in st.session_state.options:
                st.write(option_to_expand)
                st.session_state.expanded_nodes.append(st.session_state.expansion_dict_for_multiselect[option_to_expand][0])
                st.session_state.expansion_dict_for_multiselect[option_to_expand][1].remove(st.session_state.expansion_dict_for_multiselect[option_to_expand][0])
                st.session_state.options = []
            st.experimental_rerun()

st.header("Dependency Parse & Part-of-speech tags")
if st.button("Show Parser and Tagger"):
    st.header("Dependency Parse")
    collapse = st.checkbox("Collapse")
    options = {
        "collapse_punct": collapse
    }
    # docs = [span.as_doc() for span in doc.sents] if split_sents else [doc]
    # for sent in docs:
    doc = noun_phrase
    html = displacy.render(doc, options=options)
    # Double newlines seem to mess with the rendering
    html = html.replace("\n\n", "\n")
    st.markdown(f"> {doc.text}")
    st.write(HTML_WRAPPER.format(html), unsafe_allow_html=True)

