import copy
import optparse
import time
import math

# Parãmetros de entrada
parser = optparse.OptionParser()
parser.add_option('-o','--out',
                  help='Opção obrigatória. Arquivo de saida da melhor solucao encontrada',
                  dest='saida')

parser.add_option('-d','--dat',
                  help='Opção obrigatória. Arquivo de entrada com a instancia (.dat)',
                  dest='arquivo_dat')
parser.add_option('-i','--interchange',
                  help='Quantidade de interchanges para a perturbação\n'
                       'Maximo de metade do tamanho da lista',
                  type="int",
                  dest='qtd_interchanges')
parser.add_option('-t','--tempo_execucao',
                  help='Tempo limite de execucao em segundos\n',
                  type="int",
                  dest='tempo_execucao')

comandos_obrigatorios = ['saida', 'arquivo_dat']

(opts,args)=parser.parse_args()

for m in comandos_obrigatorios:
    if not opts.__dict__[m]:
        print('Comando obrigatorio esta faltando ',)
        parser.print_help()
        exit(-1)

# Variáveis globais para armazenamento das soluções parciais
makespanGlobal =0
tempoMelhorSolucao =0
melhorSolucaoAtual = []

class Tarefa(object):
    label = 0
    pi = 0
    si = None

# solucaoInicial: Recebe um nome de arquivo e retorna a solução inicial
def solucaoInicial(nomeArquivo):

    #Leitura dos dados do arquivo
    arquivo = open(nomeArquivo, 'r')
    lista = arquivo.readlines()
    arquivo.close()

    # lista: lista com todas as linhas lidas do arquivo, em formato de inteiros
    lista = [int(i) for i in lista]
    tarefas = []

    # numeroTarefas: total de tarefas recebidas do arquivo, é a primeira linha do arquivo
    numeroTarefas=lista.pop(0);

    #Ordenação da lista do menor tempo de processamento para o maior
    lista.sort(reverse=True)

    for i in range(len(lista)):
        tarefa = Tarefa()
        tarefa.pi = lista[i]
        tarefa.label=i
        tarefas.append(tarefa)

    solucaoInicial = sum(lista)
    print(solucaoInicial)

    listaDeInicios = [0]
    inicioPrimeiraTarefa = 0

    for i in range (len(lista)) :
        listaDeInicios.append(listaDeInicios[i] + lista[i])

    listaDeInicios.pop(-1)

    for i in range(len(listaDeInicios)):
        tarefas[i].si = listaDeInicios[i]

    return tarefas

# calculaMakespan: Recebe uma lista de tarefas e retorna o tempo de duração total para a execução das tarefas
def calculaMakespan(listaDeTarefas):
    makespan=0
    for i in range(len(listaDeTarefas)):
        if (listaDeTarefas[i].pi+listaDeTarefas[i].si >= makespan):
            makespan = listaDeTarefas[i].pi+listaDeTarefas[i].si
    return makespan

def insereEShift(listaDeTarefas,posASerInserida,posASerRemovida):

    listaProvisoria = copy.deepcopy(listaDeTarefas)
    tarefaAInserir = listaProvisoria[posASerRemovida]

    if (posASerInserida==posASerRemovida):
        return listaProvisoria
    else:
        if (posASerInserida<posASerRemovida):
            for i in range(posASerRemovida,posASerInserida,-1):
                listaProvisoria[i]=listaDeTarefas[i-1]
        else:
            if (posASerInserida>posASerRemovida):
                for i in range(posASerRemovida,posASerInserida):
                    listaProvisoria[i]=listaDeTarefas[i+1]

    listaProvisoria[posASerInserida]=tarefaAInserir
    return listaProvisoria

def comparaTarefas(pos, lista):
    minimoentreatualeanterior = min(lista[pos-1].pi, lista[pos].pi)
    minimoainserir = lista[pos-1].si + minimoentreatualeanterior

    minAtual = 0

    for a in range(pos):
        m = min(lista[a].pi, lista[pos].pi)
        if (lista[a].si + m>=minAtual):
            minAtual=lista[a].si+m

    tarefaquetemomax = minAtual

    tempo = max(tarefaquetemomax, minimoainserir)

    return tempo

# constroiNovaLista:
def constroiNovaLista(listaPermutada, posASerInserida):
    for i in range(posASerInserida,len(listaPermutada)):
        tempo = comparaTarefas(i,listaPermutada)
        listaPermutada[i].si = tempo
    return listaPermutada

# buscaLocal:
def buscaLocal(listaDeTarefas):
    global makespanGlobal
    global tempoMelhorSolucao
    global melhorSolucaoAtual
    from random import randint

    makespanInicial = makespanGlobal

    copiaLista = copy.deepcopy(listaDeTarefas)

    melhorou = True
    while (melhorou==True):
        random1 = randint(1, len(listaDeTarefas) - 2)
        random2 = randint(random1 + 1, len(listaDeTarefas) - 1)
        posASerInserida = random1
        posASerRemovida = random2

        listaPermutada = copy.deepcopy(insereEShift(copiaLista, posASerInserida, posASerRemovida))

        novaLista = copy.deepcopy(constroiNovaLista(listaPermutada, posASerInserida))
        makenovo = calculaMakespan(novaLista)
        if (makenovo < makespanInicial):
            tempoMelhorSolucao = (time.time() - start_time)
            makespanInicial=makenovo
            melhorou = True
            copiaLista = copy.deepcopy(novaLista)
        else:
            melhorou = False

    return copiaLista

# imprimeListaTarefas: Imprime uma lista de tarefas, com seu label, tempo de processamento e tempo de início
def imprimeListaTarefas(listaDeTarefas):
    for i in range(len(listaDeTarefas)):
        print('label',listaDeTarefas[i].label)
        print('P', listaDeTarefas[i].pi)
        print('S', listaDeTarefas[i].si)

# imprimeLabel: Imprime o label de uma lista de tarefas. Útil para verificar a ordem das tarefas na lista
def imprimeLabel(listaDeTarefas):
    for i in range(len(listaDeTarefas)):
        print(""+str(listaDeTarefas[i].label))

# interchange: Realiza "qtd_swaps" de trocas entre tarefas na lista
def interchange(lista,qtd_swaps):
    import random
    import math
    metade = math.floor(len(lista)/2)
    lista_random1 = random.sample(range(1, metade),qtd_swaps)
    lista_random2 = random.sample(range(metade, len(lista)), qtd_swaps)

    copiaLista = copy.deepcopy(lista)

    for i in range(0,len(lista_random1)):
        aux = copiaLista[lista_random2[i]]
        copiaLista[lista_random2[i]]= copiaLista[lista_random1[i]]
        copiaLista[lista_random1[i]] = aux

    return copy.deepcopy(copiaLista)

def perturbaLista(lista):

    lista = copy.deepcopy(interchange(lista, opts.qtd_interchanges))
    lista = copy.deepcopy(constroiNovaLista(lista, 1))
    return lista

def ils(solucao):

    global makespanGlobal
    global tempoMelhorSolucao
    global melhorSolucaoAtual



# ------------------ Início
# ------------------ Iterated Local Search

# Solução inicial
melhorSolucaoAtual = solucaoInicial(optparse.gettext(opts.arquivo_dat))

# Verificação dos parâmetros de entrada
if (opts.__dict__['qtd_interchanges']):
    limite = math.floor((len(melhorSolucaoAtual) / 2) - 1)
    if (opts.qtd_interchanges > limite):
        print("--- ERRO!!! ----")
        print("Parametro (interchanges) inválido. Deve ser um numero menor ou igual a ", limite)
        exit(-1)
else:
    opts.qtd_interchanges = math.floor(len(melhorSolucaoAtual) * 0.05)
    print('Parametro -i não informado. Prosseguindo com o padrão de %s interchange(s)' % opts.qtd_interchanges)

if not opts.__dict__['tempo_execucao']:
    opts.tempo_execucao = 1800
    print(
        'Parametro -t não informado. Prosseguindo com o padrão de %s segundos para execução' % opts.tempo_execucao)
imprimeLabel(melhorSolucaoAtual)

# Geração do arquivo de log para a solução
arq_saida = open(optparse.gettext(opts.saida), 'w')

start_time = time.time()

makespan = calculaMakespan(melhorSolucaoAtual)
print("Makespan da solução inicial: ", makespan)
makespanGlobal = makespan

solucao = copy.deepcopy(melhorSolucaoAtual)

solucao = copy.deepcopy(buscaLocal(solucao))

# # Busca local com a solução inicial
# while ((time.time() - start_time) < 20):
#     solucao = buscaLocal(solucao)
#     makespannovo = calculaMakespan(solucao)
#     if (makespannovo <= makespanGlobal):
#         print('Novo makespan DENTRO DO PRIMEIRO BUSCA LOCAL: ', makespannovo)
#         print("--- %s seconds ---" % (time.time() - start_time))
#         tempoMelhorSolucao = (time.time() - start_time)
#         makespanGlobal = makespannovo
#         melhorSolucaoAtual = copy.deepcopy(solucao)
#     solucao = copy.deepcopy(melhorSolucaoAtual)


# Laço principal do ILS
while ((time.time() - start_time) < opts.tempo_execucao):

    # Perturbação na lista
    s1 = perturbaLista(solucao)
    # Busca Local com a lista após a perturbação
    s2 = buscaLocal(s1)

    makespannovo = calculaMakespan(s2)
    if (makespannovo <= makespanGlobal):
        if (makespannovo < makespanGlobal):
            tempoMelhorSolucao = (time.time() - start_time)
        print('Novo makespan DENTRO DO LAÇO PRINCIPAL: ', makespannovo)
        print("--- %s seconds ---" % (time.time() - start_time))
        makespanGlobal = makespannovo
        melhorSolucaoAtual = copy.deepcopy(s2)

        solucao = copy.deepcopy(s2)
    else:
        solucao = copy.deepcopy(melhorSolucaoAtual)

final_makespan = calculaMakespan(melhorSolucaoAtual)
print("Makespan FINAL: ", final_makespan)

# Gera os dados e insere no arquivo de LOG
arq_saida.write("Solucao para o arquivo: " + opts.arquivo_dat)
arq_saida.write("\n")
arq_saida.write("\n")

arq_saida.write("Makespan: "+str(final_makespan))
arq_saida.write("\n")
arq_saida.write("\n")

arq_saida.write("Ordem final das tarefas (labels):", )
arq_saida.write("\n")
for s in solucao:
    arq_saida.write("" + str(s.label))
    arq_saida.write(" ")

arq_saida.write("\n")
arq_saida.write("\n")
arq_saida.write("Si = [ ",)
for s in solucao:
    arq_saida.write(""+str(s.si))
    arq_saida.write(" ")
arq_saida.write("]")

arq_saida.write("\n")

arq_saida.write("Pi = [ ", )
for s in solucao:
    arq_saida.write("" + str(s.pi))
    arq_saida.write(" ")
arq_saida.write("]")

arq_saida.write("\n")
arq_saida.write("\n\n")
arq_saida.write("Tempo para encontrar a melhor solucao atual: %f segundos ---" % tempoMelhorSolucao)
arq_saida.write("\n\n")
arq_saida.write("Tempo total de execucao do programa: %s segundos ---" % (time.time() - start_time))
arq_saida.close()
print("--- %s seconds ---" % (time.time() - start_time))