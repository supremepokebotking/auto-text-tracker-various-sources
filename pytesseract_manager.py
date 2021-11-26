
import cv2
import pytesseract
import re

try:
    from PIL import Image
except ImportError:
    import Image

import os

def parse_rect_with_pytesseract_config(image_section, ocr_config):
    print('ocr_config', ocr_config)

    messages = []

    results = []

    always_use_list = False
    if 'always_use_list' in ocr_config:
        always_use_list = ocr_config['always_use_list']

    for language_config in ocr_config['language_configs']:
        # default values
        support_other_langages=False
        psm_7=False
        system_language=None
        language = 'eng'
        game_config = 'pokemon-sword'

        if 'support_other_langages' in language_config:
            support_other_langages=language_config['support_other_langages']
        if 'psm_7' in language_config:
            psm_7=language_config['psm_7']
        if 'language' in language_config:
            system_language=language_config['language']

        text = parse_rect_with_pytesseract(image_section, support_other_langages, psm_7, system_language)
        print('detected text: %s'% text)
        results.append(text)

    if len(results) == 1:
        if not always_use_list:
            return {"result":results[0]}

    return {"result":results}

def parse_rect_with_pytesseract(image_section, support_other_langages=False, psm_7=False, system_language=None):
    img = Image.fromarray(image_section)
    if support_other_langages and psm_7:
        tess_lang = "jpn+kor+chi_sim"
        if system_language is not None and system_language not in tess_lang:
            tess_lang = '%s+%s' % (system_language, tess_lang)
        raw_text = pytesseract.image_to_string(img, lang=tess_lang, config='--psm 7')
    elif support_other_langages:
        tess_lang = "jpn+kor+chi_sim"
        if system_language is not None and system_language not in tess_lang:
            tess_lang = '%s+%s' % (system_language, tess_lang)
        raw_text = pytesseract.image_to_string(img, lang=tess_lang)
    elif psm_7:
        raw_text = pytesseract.image_to_string(img, config='--psm 7')
    else:
        tess_lang = "eng"
        if system_language is not None and system_language not in tess_lang:
            tess_lang = '%s+%s' % (system_language, tess_lang)
            tess_lang = system_language
        raw_text = pytesseract.image_to_string(img, lang=tess_lang, config='--psm 7')
    raw_text = raw_text.strip()
    return raw_text
