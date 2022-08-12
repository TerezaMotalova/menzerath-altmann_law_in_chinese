# FUNCTIONS FOR ALTERNATION OF PINYIN TRANSCRIPTION IN ORDER TO CORRESPOND TO IPA SOUNDS
# RULES BASED ON: Lin, Y. -H. (2007) The Sounds of Chinese, Cambridge University Press, Cambridge."


def replace_initials(a_word):
    """checks a word for three initials and replaces them by the character '$'"""

    initials = ['ch', 'sh', 'zh']

    for initial in initials:
        if initial in a_word:
            a_word = a_word.replace(initial, '$')

    return a_word


def replace_diphthongs(a_word):
    """checks a word for the presence of diphthongs and replaces them by the character '#'"""

    diphthongs = ['ai', 'ao', 'ei', 'ou']

    for diphthong in diphthongs:
        if diphthong in a_word:
            a_word = a_word.replace(diphthong, '#')

    return a_word


def replace_yue_yuan(a_word):
    """checks a word for syllables 'yue' and 'yuan' and replaces them by a modified syllable"""

    if 'yue' in a_word:
        a_word = a_word.replace('yue', 'ɥe')
    if 'yuan' in a_word:
        a_word = a_word.replace('yuan', 'ɥæn')

    return a_word


def replace_o(a_word):
    """checks a word for the syllables 'bo', 'fo', 'mo', 'po' and replaces 'o' by 'wo'"""
    # fou, mou, pou will not exist anymore after execution of previous function (replace_diphthongs)

    bofomopos = ['bo', 'fo', 'mo', 'po']

    for bofomopo in bofomopos:
        if bofomopo in a_word:
            a_word = a_word.replace(bofomopo, bofomopo[0] + 'wo')

    return a_word


def replace_ing(a_word):
    """checks a word for the presence of 'ing' and replaces 'i' by 'jə' (==inserts a schwa) except for 'ying'"""

    st_index = 0

    for _ in range(a_word.count('ing')):
        if a_word[(a_word.find('ing', st_index) - 1)] != 'y':
            a_word = a_word[:(a_word.find('ing', st_index))] + 'jə' + a_word[(a_word.find('ing', st_index) + 1):]
        st_index += 3

    return a_word


def replace_un(a_word):
    """checks a word for the presence of 'un' and replaces it by 'wən' except for 'jun', 'qun', 'xun' and 'yun'"""

    initials = 'jqxy'  # jun, qun, xun, yun
    st_index = 0

    for _ in range(a_word.count('un')):
        if a_word[(a_word.find('un', st_index) - 1)] not in initials:
            a_word = a_word[:(a_word.find('un', st_index))] + 'wə' + a_word[(a_word.find('un', st_index) + 1):]
        st_index += 2

    return a_word


def replace_nasal_ng(a_word):
    """checks a word for the presence of 'ng' and replaces it by the character 'ŋ'"""

    if 'ng' in a_word:
        a_word = a_word.replace('ng', 'ŋ')

    return a_word


def transform_into_sound(a_word):
    """calls all functions related to pinyin alternation and returns an altered word"""

    a_word = replace_initials(a_word)
    a_word = replace_diphthongs(a_word)
    a_word = replace_yue_yuan(a_word)
    a_word = replace_o(a_word)
    a_word = replace_ing(a_word)
    a_word = replace_un(a_word)
    a_word = replace_nasal_ng(a_word)

    return a_word
