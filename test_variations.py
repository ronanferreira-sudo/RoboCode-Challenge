import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.evaluator import execute_python_code
from app.main import normalize_output, is_lenient_match

# Código do solution_code do banco
solution_code = """nomes = []
precos = []

for i in range(5):
    nome = input()
    preco = float(input())
    nomes.append(nome)
    precos.append(preco)

for i in range(5):
    print("Produto:", nomes[i], "- Preço: R$", format(precos[i], ".2f"))"""

# Test case do banco
input_data = "Arroz\n25\nFeijão\n10\nCafé\n15\nLeite\n5\nAçúcar\n4\n"
expected_output = """Produto: Arroz - Preço: R$ 25.00
Produto: Feijão - Preço: R$ 10.00
Produto: Café - Preço: R$ 15.00
Produto: Leite - Preço: R$ 5.00
Produto: Açúcar - Preço: R$ 4.00"""

print("=== Testando solution_code ===")
result = execute_python_code(solution_code, input_data)
print("Error:", result['error'])
print("Output:", repr(result['output']))

actual_output = normalize_output(result['output'])
expected_norm = normalize_output(expected_output)
print("Actual norm:", repr(actual_output))
print("Expected norm:", repr(expected_norm))
print("Match:", is_lenient_match(actual_output, expected_norm))
print()

# Now test with different user code that might have issues
# User might use f-string with :.2f instead of format()
user_code_v1 = """nomes = []
precos = []

for i in range(5):
    nome = input()
    preco = float(input())
    nomes.append(nome)
    precos.append(preco)

for i in range(5):
    print(f"Produto: {nomes[i]} - Preço: R$ {precos[i]:.2f}")"""

print("=== Testando user_code com f-string ===")
result = execute_python_code(user_code_v1, input_data)
print("Error:", result['error'])
print("Output:", repr(result['output']))
print("Match:", is_lenient_match(normalize_output(result['output']), expected_norm))
print()

# User might use format() but wrong decimal places
user_code_v2 = """nomes = []
precos = []

for i in range(5):
    nome = input()
    preco = float(input())
    nomes.append(nome)
    precos.append(preco)

for i in range(5):
    print("Produto:", nomes[i], "- Preço: R$", format(precos[i], ".1f"))"""

print("=== Testando user_code com 1 casa decimal ===")
result = execute_python_code(user_code_v2, input_data)
print("Error:", result['error'])
print("Output:", repr(result['output']))
print("Match:", is_lenient_match(normalize_output(result['output']), expected_norm))