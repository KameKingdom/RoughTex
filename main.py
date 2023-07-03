import re
import pyperclip
import subprocess
import os
from math_component import convert_math_to_latex

def transform_latex(text):
    # text = text.replace(" ","")
    return text


def is_error_exists(text):
    necessary_list = ["main"]
    for item in necessary_list:
        if f"<{item}>" not in text or f"</{item}>" not in text:
            print(f"Error: Necessary element '{item}' not found.")
            return True
    return False


def simple_converter(text, element):
    text_pattern = fr"<{element}>(.*?)</{element}>"
    if element in "leftrightcenter":
        element = f"{element}line"
    converted_text = re.sub(text_pattern, fr"\\{element}{{\1}}\n", text)
    return converted_text

def replace_fractions(expr):
    # 分数を置換するための正規表現パターン
    pattern = r"([a-zA-Z0-9+*-]+)/([a-zA-Z0-9+*-]+)"
    repl = r"\\frac{\1}{\2}"
    result = re.sub(pattern, repl, expr)
    return result

def begin_end_converter(text, element, content):
    converted_text = text.replace(f"</{element}>", "\\end{" + content + "}")
    converted_text = converted_text.replace(f"<{element}>", "\\begin{" + content + "}")
    return converted_text


def section_converter(text):
    pattern = r"(?s)<section>\s*<headline>(.*?)</headline>\s*(.*?)\s*</section>"
    converted_text = re.sub(pattern, r"\\section{\g<1>}\n\g<2>", text)
    return converted_text


def convert_to_latex(text):
    setting_list = ["\\documentclass[titlepage]{jsarticle}", "\\usepackage{graphicx}", ""]
    for setting in reversed(setting_list):
        text = f"{setting}\n{text}"

    index_list = ["title", "author", "date", "left", "center", "right"]
    for index in index_list:
        text = simple_converter(text, index)

    # <main> と </main> の間の部分を抽出
    pattern = r"<main>(.*?)</main>"
    matches = re.search(pattern, text, re.DOTALL)
    if matches:
        text = text.replace("<main>", "<main>\n\\maketitle")

    element_and_content_dict = {
        "main": "document",
        "abstract": "abstract"
    }
    for element, content in element_and_content_dict.items():
        text = begin_end_converter(text, element, content)
    text = section_converter(text)

    # 方程式の変換
    # <eq> (equiation)
    # <fm> (formula)
    equation_pattern = r"<eq>(.*?)</eq>"
    def convert_equation(match):
        equations = match.group(1)
        eq_lines = equations.split('\n')[1:-1]  # Remove opening and closing tags
        latex_lines = [re.sub(r"<fm>(.*?)</fm>", r"\1 \\\\", line) for line in eq_lines]
        pattern = r"<fm>(.*?)</fm>"
        matches = re.findall(pattern, equations)
        bracket_count = sum(match.count("&") for match in matches)
        column = "l" * (bracket_count+1)
        return "\n\n\\[\n\\left\\{\n\\begin{array}{" + column + "}\n" + "\n".join(latex_lines) + "\n\\end{array}\n\\right.\n\\]"

    text = re.sub(equation_pattern, convert_equation, text, flags=re.DOTALL)

    text = replace_fractions(text) # 分数の変換

    print(f"【Result】\n\n{text}")
    print("クリップボードにコピーされました")
    pyperclip.copy(text)

    return text

def write_tex_file(content, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

def compile_tex_to_pdf(tex_filename):
    try:
        subprocess.run(["platex", f"{tex_filename}.tex"], check=True)
        subprocess.run(["dvipdfmx", f"{tex_filename}.dvi"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"TeX compilation failed with error: {e}")
# テスト
text = """

<title>ヒューマンコンピュータインタラクションR2</title>
<author>中村裕大</author>
<date>May 24, 2023</date>

<main>

<abstract>R2-1, R2-2のそれぞれのレポートの詳細は各々のzipファイルの中に格納している</abstract>
<section>
<headline>R2-1</headline>
「サンプルプログラムを参考にして， カメラ入力に対応して出力・振る舞いが変化する プログラム・作品を作成しなさい． 出力内容の独創性やアプリケーションのおもしろさも評価の対象となる． 例えば，入力画像の手領域をラケットのかわりにしてボールを打つ対戦ゲームなどが考えられる．」
とのことだったのでキーボードを空中に表示し、入力できるインターフェースを作成してみた。
作成に当たりPython言語を使用しているが、教授に許可はいただいています。
起動前に環境構築用のpythonプログラム[downloader.py]を作成しているので、pythonで起動していただきたい。
不具合が起きる可能性大なので、37021404中村裕大まで問い合わせください。
<section>

<headline>R2-2</headline>
上記のプログラムとは打って変わり、なんの変哲もない顔認証プログラムであります。
processingで書いているのでとくに環境構築などは必要ありません。
</main>
"""

"""
<eq>
<fm>sin x + y = 1</fm>
<fm>x + 2y = 3 & (c = 0, 1, 2, ...) </fm>
<fm>3x + y = 4/5 + 10</fm>
</eq>

"""


if __name__ == "__main__":
    print("file name >> ")
    filename = f"{input()}"
    if not is_error_exists(text):
        text = convert_math_to_latex(text)
        print(text)
        text = transform_latex(text)
        text = convert_to_latex(text)
        print(text)
        write_tex_file(text, f"{filename}.tex")
        compile_tex_to_pdf(filename)
        os.remove(f"{filename}.aux")
        os.remove(f"{filename}.dvi")
        os.remove(f"{filename}.log")
