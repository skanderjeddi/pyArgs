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

def parse_args(args, positionals, optionals = [], optionals_valueless = [], script_name = 'script.py', from_sys_argv = False):
    if from_sys_argv:
        args = args[1:]
    args_map = {}
    current_key, current_value = None, None
    found_positionals = 0
    seek_value = False
    for i in range(0, len(args)):
        current_obj = args[i]
        if seek_value:
            if current_obj.startswith('--') or (current_obj.startswith('-') and len(current_obj) == 2):
                current_key = current_obj
                if current_key.startswith('--') and len(current_key) <= 3:
                    print(f'Malformed argument {current_key}, -- should only be used for long form optionals')
                    exit(-1)
                if current_key.startswith('-') and len(current_key) > 2:
                    print(f'Malformed argument {current_key}, - should only be used for short form optionals')
                    exit(-1)
                if current_key.startswith('-') and len(current_key) == 2:
                    while current_key.startswith('-'):
                        current_key = current_key[1:]
                    for o in optionals:
                        if current_key in o:
                            current_key = o[0]
                    for o in optionals_valueless:
                        if current_key in o:
                            current_key = o[0]
                args_map[current_key] = 'VALUELESS'
                current_value = None
                seek_value = True
                if i == len(args) - 1:
                    args_map[current_key] = 'VALUELESS'
            else:
                current_value = current_obj
                while current_key.startswith('-'):
                    current_key = current_key[1:]
                args_map[current_key] = current_value
                current_key, current_value = None, None
                seek_value = False
        elif current_obj.startswith('--') or (current_obj.startswith('-') and len(current_obj) == 2):
            current_key = current_obj
            if current_key.startswith('--') and len(current_key) <= 3:
                print(f'Malformed argument {current_key}, -- should only be used for long form optionals')
                exit(-1)
            if current_key.startswith('-') and len(current_key) > 2:
                print(f'Malformed argument {current_key}, - should only be used for short form optionals')
                exit(-1)
            if current_key.startswith('-') and len(current_key) == 2:
                while current_key.startswith('-'):
                    current_key = current_key[1:]
                for o in optionals:
                    if current_key in o:
                        current_key = o[0]
                for o in optionals_valueless:
                    if current_key in o:
                        current_key = o[0]
            seek_value = True
            in_ov = False
            for ov in optionals_valueless:
                if current_key in ov:
                    in_ov = True
            if i == len(args) - 1 or in_ov:
                args_map[current_key] = 'VALUELESS'
                seek_value = False
        else:
            try:
                args_map[positionals[found_positionals]] = current_obj
            except IndexError:
                print(f'Too many positionals found, malformed arguments, needed {found_positionals}, found {found_positionals + 1}')
                for k in args_map:
                    print(f'{k}:', args_map[k], ('(p)' if k in positionals else '(o)'))
                print(f'Extra positional: {current_obj}')
                args_line = ''
                for p in positionals:
                    args_line += f'<{p}> '
                for o in optionals:
                    args_line += f'[--{o[0]}/-{o[1]} value] '
                for o in optionals_valueless:
                    args_line += f'[--{o[0]}/-{o[1]}] '
                print(f'Usage: python {script_name} {args_line}')
                exit(-1)
            found_positionals += 1
    if found_positionals != len(positionals):
        found_positionals_list = [ p for p in positionals if p in args_map ]
        print(f'Not enough positionals found, malformed arguments, needed {positionals}, found {found_positionals_list}')
        for k in args_map:
            print(f'{k}:', args_map[k], ('(p)' if k in positionals else '(o)'))
        args_line = ''
        for p in positionals:
            args_line += f'<{p}> '
        for o in optionals:
            args_line += f'[--{o[0]}/-{o[1]} value] '
        for o in optionals_valueless:
            args_line += f'[--{o[0]}/-{o[1]}] '
        print(f'Usage: python {script_name} {args_line}')
        exit(-1)
    unwanted = []
    for k in args_map:
        in_o, in_ov = False, False
        for o in optionals:
            if k in o:
                in_o = True
        for ov in optionals_valueless:
            if k in ov:
                in_ov = True
        if k not in positionals and not in_o and not in_ov:
            unwanted.append(k)
    if len(unwanted) > 0:
        print(f'Unwanted arguments found: {unwanted}')
        args_line = ''
        for p in positionals:
            args_line += f'<{p}> '
        for o in optionals:
            args_line += f'[--{o[0]}/-{o[1]} value] '
        for o in optionals_valueless:
            args_line += f'[--{o[0]}/-{o[1]}] '
        print(f'Usage: python {script_name} {args_line}')
        exit(-1)
    return args_map
