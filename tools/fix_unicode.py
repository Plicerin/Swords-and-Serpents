#!/usr/bin/env python3
"""Fix Unicode characters in decode_full_pipeline.py"""
content = open('decode_full_pipeline.py', 'r', encoding='utf-8').read()
# Replace all Unicode arrows, em dashes, en dashes
content = content.replace('\u2192', '->')  # right arrow
content = content.replace('\u2014', '--')  # em dash
content = content.replace('\u2013', '-')   # en dash
content = content.replace('\u2190', '<-')  # left arrow
open('decode_full_pipeline.py', 'w', encoding='utf-8').write(content)
print("Fixed all Unicode characters")
