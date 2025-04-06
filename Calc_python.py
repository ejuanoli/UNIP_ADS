def soma():
    num1 = float(input("Primeiro número: "))
    num2 = float(input("Segundo número: "))
    print("Resultado:", num1 + num2)

def subtracao():
    num1 = float(input("Primeiro número: "))
    num2 = float(input("Segundo número: "))
    print("Resultado:", num1 - num2)

def divisao():
    num1 = float(input("Dividendo: "))
    num2 = float(input("Divisor: "))
    if num2 == 0:
        print("Erro: Divisão por zero!")
    else:
        print("Resultado:", num1 / num2)

def multiplicacao():
    num1 = float(input("Primeiro número: "))
    num2 = float(input("Segundo número: "))
    print("Resultado:", num1 * num2)

def potencia_quadrado():
    num = float(input("Número: "))
    print("Resultado:", num ** 2)

def soma_ilimitada():
    total = 0
    contador = 0
    while True:
        contador += 1
        try:
            num = float(input(f'Digite o {contador}º número: '))
            total += num
            print(f'Resultado parcial: {total}')
        except ValueError:
            print("Entrada inválida. Digite um número válido.")
            continue
        if escolha() == 0:
            break
    print(f'O resultado final da soma ilimitada é {total}')

def bhaskara():
    a = float(input("a: "))
    b = float(input("b: "))
    c = float(input("c: "))
    delta = b ** 2 - 4 * a * c

    if delta < 0:
        print("Sem raízes reais")
    else:
        x1 = (-b + delta ** 0.5) / (2 * a)
        x2 = (-b - delta ** 0.5) / (2 * a)
        print(f"Raízes: {x1} e {x2}")

def conjuntos():
    set1 = input("Primeiro conjunto (elementos separados por vírgula): ").split(',')
    set1 = [item.strip() for item in set1]
    set2 = input("Segundo conjunto (elementos separados por vírgula): ").split(',')
    set2 = [item.strip() for item in set2]

    uniao = []
    for item in set1 + set2:
        if item not in uniao:
            uniao.append(item)
    print("União:", uniao)

    intersecao = []
    for item in set1:
        if item in set2 and item not in intersecao:
            intersecao.append(item)
    print("Intersecção:", intersecao)


def raiz_quadrada():
    num = float(input("Número: "))
    if num < 0:
        print("Número inválido!")
    else:
        print(f"Raiz quadrada:{num ** 0.5:.2f}")


def escolha():
    opcao = 0
    while not opcao == 1:
        escolha = 0
        if not escolha == 1:
            opcao = int(input('\nEscolha uma opção:\n[0] - Resultado\n[1] - Acrescentar número\nOpção: '))
            if opcao == 0:
                return opcao
            elif opcao == 1:
                return opcao
            else:
                print("Opção inválida. Escolha 0 ou 1.")
        else:
            print("Entrada inválida. Digite um número válido.")

def porcentagem():
    print("Escolha um cálculo de porcentagem:")
    print("1. Desconto")
    print("2. Acréscimo")
    operacao_porcentagem = int(input("Digite o número da operação desejada: "))
    valor = float(input("Digite o valor: "))
    porcentagem = float(input("Digite a porcentagem: "))
    if operacao_porcentagem == 1:
        resultado = calcular_desconto(valor, porcentagem)
        print(f"Resultado: {resultado}")
    elif operacao_porcentagem == 2:
        resultado = calcular_acrescimo(valor, porcentagem)
        print(f"Resultado: {resultado}")
    else:
        print("Opção inválida.")

def calcular_desconto(valor, porcentagem):
    return valor - (valor * porcentagem / 100)

def calcular_acrescimo(valor, porcentagem):
    return valor + (valor * porcentagem / 100)

def regra_de_tres_normal(a, b, c):
    return (b * c) / a

def regra_de_tres_inversa(a, b, c):
    return (a * b) / c

def funcao_linear():
    a = float(input("Coeficiente angular (a): "))
    b = float(input("Coeficiente linear (b): "))

    print("1. Calcular f(x)")
    print("2. Encontrar x dado f(x)")
    op = input("Escolha: ")

    if op == '1':
        x = float(input("x = "))
        print(f"f({x}) = {a * x + b}")
    elif op == '2':
        y = float(input("y = "))
        x = (y - b) / a
        print(f"x = {x}")


def equacoes_lineares():
    print("Primeira equação (ax + by = e):")
    a = float(input("a: "))
    b = float(input("b: "))
    e = float(input("e: "))

    print("Segunda equação (cx + dy = f):")
    c = float(input("c: "))
    d = float(input("d: "))
    f = float(input("f: "))

    det = a * d - b * c
    if det == 0:
        print("Sistema sem solução única!")
        return

    x = (e * d - b * f) / det
    y = (a * f - e * c) / det
    print(f"Solução: x = {x}, y = {y}")

def main():
    opcao = 0
    while not opcao == 1:
        print("[0] Sair")  # Ok
        print("[1] Soma")  # Ok
        print("[2] Subtração")  # Ok
        print("[3] Divisão")  # Ok
        print("[4] Multiplicação")  # Ok
        print("[5] Potência ao quadrado")  # Ok
        print("[6] Soma Ilimitada")  # Ok
        print("[7] Bhaskara")  # Ok
        print("[8] Conjuntos")  # Ok
        print("[9] Raiz Quadrada")  # Ok
        print("[10] Cálculos de Porcentagem")  # Ok
        print("[11] Regra de 3")  # Ok
        print("[12] Função Linear")  # Validar
        print("[13] Equações Lineares")  # Validar

        escolha = input("\nEscolha uma opção: ")

        if escolha == '0':
            print("/////////////////////\n\
Desenvolvido por:\n\
EDUARDO JUAN\n\
LUCCA VIEIRA\n\
GABRIEL COELHO\n\
LEONARDO FISCHER\n\
/////////////////////")
            input("Pressione qualquer tecla para fechar...")
            break
        elif escolha == '1':
            soma()
        elif escolha == '2':
            subtracao()
        elif escolha == '3':
            divisao()
        elif escolha == '4':
            multiplicacao()
        elif escolha == '5':
            potencia_quadrado()
        elif escolha == '6':
            soma_ilimitada()
        elif escolha == '7':
            bhaskara()
        elif escolha == '8':
            conjuntos()
        elif escolha == '9':
            raiz_quadrada()
        elif escolha == '10':
            porcentagem()
        elif escolha == '11':
            print("Escolha um tipo de Regra de 3:")
            print("1. Normal")
            print("2. Inversa")
            tipo_regra = int(input("Digite o número da operação desejada: "))
            a = float(input("Digite o valor de A: "))
            b = float(input("Digite o valor de B: "))
            c = float(input("Digite o valor de C: "))
            if tipo_regra == 1:
                resultado = regra_de_tres_normal(a, b, c)
                print(f"Resultado: {resultado}")
            elif tipo_regra == 2:
                resultado = regra_de_tres_inversa(a, b, c)
                print(f"Resultado: {resultado}")
            else:
                print("Opção inválida.")
        elif escolha == '12':
            funcao_linear()
        elif escolha == '13':
            equacoes_lineares()
        else:
            print("Opção inválida!")

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
