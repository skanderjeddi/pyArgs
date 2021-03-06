'''
MIT License
Copyright (c) 2021 Skander Jeddi
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys


def parse_args(args, positionals, optionals = [], optionals_valueless = [], script_name = 'script.py', from_sys_argv = False):
    if from_sys_argv:
        args = args[1:]
    args_map = {}
    args_map['positionals'] = {}
    args_map['optionals'] = {}
    args_map['optionals_valueless'] = []
    current_key, current_value = None, None
    found_positionals = 0
    seek_value = False
    for i in range(len(args)):
        current_obj = args[i]
        if seek_value:
            if is_param_name(current_obj):
                current_key = current_obj
                print(current_key)
                validate_key_format(current_key)
                current_key = extract_key(current_key)
                if len(current_key) <= 2:
                    current_key = retrieve_long_form(current_key, optionals, optionals_valueless)
                if not is_param_valid(current_key, positionals, optionals, optionals_valueless):
                    print(f'Malformed command, found extra argument {current_obj}')
                    print_usage(positionals, optionals, optionals_valueless, script_name)
                args_map['optionals_valueless'].append(current_key)
                # args_map[current_key] = 'VALUELESS'
                current_value = None
                seek_value = True
                if i == len(args) - 1:
                    args_map['optionals_valueless'].append(current_key)
                    # args_map[current_key] = 'VALUELESS'
            else:
                current_value = current_obj
                current_key = extract_key(current_key)
                args_map['optionals'][current_key] = current_value
                # args_map[current_key] = current_value
                current_key, current_value = None, None
                seek_value = False
        elif is_param_name(current_obj):
            current_key = current_obj
            validate_key_format(current_key)
            current_key = extract_key(current_key)
            if len(current_key) <= 2:
                current_key = retrieve_long_form(current_key, optionals, optionals_valueless)
            if not is_param_valid(current_key, positionals, optionals, optionals_valueless):
                print(f'Malformed command, found extra argument {current_obj}')
                print_usage(positionals, optionals, optionals_valueless, script_name)
            seek_value = True
            is_optional_param = False
            for optional_pair in optionals_valueless:
                if current_key in optional_pair:
                    is_optional_param = True
            if i == len(args) - 1 or is_optional_param:
                args_map['optionals_valueless'].append(current_key)
                # args_map[current_key] = 'VALUELESS'
                seek_value = False
        else:
            try:
                args_map['positionals'][positionals[found_positionals]] = current_obj
                # args_map[positionals[found_positionals]] = current_obj
            except IndexError:
                print(f'Too many positionals found, needed {found_positionals}, found {found_positionals + 1}')
                print_current_args_map(args_map, positionals)
                print(f'Extra positional: {current_obj}')
                print_usage(positionals, optionals, optionals_valueless, script_name)
            found_positionals += 1
    if found_positionals != len(positionals):
        found_positionals_list = [p for p in positionals if p in args_map]
        print(f'Not enough positionals found, needed {positionals}, found {found_positionals_list}')
        print_current_args_map(args_map, positionals)
        print_usage(positionals, optionals, optionals_valueless, script_name)
    unwanted = []
    for category in args_map:
        for param in args_map[category]:
            if not is_param_valid(param, positionals, optionals, optionals_valueless):
                unwanted.append(param)
    if len(unwanted) > 0:
        print(f'Unwanted arguments found: {unwanted}')
        print_usage(positionals, optionals, optionals_valueless, script_name)
    return args_map


def is_param_name(key):
    return key.startswith('--') or (key.startswith('-') and len(key) <= 3)


def validate_key_format(key, should_exit = True):
    if key.startswith('-') and key[1:2] != '-' and len(key) > 3:
        print(f'Malformed argument {key}, - should only be used for short form optionals')
        if should_exit:
            exit(1)
    if key.startswith('--') and len(key) <= 3:
        print(f'Malformed argument {key}, -- should only be used for long form optionals')
        if should_exit:
            exit(1)


def extract_key(key):
    if key is None:
        print('Malformed command', key)
        exit(1)
    while key.startswith('-'):
        key = key[1:]
    return key


def is_param_valid(param, positionals, optionals, optionals_valueless):
    if param is None:
        return False
    valid = False
    for optional_pair in optionals:
        if param[0] in optional_pair or param in optional_pair:
            valid = True
    for optional_pair in optionals_valueless:
        if param[0] in optional_pair or param in optional_pair:
            valid = True
    return valid or (param[0] in positionals) or (param in positionals)


def retrieve_long_form(key, optionals, optionals_valueless):
    for optional_pair in optionals:
        if key in optional_pair:
            return optional_pair[0]
    for optional_pair in optionals_valueless:
        if key in optional_pair:
            return optional_pair[0]


def print_current_args_map(args_map, positionals):
    for category in args_map:
        for key in args_map[category]:
            if key in positionals:
                print(f'{key}: (positional)')
            else:
                print(f'{key}: (optional)')
    

def print_usage(positionals, optionals, optionals_valueless, script_name = 'script.py', should_exit = True):
    args_line = ''
    for optional in optionals:
        args_line += f'[--{optional[0]}/-{optional[1]} value] '
    for optional in optionals_valueless:
        args_line += f'[--{optional[0]}/-{optional[1]}] '
    for positional in positionals:
        args_line += f'<{positional}> '
    print(f'Usage: python {script_name} {args_line}')
    if should_exit:
        exit(1)


def main():
    args_map = parse_args(sys.argv[1:], ['path', 'mode', 'key'], [('output', 'o')], [ ('recursive', 'R'), ('verbose', 'v'), ('remove', 'r0')], script_name = 'pyArgs.py')
    positionals, optionals, optionals_valueless = args_map['positionals'], args_map['optionals'], args_map['optionals_valueless']
    print(positionals['path'], positionals['mode'], positionals['key'])
    print(optionals['output'])
    print(optionals_valueless)


if __name__ == "__main__":
    main()
