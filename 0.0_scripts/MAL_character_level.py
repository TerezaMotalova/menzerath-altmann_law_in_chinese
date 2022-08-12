# CHARACTER LEVEL
# Triplet of character-component-stroke


import pandas as pd
import MAL_word_character_processing as CH
import MAL_xfy as xfy


# AUXILIARY FUNCTIONS
def count_all_components(a_character, metadata_dict):
    """recursively counts all components in a character, i.e. until each component cannot be decomposed further,
       ==maximal decomposition"""

    component_n = 0

    for component in metadata_dict[a_character]['component']:
        if component in metadata_dict and metadata_dict[component]['component_n'] > 1:
            component_n += count_all_components(component, metadata_dict)
        else:
            component_n += 1

    return component_n


def find_component_stroke_data(a_character, metadata_dict_blcu, metadata_dict_chise):
    """returns the number of component(s) and stroke(s) of a given character (if findable)"""

    component_n = 0
    stroke_n = 0

    # if-block for BLCU source
    if a_character in metadata_dict_blcu:
        # component_n = count_all_components(a_character, metadata_dict_blcu)  # maximal decomposition
        component_n = metadata_dict_blcu[a_character]['component_n']
        stroke_n = metadata_dict_blcu[a_character]['stroke_n']

    # # if-block for CHISE source (while using BLCU source for the number of strokes)
    # if a_character in metadata_dict_chise and a_character in metadata_dict_blcu:
    #     # component_n = count_all_components(a_character, metadata_dict_chise)  # maximal decomposition
    #     component_n = metadata_dict_chise[a_character]['component_n']
    #     stroke_n = metadata_dict_blcu[a_character]['stroke_n']

    return component_n, stroke_n


def process_types(input_file, output_file, column_name):
    """loads quantified data of character tokens, drops duplicates, saves quantified data for character types"""

    token_df = pd.read_csv(input_file, delimiter='\t')
    type_df = token_df.drop_duplicates(subset=[column_name])
    type_df.to_csv(path_or_buf=output_file, sep='\t', index=False)


# CORE FUNCTION
def character_component_stroke(a_treebank, weighted_avg_limit):
    """quantifies a UD treebank on the character level while taking tokens and types into account,
       creates files with data quantification, xfy for original and weighted values,
       x==character length in the number of components, f(x)==its frequency, y==component length in the number of stroke"""

    character_metadata_blcu = CH.create_dict('hzinfo.txt')
    character_metadata_chise = CH.create_ids_dictionary('IDS-UCS-Basic.txt')

    # tokens
    with open('character_component_stroke_token.txt', mode='w', encoding='utf-8') as output:
        print('sent_id' + '\t' + 'character' + '\t' + 'component_n' + '\t' + 'stroke_n', file=output)  # header

        for sentence in a_treebank.sentence_list:
            for word in sentence.word_list:
                if word.deprel != 'punct':
                    for character in word.form:
                        if not character.isascii():  # ascii letters U+0000-U+007F -> basic latin
                            component_n, stroke_n = find_component_stroke_data(character, character_metadata_blcu, character_metadata_chise)
                            print(sentence.id + '\t' + character + '\t' + str(component_n) + '\t' + str(stroke_n), file=output)

    xfy.calculate_xfy('character_component_stroke_token.txt', 'character_component_stroke_token_xfy.txt', 'component_n', 'stroke_n')
    xfy.calculate_weighted_xfy('character_component_stroke_token_xfy.txt', 'character_component_stroke_token_xfy_weighted.txt', weighted_avg_limit)

    # types
    process_types('character_component_stroke_token.txt', 'character_component_stroke_type.txt', 'character')
    xfy.calculate_xfy('character_component_stroke_type.txt', 'character_component_stroke_type_xfy.txt', 'component_n', 'stroke_n')
    xfy.calculate_weighted_xfy('character_component_stroke_type_xfy.txt', 'character_component_stroke_type_xfy_weighted.txt', weighted_avg_limit)
