import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.main import normalize_output, canonicalize_numbers, is_lenient_match

expected = """Produto: Arroz - Preço: R$ 25.00
Produto: Feijão - Preço: R$ 10.00
Produto: Café - Preço: R$ 15.00
Produto: Leite - Preço: R$ 5.00
Produto: Açúcar - Preço: R$ 4.00"""

actual = """Produto: Arroz - Preço: R$ 25.00
Produto: Feijao - Preço: R$ 10.00
Produto: Cafe - Preço: R$ 15.00
Produto: Leite - Preço: R$ 5.00
Produto: Acucar - Preço: R$ 4.00"""

print("Expected:")
print(repr(expected))
print()
print("Actual:")
print(repr(actual))
print()

actual_norm = normalize_output(actual)
expected_norm = normalize_output(expected)
print("Normalized actual:", repr(actual_norm))
print("Normalized expected:", repr(expected_norm))
print()

print("is_lenient_match:", is_lenient_match(actual, expected))