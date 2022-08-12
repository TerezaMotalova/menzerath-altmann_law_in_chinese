# FUNCTIONS FOR CALCULATING CONSTRUCT LENGTHS, THEIR FREQUENCIES, CONSTITUENT LENGTHS + WEIGHTED VALUES


import pandas as pd


def calculate_xfy(input_file, output_file, construct_column, constituent_column):
    """calculates construct lengths, their frequencies and constituent lengths"""

    input_df = pd.read_csv(input_file, delimiter='\t')
    construct_dict = {}

    # filters out records where constituent lengths equal zero
    index_to_be_drop = input_df[input_df[constituent_column] == 0].index
    input_df.drop(index_to_be_drop, inplace=True)

    unique_constructs = input_df[construct_column].unique()
    construct_n = input_df.groupby(construct_column)[constituent_column].count()
    constituent_sum = input_df.groupby(construct_column)[constituent_column].sum()

    # filters out records where construct lengths equal zero
    for value in unique_constructs:
        if value != 0:
            construct_dict[value] = {}

    for value in construct_dict:
        construct_dict[value]['frequency'] = construct_n[value]
        construct_dict[value]['avg_constituent_len'] = constituent_sum[value]/construct_n[value]/value

    xfy_df = pd.DataFrame.from_dict(construct_dict, orient="index").sort_index()
    xfy_df.to_csv(path_or_buf=output_file, sep='\t', index_label=['construct'])


def calculate_values(xfy_list, index_1, index_2):
    """calculates required values .. too tired to write a comment here"""

    total_frequency = xfy_list[index_1]['frequency'] + xfy_list[index_2]['frequency']
    w_avg_construct_1 = xfy_list[index_1]['construct'] * xfy_list[index_1]['frequency']
    w_avg_construct_2 = xfy_list[index_2]['construct'] * xfy_list[index_2]['frequency']
    w_avg_construct = (w_avg_construct_1 + w_avg_construct_2) / total_frequency
    w_avg_constituent_1 = xfy_list[index_1]['avg_constituent_len'] * xfy_list[index_1]['frequency']
    w_avg_constituent_2 = xfy_list[index_2]['avg_constituent_len'] * xfy_list[index_2]['frequency']
    w_avg_constituent = (w_avg_constituent_1 + w_avg_constituent_2) / total_frequency

    return w_avg_construct, total_frequency, w_avg_constituent


def calculate_weighted_xfy(input_file, output_file, constant):
    """loads xfy data and calculates weighted average (if applicable), bottom-up"""

    xfy_df = pd.read_csv(input_file, delimiter='\t')
    xfy_list = xfy_df.to_dict('records')

    for index in range(len(xfy_list) - 1, -1, -1):
        if index > 0 and xfy_list[index]['frequency'] < constant:
            x, f, y = calculate_values(xfy_list, index, index - 1)
            xfy_list[index - 1]['construct'] = x
            xfy_list[index - 1]['frequency'] = f
            xfy_list[index - 1]['avg_constituent_len'] = y
            xfy_list.pop(index)
        elif index == 0 and xfy_list[index]['frequency'] < constant:
            x, f, y = calculate_values(xfy_list, index, index + 1)
            xfy_list[index + 1]['construct'] = x
            xfy_list[index + 1]['frequency'] = f
            xfy_list[index + 1]['avg_constituent_len'] = y
            xfy_list.pop(index)

    with open(output_file, mode='w', encoding='utf-8') as output:
        print('construct' + '\t' + 'frequency' + '\t' + 'avg_constituent_len', file=output)  # header

        for xfy_dict in xfy_list:
            print(str(xfy_dict['construct']) + '\t' + str(xfy_dict['frequency']) + '\t' + str(xfy_dict['avg_constituent_len']), file=output)
