# FUNCTIONS FOR CALCULATING PARAMETERS OF MAL'S MODELS AND COEFFICIENT OF DETERMINATION
# WHILE USING NLREG -> Sherrod, P. H. (2005) NLREG Version 6.3 (Advanced)


from subprocess import run


def load_xfy_file(input_file):
    """loads xfy data and creates their list,
       x==construct lengths, f(x)==their frequencies, y==constituent lengths"""

    data_list = []

    with open(input_file, mode='r', encoding='utf-8') as input:
        for line in input:
            data_list.append(line.split('\t'))

    return data_list


def prepare_program_file(input_file, truncated_program_file, complete_program_file):
    """creates two program files to be run by NLREG, one for truncated formula, one for complete formula"""

    # load variables including header!
    data_list = load_xfy_file(input_file)

    variable = 'Variables x,y;'
    parameter_truncated = 'Parameter b;'  # parameter a == an empirically obtained value
    parameter_complete = 'Parameters a,b,c;'
    # xfy data file contains a header, hence, index starts with 1 to exclude the header
    constant = 'Constant firstConstr = ' + data_list[1][2].strip() + ';'
    function_truncated = 'Function y = firstConstr * (x^b);'
    function_complete = 'function y = a * x^b * exp(-c * x);'
    data = 'data;'

    # truncated model
    with open(truncated_program_file, mode='w', encoding='utf-8') as output:
        print(variable, file=output)
        print(parameter_truncated, file=output)
        print(constant, file=output)
        print(function_truncated, file=output)
        print(data, file=output)
        # xfy data file contains a header, hence, index starts with 1 to exclude the header
        for index in range(1, len(data_list)):
            print(data_list[index][0] + '\t' + data_list[index][2], end='', file=output)

    # complete model
    with open(complete_program_file, mode='w', encoding='utf-8') as output:
        print(variable, file=output)
        print(parameter_complete, file=output)
        print(function_complete, file=output)
        print(data, file=output)
        # xfy data file contains a header, hence, index starts with 1 to exclude the header
        for index in range(1, len(data_list)):
            print(data_list[index][0] + '\t' + data_list[index][2], end='', file=output)


def run_nlreg(input_file):
    """creates names for nlr and lst files and run NLREG using cmd line"""

    input_file_split = input_file.split('.')

    truncated_program_file = input_file_split[0] + "_truncated.nlr"
    complete_program_file = input_file_split[0] + "_complete.nlr"

    prepare_program_file(input_file, truncated_program_file, complete_program_file)

    # for an output of truncated model
    nlreg_truncated_output = truncated_program_file.split('.')[0] + '_nlreg.lst'
    # for an output of complete model
    nlreg_complete_output = complete_program_file.split('.')[0] + '_nlreg.lst'

    run(['NLREGCA', truncated_program_file, '/list', nlreg_truncated_output])
    run(['NLREGCA', complete_program_file, '/list', nlreg_complete_output])
