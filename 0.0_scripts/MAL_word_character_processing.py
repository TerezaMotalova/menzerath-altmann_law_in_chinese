# FUNCTIONS FOR PROCESSING METADATA ABOUT CHINESE CHARACTERS (using the source below)
# SOURCE #1: 汉字信息词典 (Dictionary of Chinese Character Information), BCC语料库 - 北京语言大学 (BCC Corpus – Beijing Language and Culture University)
# available at http://bcc.blcu.edu.cn/downloads/resources/%E6%B1%89%E5%AD%97%E4%BF%A1%E6%81%AF%E8%AF%8D%E5%85%B8.zip


from codecs import open


def process_stroke(a_stringy):
    """cleans a string containing the number of strokes"""

    a_stringy = a_stringy.split(':')

    return int(a_stringy[1].strip())


def process_pinyin(a_stringy):
    """cleans a string containing pinyin"""

    a_stringy = a_stringy.split(':')

    return a_stringy[1].strip()


def process_component(a_stringy):
    """cleans a string containing components"""

    a_stringy = a_stringy.split(':')
    component_list = a_stringy[1].split()

    return component_list


def create_blcu_dict(filename):
    """creates a dictionary of Chinese characters containing their metadata based on the source #1"""

    with open(filename, mode='r', encoding='gb18030') as text:
        list_to_process = [line for line in text]

    char_dict = {}
    item_n = 0
    while item_n < len(list_to_process):
        if list_to_process[item_n].startswith('#'):
            char_dict[list_to_process[item_n][1]] = {}
            char_dict[list_to_process[item_n][1]]['stroke_n'] = process_stroke(list_to_process[item_n + 1])
            char_dict[list_to_process[item_n][1]]['pinyin'] = process_pinyin(list_to_process[item_n + 2])
            char_dict[list_to_process[item_n][1]]['component'] = process_component(list_to_process[item_n + 3])
            char_dict[list_to_process[item_n][1]]['component_n'] = len(char_dict[list_to_process[item_n][1]]['component'])
            item_n += 4

    return char_dict


# FUNCTIONS FOR PROCESSING METADATA ABOUT CHINESE CHARACTERS (using the source below)
# SOURCE 2: CHISE - CHaracter Information Service Environment (2021), https://www.chise.org/index.en.html
# available at http://git.chise.org/gitweb/?p=chise/ids.git;a=blob;f=IDS-UCS-Basic.txt and
# Unicode (2021) Ideographic Description Characters: Range: 2FF0–2FFF
# available at: https://www.unicode.org/charts/PDF/U2FF0.pdf


def process_data(a_character, component_line):

    char_dictionary = {'blocks': [], 'component': [], 'component_n': 0, 'stroke_n': 0}

    blocks = ['⿰', '⿱', '⿲', '⿳', '⿴', '⿵', '⿶', '⿷', '⿸', '⿹', '⿺', '⿻']

    if len(component_line) == 0:
        # contains only @apperant note
        char_dictionary['component'] = a_character
        char_dictionary['component_n'] = 1
        return char_dictionary

    for grapheme in component_line:
        if grapheme == '&' or (grapheme not in blocks and not grapheme.isascii()):  # == basic Latin, i.e. U+0000 to U+007F
            char_dictionary['component'].append(grapheme)
        elif grapheme in blocks:
            char_dictionary['blocks'].append(grapheme)

    char_dictionary['component_n'] = len(char_dictionary['component'])

    return char_dictionary


def create_chise_dictionary(filename):
    """creates a dictionary of Chinese characters containing their metadata based on the source #2"""

    char_dictionary = {}

    with open(filename, mode='r', encoding='utf-8') as a_database:
        for line in a_database:
            item_list = line.split('\t')
            char_dictionary[item_list[1]] = process_data(item_list[1], item_list[2])

    return char_dictionary
