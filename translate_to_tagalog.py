#!/usr/bin/env python3
"""
translate_to_tagalog.py

CLI translator to Tagalog (Filipino) using OpenAI's Responses API.
- Translates up to 4000 words per chunk with accuracy-focused settings
- Preserves names, code blocks, numbers, URLs, and a custom glossary
- Reads from file or stdin; writes to stdout or a file

Usage:
  python translate_to_tagalog.py -i input.txt -o output.tl.txt
  echo "Your text here" | python translate_to_tagalog.py
  python translate_to_tagalog.py -i input.txt --formal --glossary "Blue Butterfly,Dragon,Jeet Kune Do,Microsoft"

Env:
  OPENAI_API_KEY must be set.
"""

import os
import sys
import argparse
import re
from typing import List, Iterable

# ------- Config -------
DEFAULT_MODEL = "gpt-4.1-mini"   # quality/cost balanced; change to a bigger model if desired
MAX_WORDS_PER_CHUNK = 4000
TEMPERATURE = 0.2                 # low temp for faithful translation
# ----------------------


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def split_into_paragraphs(text: str) -> List[str]:
    # Keep paragraph boundaries; normalize Windows newlines.
    text = text.replace("\r\n", "\n")
    # Split on two or more newlines to keep structure
    parts = re.split(r"\n{2,}", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_by_words(text: str, max_words: int = MAX_WORDS_PER_CHUNK) -> List[str]:
    """Greedy pack paragraphs into chunks up to max_words."""
    paras = split_into_paragraphs(text)
    chunks, buff, count = [], [], 0
    for p in paras:
        wc = word_count(p)
        if wc > max_words:
            # If a single paragraph is too long, split by sentences.
            sentences = re.split(r'(?<=[.!?])\s+', p)
            cur, cur_wc = [], 0
            for s in sentences:
                swc = word_count(s)
                if cur_wc + swc > max_words and cur:
                    chunks.append("\n".join(buff + [" ".join(cur)]))
                    buff, count, cur, cur_wc = [], 0, [], 0
                cur.append(s)
                cur_wc += swc
            if cur:
                if count + cur_wc > max_words and buff:
                    chunks.append("\n\n".join(buff))
                    buff, count = [], 0
                buff.append(" ".join(cur))
                count += cur_wc
        else:
            if count + wc > max_words and buff:
                chunks.append("\n\n".join(buff))
                buff, count = [], 0
            buff.append(p)
            count += wc
    if buff:
        chunks.append("\n\n".join(buff))
    return chunks


def build_system_instruction(formal: bool, glossary: List[str]) -> str:
    tone = (
        "Gamitin ang **magalang at pormal** na Tagalog (Filipino),"
        if formal else
        "Gamitin ang **natural at malinaw** na Tagalog (Filipino) na pangkalahatang mambabasa,"
    )
    glossary_guidance = ""
    if glossary:
        glossary_guidance = (
            "\n- Huwag isalin ang mga sumusunod (panatilihing eksakto ang baybay): "
            + ", ".join([f"“{term.strip()}”" for term in glossary if term.strip()]) + "."
        )

    return f"""Ikaw ay isang **propesyonal at lubos na maingat na tagasalin**.
Layunin: tumpak, kumpleto, at idiomatic na pagsasalin sa Tagalog (Filipino), may tamang daloy at konteksto.
Mga panuntunan:
- {tone} at panatilihin ang kahulugan, tono, at intensyon ng orihinal.
- Iwasan ang literal na salin kapag hindi natural; gumamit ng katumbas na idyoma sa Filipino.
- Panatilihin: mga pangalan, terminong teknikal, code blocks, numero, unit, URL, at email.
- Ayusin ang bantas at baybay upang maging malinis at madaling basahin.
- Huwag magdagdag o magbawas ng impormasyon; huwag magkomento—**pagsasalin lamang ang ilalabas**.
- Gumamit ng “ni/sa/kay/kina” at iba pang pang-ukol nang wasto; iwasan ang sobrang pag-ingles.
- Kung may di-malinaw, isalin sa pinaka-makatwirang paraan batay sa konteksto.
{glossary_guidance}
Output: **Isang kumpletong salin sa Tagalog**; panatilihin ang talata/format ng orihinal."""
    

def translate_chunk(client, model: str, chunk: str, system_instruction: str) -> str:
    # Use Responses API (Python SDK)
    # Docs: https://platform.openai.com/docs/api-reference/responses
    response = client.responses.create(
        model=model,
        temperature=TEMPERATURE,
        input=f"{system_instruction}\n\n---\n\nIsalin ang sumusunod na teksto sa Tagalog (Filipino):\n\n{chunk}\n",
    )
    # In the new SDK, output_text provides the text aggregate conveniently.
    return getattr(response, "output_text", None) or response.output[0].content[0].text


def main():
    try:
        from openai import OpenAI  # official SDK
    except Exception as e:
        print("Please install the official OpenAI Python SDK:\n  pip install openai", file=sys.stderr)
        sys.exit(2)

    parser = argparse.ArgumentParser(description="Translate text to Tagalog (Filipino) using OpenAI.")
    parser.add_argument("-i", "--input", help="Path to input text file. Omit to read from stdin.")
    parser.add_argument("-o", "--output", help="Path to write translated text. Omit to print to stdout.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"OpenAI model (default: {DEFAULT_MODEL})")
    parser.add_argument("--formal", action="store_true", help="Use more formal Tagalog tone.")
    parser.add_argument("--glossary", default="", help="Comma-separated terms to keep in original form.")
    parser.add_argument("--max-words", type=int, default=MAX_WORDS_PER_CHUNK, help="Max words per chunk.")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    # Read input
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    text = text.strip()
    if not text:
        print("No input text provided.", file=sys.stderr)
        sys.exit(1)

    # Prepare
    glossary = [t.strip() for t in args.glossary.split(",")] if args.glossary else []
    sys_instruction = build_system_instruction(args.formal, glossary)
    chunks = chunk_by_words(text, max_words=args.max_words)

    client = OpenAI()
    outputs: List[str] = []

    for idx, chunk in enumerate(chunks, 1):
        translated = translate_chunk(client, args.model, chunk, sys_instruction)
        outputs.append(translated)

    final_text = "\n\n".join(outputs)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(final_text)
    else:
        sys.stdout.write(final_text)


if __name__ == "__main__":
    main()