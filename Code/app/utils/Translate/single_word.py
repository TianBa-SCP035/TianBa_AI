# -*- coding: utf-8 -*-
from translate import Translator

def translate_text(text: str, from_lang: str = "zh-cn", to_lang: str = "en") -> str:
    """文本翻译功能"""
    if not text or not text.strip():
        return text
    
    try:
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text

if __name__ == "__main__":
    original = "为76有牺牲2多壮志，you看看me"
    translated = translate_text(original)
    print(f"原文: {original}")
    print(f"翻译: {translated}")