import re
import spacy
import logging
import language_tool_python
import difflib
from num2words import num2words

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

LOG_FILE = "profanity_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

safe_phrases = [
    "black man", "white woman", "asian guy", "gay man", "lesbian woman"
]

custom_map = {
    "fuck off": ["bugger off"],
    "fuck them": ["screw them"],
    "fucking": ["freaking"],
    "fuck": ["freak"],
    "bitch": ["bish"],
    "shit": ["crap"],
    "dick": ["joystick"],
    "penis": ["manhood"],
    "vagina": ["special area"],
    "balls": ["family jewels"],
    "asshole": ["a-hole"],
    "ass": ["buns"],
    "naked": ["unclothed"],
    "porn": ["corn"],
    "masturbate": ["solo"],
    "jerk off": ["solo"],
    "blow job": ["BJ"],
    "oral sex": ["play his flute"],
    "anal": ["backdoor"],
    "rape": ["SA'd"],
    "suicide": ["unalive"],
    "kill": ["offed"],
    "murder": ["ended"],
    "cum": ["his smoothie"],
    "orgasm": ["the big O"],
    "ejaculated": ["released"],
    "threesome": ["three-way"],
    "stripper": ["exotic dancer"],
    "brothel": ["red-light zone"],
    "prostitute": ["worker girl"],
    "escort": ["cash-only companion"],
    "pornography": ["cornography"],
    "incest": ["family relations"],
    "drugs": ["substances"],
    "cocaine": ["substances"],
    "heroin": ["substances"],
    "retard": ["mentally slow"],
    "goddam": ["damn"],
    "fuckin'": ["freaking"],
    " f***ING": ["freaking"],
    "WTF": ["What the Freaking"],
    "fucked": ["freaked"],
   }

sorted_phrases = sorted(custom_map.keys(), key=len, reverse=True)

def is_safe_phrase_in_text(text):
    return any(phrase in text.lower() for phrase in safe_phrases)

def replace_profanities(text):
    def replacer(match):
        word = match.group(0)
        word_lower = word.lower()
        if word_lower in custom_map:
            replacement = custom_map[word_lower][0]
            return replacement.capitalize() if word.istitle() else replacement.upper() if word.isupper() else replacement
        return word
    pattern = r'\b(?:' + '|'.join(re.escape(k) for k in sorted_phrases) + r')\b'
    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)

def expand_number_suffixes(text):
    def suffix_replace(match):
        num = match.group(1)
        suffix = match.group(2).lower()
        try:
            num_val = int(num)
            multiplier = {'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000}.get(suffix, 1)
            total = num_val * multiplier
            return num2words(total).capitalize()
        except:
            return match.group(0)
    return re.sub(r'\b(\d+)([kKmMbB])\b', suffix_replace, text)

def replace_units(text):
    unit_map = {
        'ft': 'feet',
        'kg': 'kilograms',
        'lb': 'pounds',
        'lbs': 'pounds',
        'km': 'kilometers',
        'm': 'meters',
        'cm': 'centimeters',
        'mm': 'millimeters',
        'in': 'inches',
        '%': 'percent'
    }
    def unit_replace(match):
        num = match.group(1)
        unit = match.group(2).lower()
        if unit in unit_map:
            try:
                word = num2words(int(num)).capitalize()
                return f"{word} {unit_map[unit]}"
            except:
                return match.group(0)
        return match.group(0)
    return re.sub(r'\b(\d+)\s?(ft|kg|lb|lbs|km|m|cm|mm|in|%)\b', unit_replace, text)

def replace_currency_and_numbers(text):
    def currency_replace(match):
        symbol = match.group(1)
        num = match.group(2).replace(",", "")
        try:
            number = float(num)
            word_number = num2words(number).capitalize()
            currency_word = {
                '$': "dollars",
                'USD': "dollars",
                'usd': "dollars",
                'Rs.': "rupees",
                'rs.': "rupees",
                'INR': "rupees",
                'inr': "rupees"
            }.get(symbol, "currency")
            return f"{word_number} {currency_word}"
        except:
            return match.group(0)

    text = re.sub(r'\b(\$|USD|usd|Rs\.|rs\.|INR|inr)\s?(\d{1,3}(?:,\d{3})*|\d+(\.\d+)?)\b', currency_replace, text)
    text = re.sub(r'\$', "money", text)
    text = re.sub(
        r'\b(\d{1,2})\s*(A\.M\.|P\.M\.)\b',
        lambda m: f"{num2words(int(m.group(1))).capitalize()} {m.group(2).upper()}",
        text,
        flags=re.IGNORECASE
    )
    def number_replace(match):
        try:
            num = int(match.group())
            return num2words(num, to='year').capitalize() if 1000 <= num <= 2100 else num2words(num).capitalize()
        except:
            return match.group()
    text = re.sub(r'\b\d+\b', number_replace, text)
    return text

def remove_irrelevant_phrases(text):
    return "" if text.strip().lower() == "thank you for me" else text

def paragraphify(text, max_words=60):
    words = text.split()
    return "\n\n".join(" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words))

def mark_changes_in_original(orig_para, edited_para):
    orig_words = orig_para.split()
    edited_words = edited_para.split()
    matcher = difflib.SequenceMatcher(None, orig_words, edited_words)

    bolded_orig = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            bolded_orig.extend(orig_words[i1:i2])
        else:
            # Bold all changed tokens (words or punctuation) exactly once
            for w in orig_words[i1:i2]:
                # Avoid duplicating if the word is already bolded
                if not (w.startswith("**") and w.endswith("**")):
                    bolded_orig.append(f"**{w}**")
                else:
                    bolded_orig.append(w)
    return ' '.join(bolded_orig)


def edit_comment(comment):
    if not comment.strip():
        return "", ""

    if is_safe_phrase_in_text(comment):
        return comment.strip(), comment.strip()

    paragraphs = re.split(r'\n{1,2}', comment.strip())
    bolded_original_paragraphs = []
    edited_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            continue
        edited_para = replace_profanities(para)
        edited_para = expand_number_suffixes(edited_para)
        edited_para = replace_units(edited_para)
        edited_para = replace_currency_and_numbers(edited_para)
        edited_para = language_tool_python.utils.correct(edited_para, tool.check(edited_para))
        edited_para = remove_irrelevant_phrases(edited_para)

        if not edited_para:
            continue

        bolded_orig = mark_changes_in_original(para, edited_para)
        bolded_original_paragraphs.append(bolded_orig)
        edited_paragraphs.append(paragraphify(edited_para))

    return "\n\n".join(bolded_original_paragraphs), "\n\n".join(edited_paragraphs)
