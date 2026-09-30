import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.evaluator import execute_python_code

code = """nomes = []
precos = []

for i in range(5):
    nome = input()
    preco = float(input())
    nomes.append(nome)
    precos.append(preco)

for i in range(5):
    print("Produto:", nomes[i], "- Preço: R$", format(precos[i], ".2f"))"""

input_data = "Arroz\n25\nFeijao\n10\nCafe\n15\nLeite\n5\nAcucar\n4\n"

result = execute_python_code(code, input_data)
print('OUTPUT:')
print(repr(result['output']))
print('ERROR:', result['error'])