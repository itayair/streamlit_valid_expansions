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


def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

# Example
if __name__ == '__main__':
    install("https://storage.googleapis.com/en_ud_model/en_ud_model_sm-2.0.0.tar.gz")

def load_model():
    nlp = spacy.load("en_ud_model_sm")
    return nlp

noun_tags_lst = ['NN', 'NNS', 'WP', 'PRP', 'NNP', 'NNPS']


def get_noun_in_sentence(sentence_dep_graph):
    noun_lst = []
    for token in sentence_dep_graph:
        if token.tag_ in noun_tags_lst:
            noun_lst.append(token)
    return noun_lst


@st.cache(allow_output_mutation=True)
def process_text(head_word_index, text):
    # nlp = spacy.load("en_ud_model_sm")
    nlp_2 = load_model()
    sent_dep_graph = nlp_2(text)
    noun_phrase, head_word_in_np_index, boundary_np_to_the_left = ut.get_np_boundary(head_word_index,
                                                                                     sent_dep_graph)
    all_valid_sub_np = valid_deps.get_all_valid_sub_np(noun_phrase[head_word_in_np_index], boundary_np_to_the_left)
    sub_np_final_lst = []
    sub_np_final_lst = ut.from_lst_to_sequence(sub_np_final_lst, all_valid_sub_np, [])
    for sub_np in sub_np_final_lst:
        sub_np.sort(key=lambda x: x.i)
    valid_expansion_results = set()
    for tokens in sub_np_final_lst:
        span = ut.get_tokens_as_span(tokens)
        valid_expansion_results.add(span)
    return list(valid_expansion_results)



st.title("All Valid expansions in Noun phrase")


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
for noun in noun_lst:
    noun_button = str(idx) + ": " + noun.text
    buttons.append((c[int((idx - 1) / 5)].button(noun_button), noun))
    word_to_noun_token[noun_button] = noun
    idx += 1


for button, noun in buttons:
    if button:
        st.header(noun.text)
        valid_expansion_results = process_text(noun.i, text)
        df = pd.DataFrame(valid_expansion_results, columns=attrs)
        dfStyler = df.style.set_properties(**{'text-align': 'left'})
        dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
        st.dataframe(df)



