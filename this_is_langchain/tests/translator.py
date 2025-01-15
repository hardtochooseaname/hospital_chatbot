from deep_translator import GoogleTranslator

def translate_to_chinese_with_format(data: str) -> str:
    """
    Translate the input English text to Chinese while preserving the original format, 
    including indentation and line breaks.
    """
    # 分割为行，逐行翻译
    lines = data.splitlines()
    translated_lines = []
    translator = GoogleTranslator(source='en', target='chinese (simplified)')
    
    for line in lines:
        # 检测前导空白
        leading_spaces = len(line) - len(line.lstrip())
        # 翻译非空行
        if line.strip():
            translated_text = translator.translate(line.strip())
            # 恢复前导空白
            translated_lines.append(" " * leading_spaces + translated_text)
        else:
            # 空行直接添加
            translated_lines.append("")
    
    # 合并行并返回
    return "\n".join(translated_lines)

input_text = """
  Magnesium: spinach, almonds, cashews
  Vitamin C: oranges, strawberries, bell peppers
"""

translated_text = translate_to_chinese_with_format(input_text)
print(translated_text)
