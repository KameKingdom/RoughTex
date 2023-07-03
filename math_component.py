import re

functions = ["sin", "cos", "tan"]
functions_to_command = {
    "\=": "neq",
    "...": "cdots",
    "*": "times",
    "+": "plus",
    "-": "minus"

}

def fraction_converter(text):
    index = text.find("/")
    while index != -1:
        before = ""
        after = ""
        # 前方
        count = 0
        for i in range(index - 1, -1, -1):
            if text[i] in ")":
                count += 1
            elif text[i] in "(":
                count -= 1
            elif (text[i] in "+-/*=") and count == 0:
                break
            before = text[i] + before
        # 後方
        count = 0
        for i in range(index + 1, len(text)):
            if text[i] in "(":
                count += 1
            elif text[i] in ")":
                count -= 1
            elif (text[i] in "+-/*=") and count == 0:
                break
            after += text[i]

        text = text.replace(f"{before}/{after}", r'\frac{' + before + r'}{' + after + r'}')
        index = text.find("/")


    return text

def add_backslash(text, functions):
    for word in functions:
        replaced_text = f" \\{word} "
        text = text.replace(word, replaced_text)
    return text

def convert_math_to_latex(text):
    pattern = r'\[(.*?)\]'
    matches = re.findall(pattern, text, re.DOTALL)

    for match in matches:
        equation = match.replace('\n', '').replace(' ', '')
        if "/" in equation:  # / の検出
            equation = fraction_converter(equation)
        equation = add_backslash(equation, functions)

        for function, command in functions_to_command.items():
            equation = equation.replace(function, f"\\{command}")
        text = text.replace(match, equation)
    
    text = text.replace('[', '$').replace(']', '$')

    return text