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

input_data = "Arroz\n25\nFeijão\n10\nCafé\n15\nLeite\n5\nAçúcar\n4\n"

expected_output = """Produto: Arroz - Preço: R$ 25.00
Produto: Feijão - Preço: R$ 10.00
Produto: Café - Preço: R$ 15.00
Produto: Leite - Preço: R$ 5.00
Produto: Açúcar - Preço: R$ 4.00"""

result = execute_python_code(solution_code, input_data)
print("Solution output:", repr(result['output']))
print("Error:", result['error'])

actual_norm = normalize_output(result['output'])
expected_norm = normalize_output(expected_output)
print("Normalized actual:", repr(actual_norm))
print("Normalized expected:", repr(expected_norm))
print("Match:", is_lenient_match(result['output'], expected_output))