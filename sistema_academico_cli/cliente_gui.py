"""
===============================================================================
SISTEMA ACADÊMICO - INTERFACE GRÁFICA (GUI)
===============================================================================

Descrição:
    Sistema completo de gestão acadêmica com interface gráfica moderna
    Suporta múltiplos perfis (Aluno, Professor, Administrador)
    Integrado com backend em C via DLL/SO

Tecnologias:
    - Python 3.x + Tkinter (interface gráfica)
    - Socket (comunicação cliente-servidor)
    - C DLL (banco de dados backend)
    - JSON (persistência de dados adicionais)
    - Threading/Multiprocessing (servidor paralelo)

Funcionalidades Principais:
    - Sistema de autenticação com recuperação de senha
    - Gestão de turmas, alunos e professores
    - Lançamento e visualização de notas
    - Controle de presença com calendário
    - Sistema de anotações pessoais
    - Temas claro/escuro com transição suave
    - Upload e gerenciamento de arquivos

Estrutura de Classes:
    - LoginWindow: Tela de login/cadastro/recuperação
    - App: Interface principal após login (dashboard, gerenciamento)
    - DatabaseManager: Gestão de usuários e dados JSON

Arquivos Relacionados:
    - database.dll/so: Backend em C para operações de turmas/alunos
    - users.json: Dados de usuários e autenticação
    - anotacoes.json: Sistema de anotações pessoais
    - *.dat: Arquivos binários de persistência (notas, presenças)

Autor: Equipe de Desenvolvimento UNIP
Versão: 2.0.0
===============================================================================
"""

# ==============================================================================
# IMPORTAÇÕES
# ==============================================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
import socket
import os
import ctypes
import threading
import multiprocessing
import time
import struct
import calendar
import re
import json
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS
# ==============================================================================

# Configurar calendário para padrão brasileiro (semana começa na Segunda-feira)
calendar.setfirstweekday(calendar.MONDAY)

# ==============================================================================
# LOCKS E VARIÁVEIS GLOBAIS
# ==============================================================================

# Lock para operações de presença (previne race conditions)
presenca_lock = threading.Lock()

# ==============================================================================
# DEFINIÇÕES DE TEMAS (LIGHT E DARK)
# ==============================================================================

LIGHT_THEME = {
    # --- Cores de Fundo e Estrutura ---
    'bg': '#FFFFFF',          # Cinza muito claro, quase branco, para o fundo principal da aplicação. Proporciona um fundo suave e neutro.
    'card': '#FFFFFF',        # Branco puro, usado para cartões e contêineres, criando um contraste claro com o fundo.
    'input_bg': '#FFFFFF',    # Um branco levemente acinzentado para campos de entrada, sutilmente diferente do fundo do cartão.

    # --- Cor Primária (Destaques e Ações) ---
    'primary': '#0052CC',      # Azul corporativo (Atlassian Blue), usado para botões principais, links e elementos interativos.
    'primary_hover': '#0041A3', # Tom de azul mais escuro para o efeito "hover" (mouse sobre), dando feedback visual claro.

    # --- Cores de Texto ---
    'text': '#172B4D',          # Cinza-azulado muito escuro para o texto principal, garantindo excelente legibilidade e contraste.
    'text_secondary': '#6B778C', # Cinza médio para textos secundários, como legendas, placeholders ou informações de apoio.

    # --- Cores para Linhas de Tabelas e Listas ---
    'row_even': '#FFFFFF',      # Fundo branco para linhas pares, alinhado com a cor dos cartões.
    'row_odd': '#F7F7F7',       # Cinza muito claro para linhas ímpares, criando o efeito "zebrado" para facilitar a leitura.

    # --- Cores de Feedback de Erro ---
    'error_bg': '#FFECEC',      # Vermelho pastel ou rosa muito claro para o fundo de campos com erro, destacando-os suavemente.
    'error_text': '#C00000',    # Vermelho escuro e forte para o texto da mensagem de erro, garantindo visibilidade imediata.

    # --- Outros Elementos de UI ---
    'border': '#DFE1E6',        # Cinza claro para bordas, usado para separar elementos de forma sutil, sem sobrecarregar o visual.
    'shadow': '#BDBDBD',        # Cinza suave para sombras, adicionando profundidade e elevação aos elementos da interface.
}
# Tema escuro (única definição)
# Comentário descritivo da paleta de cores DARK_THEME

DARK_THEME = {
    # --- Cores de Fundo e Estrutura ---
    'bg': '#1E1E2F',          # Azul-escuro, quase preto, usado para o fundo principal da aplicação.
    'card': '#1E1E2F',        # Mesma cor do fundo, para elementos de cartão, mantendo uma aparência integrada.
    'input_bg': '#1E1E2F',    # Fundo para campos de entrada (inputs), consistente com o fundo geral.

    # --- Cores de Texto ---
    'text': '#E6EEF8',          # Um azul muito claro, quase branco, para texto principal, garantindo alta legibilidade.
    'text_secondary': '#C1C6D0', # Cinza-azulado claro para textos secundários, como placeholders ou legendas.

    # --- Cor Primária (Destaques e Ações) ---
    'primary': '#7AA2FF',      # Azul vibrante usado para botões principais, ícones e elementos em foco.
    'primary_hover': '#6A93E6', # Tom de azul um pouco mais escuro para o efeito "hover" (mouse sobre) em elementos primários.

    # --- Cores para Linhas de Tabelas e Listas ---
    'row_even': '#2A2A3A',      # Cinza-azulado escuro para linhas pares, criando um contraste sutil.
    'row_odd': '#252532',       # Tom ligeiramente mais escuro que o 'row_even' para linhas ímpares.

    # --- Cores de Feedback e Estado ---
    'success': '#4D4D5A',       # Cinza-azulado médio, usado para indicar sucesso ou confirmação.
    'error': '#42424E',         # Tom de cinza-azulado escuro para indicar erros ou ações destrutivas.
    'warning': '#1E1E2F',       # A cor de fundo é reutilizada para avisos, indicando uma área de atenção.
    'error_bg': '#1E1E2F',      # Fundo específico para campos com erro.
    'error_text': '#1E1E2F',    # Cor para o texto dentro de uma notificação de erro.

    # --- Outros Elementos de UI ---
    'border': '#3B3B3B',        # Preto puro para bordas, criando uma separação nítida.
    'shadow': '#000000',        # Preto puro para sombras, conferindo profundidade aos elementos.
    'link': '#58A6FF',          # Azul claro e brilhante para links, garantindo que se destaquem.
    'hover': '#000000',         # Cinza escuro (conhecido como "Black Olive" ou "Eclipse") para o efeito "hover" em elementos secundários.
}

# Fontes padrão
DEFAULT_FONTS = {
    'logo': ("Helvetica", 36),
    'title': ("Helvetica", 18, "bold"),
    'body': ("Helvetica", 10),
    'button': ("Helvetica", 10, "bold"),
    'icon_button': ("Helvetica", 12)
}

def load_notas_dat(path=None):
    if path is None:
        path = os.path.join('uploads','notas.dat')
    rec_fmt = '<i4f'  # int32 matricula, 4 floats: np1,np2,pim,media
    rec_size = struct.calcsize(rec_fmt)
    notas = {}
    try:
        with open(path, 'rb') as f:
            data = f.read()
            # If data size matches fixed-record format, parse as binary
            if len(data) % rec_size == 0 and len(data) > 0:
                for i in range(0, len(data), rec_size):
                    chunk = data[i:i+rec_size]
                    m, np1, np2, pim, media = struct.unpack(rec_fmt, chunk)
                    notas[str(m)] = (f"{np1:.1f}", f"{np2:.1f}", f"{pim:.1f}", f"{media:.1f}")
            else:
                # fallback: try parse as text lines (matricula|np1|np2|pim|media)
                try:
                    text = data.decode('utf-8', errors='ignore')
                    for line in text.splitlines():
                        if not line.strip():
                            continue
                        parts = line.strip().split('|')
                        if len(parts) >= 5:
                            notas[parts[0]] = (parts[1], parts[2], parts[3], parts[4])
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return notas


def save_presencas_dat(id_turma: str, date_str: str, presencas: list):
    """Save presences for a turma and date into uploads/presencas_turma_{id}.dat as binary records.

    Records: struct '<i10sB' -> matricula:int32, date:10s (DD/MM/YYYY), presente:uint8 (1/0)
    The function will merge/update entries for the same matricula+date and write atomically.
    """
    os.makedirs('uploads', exist_ok=True)
    path = os.path.join('uploads', f'presencas_turma_{id_turma}.dat')
    rec_fmt = '<i10sB'
    rec_size = struct.calcsize(rec_fmt)

    # Load existing into dict keyed by (matricula, date)
    existing = {}
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                data = f.read()
            if len(data) % rec_size == 0:
                for i in range(0, len(data), rec_size):
                    chunk = data[i:i+rec_size]
                    m, dbytes, pres = struct.unpack(rec_fmt, chunk)
                    d = dbytes.decode('ascii', errors='ignore').rstrip('\x00')
                    existing[(int(m), d)] = bool(pres)
        except Exception:
            existing = {}

    # Update with new presencas (list of dicts with matricula/presente)
    for p in presencas:
        try:
            m = int(p.get('matricula'))
            pres = bool(p.get('presente'))
            existing[(m, date_str)] = pres
        except Exception:
            continue

    # Write atomically
    tmp = path + '.tmp'
    with presenca_lock:
        try:
            with open(tmp, 'wb') as f:
                for (m, d), pres in existing.items():
                    dbytes = d.encode('ascii')[:10].ljust(10, b'\x00')
                    f.write(struct.pack(rec_fmt, int(m), dbytes, 1 if pres else 0))
            os.replace(tmp, path)
            return True
        except Exception:
            try:
                if os.path.exists(tmp): os.remove(tmp)
            except Exception:
                pass
            return False


def read_presencas_dat(id_turma: str):
    """Read all presence records for a turma from uploads/presencas_turma_{id}.dat.

    Returns a list of dicts: {'matricula': int, 'date': 'DD/MM/YYYY', 'presente': bool}
    """
    path = os.path.join('uploads', f'presencas_turma_{id_turma}.dat')
    rec_fmt = '<i10sB'
    rec_size = struct.calcsize(rec_fmt)
    result = []
    if not os.path.exists(path):
        return result
    try:
        with open(path, 'rb') as f:
            data = f.read()
        if len(data) % rec_size == 0:
            for i in range(0, len(data), rec_size):
                chunk = data[i:i+rec_size]
                m, dbytes, pres = struct.unpack(rec_fmt, chunk)
                d = dbytes.decode('ascii', errors='ignore').rstrip('\x00')
                result.append({'matricula': int(m), 'date': d, 'presente': bool(pres)})
    except Exception:
        return []
    return result


# Funções para gerenciamento de turnos de turmas
def load_turnos_turmas():
    """Carrega os turnos das turmas"""
    try:
        if os.path.exists('turnos_turmas.json'):
            with open('turnos_turmas.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('turnos', {})
        return {}
    except Exception:
        return {}

def save_turnos_turmas(turnos_data):
    """Salva os turnos das turmas"""
    try:
        with open('turnos_turmas.json', 'w', encoding='utf-8') as f:
            json.dump({'turnos': turnos_data}, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_turno_turma(id_turma):
    """Retorna o turno de uma turma específica (via servidor)"""
    return get_turno_server(id_turma)

def set_turno_turma(id_turma, turno):
    """Define o turno de uma turma (via servidor)"""
    return set_turno_server(id_turma, turno)

# Funções para gerenciamento de notas de exame
def load_exames():
    """Carrega as notas de exame"""
    try:
        if os.path.exists('exames.json'):
            with open('exames.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('exames', {})
        return {}
    except Exception:
        return {}

def save_exames(exames_data):
    """Salva as notas de exame"""
    try:
        with open('exames.json', 'w', encoding='utf-8') as f:
            json.dump({'exames': exames_data}, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_nota_exame_local(matricula, exames_dict):
    """Retorna a nota de exame de um aluno (versão local para uso no servidor)"""
    return exames_dict.get(str(matricula), 0.0)

def get_nota_exame(matricula):
    """Retorna a nota de exame de um aluno (via servidor)"""
    return get_nota_exame_server(matricula)

def set_nota_exame(matricula, nota):
    """Define a nota de exame de um aluno (via servidor)"""
    return set_nota_exame_server(matricula, nota)

# Funções para gerenciamento de provas
def load_provas():
    """Carrega as datas de provas do arquivo provas.json"""
    try:
        if os.path.exists('provas.json'):
            with open('provas.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('provas', {})
        return {}
    except Exception:
        return {}

def save_provas(provas_data):
    """Salva as datas de provas no arquivo provas.json"""
    try:
        with open('provas.json', 'w', encoding='utf-8') as f:
            json.dump({'provas': provas_data}, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_provas_turma(id_turma):
    """Retorna as datas de provas de uma turma específica (via servidor)"""
    return get_provas_turma_server(id_turma)

def set_provas_turma(id_turma, np1=None, np2=None, pim=None, exame=None):
    """Define as datas de provas para uma turma (via servidor)"""
    return set_provas_turma_server(id_turma, np1, np2, pim, exame)


def run_server():
    """Encapsula toda a lógica do servidor para ser executada em um processo."""
    
    # Match the C structures declared in database.h exactly to avoid memory/layout issues
    class Turma(ctypes.Structure):
        _fields_ = [("id", ctypes.c_int), ("nome_disciplina", ctypes.c_char * 100), ("nome_professor", ctypes.c_char * 100)]

    class Notas(ctypes.Structure):
        _fields_ = [("np1", ctypes.c_float), ("np2", ctypes.c_float), ("pim", ctypes.c_float), ("media", ctypes.c_float)]

    class Avaliacao(ctypes.Structure):
        _fields_ = [("nota", ctypes.c_float), ("comentario", ctypes.c_char * 500), ("data", ctypes.c_char * 11)]

    class Presenca(ctypes.Structure):
        _fields_ = [("data", ctypes.c_char * 11), ("presente", ctypes.c_int)]

    class Aluno(ctypes.Structure):
        _fields_ = [
            ("id_turma", ctypes.c_int),
            ("matricula", ctypes.c_int),
            ("nome", ctypes.c_char * 100),
            ("notas", Notas),
            ("avaliacoes", Avaliacao * 10),
            ("presencas", Presenca * 50),
            ("num_avaliacoes", ctypes.c_int),
            ("num_presencas", ctypes.c_int)
        ]

    try:
        lib_path = "./libdatabase.so" if os.name != 'nt' else "./database.dll"
        lib = ctypes.CDLL(lib_path)
        
        # As definições de 'salvar' devem esperar ponteiros
        lib.salvar_turma.argtypes = [ctypes.POINTER(Turma)]
        lib.salvar_aluno.argtypes = [ctypes.POINTER(Aluno)]

        lib.turma_existe.argtypes = [ctypes.c_int]; lib.turma_existe.restype = ctypes.c_int
        lib.matricula_existe.argtypes = [ctypes.c_int]; lib.matricula_existe.restype = ctypes.c_int
        lib.listar_turmas.argtypes = [ctypes.POINTER(Turma), ctypes.c_int]; lib.listar_turmas.restype = ctypes.c_int
        lib.listar_alunos_por_turma.argtypes = [ctypes.c_int, ctypes.POINTER(Aluno), ctypes.c_int]; lib.listar_alunos_por_turma.restype = ctypes.c_int
        lib.buscar_turma_por_id.argtypes = [ctypes.c_int, ctypes.POINTER(Turma)]; lib.buscar_turma_por_id.restype = ctypes.c_int
        lib.buscar_aluno_por_matricula.argtypes = [ctypes.c_int, ctypes.POINTER(Aluno)]; lib.buscar_aluno_por_matricula.restype = ctypes.c_int
        lib.atualizar_turma.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]; lib.atualizar_turma.restype = ctypes.c_int
        lib.atualizar_aluno.argtypes = [ctypes.c_int, ctypes.c_char_p]; lib.atualizar_aluno.restype = ctypes.c_int
        lib.deletar_turma.argtypes = [ctypes.c_int]; lib.deletar_turma.restype = ctypes.c_int
        lib.deletar_aluno.argtypes = [ctypes.c_int]; lib.deletar_aluno.restype = ctypes.c_int
        lib.alterar_id_turma.argtypes = [ctypes.c_int, ctypes.c_int]; lib.alterar_id_turma.restype = ctypes.c_int
        lib.alterar_matricula_aluno.argtypes = [ctypes.c_int, ctypes.c_int]; lib.alterar_matricula_aluno.restype = ctypes.c_int

    except (OSError, AttributeError) as e:
        print(f"[SERVIDOR-ERRO] Erro fatal ao carregar a biblioteca C: {e}")
        # If C lib cannot be loaded, continue; we'll fallback for some operations
        lib = None

    # Estruturas de dados do servidor
    server_data_folder = "server_data"
    os.makedirs(server_data_folder, exist_ok=True)
    
    users_file = os.path.join(server_data_folder, "users.json")
    provas_file = os.path.join(server_data_folder, "provas.json")
    turnos_file = os.path.join(server_data_folder, "turnos_turmas.json")
    exames_file = os.path.join(server_data_folder, "exames.json")
    anotacoes_file = os.path.join(server_data_folder, "anotacoes.json")
    
    def load_json_data(filename, default):
        """Carrega dados JSON do servidor"""
        try:
            if os.path.exists(filename):
                f = open(filename, 'r', encoding='utf-8')
                data = json.load(f)
                f.close()
                # Retorna o tipo correto baseado no default
                if isinstance(default, dict):
                    return data if isinstance(data, dict) else {}
                elif isinstance(default, list):
                    return data if isinstance(data, list) else []
                return data
            return default
        except Exception:
            return default
    
    
    def save_json_data(filename, data):
        """Salva dados JSON no servidor"""
        try:
            tmp = filename + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, filename)
            return True
        except Exception:
            return False
    
    def save_provas_data(provas_dict):
        """Salva dados de provas no formato correto"""
        return save_json_data(provas_file, {'provas': provas_dict})
    
    def save_turnos_data(turnos_dict):
        """Salva dados de turnos no formato correto"""
        return save_json_data(turnos_file, {'turnos': turnos_dict})
    
    def save_exames_data(exames_dict):
        """Salva dados de exames no formato correto"""
        return save_json_data(exames_file, {'exames': exames_dict})
    
    def save_anotacoes_data(anotacoes_list):
        """Salva dados de anotações"""
        return save_json_data(anotacoes_file, anotacoes_list)
    
    # Carregar dados iniciais do servidor
    server_users = load_json_data(users_file, {})
    server_provas_raw = load_json_data(provas_file, {})
    server_provas = server_provas_raw.get('provas', {}) if isinstance(server_provas_raw, dict) else {}
    server_turnos_raw = load_json_data(turnos_file, {})
    server_turnos = server_turnos_raw.get('turnos', {}) if isinstance(server_turnos_raw, dict) else {}
    server_exames_raw = load_json_data(exames_file, {})
    server_exames = server_exames_raw.get('exames', {}) if isinstance(server_exames_raw, dict) else {}
    server_anotacoes = load_json_data(anotacoes_file, [])

    # Inicializar UserDatabase com arquivo do servidor
    user_db = UserDatabase()
    user_db.filename = users_file  # Usar arquivo do servidor
    user_db.users = server_users  # Carregar usuários do servidor
    user_db.save_users()  # Salvar qualquer migração ou inicialização

    UPLOAD_FOLDER = "uploads"; os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_lock = threading.Lock()



    def handle_client(conn, addr):
        print(f"[SERVIDOR] Nova conexão de {addr}")
        try:
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data: break
                
                parts = data.split('|'); command = parts[0]
                response = "ERRO: Comando não reconhecido."

                if command == "ADD_TURMA":
                    with file_lock:
                        id_turma = int(parts[1])
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        else:
                            if lib.turma_existe(id_turma):
                                response = "ERRO: ID de turma já existe."
                            else:
                                turma = Turma(id=id_turma, nome_disciplina=parts[2].encode('utf-8'), nome_professor=parts[3].encode('utf-8'))
                                lib.salvar_turma(ctypes.byref(turma)); response = "SUCESSO: Turma adicionada."
                
                elif command == "LIST_TURMAS":
                    if not lib:
                        response = "Nenhuma turma cadastrada."
                    else:
                        TurmasArray = Turma * 100; turmas = TurmasArray()
                        # CORRIGIDO: Passa o array diretamente, sem byref()
                        count = lib.listar_turmas(turmas, 100)
                        if count == 0:
                            response = "Nenhuma turma cadastrada."
                        else:
                            response = ""
                            for i in range(count): response += f"ID: {turmas[i].id}, Disciplina: {turmas[i].nome_disciplina.decode('utf-8')}, Prof: {turmas[i].nome_professor.decode('utf-8')}\n"
                
                elif command == "ADD_ALUNO":
                    with file_lock:
                        id_turma, matricula = int(parts[1]), int(parts[2])
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        else:
                            if lib.matricula_existe(matricula):
                                response = "ERRO: Matrícula já cadastrada."
                            else:
                                # Create an Aluno instance; nested fields (notas/avaliacoes/presencas) will be zero-initialized
                                aluno = Aluno(id_turma=id_turma, matricula=matricula, nome=parts[3].encode('utf-8'))
                                lib.salvar_aluno(ctypes.byref(aluno)); response = "SUCESSO: Aluno adicionado."

                elif command == "LIST_ALUNOS_POR_TURMA":
                    id_turma = int(parts[1])
                    if not lib:
                        response = "Nenhum aluno encontrado para esta turma."
                    else:
                        AlunosArray = Aluno * 100; alunos = AlunosArray()
                        # CORRIGIDO: Passa o array diretamente, sem byref()
                        count = lib.listar_alunos_por_turma(id_turma, alunos, 100)
                        if count == 0:
                            response = "Nenhum aluno encontrado para esta turma."
                        else:
                            # Incluir notas, média E exame na resposta para o cliente exibir dados completos
                            # IMPORTANTE: Dados sempre vêm do servidor, garantindo sincronização
                            response = ""
                            for i in range(count):
                                try:
                                    # Buscar notas básicas do banco C
                                    np1 = float(alunos[i].notas.np1)
                                    np2 = float(alunos[i].notas.np2)
                                    pim = float(alunos[i].notas.pim)
                                    media = float(alunos[i].notas.media)
                                except Exception:
                                    np1 = np2 = pim = media = 0.0
                                
                                # Buscar nota de exame do arquivo do servidor (exames.json)
                                # Exame é armazenado separadamente pois não faz parte do banco C
                                exame = get_nota_exame_local(alunos[i].matricula, server_exames)
                                
                                # Retornar linha completa com TODAS as informações do aluno
                                response += (
                                    f"Matrícula: {alunos[i].matricula}, Nome: {alunos[i].nome.decode('utf-8')}, "
                                    f"NP1: {np1:.1f}, NP2: {np2:.1f}, PIM: {pim:.1f}, Média: {media:.1f}, Exame: {exame:.1f}\n"
                                )
                
                # ... (restante dos comandos, que já estavam corretos) ...
                elif command == "GET_TURMA_DATA":
                    id_turma = int(parts[1]); turma_encontrada = Turma()
                    if not lib:
                        response = "ERRO: Biblioteca C não carregada."
                    elif lib.buscar_turma_por_id(id_turma, ctypes.byref(turma_encontrada)):
                        response = f"{turma_encontrada.nome_disciplina.decode('utf-8')}|{turma_encontrada.nome_professor.decode('utf-8')}"
                    else:
                        response = "ERRO: Turma não encontrada."

                elif command == "UPDATE_TURMA":
                    with file_lock:
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        elif lib.atualizar_turma(int(parts[1]), parts[2].encode('utf-8'), parts[3].encode('utf-8')):
                            response = "SUCESSO: Dados da turma atualizados."
                        else:
                            response = "ERRO: Falha ao atualizar."

                elif command == "DELETE_TURMA":
                    with file_lock:
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        elif lib.deletar_turma(int(parts[1])):
                            response = "SUCESSO: Turma e alunos associados foram excluídos."
                        else:
                            response = "ERRO: Turma não encontrada."

                elif command == "CHANGE_TURMA_ID":
                    with file_lock:
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        else:
                            ret_code = lib.alterar_id_turma(int(parts[1]), int(parts[2]))
                            if ret_code == 1:
                                response = "SUCESSO: ID da turma alterado."
                            elif ret_code == -1:
                                response = f"ERRO: O novo ID '{parts[2]}' já está em uso."
                            else:
                                response = f"ERRO: Turma com ID antigo não encontrada."

                elif command == "GET_ALUNO_DATA":
                    matricula = int(parts[1]); aluno_encontrado = Aluno()
                    if not lib:
                        response = "ERRO: Biblioteca C não carregada."
                    elif lib.buscar_aluno_por_matricula(matricula, ctypes.byref(aluno_encontrado)):
                        response = f"{aluno_encontrado.nome.decode('utf-8')}"
                    else:
                        response = "ERRO: Aluno não encontrado."

                elif command == "UPDATE_ALUNO":
                    with file_lock:
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        elif lib.atualizar_aluno(int(parts[1]), parts[2].encode('utf-8')):
                            response = "SUCESSO: Dados do aluno atualizados."
                        else:
                            response = "ERRO: Falha ao atualizar."
                
                elif command == "DELETE_ALUNO":
                    with file_lock:
                        if lib and hasattr(lib, 'deletar_aluno'):
                            if lib.deletar_aluno(int(parts[1])):
                                response = "SUCESSO: Aluno excluído."
                            else:
                                response = "ERRO: Falha ao excluir aluno (matrícula não encontrada)."
                        else:
                            # Se a biblioteca C ou a função não existir, a operação não é suportada.
                            response = "ERRO: Funcionalidade não disponível (biblioteca C ausente)."
                
                elif command == "CHANGE_ALUNO_ID":
                     with file_lock:
                        if not lib:
                            response = "ERRO: Biblioteca C não carregada."
                        else:
                            ret_code = lib.alterar_matricula_aluno(int(parts[1]), int(parts[2]))
                            if ret_code == 1:
                                response = "SUCESSO: Matrícula alterada."
                            elif ret_code == -1:
                                response = f"ERRO: A nova matrícula '{parts[2]}' já existe."
                            else:
                                response = f"ERRO: Aluno com matrícula antiga não encontrado."

                elif command == "UPDATE_NOTAS":
                    # Client sends: UPDATE_NOTAS|matricula|np1|np2|pim|media
                    try:
                        matricula = int(parts[1])
                        np1, np2, pim, media = float(parts[2]), float(parts[3]), float(parts[4]), float(parts[5])
                        
                        # Usar a função salvar_notas da biblioteca C
                        if lib and hasattr(lib, 'salvar_notas'):
                            # Criar estrutura Notas
                            notas = Notas()
                            notas.np1 = ctypes.c_float(np1)
                            notas.np2 = ctypes.c_float(np2)
                            notas.pim = ctypes.c_float(pim)
                            notas.media = ctypes.c_float(media)
                            
                            # Chamar salvar_notas
                            lib.salvar_notas.argtypes = [ctypes.c_int, ctypes.POINTER(Notas)]
                            lib.salvar_notas.restype = ctypes.c_int
                            
                            if lib.salvar_notas(matricula, ctypes.byref(notas)):
                                response = "SUCESSO: Notas atualizadas."
                            else:
                                response = "ERRO: Falha ao atualizar notas via C lib."
                        else:
                            # Fallback persistence: store in binary .dat (struct '<i4f')
                            notas_path = os.path.join(UPLOAD_FOLDER, 'notas.dat')
                            rec_fmt = '<i4f'  # matricula (int32), np1,np2,pim,media as floats
                            try:
                                # Load existing records into a dict
                                notas_db = {}
                                if os.path.exists(notas_path):
                                    try:
                                        with open(notas_path, 'rb') as bf:
                                            data = bf.read()
                                        rec_size = struct.calcsize(rec_fmt)
                                        if len(data) % rec_size == 0:
                                            for i in range(0, len(data), rec_size):
                                                chunk = data[i:i+rec_size]
                                                m, a, b, c, d = struct.unpack(rec_fmt, chunk)
                                                notas_db[str(m)] = (a, b, c, d)
                                    except Exception:
                                        # ignore parse problems and continue with empty db
                                        notas_db = {}

                                # update current matricula
                                notas_db[str(matricula)] = (np1, np2, pim, media)

                                # write back atomically under lock
                                with file_lock:
                                    tmp_path = notas_path + '.tmp'
                                    with open(tmp_path, 'wb') as bf:
                                        for mkey, vals in notas_db.items():
                                            try:
                                                m_int = int(mkey)
                                                bf.write(struct.pack(rec_fmt, m_int, float(vals[0]), float(vals[1]), float(vals[2]), float(vals[3])))
                                            except Exception:
                                                # skip malformed keys
                                                continue
                                    os.replace(tmp_path, notas_path)

                                response = "SUCESSO: Notas salvas (fallback)."
                            except Exception as e:
                                response = f"ERRO: Falha ao salvar notas: {e}"
                    except Exception as e:
                        response = f"ERRO: Formato inválido para UPDATE_NOTAS: {e}"

                elif command == "UPLOAD_FILE":
                    id_turma, filename, filesize = parts[1], parts[2], int(parts[3])
                    turma_folder = os.path.join(UPLOAD_FOLDER, f"turma_{id_turma}"); os.makedirs(turma_folder, exist_ok=True)
                    filepath = os.path.join(turma_folder, f"{int(time.time())}_{os.path.basename(filename)}")
                    conn.sendall(b"OK_SEND_DATA")
                    with open(filepath, "wb") as f:
                        bytes_received = 0
                        while bytes_received < filesize:
                            chunk = conn.recv(4096)
                            if not chunk: break
                            f.write(chunk); bytes_received += len(chunk)
                    response = "SUCESSO: Arquivo recebido."

                elif command == "LIST_FILES":
                    id_turma = parts[1]
                    turma_folder = os.path.join(UPLOAD_FOLDER, f"turma_{id_turma}")
                    if not os.path.exists(turma_folder):
                        response = "Nenhuma atividade encontrada para esta turma."
                    else:
                        files = os.listdir(turma_folder)
                        if not files:
                            response = "Nenhuma atividade encontrada para esta turma."
                        else:
                            response = "\n".join(files)

                elif command == "DOWNLOAD_FILE":
                    id_turma, filename = parts[1], parts[2]
                    filepath = os.path.join(UPLOAD_FOLDER, f"turma_{id_turma}", filename)
                    if not os.path.exists(filepath):
                        response = "ERRO: Arquivo não encontrado."
                    else:
                        filesize = os.path.getsize(filepath)
                        conn.sendall(f"OK_DOWNLOAD|{filesize}".encode('utf-8'))
                        with open(filepath, "rb") as f:
                            while (chunk := f.read(4096)):
                                conn.sendall(chunk)
                        return  # Skip sending additional response
                
                # Comandos de gerenciamento de usuários
                elif command == "LOGIN":
                    username, password = parts[1], parts[2] if len(parts) > 2 else ""
                    with file_lock:
                        if user_db.verify_user(username, password):
                            role = user_db.get_role(username)
                            response = f"SUCESSO|{role}"
                        else:
                            response = "ERRO: Credenciais inválidas"
                
                elif command == "CREATE_USER":
                    username, password, role = parts[1], parts[2] if len(parts) > 2 else "", parts[3] if len(parts) > 3 else "professor"
                    email = parts[4] if len(parts) > 4 else None
                    with file_lock:
                        success, msg = user_db.add_user(username, password, role, email)
                        response = f"SUCESSO: {msg}" if success else f"ERRO: {msg}"
                
                elif command == "GET_USER_DATA":
                    username = parts[1]
                    with file_lock:
                        user_data = user_db.get_user_data(username)
                        if user_data:
                            import json
                            # Não enviar a senha
                            safe_data = {k: v for k, v in user_data.items() if k != 'password' and k != 'secret_answer'}
                            response = "SUCESSO|" + json.dumps(safe_data)
                        else:
                            response = "ERRO: Usuário não encontrado"
                
                elif command == "UPDATE_USER":
                    username = parts[1]
                    updates_json = parts[2] if len(parts) > 2 else "{}"
                    import json
                    try:
                        updates = json.loads(updates_json)
                        with file_lock:
                            if username in user_db.users:
                                user_db.users[username].update(updates)
                                user_db.save_users()
                                response = "SUCESSO: Dados atualizados"
                            else:
                                response = "ERRO: Usuário não encontrado"
                    except Exception as e:
                        response = f"ERRO: {str(e)}"
                
                elif command == "UPDATE_PASSWORD":
                    username, old_password, new_password = parts[1], parts[2], parts[3]
                    with file_lock:
                        success, msg = user_db.update_password(username, old_password, new_password)
                        response = f"SUCESSO: {msg}" if success else f"ERRO: {msg}"
                
                elif command == "SET_PASSWORD":
                    username, new_password = parts[1], parts[2]
                    with file_lock:
                        success, msg = user_db.set_password(username, new_password)
                        response = f"SUCESSO: {msg}" if success else f"ERRO: {msg}"
                
                elif command == "LIST_USERS":
                    with file_lock:
                        import json
                        safe_users = {}
                        for uname, udata in user_db.users.items():
                            safe_users[uname] = {k: v for k, v in udata.items() if k != 'password' and k != 'secret_answer'}
                        response = json.dumps(safe_users, ensure_ascii=False)
                
                elif command == "DELETE_USER":
                    username = parts[1]
                    with file_lock:
                        if username in user_db.users:
                            del user_db.users[username]
                            user_db.save_users()
                            response = "SUCESSO: Usuário removido"
                        else:
                            response = "ERRO: Usuário não encontrado"
                
                elif command == "APPROVE_USER":
                    username = parts[1]
                    with file_lock:
                        if username in user_db.users:
                            user_db.users[username]['status'] = 'approved'
                            user_db.save_users()
                            response = "SUCESSO: Usuário aprovado"
                        else:
                            response = "ERRO: Usuário não encontrado"
                
                # Comandos para gerenciamento de provas
                elif command == "GET_PROVAS":
                    with file_lock:
                        import json
                        response = json.dumps(server_provas, ensure_ascii=False)
                
                elif command == "GET_PROVAS_TURMA":
                    id_turma = str(parts[1])
                    with file_lock:
                        if id_turma in server_provas:
                            import json
                            response = json.dumps(server_provas[id_turma], ensure_ascii=False)
                        else:
                            response = json.dumps({'NP1': None, 'NP2': None, 'PIM': None, 'Exame': None}, ensure_ascii=False)
                
                elif command == "SET_PROVAS_TURMA":
                    id_turma = str(parts[1])
                    np1 = parts[2] if len(parts) > 2 and parts[2] else None
                    np2 = parts[3] if len(parts) > 3 and parts[3] else None
                    pim = parts[4] if len(parts) > 4 and parts[4] else None
                    exame = parts[5] if len(parts) > 5 and parts[5] else None
                    with file_lock:
                        if id_turma not in server_provas:
                            server_provas[id_turma] = {}
                        if np1 is not None:
                            server_provas[id_turma]['NP1'] = np1
                        if np2 is not None:
                            server_provas[id_turma]['NP2'] = np2
                        if pim is not None:
                            server_provas[id_turma]['PIM'] = pim
                        if exame is not None:
                            server_provas[id_turma]['Exame'] = exame
                        if save_provas_data(server_provas):
                            response = "SUCESSO: Datas de provas atualizadas"
                        else:
                            response = "ERRO: Falha ao salvar dados"
                
                # Comandos para gerenciamento de turnos
                elif command == "GET_TURNO":
                    id_turma = str(parts[1])
                    with file_lock:
                        response = server_turnos.get(id_turma, 'matutino')
                
                elif command == "SET_TURNO":
                    id_turma = str(parts[1])
                    turno = parts[2]
                    with file_lock:
                        server_turnos[id_turma] = turno
                        if save_turnos_data(server_turnos):
                            response = "SUCESSO: Turno atualizado"
                        else:
                            response = "ERRO: Falha ao salvar turno"
                
                # Comandos para gerenciamento de exames
                elif command == "GET_EXAME":
                    matricula = str(parts[1])
                    with file_lock:
                        nota = server_exames.get(matricula, 0.0)
                        response = str(nota)
                
                elif command == "SET_EXAME":
                    matricula = str(parts[1])
                    nota = float(parts[2])
                    with file_lock:
                        server_exames[matricula] = nota
                        if save_exames_data(server_exames):
                            response = "SUCESSO: Nota de exame atualizada"
                        else:
                            response = "ERRO: Falha ao salvar nota"
                
                elif command == "GET_ALL_EXAMES":
                    with file_lock:
                        import json
                        response = json.dumps(server_exames, ensure_ascii=False)
                
                # Comandos para gerenciamento de anotações
                elif command == "GET_ANOTACOES":
                    with file_lock:
                        import json
                        response = json.dumps(server_anotacoes, ensure_ascii=False)
                
                elif command == "ADD_ANOTACAO":
                    import json
                    import datetime
                    anotacao_json = parts[1] if len(parts) > 1 else "{}"
                    try:
                        anotacao = json.loads(anotacao_json)
                        titulo = anotacao.get('titulo', '')
                        conteudo = anotacao.get('conteudo', '')
                        with file_lock:
                            # Verificar se já existe anotação com mesmo título
                            exists = False
                            for a in server_anotacoes:
                                if a.get('titulo') == titulo:
                                    exists = True
                                    break
                            
                            if exists:
                                response = "ERRO: Anotação com este título já existe"
                            else:
                                nova_anotacao = {
                                    'titulo': titulo,
                                    'conteudo': conteudo,
                                    'data': datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                                }
                                server_anotacoes.append(nova_anotacao)
                                if save_anotacoes_data(server_anotacoes):
                                    response = "SUCESSO: Anotação adicionada"
                                else:
                                    response = "ERRO: Falha ao salvar anotação"
                    except Exception as e:
                        response = f"ERRO: {str(e)}"
                
                elif command == "UPDATE_ANOTACAO":
                    import json
                    titulo_antigo = parts[1] if len(parts) > 1 else ""
                    anotacao_json = parts[2] if len(parts) > 2 else "{}"
                    try:
                        anotacao = json.loads(anotacao_json)
                        with file_lock:
                            encontrado = False
                            for a in server_anotacoes:
                                if a.get('titulo') == titulo_antigo:
                                    a.update(anotacao)
                                    encontrado = True
                                    break
                            
                            if encontrado and save_anotacoes_data(server_anotacoes):
                                response = "SUCESSO: Anotação atualizada"
                            else:
                                response = "ERRO: Anotação não encontrada"
                    except Exception as e:
                        response = f"ERRO: {str(e)}"
                
                elif command == "DELETE_ANOTACAO":
                    titulo = parts[1] if len(parts) > 1 else ""
                    with file_lock:
                        server_anotacoes = [a for a in server_anotacoes if a.get('titulo') != titulo]
                        if save_anotacoes_data(server_anotacoes):
                            response = "SUCESSO: Anotação removida"
                        else:
                            response = "ERRO: Falha ao remover anotação"

                conn.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"[SERVIDOR-ERRO] Erro com {addr}: {e}")
        finally:
            print(f"[SERVIDOR] Conexão com {addr} encerrada."); conn.close()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM); server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 65432)); server.listen()
    print("[SERVIDOR] Escutando em 0.0.0.0:65432")
    while True:
        conn, addr = server.accept(); threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

HOST, PORT = '127.0.0.1', 65432
#Alterar o host para o do servidor
# ==============================================================================
# FUNÇÕES AUXILIARES PARA COMUNICAÇÃO COM O SERVIDOR VIA SOCKET
# ==============================================================================

def send_server_command(command, buffer=8192):
    """Envia um comando ao servidor e retorna a resposta"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(command.encode('utf-8'))
            return s.recv(buffer).decode('utf-8')
    except Exception as e:
        print(f"[CLIENTE-ERRO] Erro ao conectar ao servidor: {e}")
        return None

# Funções auxiliares para operações de provas, turnos, exames e anotações via servidor
def get_provas_server():
    """Obtém todas as provas do servidor"""
    response = send_server_command("GET_PROVAS")
    if response:
        try:
            import json
            return json.loads(response)
        except:
            return {}
    return {}

def get_provas_turma_server(id_turma):
    """Obtém as provas de uma turma específica"""
    response = send_server_command(f"GET_PROVAS_TURMA|{id_turma}")
    if response:
        try:
            import json
            return json.loads(response)
        except:
            return {'NP1': None, 'NP2': None, 'PIM': None, 'Exame': None}
    return {'NP1': None, 'NP2': None, 'PIM': None, 'Exame': None}

def set_provas_turma_server(id_turma, np1=None, np2=None, pim=None, exame=None):
    """Define as datas de provas para uma turma"""
    parts = [f"SET_PROVAS_TURMA|{id_turma}"]
    if np1:
        parts.append(str(np1))
    else:
        parts.append("")
    if np2:
        parts.append(str(np2))
    else:
        parts.append("")
    if pim:
        parts.append(str(pim))
    else:
        parts.append("")
    if exame:
        parts.append(str(exame))
    else:
        parts.append("")
    
    response = send_server_command("|".join(parts))
    return response and "SUCESSO" in response

def get_turno_server(id_turma):
    """Obtém o turno de uma turma"""
    response = send_server_command(f"GET_TURNO|{id_turma}")
    if response and not response.startswith("ERRO"):
        return response
    return 'matutino'

def set_turno_server(id_turma, turno):
    """Define o turno de uma turma"""
    response = send_server_command(f"SET_TURNO|{id_turma}|{turno}")
    return response and "SUCESSO" in response

def get_nota_exame_server(matricula):
    """Obtém a nota de exame de um aluno"""
    response = send_server_command(f"GET_EXAME|{matricula}")
    if response and not response.startswith("ERRO"):
        try:
            return float(response)
        except:
            return 0.0
    return 0.0

def set_nota_exame_server(matricula, nota):
    """Define a nota de exame de um aluno"""
    response = send_server_command(f"SET_EXAME|{matricula}|{nota}")
    return response and "SUCESSO" in response

def get_all_exames_server():
    """Obtém todas as notas de exame"""
    response = send_server_command("GET_ALL_EXAMES")
    if response:
        try:
            import json
            return json.loads(response)
        except:
            return {}
    return {}

def get_anotacoes_server():
    """Obtém todas as anotações do servidor"""
    response = send_server_command("GET_ANOTACOES")
    if response:
        try:
            import json
            return json.loads(response)
        except:
            return []
    return []

def add_anotacao_server(titulo, conteudo):
    """Adiciona uma nova anotação"""
    import json
    anotacao = {'titulo': titulo, 'conteudo': conteudo}
    anotacao_json = json.dumps(anotacao)
    response = send_server_command(f"ADD_ANOTACAO|{anotacao_json}")
    return response and "SUCESSO" in response

def update_anotacao_server(titulo_antigo, titulo, conteudo):
    """Atualiza uma anotação existente"""
    import json
    anotacao = {'titulo': titulo, 'conteudo': conteudo}
    anotacao_json = json.dumps(anotacao)
    response = send_server_command(f"UPDATE_ANOTACAO|{titulo_antigo}|{anotacao_json}")
    return response and "SUCESSO" in response

def delete_anotacao_server(titulo):
    """Remove uma anotação"""
    response = send_server_command(f"DELETE_ANOTACAO|{titulo}")
    return response and "SUCESSO" in response

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title=None, fields=None, initial_values=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.fields = fields or []
        self.initial_values = initial_values or {}
        self.result = None
        
        # Configure background first
        try:
            self.configure(bg=getattr(parent, 'colors', {}).get('card', '#FFFFFF'))
        except Exception:
            pass
            
        body = ttk.Frame(self)
        self.entries = {}
        # Ensure dialog has application icon if available
        try:
            _set_window_icon(self)
        except Exception:
            try:
                self.iconbitmap("img/icone.ico")
            except Exception:
                pass
        # Try to apply popup theme from parent if available
        try:
            _apply_popup_theme(self, getattr(parent, 'colors', {}), getattr(parent, 'fonts', {}), getattr(parent, 'style', None))
        except Exception:
            pass
        for i,f in enumerate(self.fields):
            ttk.Label(body,text=f"{f}:",width=20).grid(row=i,column=0,sticky="w",padx=5,pady=3)
            e=ttk.Entry(body,width=35); e.grid(row=i,column=1,sticky="ew",padx=5,pady=3)
            if f in self.initial_values: e.insert(0,self.initial_values[f])
            self.entries[f]=e
        if self.fields: self.entries[self.fields[0]].focus_set(); body.pack(padx=10,pady=10); box=ttk.Frame(self); ttk.Button(box,text="OK",command=self._ok).pack(side=tk.LEFT,padx=10,pady=5);
        ttk.Button(box,text="Cancelar",command=self._cancel).pack(side=tk.RIGHT,padx=10,pady=5); box.pack(); self.bind("<Return>",lambda e: self._ok()); self.bind("<Escape>",lambda e: self._cancel());
        self.protocol("WM_DELETE_WINDOW",self._cancel); self.grab_set(); self.wait_window(self)
    def _ok(self): self.result={f: e.get() for f,e in self.entries.items()}; self.destroy()
    def _cancel(self): self.result=None; self.destroy()

def custom_messagebox(parent, title, message, type_="info", buttons="ok"):
    """
    Dialog customizado que respeita o tema dark/light
    
    Args:
        parent: Janela pai do dialog
        title: Título do dialog
        message: Mensagem a ser exibida
        type_: Tipo do dialog ('info', 'warning', 'error', 'question')
        buttons: Botões a exibir ('ok', 'okcancel', 'yesno')
    
    Returns:
        True/False para yesno, True para ok, None para cancel
    """
    # Criar dialog como filho da janela pai
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    dialog.resizable(False, False)
    
    # Obter cores e fontes do tema atual da janela pai
    colors = getattr(parent, 'colors', {})
    fonts = getattr(parent, 'fonts', {})
    
    # Se não houver cores no parent, usar tema padrão baseado em dark_mode
    if not colors and hasattr(parent, 'dark_mode'):
        colors = DARK_THEME if parent.dark_mode else LIGHT_THEME
    elif not colors:
        colors = LIGHT_THEME
    
    # Aplicar tema ao dialog
    try:
        _apply_popup_theme(dialog, colors, fonts, getattr(parent, 'style', None))
    except Exception:
        pass
    
    # Definir ícone da aplicação
    _set_window_icon(dialog)
    
    # Ícones por tipo
    icons = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'question': '❓'
    }
    
    # Cores por tipo
    icon_colors = {
        'info': '#2196F3',     # Azul
        'warning': '#FF9800',  # Laranja
        'error': '#F44336',    # Vermelho
        'question': '#9C27B0'  # Roxo
    }
    
    # Frame principal
    main_frame = tk.Frame(dialog, bg=colors.get('card', '#FFFFFF'))
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Ícone e mensagem
    icon_frame = tk.Frame(main_frame, bg=colors.get('card', '#FFFFFF'))
    icon_frame.pack(fill=tk.X, pady=(0, 15))
    
    icon_label = tk.Label(icon_frame, text=icons.get(type_, 'ℹ️'), 
                         font=('Arial', 32), 
                         bg=colors.get('card', '#FFFFFF'),
                         fg=icon_colors.get(type_, '#2196F3'))
    icon_label.pack(side=tk.LEFT, padx=(0, 15))
    
    message_label = tk.Label(icon_frame, text=message, 
                            font=('Arial', 11), 
                            bg=colors.get('card', '#FFFFFF'),
                            fg=colors.get('text', '#000000'),
                            wraplength=350, justify=tk.LEFT)
    message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Frame de botões
    button_frame = tk.Frame(main_frame, bg=colors.get('card', '#FFFFFF'))
    button_frame.pack(fill=tk.X)
    
    result = {'value': None}
    
    def on_yes_ok():
        result['value'] = True
        dialog.destroy()
    
    def on_no_cancel():
        result['value'] = False
        dialog.destroy()
    
    # Criar botões baseado no tipo
    if buttons == "yesno":
        btn_yes = tk.Button(button_frame, text="Sim", 
                           command=on_yes_ok,
                           bg=colors.get('primary', '#0052CC'),
                           fg='white',
                           font=('Arial', 10, 'bold'),
                           relief='flat',
                           cursor='hand2',
                           padx=20, pady=8)
        btn_yes.pack(side=tk.LEFT, padx=5)
        
        btn_no = tk.Button(button_frame, text="Não", 
                          command=on_no_cancel,
                          bg=colors.get('border', '#DFE1E6'),
                          fg=colors.get('text', '#000000'),
                          font=('Arial', 10),
                          relief='flat',
                          cursor='hand2',
                          padx=20, pady=8)
        btn_no.pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: on_yes_ok())
        btn_yes.focus_set()
        
    elif buttons == "okcancel":
        btn_ok = tk.Button(button_frame, text="OK", 
                          command=on_yes_ok,
                          bg=colors.get('primary', '#0052CC'),
                          fg='white',
                          font=('Arial', 10, 'bold'),
                          relief='flat',
                          cursor='hand2',
                          padx=20, pady=8)
        btn_ok.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = tk.Button(button_frame, text="Cancelar", 
                              command=on_no_cancel,
                              bg=colors.get('border', '#DFE1E6'),
                              fg=colors.get('text', '#000000'),
                              font=('Arial', 10),
                              relief='flat',
                              cursor='hand2',
                              padx=20, pady=8)
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        dialog.bind('<Return>', lambda e: on_yes_ok())
        btn_ok.focus_set()
        
    else:  # ok
        btn_ok = tk.Button(button_frame, text="OK", 
                          command=on_yes_ok,
                          bg=colors.get('primary', '#0052CC'),
                          fg='white',
                          font=('Arial', 10, 'bold'),
                          relief='flat',
                          cursor='hand2',
                          padx=30, pady=8)
        btn_ok.pack(padx=5)
        
        dialog.bind('<Return>', lambda e: on_yes_ok())
        btn_ok.focus_set()
    
    dialog.bind('<Escape>', lambda e: on_no_cancel())
    
    # Centralizar dialog na tela
    _center_window(dialog)
    
    # Aguardar o usuário fechar o dialog antes de retornar
    dialog.wait_window()
    return result['value']

# ==============================================================================
# FUNÇÕES AUXILIARES PARA DIALOGS CUSTOMIZADOS
# ==============================================================================

def show_info(parent, title, message):
    """
    Mostra dialog de informação com tema dark/light
    Usa o custom_messagebox para respeitar o tema atual
    """
    return custom_messagebox(parent, title, message, type_="info", buttons="ok")

def show_warning(parent, title, message):
    """
    Mostra dialog de aviso com tema dark/light
    Usa o custom_messagebox para respeitar o tema atual
    """
    return custom_messagebox(parent, title, message, type_="warning", buttons="ok")

def show_error(parent, title, message):
    """
    Mostra dialog de erro com tema dark/light
    Usa o custom_messagebox para respeitar o tema atual
    """
    return custom_messagebox(parent, title, message, type_="error", buttons="ok")

def ask_yesno(parent, title, message):
    """
    Mostra dialog de pergunta sim/não com tema dark/light
    Usa o custom_messagebox para respeitar o tema atual
    """
    return custom_messagebox(parent, title, message, type_="question", buttons="yesno")

# ==============================================================================
# FUNÇÕES AUXILIARES PARA CONFIGURAÇÃO DE JANELAS
# ==============================================================================

def _set_window_icon(win):
    """
    Define o ícone da aplicação para uma janela
    Usa icone.ico para Windows (melhor compatibilidade)
    """
    try:
        if win is None: return
        # Preferir .ico para Windows
        try:
            win.iconbitmap("img/icone.ico")
        except Exception:
            # Melhor esforço para outros formatos ou plataformas (ignora falhas)
            pass
    except Exception:
        pass

def _center_window(window):
    """
    Centraliza uma janela na tela
    Calcula a posição baseada no tamanho da janela e da tela
    """
    try:
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')
    except Exception:
        pass

def _setup_dialog_shortcuts(dialog, ok_button=None, cancel_callback=None, ok_callback=None):
    """
    Configura atalhos de teclado padrão para diálogos
    
    Args:
        dialog: Janela do diálogo a configurar
        ok_button: Botão principal (opcional) - será invocado com Enter
        cancel_callback: Função a chamar quando cancelar (opcional)
        ok_callback: Função a chamar quando confirmar (opcional)
    
    Comportamento:
        - Pressionar Enter: Executa ação principal (invoca ok_button ou ok_callback)
        - Pressionar Escape: Cancela/fecha o diálogo (chama cancel_callback ou destroy)
        - Define foco no botão principal após 100ms
    """
    try:
        # Configurar tecla Escape para fechar/cancelar
        if cancel_callback:
            dialog.bind('<Escape>', lambda e: cancel_callback())
        else:
            dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # Configurar tecla Enter para ação principal
        if ok_callback:
            dialog.bind('<Return>', lambda e: ok_callback())
        elif ok_button:
            dialog.bind('<Return>', lambda e: ok_button.invoke())
        
        # Definir foco no botão principal após carregar (evita conflitos)
        if ok_button:
            dialog.after(100, lambda: ok_button.focus_set())
    except Exception:
        pass

def _enable_canvas_scroll(canvas, scrollable_frame=None):
    """
    Habilita scroll com o mousewheel em um canvas de popup
    
    Args:
        canvas: Canvas que terá o scroll habilitado
        scrollable_frame: Frame dentro do canvas (opcional) - se fornecido, bind será aplicado recursivamente
    
    Comportamento:
        - Vincula evento <MouseWheel> ao canvas
        - Aplica bind recursivamente a todos os widgets filhos (se scrollable_frame fornecido)
        - Retorna "break" para prevenir propagação do evento (evita conflitos com outros scrolls)
        - Atualiza bindings automaticamente quando o conteúdo mudar
    """
    def on_mousewheel(event):
        """Handler para evento de scroll do mouse"""
        try:
            # Scroll vertical: -1 para inverter direção natural
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Impede propagação do evento para widgets pai
        except:
            pass
    
    # Vincular evento de mousewheel ao canvas
    canvas.bind("<MouseWheel>", on_mousewheel)
    
    if scrollable_frame:
        # Aplicar bind recursivamente para todos os filhos do frame
        def bind_children(widget):
            """Aplica bind de mousewheel recursivamente a um widget e seus filhos"""
            try:
                widget.bind("<MouseWheel>", on_mousewheel)
                for child in widget.winfo_children():
                    bind_children(child)
            except:
                pass
        
        bind_children(scrollable_frame)
        
        # Rebind quando o conteúdo mudar (novos widgets adicionados)
        def on_frame_configure(event):
            bind_children(scrollable_frame)
        
        scrollable_frame.bind("<Configure>", on_frame_configure, add="+")


def _apply_popup_theme(win, colors, fonts, style_obj=None):
    """
    Aplica tema dark/light de forma conservadora a um Toplevel e seus filhos
    
    Args:
        win: Janela Toplevel a ser tematizada
        colors: Dicionário de cores do tema (deve conter: 'card', 'text', 'input_bg', 'primary', etc)
        fonts: Dicionário de fontes (opcional)
        style_obj: Objeto ttk.Style (opcional) - se fornecido, configura estilos ttk
    
    Comportamento:
        - Aplica cores de fundo/texto recursivamente a todos os widgets tk
        - Configura estilos ttk para evitar partes brancas no modo dark
        - Limite de profundidade recursiva de 10 níveis para segurança
        - Falhas são silenciadas para não quebrar a aplicação
    
    Uso:
        _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self,'style',None))
    """
    try:
        win.configure(bg=colors.get('card', '#FFFFFF'))
    except Exception:
        pass

    def apply_to_widget(w, depth=0):
        if depth > 10:  # Limite de segurança
            return
        try:
            # tk widgets
            if isinstance(w, tk.Frame) or isinstance(w, tk.LabelFrame):
                w.configure(bg=colors.get('card'))
            elif isinstance(w, tk.Label):
                w.configure(bg=colors.get('card'), fg=colors.get('text'))
            elif isinstance(w, tk.Button) or isinstance(w, tk.Checkbutton) or isinstance(w, tk.Radiobutton):
                try:
                    w.configure(bg=colors.get('card'), fg=colors.get('text'), activebackground=colors.get('primary'))
                except Exception:
                    pass
            elif isinstance(w, tk.Entry) or isinstance(w, tk.Text):
                try:
                    w.configure(bg=colors.get('input_bg'), fg=colors.get('text'), insertbackground=colors.get('text'))
                except Exception:
                    pass
            
            # Aplicar recursivamente a todos os filhos
            try:
                for child in list(w.winfo_children()):
                    apply_to_widget(child, depth + 1)
            except Exception:
                pass
        except Exception:
            pass

    try:
        for child in list(win.winfo_children()):
            apply_to_widget(child)
    except Exception:
        pass

    # Try to nudge ttk styles for popup widgets
    # NÃO sobrescrever estilos globais - apenas configurar estilos específicos de popup se necessário
    try:
        if style_obj:
            # Apenas garantir que TNotebook e TNotebook.Tab estejam bem configurados para popups
            # Mas NÃO sobrescrever TLabel, TFrame, etc que afetam a aplicação toda
            style_obj.configure('TNotebook', background=colors.get('card'), bordercolor=colors.get('border'))
            style_obj.configure('TNotebook.Tab', 
                               background=colors.get('border'), 
                               foreground=colors.get('text'),
                               padding=[8, 3])
            style_obj.map('TNotebook.Tab', 
                         background=[('selected', colors.get('primary'))],
                         foreground=[('selected', colors.get('card'))])
    except Exception:
        pass

def _apply_messagebox_theme(colors, fonts):
    """Aplica tema customizado aos messageboxes do tkinter"""
    try:
        # Configurar cores para messageboxes
        import tkinter.messagebox as mb
        
        # Monkey patch para aplicar tema aos messageboxes
        original_showinfo = mb.showinfo
        original_showerror = mb.showerror
        original_showwarning = mb.showwarning
        original_askyesno = mb.askyesno
        original_askokcancel = mb.askokcancel
        
        def themed_showinfo(title, message, **kwargs):
            result = original_showinfo(title, message, **kwargs)
            _theme_messagebox_window(title, colors, fonts)
            return result
            
        def themed_showerror(title, message, **kwargs):
            result = original_showerror(title, message, **kwargs)
            _theme_messagebox_window(title, colors, fonts)
            return result
            
        def themed_showwarning(title, message, **kwargs):
            result = original_showwarning(title, message, **kwargs)
            _theme_messagebox_window(title, colors, fonts)
            return result
            
        def themed_askyesno(title, message, **kwargs):
            result = original_askyesno(title, message, **kwargs)
            _theme_messagebox_window(title, colors, fonts)
            return result
            
        def themed_askokcancel(title, message, **kwargs):
            result = original_askokcancel(title, message, **kwargs)
            _theme_messagebox_window(title, colors, fonts)
            return result
        
        # Aplicar os patches
        mb.showinfo = themed_showinfo
        mb.showerror = themed_showerror
        mb.showwarning = themed_showwarning
        mb.askyesno = themed_askyesno
        mb.askokcancel = themed_askokcancel
        
    except Exception:
        pass

def _theme_messagebox_window(title, colors, fonts):
    """Aplica tema a uma janela de messagebox específica"""
    try:
        import tkinter as tk
        
        # Encontrar a janela mais recente que seja um Toplevel
        for widget in tk._default_root.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() == title:
                try:
                    _apply_popup_theme(widget, colors, fonts, None)
                except Exception:
                    pass
                break
    except Exception:
        pass

class UserDatabase:
    def __init__(self):
        # New preferred storage: JSON file for robustness
        self.filename = "users.json"
        self.legacy_filename = "users.dat"
        self.users = self.load_users()

    # Password hashing helpers (PBKDF2-HMAC-SHA256)
    def _hash_password(self, password: str, iterations: int = 200000):
        import hashlib, secrets, base64
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
        return f"pbkdf2${iterations}${base64.b64encode(salt).decode('ascii')}${base64.b64encode(dk).decode('ascii')}"

    def _verify_password_hash(self, stored: str, password: str):
        import hashlib, base64
        try:
            if not stored.startswith('pbkdf2$'):
                # legacy plaintext
                return stored == password, False
            parts = stored.split('$')
            iterations = int(parts[1]); salt = base64.b64decode(parts[2]); dk = base64.b64decode(parts[3])
            newdk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
            return newdk == dk, True
        except Exception:
            return False, False

    def load_users(self):
        import json
        # Prefer JSON file
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)
                    return data if isinstance(data, dict) else {}
            except Exception:
                # corrupt JSON - fallback to empty
                return {}

        # Fallback: migrate legacy pipe-separated users.dat if present
        if os.path.exists(self.legacy_filename):
            users = {}
            try:
                with open(self.legacy_filename, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if not parts or len(parts) < 2:
                            continue
                        username = parts[0]
                        password = parts[1] if len(parts) > 1 else ''
                        role = parts[2] if len(parts) > 2 else 'professor'
                        email = parts[3] if len(parts) > 3 and parts[3] != 'None' else None
                        email_verified = parts[4] == 'True' if len(parts) > 4 else False
                        users[username] = {
                            'password': password,
                            'role': role,
                            'email': email,
                            'email_verified': email_verified
                        }
                # Save migrated JSON atomically
                try:
                    with open(self.filename + '.tmp', 'w', encoding='utf-8') as wf:
                        json.dump(users, wf, ensure_ascii=False, indent=2)
                    os.replace(self.filename + '.tmp', self.filename)
                except Exception:
                    pass
                return users
            except Exception:
                return {}

        # No storage exists: create default admin
        users = {'admin': {
            'password': self._hash_password('Admin@123'),
            'role': 'admin',
            'email': None,
            'email_verified': False
        }}
        self.save_users(users)
        return users

    def save_users(self, users=None):
        import json
        if users is None:
            users = self.users
        # Write JSON atomically
        tmp = self.filename + '.tmp'
        try:
            with open(tmp, 'w', encoding='utf-8') as jf:
                json.dump(users, jf, ensure_ascii=False, indent=2)
            os.replace(tmp, self.filename)
        except Exception:
            # Best-effort fallback to write plain text (legacy format)
            try:
                with open(self.legacy_filename, 'w', encoding='utf-8') as f:
                    for username, data in users.items():
                        f.write(f"{username}|{data.get('password','')}|{data.get('role','')}|{data.get('email') or 'None'}|{data.get('email_verified', False)}\n")
            except Exception:
                pass

    def validate_password(self, password):
        # Pelo menos 8 caracteres
        if len(password) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres"
        
        # Deve conter letra maiúscula, minúscula, número e caractere especial
        if not re.search(r"[A-Z]", password):
            return False, "A senha deve conter pelo menos uma letra maiúscula"
        if not re.search(r"[a-z]", password):
            return False, "A senha deve conter pelo menos uma letra minúscula"
        if not re.search(r"\d", password):
            return False, "A senha deve conter pelo menos um número"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "A senha deve conter pelo menos um caractere especial"
        
        return True, "Senha válida"

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def add_user(self, username, password, role, email=None, pending=False, turno='matutino', matricula=None):
        if username in self.users:
            return False, "Nome de usuário já existe"
        
        # Valida a senha
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg
            
        # Valida o email se fornecido
        if email and not self.validate_email(email):
            return False, "Email inválido"
            
        # store hashed password
        hashed = self._hash_password(password)
        # No question/answer by default
        import datetime
        now = datetime.datetime.now().isoformat()
        
        self.users[username] = {
            'password': hashed,
            'role': role,
            'email': email,
            'email_verified': False,
            'secret_question': None,
            'secret_answer': None,
            'preferences': {},
            'status': 'pending' if pending else 'approved',
            'created_at': now,
            'last_login': None,
            'login_time': None,  # timestamp do login atual
            'total_time': 0,  # tempo total de uso em segundos
            'turno': turno  # turno do usuário
        }
        
        # Se for aluno e matrícula foi fornecida, atribuir
        if role == 'aluno' and matricula:
            self.users[username]['matricula'] = matricula
        
        self.save_users()
        if pending:
            return True, "Cadastro enviado para aprovação do administrador. Aguarde a aprovação para acessar o sistema."
        return True, "Usuário cadastrado com sucesso"

    def set_user_pref(self, username, key, value):
        """Set a preferences key for a user and persist to storage."""
        if username not in self.users:
            return False, "Usuário não encontrado"
        prefs = self.users[username].setdefault('preferences', {})
        prefs[key] = value
        self.save_users()
        return True, "Preferência salva"

    def get_user_pref(self, username, key, default=None):
        if username not in self.users:
            return default
        return self.users[username].get('preferences', {}).get(key, default)

    def set_secret_question(self, username, question: str, answer: str):
        """Store a secret question and hashed answer for a user."""
        if username not in self.users:
            return False, "Usuário não encontrado"
        if not question or not answer:
            return False, "Pergunta e resposta secreta são obrigatórias"
        # store question and hashed answer (reuse hashing helper)
        hashed = self._hash_password(answer)
        self.users[username]['secret_question'] = question
        self.users[username]['secret_answer'] = hashed
        self.save_users()
        return True, "Pergunta secreta registrada"

    def verify_secret_answer(self, username, answer: str):
        """Verify the provided answer against stored hash. Returns True/False."""
        if username not in self.users:
            return False
        stored = self.users[username].get('secret_answer')
        if not stored or not answer:
            return False
        ok, _ = self._verify_password_hash(stored, answer)
        return ok

    def set_password(self, username, new_password: str):
        """Set a new password for username without requiring the old password. Validates rules."""
        if username not in self.users:
            return False, "Usuário não encontrado"
        is_valid, msg = self.validate_password(new_password)
        if not is_valid:
            return False, msg
        self.users[username]['password'] = self._hash_password(new_password)
        self.save_users()
        return True, "Senha atualizada com sucesso"

    def verify_user(self, username, password):
        if username not in self.users: return False
        
        # Verificar se o usuário está aprovado
        if self.users[username].get('status') == 'pending':
            return False  # Usuário pendente não pode fazer login
        
        stored = self.users[username]['password']
        ok, was_hash = self._verify_password_hash(stored, password)
        if ok and not was_hash:
            # Legacy plaintext matched, re-hash and save
            self.users[username]['password'] = self._hash_password(password)
            self.save_users()
        return ok

    def get_role(self, username):
        return self.users[username]['role'] if username in self.users else None

    def get_user_data(self, username):
        return self.users.get(username)

    def update_email(self, username, email):
        if not self.validate_email(email):
            return False, "Email inválido"
        if username in self.users:
            self.users[username]['email'] = email
            self.users[username]['email_verified'] = False
            self.save_users()
            return True, "Email atualizado com sucesso"
        return False, "Usuário não encontrado"

    def update_password(self, username, old_password, new_password):
        if not self.verify_user(username, old_password):
            return False, "Senha atual incorreta"
        
        is_valid, msg = self.validate_password(new_password)
        if not is_valid:
            return False, msg
        # set hashed new password
        self.users[username]['password'] = self._hash_password(new_password)
        self.save_users()
        return True, "Senha atualizada com sucesso"

    def set_professor_subjects(self, username, subjects):
        """Define as matérias que um professor pode acessar"""
        if username not in self.users:
            return False, "Usuário não encontrado"
        if self.users[username]['role'] != 'professor':
            return False, "Usuário não é um professor"
        
        self.users[username]['subjects'] = subjects
        self.save_users()
        return True, "Matérias do professor atualizadas com sucesso"
    
    def generate_username_from_name(self, nome):
        """Gera um username único baseado no nome"""
        import re
        # Remover acentos e caracteres especiais
        nome_limpo = nome.lower().strip()
        nome_limpo = re.sub(r'[àáâãäå]', 'a', nome_limpo)
        nome_limpo = re.sub(r'[èéêë]', 'e', nome_limpo)
        nome_limpo = re.sub(r'[ìíîï]', 'i', nome_limpo)
        nome_limpo = re.sub(r'[òóôõö]', 'o', nome_limpo)
        nome_limpo = re.sub(r'[ùúûü]', 'u', nome_limpo)
        nome_limpo = re.sub(r'[ç]', 'c', nome_limpo)
        nome_limpo = re.sub(r'[ñ]', 'n', nome_limpo)
        # Remover espaços e caracteres não alfanuméricos
        nome_limpo = re.sub(r'[^a-z0-9]', '', nome_limpo)
        
        # Pegar primeira parte do nome
        base_username = nome_limpo[:15] if len(nome_limpo) > 15 else nome_limpo
        
        # Verificar se já existe, se sim adicionar número
        username = base_username
        counter = 1
        while username in self.users:
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def generate_temp_password(self):
        """Gera uma senha temporária de 8 caracteres com pelo menos um caractere especial"""
        import random
        import string
        # Garantir pelo menos uma letra maiúscula, uma minúscula, um número e um caractere especial
        especiais = "!@#$%&*"
        
        # Selecionar pelo menos um de cada tipo
        senha_parts = [
            random.choice(string.ascii_uppercase),  # Maiúscula
            random.choice(string.ascii_lowercase),  # Minúscula
            random.choice(string.digits),            # Número
            random.choice(especiais)                 # Especial
        ]
        
        # Preencher o resto com caracteres aleatórios
        todos_chars = string.ascii_letters + string.digits + especiais
        for _ in range(4):  # 8 total - 4 obrigatórios = 4 restantes
            senha_parts.append(random.choice(todos_chars))
        
        # Embaralhar para não ter padrão previsível
        random.shuffle(senha_parts)
        return ''.join(senha_parts)
    
    def get_professor_subjects(self, username):
        """Retorna as matérias que um professor pode acessar"""
        if username not in self.users:
            return []
        return self.users[username].get('subjects', [])
    
    def can_access_subject(self, username, subject_id):
        """Verifica se um professor pode acessar uma matéria específica"""
        if username not in self.users:
            print(f"[DEBUG] Usuário '{username}' não encontrado")
            return False
        
        user_role = self.users[username]['role']
        
        if user_role == 'admin':
            print(f"[DEBUG] Admin '{username}' tem acesso total")
            return True  # Admin pode acessar tudo
        
        if user_role == 'aluno':
            print(f"[DEBUG] Aluno '{username}' - verificação de acesso não aplicável")
            return False
        
        if user_role != 'professor':
            print(f"[DEBUG] Usuário '{username}' com role '{user_role}' não tem acesso")
            return False
        
        subjects = self.users[username].get('subjects', [])
        # Converter subject_id para string para comparação consistente
        subject_id_str = str(subject_id)
        # Verificar se está na lista (pode estar como string ou int)
        has_access = subject_id_str in [str(s) for s in subjects]
        
        print(f"[DEBUG] Professor '{username}' - Turma '{subject_id}' - Matérias atribuídas: {subjects} - Acesso: {has_access}")
        
        return has_access
    
    def get_all_professors(self):
        """Retorna lista de todos os professores"""
        professors = []
        for username, data in self.users.items():
            if data['role'] == 'professor':
                subjects = data.get('subjects', [])
                professors.append({
                    'username': username,
                    'email': data.get('email', ''),
                    'subjects': subjects
                })
        return professors
    
    def set_student_matricula(self, username, matricula):
        """Associa uma matrícula a um usuário aluno"""
        if username not in self.users:
            return False, "Usuário não encontrado"
        if self.users[username]['role'] != 'aluno':
            return False, "Usuário não é um aluno"
        
        self.users[username]['matricula'] = matricula
        self.save_users()
        return True, "Matrícula associada com sucesso"
    
    def get_student_matricula(self, username):
        """Retorna a matrícula associada a um usuário aluno"""
        if username not in self.users:
            return None
        if self.users[username]['role'] != 'aluno':
            return None
        return self.users[username].get('matricula')
    
    def get_pending_users(self):
        """Retorna lista de usuários pendentes de aprovação"""
        pending = []
        for username, data in self.users.items():
            if data.get('status') == 'pending':
                pending.append({
                    'username': username,
                    'email': data.get('email', ''),
                    'role': data.get('role', ''),
                    'created_at': data.get('created_at', None)
                })
        return pending
    
    def approve_user(self, username):
        """Aprova um usuário pendente"""
        if username not in self.users:
            return False, "Usuário não encontrado"
        if self.users[username].get('status') != 'pending':
            return False, "Usuário não está pendente"
        
        self.users[username]['status'] = 'approved'
        self.save_users()
        return True, "Usuário aprovado com sucesso"
    
    def reject_user(self, username):
        """Rejeita e remove um usuário pendente"""
        if username not in self.users:
            return False, "Usuário não encontrado"
        if self.users[username].get('status') != 'pending':
            return False, "Usuário não está pendente"
        
        del self.users[username]
        self.save_users()
        return True, "Usuário rejeitado e removido"
    
    def update_user(self, username, new_data):
        """Permite admin atualizar dados de qualquer usuário"""
        if username not in self.users:
            return False, "Usuário não encontrado"
        
        # Atualizar campos permitidos
        if 'email' in new_data:
            if new_data['email'] and not self.validate_email(new_data['email']):
                return False, "Email inválido"
            self.users[username]['email'] = new_data['email']
        
        if 'role' in new_data:
            self.users[username]['role'] = new_data['role']
        
        if 'status' in new_data:
            self.users[username]['status'] = new_data['status']
        
        if 'telefone' in new_data:
            self.users[username]['telefone'] = new_data['telefone']
        
        if 'foto_perfil' in new_data:
            self.users[username]['foto_perfil'] = new_data['foto_perfil']
        
        if 'data_nascimento' in new_data:
            self.users[username]['data_nascimento'] = new_data['data_nascimento']
        
        if 'cpf' in new_data:
            self.users[username]['cpf'] = new_data['cpf']
        
        if 'endereco' in new_data:
            self.users[username]['endereco'] = new_data['endereco']
        
        if 'bio' in new_data:
            self.users[username]['bio'] = new_data['bio']
        
        self.save_users()
        return True, "Usuário atualizado com sucesso"

def show_calendar_picker(parent, entry_widget, colors):
    """Exibe um calendário visual para seleção de data"""
    cal_dialog = tk.Toplevel(parent)
    cal_dialog.title("Selecionar Data")
    cal_dialog.geometry("350x400")
    cal_dialog.transient(parent)
    cal_dialog.grab_set()
    cal_dialog.resizable(False, False)
    _center_window(cal_dialog)
    
    # Aplicar tema
    cal_dialog.configure(bg=colors['card'])
    try:
        # Tentar aplicar tema completo se disponível
        if hasattr(parent, 'fonts'):
            _apply_popup_theme(cal_dialog, colors, parent.fonts, getattr(parent, 'style', None))
    except Exception:
        pass
    _set_window_icon(cal_dialog)
    
    # Variáveis para controle do calendário
    today = datetime.now()
    current_month = tk.IntVar(value=today.month)
    current_year = tk.IntVar(value=today.year)
    selected_date = None
    
    # Frame principal
    main_frame = tk.Frame(cal_dialog, bg=colors['card'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Frame de navegação
    nav_frame = tk.Frame(main_frame, bg=colors['card'])
    nav_frame.pack(fill=tk.X, pady=(0, 10))
    
    def update_calendar():
        """Atualiza o calendário com o mês/ano atual"""
        # Limpar frame do calendário
        for widget in cal_frame.winfo_children():
            widget.destroy()
        
        month = current_month.get()
        year = current_year.get()
        
        # Cabeçalho com mês e ano
        month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        header_label = tk.Label(cal_frame, text=f"{month_names[month-1]} {year}", 
                               font=('Arial', 12, 'bold'), bg=colors['card'], 
                               fg=colors['primary'])
        header_label.grid(row=0, column=0, columnspan=7, pady=10)
        
        # Dias da semana (Brasil: Segunda a Domingo)
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            tk.Label(cal_frame, text=day, font=('Arial', 9, 'bold'), 
                    bg=colors['card'], fg=colors['text_secondary'], 
                    width=4).grid(row=1, column=i, padx=2, pady=2)
        
        # Obter calendário do mês
        cal = calendar.monthcalendar(year, month)
        
        def select_date(day):
            nonlocal selected_date
            selected_date = f"{day:02d}/{month:02d}/{year}"
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date)
            cal_dialog.destroy()
        
        # Preencher dias
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Dia vazio
                    tk.Label(cal_frame, text="", bg=colors['card'], 
                            width=4, height=2).grid(row=week_num+2, column=day_num, 
                                                   padx=1, pady=1)
                else:
                    # Verificar se é o dia atual
                    is_today = (day == today.day and month == today.month and year == today.year)
                    
                    btn = tk.Button(cal_frame, text=str(day), 
                                   font=('Arial', 9, 'bold' if is_today else 'normal'),
                                   bg=colors['primary'] if is_today else colors['bg'],
                                   fg='white' if is_today else colors['text'],
                                   activebackground=colors['primary_hover'],
                                   activeforeground='white',
                                   relief='flat' if not is_today else 'raised',
                                   bd=1,
                                   cursor='hand2',
                                   width=4, height=2,
                                   command=lambda d=day: select_date(d))
                    btn.grid(row=week_num+2, column=day_num, padx=1, pady=1)
                    
                    # Efeito hover
                    def on_enter(e, b=btn):
                        if b['bg'] != colors['primary']:
                            b.config(bg=colors['border'])
                    
                    def on_leave(e, b=btn, today_btn=is_today):
                        if not today_btn:
                            b.config(bg=colors['bg'])
                    
                    btn.bind('<Enter>', on_enter)
                    btn.bind('<Leave>', on_leave)
    
    def prev_month():
        month = current_month.get()
        year = current_year.get()
        if month == 1:
            current_month.set(12)
            current_year.set(year - 1)
        else:
            current_month.set(month - 1)
        update_calendar()
    
    def next_month():
        month = current_month.get()
        year = current_year.get()
        if month == 12:
            current_month.set(1)
            current_year.set(year + 1)
        else:
            current_month.set(month + 1)
        update_calendar()
    
    # Botões de navegação
    btn_prev = tk.Button(nav_frame, text="◀", font=('Arial', 12, 'bold'),
                        bg=colors['primary'], fg='white', 
                        activebackground=colors['primary_hover'],
                        relief='flat', cursor='hand2', width=3,
                        command=prev_month)
    btn_prev.pack(side=tk.LEFT, padx=5)
    
    tk.Label(nav_frame, text="", bg=colors['card']).pack(side=tk.LEFT, expand=True)
    
    btn_next = tk.Button(nav_frame, text="▶", font=('Arial', 12, 'bold'),
                        bg=colors['primary'], fg='white',
                        activebackground=colors['primary_hover'],
                        relief='flat', cursor='hand2', width=3,
                        command=next_month)
    btn_next.pack(side=tk.RIGHT, padx=5)
    
    # Frame para o calendário
    cal_frame = tk.Frame(main_frame, bg=colors['card'])
    cal_frame.pack(fill=tk.BOTH, expand=True)
    
    # Frame de botões
    btn_frame = tk.Frame(main_frame, bg=colors['card'])
    btn_frame.pack(fill=tk.X, pady=(10, 0))
    
    tk.Button(btn_frame, text="Hoje", font=('Arial', 9),
             bg=colors['primary'], fg='white',
             activebackground=colors['primary_hover'],
             relief='flat', cursor='hand2',
             command=lambda: (current_month.set(today.month), 
                            current_year.set(today.year), 
                            update_calendar())).pack(side=tk.LEFT, padx=5)
    
    cancel_btn = tk.Button(btn_frame, text="Cancelar", font=('Arial', 9),
             bg=colors['border'], fg=colors['text'],
             relief='flat', cursor='hand2',
             command=cal_dialog.destroy)
    cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    # Configurar atalhos (ESC fecha)
    _setup_dialog_shortcuts(cal_dialog, cancel_callback=cal_dialog.destroy)
    
    # Inicializar calendário
    update_calendar()

class LoginWindow(tk.Tk):
    # Lista de perguntas padrão definida a nível de classe
    @staticmethod
    def _hex_to_rgba(hex_color, alpha=255):
        """Converte uma cor no formato #RRGGBB para uma tupla (R,G,B,A)."""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c * 2 for c in hex_color])
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, alpha)
        except Exception:
            return (255, 255, 255, alpha)

    PREDEFINED_SECRET_QUESTIONS = [
        "Qual o nome do seu primeiro animal de estimação?",
        "Qual o nome de solteira da sua mãe?",
        "Em que cidade você nasceu?",
        "Qual era o modelo do seu primeiro carro?",
        "Qual o nome do seu professor favorito do ensino médio?"
    ]

    def __init__(self):
        super().__init__()
        self.db = UserDatabase()
        
        # --- SEM MUDANÇAS AQUI, MAS GARANTA QUE ESTÁ ASSIM ---
        self.user_icon_photo = None
        self.lock_icon_photo = None
        self.eye_open_photo = None
        self.eye_closed_photo = None
        
        # Guardaremos as imagens PIL originais aqui
        self.sun_pil = None
        self.moon_pil = None

        try:
            from PIL import Image, ImageTk
            
            user_img = Image.open("img/user.png").convert("RGBA").resize((20, 20), Image.LANCZOS)
            self.user_icon_photo = ImageTk.PhotoImage(user_img)

            lock_img = Image.open("img/lock.png").convert("RGBA").resize((20, 20), Image.LANCZOS)
            self.lock_icon_photo = ImageTk.PhotoImage(lock_img)

            eye_open_img = Image.open("img/open_eye.png").convert("RGBA").resize((21, 21), Image.LANCZOS)
            self.eye_open_photo = ImageTk.PhotoImage(eye_open_img)

            eye_closed_img = Image.open("img/close_eye.png").convert("RGBA").resize((21, 21), Image.LANCZOS)
            self.eye_closed_photo = ImageTk.PhotoImage(eye_closed_img)
            
            # Apenas carregue as imagens PIL, não converta para PhotoImage ainda
            self.sun_pil = Image.open("img/sun_mode.png").convert("RGBA").resize((65, 30), Image.LANCZOS)
            self.moon_pil = Image.open("img/moon_mode.png").convert("RGBA").resize((65, 30), Image.LANCZOS)

            # Cria PhotoImage pré-renderizadas mantendo alfa (transparência)
            try:
                self.sun_icon_photo = ImageTk.PhotoImage(self.sun_pil)
            except Exception:
                self.sun_icon_photo = None
            try:
                self.moon_icon_photo = ImageTk.PhotoImage(self.moon_pil)
            except Exception:
                self.moon_icon_photo = None

        except Exception as e:
            print(f"AVISO: Não foi possível carregar os ícones. Verifique os arquivos. {e}")
        
        self._setup_window()
        self._setup_theme()
        self._create_widgets()
        
    def _setup_window(self):
        self.title("Login - Sistema Acadêmico")
        self.geometry("450x580")
        self.resizable(False, False)
        
        try:
            self.iconbitmap("img/icone.ico") 
        except tk.TclError:
            print("Aviso: Arquivo 'icone.ico' não encontrado.")

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f'{self.winfo_width()}x{self.winfo_height()}+{x}+{y}')

    def _setup_theme(self):
        # Usar definições globais de temas
        self.colors = LIGHT_THEME.copy()
        self.fonts = DEFAULT_FONTS.copy()
        self.configure(bg=self.colors['bg'])
        self.dark_mode = getattr(self, 'dark_mode', False)
        if self.dark_mode:
            self.colors.update(DARK_THEME)

        try:
            self.style = ttk.Style(self)
            self.style.theme_use('clam')
            self.style.configure('Primary.TButton', background=self.colors['primary'], foreground=self.colors['card'], padding=(12, 8), relief='flat')
            self.style.map('Primary.TButton', background=[('active', self.colors.get('primary_hover', self.colors['primary']))])
            self.style.configure('Secondary.TButton', background=self.colors['card'], foreground=self.colors['primary'], padding=(12, 8), relief='flat')
            self.style.map('Secondary.TButton', background=[('active', self.colors.get('bg', self.colors['card']))])
        except Exception:
            pass

    def _create_widgets(self):
        card_bg = self.colors.get('bg', 'card')
        card_frame = tk.Frame(self, bg=card_bg, padx=40, pady=30, highlightbackground=self.colors.get('shadow'), highlightthickness=1)
        card_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._login_card = card_frame

        # Logo, Título e Subtítulo
        logo_img = None
        try:
            from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(__file__), "img/samurai.png")
            if os.path.exists(img_path):
                pil_img = Image.open(img_path).convert('RGBA').resize((72, 72), Image.LANCZOS)
                bg_image = Image.new('RGBA', pil_img.size, self._hex_to_rgba(card_bg))
                composed_image = Image.alpha_composite(bg_image, pil_img)
                logo_img = ImageTk.PhotoImage(composed_image)
                self._logo_pil = pil_img
        except Exception:
            logo_img = None

        self._logo_label = tk.Label(card_frame, image=logo_img, bg=card_bg, borderwidth=0)
        if logo_img: self._logo_label.image = logo_img
        else: self._logo_label.config(text="🎓", fg=self.colors['primary'], font=self.fonts['logo'])
        self._logo_label.pack(pady=(0, 10))
        
        self._login_title = tk.Label(card_frame, text="Bem-vindo", bg=card_bg, fg=self.colors['text'], font=self.fonts['title'])
        self._login_title.pack(pady=(0, 5))
        self._login_subtitle = tk.Label(card_frame, text="Acesse o Sistema Acadêmico", bg=card_bg, fg=self.colors['text_secondary'], font=self.fonts['body'])
        self._login_subtitle.pack(pady=(0, 25))

        self.user_container, self.username_entry = self._create_icon_entry(card_frame, "user", "Usuário ou Email")
        self.user_container.pack(pady=5, fill=tk.X)
        
        password_frame = tk.Frame(card_frame, bg=card_bg)
        password_frame.pack(pady=5, fill=tk.X)
        
        self.password_entry_container, self.password_entry = self._create_icon_entry(password_frame, "lock", "Senha", show="•")
        self.password_entry_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.show_pass_var = tk.BooleanVar(value=False)
        self.show_pass_button = tk.Checkbutton(password_frame, image=self.eye_closed_photo, selectimage=self.eye_open_photo, variable=self.show_pass_var, command=self._toggle_password_visibility, bg=card_bg, activebackground=card_bg, selectcolor=card_bg, highlightthickness=0, indicatoron=0, bd=0, relief="flat", cursor="hand2")
        self.show_pass_button.pack(side=tk.RIGHT, padx=(5, 0))

        button_frame = tk.Frame(card_frame, bg=card_bg)
        button_frame.pack(fill=tk.X, pady=(20, 10))
        ttk.Button(button_frame, text="Entrar", command=self.login, style='Primary.TButton', cursor="hand2").pack(fill=tk.X)
        ttk.Button(button_frame, text="Cadastrar Novo Usuário", command=self.show_register, style='Secondary.TButton', cursor="hand2").pack(fill=tk.X, pady=5)

        self.forgot_label = tk.Label(card_frame, text="Esqueceu sua senha?", fg=self.colors['primary'], bg=card_bg, cursor="hand2", font=(self.fonts['body'][0], 9, "underline"))
        self.forgot_label.pack(pady=(5,0))
        self.forgot_label.bind("<Button-1>", lambda e: self.show_password_recovery())

        bottom_frame = tk.Frame(card_frame, bg=card_bg)
        bottom_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.dark_var = tk.BooleanVar(value=self.dark_mode)
        
            # Botão de modo escuro com ícone de sol/lua
        self.dark_mode_button = tk.Checkbutton(
            bottom_frame,
            variable=self.dark_var,
            command=self._apply_theme_changes,
            indicatoron=0,
            bd=0,
            borderwidth=0,
            highlightthickness=0,
            highlightbackground=card_bg,
            highlightcolor=card_bg,
            activebackground=card_bg,
            bg=card_bg,
            relief="flat",
            cursor="hand2",
            takefocus=0,
            selectcolor=card_bg,
            padx=0,
            pady=0,
            font=(self.fonts['icon_button'][0], 16),
            compound='center'
        )
        self._apply_theme_changes() 
        self._update_dark_mode_icon()
        self.dark_mode_button.pack(side=tk.RIGHT)
            ### MODIFICAÇÃO FIM ###

    def _update_dark_mode_icon(self):
        # Atualiza o ícone do botão de modo escuro
        try:
            # Use imagens PIL carregadas se disponíveis para um visual mais polido
            # Prefer cached ImageTk.PhotoImage objects created no __init__ (mantêm alfa)
            if getattr(self, 'dark_mode', False) and getattr(self, 'moon_icon_photo', None):
                self.dark_mode_button.config(image=self.moon_icon_photo, text='')
                self.dark_mode_button.image = self.moon_icon_photo
            elif not getattr(self, 'dark_mode', False) and getattr(self, 'sun_icon_photo', None):
                self.dark_mode_button.config(image=self.sun_icon_photo, text='')
                self.dark_mode_button.image = self.sun_icon_photo
            else:
                # Fallback para emoji se as imagens não existirem
                self.dark_mode_button.config(image='', text=("🌙" if getattr(self, 'dark_mode', False) else "☀️"), fg=self.colors['primary'])
        except Exception:
            # Silencioso: use emoji fallback
            self.dark_mode_button.config(text=("🌙" if getattr(self, 'dark_mode', False) else "☀️"), fg=self.colors['primary'])
        # Focus bindings
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
    def _create_icon_entry(self, parent, icon, placeholder, **kwargs):
        # ... (código desta função permanece o mesmo)
        show_char = kwargs.pop('show', None)
        parent_bg = self.colors.get('card')
        container = tk.Frame(parent, bd=1, relief="solid", bg=self.colors['border'], highlightthickness=0)
        inner_container = tk.Frame(container, bg=parent_bg, highlightthickness=0)
        inner_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        icon_frame = tk.Frame(inner_container, width=35, bg=parent_bg)
        icon_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        icon_frame.pack_propagate(False)

        icon_label = None
        if icon == 'user' and self.user_icon_photo:
            icon_label = tk.Label(icon_frame, image=self.user_icon_photo, bg=parent_bg, bd=0)
        elif icon == 'lock' and self.lock_icon_photo:
            icon_label = tk.Label(icon_frame, image=self.lock_icon_photo, bg=parent_bg, bd=0)
        else:
            icon_label = tk.Label(icon_frame, text=icon, bg=parent_bg, font=("Helvetica", 12), fg=self.colors['text_secondary'])
        
        if icon_label:
            icon_label.pack(expand=True)
            container.icon_label = icon_label

        entry = tk.Entry(inner_container, bd=0, relief="flat", bg=parent_bg, fg=self.colors['text'], insertbackground=self.colors['text'], highlightthickness=0, font=self.fonts['body'], **kwargs)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5, padx=(5, 7))
        entry._placeholder, entry._show_char = placeholder, show_char
        entry.insert(0, placeholder)
        entry.config(fg=self.colors['text_secondary'])

        def on_focus_in(event):
            w = event.widget
            if w.get() == w._placeholder:
                w.delete(0, tk.END); w.config(fg=self.colors['text'])
                if getattr(w, '_show_char', None): w.config(show=w._show_char)
        def on_focus_out(event):
            w = event.widget
            if not w.get():
                if getattr(w, '_show_char', None): w.config(show='')
                w.insert(0, w._placeholder); w.config(fg=self.colors['text_secondary'])

        entry.bind('<FocusIn>', on_focus_in); entry.bind('<FocusOut>', on_focus_out)
        return container, entry

    def _toggle_password_visibility(self):
        # ... (código desta função permanece o mesmo)
        is_placeholder = self.password_entry.get() == getattr(self.password_entry, '_placeholder', None)
        if not is_placeholder:
            self.password_entry.config(show="" if self.show_pass_var.get() else "•")

    def get_username(self):
        # ... (código desta função permanece o mesmo)
        user = self.username_entry.get(); return "" if user == "Usuário ou Email" else user

    def get_password(self):
        # ... (código desta função permanece o mesmo)
        pwd = self.password_entry.get(); return "" if pwd == "Senha" else pwd
        
    def login(self):
        # ... (código desta função permanece o mesmo)
        username = self.get_username()
        password = self.get_password()
        if not username or not password:
            show_error(self, "Erro de Login", "Por favor, preencha todos os campos.")
            return
        
        user_to_verify = username
        if '@' in username:
            user_to_verify = next((u for u, d in self.db.users.items() if d.get('email') == username), None)
            if not user_to_verify:
                show_error(self, "Erro de Login", "Email não encontrado.")
                return
            
        # Verificar se o usuário existe e se está pendente
        user_data = self.db.get_user_data(user_to_verify)
        if user_data and user_data.get('status') == 'pending':
            show_warning(self, "Aguardando Aprovação", 
                        "Seu cadastro está aguardando aprovação do administrador.\n"
                        "Você receberá acesso assim que for aprovado.")
            return
        
        if self.db.verify_user(user_to_verify, password):
            # Registrar login
            import datetime
            now = datetime.datetime.now().isoformat()
            if user_to_verify in self.db.users:
                self.db.users[user_to_verify]['last_login'] = now
                self.db.users[user_to_verify]['login_time'] = datetime.datetime.now().timestamp()
                self.db.save_users()
            
            self.destroy()
            App(role=self.db.get_role(user_to_verify), username=user_to_verify, dark_mode=self.dark_mode).mainloop()
        else:
            show_error(self, "Erro de Login", "Usuário ou senha inválidos.")

    def _apply_theme_changes(self):
        if hasattr(self, 'dark_var'): # Garante que não rode antes do botão existir
            self.dark_mode = self.dark_var.get()
        
        # Usar definições globais de temas
        if self.dark_mode:
            self.colors = DARK_THEME.copy()
        else:
            self.colors = LIGHT_THEME.copy()
            
        # Atualiza ícone do botão de modo escuro
        if hasattr(self, 'dark_mode_button'):
            self._update_dark_mode_icon()
        
        card_bg = self.colors['card']
        self.configure(bg=self.colors['bg'])
        self._login_card.configure(bg=card_bg, highlightbackground=self.colors['shadow'])
        
        for widget in self._login_card.winfo_children():
            try: widget.configure(bg=card_bg)
            except tk.TclError: pass
        
        self._login_title.configure(fg=self.colors['text'])
        self._login_subtitle.configure(fg=self.colors['text_secondary'])
        self.forgot_label.configure(fg=self.colors['primary'])
        
        # Atualizar cores do botão de mostrar senha
        self.show_pass_button.configure(
            bg=card_bg, 
            activebackground=card_bg,
            selectcolor=card_bg,
            highlightbackground=card_bg,
            highlightcolor=card_bg
        )

        # estilo do botão modo escuro (aplica borda arredondada simulada)
        try:
            # Make the checkbutton look like an icon button
            # Ensure the button remains fully borderless
            self.dark_mode_button.configure(
                bg=card_bg,
                activebackground=card_bg,
                bd=0,
                borderwidth=0,
                highlightthickness=0,
                highlightbackground=card_bg,
                highlightcolor=card_bg,
                relief='flat',
                takefocus=0,
                selectcolor=card_bg
            )
        except Exception:
            pass

        def update_container_theme(container):
            container.configure(bg=self.colors['border'])
            inner_container = container.winfo_children()[0]
            inner_container.configure(bg=card_bg)
            icon_frame, entry = inner_container.winfo_children()
            icon_frame.configure(bg=card_bg)
            entry.configure(bg=card_bg, fg=self.colors['text'], insertbackground=self.colors['text'])
            if hasattr(container, 'icon_label'):
                container.icon_label.configure(bg=card_bg)
            if entry.get() == getattr(entry, '_placeholder', None):
                entry.config(fg=self.colors['text_secondary'])

        update_container_theme(self.user_container)
        update_container_theme(self.password_entry_container)
        
        # Atualizar também o frame do password que contém o botão de show/hide
        try:
            # Procurar o frame pai do password_entry_container
            for widget in self._login_card.winfo_children():
                if isinstance(widget, tk.Frame):
                    # Verificar se contém o password_entry_container
                    for child in widget.winfo_children():
                        if child == self.password_entry_container:
                            widget.configure(bg=card_bg)
                            break
        except Exception:
            pass

        if hasattr(self, '_logo_pil'):
            try:
                from PIL import Image, ImageTk
                bg_image = Image.new('RGBA', self._logo_pil.size, self._hex_to_rgba(card_bg))
                composed = Image.alpha_composite(bg_image, self._logo_pil)
                self._logo_photo = ImageTk.PhotoImage(composed)
                self._logo_label.configure(image=self._logo_photo, bg=card_bg)
            except Exception: pass


    def show_password_recovery(self):
        recovery_window, main_frame = self._create_dialog_window("Recuperação de Senha", "450x400")
        step_frame = tk.Frame(main_frame, bg=self.colors['card'])
        step_frame.pack(fill=tk.BOTH, expand=True)

        def show_step_1():
            for widget in step_frame.winfo_children(): widget.destroy()
            tk.Label(step_frame, text="Passo 1 de 3: Identificação", font=self.fonts['title'], bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 20))
            tk.Label(step_frame, text="Digite seu usuário ou email para começar.", font=self.fonts['body'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(pady=(0, 15))
            user_container, entry_identifier = self._create_icon_entry(step_frame, "📧", "Usuário ou Email")
            user_container.pack(fill=tk.X, pady=5)

            def process_step_1():
                identifier = entry_identifier.get()
                if not identifier or identifier == "Usuário ou Email": show_error(recovery_window, "Erro", "Por favor, insira seu usuário ou email."); return
                username = next((u for u,d in self.db.users.items() if d.get('email')==identifier), identifier if identifier in self.db.users else None)
                if not username: show_error(recovery_window, "Erro", "Email/Usuário não encontrado."); return
                question = self.db.get_user_data(username).get('secret_question')
                if not question: show_error(recovery_window, "Erro", "Nenhuma pergunta secreta cadastrada."); recovery_window.destroy(); return
                show_step_2(username, question)

            advance_btn = tk.Button(step_frame, text="Avançar", command=process_step_1, bg=self.colors['primary'], fg='white', font=self.fonts['button'], relief="flat", padx=20, pady=8, cursor="hand2")
            advance_btn.pack(fill=tk.X, pady=(20, 0))
            
            # Atalhos de teclado
            recovery_window.bind('<Return>', lambda e: process_step_1())
            recovery_window.bind('<Escape>', lambda e: recovery_window.destroy())
            advance_btn.focus_set()

        def show_step_2(username, question):
            for widget in step_frame.winfo_children(): widget.destroy()
            tk.Label(step_frame, text="Passo 2 de 3: Pergunta Secreta", font=self.fonts['title'], bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 15))
            tk.Label(step_frame, text=question, font=self.fonts['body'], bg=self.colors['input_bg'], fg=self.colors['text'], wraplength=300, justify="center", relief="solid", bd=1).pack(fill=tk.X, ipady=10, pady=(0, 15))
            
            # Frame para resposta secreta com botão de visualizar
            answer_frame = tk.Frame(step_frame, bg=self.colors['card'])
            answer_frame.pack(fill=tk.X, pady=5)
            
            answer_container, answer_entry = self._create_icon_entry(answer_frame, "🔑", "Sua Resposta Secreta", show="•")
            answer_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Botão para mostrar/ocultar resposta secreta
            show_answer_var = tk.BooleanVar(value=False)
            
            def toggle_answer_visibility():
                is_placeholder = answer_entry.get() == getattr(answer_entry, '_placeholder', None)
                if not is_placeholder:
                    answer_entry.config(show="" if show_answer_var.get() else "•")
            
            try:
                show_answer_button = tk.Checkbutton(answer_frame, image=self.eye_closed_photo, 
                                                  selectimage=self.eye_open_photo, 
                                                  variable=show_answer_var, 
                                                  command=toggle_answer_visibility, 
                                                  bg=self.colors['card'], 
                                                  activebackground=self.colors['card'],
                                                  selectcolor=self.colors['card'],
                                                  highlightthickness=0,
                                                  indicatoron=0, bd=0, relief="flat", cursor="hand2")
                show_answer_button.pack(side=tk.RIGHT, padx=(5, 0))
            except:
                # Fallback se as imagens não estiverem disponíveis
                pass

            def process_step_2():
                answer = answer_entry.get()
                if not answer or answer == "Sua Resposta Secreta": show_error(recovery_window, "Erro", "A resposta não pode estar em branco."); return
                if self.db.verify_secret_answer(username, answer): show_step_3(username)
                else: show_error(recovery_window, "Erro", "Resposta incorreta.")

            verify_btn = tk.Button(step_frame, text="Verificar Resposta", command=process_step_2, bg=self.colors['primary'], fg='white', font=self.fonts['button'], relief="flat", padx=20, pady=8, cursor="hand2")
            verify_btn.pack(fill=tk.X, pady=(20, 0))
            
            # Atalhos de teclado
            recovery_window.bind('<Return>', lambda e: process_step_2())
            recovery_window.bind('<Escape>', lambda e: recovery_window.destroy())
            verify_btn.focus_set()

        def show_step_3(username):
            for widget in step_frame.winfo_children(): widget.destroy()
            tk.Label(step_frame, text="Passo 3 de 3: Definir Nova Senha", font=self.fonts['title'], bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 20))
            pass_container, pass_entry = self._create_icon_entry(step_frame, "lock", "Nova Senha", show="•")
            pass_container.pack(fill=tk.X, pady=5)
            confirm_container, confirm_entry = self._create_icon_entry(step_frame, "lock", "Confirmar Nova Senha", show="•")
            confirm_container.pack(fill=tk.X, pady=5)

            def process_step_3():
                new_pass, confirm_pass = pass_entry.get(), confirm_entry.get()
                if new_pass != confirm_pass: show_error(recovery_window, "Erro", "As senhas não coincidem."); return
                success, msg = self.db.set_password(username, new_pass)
                if success: show_info(recovery_window, "Sucesso", msg); recovery_window.destroy()
                else: show_error(recovery_window, "Erro", msg)
            
            save_btn = tk.Button(step_frame, text="Salvar Nova Senha", command=process_step_3, bg=self.colors['primary'], fg='white', font=self.fonts['button'], relief="flat", padx=20, pady=8, cursor="hand2")
            save_btn.pack(fill=tk.X, pady=(20, 0))
            
            # Atalhos de teclado
            recovery_window.bind('<Return>', lambda e: process_step_3())
            recovery_window.bind('<Escape>', lambda e: recovery_window.destroy())
            save_btn.focus_set()

        show_step_1()

    def _create_dialog_window(self, title, geometry="500x650"):
        dialog = tk.Toplevel(self)
        _set_window_icon(dialog)
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dialog.title(title); dialog.resizable(False, False); dialog.geometry(geometry)
        dialog.configure(bg=self.colors['card']); dialog.transient(self); dialog.grab_set()
        w, h = map(int, geometry.split('x'))
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        main_frame = tk.Frame(dialog, bg=self.colors['card'], padx=30, pady=30, highlightbackground=self.colors['shadow'], highlightthickness=1)
        main_frame.pack(fill=tk.BOTH, expand=True)
        return dialog, main_frame

    def show_register(self):
        register_window, main_frame = self._create_dialog_window("Cadastro de Novo Usuário", "450x750")
        tk.Label(main_frame, text="Criar Nova Conta", font=self.fonts['title'], bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 20))
        entries = {}
        fields = [("📧", "Email", 'email'), ("user", "Nome de Usuário", 'username'), ("lock", "Senha", 'password'), ("lock", "Confirmar Senha", 'confirm')]
        for icon, placeholder, key in fields:
            is_pass = 'Senha' in placeholder
            container, entry = self._create_icon_entry(main_frame, icon, placeholder, show="•" if is_pass else "")
            container.pack(fill=tk.X, pady=4)
            entries[key] = entry
        
        tk.Label(main_frame, text="Pergunta Secreta:", font=self.fonts['body'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor="w", padx=5, pady=(10, 2))
        question_combo = ttk.Combobox(main_frame, values=self.PREDEFINED_SECRET_QUESTIONS, state="readonly", font=self.fonts['body'])
        question_combo.set("Selecione uma pergunta"); question_combo.pack(fill=tk.X, pady=4, ipady=4)
        
        # Frame para resposta secreta com botão de visualizar
        answer_frame = tk.Frame(main_frame, bg=self.colors['card'])
        answer_frame.pack(fill=tk.X, pady=(10, 4))
        
        answer_container, entries['answer'] = self._create_icon_entry(answer_frame, "🔑", "Sua Resposta Secreta", show="•")
        answer_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão para mostrar/ocultar resposta secreta
        show_answer_var = tk.BooleanVar(value=False)
        
        def toggle_answer_visibility():
            is_placeholder = entries['answer'].get() == getattr(entries['answer'], '_placeholder', None)
            if not is_placeholder:
                entries['answer'].config(show="" if show_answer_var.get() else "•")
        
        try:
            show_answer_button = tk.Checkbutton(answer_frame, image=self.eye_closed_photo, 
                                              selectimage=self.eye_open_photo, 
                                              variable=show_answer_var, 
                                              command=toggle_answer_visibility, 
                                              bg=self.colors['card'], 
                                              activebackground=self.colors['card'],
                                              selectcolor=self.colors['card'],
                                              highlightthickness=0,
                                              indicatoron=0, bd=0, relief="flat", cursor="hand2")
            show_answer_button.pack(side=tk.RIGHT, padx=(5, 0))
        except:
            # Fallback se as imagens não estiverem disponíveis
            pass

        # Turno
        turno_frame = tk.Frame(main_frame, bg=self.colors['card'])
        turno_frame.pack(fill=tk.X, pady=(10, 10))
        tk.Label(turno_frame, text="Turno:", font=self.fonts['body'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor="w")
        turno_var = tk.StringVar(value="matutino")
        turno_options = tk.Frame(turno_frame, bg=self.colors['card'])
        turno_options.pack(fill=tk.X, pady=(5, 0))
        
        for turno_nome, turno_valor in [("Matutino", "matutino"), ("Vespertino", "vespertino"), ("Noturno", "noturno")]:
            tk.Radiobutton(turno_options, text=turno_nome, variable=turno_var, value=turno_valor,
                          bg=self.colors['card'], fg=self.colors['text'],
                          activebackground=self.colors['card'], activeforeground=self.colors['text'],
                          selectcolor=self.colors['input_bg'],
                          highlightthickness=0,
                          cursor="hand2").pack(side=tk.LEFT, padx=8)
        
        # Tipo de usuário
        role_frame = tk.Frame(main_frame, bg=self.colors['card'])
        role_frame.pack(fill=tk.X, pady=(10, 15))
        tk.Label(role_frame, text="Tipo de Usuário:", font=self.fonts['body'], bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor="w")
        role_var = tk.StringVar(value="aluno")
        role_options = tk.Frame(role_frame, bg=self.colors['card'])
        role_options.pack(fill=tk.X, pady=(5, 0))
        
        tk.Radiobutton(role_options, text="Aluno", variable=role_var, value="aluno", 
                      bg=self.colors['card'], fg=self.colors['text'],
                      activebackground=self.colors['card'], activeforeground=self.colors['text'],
                      selectcolor=self.colors['input_bg'], 
                      highlightthickness=0,
                      cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_options, text="Professor", variable=role_var, value="professor", 
                      bg=self.colors['card'], fg=self.colors['text'],
                      activebackground=self.colors['card'], activeforeground=self.colors['text'],
                      selectcolor=self.colors['input_bg'], 
                      highlightthickness=0,
                      cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_options, text="Admin", variable=role_var, value="admin", 
                      bg=self.colors['card'], fg=self.colors['text'],
                      activebackground=self.colors['card'], activeforeground=self.colors['text'],
                      selectcolor=self.colors['input_bg'], 
                      highlightthickness=0,
                      cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Terms of use checkbox and link
        terms_frame = tk.Frame(main_frame, bg=self.colors['card'])
        terms_frame.pack(fill=tk.X, pady=(10, 15))
        
        terms_var = tk.BooleanVar(value=False)
        terms_cb = tk.Checkbutton(terms_frame, text="Li e aceito os ", variable=terms_var, 
                                bg=self.colors['card'], fg=self.colors['text'],
                                activebackground=self.colors['card'], activeforeground=self.colors['text'],
                                selectcolor=self.colors['input_bg'])
        terms_cb.pack(side=tk.LEFT)
        
        terms_link = tk.Label(terms_frame, text="termos de uso", 
                            fg=self.colors['primary'], cursor="hand2", 
                            bg=self.colors['card'], font=(self.fonts['body'][0], 10, "underline"))
        terms_link.pack(side=tk.LEFT)

        def do_register():
            # reset field highlights - restaurar para cor do input_bg
            for ent in entries.values():
                try: ent.configure(bg=self.colors['input_bg'], fg=self.colors['text'])
                except Exception: pass

            vals = {k: (v.get() if v.get() != getattr(v, '_placeholder', None) else "") for k, v in entries.items()}
            question = question_combo.get()

            # terms required
            if not terms_var.get():
                show_error(register_window, "Erro", "Você precisa aceitar os termos de uso para se cadastrar.")
                return

            # Required fields: email, username, password, confirm, question, answer
            required = [('email', 'Email'), ('username', 'Nome de Usuário'), ('password', 'Senha'), ('confirm', 'Confirmar Senha')]
            for key, label in required:
                if not vals.get(key):
                    try: entries[key].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                    except Exception: pass
                    show_error(register_window, 'Erro', f'{label} é obrigatório.')
                    try: entries[key].focus_set()
                    except Exception: pass
                    return

            # secret question and answer required
            if question == 'Selecione uma pergunta':
                show_error(register_window, 'Erro', 'Selecione uma pergunta secreta.')
                try: question_combo.focus_set()
                except Exception: pass
                return
            if not vals.get('answer'):
                try: entries['answer'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                except Exception: pass
                show_error(register_window, 'Erro', 'A resposta da pergunta secreta é obrigatória.')
                try: entries['answer'].focus_set()
                except Exception: pass
                return

            # Validate email format
            if not self.db.validate_email(vals['email']):
                try: entries['email'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                except Exception: pass
                show_error(register_window, 'Erro', 'Email inválido.')
                try: entries['email'].focus_set()
                except Exception: pass
                return

            # Password strength
            is_valid, pwd_msg = self.db.validate_password(vals['password'])
            if not is_valid:
                try: entries['password'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                except Exception: pass
                show_error(register_window, 'Erro', pwd_msg)
                try: entries['password'].focus_set()
                except Exception: pass
                return

            if vals['password'] != vals['confirm']:
                try: 
                    entries['confirm'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                    entries['password'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                except Exception: pass
                show_error(register_window, 'Erro', 'As senhas não coincidem!')
                try: entries['confirm'].focus_set()
                except Exception: pass
                return

            # Check username uniqueness early
            if vals['username'] in self.db.users:
                try: entries['username'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                except Exception: pass
                show_error(register_window, 'Erro', 'Nome de usuário já existe.')
                try: entries['username'].focus_set()
                except Exception: pass
                return

            # Attempt to add user (this will also re-check constraints)
            # Novos cadastros ficam pendentes de aprovação
            success, msg = self.db.add_user(vals['username'], vals['password'], role_var.get(), 
                                           email=vals['email'] or None, pending=True, turno=turno_var.get())
            if success:
                # store secret question/answer
                self.db.set_secret_question(vals['username'], question, vals['answer'])
                show_info(register_window, 'Sucesso', msg)
                register_window.destroy()
            else:
                # highlight likely fields based on message
                if 'email' in msg.lower():
                    try: entries['email'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                    except Exception: pass
                if 'usuário' in msg.lower() or 'usuario' in msg.lower():
                    try: entries['username'].configure(bg=self.colors['error_bg'], fg=self.colors['error_text'])
                    except Exception: pass
                show_error(register_window, 'Erro', msg)

        def show_terms():
            terms_window = tk.Toplevel(register_window)
            _set_window_icon(terms_window)
            try:
                _apply_popup_theme(terms_window, self.colors, self.fonts, getattr(self, 'style', None))
            except Exception:
                pass
            terms_window.title("Termos de Uso")
            terms_window.geometry("600x400")
            terms_window.transient(register_window)
            terms_window.grab_set()
            # Apply dark mode if enabled
            colors = DARK_THEME if getattr(self, 'dark_mode', False) else LIGHT_THEME
            terms_window.configure(bg=colors['card'])
            
            # Frame para text widget com scrollbar
            text_frame = tk.Frame(terms_window, bg=colors['card'])
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(text_frame, bg=colors['card'])
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=20, pady=20, 
                                 bg=colors['card'], fg=colors['text'], 
                                 insertbackground=colors['text'],
                                 yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            terms_text = """Termos de Uso - Sistema Acadêmico

    1. Aceitação dos Termos
    Ao utilizar este sistema, você concorda com estes termos de uso em sua totalidade.

    2. Uso do Sistema
    2.1. O sistema destina-se exclusivamente para uso acadêmico e administrativo.
    2.2. Os usuários devem manter suas credenciais de acesso em sigilo.
    2.3. É proibido o compartilhamento de senhas ou acesso não autorizado.

    3. Privacidade e Dados
    3.1. Informações pessoais serão tratadas conforme a política de privacidade.
    3.2. Os dados inseridos devem ser verdadeiros e atualizados.

    4. Responsabilidades
    4.1. Os usuários são responsáveis por suas ações no sistema.
    4.2. O uso indevido pode resultar em suspensão ou cancelamento do acesso.

    5. Alterações
    5.1. Estes termos podem ser atualizados sem aviso prévio.
    5.2. Alterações significativas serão comunicadas aos usuários.

    6. Suporte
    6.1. Problemas técnicos devem ser reportados à administração.
    6.2. O suporte está disponível em horário comercial.

    Ao marcar a caixa de seleção, você confirma que leu e concorda com estes termos."""
            text_widget.insert('1.0', terms_text)
            text_widget.config(state='disabled')
            close_button = ttk.Button(terms_window, text="✕ Fechar", command=terms_window.destroy, style='Secondary.TButton')
            close_button.pack(pady=10)
            
            # Configurar atalhos (ESC fecha)
            _setup_dialog_shortcuts(terms_window, ok_button=close_button, cancel_callback=terms_window.destroy)
            # Center the window
            terms_window.update_idletasks()
            width = terms_window.winfo_width()
            height = terms_window.winfo_height()
            x = register_window.winfo_x() + (register_window.winfo_width() // 2) - (width // 2)
            y = register_window.winfo_y() + (register_window.winfo_height() // 2) - (height // 2)
            terms_window.geometry(f'+{x}+{y}')

        terms_link.bind('<Button-1>', lambda e: show_terms())

        # register_btn will call the do_register() defined earlier in this scope

        register_btn = tk.Button(main_frame, text="Cadastrar", command=do_register, bg=self.colors['primary'], fg='white', font=self.fonts['button'], relief="flat", padx=20, pady=8, cursor="hand2")
        register_btn.pack(fill=tk.X, pady=10)
        register_btn.bind('<Enter>', lambda e: register_btn.configure(background=self.colors['primary_hover']))
        register_btn.bind('<Leave>', lambda e: register_btn.configure(background=self.colors['primary']))
        
        # Atalhos de teclado
        register_window.bind('<Return>', lambda e: do_register())
        register_window.bind('<Escape>', lambda e: register_window.destroy())
        # Focar no primeiro campo
        register_window.after(100, lambda: entries['email'].focus_set())

class ToggleButton(tk.Canvas):
    """A custom, theme-aware toggle button to hide and show the sidebar."""

    def __init__(self, parent, command, colors, **kwargs):
        super().__init__(parent, width=40, bg=colors['bg'], highlightthickness=0, cursor="hand2", **kwargs)
        self.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self._command = command
        self.colors = colors
        self.is_sidebar_visible = True
        
        # --- NOVO: Inicializa a referência para a linha vertical ---
        self.vertical_line = None
        
        self._images = {}
        self._using_png = self._load_arrow_images()
        
        self._draw_button()

        self.bind('<Button-1>', lambda e: self._command())
        self.bind('<Enter>', self._on_hover)
        self.bind('<Leave>', self._on_leave)
        
        # Vincula o evento de redimensionamento para recentralizar o ícone e a linha
        self.bind('<Configure>', self._on_resize)

    def _load_arrow_images(self):
        """Loads leftarrow.png and rightarrow.png if they exist."""
        try:
            from PIL import Image, ImageTk
            
            path_left = os.path.join('img', 'leftarrow.png')
            path_right = os.path.join('img', 'rightarrow.png')

            if os.path.exists(path_left) and os.path.exists(path_right):
                img_left = Image.open(path_left).resize((35, 35), Image.Resampling.LANCZOS)
                self._images['left'] = ImageTk.PhotoImage(img_left)
                
                img_right = Image.open(path_right).resize((35, 35), Image.Resampling.LANCZOS)
                self._images['right'] = ImageTk.PhotoImage(img_right)
                return True
        except Exception as e:
            print(f"[DEBUG] Could not load sidebar toggle PNGs: {e}")
        return False

    def _draw_button(self):
        """Draws the visual elements of the button without setting a fixed position."""
        self.delete("all")
        
        arrow_to_draw_is_left = getattr(self, 'is_sidebar_visible', True)
        
        if self._using_png:
            image_to_use = self._images['left'] if arrow_to_draw_is_left else self._images['right']
            self.icon = self.create_image(0, 0, image=image_to_use)
        else:
            is_light = self.colors['bg'] == LIGHT_THEME['bg']
            circle_fill = '#FFFFFF' if is_light else '#2A2A3A'
            circle_outline = '#CCCCCC' if is_light else '#3B3B3B'
            icon_color = '#333333' if is_light else '#E6EEF8'
            
            self.circle = self.create_oval(0, 0, 0, 0, outline=circle_outline, width=0, fill=circle_fill)
            text_to_use = "◀" if arrow_to_draw_is_left else "▶"
            self.icon = self.create_text(0, 0, text=text_to_use, font=('Segoe UI Symbol', 14, 'bold'), fill=icon_color)
            
        # --- NOVO: Cria a linha vertical pela primeira vez ---
        self.vertical_line = self.create_line(0, 0, 0, 0, width=0)
        # Atualiza a linha e o ícone para suas posições corretas
        self._update_all_elements()

    def _on_resize(self, event=None):
        """Callback for when the canvas is resized."""
        self._update_all_elements()
        
    def _update_all_elements(self):
        """Centraliza o ícone e atualiza a posição e cor da linha vertical."""
        if not hasattr(self, 'icon') or not self.winfo_exists():
            return

        # 1. Atualiza o ícone (centraliza)
        canvas_height = self.winfo_height()
        canvas_width = self.winfo_width()
        center_y = canvas_height / 2
        center_x = canvas_width / 2

        if self._using_png:
            self.coords(self.icon, center_x, center_y)
        else:
            radius = 14
            self.coords(self.circle, center_x - radius, center_y - radius, center_x + radius, center_y + radius)
            self.coords(self.icon, center_x, center_y)

        # 2. Atualiza a linha vertical
        if self.vertical_line:
            is_light_theme = self.colors.get('bg', '') == LIGHT_THEME.get('bg', '')
            
            # Define a cor com base no tema
            if is_light_theme:
                line_color = 'white'
            else:
                line_color = self.colors.get('card', '#1E1E2F') # Azul claro do tema escuro
            
            # Define a posição X com base no estado da sidebar
            if self.is_sidebar_visible:
                # Aberta: linha à direita
                line_x = canvas_width - 2
            else:
                # Fechada: linha à esquerda
                line_x = 2
                
            # Atualiza as coordenadas e a cor da linha
            self.coords(self.vertical_line, line_x, 0, line_x, canvas_height)
            self.itemconfig(self.vertical_line, fill=line_color)

    def update_arrow(self, is_sidebar_visible):
        """Updates the arrow icon and the internal state, then updates elements."""
        self.is_sidebar_visible = is_sidebar_visible
        
        if self._using_png:
            new_image = self._images['left'] if is_sidebar_visible else self._images['right']
            self.itemconfig(self.icon, image=new_image)
        else:
            new_text = "◀" if is_sidebar_visible else "▶"
            self.itemconfig(self.icon, text=new_text)
        
        # --- NOVO: Atualiza a linha após a mudança de estado ---
        self._update_all_elements()

    def update_theme(self, new_colors):
        """Redraws the button with new theme colors, and updates all elements."""
        self.colors = new_colors
        self.configure(bg=self.colors['bg'])
        self._draw_button() # Redesenha tudo, incluindo a criação da linha
        # A chamada para _update_all_elements já está em _draw_button

    def _on_hover(self, event=None):
        """Changes appearance on hover (only for fallback text version)."""
        if not self._using_png:
            is_light = self.colors['bg'] == LIGHT_THEME['bg']
            hover_fill = '#F0F0F0' if is_light else '#3A3A4A'
            self.itemconfig(self.circle, fill=hover_fill)

    def _on_leave(self, event=None):
        """Reverts appearance when mouse leaves (only for fallback)."""
        if not self._using_png:
            is_light = self.colors['bg'] == LIGHT_THEME['bg']
            normal_fill = '#FFFFFF' if is_light else '#2A2A3A'
            self.itemconfig(self.circle, fill=normal_fill)

class App(tk.Tk):
    def __init__(self, role="professor", username="", dark_mode=False):
        super().__init__()
        self.role = role
        self.username = username
        self.db = UserDatabase()
        
        # inherit dark mode preference
        # Try to read saved preference for this user; fallback to passed dark_mode
        self.dark_mode = dark_mode
        try:
            pref = self.db.get_user_pref(self.username, 'dark_mode', None)
            if pref is not None:
                self.dark_mode = bool(pref)
        except Exception:
            pass
        
        self._setup_theme() # <-- MUDANÇA: Centraliza a configuração de estilo
        # Initialize sorting state early (used by _update_display before widgets may be created)
        self._sort_state = {}
        # Apply theme according to dark_mode flag
        try:
            self._apply_app_theme()
        except Exception:
            pass
        self._setup_window()
        self._create_menu()
        self._create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.listar_turmas()

    def _load_image_with_transparency(self, img_path, size=None):
        """Load image (PNG preferred) with alpha compositing over current background.
        Returns (PIL image, PhotoImage) tuple, or (None, None) if loading fails."""
        try:
            from PIL import Image, ImageTk
            if not os.path.exists(img_path):
                return None, None
                
            pil_img = Image.open(img_path).convert('RGBA')
            if size:
                if isinstance(size, (tuple, list)) and len(size) == 2:
                    pil_img = pil_img.resize(size, Image.LANCZOS)
                else:
                    pil_img.thumbnail(size, Image.LANCZOS)
                    
            # Composite onto current theme background
            # CORREÇÃO: Usar 'bg' para corresponder ao fundo da janela, não 'card'.
            bg_color = self.colors.get('bg', '#F0F2F5') 
            bg = Image.new('RGBA', pil_img.size, self._hex_to_rgba(bg_color))
            composed = Image.alpha_composite(bg, pil_img)
            
            photo = ImageTk.PhotoImage(composed)
            return pil_img, photo
        except Exception:
            return None, None
            
    def _hex_to_rgba(self, hex_color, alpha=255):
        """Convert #RRGGBB to RGBA tuple."""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c*2 for c in hex_color)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, alpha)
        except Exception:
            return (255, 255, 255, alpha)

    def _setup_theme(self):
        # Usar definições globais de temas
        self.colors = LIGHT_THEME.copy()
        self.fonts = DEFAULT_FONTS.copy()
        self.configure(bg=self.colors['bg'])
        # track dark mode state (default False)
        self.dark_mode = getattr(self, 'dark_mode', False)
        if self.dark_mode:
            # apply dark palette immediately
            self.colors.update(DARK_THEME)

        # --- INÍCIO DA MELHORIA DOS BOTÕES ---
        try:
            self.style = ttk.Style()
            self.style.theme_use('clam')

            # 1. Botão Primário (Entrar): Sólido e destacado
            self.style.configure('Primary.TButton',
                                background=self.colors['primary'],
                                foreground=self.colors['card'],
                                font=self.fonts['button'],
                                bordercolor=self.colors['border'],
                                padding=(12, 8),
                                borderwidth=0,  # Sem borda para um visual flat
                                relief='flat',
                                focusthickness=0) # Remove a borda pontilhada de foco
            
            self.style.map('Primary.TButton',
                           # Define uma cor de fundo um pouco mais escura para o hover
                           background=[('pressed', self.colors['primary']), 
                                       ('active', self.colors['primary_hover'])])

            # 2. Botão Secundário (Cadastrar): Estilo "Outline"
            self.style.configure('Secondary.TButton',
                                 background=self.colors['card'],         # Fundo "transparente" (cor do card)
                                 foreground=self.colors['primary'],      # Texto na cor primária
                                 font=self.fonts['button'],
                                 padding=(12, 8),
                                 relief='solid',                         # 'solid' para mostrar a borda
                                 borderwidth=1,                          # Espessura da borda
                                 bordercolor=self.colors['primary'],     # Cor da borda
                                 focusthickness=0)

            self.style.map('Secondary.TButton',
                           # No hover, o botão se preenche para dar um feedback claro
                           background=[('pressed', self.colors['primary']),
                                       ('active', self.colors['primary_hover'])],
                           # O texto fica branco (cor do card) quando preenchido
                           foreground=[('pressed', self.colors['card']),
                                       ('active', self.colors['card'])],
                           # A borda acompanha a cor do fundo no hover
                           bordercolor=[('active', self.colors['primary_hover'])])
        except Exception:
            pass

    def _apply_app_theme(self):
        """Apply the App's dark_mode to the colors and refresh UI styles/widgets."""
        if getattr(self, 'dark_mode', False):
            # Usar definição global de tema escuro
            self.colors = DARK_THEME.copy()
        else:
            # Usar definição global de tema claro
            self.colors = LIGHT_THEME.copy()
        try:
            self.configure(bg=self.colors['bg'])
        except Exception:
            pass
        # update ttk styles
        try:
            self.style.configure('.', background=self.colors['bg'], foreground=self.colors['text'], font=self.fonts['body'])
            self.style.configure("TFrame", background=self.colors['bg'])
            self.style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['text'])
            self.style.configure("Title.TLabel", background=self.colors['bg'], foreground=self.colors['text'], font=("Helvetica", 20, "bold"))
            self.style.configure("TLabelframe", background=self.colors['bg'], bordercolor=self.colors['border'])
            self.style.configure("TLabelframe.Label", background=self.colors['bg'], foreground=self.colors['text_secondary'])
            
            # --- ALTERAÇÃO NA TABELA AQUI ---
            # Adicionada a opção 'rowheight=18' para diminuir a altura das linhas
            self.style.configure("Treeview", 
                                 background=self.colors['card'], 
                                 fieldbackground=self.colors['card'], 
                                 foreground=self.colors['text'],
                                 rowheight=18) # <-- LINHA ADICIONADA
            
            self.style.configure("Treeview.Heading", background=self.colors['text'], foreground=self.colors['card'])
            
            # Custom.Treeview para tabelas de notas e presença
            self.style.configure("Custom.Treeview", 
                                background=self.colors['card'], 
                                fieldbackground=self.colors['card'], 
                                foreground=self.colors['text'],
                                borderwidth=1,
                                relief='solid',
                                rowheight=18) # <-- Adicionado aqui também para consistência
            self.style.configure("Custom.Treeview.Heading", 
                                background=self.colors['primary'], 
                                foreground=self.colors['card'],
                                borderwidth=1,
                                relief='raised')
            self.style.map("Custom.Treeview", 
                          background=[('selected', self.colors['primary'])],
                          foreground=[('selected', self.colors['card'])])
            
            # Combobox styling para melhor legibilidade
            self.style.configure("TCombobox", 
                                fieldbackground=self.colors['input_bg'], 
                                background=self.colors['card'],
                                foreground=self.colors['text'],
                                arrowcolor=self.colors['text'],
                                bordercolor=self.colors['border'],
                                lightcolor=self.colors['border'],
                                darkcolor=self.colors['border'],
                                selectbackground=self.colors['primary'],
                                selectforeground=self.colors['card'])
            self.style.map("TCombobox",
                          fieldbackground=[('readonly', self.colors['input_bg']),
                                          ('disabled', self.colors['border'])],
                          foreground=[('readonly', self.colors['text']),
                                     ('disabled', self.colors['text_secondary'])],
                          background=[('active', self.colors['hover'] if getattr(self, 'dark_mode', False) else self.colors['border'])])
            
            # TEntry styling para campos de entrada
            self.style.configure("TEntry",
                                fieldbackground=self.colors['input_bg'],
                                foreground=self.colors['text'],
                                bordercolor=self.colors['border'],
                                lightcolor=self.colors['border'],
                                darkcolor=self.colors['border'],
                                insertcolor=self.colors['text'])
            self.style.map("TEntry",
                          fieldbackground=[('readonly', self.colors['border']),
                                          ('disabled', self.colors['border'])],
                          foreground=[('disabled', self.colors['text_secondary'])])
            
            # TNotebook styling para abas em popups
            self.style.configure("TNotebook", 
                                background=self.colors['card'], 
                                bordercolor=self.colors['border'],
                                lightcolor=self.colors['border'],
                                darkcolor=self.colors['border'])
            self.style.configure("TNotebook.Tab", 
                                background=self.colors['border'], 
                                foreground=self.colors['text'],
                                padding=[8, 3],
                                borderwidth=0)
            self.style.map("TNotebook.Tab", 
                          background=[('selected', self.colors['primary']),
                                     ('active', self.colors['hover'] if getattr(self, 'dark_mode', False) else self.colors['border'])],
                          foreground=[('selected', self.colors['card']),
                                     ('active', self.colors['text'])])
            
            # --- ALTERAÇÃO NOS BOTÕES AQUI ---
            # Botão padrão com hover sutil e bordas de alto contraste.
            if not getattr(self, 'dark_mode', False):
                # MODO CLARO
                btn_bg = self.colors.get('text_secondary', '#6B778C')  # Fundo cinza-azulado
                btn_fg = self.colors.get('card', '#FFFFFF')
                btn_hover = '#5A677D'  # Um tom de cinza sutilmente mais escuro para o hover
                btn_border = 'black'  # Borda preta, como solicitado
            else:
                # MODO ESCURO
                btn_bg = self.colors.get('primary')
                btn_fg = self.colors.get('card')
                btn_hover = self.colors.get('primary_hover')
                btn_border = '#CCCCCC'  # Borda cinza clara, como solicitado

            self.style.configure("TButton", 
                                background=btn_bg, 
                                foreground=btn_fg, 
                                padding=(10, 5), 
                                font=('Helvetica', 9, 'bold'),
                                borderwidth=1,         # Largura da borda
                                relief='solid',        # Estilo da borda para que ela apareça
                                bordercolor=btn_border)  # Cor da borda definida para cada tema

            # Mapa de estilo para o efeito "hover" (mouse sobre)
            # A borda agora é estática, então não precisamos mapeá-la
            self.style.map("TButton", 
                        background=[('active', btn_hover),
                                    ('pressed', btn_bg)],
                        foreground=[('active', btn_fg),
                                    ('pressed', btn_fg)])
            
            # Estilo para botões de diálogo padronizados (primário)
            self.style.configure('Dialog.TButton', 
                                background=btn_bg, 
                                foreground=btn_fg, 
                                padding=(15, 5),
                                font=('Arial', 10, 'bold'),
                                borderwidth=0,
                                relief='flat')
            self.style.map('Dialog.TButton', 
                          background=[('active', btn_hover),
                                     ('pressed', btn_bg)],
                          foreground=[('active', 'white'),
                                     ('pressed', 'white')])
            
            # Estilo para botões de perigo (exclusão)
            self.style.configure('Danger.TButton', 
                                background='#dc3545', 
                                foreground='white', 
                                padding=(15, 5),
                                font=('Arial', 10, 'bold'),
                                borderwidth=0,
                                relief='flat')
            self.style.map('Danger.TButton', 
                          background=[('active', '#c82333'),
                                     ('pressed', '#a71d2a')],
                          foreground=[('active', 'white'),
                                     ('pressed', 'white')])
            
            # Estilo para botões de sucesso (aprovar)
            self.style.configure('Success.TButton', 
                                background='#4CAF50', 
                                foreground='white', 
                                padding=(15, 5),
                                font=('Arial', 10, 'bold'),
                                borderwidth=0,
                                relief='flat')
            self.style.map('Success.TButton', 
                          background=[('active', '#45a049'),
                                     ('pressed', '#3d8b40')],
                          foreground=[('active', 'white'),
                                     ('pressed', 'white')])
            
            # Estilo para botões secundários (cancelar, voltar)
            self.style.configure('Secondary.TButton', 
                                background=self.colors.get('card'), 
                                foreground=self.colors.get('text'), 
                                padding=(15, 5),
                                font=('Arial', 10),
                                relief='solid',
                                borderwidth=2,
                                bordercolor=self.colors.get('border'))
            self.style.map('Secondary.TButton', 
                          background=[('active', self.colors.get('hover', self.colors['border'])),
                                     ('pressed', self.colors.get('border'))],
                          foreground=[('active', self.colors.get('text')),
                                     ('pressed', self.colors.get('text'))],
                          bordercolor=[('active', self.colors.get('primary')),
                                      ('pressed', self.colors.get('primary'))])
            
            # Scrollbar com design aprimorado e setas
            if not getattr(self, 'dark_mode', False):
                # Cores para o Modo Claro
                trough_color = '#F0F0F0'  # Fundo da calha
                slider_color = '#BDBDBD'  # A barra que se move
                arrow_color = '#424242'   # Cor das setas
                slider_active = '#9E9E9E' # Cor da barra ao passar o mouse
            else:
                # Cores para o Modo Escuro
                trough_color = self.colors['bg']
                slider_color = '#555555'
                arrow_color = self.colors['text']
                slider_active = '#757575'
            
            self.style.configure("Vertical.TScrollbar",
                                troughcolor=trough_color,
                                background=slider_color,
                                bordercolor=trough_color,
                                arrowcolor=arrow_color,
                                lightcolor=trough_color,
                                darkcolor=trough_color,
                                arrowsize=14,  # <-- NOVO: Define o tamanho das setas
                                width=16)      # <-- AUMENTADO: Para acomodar as setas
            
            self.style.map("Vertical.TScrollbar",
                          background=[('active', slider_active),
                                     ('pressed', slider_active)])
            
            # Estilo consistente para a scrollbar horizontal (caso seja usada)
            self.style.configure("Horizontal.TScrollbar",
                                troughcolor=trough_color,
                                background=slider_color,
                                bordercolor=trough_color,
                                arrowcolor=arrow_color,
                                lightcolor=trough_color,
                                darkcolor=trough_color,
                                arrowsize=14,
                                height=16)
            
            self.style.map("Horizontal.TScrollbar",
                          background=[('active', slider_active),
                                     ('pressed', slider_active)])

            # update treeview row tag colors
            try:
                if hasattr(self, 'display_tree') and self.display_tree:
                    self.display_tree.tag_configure('odd', background=self.colors.get('row_odd', self.colors['card']))
                    self.display_tree.tag_configure('even', background=self.colors.get('row_even', self.colors['card']))
                    self.display_tree.tag_configure('aprovado', foreground='#3CB371')
                    self.display_tree.tag_configure('reprovado', foreground='#F44336')
            except Exception:
                pass

        except Exception:
            pass
        
        # Aplicar tema aos messageboxes
        try:
            _apply_messagebox_theme(self.colors, self.fonts)
        except Exception:
            pass
        
        # Atualizar cores dos menus
        try:
            if hasattr(self, 'menubar'):
                menu_bg = self.colors.get('card', '#FFFFFF')
                menu_fg = self.colors.get('text', '#172B4D')
                menu_active_bg = self.colors.get('primary', '#0052CC')
                menu_active_fg = self.colors.get('card', '#FFFFFF')
                
                self.menubar.configure(
                    bg=menu_bg,
                    fg=menu_fg,
                    activebackground=menu_active_bg,
                    activeforeground=menu_active_fg
                )
                
                for i in range(self.menubar.index('end') + 1):
                    try:
                        menu = self.menubar.nametowidget(self.menubar.entrycget(i, 'menu'))
                        if menu:
                            menu.configure(
                                bg=menu_bg,
                                fg=menu_fg,
                                activebackground=menu_active_bg,
                                activeforeground=menu_active_fg
                            )
                    except Exception:
                        continue
        except Exception:
            pass

    def _manage_scrollbar_visibility(self, canvas, scrollbar, content_frame):
        """Mostra a scrollbar apenas se o conteúdo for maior que a área visível, usando um método robusto."""
        # O evento <Configure> já garante que a geometria está sendo atualizada.
        
        # Usamos canvas.bbox("all") que retorna a caixa delimitadora (x1, y1, x2, y2) de todo o conteúdo.
        # É a maneira mais confiável de medir a altura real do conteúdo.
        bbox = canvas.bbox("all")
        
        # bbox será None se o canvas estiver vazio.
        content_height = bbox[3] if bbox else 0  # A altura é a coordenada y2 (índice 3)

        canvas_height = canvas.winfo_height()

        # Adiciona ou remove a scrollbar com base na comparação
        if content_height > canvas_height:
            # Verifica se a scrollbar já não está visível para evitar repetições
            if not scrollbar.winfo_viewable():
                scrollbar.pack(side="right", fill="y", padx=(5, 0))
        else:
            # Verifica se a scrollbar está visível antes de tentar removê-la
            if scrollbar.winfo_viewable():
                scrollbar.pack_forget()

    def _setup_window(self):
        self.title(f"Sistema Acadêmico - {self.role.title()}: {self.username}")
        self.geometry("1200x700")
        try:
            self.iconbitmap("img/icone.ico")
        except tk.TclError:
            pass # Continua se o ícone não for encontrado
        # Abrir a janela maximizada (Windows: 'zoomed')
        try:
            # state 'zoomed' maximizes on Windows
            self.state('zoomed')
        except Exception:
            try:
                # fallback para alguns ambientes X11
                self.wm_attributes('-zoomed', True)
            except Exception:
                pass

    def _create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        menubar = self.menubar  # Compatibilidade com código existente
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Trocar Usuário", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Tema com opções
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tema", menu=theme_menu)
        
        # Variável para rastrear tema atual
        self._theme_var = tk.IntVar(value=1 if self.dark_mode else 0)
        
        def set_light_theme():
            self.dark_mode = False
            self._theme_var.set(0)
            try:
                self.db.set_user_pref(self.username, 'dark_mode', False)
            except Exception:
                pass
            self._apply_app_theme()
            self._update_widgets_theme()
        
        def set_dark_theme():
            self.dark_mode = True
            self._theme_var.set(1)
            try:
                self.db.set_user_pref(self.username, 'dark_mode', True)
            except Exception:
                pass
            self._apply_app_theme()
            self._update_widgets_theme()
        
        theme_menu.add_radiobutton(label="Modo Claro", variable=self._theme_var, value=0, command=set_light_theme)
        theme_menu.add_radiobutton(label="Modo Escuro", variable=self._theme_var, value=1, command=set_dark_theme)
        
        # Menu de administração (apenas para admins) - ADICIONAR ANTES DO TEMA
        if self.role == 'admin':
            # Contar usuários pendentes
            pending_count = len(self.db.get_pending_users())
            
            # Criar label do menu com badge de notificação se houver pendentes
            if pending_count > 0:
                admin_label = f'Administração ({pending_count})'
            else:
                admin_label = 'Administração'
            
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label=admin_label, menu=admin_menu)
            # Armazenar índice do menu de administração DEPOIS de adicionar
            self._admin_menu_index = menubar.index('end')
            # Salvar referência ao submenu para poder atualizar itens
            self._admin_submenu = admin_menu
            
            # Label do menu com indicador se houver pendentes
            aprovar_label = f'⏳ Aprovar Cadastros Pendentes ({pending_count})' if pending_count > 0 else 'Aprovar Cadastros Pendentes'
            admin_menu.add_command(label=aprovar_label, command=self.aprovar_cadastros)
            self._aprovar_menu_item_index = 0  # Índice do item "Aprovar Cadastros"
            
            admin_menu.add_command(label='Gerenciar Usuários', command=self.gerenciar_usuarios)
            admin_menu.add_separator()
            admin_menu.add_command(label='Gerenciar Acessos de Professores', command=self.gerenciar_acessos_professores)
            admin_menu.add_separator()
            admin_menu.add_command(label='Listar Usuários', command=self.listar_usuarios_consolidado)
        
        # Menu do Aluno (apenas para alunos)
        if self.role == 'aluno':
            aluno_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label='Minhas Informações', menu=aluno_menu)
            aluno_menu.add_command(label='Ver Minhas Notas', command=self.ver_minhas_notas)
            aluno_menu.add_command(label='Ver Minhas Faltas', command=self.ver_minhas_faltas)
            aluno_menu.add_separator()
            aluno_menu.add_command(label='Ver Presenças por Data', command=self.ver_presencas_por_data)
        
        # Menu de Perfil (para todos os usuários)
        perfil_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Meu Perfil', menu=perfil_menu)
        perfil_menu.add_command(label='Ver/Editar Perfil', command=self.ver_editar_perfil)
        perfil_menu.add_separator()
        perfil_menu.add_command(label='Editar Email', command=self.editar_meu_email)
        perfil_menu.add_command(label='Alterar Senha', command=self.alterar_minha_senha)
        
        # Add Sobre menu item to show credits
        def show_about():
            about = tk.Toplevel(self)
            try:
                _apply_popup_theme(about, self.colors, self.fonts, getattr(self, 'style', None))
            except Exception:
                pass
            try:
                _set_window_icon(about)
            except Exception:
                pass
            about.title('Sobre o Sistema Acadêmico')
            about.geometry('600x500')
            about.transient(self); about.grab_set()
            
            # Centralizar janela
            about.update_idletasks()
            x = (about.winfo_screenwidth() // 2) - (600 // 2)
            y = (about.winfo_screenheight() // 2) - (500 // 2)
            about.geometry(f'600x500+{x}+{y}')
            
            # Use same colors/fonts as app
            card_bg = self.colors.get('card')
            about.configure(bg=card_bg)
            
            # Frame principal com scrollbar
            main_frame = tk.Frame(about, bg=card_bg)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Canvas para scrollbar
            canvas = tk.Canvas(main_frame, bg=card_bg, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=card_bg)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Título principal
            title_label = tk.Label(scrollable_frame, text='Sistema Acadêmico UNIP', 
                                 font=('Arial', 16, 'bold'), bg=card_bg, fg=self.colors.get('primary'))
            title_label.pack(pady=(0, 15))
            
            # Versão e informações do sistema
            version_frame = tk.Frame(scrollable_frame, bg=card_bg)
            version_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(version_frame, text='Versão: 2.0.0', font=('Arial', 10, 'bold'), 
                    bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(version_frame, text='Desenvolvido em: Python 3.x + Tkinter', 
                    font=('Arial', 9), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(version_frame, text='Banco de dados: C (DLL/SO)', 
                    font=('Arial', 9), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            
            # Equipe de desenvolvimento
            team_frame = tk.Frame(scrollable_frame, bg=card_bg)
            team_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(team_frame, text='👥 Equipe de Desenvolvimento', 
                    font=('Arial', 12, 'bold'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w', pady=(0, 8))
            
            team_members = [
                ('Danilo Oliveira', 'R660648', ''),
                ('Eduardo Juan', 'R590AJ8', ''),
                ('Adriano Junior', 'H7451E8', ''),
                ('João Acerbi', 'R855DD4', ''),
                ('Rafael Botti', 'R8497A1', '')
            ]
            
            for name, ra, role in team_members:
                member_frame = tk.Frame(team_frame, bg=card_bg)
                member_frame.pack(fill=tk.X, pady=2)
                tk.Label(member_frame, text=f'• {name} ({ra})', 
                        font=('Arial', 10, 'bold'), bg=card_bg, fg=self.colors.get('text')).pack(side=tk.LEFT)
                tk.Label(member_frame, text=f' - {role}', 
                        font=('Arial', 9), bg=card_bg, fg=self.colors.get('text')).pack(side=tk.LEFT)
            
            # Informações acadêmicas
            academic_frame = tk.Frame(scrollable_frame, bg=card_bg)
            academic_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(academic_frame, text='🏫 Informações Acadêmicas', 
                    font=('Arial', 12, 'bold'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w', pady=(0, 8))
            tk.Label(academic_frame, text='Faculdade: UNIP - Universidade Paulista', 
                    font=('Arial', 10), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(academic_frame, text='Curso: Ciência da Computação', 
                    font=('Arial', 10), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(academic_frame, text='Trabalho: PIM - Projeto Integrado Multidisciplinar', 
                    font=('Arial', 10), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(academic_frame, text='Semestre: 2025/1', 
                    font=('Arial', 10), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            
            # Funcionalidades do sistema
            features_frame = tk.Frame(scrollable_frame, bg=card_bg)
            features_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(features_frame, text='⚙️ Funcionalidades do Sistema', 
                    font=('Arial', 12, 'bold'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w', pady=(0, 8))
            
            features = [
                '• Gerenciamento de turmas e disciplinas',
                '• Cadastro e controle de alunos',
                '• Lançamento de notas (NP1, NP2, PIM)',
                '• Controle de presença',
                '• Upload e download de atividades',
                '• Sistema de anotações pessoais',
                '• Interface responsiva com tema dark/light',
                '• Sistema de níveis de acesso (Admin/Professor)',
                '• Exportação de dados em múltiplos formatos'
            ]
            
            for feature in features:
                tk.Label(features_frame, text=feature, 
                        font=('Arial', 9), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w', padx=(10, 0))
            
            # Tecnologias utilizadas
            tech_frame = tk.Frame(scrollable_frame, bg=card_bg)
            tech_frame.pack(fill=tk.X, pady=(0, 15))
            
            tk.Label(tech_frame, text='💻 Tecnologias Utilizadas', 
                    font=('Arial', 12, 'bold'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w', pady=(0, 8))
            tk.Label(tech_frame, text='Python 3.x, Tkinter, C (DLL), JSON, Threading', 
                    font=('Arial', 9), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            
            # Copyright
            copyright_frame = tk.Frame(scrollable_frame, bg=card_bg)
            copyright_frame.pack(fill=tk.X, pady=(10, 0))
            
            tk.Label(copyright_frame, text='© 2025 - Equipe de Desenvolvimento UNIP', 
                    font=('Arial', 8, 'italic'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            tk.Label(copyright_frame, text='Todos os direitos reservados', 
                    font=('Arial', 8, 'italic'), bg=card_bg, fg=self.colors.get('text')).pack(anchor='w')
            
            # Configurar scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Botão fechar
            button_frame = tk.Frame(about, bg=card_bg)
            button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
            close_btn = ttk.Button(button_frame, text='Fechar', command=about.destroy)
            close_btn.pack(side=tk.RIGHT)
            
            # Configurar atalhos (ESC fecha)
            _setup_dialog_shortcuts(about, ok_button=close_btn, cancel_callback=about.destroy)
            
            # Habilitar scroll com mousewheel
            _enable_canvas_scroll(canvas, scrollable_frame)
        
        menubar.add_command(label='Sobre', command=show_about)
        
    def _create_widgets(self):
        self._last_turma = None
        self._sidebar_visible = True

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- ETAPA 1: Criar e empacotar os widgets principais do layout ---
        
        # 1. SIDEBAR FRAME
        self.sidebar_frame = tk.Frame(main_frame, width=210, bg=self.colors['bg'])
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        self.sidebar_frame.pack_propagate(False)

        # Área rolável dentro da sidebar (código inalterado)
        sidebar_canvas = tk.Canvas(self.sidebar_frame, bg=self.colors['bg'], highlightthickness=0)
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", command=sidebar_canvas.yview, style="Vertical.TScrollbar")
        self.sidebar_scrollable_content = ttk.Frame(sidebar_canvas)
        sidebar_canvas.create_window((0, 0), window=self.sidebar_scrollable_content, anchor="nw")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        def update_scroll_region(event=None):
            sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
            content_height = sidebar_canvas.bbox("all")[3] if sidebar_canvas.bbox("all") else 0
            if content_height > sidebar_canvas.winfo_height():
                sidebar_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                sidebar_scrollbar.pack_forget()
        
        self.sidebar_scrollable_content.bind("<Configure>", update_scroll_region)
        sidebar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 2. BOTÃO DE TOGGLE
        self.toggle_button = ToggleButton(main_frame, command=self._toggle_sidebar, colors=self.colors)

        # 3. CONTAINER DE EXIBIÇÃO PRINCIPAL
        self.display_container = ttk.Frame(main_frame)
        self.display_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- ETAPA 2: Popular os containers que já foram empacotados ---
        
        # Popular a Sidebar
        turma_frame = ttk.LabelFrame(self.sidebar_scrollable_content, text="Gerenciamento de Turmas", padding=8)
        turma_frame.pack(fill=tk.X, pady=3, padx=10)
        if self.role == 'admin':
            ttk.Button(turma_frame, text="Cadastrar Turma", command=self.cadastrar_turma).pack(fill=tk.X, pady=2)
        ttk.Button(turma_frame, text="Listar Turmas", command=self.listar_turmas).pack(fill=tk.X, pady=2)
        if self.role == 'admin':
            ttk.Button(turma_frame, text="Pesquisar Professor", command=self.pesquisar_professor).pack(fill=tk.X, pady=2)
        if self.role in ['admin', 'professor']:
            ttk.Button(turma_frame, text="Editar Turma", command=self.alterar_turma).pack(fill=tk.X, pady=2)
        ttk.Button(turma_frame, text="Calendário de Provas", command=self.calendario_provas).pack(fill=tk.X, pady=2)
        

        aluno_frame = ttk.LabelFrame(self.sidebar_scrollable_content, text="Gerenciamento de Alunos", padding=8)
        aluno_frame.pack(fill=tk.X, pady=3, padx=10)
        if self.role == 'admin':
            ttk.Button(aluno_frame, text="Cadastrar Aluno", command=self.cadastrar_aluno).pack(fill=tk.X, pady=2)
        ttk.Button(aluno_frame, text="Listar Alunos (por Turma)", command=self.listar_alunos_turma).pack(fill=tk.X, pady=2)
        if self.role == 'admin':
            ttk.Button(aluno_frame, text="Editar Aluno", command=self.editar_aluno).pack(fill=tk.X, pady=2)
        if self.role in ['admin']:
            ttk.Button(aluno_frame, text="Pesquisar Aluno", command=self.pesquisar_aluno).pack(fill=tk.X, pady=2)
        if self.role in ['admin', 'professor']:
            ttk.Button(aluno_frame, text="Lançar Notas", command=self.lancar_notas).pack(fill=tk.X, pady=2)
            ttk.Button(aluno_frame, text="Controle de Presença", command=self.controle_presenca).pack(fill=tk.X, pady=2)

        atividade_frame = ttk.LabelFrame(self.sidebar_scrollable_content, text="Atividades", padding=8)
        atividade_frame.pack(fill=tk.X, pady=3, padx=10)
        if self.role in ['admin', 'professor']:
            ttk.Button(atividade_frame, text="Upload de Atividade", command=self.upload_atividade).pack(fill=tk.X, pady=2)
        ttk.Button(atividade_frame, text="Gerenciar Atividades", command=self.listar_atividades).pack(fill=tk.X, pady=2)

        anotacoes_frame = ttk.LabelFrame(self.sidebar_scrollable_content, text="Anotações", padding=8)
        anotacoes_frame.pack(fill=tk.X, pady=3, padx=10)
        ttk.Button(anotacoes_frame, text="Gerenciar Anotações", command=self.gerenciar_anotacoes).pack(fill=tk.X, pady=2)
        
        # Popular o Container de Exibição
        self.header_label = ttk.Label(self.display_container, text="", style="Title.TLabel")
        self.header_label.pack(anchor="w", pady=(0, 5), padx=10)
        
        tree_frame = ttk.Frame(self.display_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Adicionar scrollbar vertical para o Treeview
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", style="Vertical.TScrollbar")
        
        self.display_tree = ttk.Treeview(tree_frame, style="Treeview",
                                         yscrollcommand=vsb.set)
        
        vsb.config(command=self.display_tree.yview)
        
        # Layout com grid para melhor controle
        self.display_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Configurar peso das linhas e colunas
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.display_tree.tag_configure('odd', background=self.colors['row_odd'])
        self.display_tree.tag_configure('even', background=self.colors['row_even'])
        self.display_tree.tag_configure('aprovado', foreground='#3CB371')
        self.display_tree.tag_configure('reprovado', foreground='#F44336')
        self._sort_state = {}

        # --- ETAPA 3: Criar e posicionar o header por cima de tudo ---
        
        self.header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        
        self.right_header = tk.Frame(self.header_frame, bg=self.colors['bg'])
        self.right_header.pack(side=tk.RIGHT)
        
        # Carregar imagem do samurai
        try:
            # Garanta que o caminho __file__ funcione corretamente
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "img", "samurai.png")
            
            pil_img, photo = self._load_image_with_transparency(img_path, size=(35, 35))
            if pil_img and photo:
                self._samurai_pil = pil_img
                self._samurai_photo = photo
                self._samurai_label = tk.Label(self.right_header, image=self._samurai_photo, bg=self.colors['bg'])
                self._samurai_label.pack(side=tk.LEFT, padx=(0, 8))
            else:
                # Fallback para texto caso a imagem falhe
                print(f"AVISO: Não foi possível carregar a imagem 'samurai.png' do caminho: {img_path}")
                self._samurai_label = tk.Label(self.right_header, text=" samurai ", bg=self.colors['bg'])
                self._samurai_label.pack(side=tk.LEFT, padx=(0, 8))
        except Exception as e:
            print(f"ERRO ao carregar samurai.png: {e}")

        # Label de data/hora
        self.datetime_label = tk.Label(self.right_header, text="", font=("Helvetica", 10), 
                                       bg=self.colors['bg'], fg=self.colors['text'])
        self.datetime_label.pack(side=tk.LEFT)
        
        # Posicionar o frame do header
        self.header_frame.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=-5)
        
        # Iniciar o relógio
        self._update_datetime()

    def _toggle_sidebar(self):
        """Shows or hides the sidebar frame."""
        self._sidebar_visible = not self._sidebar_visible
        
        if self._sidebar_visible:
            # Re-pack the sidebar frame before the toggle button
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), before=self.toggle_button)
        else:
            # Simply hide the sidebar frame
            self.sidebar_frame.pack_forget()
        
        # Update the arrow icon on the button to reflect the new state
        self.toggle_button.update_arrow(self._sidebar_visible)
    
    def _update_datetime(self):
        """Atualiza o label de data/hora no topo direito."""
        try:
            now = datetime.now()
            # Formato: Sexta-feira, 17/10/2025 - 14:30:45
            dias_semana = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                          'Sexta-feira', 'Sábado', 'Domingo']
            dia_semana = dias_semana[now.weekday()]
            data_hora = f"{dia_semana}, {now.strftime('%d/%m/%Y - %H:%M:%S')}"
            
            if hasattr(self, 'datetime_label'):
                self.datetime_label.config(text=data_hora)
            
            # Atualizar a cada segundo
            self.after(1000, self._update_datetime)
        except Exception:
            pass

    def _update_widgets_theme(self):
        """Updates all custom widgets when the application theme changes."""
        # Update the theme of the custom toggle button
        if hasattr(self, 'toggle_button'):
            self.toggle_button.update_theme(self.colors)
        
        # Update header frames background
        if hasattr(self, 'header_frame'):
            self.header_frame.configure(bg=self.colors['bg'])
        
        if hasattr(self, 'right_header'):
            self.right_header.configure(bg=self.colors['bg'])
        
        # Update header widgets (datetime label)
        if hasattr(self, 'datetime_label'):
            self.datetime_label.configure(bg=self.colors['bg'], fg=self.colors['text'])
        
        # Update samurai image with new background
        if hasattr(self, '_samurai_label') and hasattr(self, '_samurai_pil'):
            try:
                from PIL import Image, ImageTk
                bg_color = self.colors.get('bg', '#F0F2F5')
                # Recompor a imagem com o novo fundo
                bg_image = Image.new('RGBA', self._samurai_pil.size, self._hex_to_rgba(bg_color))
                composed_image = Image.alpha_composite(bg_image, self._samurai_pil)
                self._samurai_photo = ImageTk.PhotoImage(composed_image)
                self._samurai_label.configure(image=self._samurai_photo, bg=bg_color)
            except Exception:
                pass
            
        # Update the main sidebar frame background
        if hasattr(self, 'sidebar_frame'):
            self.sidebar_frame.configure(bg=self.colors['bg'])
            # Also update its child canvas and scrollable content frame
            try:
                for child in self.sidebar_frame.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.configure(bg=self.colors['bg'])
                        # Update the frame inside the canvas
                        for inner_child in child.winfo_children():
                             if isinstance(inner_child, ttk.Frame):
                                 # This is the self.sidebar_scrollable_content
                                 # Its style will be updated by _apply_app_theme
                                 pass
            except Exception:
                pass

        self.update_idletasks()
    
    def _update_admin_menu_label(self):
        """Atualiza o label do menu Administração com o contador de pendentes"""
        if self.role != 'admin' or not hasattr(self, '_admin_menu_index'):
            return
        
        pending_count = len(self.db.get_pending_users())
        
        # Criar novo label para o menu principal
        if pending_count > 0:
            new_label = f'Administração ({pending_count} pendente{"s" if pending_count > 1 else ""})'
        else:
            new_label = 'Administração'
        
        # Atualizar o label do menu principal
        try:
            self.menubar.entryconfig(self._admin_menu_index, label=new_label)
        except Exception as e:
            print(f"[DEBUG] Erro ao atualizar menu principal: {e}")
        
        # Atualizar também o item "Aprovar Cadastros Pendentes" no submenu
        try:
            if hasattr(self, '_admin_submenu') and hasattr(self, '_aprovar_menu_item_index'):
                aprovar_label = f'⏳ Aprovar Cadastros Pendentes ({pending_count})' if pending_count > 0 else 'Aprovar Cadastros Pendentes'
                self._admin_submenu.entryconfig(self._aprovar_menu_item_index, label=aprovar_label)
        except Exception as e:
            print(f"[DEBUG] Erro ao atualizar item do submenu: {e}")
    
    def _refresh_pending_notification(self):
        """Atualiza apenas o contador de pendentes no menu Administração"""
        if self.role != 'admin':
            return
        
        # Atualizar menu
        self._update_admin_menu_label()
    
    # O restante dos métodos da classe App (on_closing, logout, etc.) permanecem os mesmos
    # ...
    def on_closing(self):
        # Use a small custom confirmation dialog to ensure icon is set
        dlg = tk.Toplevel(self)
        dlg.configure(bg=self.colors['bg'])
        _set_window_icon(dlg)
        try:
            _apply_popup_theme(dlg, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dlg.title("Sair")
        dlg.geometry("320x120")
        dlg.transient(self); dlg.grab_set()
        _center_window(dlg)
        
        ttk.Label(dlg, text="Deseja sair?", font=self.fonts['title']).pack(pady=(10,5))
        
        frm = ttk.Frame(dlg)
        frm.pack(pady=10)
        
        def do_exit():
            dlg.destroy(); self.destroy()
        def do_cancel():
            dlg.destroy()
        
        # Criar botões e focar no principal
        exit_btn = ttk.Button(frm, text="Sair", command=do_exit)
        exit_btn.pack(side=tk.LEFT, padx=8)
        cancel_btn = ttk.Button(frm, text="Cancelar", command=do_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=8)
        
        # Bindings de teclado
        dlg.bind('<Return>', lambda e: do_exit())
        dlg.bind('<Escape>', lambda e: do_cancel())
        
        # Focar no botão Sair após o diálogo ser exibido
        dlg.after(100, lambda: exit_btn.focus_set())
            
    def logout(self):
        if messagebox.askokcancel("Logout", "Deseja trocar de usuário?"):
            # Calcular tempo de uso desta sessão
            if self.username in self.db.users:
                import datetime
                login_time = self.db.users[self.username].get('login_time')
                if login_time:
                    session_time = datetime.datetime.now().timestamp() - login_time
                    current_total = self.db.users[self.username].get('total_time', 0)
                    self.db.users[self.username]['total_time'] = current_total + session_time
                    self.db.users[self.username]['login_time'] = None
                    self.db.save_users()
            
            self.destroy()
            login = LoginWindow()
            login.mainloop()
            
    def view_profile(self):
        user_data = self.db.get_user_data(self.username)
        if user_data:
            info = f"Usuário: {self.username}\n"
            info += f"Função: {user_data['role']}\n"
            info += f"Email: {user_data['email'] or 'Não cadastrado'}\n"
            messagebox.showinfo("Perfil do Usuário", info)
            
    def _send_request(self, request, buffer=8192):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT)); s.sendall(request.encode('utf-8')); return s.recv(buffer).decode('utf-8')
        except Exception as e: messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao servidor: {e}"); return None

    def _update_display(self, title, headers, data):
        """Atualiza o display com novos dados"""
        try:
            # Atualiza o cabeçalho se existir
            if hasattr(self, 'header_label'):
                self.header_label.configure(text=title)
            
            # Verifica se o display_tree existe
            if not hasattr(self, 'display_tree') or not self.display_tree:
                messagebox.showerror("Erro", "Erro na inicialização da visualização")
                return

            # Limpa a árvore existente
            for item in self.display_tree.get_children():
                self.display_tree.delete(item)
            
            # Configura as colunas
            self.display_tree["columns"] = headers
            self.display_tree["show"] = "headings"
            
            # Configura os cabeçalhos (tornando-os clicáveis para ordenação)
            for col in headers:
                # Show arrow if this column is currently sorted
                arrow = ''
                if col in self._sort_state:
                    arrow = ' ▲' if not self._sort_state.get(col, False) else ' ▼'
                # Use a lambda capture to bind the column name
                self.display_tree.heading(col, text=f"{col}{arrow}", anchor=tk.CENTER,
                                          command=lambda _col=col: self._sort_by(_col, False))
                self.display_tree.column(col, anchor=tk.CENTER, minwidth=100)
            
            # Insere os dados com cores alternadas e status coloring when present
            for i, row in enumerate(data):
                tags = ('even' if i % 2 == 0 else 'odd',)
                # If there's a Status column, apply color tag
                if len(row) > 0 and headers and headers[-1] == 'Status':
                    status = str(row[-1]).lower()
                    if 'aprov' in status:
                        tags = tags + ('aprovado',)
                    elif 'reprov' in status:
                        tags = tags + ('reprovado',)
                self.display_tree.insert("", tk.END, values=row, tags=tags)
            
            # Ajusta o tamanho das colunas automaticamente
            if data:
                font = tkFont.Font()
                for col in headers:
                    max_width = font.measure(col) + 20
                    col_idx = headers.index(col)
                    
                    for row in data:
                        if col_idx < len(row):
                            cell_width = font.measure(str(row[col_idx])) + 20
                            max_width = max(max_width, cell_width)
                    
                    self.display_tree.column(col, width=min(max_width, 300))

        except Exception as e:
            print(f"Erro ao atualizar display: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar visualização: {str(e)}")
            return False
        
        return True

    def _sort_by(self, col, descending):
        """Sort tree contents when a heading is clicked."""
        try:
            # grab values to sort
            data = [(self.display_tree.set(child, col), child) for child in self.display_tree.get_children('')]

            # Custom ordering for Status column (put Reprovado first)
            if col.lower() == 'status':
                order = {'reprovado': 0, 'aprovado': 1}
                data.sort(key=lambda t: order.get(str(t[0]).strip().lower(), 2), reverse=descending)
            else:
                # Try numeric sort first
                try:
                    data.sort(key=lambda t: float(t[0]) if t[0] != '' else float('-inf'), reverse=descending)
                except Exception:
                    # Fallback to string sort
                    data.sort(key=lambda t: t[0].lower() if isinstance(t[0], str) else str(t[0]), reverse=descending)

            # reorder
            for index, (val, child) in enumerate(data):
                self.display_tree.move(child, '', index)

            # reverse sort next time and show arrow indicator
            self._sort_state = {col: descending}
            # Update header labels to reflect arrow state
            try:
                headers = list(self.display_tree['columns'])
                for h in headers:
                    arrow = ''
                    if h in self._sort_state:
                        arrow = ' ▲' if not self._sort_state.get(h, False) else ' ▼'
                    self.display_tree.heading(h, text=f"{h}{arrow}")
            except Exception:
                pass
            self.display_tree.heading(col, command=lambda: self._sort_by(col, not descending))
        except Exception as e:
            print(f"Erro ao ordenar coluna {col}: {e}")

    def _gerar_proximo_id_turma(self):
        """Gera automaticamente o próximo ID de turma incremental"""
        # Obter lista de turmas primeiro
        resp = self._send_request("LIST_TURMAS")
        if not resp or "Nenhuma turma" in resp:
            return 1  # Primeira turma
        
        ids_existentes = []
        for linha in resp.strip().split('\n'):
            if linha.strip():  # Verificar se a linha não está vazia
                try:
                    # Formato esperado: "ID: X, Disciplina: Y, Professor: Z"
                    partes = linha.split(', ')
                    if len(partes) > 0:
                        id_parte = partes[0].strip()
                        if 'ID:' in id_parte or 'Id:' in id_parte or 'id:' in id_parte:
                            # Extrair número após "ID:"
                            id_str = id_parte.split(':')[1].strip()
                            id_turma = int(id_str)
                            if id_turma > 0:  # Validar que o ID é positivo
                                ids_existentes.append(id_turma)
                except (ValueError, IndexError, AttributeError) as e:
                    # Log para debug se necessário
                    print(f"Aviso: Não foi possível parsear linha: {linha}. Erro: {e}")
                    continue
        
        if ids_existentes:
            # Retornar o maior ID + 1
            proximo_id = max(ids_existentes) + 1
            print(f"Debug: IDs existentes: {sorted(ids_existentes)}, Próximo ID: {proximo_id}")
            return proximo_id
        else:
            print("Debug: Nenhum ID existente encontrado, iniciando em 1")
            return 1
    
    def cadastrar_turma(self):
        # Apenas admin pode cadastrar turmas
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem cadastrar turmas.")
            return
        
        # Criar interface customizada
        dialog = tk.Toplevel(self)
        dialog.title("Cadastrar Nova Turma")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Cadastrar Nova Turma", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # ID (apenas visualização) - será gerado no momento do cadastro
        tk.Label(main_frame, text="ID (será gerado automaticamente):", 
                font=('Arial', 10, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        id_label = tk.Label(main_frame, text="Será atribuído no cadastro", 
                font=('Arial', 11), bg=self.colors['border'], fg=self.colors['text'], 
                relief='solid', bd=1, padx=8, pady=5)
        id_label.pack(fill=tk.X, pady=(3, 15))
        
        # Disciplina
        tk.Label(main_frame, text="Disciplina:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        disciplina_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        disciplina_entry.pack(fill=tk.X, pady=(3, 15))
        
        # Professor
        tk.Label(main_frame, text="Professor:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        professor_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        professor_entry.pack(fill=tk.X, pady=(3, 15))
        
        # Turno
        tk.Label(main_frame, text="Turno:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        turno_var = tk.StringVar(value="matutino")
        turno_frame = tk.Frame(main_frame, bg=self.colors['card'])
        turno_frame.pack(fill=tk.X, pady=(3, 20))
        
        for turno_nome, turno_valor in [("Matutino", "matutino"), ("Vespertino", "vespertino"), ("Noturno", "noturno")]:
            tk.Radiobutton(turno_frame, text=turno_nome, variable=turno_var, value=turno_valor,
                          bg=self.colors['card'], fg=self.colors['text'],
                          activebackground=self.colors['card'], activeforeground=self.colors['text'],
                          selectcolor=self.colors['input_bg'],
                          highlightthickness=0,
                          cursor="hand2").pack(side=tk.LEFT, padx=8)
        
        def cadastrar():
            disciplina = disciplina_entry.get()
            professor = professor_entry.get()
            
            if not disciplina or not professor:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return
            
            # Verificar se já existe turma com esse nome de disciplina
            turmas_existentes = self._get_turmas_list()
            for turma in turmas_existentes:
                if turma['nome_disciplina'].lower() == disciplina.lower():
                    messagebox.showerror("Erro", 
                                       f"Já existe uma turma com a disciplina '{disciplina}'!\n\n"
                                       f"Turma existente: ID {turma['id']} - {turma['nome_disciplina']} ({turma['nome_professor']})\n\n"
                                       "Escolha outro nome de disciplina ou edite a turma existente.")
                    return
            
            # Gerar ID no momento do cadastro (garante ID correto mesmo se demorar para preencher)
            novo_id = self._gerar_proximo_id_turma()
            
            # Atualizar label com o ID gerado
            id_label.config(text=str(novo_id))
            
            # Criar usuário para o professor automaticamente
            prof_username = self.db.generate_username_from_name(professor)
            prof_password = self.db.generate_temp_password()
            
            # Verificar se já existe um usuário com esse nome
            user_exists = prof_username in self.db.users
            if not user_exists:
                # Criar novo usuário professor
                success, msg = self.db.add_user(prof_username, prof_password, 'professor', 
                                              turno=turno_var.get(), pending=False)
                if not success:
                    messagebox.showerror("Erro", f"Erro ao criar usuário do professor: {msg}")
                    return
            
            # Adicionar turma no sistema C
            resp = self._send_request(f"ADD_TURMA|{novo_id}|{disciplina}|{professor}")
            if resp:
                # Associar a turma ao professor (adicionar à lista de subjects)
                current_subjects = self.db.get_professor_subjects(prof_username)
                if str(novo_id) not in [str(s) for s in current_subjects]:
                    current_subjects.append(str(novo_id))
                    self.db.set_professor_subjects(prof_username, current_subjects)
                
                # Salvar turno separadamente
                set_turno_turma(novo_id, turno_var.get())
                
                # Mensagem de sucesso com informações do login
                msg_sucesso = f"Turma cadastrada com sucesso!\nID: {novo_id}\nTurno: {turno_var.get().title()}\n\n"
                if not user_exists:
                    msg_sucesso += f"🔑 Login criado automaticamente:\n"
                    msg_sucesso += f"Usuário: {prof_username}\n"
                    msg_sucesso += f"Senha: {prof_password}\n\n"
                    msg_sucesso += "⚠️ IMPORTANTE: Anote essas credenciais!\n"
                    msg_sucesso += "O professor deve fazer login e alterar a senha.\n\n"
                else:
                    msg_sucesso += f"✅ Turma associada ao usuário existente: {prof_username}\n\n"
                
                msg_sucesso += resp
                messagebox.showinfo("Sucesso", msg_sucesso)
                dialog.destroy()
                self.listar_turmas()
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="Cadastrar", command=cadastrar, 
                  style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                  style='Secondary.TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos (ESC cancela, Enter cadastra)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
    
    def _get_turmas_list(self, filtrar_turno=True):
        """Return a list of dicts with turma info for existing turmas by querying the server.
        Se filtrar_turno=True, filtra por turno do usuário (exceto admin)."""
        resp = self._send_request("LIST_TURMAS")
        turmas = []
        if not resp or "Nenhuma turma" in resp:
            return turmas
        
        turno_usuario = self.db.users.get(self.username, {}).get('turno', 'matutino')
        
        for linha in resp.strip().split('\n'):
            if not linha: continue
            partes = linha.split(', ')
            try:
                id_turma = partes[0].split(': ')[1]
                disciplina = partes[1].split(': ')[1] if len(partes) > 1 else ''
                professor = partes[2].split(': ')[1] if len(partes) > 2 else ''
                
                # Buscar turno da turma
                turno_turma = get_turno_turma(id_turma)
                
                # Filtrar por turno se não for admin e filtro ativo
                if filtrar_turno and self.role != 'admin':
                    if turno_turma != turno_usuario:
                        continue  # Pula turmas de outros turnos
                
                # Return both tuple for backward compatibility and dict for new features
                turmas.append({
                    'id': id_turma,
                    'nome_disciplina': disciplina,
                    'nome_professor': professor,
                    'turno': turno_turma,
                    'tuple': (id_turma, f"{id_turma} - {disciplina} ({turno_turma.title()})")
                })
            except Exception:
                continue
        return turmas

    def _ask_turma_dropdown(self, title="Selecionar Turma"):
        """Show a small dialog with a Combobox listing turmas and return the selected id or None."""
        turmas = self._get_turmas_list()
        
        # Filtrar turmas baseado no acesso do usuário
        if self.role == 'professor':
            # Professor só vê turmas que tem acesso
            turmas_acessiveis = []
            for t in turmas:
                if self.db.can_access_subject(self.username, t['id']):
                    turmas_acessiveis.append(t)
            turmas = turmas_acessiveis
        
        if not turmas:
            if self.role == 'professor':
                messagebox.showwarning("Aviso", "Você não tem acesso a nenhuma turma.\nEntre em contato com o administrador para atribuir matérias.")
            else:
                messagebox.showwarning("Aviso", "Nenhuma turma cadastrada.")
            return None
        dlg = tk.Toplevel(self)
        _set_window_icon(dlg)
        try:
            _apply_popup_theme(dlg, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dlg.title(title)
        dlg.geometry("360x120")
        dlg.transient(self); dlg.grab_set()
        _center_window(dlg)
        ttk.Label(dlg, text="Selecione a Turma:").pack(padx=10, pady=(10, 4))
        combo = ttk.Combobox(dlg, values=[t['tuple'][1] for t in turmas], state='readonly')
        combo.pack(fill=tk.X, padx=10)
        # Preselect last turma if present
        initial_index = 0
        if self._last_turma:
            for idx, t in enumerate(turmas):
                if t['id'] == self._last_turma:
                    initial_index = idx; break
        combo.current(initial_index)
        result = {'value': None}
        def ok():
            sel = combo.get()
            for t in turmas:
                if t['tuple'][1] == sel:
                    result['value'] = t['id']
                    break
            # persist last selected turma
            try:
                self._last_turma = result['value']
            except Exception:
                pass
            dlg.destroy()
        def cancel():
            dlg.destroy()
        
        btnf = ttk.Frame(dlg)
        btnf.pack(pady=10)
        ok_btn = ttk.Button(btnf, text="OK", command=ok, style='Dialog.TButton')
        ok_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(btnf, text="Cancelar", command=cancel, style='Secondary.TButton').pack(side=tk.LEFT, padx=6)
        
        # Configurar atalhos de teclado e foco
        _setup_dialog_shortcuts(dlg, ok_button=ok_btn, cancel_callback=cancel)
        
        self.wait_window(dlg)
        return result['value']

    def _get_alunos_list(self, id_turma=None):
        """Return a list of tuples (matricula, label) for alunos.
        If id_turma is provided, list only that turma; otherwise aggregate from all turmas.
        """
        alunos = []
        if id_turma:
            resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{id_turma}")
            if not resp or "Nenhum aluno" in resp:
                return alunos
            for linha in resp.strip().split('\n'):
                if not linha: continue
                partes = linha.split(', ')
                try:
                    matricula = partes[0].split(': ')[1]
                    nome = partes[1].split(': ')[1]
                    alunos.append((matricula, f"{matricula} - {nome}"))
                except Exception:
                    continue
            return alunos

        # Aggregate across all turmas
        turmas = self._get_turmas_list()
        for t in turmas:
            tid = t['id']
            # Se for professor, verificar acesso
            if self.role == 'professor' and not self.db.can_access_subject(self.username, tid):
                continue  # Pular turmas sem acesso
            
            resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
            if not resp or "Nenhum aluno" in resp:
                continue
            for linha in resp.strip().split('\n'):
                if not linha: continue
                partes = linha.split(', ')
                try:
                    matricula = partes[0].split(': ')[1]
                    nome = partes[1].split(': ')[1]
                    alunos.append((matricula, f"{matricula} - {nome}"))
                except Exception:
                    continue
        return alunos
    
    def listar_alunos_turma(self):
        # Para alunos, mostrar apenas alunos da sua turma
        if self.role == 'aluno':
            matricula = self.db.get_student_matricula(self.username)
            if not matricula:
                messagebox.showerror("Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
                return
            
            # Encontrar turma do aluno
            resp_list = self._send_request(f"LIST_TURMAS")
            if not resp_list or "Nenhuma turma" in resp_list:
                messagebox.showerror("Erro", "Nenhuma turma encontrada.")
                return
            
            id_t = None
            for linha in resp_list.strip().split('\n'):
                if linha:
                    partes = linha.split(', ')
                    tid = partes[0].split(': ')[1]
                    
                    alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                    if alunos_resp and "Nenhum aluno" not in alunos_resp:
                        for aluno_linha in alunos_resp.strip().split('\n'):
                            if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                                id_t = tid
                                break
                    if id_t:
                        break
            
            if not id_t:
                messagebox.showerror("Erro", "Sua turma não foi encontrada.")
                return
            
            self._refresh_aluno_list(id_t)
        else:
            # Professor e Admin selecionam a turma
            id_t = self._ask_turma_dropdown(title="Listar Alunos - Selecionar Turma")
            if id_t:
                # Verificação de acesso adicional (segurança extra)
                if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
                    messagebox.showerror("Acesso Negado", 
                                       f"Você não tem permissão para visualizar alunos desta turma (ID: {id_t}).\n"
                                       f"Entre em contato com o administrador para solicitar acesso.")
                    return
                self._refresh_aluno_list(id_t)

    def pesquisar_aluno(self):
        """Pesquisa detalhada de informações de alunos - apenas para admin e professores"""
        if self.role not in ['admin', 'professor']:
            messagebox.showerror("Acesso Negado", "Apenas administradores e professores podem pesquisar alunos.")
            return
        
        # Criar dialog
        dialog = tk.Toplevel(self)
        dialog.title("Pesquisar Informações de Aluno")
        
        # Configurar para ocupar altura inteira da tela
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        largura = 600
        altura = screen_height - 90  # Deixa margem para barra de tarefas
        x = (screen_width - largura) // 2
        y = 0
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Pesquisar Informações de Aluno", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Frame de busca
        search_frame = tk.LabelFrame(main_frame, text="Selecionar Aluno", 
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     font=('Arial', 11, 'bold'), padx=15, pady=15)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Coletar todos os alunos acessíveis
        alunos_disponiveis = []
        
        # Buscar todas as turmas
        turmas_resp = self._send_request("LIST_TURMAS")
        if turmas_resp and "Nenhuma turma" not in turmas_resp:
            for linha in turmas_resp.strip().split('\n'):
                if linha:
                    partes = linha.split(', ')
                    tid = partes[0].split(': ')[1]
                    
                    # Verificar se professor tem acesso
                    if self.role == 'professor' and not self.db.can_access_subject(self.username, tid):
                        continue
                    
                    # Buscar alunos da turma
                    alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                    if alunos_resp and "Nenhum aluno" not in alunos_resp:
                        for aluno_linha in alunos_resp.strip().split('\n'):
                            if aluno_linha:
                                partes_aluno = aluno_linha.split(', ')
                                matricula = partes_aluno[0].split(': ')[1]
                                nome = partes_aluno[1].split(': ')[1]
                                
                                # Evitar duplicados
                                if not any(a['matricula'] == matricula for a in alunos_disponiveis):
                                    alunos_disponiveis.append({
                                        'matricula': matricula,
                                        'nome': nome,
                                        'turma_id': tid
                                    })
        
        if not alunos_disponiveis:
            tk.Label(search_frame, text="Nenhum aluno encontrado.", 
                    font=('Arial', 11), bg=self.colors['card'], fg=self.colors['text']).pack()
            ttk.Button(main_frame, text="Fechar", command=dialog.destroy, 
                      style='Secondary.TButton').pack(pady=10)
            return
        
        # Combobox com alunos
        tk.Label(search_frame, text="Aluno:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 5))
        
        aluno_var = tk.StringVar()
        aluno_values = [f"{a['matricula']} - {a['nome']}" for a in alunos_disponiveis]
        aluno_combo = ttk.Combobox(search_frame, textvariable=aluno_var,
                                   values=aluno_values,
                                   state="readonly", width=60, font=('Arial', 10))
        aluno_combo.pack(fill=tk.X, pady=(0, 10))
        if aluno_values:
            aluno_combo.current(0)
        
        # Frame para exibir informações
        info_frame = tk.LabelFrame(main_frame, text="Informações Detalhadas", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Arial', 11, 'bold'), padx=15, pady=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Canvas com scrollbar para informações
        canvas = tk.Canvas(info_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def exibir_informacoes():
            """Carrega e exibe informações do aluno selecionado"""
            # Limpar frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            if not aluno_var.get():
                return
            
            matricula = aluno_var.get().split(' - ')[0]
            
            # Buscar informações do aluno
            aluno_info = next((a for a in alunos_disponiveis if a['matricula'] == matricula), None)
            if not aluno_info:
                return
            
            tid = aluno_info['turma_id']
            
            # Buscar dados completos da turma
            turma_resp = self._send_request(f"GET_TURMA_DATA|{tid}")
            disciplina, professor = "", ""
            if turma_resp and "ERRO" not in turma_resp:
                disciplina, professor = turma_resp.split('|')
            
            # Buscar notas do aluno DIRETAMENTE DO SERVIDOR
            alunos_turma_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
            np1, np2, pim, media, exame = 0.0, 0.0, 0.0, 0.0, 0.0
            
            if alunos_turma_resp and "Nenhum aluno" not in alunos_turma_resp:
                for linha in alunos_turma_resp.strip().split('\n'):
                    if linha and f"Matrícula: {matricula}" in linha:
                        partes = linha.split(', ')
                        for p in partes[2:]:
                            if p.startswith('NP1:'):
                                try:
                                    np1 = float(p.split(': ')[1])
                                except:
                                    np1 = 0.0
                            elif p.startswith('NP2:'):
                                try:
                                    np2 = float(p.split(': ')[1])
                                except:
                                    np2 = 0.0
                            elif p.startswith('PIM:'):
                                try:
                                    pim = float(p.split(': ')[1])
                                except:
                                    pim = 0.0
                            elif p.startswith('Média:'):
                                try:
                                    media = float(p.split(': ')[1])
                                except Exception:
                                    media = 0.0
                            elif p.startswith('Exame:'):
                                try:
                                    exame = float(p.split(': ')[1])
                                except Exception:
                                    exame = 0.0
                        break
            
            # Calcular faltas
            faltas = 0
            try:
                for rec in read_presencas_dat(tid):
                    if str(rec.get('matricula')) == str(matricula) and not rec.get('presente'):
                        faltas += 1
            except Exception:
                pass
            
            # Calcular status (lógica idêntica ao _refresh_aluno_list)
            tem_notas = (np1 > 0 or np2 > 0 or pim > 0)
            if not tem_notas:
                # Se não há nenhuma nota atribuída
                status = "Pendente Atribuir Notas"
            elif media >= 7.0:
                # Se média >= 7, aprovado direto
                status = "Aprovado"
            elif media < 7.0 and exame == 0.0:
                # Se média < 7 e exame vazio, pendente exame
                status = "Pendente Exame"
            elif media < 7.0 and exame >= 5.0:
                # Se média < 7 mas exame >= 5, aprovado
                status = "Aprovado (Exame)"
            elif media < 7.0 and 0.0 < exame < 5.0:
                # Se média < 7 e exame < 5, reprovado
                status = "Reprovado"
            else:
                status = "Pendente"
            
            # Buscar dados do usuário no banco
            username_aluno = None
            email, data_criacao, ultimo_acesso, tempo_uso = "", "", "", ""
            foto_perfil_path = None
            
            for username, user_data in self.db.users.items():
                if user_data.get('matricula') == int(matricula):
                    username_aluno = username
                    email = user_data.get('email', 'Não informado')
                    data_criacao = user_data.get('created_at', 'Não informado')
                    ultimo_acesso = user_data.get('last_login', 'Nunca acessou')
                    tempo_uso_seg = user_data.get('total_time', 0)
                    foto_perfil_path = user_data.get('foto_perfil')
                    
                    # Converter tempo de uso para formato legível
                    horas = tempo_uso_seg // 3600
                    minutos = (tempo_uso_seg % 3600) // 60
                    tempo_uso = f"{int(horas)}h {int(minutos)}min"
                    break
            
            # Exibir foto de perfil no topo
            foto_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
            foto_frame.pack(pady=(0, 15))
            
            try:
                if foto_perfil_path and os.path.exists(foto_perfil_path):
                    from PIL import Image, ImageTk, ImageDraw
                    img = Image.open(foto_perfil_path)
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)
                    
                    # Criar máscara circular
                    mask = Image.new('L', (60, 60), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 60, 60), fill=255)
                    
                    # Aplicar máscara
                    output = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
                    output.paste(img, (0, 0))
                    output.putalpha(mask)
                    
                    photo = ImageTk.PhotoImage(output)
                    foto_label = tk.Label(foto_frame, image=photo, bg=self.colors['card'])
                    foto_label.image = photo  # Manter referência
                    foto_label.pack()
                else:
                    # Placeholder se não tiver foto
                    placeholder = tk.Label(foto_frame, text="👤", font=('Arial', 40), 
                                         bg=self.colors['border'], fg=self.colors['text_secondary'],
                                         width=3, height=1)
                    placeholder.pack()
            except Exception as e:
                # Placeholder em caso de erro
                placeholder = tk.Label(foto_frame, text="👤", font=('Arial', 40), 
                                     bg=self.colors['border'], fg=self.colors['text_secondary'],
                                     width=3, height=1)
                placeholder.pack()
            
            # Exibir informações organizadas
            sections = [
                ("Informações Básicas", [
                    ("Matrícula", matricula),
                    ("Nome", aluno_info['nome']),
                    ("Email", email),
                    ("Username", username_aluno or "Não encontrado")
                ]),
                ("Turma e Notas", [
                    ("Turma ID", tid),
                    ("Disciplina", disciplina),
                    ("Professor", professor),
                    ("NP1", f"{np1:.1f}"),
                    ("NP2", f"{np2:.1f}"),
                    ("PIM", f"{pim:.1f}"),
                    ("Média", f"{media:.1f}"),
                    ("Exame", f"{exame:.1f}"),
                    ("Faltas", str(faltas)),
                    ("Status", status)
                ]),
                ("Informações do Sistema", [
                    ("Data de Criação", data_criacao),
                    ("Último Acesso", ultimo_acesso),
                    ("Tempo de Uso Total", tempo_uso)
                ])
            ]
            
            for section_title, fields in sections:
                # Título da seção
                section_label = tk.Label(scrollable_frame, text=section_title, 
                                        font=('Arial', 12, 'bold'), 
                                        bg=self.colors['primary'], fg='white',
                                        padx=10, pady=5)
                section_label.pack(fill=tk.X, pady=(10, 0))
                
                # Campos da seção
                for label, value in fields:
                    field_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
                    field_frame.pack(fill=tk.X, pady=2)
                    
                    tk.Label(field_frame, text=f"{label}:", font=('Arial', 10, 'bold'),
                            bg=self.colors['card'], fg=self.colors['text'],
                            width=20, anchor='w').pack(side=tk.LEFT, padx=5)
                    
                    # Colorir status
                    fg_color = self.colors['text']
                    if label == "Status":
                        if "Aprovado" in value:
                            fg_color = '#28a745'  # Verde
                        elif "Reprovado" in value:
                            fg_color = '#dc3545'  # Vermelho
                        elif "Pendente" in value:
                            fg_color = '#ffc107'  # Amarelo
                    
                    tk.Label(field_frame, text=str(value), font=('Arial', 10),
                            bg=self.colors['input_bg'], fg=fg_color,
                            relief='solid', bd=1, padx=8, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão pesquisar
        search_btn = ttk.Button(search_frame, text="Pesquisar", command=exibir_informacoes,
                  style='Dialog.TButton')
        search_btn.pack(pady=5)
        
        # Botão fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=dialog.destroy,
                  style='Secondary.TButton')
        close_btn.pack()
        
        # Configurar atalhos (ESC fecha, Enter pesquisa)
        _setup_dialog_shortcuts(dialog, ok_button=search_btn, cancel_callback=dialog.destroy)
        
        # Habilitar scroll com mousewheel
        _enable_canvas_scroll(canvas, scrollable_frame)
        
        # Carregar informações do primeiro aluno automaticamente
        if aluno_values:
            dialog.after(100, exibir_informacoes)

    def pesquisar_professor(self):
        """Pesquisa detalhada de informações de professores - apenas para admin"""
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem pesquisar professores.")
            return
        
        # Criar dialog
        dialog = tk.Toplevel(self)
        dialog.title("Pesquisar Informações de Professor")
        
        # Configurar para ocupar altura inteira da tela
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        largura = 600
        altura = screen_height - 90  # Deixa margem para barra de tarefas
        x = (screen_width - largura) // 2
        y = 0
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Pesquisar Informações de Professor", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Frame de busca
        search_frame = tk.LabelFrame(main_frame, text="Selecionar Professor", 
                                     bg=self.colors['card'], fg=self.colors['text'],
                                     font=('Arial', 11, 'bold'), padx=15, pady=15)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Coletar todos os professores
        professores_disponiveis = []
        
        for username, user_data in self.db.users.items():
            if user_data.get('role') == 'professor':
                professores_disponiveis.append({
                    'username': username,
                    'email': user_data.get('email', 'Não informado'),
                    'subjects': user_data.get('subjects', [])
                })
        
        if not professores_disponiveis:
            tk.Label(search_frame, text="Nenhum professor encontrado.", 
                    font=('Arial', 11), bg=self.colors['card'], fg=self.colors['text']).pack()
            ttk.Button(main_frame, text="Fechar", command=dialog.destroy, 
                      style='Secondary.TButton').pack(pady=10)
            return
        
        # Combobox com professores
        tk.Label(search_frame, text="Professor:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 5))
        
        prof_var = tk.StringVar()
        prof_values = [f"{p['username']}" for p in professores_disponiveis]
        prof_combo = ttk.Combobox(search_frame, textvariable=prof_var,
                                   values=prof_values,
                                   state="readonly", width=60, font=('Arial', 10))
        prof_combo.pack(fill=tk.X, pady=(0, 10))
        if prof_values:
            prof_combo.current(0)
        
        # Frame para exibir informações
        info_frame = tk.LabelFrame(main_frame, text="Informações Detalhadas", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Arial', 11, 'bold'), padx=15, pady=15)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Canvas com scrollbar
        canvas = tk.Canvas(info_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def exibir_informacoes():
            """Carrega e exibe informações do professor selecionado"""
            # Limpar frame
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            if not prof_var.get():
                return
            
            username = prof_var.get()
            
            # Buscar informações do professor
            prof_info = next((p for p in professores_disponiveis if p['username'] == username), None)
            if not prof_info:
                return
            
            user_data = self.db.users.get(username, {})
            
            # Buscar foto de perfil
            foto_perfil_path = user_data.get('foto_perfil')
            
            # Exibir foto de perfil no topo
            foto_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
            foto_frame.pack(pady=(0, 15))
            
            try:
                if foto_perfil_path and os.path.exists(foto_perfil_path):
                    from PIL import Image, ImageTk, ImageDraw
                    img = Image.open(foto_perfil_path)
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)
                    
                    # Criar máscara circular
                    mask = Image.new('L', (60, 60), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 60, 60), fill=255)
                    
                    # Aplicar máscara
                    output = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
                    output.paste(img, (0, 0))
                    output.putalpha(mask)
                    
                    photo = ImageTk.PhotoImage(output)
                    foto_label = tk.Label(foto_frame, image=photo, bg=self.colors['card'])
                    foto_label.image = photo
                    foto_label.pack()
                else:
                    placeholder = tk.Label(foto_frame, text="👤", font=('Arial', 40), 
                                         bg=self.colors['border'], fg=self.colors['text_secondary'],
                                         width=3, height=1)
                    placeholder.pack()
            except Exception:
                placeholder = tk.Label(foto_frame, text="👤", font=('Arial', 40), 
                                     bg=self.colors['border'], fg=self.colors['text_secondary'],
                                     width=3, height=1)
                placeholder.pack()
            
            # Buscar turmas associadas
            turmas_associadas = []
            if prof_info['subjects']:
                turmas_resp = self._send_request("LIST_TURMAS")
                if turmas_resp and "Nenhuma turma" not in turmas_resp:
                    for linha in turmas_resp.strip().split('\n'):
                        if linha:
                            partes = linha.split(', ')
                            tid = partes[0].split(': ')[1]
                            if str(tid) in [str(s) for s in prof_info['subjects']]:
                                disciplina = partes[1].split(': ')[1] if len(partes) > 1 else "N/A"
                                turmas_associadas.append(f"ID {tid} - {disciplina}")
            
            turmas_texto = ", ".join(turmas_associadas) if turmas_associadas else "Nenhuma turma atribuída"
            
            # Buscar dados do sistema
            email = user_data.get('email', 'Não informado')
            data_criacao = user_data.get('created_at', 'Não informado')
            ultimo_acesso = user_data.get('last_login', 'Nunca acessou')
            tempo_uso_seg = user_data.get('total_time', 0)
            turno = user_data.get('turno', 'Não informado')
            
            # Converter tempo de uso
            horas = tempo_uso_seg // 3600
            minutos = (tempo_uso_seg % 3600) // 60
            tempo_uso = f"{int(horas)}h {int(minutos)}min"
            
            # Exibir informações organizadas
            sections = [
                ("Informações Básicas", [
                    ("Username", username),
                    ("Email", email),
                    ("Turno", turno.title())
                ]),
                ("Turmas Atribuídas", [
                    ("Turmas", turmas_texto)
                ]),
                ("Informações do Sistema", [
                    ("Data de Criação", data_criacao),
                    ("Último Acesso", ultimo_acesso),
                    ("Tempo de Uso Total", tempo_uso)
                ])
            ]
            
            for section_title, fields in sections:
                # Título da seção
                section_label = tk.Label(scrollable_frame, text=section_title, 
                                        font=('Arial', 12, 'bold'), 
                                        bg=self.colors['primary'], fg='white',
                                        padx=10, pady=5)
                section_label.pack(fill=tk.X, pady=(10, 0))
                
                # Campos da seção
                for label, value in fields:
                    field_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
                    field_frame.pack(fill=tk.X, pady=2)
                    
                    tk.Label(field_frame, text=f"{label}:", font=('Arial', 10, 'bold'),
                            bg=self.colors['card'], fg=self.colors['text'],
                            width=20, anchor='w').pack(side=tk.LEFT, padx=5)
                    
                    tk.Label(field_frame, text=str(value), font=('Arial', 10),
                            bg=self.colors['input_bg'], fg=self.colors['text'],
                            relief='solid', bd=1, padx=8, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botão pesquisar
        search_btn = ttk.Button(search_frame, text="Pesquisar", command=exibir_informacoes,
                  style='Dialog.TButton')
        search_btn.pack(pady=5)
        
        # Botão fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=dialog.destroy,
                  style='Secondary.TButton')
        close_btn.pack()
        
        # Configurar atalhos (ESC fecha, Enter pesquisa)
        _setup_dialog_shortcuts(dialog, ok_button=search_btn, cancel_callback=dialog.destroy)
        
        # Habilitar scroll com mousewheel
        _enable_canvas_scroll(canvas, scrollable_frame)
        
        # Carregar informações do primeiro professor automaticamente
        if prof_values:
            dialog.after(100, exibir_informacoes)

    def _ask_aluno_dropdown(self, title="Selecionar Aluno", id_turma=None):
        """Show a dialog with a Combobox listing alunos and return the selected matricula or None."""
        alunos = self._get_alunos_list(id_turma)
        if not alunos:
            messagebox.showwarning("Aviso", "Nenhum aluno encontrado.")
            return None
        dlg = tk.Toplevel(self)
        _set_window_icon(dlg)
        try:
            _apply_popup_theme(dlg, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dlg.title(title)
        dlg.geometry("420x120")
        dlg.transient(self); dlg.grab_set()
        _center_window(dlg)
        ttk.Label(dlg, text="Selecione o Aluno:").pack(padx=10, pady=(10, 4))
        combo = ttk.Combobox(dlg, values=[a[1] for a in alunos], state='readonly')
        combo.pack(fill=tk.X, padx=10)
        combo.current(0)
        result = {'value': None}
        def ok():
            sel = combo.get()
            for mat, label in alunos:
                if label == sel:
                    result['value'] = mat
                    break
            dlg.destroy()
        def cancel():
            dlg.destroy()
        
        btnf = ttk.Frame(dlg)
        btnf.pack(pady=10)
        ok_btn = ttk.Button(btnf, text="OK", command=ok, style='Dialog.TButton')
        ok_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(btnf, text="Cancelar", command=cancel, style='Secondary.TButton').pack(side=tk.LEFT, padx=6)
        
        # Configurar atalhos de teclado e foco
        _setup_dialog_shortcuts(dlg, ok_button=ok_btn, cancel_callback=cancel)
        
        self.wait_window(dlg)
        return result['value']

    def _combined_turma_aluno_selector(self, title="Selecionar Turma/Aluno"):
        """Combined dialog: select a turma, then the aluno Combobox updates to show alunos for that turma.
        Returns (id_turma, matricula) or None if cancelled.
        """
        turmas = self._get_turmas_list()
        
        # Filtrar turmas baseado no acesso do usuário
        if self.role == 'professor':
            # Professor só vê turmas que tem acesso
            turmas_acessiveis = []
            for t in turmas:
                if self.db.can_access_subject(self.username, t['id']):
                    turmas_acessiveis.append(t)
            turmas = turmas_acessiveis
        
        if not turmas:
            if self.role == 'professor':
                messagebox.showwarning("Aviso", "Você não tem acesso a nenhuma turma.\nEntre em contato com o administrador para atribuir matérias.")
            else:
                messagebox.showwarning("Aviso", "Nenhuma turma cadastrada.")
            return None
        dlg = tk.Toplevel(self)
        dlg.configure(bg=self.colors['card'])
        _set_window_icon(dlg)
        try:
            _apply_popup_theme(dlg, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dlg.title(title)
        dlg.geometry("480x160")
        dlg.transient(self); dlg.grab_set()
        _center_window(dlg)

        ttk.Label(dlg, text="Turma:").pack(anchor='w', padx=10, pady=(10,0))
        turma_combo = ttk.Combobox(dlg, values=[t['tuple'][1] for t in turmas], state='readonly')
        turma_combo.pack(fill=tk.X, padx=10)
        # preselect last turma if available
        init_idx = 0
        if self._last_turma:
            for idx, t in enumerate(turmas):
                if t['id'] == self._last_turma:
                    init_idx = idx; break
        turma_combo.current(init_idx)

        ttk.Label(dlg, text="Aluno:").pack(anchor='w', padx=10, pady=(8,0))
        aluno_combo = ttk.Combobox(dlg, values=[], state='readonly')
        aluno_combo.pack(fill=tk.X, padx=10)

        # Fill aluno combo when turma changes
        def refresh_alunos(event=None):
            sel = turma_combo.get()
            sel_tid = None
            for t in turmas:
                if t['tuple'][1] == sel:
                    sel_tid = t['id']; break
            if not sel_tid:
                aluno_combo['values'] = []
                return
            alunos = self._get_alunos_list(sel_tid)
            aluno_combo['values'] = [a[1] for a in alunos]
            if alunos:
                aluno_combo.current(0)
            else:
                aluno_combo.set('')

        turma_combo.bind('<<ComboboxSelected>>', refresh_alunos)
        # initial fill
        refresh_alunos()

        result = {'value': None}
        def ok():
            turma_label = turma_combo.get()
            aluno_label = aluno_combo.get()
            tid = None; mat = None
            for t in turmas:
                if t['tuple'][1] == turma_label:
                    tid = t['id']; break
            if aluno_label:
                # find matricula
                alunos = self._get_alunos_list(tid)
                for m, lbl in alunos:
                    if lbl == aluno_label:
                        mat = m; break
            result['value'] = (tid, mat)
            try:
                self._last_turma = tid
            except Exception:
                pass
            dlg.destroy()

        def cancel():
            dlg.destroy()

        btnf = ttk.Frame(dlg)
        btnf.pack(pady=10)
        ok_btn = ttk.Button(btnf, text="OK", command=ok, style='Dialog.TButton')
        ok_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(btnf, text="Cancelar", command=cancel, style='Secondary.TButton').pack(side=tk.LEFT, padx=6)
        
        # Configurar atalhos de teclado e foco
        _setup_dialog_shortcuts(dlg, ok_button=ok_btn, cancel_callback=cancel)
        
        self.wait_window(dlg)
        return result['value']
    def listar_turmas(self):
        resp = self._send_request("LIST_TURMAS")
        if resp is not None and resp != "Nenhuma turma cadastrada.":
            turmas_data = []
            turno_usuario = self.db.users.get(self.username, {}).get('turno', 'matutino')
            
            for linha in resp.strip().split('\n'):
                if linha:
                    # Extrai os dados da linha
                    partes = linha.split(', ')
                    id_turma = partes[0].split(': ')[1]
                    disciplina = partes[1].split(': ')[1]
                    professor = partes[2].split(': ')[1]
                    
                    # Buscar turno da turma
                    turno_turma = get_turno_turma(id_turma)
                    
                    # Filtrar por turno se não for admin
                    if self.role != 'admin':
                        if turno_turma != turno_usuario:
                            continue  # Pula turmas de outros turnos
                    
                    # Conta alunos da turma
                    alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{id_turma}")
                    total_alunos = 0
                    if alunos_resp and "Nenhum aluno" not in alunos_resp:
                        total_alunos = len(alunos_resp.strip().split('\n'))
                    
                    # Ícone do turno
                    turno_icone = {'matutino': '', 'vespertino': '', 'noturno': ''}.get(turno_turma, '🕐')
                    turno_display = f"{turno_icone} {turno_turma.title()}"
                    
                    turmas_data.append([id_turma, disciplina, professor, turno_display, total_alunos])
            
            # Atualiza o display com o novo formato
            headers = ["ID", "Disciplina", "Professor", "Turno", "Total Alunos"]
            self._update_display("Lista de Turmas", headers, turmas_data)
        else:
            self._update_display("Lista de Turmas", [], [])
    
    def calendario_provas(self):
        """Interface de calendário de provas com controle de acesso por perfil"""
        # Admin tem acesso total
        # Professor só vê/edita suas turmas
        # Aluno só vê as provas da sua turma
        
        if self.role == 'aluno':
            self._calendario_provas_aluno()
        elif self.role in ['professor', 'admin']:
            self._calendario_provas_professor_admin()
    
    def _calendario_provas_aluno(self):
        """Interface de visualização de provas para alunos"""
        # Buscar matrícula do aluno
        matricula = self.db.get_student_matricula(self.username)
        if not matricula:
            messagebox.showerror("Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
            return
        
        # Buscar turma do aluno
        resp_list = self._send_request(f"LIST_TURMAS")
        if not resp_list or "Nenhuma turma" in resp_list:
            messagebox.showerror("Erro", "Nenhuma turma encontrada.")
            return
        
        id_turma = None
        disciplina = None
        for linha in resp_list.strip().split('\n'):
            if linha:
                partes = linha.split(', ')
                tid = partes[0].split(': ')[1]
                disc = partes[1].split(': ')[1]
                
                alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                if alunos_resp and "Nenhum aluno" not in alunos_resp:
                    for aluno_linha in alunos_resp.strip().split('\n'):
                        if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                            id_turma = tid
                            disciplina = disc
                            break
                if id_turma:
                    break
        
        if not id_turma:
            messagebox.showerror("Erro", "Sua turma não foi encontrada.")
            return
        
        # Criar janela
        dialog = tk.Toplevel(self)
        dialog.title(f"Calendário de Provas - {disciplina}")
        dialog.geometry("700x500")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text=f"Calendário de Provas", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 5))
        
        tk.Label(main_frame, text=f"Disciplina: {disciplina}", 
                font=('Arial', 12), bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 20))
        
        # Buscar datas das provas
        provas = get_provas_turma(id_turma)
        hoje = datetime.now().strftime('%d/%m/%Y')
        
        # Frame de provas
        provas_frame = tk.Frame(main_frame, bg=self.colors['card'])
        provas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        tipos_prova = [
            ('NP1', 'NP1 - Primeira Avaliação', provas.get('NP1')),
            ('NP2', 'NP2 - Segunda Avaliação', provas.get('NP2')),
            ('PIM', 'PIM - Trabalho Semestral', provas.get('PIM')),
            ('Exame', 'Exame - Recuperação', provas.get('Exame'))
        ]
        
        for tipo, nome, data in tipos_prova:
            prova_card = tk.Frame(provas_frame, bg=self.colors['card'], relief='solid', bd=1, padx=15, pady=12)
            prova_card.pack(fill=tk.X, pady=5)
            
            # Determinar cor do card
            card_bg = self.colors['card']
            data_color = self.colors['text']
            
            if data and data == hoje:
                card_bg = '#FFEBEE' if not getattr(self, 'dark_mode', False) else '#4D1B1B'
                data_color = '#C00000'
            
            prova_card.config(bg=card_bg)
            
            tk.Label(prova_card, text=nome, font=('Arial', 12, 'bold'), 
                    bg=card_bg, fg=self.colors['text']).pack(anchor='w')
            
            if data:
                data_text = f"Data: {data}"
                if data == hoje:
                    data_text += " HOJE!"
                tk.Label(prova_card, text=data_text, font=('Arial', 11), 
                        bg=card_bg, fg=data_color).pack(anchor='w', pady=(5, 0))
            else:
                tk.Label(prova_card, text="Data ainda não definida", 
                        font=('Arial', 10, 'italic'), 
                        bg=card_bg, fg=self.colors['text_secondary']).pack(anchor='w', pady=(5, 0))
        
        # Botão fechar
        close_btn = ttk.Button(main_frame, text="Fechar", command=dialog.destroy, 
                  style='Secondary.TButton')
        close_btn.pack(pady=(10, 0))
        
        # Configurar atalhos (ESC fecha)
        _setup_dialog_shortcuts(dialog, ok_button=close_btn, cancel_callback=dialog.destroy)
    
    def _calendario_provas_professor_admin(self):
        """Interface de gerenciamento de provas para professores e administradores"""
        # Criar janela
        dialog = tk.Toplevel(self)
        dialog.title("Gerenciar Calendário de Provas")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="Gerenciar Calendário de Provas", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Seleção de turma
        turma_frame = tk.Frame(main_frame, bg=self.colors['card'])
        turma_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(turma_frame, text="Selecionar Turma:", font=('Arial', 12, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 5))
        
        # Buscar turmas acessíveis
        turmas = self._get_turmas_list()
        
        # Filtrar por permissão se for professor
        if self.role == 'professor':
            turmas_acessiveis = []
            for t in turmas:
                if self.db.can_access_subject(self.username, t['id']):
                    turmas_acessiveis.append(t)
            turmas = turmas_acessiveis
        
        if not turmas:
            tk.Label(main_frame, text="Nenhuma turma disponível para gerenciar.", 
                    bg=self.colors['card'], fg=self.colors['text']).pack()
            ttk.Button(main_frame, text="Fechar", command=dialog.destroy, 
                      style='Secondary.TButton').pack(pady=(15, 0))
            return
        
        turma_var = tk.StringVar()
        turma_combo = ttk.Combobox(turma_frame, textvariable=turma_var, 
                                   values=[f"{t['id']} - {t['tuple'][1]}" for t in turmas], 
                                   state="readonly", width=50)
        turma_combo.pack(anchor='w')
        turma_combo.current(0)
        
        # Frame de edição de datas
        datas_frame = tk.LabelFrame(main_frame, text="Datas das Provas", 
                                    bg=self.colors['card'], fg=self.colors['text'], 
                                    font=('Arial', 11, 'bold'), padx=15, pady=15)
        datas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Campos de entrada para cada tipo de prova
        date_entries = {}
        tipos_prova = [
            ('NP1', 'NP1 - Primeira Avaliação'),
            ('NP2', 'NP2 - Segunda Avaliação'),
            ('PIM', 'PIM - Trabalho Semestral'),
            ('Exame', 'Exame - Recuperação (Média < 5)')
        ]
        
        for tipo, nome in tipos_prova:
            field_frame = tk.Frame(datas_frame, bg=self.colors['card'])
            field_frame.pack(fill=tk.X, pady=8)
            
            tk.Label(field_frame, text=nome, font=('Arial', 10), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 3))
            
            # Frame para entrada e botão
            entry_btn_frame = tk.Frame(field_frame, bg=self.colors['card'])
            entry_btn_frame.pack(anchor='w')
            
            entry = ttk.Entry(entry_btn_frame, width=20)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            entry.insert(0, 'DD/MM/AAAA')
            date_entries[tipo] = entry
            
            # Botão de calendário
            cal_btn = tk.Button(entry_btn_frame, text="📅", font=('Arial', 12),
                              bg=self.colors['primary'], fg='white',
                              activebackground=self.colors['primary_hover'],
                              relief='flat', cursor='hand2',
                              width=3, height=1,
                              command=lambda e=entry: show_calendar_picker(dialog, e, self.colors))
            cal_btn.pack(side=tk.LEFT)
            
            # Placeholder behavior
            def on_focus_in(e, ent=entry):
                if ent.get() == 'DD/MM/AAAA':
                    ent.delete(0, tk.END)
            
            def on_focus_out(e, ent=entry):
                if not ent.get():
                    ent.insert(0, 'DD/MM/AAAA')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        def carregar_datas(event=None):
            """Carrega as datas da turma selecionada"""
            sel = turma_combo.get()
            if not sel:
                return
            
            tid = sel.split(' - ')[0]
            provas = get_provas_turma(tid)
            
            for tipo, entry in date_entries.items():
                entry.delete(0, tk.END)
                data = provas.get(tipo)
                if data:
                    entry.insert(0, data)
                else:
                    entry.insert(0, 'DD/MM/AAAA')
        
        turma_combo.bind('<<ComboboxSelected>>', carregar_datas)
        carregar_datas()  # Carregar inicial
        
        def salvar_datas():
            """Salva as datas das provas"""
            sel = turma_combo.get()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma turma!")
                return
            
            tid = sel.split(' - ')[0]
            
            # Validar e salvar datas
            datas_validas = {}
            for tipo, entry in date_entries.items():
                data = entry.get()
                if data and data != 'DD/MM/AAAA':
                    # Validar formato
                    if not re.match(r'^\d{2}/\d{2}/\d{4}$', data):
                        messagebox.showerror("Erro", f"Data inválida para {tipo}. Use o formato DD/MM/AAAA")
                        return
                    datas_validas[tipo.lower()] = data
                else:
                    datas_validas[tipo.lower()] = None
            
            # Salvar
            if set_provas_turma(tid, **datas_validas):
                messagebox.showinfo("Sucesso", "Datas das provas salvas com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar datas das provas.")
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="💾 Salvar Datas", command=salvar_datas, 
                  style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        close_btn = ttk.Button(btn_frame, text="Fechar", command=dialog.destroy, 
                  style='Secondary.TButton')
        close_btn.pack(side=tk.RIGHT)
        
        # Configurar atalhos (ESC fecha, Enter salva)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
    
    def alterar_turma(self):
        # Admin e Professores podem acessar, mas com diferentes permissões
        if self.role not in ['admin', 'professor']:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para alterar turmas.")
            return
        
        id_t = self._ask_turma_dropdown(title="Editar Turma")
        if not id_t: return
        
        # Verificar se professor tem acesso a esta turma
        if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para alterar esta turma.")
            return
        
        # Cria uma janela de diálogo personalizada
        dialog = tk.Toplevel(self)
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        dialog.title(f"Editando Turma {id_t}")
        dialog.geometry("450x350")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        resp = self._send_request(f"GET_TURMA_DATA|{id_t}")
        if resp and "ERRO" not in resp:
            disc, prof = resp.split('|')
            
            # ID (apenas visualização)
            tk.Label(main_frame, text="ID da Turma:", font=('Arial', 10, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            id_label = tk.Label(main_frame, text=id_t, font=('Arial', 11), 
                               bg=self.colors['input_bg'], fg=self.colors['text'], 
                               relief='solid', bd=1, padx=5, pady=5)
            id_label.pack(fill=tk.X, pady=(3, 15))
            
            # Disciplina (read-only para professor, editável para admin)
            tk.Label(main_frame, text="Disciplina:", font=('Arial', 10, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            if self.role == 'admin':
                disciplina_entry = ttk.Entry(main_frame, width=40)
                disciplina_entry.insert(0, disc)
                disciplina_entry.pack(fill=tk.X, pady=(3, 15))
            else:
                disc_label = tk.Label(main_frame, text=disc, font=('Arial', 11), 
                                     bg=self.colors['input_bg'], fg=self.colors['text'], 
                                     relief='solid', bd=1, padx=5, pady=5)
                disc_label.pack(fill=tk.X, pady=(3, 15))
            
            # Professor (editável para admin)
            tk.Label(main_frame, text="Professor:", font=('Arial', 10, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            if self.role == 'admin':
                professor_entry = ttk.Entry(main_frame, width=40)
                professor_entry.insert(0, prof)
                professor_entry.pack(fill=tk.X, pady=(3, 20))
            else:
                prof_label = tk.Label(main_frame, text=prof, font=('Arial', 11), 
                                     bg=self.colors['input_bg'], fg=self.colors['text'], 
                                     relief='solid', bd=1, padx=5, pady=5)
                prof_label.pack(fill=tk.X, pady=(3, 20))
            
            def save_changes():
                if self.role != 'admin':
                    messagebox.showwarning("Aviso", "Apenas administradores podem salvar alterações em turmas.")
                    return
                
                # Atualiza dados básicos
                up_resp = self._send_request(f"UPDATE_TURMA|{id_t}|{disciplina_entry.get()}|{professor_entry.get()}")
                if up_resp and "SUCESSO" in up_resp:
                    messagebox.showinfo("Sucesso", "Turma atualizada com sucesso!")
                    dialog.destroy()
                    self.listar_turmas()
                else:
                    messagebox.showerror("Erro", up_resp or "Erro ao atualizar")
            
            btn_frame = ttk.Frame(main_frame)
            btn_frame.pack(fill=tk.X)
            
            if self.role == 'admin':
                ttk.Button(btn_frame, text="Salvar Alterações", command=save_changes, 
                          style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
                
                def do_delete():
                    if messagebox.askyesno("Confirmar", f"Excluir a turma {id_t} e TODOS os seus alunos?", icon='warning'):
                        resp = self._send_request(f"DELETE_TURMA|{id_t}")
                        if resp: messagebox.showinfo("Servidor", resp); dialog.destroy(); self.listar_turmas()
                
                ttk.Button(btn_frame, text="Excluir Turma", command=do_delete, 
                          style="Danger.TButton").pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Fechar", command=dialog.destroy, 
                      style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)
        else:
            messagebox.showerror("Erro", resp or "N/A")
            dialog.destroy()
    
    def _gerar_proxima_matricula(self):
        """Gera automaticamente a próxima matrícula incremental"""
        matriculas_existentes = []
        
        # Verificar matrículas dos usuários no sistema JSON
        for user_data in self.db.users.values():
            if 'matricula' in user_data and user_data['matricula']:
                try:
                    mat = int(user_data['matricula'])
                    if mat > 0:  # Validar que a matrícula é positiva
                        matriculas_existentes.append(mat)
                except (ValueError, TypeError):
                    pass
        
        # Verificar matrículas de todos os alunos cadastrados no sistema C
        try:
            # Buscar todas as turmas e seus alunos
            turmas_resp = self._send_request("LIST_TURMAS")
            if turmas_resp and "Nenhuma turma" not in turmas_resp:
                for linha in turmas_resp.strip().split('\n'):
                    if linha.strip():  # Verificar se a linha não está vazia
                        try:
                            # Extrair ID da turma com mais segurança
                            partes = linha.split(',')
                            if len(partes) > 0 and ':' in partes[0]:
                                id_turma = partes[0].split(':')[1].strip()
                                # Buscar alunos desta turma
                                alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{id_turma}")
                                if alunos_resp and "Nenhum aluno" not in alunos_resp:
                                    for aluno_linha in alunos_resp.strip().split('\n'):
                                        if aluno_linha.strip() and 'Matrícula:' in aluno_linha:
                                            try:
                                                # Formato: "Matrícula: XXXXX, Nome: YYY, ..."
                                                mat_str = aluno_linha.split(',')[0].split(':')[1].strip()
                                                mat = int(mat_str)
                                                if mat > 0:  # Validar que a matrícula é positiva
                                                    matriculas_existentes.append(mat)
                                            except (ValueError, IndexError):
                                                pass
                        except (ValueError, IndexError, AttributeError):
                            continue
        except Exception as e:
            print(f"Aviso: Erro ao buscar matrículas do sistema C: {e}")
            pass  # Se falhar, continua com as matrículas do JSON apenas
        
        if matriculas_existentes:
            proxima_mat = max(matriculas_existentes) + 1
            print(f"Debug: Matrículas existentes: {len(matriculas_existentes)}, Próxima matrícula: {proxima_mat}")
            return proxima_mat
        else:
            print("Debug: Nenhuma matrícula existente encontrada, iniciando em 20250001")
            return 20250001  # Primeira matrícula: Ano 2025 + 0001

    def cadastrar_aluno(self):
        # Apenas admin pode cadastrar alunos
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem cadastrar alunos.")
            return
        
        # Buscar turmas disponíveis
        turmas = self._get_turmas_list()
        
        if not turmas:
            messagebox.showwarning("Aviso", "Não há turmas cadastradas. Cadastre uma turma primeiro.")
            return
        
        # Gerar matrícula automaticamente
        nova_matricula = self._gerar_proxima_matricula()
        
        # Criar dialog customizado
        dialog = tk.Toplevel(self)
        dialog.title("Cadastrar Aluno")
        dialog.geometry("500x350")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Cadastrar Novo Aluno", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Matrícula (gerada automaticamente - apenas visualização)
        tk.Label(main_frame, text="Matrícula (gerada automaticamente):", 
                font=('Arial', 10, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        mat_label = tk.Label(main_frame, text=str(nova_matricula), 
                            font=('Arial', 11), bg=self.colors['border'], fg=self.colors['text'], 
                            relief='solid', bd=1, padx=8, pady=5)
        mat_label.pack(fill=tk.X, pady=(3, 15))
        
        # Turma (menu suspenso)
        tk.Label(main_frame, text="Selecionar Turma:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        turma_var = tk.StringVar()
        turma_combo = ttk.Combobox(main_frame, textvariable=turma_var,
                                   values=[f"{t['id']} - {t['nome_disciplina']}" for t in turmas],
                                   state="readonly", width=40, font=('Arial', 10))
        turma_combo.set(f"{turmas[0]['id']} - {turmas[0]['nome_disciplina']}")
        turma_combo.pack(fill=tk.X, pady=(3, 15))
        
        # Nome
        tk.Label(main_frame, text="Nome do Aluno:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        nome_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        nome_entry.pack(fill=tk.X, pady=(3, 20))
        
        def cadastrar():
            if not nome_entry.get():
                messagebox.showerror("Erro", "O nome é obrigatório!")
                return
            
            tid = turma_var.get().split(' - ')[0]
            nome_aluno = nome_entry.get()
            
            # Criar usuário para o aluno automaticamente
            aluno_username = self.db.generate_username_from_name(nome_aluno)
            aluno_password = self.db.generate_temp_password()
            
            # Verificar se já existe um usuário com esse nome
            user_exists = aluno_username in self.db.users
            
            # Buscar turno da turma
            turno_turma = get_turno_turma(tid)
            
            if not user_exists:
                # Criar novo usuário aluno com matrícula
                success, msg = self.db.add_user(aluno_username, aluno_password, 'aluno', 
                                              turno=turno_turma, pending=False, 
                                              matricula=nova_matricula)
                if not success:
                    messagebox.showerror("Erro", f"Erro ao criar usuário do aluno: {msg}")
                    return
            else:
                # Se usuário já existe, apenas associar/atualizar a matrícula
                self.db.set_student_matricula(aluno_username, nova_matricula)
            
            resp = self._send_request(f"ADD_ALUNO|{tid}|{nova_matricula}|{nome_aluno}")
            if resp:
                # Mensagem de sucesso com informações do login
                msg_sucesso = f"Aluno cadastrado com sucesso!\nMatrícula: {nova_matricula}\n\n"
                if not user_exists:
                    msg_sucesso += f"🔑 Login criado automaticamente:\n"
                    msg_sucesso += f"Usuário: {aluno_username}\n"
                    msg_sucesso += f"Senha: {aluno_password}\n"
                    msg_sucesso += f"Turno: {turno_turma.title()}\n\n"
                    msg_sucesso += "⚠️ IMPORTANTE: Anote essas credenciais!\n"
                    msg_sucesso += "O aluno deve fazer login e alterar a senha.\n\n"
                else:
                    msg_sucesso += f"✅ Aluno associado ao usuário existente: {aluno_username}\n\n"
                
                msg_sucesso += resp
                messagebox.showinfo("Sucesso", msg_sucesso)
                dialog.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao cadastrar aluno")
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="Cadastrar", command=cadastrar, 
                  style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                  style='Secondary.TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos (ESC cancela, Enter cadastra)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
    def _refresh_aluno_list(self, id_t):
        """Busca e exibe a lista de alunos para uma turma específica."""
        if not id_t:
            return

        turma_resp = self._send_request(f"GET_TURMA_DATA|{id_t}")
        if not turma_resp or "ERRO" in turma_resp:
            messagebox.showerror("Erro", "Turma não encontrada")
            return

        disc, prof = turma_resp.split('|')
        
        # Buscar turno da turma
        turno_turma = get_turno_turma(id_t)
        turno_usuario = self.db.users.get(self.username, {}).get('turno', 'matutino')
        
        # Verificar se usuário tem acesso a esta turma (por turno)
        if self.role != 'admin':
            if turno_turma != turno_usuario:
                messagebox.showerror("Acesso Negado", 
                                   f"Você não tem acesso a esta turma.\n"
                                   f"Turno da turma: {turno_turma.title()}\n"
                                   f"Seu turno: {turno_usuario.title()}")
                return
        
        resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{id_t}")

        if not resp or "Nenhum aluno" in resp:
            self._update_display(f"Alunos da Turma {id_t} - {disc}", [], [])
            return

        alunos_data = []
        for linha in resp.strip().split('\n'):
            if not linha: continue
            partes = linha.split(', ')
            matricula, nome = partes[0].split(': ')[1], partes[1].split(': ')[1]
            np1, np2, pim, media = "0.0", "0.0", "0.0", "0.0"
            for p in partes[2:]:
                if p.startswith('NP1:'): np1 = p.split(': ')[1]
                elif p.startswith('NP2:'): np2 = p.split(': ')[1]
                elif p.startswith('PIM:'): pim = p.split(': ')[1]
                elif p.startswith('Média:'): media = p.split(': ')[1]
            alunos_data.append([matricula, nome, np1, np2, pim, media])

        # Suplementa notas do arquivo local (fallback)
        try:
            notas_map = load_notas_dat()
            if notas_map:
                for row in alunos_data:
                    m = str(row[0])
                    if m in notas_map:
                        a, b, c, d = notas_map[m]
                        if row[2] in ("0.0", "0"): row[2] = a
                        if row[3] in ("0.0", "0"): row[3] = b
                        if row[4] in ("0.0", "0"): row[4] = c
                        if row[5] in ("0.0", "0"): row[5] = d
        except Exception:
            pass

        # Calcula e adiciona faltas
        faltas_map = {}
        try:
            for rec in read_presencas_dat(id_t):
                if not rec.get('presente'):
                    mkey = str(rec.get('matricula'))
                    faltas_map[mkey] = faltas_map.get(mkey, 0) + 1
        except Exception:
            pass

        # Calcula status final e formata a linha para exibição
        # Lógica correta de aprovação conforme especificado
        for row in alunos_data:
            # Converter notas para float
            np1_val = float(row[2]) if row[2] and row[2] != "0.0" else 0.0
            np2_val = float(row[3]) if row[3] and row[3] != "0.0" else 0.0
            pim_val = float(row[4]) if row[4] and row[4] != "0.0" else 0.0
            media_val = float(row[5]) if row[5] else 0.0
            faltas = faltas_map.get(str(row[0]), 0)
            
            # Buscar nota de exame do arquivo
            nota_exame = get_nota_exame(row[0])
            
            # Verificar se há notas atribuídas
            tem_notas = (np1_val > 0 or np2_val > 0 or pim_val > 0)
            
            # Determinar status conforme lógica especificada
            if not tem_notas:
                # Se não há nenhuma nota atribuída
                status = "Pendente Atribuir Notas"
            elif media_val >= 7.0:
                # Se média >= 7, aprovado direto
                status = "Aprovado"
            elif media_val < 7.0 and nota_exame == 0.0:
                # Se média < 7 e exame vazio, pendente exame
                status = "Pendente Exame"
            elif media_val < 7.0 and nota_exame >= 5.0:
                # Se média < 7 mas exame >= 5, aprovado
                status = "Aprovado (Exame)"
            elif media_val < 7.0 and nota_exame < 5.0:
                # Se média < 7 e exame < 5, reprovado
                status = "Reprovado"
            else:
                status = "Pendente"
            
            # Adicionar turno
            turno_icone = {'matutino': '', 'vespertino': '', 'noturno': ''}.get(turno_turma, '🕐')
            turno_display = f"{turno_icone} {turno_turma.title()}"
            
            row.extend([str(faltas), turno_display, f"{nota_exame:.1f}", status])

        headers = ["Matrícula", "Nome", "NP1", "NP2", "PIM", "Média", "Faltas", "Turno", "Exame", "Status"]
        self._update_display(f"Alunos da Turma {id_t} - {disc}", headers, alunos_data)

    def editar_aluno(self):
        # Apenas admin pode editar alunos
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem editar alunos.")
            return
        
        # Criar dialog de seleção com menu suspenso
        sel_dialog = tk.Toplevel(self)
        sel_dialog.title("Editar Aluno - Selecionar Tipo")
        sel_dialog.geometry("450x180")
        sel_dialog.transient(self)
        sel_dialog.grab_set()
        _center_window(sel_dialog)
        
        try:
            _apply_popup_theme(sel_dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(sel_dialog)
        
        main_frame = tk.Frame(sel_dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Selecione o tipo de aluno para editar:", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(pady=(0, 15))
        
        # Menu suspenso
        tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var,
                                 values=['Alunos com Turma (sistema C)', 'Alunos sem Turma (apenas usuários)'],
                                 state="readonly", width=40, font=('Arial', 10))
        tipo_combo.set('Alunos com Turma (sistema C)')
        tipo_combo.pack(fill=tk.X, pady=(0, 20))
        
        result = {'tipo': None}
        
        def confirmar():
            if tipo_var.get() == 'Alunos com Turma (sistema C)':
                result['tipo'] = 'com_turma'
            else:
                result['tipo'] = 'sem_turma'
            sel_dialog.destroy()
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Continuar", command=confirmar, 
                  style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=sel_dialog.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)
        
        self.wait_window(sel_dialog)
        
        if not result['tipo']:
            return
        
        if result['tipo'] == 'com_turma':
            self._editar_aluno_com_turma()
        else:
            self._editar_aluno_sem_turma()
    
    def _editar_aluno_com_turma(self):
        """Edita aluno que está em uma turma (sistema C)"""
        # Combined selector: choose turma then aluno in the same dialog
        sel = self._combined_turma_aluno_selector(title="Editar Aluno com Turma")
        if not sel: return
        id_t, mat = sel
        
        # Buscar username do usuário pela matrícula
        username_aluno = None
        for uname, udata in self.db.users.items():
            if udata.get('role') == 'aluno' and udata.get('matricula') == int(mat):
                username_aluno = uname
                break
        
        dialog = tk.Toplevel(self)
        dialog.configure(bg=self.colors['card'])
        _set_window_icon(dialog)
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dialog.title(f"Editando Aluno {mat}")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de dados básicos (turma C)
        dados_frame = ttk.Frame(notebook)
        notebook.add(dados_frame, text="Dados da Turma")
        
        resp = self._send_request(f"GET_ALUNO_DATA|{mat}")
        if resp and "ERRO" not in resp:
            nome = resp
            
            ttk.Label(dados_frame, text="Matrícula:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10,0), padx=10)
            mat_label = tk.Label(dados_frame, text=mat, font=('Arial', 11), 
                                bg=self.colors['border'], fg=self.colors['text'], 
                                relief='solid', bd=1, padx=8, pady=5)
            mat_label.pack(fill=tk.X, pady=(3, 15), padx=10)
            
            ttk.Label(dados_frame, text="Nome (na turma):").pack(anchor="w", pady=(10,0), padx=10)
            nome_entry = ttk.Entry(dados_frame, width=40, font=('Arial', 10))
            nome_entry.insert(0, nome)
            nome_entry.pack(fill=tk.X, pady=5, padx=10)
            
            # Aba de trocar turma (apenas admin)
            turma_frame = ttk.Frame(notebook)
            notebook.add(turma_frame, text="Trocar Turma")
            
            ttk.Label(turma_frame, text="Turma Atual:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10,0), padx=10)
            ttk.Label(turma_frame, text=f"ID {id_t}", font=('Arial', 11)).pack(anchor="w", padx=10, pady=(0, 15))
            
            ttk.Label(turma_frame, text="Nova Turma:", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10,0), padx=10)
            
            # Buscar turmas disponíveis
            turmas_disponiveis = self._get_turmas_list()
            nova_turma_var = tk.StringVar()
            
            nova_turma_combo = ttk.Combobox(turma_frame, textvariable=nova_turma_var,
                                           values=[f"{t['id']} - {t['nome_disciplina']}" for t in turmas_disponiveis],
                                           state="readonly", width=40)
            nova_turma_combo.pack(anchor='w', padx=10, pady=(5, 15))
            
            ttk.Label(turma_frame, text="Atenção: Esta ação não pode ser desfeita facilmente.", 
                     font=('Arial', 9, 'italic')).pack(anchor='w', padx=10, pady=(10, 5))
            
            def trocar_turma():
                if not nova_turma_var.get():
                    messagebox.showwarning("Aviso", "Selecione uma turma!")
                    return
                
                nova_turma_id = nova_turma_var.get().split(' - ')[0]
                
                if nova_turma_id == id_t:
                    messagebox.showwarning("Aviso", "O aluno já está nesta turma!")
                    return
                
                # Confirmar ação
                if not messagebox.askyesno("Confirmar", 
                    f"Tem certeza que deseja mover o aluno {mat} da turma {id_t} para a turma {nova_turma_id}?\n\n"
                    "Esta operação irá:\n"
                    "1. Remover o aluno da turma atual\n"
                    "2. Adicionar na nova turma com as mesmas informações",
                    icon='warning'):
                    return
                
                # Deletar da turma atual
                del_resp = self._send_request(f"DELETE_ALUNO|{mat}")
                if not del_resp or "ERRO" in del_resp:
                    messagebox.showerror("Erro", "Erro ao remover aluno da turma atual")
                    return
                
                # Adicionar na nova turma
                add_resp = self._send_request(f"ADD_ALUNO|{nova_turma_id}|{mat}|{nome}")
                if add_resp:
                    if "SUCESSO" in add_resp or "adicionado" in add_resp.lower():
                        messagebox.showinfo("Sucesso", f"Aluno transferido para a turma {nova_turma_id} com sucesso!")
                        dialog.destroy()
                        self.listar_turmas()
                    else:
                        messagebox.showinfo("Servidor", add_resp)
                else:
                    messagebox.showerror("Erro", "Erro ao adicionar aluno na nova turma")
            
            ttk.Button(turma_frame, text="Trocar Turma", command=trocar_turma, 
                      style='Dialog.TButton').pack(anchor='w', padx=10, pady=(10, 0))
            
            # Aba de dados do usuário
            if username_aluno:
                user_frame = ttk.Frame(notebook)
                notebook.add(user_frame, text="Dados do Usuário")
                
                user_data = self.db.get_user_data(username_aluno)
                
                ttk.Label(user_frame, text="Username:").pack(anchor="w", pady=(10,0), padx=10)
                ttk.Label(user_frame, text=username_aluno, font=('Arial', 10, 'bold')).pack(anchor="w", padx=10)
                
                ttk.Label(user_frame, text="Matrícula (usuário):", font=('Arial', 10, 'bold')).pack(anchor="w", pady=(10,0), padx=10)
                user_mat_label = tk.Label(user_frame, text=str(user_data.get('matricula', 'Não atribuída')), 
                                         font=('Arial', 11), bg=self.colors['border'], fg=self.colors['text'], 
                                         relief='solid', bd=1, padx=8, pady=5)
                user_mat_label.pack(fill=tk.X, pady=(3, 15), padx=10)
                
                ttk.Label(user_frame, text="Email:").pack(anchor="w", pady=(10,0), padx=10)
                email_entry = ttk.Entry(user_frame, width=40, font=('Arial', 10))
                email_entry.insert(0, user_data.get('email', ''))
                email_entry.pack(fill=tk.X, pady=5, padx=10)
            
            def save_changes():
                # Atualiza nome na turma C
                up_resp = self._send_request(f"UPDATE_ALUNO|{mat}|{nome_entry.get()}")
                if up_resp and "SUCESSO" in up_resp:
                    # Atualizar dados do usuário se existir
                    if username_aluno:
                        new_user_data = {
                            'email': email_entry.get()
                        }
                        
                        success, msg = self.db.update_user(username_aluno, new_user_data)
                        if not success:
                            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {msg}")
                            return
                    
                    messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso!")
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro", up_resp or "Erro ao atualizar")
            
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Salvar Alterações", command=save_changes, style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
            
            def do_delete_aluno():
                if messagebox.askyesno("Confirmar", f"Excluir aluno de matrícula {mat}?", icon='warning'):
                    resp = self._send_request(f"DELETE_ALUNO|{mat}")
                    if resp: messagebox.showinfo("Servidor", resp); dialog.destroy(); self.listar_turmas()
            
            ttk.Button(btn_frame, text="Excluir Aluno", command=do_delete_aluno, style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        else:
            messagebox.showerror("Erro", resp or "N/A")
            dialog.destroy()
    
    def _editar_aluno_sem_turma(self):
        """Edita aluno que é apenas usuário (sem turma atribuída)"""
        # Buscar alunos sem turma no sistema C
        alunos_sem_turma = []
        
        print(f"[DEBUG] Procurando alunos sem turma...")
        for username, data in self.db.users.items():
            if data.get('role') == 'aluno':
                matricula = data.get('matricula')
                print(f"[DEBUG] Verificando {username} - Matrícula: {matricula}")
                
                # Verificar se tem matrícula
                tem_turma = False
                if matricula:
                    # Verificar se existe no sistema C
                    resp = self._send_request(f"GET_ALUNO_DATA|{matricula}")
                    print(f"[DEBUG] Resposta para {matricula}: {resp}")
                    if resp and "ERRO" not in resp:
                        tem_turma = True
                
                # Se não tem turma no sistema C, adicionar à lista
                if not tem_turma:
                    print(f"[DEBUG] {username} NÃO tem turma - adicionando à lista")
                    status = data.get('status', 'approved')
                    alunos_sem_turma.append({
                        'username': username,
                        'matricula': matricula if matricula else 'Não atribuída',
                        'email': data.get('email', 'Não cadastrado'),
                        'status': status
                    })
                else:
                    print(f"[DEBUG] {username} TEM turma - ignorando")
        
        print(f"[DEBUG] Total de alunos sem turma: {len(alunos_sem_turma)}")
        
        if not alunos_sem_turma:
            messagebox.showinfo("Informação", "Não há alunos sem turma para editar.\n\nTodos os alunos já estão associados a turmas.")
            return
        
        # Dialog de seleção
        sel_dialog = tk.Toplevel(self)
        sel_dialog.title("Selecionar Aluno sem Turma")
        sel_dialog.geometry("800x700")
        sel_dialog.transient(self)
        sel_dialog.grab_set()
        _center_window(sel_dialog)
        
        try:
            _apply_popup_theme(sel_dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(sel_dialog)
        
        main_frame = tk.Frame(sel_dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Alunos sem Turma Atribuída:", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Lista de alunos
        listbox_frame = tk.Frame(main_frame, bg=self.colors['card'])
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                            font=('Arial', 10), bg=self.colors['input_bg'], 
                            fg=self.colors['text'])
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for aluno in alunos_sem_turma:
            status_badge = "Aprovado" if aluno['status'] == 'approved' else "Pendente"
            listbox.insert(tk.END, f"[{status_badge}] {aluno['username']} | Matrícula: {aluno['matricula']} | {aluno['email']}")
        
        result = {'aluno': None}
        
        def selecionar():
            sel = listbox.curselection()
            if sel:
                result['aluno'] = alunos_sem_turma[sel[0]]
                sel_dialog.destroy()
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Editar Selecionado", command=selecionar, 
                  style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=sel_dialog.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)
        
        self.wait_window(sel_dialog)
        
        if not result['aluno']:
            return
        
        # Abrir dialog de edição
        aluno = result['aluno']
        self._abrir_editor_aluno_sem_turma(aluno)
    
    def _abrir_editor_aluno_sem_turma(self, aluno_info):
        """Abre interface de edição para aluno sem turma"""
        username = aluno_info['username']
        user_data = self.db.get_user_data(username)
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar Aluno: {username}")
        dialog.geometry("800x700")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Cabeçalho com nome e status discreto
        header_frame = tk.Frame(main_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text=f"Editando: {username}", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(side=tk.LEFT)
        
        # Status discreto (badge pequeno)
        status = user_data.get('status', 'approved')
        status_color = '#4CAF50' if status == 'approved' else '#FF9800'
        status_text = '✓' if status == 'approved' else '⏳'
        
        status_badge = tk.Label(header_frame, text=status_text, 
                               font=('Arial', 9, 'bold'), bg=status_color, fg='white',
                               padx=6, pady=2, relief='flat')
        status_badge.pack(side=tk.LEFT, padx=(10, 0))
        
        # Matrícula (read-only, apenas visualização)
        info_frame = tk.Frame(main_frame, bg=self.colors['border'], relief='solid', bd=1, padx=12, pady=8)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(info_frame, text=f"Matrícula: {user_data.get('matricula', 'Não atribuída')}", 
                font=('Arial', 10), bg=self.colors['border'], fg=self.colors['text']).pack(anchor='w')
        
        # Email
        tk.Label(main_frame, text="Email:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        email_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        email_entry.insert(0, user_data.get('email', ''))
        email_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Associar a turma
        turma_frame = tk.LabelFrame(main_frame, text="Associar a uma Turma (Opcional)", 
                                    bg=self.colors['card'], fg=self.colors['text'], 
                                    font=('Arial', 10, 'bold'), padx=12, pady=10)
        turma_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Buscar turmas disponíveis
        turmas = self._get_turmas_list()
        
        turma_var = tk.StringVar()
        if turmas:
            turma_combo = ttk.Combobox(turma_frame, textvariable=turma_var,
                                      values=['Não associar'] + [f"{t['id']} - {t['nome_disciplina']}" for t in turmas],
                                      state="readonly", width=45, font=('Arial', 10))
            turma_combo.set('Não associar')
            turma_combo.pack(fill=tk.X)
        else:
            tk.Label(turma_frame, text="Nenhuma turma disponível", 
                    font=('Arial', 10), bg=self.colors['card'], 
                    fg=self.colors['text_secondary']).pack()
        
        def salvar_tudo():
            """Salva email e associa turma se selecionada"""
            # 1. Atualizar email
            new_data = {'email': email_entry.get()}
            
            if not self.db.validate_email(new_data['email']):
                messagebox.showerror("Erro", "Email inválido!")
                return
            
            success, msg = self.db.update_user(username, new_data)
            if not success:
                messagebox.showerror("Erro", f"Erro ao atualizar email: {msg}")
                return
            
            # 2. Associar a turma se selecionada
            if turmas and turma_var.get() != 'Não associar':
                tid = turma_var.get().split(' - ')[0]
                matricula = user_data.get('matricula')
                
                if not matricula:
                    messagebox.showerror("Erro", "Aluno não possui matrícula!")
                    return
                
                # Adicionar aluno na turma C
                resp = self._send_request(f"ADD_ALUNO|{tid}|{matricula}|{username}")
                if resp:
                    if "SUCESSO" in resp or "adicionado" in resp.lower():
                        messagebox.showinfo("Sucesso", 
                                          f"Email atualizado\n"
                                          f"Aluno associado à turma {tid}\n\n"
                                          "Todas as alterações foram salvas!")
                    else:
                        messagebox.showinfo("Sucesso", 
                                          f"Email atualizado\n\n"
                                          f"Turma: {resp}")
                else:
                    messagebox.showwarning("Parcial", 
                                         f"Email atualizado\n"
                                         f"Erro ao associar turma")
            else:
                messagebox.showinfo("Sucesso", "Email atualizado com sucesso!")
            
            dialog.destroy()
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Salvar e Fechar", command=salvar_tudo, 
                  style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)
            
    def lancar_notas(self):
        id_t = self._ask_turma_dropdown(title="Lançar Notas - Selecionar Turma")
        if not id_t: return

        # Verifica se a turma existe
        turma_resp = self._send_request(f"GET_TURMA_DATA|{id_t}")
        if not turma_resp or "ERRO" in turma_resp:
            messagebox.showerror("Erro", "Turma não encontrada!")
            return
        
        # Verificação de acesso adicional (segurança extra)
        if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
            messagebox.showerror("Acesso Negado", 
                               f"Você não tem permissão para alterar notas desta turma (ID: {id_t}).\n"
                               f"Entre em contato com o administrador para solicitar acesso.")
            return

        # Popup para escolher tipo de nota
        tipo_nota_dialog = tk.Toplevel(self)
        tipo_nota_dialog.title("Tipo de Lançamento")
        tipo_nota_dialog.geometry("550x250")
        tipo_nota_dialog.transient(self)
        tipo_nota_dialog.grab_set()
        tipo_nota_dialog.resizable(False, False)
        try:
            _apply_popup_theme(tipo_nota_dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(tipo_nota_dialog)
        
        # Centralizar popup
        tipo_nota_dialog.update_idletasks()
        width = tipo_nota_dialog.winfo_width()
        height = tipo_nota_dialog.winfo_height()
        x = (tipo_nota_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (tipo_nota_dialog.winfo_screenheight() // 2) - (height // 2)
        tipo_nota_dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        selected_tipo = tk.StringVar(value="")
        
        # Frame principal
        main_frame = ttk.Frame(tipo_nota_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título
        ttk.Label(main_frame, text="Selecione o tipo de nota a lançar:", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 20))
        
        # Combobox - layout vertical para evitar cortes
        ttk.Label(main_frame, text="Tipo de Nota:", font=('Arial', 10)).pack(anchor='w', pady=(0, 5))
        tipo_combo = ttk.Combobox(main_frame, textvariable=selected_tipo, 
                                 values=["Notas Comuns (NP1, NP2, PIM)", "Nota de Exame"],
                                 state='readonly', width=35, font=('Arial', 10))
        tipo_combo.pack(fill=tk.X, pady=(0, 10))
        tipo_combo.current(0)  # Selecionar o primeiro por padrão
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(20, 0))
        
        def confirmar_tipo():
            if selected_tipo.get():
                tipo_nota_dialog.destroy()
                # Determinar o tipo baseado na seleção
                tipo = "comum" if "Comuns" in selected_tipo.get() else "exame"
                NotasDialog(self, id_t, tipo)
            else:
                messagebox.showwarning("Aviso", "Por favor, selecione um tipo de nota!")
        
        confirm_btn = ttk.Button(btn_frame, text="Confirmar", command=confirmar_tipo, 
                  style='Dialog.TButton')
        confirm_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=tipo_nota_dialog.destroy, 
                  style='Secondary.TButton')
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar atalhos (ESC cancela, Enter confirma)
        _setup_dialog_shortcuts(tipo_nota_dialog, ok_button=confirm_btn, cancel_callback=tipo_nota_dialog.destroy)

        class NotasDialog:
            def __init__(self, parent, id_turma, tipo_nota):
                self.dialog = tk.Toplevel(parent)
                self.parent = parent
                self.id_turma = id_turma
                self.tipo_nota = tipo_nota  # "comum" ou "exame"
                # Herdar cores e fontes do parent
                self.colors = parent.colors
                self.fonts = parent.fonts
                try:
                    _apply_popup_theme(self.dialog, self.colors, self.fonts, getattr(parent, 'style', None))
                except Exception:
                    pass
                _set_window_icon(self.dialog)
                
                # Título baseado no tipo
                titulo = f"Lançamento de Notas Comuns - Turma {id_turma}" if tipo_nota == "comum" else f"Lançamento de Exames - Turma {id_turma}"
                self.dialog.title(titulo)
                
                # Configurar para ocupar altura inteira da tela
                screen_width = self.dialog.winfo_screenwidth()
                screen_height = self.dialog.winfo_screenheight()
                largura = 800
                altura = screen_height - 90  # Deixa margem para barra de tarefas
                x = (screen_width - largura) // 2
                y = 0
                self.dialog.geometry(f"{largura}x{altura}+{x}+{y}")
                
                self.dialog.transient(parent)
                self.dialog.grab_set()
                self.setup_ui()
                
            def setup_ui(self):
                # Frame principal
                main_frame = ttk.Frame(self.dialog)
                main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Frame para a tabela de alunos
                table_frame = ttk.LabelFrame(main_frame, text="Lista de Alunos")
                table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                # Frame para lançamento de notas
                label_frame = "Lançamento de Notas" if self.tipo_nota == "comum" else "Lançamento de Exames"
                self.nota_frame = ttk.LabelFrame(main_frame, text=label_frame)
                self.nota_frame.pack(fill=tk.X, padx=5, pady=10)
                
                # Definir colunas baseado no tipo de nota
                if self.tipo_nota == "comum":
                    self.columns = ("Matrícula", "Nome", "NP1", "NP2", "PIM", "Média")
                else:  # exame
                    self.columns = ("Matrícula", "Nome", "Média", "Exame", "Status")
                
                self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings", style="Custom.Treeview")
                
                # Configurar cabeçalhos
                for col in self.columns:
                    self.tree.heading(col, text=col, anchor=tk.CENTER)
                    self.tree.column(col, anchor=tk.CENTER, minwidth=80)
                
                # Configurar cores alternadas com suporte ao tema escuro
                self.tree.tag_configure('odd', background=self.colors.get('row_odd', '#f9f9f9'), 
                                       foreground=self.colors.get('text', '#172B4D'))
                self.tree.tag_configure('even', background=self.colors.get('row_even', 'white'),
                                       foreground=self.colors.get('text', '#172B4D'))
                
                # Adicionar scrollbar
                # Layout da tabela
                self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                # Frame para os campos de nota
                fields_frame = ttk.Frame(self.nota_frame)
                fields_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Label explicativa dos pesos (somente para notas comuns)
                if self.tipo_nota == "comum":
                    info_frame = ttk.Frame(fields_frame)
                    info_frame.pack(fill=tk.X, pady=(0,5))
                    ttk.Label(info_frame, text="Pesos: NP1 (40%) + NP2 (40%) + PIM (20%)", 
                             font=("Helvetica", 9, "italic")).pack(side=tk.LEFT)
                else:
                    info_frame = ttk.Frame(fields_frame)
                    info_frame.pack(fill=tk.X, pady=(0,5))
                    ttk.Label(info_frame, text="Exame: para alunos com média < 7 (nota ≥ 5 = aprovado)", 
                             font=("Helvetica", 9, "italic"), foreground='#FF9800').pack(side=tk.LEFT)
                
                # Campos para inserção de notas - baseado no tipo
                self.nota_entries = {}
                entrada_frame = ttk.Frame(fields_frame)
                entrada_frame.pack(fill=tk.X, pady=(5, 0))
                
                if self.tipo_nota == "comum":
                    notas_campos = ["NP1", "NP2", "PIM"]
                else:
                    notas_campos = ["Exame"]
                
                for i, nota in enumerate(notas_campos):
                    frame = ttk.Frame(entrada_frame)
                    frame.pack(side=tk.LEFT, padx=8)
                    
                    ttk.Label(frame, text=f"{nota}:").pack(side=tk.LEFT, padx=(0, 5))
                    entry = ttk.Entry(frame, width=10)
                    entry.pack(side=tk.LEFT)
                    self.nota_entries[nota] = entry
                
                # Botões
                btn_frame = ttk.Frame(self.nota_frame)
                btn_frame.pack(fill=tk.X, pady=5)
                
                save_btn = ttk.Button(btn_frame, text="Atualizar Notas", 
                          command=self.atualizar_notas)
                save_btn.pack(side=tk.LEFT, padx=5)
                # Removed Recomputar button per UX request
                cancel_btn = ttk.Button(btn_frame, text="Cancelar", 
                          command=lambda: self.dialog.destroy())
                cancel_btn.pack(side=tk.RIGHT, padx=5)
                
                # Configurar atalhos (ESC fecha, Enter atualiza)
                _setup_dialog_shortcuts(self.dialog, ok_button=save_btn, cancel_callback=self.dialog.destroy)
                
                # Bind da seleção
                self.tree.bind('<<TreeviewSelect>>', self.on_select)
                
                # Carregar dados
                self.carregar_dados()
                
                # Selecionar automaticamente o primeiro aluno após carregar os dados
                self.dialog.after(100, self.selecionar_primeiro_aluno)
                
            def selecionar_primeiro_aluno(self):
                """Seleciona automaticamente o primeiro aluno da lista"""
                items = self.tree.get_children()
                if items:
                    self.tree.selection_set(items[0])
                    self.tree.focus(items[0])
                    # Disparar o evento de seleção manualmente
                    self.tree.event_generate('<<TreeviewSelect>>')
                
            def carregar_dados(self):
                resp = self.parent._send_request(f"LIST_ALUNOS_POR_TURMA|{self.id_turma}")
                if resp and "Nenhum aluno" not in resp:
                    for i, linha in enumerate(resp.strip().split('\n')):
                        if linha:
                            partes = linha.split(', ')
                            matricula = partes[0].split(': ')[1]
                            nome = partes[1].split(': ')[1]
                            # Try to parse provided grades
                            np1 = np2 = pim = media = 0.0
                            for p in partes[2:]:
                                if p.startswith('NP1:'):
                                    np1 = float(p.split(': ')[1])
                                elif p.startswith('NP2:'):
                                    np2 = float(p.split(': ')[1])
                                elif p.startswith('PIM:'):
                                    pim = float(p.split(': ')[1])
                                elif p.startswith('Média:'):
                                    try:
                                        media = float(p.split(': ')[1])
                                    except Exception:
                                        media = 0.0
                            
                            # Buscar nota de exame
                            exame = get_nota_exame(matricula)
                            
                            # Calcular status com lógica correta
                            tem_notas = (np1 > 0 or np2 > 0 or pim > 0)
                            if not tem_notas:
                                status = "Pendente Atribuir Notas"
                            elif media >= 7.0:
                                status = "Aprovado"
                            elif media < 7.0 and exame == 0.0:
                                status = "Pendente Exame"
                            elif media < 7.0 and exame >= 5.0:
                                status = "Aprovado (Exame)"
                            elif media < 7.0 and exame < 5.0:
                                status = "Reprovado"
                            else:
                                status = "Pendente"
                            
                            row_tags = ('even' if i % 2 == 0 else 'odd', 'aprovado' if 'Aprovado' in status else 'reprovado')
                            
                            # Inserir dados baseado no tipo de nota
                            if self.tipo_nota == "comum":
                                # Mostrar apenas Matrícula, Nome, NP1, NP2, PIM, Média
                                self.tree.insert("", tk.END, values=(matricula, nome, f"{np1:.1f}", f"{np2:.1f}", f"{pim:.1f}", f"{media:.1f}"),
                                              tags=row_tags)
                            else:  # exame
                                # Mostrar apenas Matrícula, Nome, Média, Exame, Status
                                self.tree.insert("", tk.END, values=(matricula, nome, f"{media:.1f}", f"{exame:.1f}", status),
                                              tags=row_tags)
                
            def calcular_media(self, np1, np2, pim):
                return (np1 * 4 + np2 * 4 + pim * 2) / 10
                
            def on_select(self, event):
                selection = self.tree.selection()
                if not selection:
                    return
                    
                try:
                    valores = self.tree.item(selection[0])["values"]
                    
                    if self.tipo_nota == "comum":
                        # Carregar NP1, NP2, PIM (índices 2, 3, 4)
                        self.nota_entries["NP1"].delete(0, tk.END)
                        self.nota_entries["NP1"].insert(0, str(valores[2]))
                        
                        self.nota_entries["NP2"].delete(0, tk.END)
                        self.nota_entries["NP2"].insert(0, str(valores[3]))
                        
                        self.nota_entries["PIM"].delete(0, tk.END)
                        self.nota_entries["PIM"].insert(0, str(valores[4]))
                    else:  # exame
                        # Carregar apenas Exame (índice 3)
                        self.nota_entries["Exame"].delete(0, tk.END)
                        self.nota_entries["Exame"].insert(0, str(valores[3]))
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar notas: {str(e)}")
                
            def atualizar_notas(self):
                selection = self.tree.selection()
                if not selection:
                    messagebox.showwarning("Aviso", "Selecione um aluno primeiro!")
                    return
                
                try:
                    item = selection[0]
                    valores_atuais = self.tree.item(item)["values"]
                    matricula = valores_atuais[0]

                    if self.tipo_nota == "comum":
                        # Atualizar apenas notas comuns (NP1, NP2, PIM)
                        # 1. Obtenha as notas atuais diretamente da tabela como base.
                        np1_atual = float(valores_atuais[2])
                        np2_atual = float(valores_atuais[3])
                        pim_atual = float(valores_atuais[4])

                        # 2. Leia o que foi digitado nos campos.
                        np1_texto = self.nota_entries["NP1"].get().strip()
                        np2_texto = self.nota_entries["NP2"].get().strip()
                        pim_texto = self.nota_entries["PIM"].get().strip()

                        # 3. Use o valor digitado se houver. Se não, mantenha o valor atual.
                        np1 = float(np1_texto) if np1_texto else np1_atual
                        np2 = float(np2_texto) if np2_texto else np2_atual
                        pim = float(pim_texto) if pim_texto else pim_atual

                        # Validar notas
                        if not (0 <= np1 <= 10 and 0 <= np2 <= 10 and 0 <= pim <= 10):
                            messagebox.showerror("Erro", "As notas NP1, NP2 e PIM devem estar entre 0 e 10!")
                            return
                        
                        # Calcular média
                        media = self.calcular_media(np1, np2, pim)
                        
                        # Atualizar valores na árvore
                        novos_valores = (matricula, valores_atuais[1], f"{np1:.1f}", f"{np2:.1f}", f"{pim:.1f}", f"{media:.1f}")
                        self.tree.item(item, values=novos_valores)
                        
                        # Envia para o servidor (notas do semestre)
                        resp = self.parent._send_request(f"UPDATE_NOTAS|{matricula}|{np1}|{np2}|{pim}|{round(media, 1)}")
                        
                        # Verificar se houve sucesso
                        if resp and "SUCESSO" in resp:
                            messagebox.showinfo("Sucesso", "Notas atualizadas com sucesso!")
                            
                            # Recarregar os dados da tabela para mostrar as notas atualizadas
                            self.tree.delete(*self.tree.get_children())
                            self.carregar_dados()
                            
                            # Reselecionar o aluno atualizado
                            for item in self.tree.get_children():
                                valores = self.tree.item(item)["values"]
                                if valores[0] == matricula:
                                    self.tree.selection_set(item)
                                    self.tree.focus(item)
                                    self.tree.see(item)
                                    break
                        else:
                            messagebox.showerror("Erro", f"Falha ao atualizar notas: {resp}")
                    
                    else:  # exame
                        # Atualizar apenas nota de exame
                        # Buscar as notas atuais do aluno do servidor
                        resp_aluno = self.parent._send_request(f"LIST_ALUNOS_POR_TURMA|{self.id_turma}")
                        np1 = np2 = pim = media = 0.0
                        
                        if resp_aluno and "Nenhum aluno" not in resp_aluno:
                            for linha in resp_aluno.strip().split('\n'):
                                if linha:
                                    partes = linha.split(', ')
                                    mat = partes[0].split(': ')[1]
                                    if mat == matricula:
                                        for p in partes[2:]:
                                            if p.startswith('NP1:'):
                                                np1 = float(p.split(': ')[1])
                                            elif p.startswith('NP2:'):
                                                np2 = float(p.split(': ')[1])
                                            elif p.startswith('PIM:'):
                                                pim = float(p.split(': ')[1])
                                            elif p.startswith('Média:'):
                                                try:
                                                    media = float(p.split(': ')[1])
                                                except Exception:
                                                    media = 0.0
                                        break
                        
                        # Obter nota de exame digitada
                        exame_atual = float(valores_atuais[3])
                        exame_texto = self.nota_entries["Exame"].get().strip()
                        exame = float(exame_texto) if exame_texto else exame_atual
                        
                        # Validar nota de exame
                        if not (0 <= exame <= 10):
                            messagebox.showerror("Erro", "A nota do Exame deve estar entre 0 e 10!")
                            return
                        
                        # Calcular status com lógica correta
                        tem_notas = (np1 > 0 or np2 > 0 or pim > 0)
                        if not tem_notas:
                            status = "Pendente Atribuir Notas"
                        elif media >= 7.0:
                            status = "Aprovado"
                        elif media < 7.0 and exame == 0.0:
                            status = "Pendente Exame"
                        elif media < 7.0 and exame >= 5.0:
                            status = "Aprovado (Exame)"
                        elif media < 7.0 and exame < 5.0:
                            status = "Reprovado"
                        else:
                            status = "Pendente"
                        
                        # Atualizar valores na árvore
                        novos_valores = (matricula, valores_atuais[1], f"{media:.1f}", f"{exame:.1f}", status)
                        self.tree.item(item, values=novos_valores)
                        
                        # Preserve parity tag and add status tag for coloring
                        try:
                            current_tags = self.tree.item(item, 'tags') or ()
                            parity = 'even' if ('even' in current_tags) or (self.tree.index(item) % 2 == 0) else 'odd'
                            status_tag = 'aprovado' if 'Aprovado' in status else 'reprovado'
                            new_tags = (parity, status_tag)
                            self.tree.item(item, tags=new_tags)
                        except Exception:
                            pass
                        
                        # Salvar nota de exame
                        set_nota_exame(matricula, exame)
                        
                        messagebox.showinfo("Sucesso", "Nota de exame atualizada com sucesso!")
                        
                        # Recarregar os dados da tabela para mostrar as notas atualizadas
                        self.tree.delete(*self.tree.get_children())
                        self.carregar_dados()
                        
                        # Reselecionar o aluno atualizado
                        for item in self.tree.get_children():
                            valores = self.tree.item(item)["values"]
                            if valores[0] == matricula:
                                self.tree.selection_set(item)
                                self.tree.focus(item)
                                self.tree.see(item)
                                break
                    
                    # Atualizar listagem principal em background
                    try:
                        self.parent._refresh_aluno_list(self.id_turma)
                    except Exception:
                        pass
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira apenas números válidos!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar notas: {str(e)}")
        
    def controle_presenca(self):
        """
        Interface de controle de presença para professores e administradores
        
        Permite:
            - Selecionar uma data via calendário
            - Marcar presença/ausência dos alunos
            - Salvar registros de presença por data
            - Visualizar presenças já registradas
        
        Características:
            - Cabeçalho fixo (não rola com a scrollbar)
            - Scrollbar dinâmica (só aparece quando necessário)
            - Cores visuais para status (verde=presente, vermelho=ausente)
        """
        # Solicitar seleção de turma via dropdown
        id_t = self._ask_turma_dropdown(title="Controle de Presença - Selecionar Turma")
        if not id_t: return
        
        # Verificar se a turma existe no servidor
        turma_resp = self._send_request(f"GET_TURMA_DATA|{id_t}")
        if not turma_resp or "ERRO" in turma_resp:
            messagebox.showerror("Erro", "Turma não encontrada!")
            return
        
        # Verificação de acesso adicional (segurança extra para professores)
        if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
            messagebox.showerror("Acesso Negado", 
                               f"Você não tem permissão para controlar presença desta turma (ID: {id_t}).\n"
                               f"Entre em contato com o administrador para solicitar acesso.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.configure(bg=self.colors['card'])
        _set_window_icon(dialog)
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        dialog.title(f"Controle de Presença - Turma {id_t}")
        
        # Configurar para tela cheia
        dialog.state('zoomed')  # Windows
        try:
            dialog.attributes('-zoomed', True)  # Linux/Unix
        except:
            pass
        
        # Frame principal com melhor layout
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header com título e instruções
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título principal
        title_label = ttk.Label(header_frame, text=f"Controle de Presença - Turma {id_t}", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w')
        
        # Instruções de uso
        instructions_frame = ttk.Frame(header_frame)
        instructions_frame.pack(fill=tk.X, pady=(5, 0))
        
        instructions_text = """INSTRUÇÕES DE USO:
• Clique no ícone 📅 para selecionar uma data no calendário
• Clique simples: seleciona a data | Duplo clique: confirma e carrega automaticamente
• Marque os alunos presentes/ausentes clicando na coluna "Presente"
• Use os botões de ação para salvar as alterações ou fechar"""
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, 
                                     font=('Arial', 9), foreground=self.colors.get('text_secondary', self.colors['text']))
        instructions_label.pack(anchor='w')
        
        # Frame superior para data (com seletor de calendário)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 15))

        # Frame para data com melhor design
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(date_frame, text="Data selecionada:", font=('Arial', 11, 'bold')).pack(anchor='w')
        date_var = tk.StringVar(value=time.strftime("%d/%m/%Y"))
        # Campo readonly com melhor estilo - apenas exibe a data selecionada
        data_entry = ttk.Entry(date_frame, width=15, textvariable=date_var, state='readonly',
                              font=('Arial', 11), justify='center')
        data_entry.pack(pady=(5, 0))

        def open_calendar(parent_window):
            cal_win = tk.Toplevel(parent_window)
            cal_win.configure(bg=self.colors['card'])
            _set_window_icon(cal_win)
            try:
                _apply_popup_theme(cal_win, self.colors, self.fonts, getattr(self, 'style', None))
            except Exception:
                pass
            cal_win.transient(parent_window)
            cal_win.grab_set()
            cal_win.title("Selecionar Data")
            cal_win.resizable(False, False)

            now = time.localtime()
            sel_month = tk.IntVar(value=now.tm_mon)
            sel_year = tk.IntVar(value=now.tm_year)
            selected_date = tk.StringVar(value="")  # Armazena data selecionada temporariamente

            # Header com título melhorado
            header = ttk.Frame(cal_win)
            header.pack(fill=tk.X, pady=(10, 5))

            # Título do mês/ano
            month_label = ttk.Label(header, font=('Arial', 14, 'bold'))
            month_label.pack()

            # Navegação melhorada
            nav_frame = ttk.Frame(cal_win)
            nav_frame.pack(fill=tk.X, pady=5)
            
            prev_btn = tk.Button(nav_frame, text="◀", font=('Arial', 12, 'bold'),
                               bg=self.colors['primary'], fg=self.colors['card'],
                               activebackground=self.colors['primary_hover'], activeforeground=self.colors['card'],
                               relief='flat', bd=0, cursor='hand2',
                               width=3, height=1)
            prev_btn.pack(side=tk.LEFT, padx=10)
            
            next_btn = tk.Button(nav_frame, text="▶", font=('Arial', 12, 'bold'),
                               bg=self.colors['primary'], fg=self.colors['card'],
                               activebackground=self.colors['primary_hover'], activeforeground=self.colors['card'],
                               relief='flat', bd=0, cursor='hand2',
                               width=3, height=1)
            next_btn.pack(side=tk.RIGHT, padx=10)

            # Corpo do calendário com melhor espaçamento
            cal_body = ttk.Frame(cal_win)
            cal_body.pack(padx=15, pady=10)

            # Exibição da data selecionada
            date_display_frame = ttk.Frame(cal_win)
            date_display_frame.pack(fill=tk.X, pady=(5, 10))
            
            date_display = ttk.Label(date_display_frame, 
                                   text="Nenhuma data selecionada",
                                   font=('Arial', 10),
                                   foreground=self.colors.get('text_secondary', self.colors['text']))
            date_display.pack()

            def draw_calendar():
                # Limpar widgets existentes
                for w in cal_body.winfo_children():
                    w.destroy()
                    
                y = sel_year.get()
                m = sel_month.get()
                
                # Atualizar título do mês
                month_label.configure(text=f"{calendar.month_name[m]} {y}")
                
                # Cabeçalho dos dias da semana (Brasil: Segunda a Domingo)
                week_days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                for i, wd in enumerate(week_days):
                    day_header = ttk.Label(cal_body, text=wd, font=('Arial', 9, 'bold'),
                                         foreground=self.colors.get('primary'))
                    day_header.grid(row=0, column=i, padx=3, pady=2, sticky='ew')
                
                # Dias do mês
                month_cal = calendar.monthcalendar(y, m)
                for r, week in enumerate(month_cal, start=1):
                    for c, day in enumerate(week):
                        if day == 0:
                            # Espaço vazio para dias de outros meses
                            ttk.Label(cal_body, text='').grid(row=r, column=c, padx=3, pady=2)
                        else:
                            def on_select(d=day):
                                selected_date.set(f"{d:02d}/{m:02d}/{y}")
                                date_display.configure(text=f"Data selecionada: {d:02d}/{m:02d}/{y}")
                                # Destacar botão selecionado
                                for widget in cal_body.winfo_children():
                                    if isinstance(widget, tk.Button) and widget['text'] == str(d):
                                        widget.configure(bg=self.colors['primary_hover'], fg=self.colors['card'])
                            
                            def on_double_click(d=day):
                                """Double click confirma a data automaticamente"""
                                selected_date.set(f"{d:02d}/{m:02d}/{y}")
                                date_var.set(f"{d:02d}/{m:02d}/{y}")
                                cal_win.destroy()
                                load_for_date(f"{d:02d}/{m:02d}/{y}")
                            
                            # Botão do dia com melhor estilo
                            day_btn = tk.Button(cal_body, text=str(day), 
                                              font=('Arial', 9),
                                              bg=self.colors['card'], 
                                              fg=self.colors['text'],
                                              activebackground=self.colors['primary_hover'],
                                              relief='solid', bd=1,
                                              cursor='hand2',
                                              width=3, height=1)
                            day_btn.grid(row=r, column=c, padx=3, pady=2)
                            day_btn.configure(command=on_select)
                            # Adicionar double click
                            day_btn.bind("<Double-Button-1>", lambda e, d=day: on_double_click(d))

            # Configurar navegação
            def prev_month():
                if sel_month.get() == 1:
                    sel_month.set(12)
                    sel_year.set(sel_year.get() - 1)
                else:
                    sel_month.set(sel_month.get() - 1)
                draw_calendar()
                
            def next_month():
                if sel_month.get() == 12:
                    sel_month.set(1)
                    sel_year.set(sel_year.get() + 1)
                else:
                    sel_month.set(sel_month.get() + 1)
                draw_calendar()
            
            prev_btn.configure(command=prev_month)
            next_btn.configure(command=next_month)
            
            # Botões de ação melhorados
            def confirmar():
                if selected_date.get():
                    date_var.set(selected_date.get())
                    cal_win.destroy()
                    load_for_date(selected_date.get())
                else:
                    messagebox.showwarning("Aviso", "Selecione uma data primeiro!", parent=cal_win)
            
            btn_frame = ttk.Frame(cal_win)
            btn_frame.pack(fill=tk.X, pady=(10, 15))
            
            # --- CORREÇÃO: Aplicar cores do tema aos botões de ação ---
            cancel_btn = tk.Button(btn_frame, text="Cancelar", 
                                 font=('Arial', 10),
                                 bg=self.colors['border'], 
                                 fg=self.colors['text'],
                                 activebackground=self.colors['card'],
                                 activeforeground=self.colors['text'], # Cor do texto ao passar o mouse
                                 relief='flat', bd=0, cursor='hand2',
                                 padx=15, pady=5)
            cancel_btn.pack(side=tk.RIGHT, padx=(5, 15))
            
            confirm_btn = tk.Button(btn_frame, text="Confirmar", 
                                  font=('Arial', 10, 'bold'),
                                  bg=self.colors['primary'], 
                                  fg=self.colors['card'],
                                  activebackground=self.colors['primary_hover'],
                                  activeforeground=self.colors['card'], # Cor do texto ao passar o mouse
                                  relief='flat', bd=0, cursor='hand2',
                                  padx=15, pady=5)
            confirm_btn.pack(side=tk.RIGHT, padx=(5, 5))
            
            cancel_btn.configure(command=cal_win.destroy)
            confirm_btn.configure(command=confirmar)
            
            # Configurar atalhos (ESC fecha, Enter confirma)
            _setup_dialog_shortcuts(cal_win, ok_button=confirm_btn, cancel_callback=cal_win.destroy)
            
            draw_calendar()

        # Botão de calendário com ícone maior
        cal_btn = tk.Button(top_frame, text="📅", font=("Segoe UI Emoji", 20), 
                           command=lambda: open_calendar(dialog),
                           bg=self.colors['card'], fg=self.colors['primary'],
                           activebackground=self.colors['primary_hover'] if getattr(self, 'dark_mode', False) else self.colors['card'],
                           relief='flat', bd=0, cursor='hand2', padx=8, pady=4)
        cal_btn.pack(side=tk.LEFT, padx=5)
        
        # ==============================================================================
        # SEÇÃO DE LISTA DE PRESENÇA
        # ==============================================================================
        
        # Container principal para lista (contém header + dados scrollable)
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # IMPORTANTE: Cabeçalho fica FORA do canvas scrollable para permanecer fixo no topo
        # Isso evita que o cabeçalho role junto com os dados
        header_frame = tk.Frame(list_container, bg=self.colors['primary'], relief='solid', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Colunas do cabeçalho
        tk.Label(header_frame, text="Matrícula", font=('Arial', 10, 'bold'), 
                bg=self.colors['primary'], fg=self.colors['card'], width=12).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Label(header_frame, text="Nome", font=('Arial', 10, 'bold'), 
                bg=self.colors['primary'], fg=self.colors['card'], width=30).pack(side=tk.LEFT, padx=5, pady=8)
        tk.Label(header_frame, text="Presença", font=('Arial', 10, 'bold'), 
                bg=self.colors['primary'], fg=self.colors['card'], width=15).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Frame que contém canvas + scrollbar (para os dados dos alunos)
        list_frame = ttk.Frame(list_container)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas com scrollbar dinâmica para suportar muitos alunos
        canvas_list = tk.Canvas(list_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar_list = ttk.Scrollbar(list_frame, orient="vertical", command=canvas_list.yview)
        scrollable_list = tk.Frame(canvas_list, bg=self.colors['card'])
        
        # Criar janela dentro do canvas para conter o frame scrollable
        canvas_window_list = canvas_list.create_window((0, 0), window=scrollable_list, anchor="nw")
        canvas_list.configure(yscrollcommand=scrollbar_list.set)
        
        def update_scroll_list(event=None):
            """
            Atualiza a scrollregion e controla a visibilidade da scrollbar
            
            IMPORTANTE: A scrollbar só aparece quando há mais conteúdo do que a área visível
            Isso previne o problema de scroll indevido quando há poucos dados
            """
            # Atualizar todas as geometrias pendentes
            canvas_list.update_idletasks()
            
            # Obter bounding box de todo o conteúdo
            bbox = canvas_list.bbox("all")
            if bbox:
                # Configurar região scrollable
                canvas_list.configure(scrollregion=bbox)
                
                # Calcular se o conteúdo é maior que a área visível
                content_height = bbox[3] - bbox[1]  # Altura total do conteúdo
                canvas_height = canvas_list.winfo_height()  # Altura visível do canvas
                
                # Mostrar/ocultar scrollbar baseado na necessidade real
                if content_height > canvas_height:
                    # Conteúdo maior que área visível: mostrar scrollbar
                    if not scrollbar_list.winfo_viewable():
                        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
                else:
                    # Conteúdo cabe na área visível: ocultar scrollbar
                    if scrollbar_list.winfo_viewable():
                        scrollbar_list.pack_forget()
                    # Garantir que canvas está no topo (sem deslocamento)
                    canvas_list.yview_moveto(0)
        
        def on_canvas_configure_list(event):
            """Ajusta largura do conteúdo e verifica necessidade de scrollbar"""
            # Ajustar largura do frame interno para preencher o canvas
            canvas_list.itemconfig(canvas_window_list, width=event.width)
            # Verificar se scrollbar é necessária após redimensionamento
            update_scroll_list()
        
        # Vincular eventos de mudança de tamanho
        scrollable_list.bind("<Configure>", update_scroll_list)  # Quando conteúdo muda
        canvas_list.bind("<Configure>", on_canvas_configure_list)  # Quando canvas redimensiona
        
        # Empacotar canvas (scrollbar será empacotada dinamicamente se necessário)
        canvas_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # NOTA: scrollbar NÃO é empacotada aqui - será feito dinamicamente pela função update_scroll_list

        # Buscar lista de alunos da turma do servidor
        resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{id_t}")
        
        # Dicionário para armazenar os comboboxes de presença (matricula -> StringVar)
        presenca_combos = {}

        def load_for_date(date_str):
            """
            Carrega e exibe presenças para uma data específica
            
            Args:
                date_str: Data no formato DD/MM/YYYY
            
            Comportamento:
                - Limpa dados anteriores (header fica intacto pois está fora do scrollable_list)
                - Carrega registros de presença salvos para a data
                - Exibe alunos com cores baseadas no status (verde/vermelho/neutro)
                - Atualiza scrollbar dinamicamente
            """
            # Limpar linhas anteriores (header está fora do scrollable_list, então não é afetado)
            for widget in scrollable_list.winfo_children():
                widget.destroy()
            
            # Limpar dicionário de comboboxes
            presenca_combos.clear()
            
            # Build a dict of presence status for the date
            presenca_dict = {}  # matricula -> True (presente), False (ausente), None (não registrado)
            try:
                records = read_presencas_dat(id_t)
                for r in records:
                    if r.get('date') == date_str:
                        presenca_dict[int(r.get('matricula'))] = r.get('presente', False)
            except Exception:
                presenca_dict = {}

            if resp and "Nenhum aluno" not in resp:
                for i, linha in enumerate(resp.strip().split('\n')):
                    if linha:
                        partes = linha.split(', ')
                        matricula = partes[0].split(': ')[1]
                        nome = partes[1].split(': ')[1]
                        
                        # Determinar status de presença
                        mat_int = int(matricula)
                        if mat_int in presenca_dict:
                            if presenca_dict[mat_int]:
                                status_inicial = "Presente"
                                bg_color = '#e8f5e9' if not getattr(self, 'dark_mode', False) else '#1B4D3E'
                            else:
                                status_inicial = "Ausente"
                                bg_color = '#ffebee' if not getattr(self, 'dark_mode', False) else '#4D1B1B'
                        else:
                            status_inicial = "Não Registrado"
                            bg_color = self.colors['card']
                        
                        # Criar linha para o aluno
                        aluno_frame = tk.Frame(scrollable_list, bg=bg_color, relief='solid', bd=1)
                        aluno_frame.pack(fill=tk.X, pady=1)
                        
                        # Matrícula
                        tk.Label(aluno_frame, text=matricula, font=('Arial', 10), 
                                bg=bg_color, fg=self.colors['text'], width=12).pack(side=tk.LEFT, padx=5, pady=8)
                        
                        # Nome
                        tk.Label(aluno_frame, text=nome, font=('Arial', 10), 
                                bg=bg_color, fg=self.colors['text'], width=30, anchor='w').pack(side=tk.LEFT, padx=5, pady=8)
                        
                        # Menu suspenso de presença
                        presenca_var = tk.StringVar(value=status_inicial)
                        presenca_combo = ttk.Combobox(aluno_frame, textvariable=presenca_var,
                                                     values=["Presente", "Ausente", "Não Registrado"],
                                                     state="readonly", width=18, font=('Arial', 9))
                        presenca_combo.pack(side=tk.LEFT, padx=5, pady=5)
                        
                        # Guardar referência com matrícula
                        presenca_combos[matricula] = presenca_var
                        
                        # Mudar cor do frame quando mudar presença
                        def on_presenca_change(event, frame=aluno_frame, var=presenca_var):
                            status = var.get()
                            if status == "Presente":
                                new_bg = '#e8f5e9' if not getattr(self, 'dark_mode', False) else '#1B4D3E'
                            elif status == "Ausente":
                                new_bg = '#ffebee' if not getattr(self, 'dark_mode', False) else '#4D1B1B'
                            else:
                                new_bg = self.colors['card']
                            
                            frame.config(bg=new_bg)
                            for child in frame.winfo_children():
                                if isinstance(child, tk.Label):
                                    child.config(bg=new_bg)
                        
                        presenca_combo.bind('<<ComboboxSelected>>', on_presenca_change)
            
            # Atualizar scrollregion após carregar todos os dados
            # Usar a função que controla a visibilidade da scrollbar
            scrollable_list.update_idletasks()
            canvas_list.update_idletasks()
            update_scroll_list()

        # Carregar presenças da data atual ao abrir
        load_for_date(date_var.get())

        def salvar_presenca():
            """
            Salva os registros de presença para a data selecionada
            
            Comportamento:
                - Coleta status de presença de todos os alunos
                - Ignora alunos marcados como "Não Registrado"
                - Salva em arquivo .dat específico da turma
                - Recarrega dados para atualizar cores visuais
            """
            data = date_var.get()
            presencas = []
            
            # Iterar por todos os comboboxes de presença
            for matricula, presenca_var in presenca_combos.items():
                status = presenca_var.get()
                
                # Só salvar se houver um registro definido (Presente ou Ausente)
                if status != "Não Registrado":
                    presencas.append({
                        "matricula": matricula,
                        "presente": (status == "Presente")
                    })
            
            # Salvar registros no arquivo .dat da turma
            ok = save_presencas_dat(id_t, data, presencas)
            if ok:
                messagebox.showinfo("Sucesso", f"Presenças salvas para {data}!")
                load_for_date(data)  # Recarregar para atualizar cores dos frames
            else:
                messagebox.showerror("Erro", "Falha ao salvar presenças")

        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        save_btn = ttk.Button(button_frame, text="Salvar Presenças", command=salvar_presenca, style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(button_frame, text="Fechar", command=dialog.destroy, style='Dialog.TButton')
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar atalhos (ESC fecha)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
        
        # Habilitar scroll com mousewheel no canvas
        _enable_canvas_scroll(canvas_list, scrollable_list)

    def upload_atividade(self):
        id_t = self._ask_turma_dropdown(title="Upload de Atividade - Selecionar Turma")
        if not id_t: return
        
        # Verificação de acesso adicional (segurança extra)
        if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
            messagebox.showerror("Acesso Negado", 
                               f"Você não tem permissão para fazer upload de atividades desta turma (ID: {id_t}).\n"
                               f"Entre em contato com o administrador para solicitar acesso.")
            return
        
        f_path = filedialog.askopenfilename(title="Selecionar arquivo")
        if not f_path: return
        try:
            f_size=os.path.getsize(f_path); f_name=os.path.basename(f_path)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST,PORT)); s.sendall(f"UPLOAD_FILE|{id_t}|{f_name}|{f_size}".encode('utf-8'))
                if s.recv(1024)==b"OK_SEND_DATA":
                    with open(f_path,"rb") as f:
                        while (chunk := f.read(4096)): s.sendall(chunk)
                    fin_resp=s.recv(1024).decode('utf-8'); messagebox.showinfo("Upload",fin_resp)
        except Exception as e: messagebox.showerror("Erro Upload", f"Ocorreu um erro: {e}")

    def listar_atividades(self):
        # Para alunos, mostrar apenas atividades da sua turma
        if self.role == 'aluno':
            matricula = self.db.get_student_matricula(self.username)
            if not matricula:
                messagebox.showerror("Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
                return
            
            # Encontrar turma do aluno
            resp_list = self._send_request(f"LIST_TURMAS")
            if not resp_list or "Nenhuma turma" in resp_list:
                messagebox.showerror("Erro", "Nenhuma turma encontrada.")
                return
            
            id_t = None
            for linha in resp_list.strip().split('\n'):
                if linha:
                    partes = linha.split(', ')
                    tid = partes[0].split(': ')[1]
                    
                    alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                    if alunos_resp and "Nenhum aluno" not in alunos_resp:
                        for aluno_linha in alunos_resp.strip().split('\n'):
                            if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                                id_t = tid
                                break
                    if id_t:
                        break
            
            if not id_t:
                messagebox.showerror("Erro", "Sua turma não foi encontrada.")
                return
        else:
            # Professor e Admin selecionam a turma
            id_t = self._ask_turma_dropdown(title="Listar Atividades - Selecionar Turma")
            if not id_t: return
            
            # Verificação de acesso adicional (segurança extra)
            if self.role == 'professor' and not self.db.can_access_subject(self.username, id_t):
                messagebox.showerror("Acesso Negado", 
                                   f"Você não tem permissão para visualizar atividades desta turma (ID: {id_t}).\n"
                                   f"Entre em contato com o administrador para solicitar acesso.")
                return
        
        # Primeiro, busca os dados da turma
        turma_resp = self._send_request(f"GET_TURMA_DATA|{id_t}")
        if not turma_resp or "ERRO" in turma_resp:
            messagebox.showerror("Erro", "Turma não encontrada")
            return
            
        disc, _ = turma_resp.split('|')
        
        resp = self._send_request(f"LIST_FILES|{id_t}")
        if resp is not None:
            if "Nenhuma atividade" in resp:
                self._update_display(
                    f"Atividades da Turma {id_t} - {disc}",
                    ["Nome do Arquivo", "Data de Envio", "Tamanho", "Ações"],
                    []
                )
            else:
                arquivos_data = []
                for arquivo in resp.strip().split('\n'):
                    if arquivo:
                        # Extrai timestamp do nome do arquivo (assumindo o formato timestamp_nome.ext)
                        try:
                            timestamp = int(arquivo.split('_')[0])
                            nome = '_'.join(arquivo.split('_')[1:])
                            data = time.strftime('%d/%m/%Y %H:%M', time.localtime(timestamp))
                            
                            # Busca informações do arquivo
                            arquivo_path = os.path.join('uploads', f'turma_{id_t}', arquivo)
                            if os.path.exists(arquivo_path):
                                tamanho = os.path.getsize(arquivo_path)
                                if tamanho < 1024:
                                    tamanho_str = f"{tamanho} B"
                                elif tamanho < 1024*1024:
                                    tamanho_str = f"{tamanho/1024:.1f} KB"
                                else:
                                    tamanho_str = f"{tamanho/(1024*1024):.1f} MB"
                            else:
                                tamanho_str = "N/A"
                            
                        except:
                            nome = arquivo
                            data = "N/A"
                            tamanho_str = "N/A"
                            
                        arquivos_data.append([nome, data, tamanho_str, "⬇️ Baixar"])
                
                self._update_display(
                    f"Atividades da Turma {id_t} - {disc}",
                    ["Nome do Arquivo", "Data de Envio", "Tamanho", "Ações"],
                    arquivos_data
                )
                
                # Configurar clique no botão de download
                if hasattr(self, 'display_tree'):
                    self.display_tree.bind('<Double-Button-1>', lambda e: self._download_arquivo(e, id_t))
                    
    def _download_arquivo(self, event, id_turma):
        item = self.display_tree.selection()
        if not item:
            return
            
        valores = self.display_tree.item(item[0])['values']
        if not valores:
            return
            
        nome_arquivo = valores[0]
        if not nome_arquivo:
            return
            
        # Busca o nome original do arquivo
        resp = self._send_request(f"LIST_FILES|{id_turma}")
        if not resp or "Nenhuma atividade" in resp:
            return
            
        arquivo_original = None
        for arquivo in resp.strip().split('\n'):
            if arquivo and nome_arquivo in arquivo:
                arquivo_original = arquivo
                break
                
        if not arquivo_original:
            messagebox.showerror("Erro", "Arquivo não encontrado no servidor")
            return
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(nome_arquivo)[1],
            initialfile=nome_arquivo,
            title="Salvar Como"
        )
        
        if save_path:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((HOST, PORT))
                    s.sendall(f"DOWNLOAD_FILE|{id_turma}|{arquivo_original}".encode('utf-8'))
                    response = s.recv(1024).decode('utf-8')
                    
                    if "ERRO" in response:
                        messagebox.showerror("Erro", response)
                        return
                    
                    if response.startswith("OK_DOWNLOAD"):
                        filesize = int(response.split("|")[1])
                        with open(save_path, "wb") as f:
                            bytes_received = 0
                            while bytes_received < filesize:
                                chunk = s.recv(min(4096, filesize - bytes_received))
                                if not chunk: break
                                f.write(chunk)
                                bytes_received += len(chunk)
                        messagebox.showinfo("Sucesso", "Arquivo baixado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao baixar arquivo: {e}")

    def aprovar_cadastros(self):
        """Interface para admin aprovar/rejeitar cadastros pendentes"""
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem aprovar cadastros.")
            return
        
        pending_users = self.db.get_pending_users()
        
        # DEBUG: Verificar o que está sendo retornado
        print(f"[DEBUG] Total de usuários no sistema: {len(self.db.users)}")
        print(f"[DEBUG] Usuários pendentes encontrados: {len(pending_users)}")
        for user in self.db.users.values():
            print(f"[DEBUG] Usuário: {user.get('role', 'N/A')}, Status: {user.get('status', 'N/A')}")
        
        if not pending_users:
            messagebox.showinfo("Informação", "Não há cadastros pendentes de aprovação.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Aprovar Cadastros Pendentes")
        
        # Configurar para ocupar altura inteira da tela
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        largura = 800
        altura = screen_height - 90  # Deixa margem para barra de tarefas
        x = (screen_width - largura) // 2
        y = 0
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        tk.Label(main_frame, text="⏳ Cadastros Pendentes de Aprovação", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Frame scrollável para lista de usuários
        canvas = tk.Canvas(main_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        # Criar a janela no canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def update_scroll_consolidado(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._manage_scrollbar_visibility(canvas, scrollbar, scrollable_frame)
        
        def on_canvas_configure(event):
            # Ajustar largura do scrollable_frame para preencher o canvas
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", update_scroll_consolidado)
        canvas.bind("<Configure>", on_canvas_configure)
        
        def refresh_list():
            # Limpar lista
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            pending = self.db.get_pending_users()
            
            # DEBUG: Verificar na atualização da lista
            print(f"[DEBUG refresh_list] Usuários pendentes: {len(pending)}")
            for p in pending:
                print(f"[DEBUG refresh_list] - {p['username']}: {p['role']}")
            
            if not pending:
                tk.Label(scrollable_frame, text="Nenhum cadastro pendente", 
                        bg=self.colors['card'], fg=self.colors['text']).pack(pady=20)
                return
            
            for user in pending:
                # Buscar dados completos do usuário para pegar matrícula
                user_data = self.db.get_user_data(user['username'])
                matricula = user_data.get('matricula') if user_data else None
                
                user_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
                user_frame.pack(fill=tk.X, pady=5, padx=5)
                
                info_frame = tk.Frame(user_frame, bg=self.colors['card'])
                info_frame.pack(fill=tk.X, padx=10, pady=10)
                
                tk.Label(info_frame, text=f"{user['username']}", 
                        font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                tk.Label(info_frame, text=f"{user['email']}", 
                        font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                tk.Label(info_frame, text=f"Tipo: {user['role'].title()}", 
                        font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                
                # Exibir turno
                turno = user_data.get('turno', 'Não definido')
                turno_icone = {'matutino': '', 'vespertino': '', 'noturno': ''}.get(turno, '🕐')
                tk.Label(info_frame, text=f"{turno_icone} Turno: {turno.title()}", 
                        font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                
                # Exibir matrícula se for aluno
                if user['role'] == 'aluno' and matricula:
                    tk.Label(info_frame, text=f"Matrícula: {matricula}", 
                            font=('Arial', 10, 'bold'), bg=self.colors['card'], 
                            fg=self.colors['primary']).pack(anchor='w', pady=(5, 0))
                
                # Calcular e exibir tempo desde o cadastro
                if user.get('created_at'):
                    try:
                        from datetime import datetime
                        created_dt = datetime.fromisoformat(user['created_at'])
                        now = datetime.now()
                        delta = now - created_dt
                        
                        if delta.days > 0:
                            tempo_texto = f"Há {delta.days} dia{'s' if delta.days > 1 else ''}"
                        elif delta.seconds >= 3600:
                            horas = delta.seconds // 3600
                            tempo_texto = f"Há {horas} hora{'s' if horas > 1 else ''}"
                        elif delta.seconds >= 60:
                            minutos = delta.seconds // 60
                            tempo_texto = f"Há {minutos} minuto{'s' if minutos > 1 else ''}"
                        else:
                            tempo_texto = "Agora mesmo"
                        
                        # Cor baseada na urgência
                        if delta.days >= 3:
                            tempo_cor = '#F44336'  # Vermelho - urgente
                        elif delta.days >= 1:
                            tempo_cor = '#FF9800'  # Laranja - atenção
                        else:
                            tempo_cor = self.colors['text_secondary']  # Cinza - recente
                        
                        tk.Label(info_frame, text=f"Aguardando: {tempo_texto}", 
                                font=('Arial', 9, 'italic'), bg=self.colors['card'], 
                                fg=tempo_cor).pack(anchor='w', pady=(3, 0))
                    except Exception:
                        pass
                
                # Botões de ação
                btn_frame = tk.Frame(user_frame, bg=self.colors['card'])
                btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
                
                def approve(u=user['username']):
                    success, msg = self.db.approve_user(u)
                    if success:
                        messagebox.showinfo("Sucesso", msg)
                        refresh_list()
                        self._refresh_pending_notification()  # Atualizar notificação na sidebar
                    else:
                        messagebox.showerror("Erro", msg)
                
                def reject(u=user['username']):
                    if messagebox.askyesno("Confirmar", f"Deseja realmente rejeitar o cadastro de '{u}'?"):
                        success, msg = self.db.reject_user(u)
                        if success:
                            messagebox.showinfo("Sucesso", msg)
                            refresh_list()
                            self._refresh_pending_notification()  # Atualizar notificação na sidebar
                        else:
                            messagebox.showerror("Erro", msg)
                
                ttk.Button(btn_frame, text="Aprovar", command=approve,
                          style='Success.TButton').pack(side=tk.LEFT, padx=(0, 10))
                ttk.Button(btn_frame, text="Rejeitar", command=reject,
                          style='Danger.TButton').pack(side=tk.LEFT)
                scrollable_frame.after(50, update_scroll_consolidado)
        
        refresh_list()
        
        # Configurar scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", pady=(0, 15))
        
        # Habilitar scroll com o mouse
        _enable_canvas_scroll(canvas, scrollable_frame)
        
        # Botão fechar na parte inferior
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        close_btn = ttk.Button(btn_frame, text="Fechar", command=dialog.destroy, style='Secondary.TButton')
        close_btn.pack(pady=10)
        
        # Configurar atalhos (ESC fecha, foco no botão fechar)
        _setup_dialog_shortcuts(dialog, ok_button=close_btn, cancel_callback=dialog.destroy)
    
    def gerenciar_usuarios(self):
        """Interface para admin editar/gerenciar todos os usuários"""
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem gerenciar usuários.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Gerenciar Usuários")
        dialog.transient(self)
        dialog.grab_set()
        
        # Configurar para tela cheia
        dialog.state('zoomed')  # Windows
        try:
            dialog.attributes('-zoomed', True)  # Linux/Unix
        except:
            pass
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal com scrollbar para evitar corte de botões
        main_container = tk.Frame(dialog, bg=self.colors['card'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas com scrollbar
        canvas = tk.Canvas(main_container, bg=self.colors['card'], highlightthickness=0)
        scrollbar_manage = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        main_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_manage.set)
        
        def update_scroll_manage():
            """Atualiza a scrollregion e controla a visibilidade da scrollbar"""
            canvas.update_idletasks()
            
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
                
                # Verificar se o conteúdo é maior que a área visível
                content_height = bbox[3] - bbox[1]
                canvas_height = canvas.winfo_height()
                
                # Mostrar/ocultar scrollbar baseado na necessidade
                if content_height > canvas_height:
                    if not scrollbar_manage.winfo_viewable():
                        scrollbar_manage.pack(side=tk.RIGHT, fill=tk.Y)
                else:
                    if scrollbar_manage.winfo_viewable():
                        scrollbar_manage.pack_forget()
                    # Garantir que está no topo quando não há scroll
                    canvas.yview_moveto(0)
        
        # Bind para ajustar largura do frame interno quando canvas redimensionar
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
            update_scroll_manage()
        
        main_frame.bind("<Configure>", lambda e: update_scroll_manage())
        canvas.bind('<Configure>', on_canvas_configure)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Não empacotar a scrollbar inicialmente, será feito dinamicamente
        
        # Habilitar scroll com mouse
        _enable_canvas_scroll(canvas, main_frame)
        
        # Título
        tk.Label(main_frame, text="Gerenciar Usuários", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 10))
        
        # Descrição
        tk.Label(main_frame, text="Aqui você pode editar informações, alterar níveis de acesso e excluir usuários.", 
                font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text_secondary']).pack(pady=(0, 15))
        
        # Seleção de usuário
        user_frame = tk.Frame(main_frame, bg=self.colors['card'])
        user_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(user_frame, text="Selecionar Usuário:", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        # Lista de todos os usuários (exceto o próprio admin)
        all_users = [u for u in self.db.users.keys() if u != self.username]
        
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(user_frame, textvariable=user_var, values=all_users, state="readonly", width=30)
        user_combo.pack(anchor='w', pady=(5, 0))
        if all_users:
            user_combo.set(all_users[0])
        
        # Frame de edição
        edit_frame = tk.Frame(main_frame, bg=self.colors['card'])
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Menu suspenso para selecionar campo a alterar
        field_select_frame = tk.Frame(edit_frame, bg=self.colors['card'])
        field_select_frame.pack(fill=tk.X, pady=(5, 15))
        
        tk.Label(field_select_frame, text="Campo a Alterar:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
        
        field_var = tk.StringVar()
        field_options = ['Email', 'Senha', 'Pergunta Secreta', 'Resposta Secreta', 'Matrícula']
        field_combo = ttk.Combobox(field_select_frame, textvariable=field_var, 
                                   values=field_options, state="readonly", width=30)
        field_combo.pack(anchor='w', pady=(5, 0))
        field_combo.set('Email')
        
        # Frame dinâmico para o campo selecionado
        dynamic_field_frame = tk.Frame(edit_frame, bg=self.colors['card'])
        dynamic_field_frame.pack(fill=tk.X, pady=(10, 10))
        
        # Variáveis para armazenar valores
        email_entry = None
        password_entry = None
        secret_question_entry = None
        secret_answer_entry = None
        matricula_entry = None
        
        def show_selected_field(event=None):
            nonlocal email_entry, password_entry, secret_question_entry, secret_answer_entry, matricula_entry
            
            # Limpar frame dinâmico
            for widget in dynamic_field_frame.winfo_children():
                widget.destroy()
            
            selected = field_var.get()
            
            if selected == 'Email':
                tk.Label(dynamic_field_frame, text="Novo Email:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
                email_entry = ttk.Entry(dynamic_field_frame, width=40)
                email_entry.pack(anchor='w', pady=(5, 0))
                # Carregar valor atual
                username = user_var.get()
                if username:
                    user_data = self.db.get_user_data(username)
                    if user_data and user_data.get('email'):
                        email_entry.delete(0, tk.END)
                        email_entry.insert(0, str(user_data.get('email', '')))
            
            elif selected == 'Senha':
                tk.Label(dynamic_field_frame, text="Nova Senha:", font=('Arial', 11, 'bold'), 
                        bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
                password_entry = ttk.Entry(dynamic_field_frame, width=40, show="*")
                password_entry.pack(anchor='w', pady=(5, 0))
            
            elif selected == 'Pergunta Secreta':
                tk.Label(dynamic_field_frame, text="Nova Pergunta Secreta:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
                secret_question_entry = ttk.Entry(dynamic_field_frame, width=40)
                secret_question_entry.pack(anchor='w', pady=(5, 0))
                # Carregar valor atual
                username = user_var.get()
                if username:
                    user_data = self.db.get_user_data(username)
                    if user_data and user_data.get('secret_question'):
                        secret_question_entry.delete(0, tk.END)
                        secret_question_entry.insert(0, str(user_data.get('secret_question', '')))
            
            elif selected == 'Resposta Secreta':
                tk.Label(dynamic_field_frame, text="Nova Resposta Secreta:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
                
                # Frame para resposta secreta com botão de visualizar
                answer_edit_frame = tk.Frame(dynamic_field_frame, bg=self.colors['card'])
                answer_edit_frame.pack(anchor='w', pady=(5, 0))
                
                secret_answer_entry = ttk.Entry(answer_edit_frame, width=37, show="*")
                secret_answer_entry.pack(side=tk.LEFT)
                
                # Botão para mostrar/ocultar resposta secreta
                show_answer_edit_var = tk.BooleanVar(value=False)
                
                def toggle_answer_edit_visibility():
                    if secret_answer_entry.get():
                        secret_answer_entry.config(show="" if show_answer_edit_var.get() else "*")
                
                try:
                    show_answer_edit_button = tk.Checkbutton(answer_edit_frame, image=self.eye_closed_photo, 
                                                          selectimage=self.eye_open_photo, 
                                                          variable=show_answer_edit_var, 
                                                          command=toggle_answer_edit_visibility, 
                                                          bg=self.colors['card'], 
                                                          activebackground=self.colors['card'],
                                                          selectcolor=self.colors['card'],
                                                          highlightthickness=0,
                                                          indicatoron=0, bd=0, relief="flat", cursor="hand2")
                    show_answer_edit_button.pack(side=tk.LEFT, padx=(5, 0))
                except:
                    # Fallback se as imagens não estiverem disponíveis
                    pass
                
                tk.Label(dynamic_field_frame, text="(A resposta atual não será exibida por segurança)", 
                        font=('Arial', 9, 'italic'), bg=self.colors['card'], 
                        fg=self.colors['text_secondary']).pack(anchor='w', pady=(3, 0))
            
            elif selected == 'Matrícula':
                tk.Label(dynamic_field_frame, text="Nova Matrícula (apenas para alunos):", font=('Arial', 11, 'bold'), 
                        bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
                matricula_entry = ttk.Entry(dynamic_field_frame, width=40)
                matricula_entry.pack(anchor='w', pady=(5, 0))
                # Carregar valor atual
                username = user_var.get()
                if username:
                    user_data = self.db.get_user_data(username)
                    if user_data and user_data.get('role') == 'aluno' and user_data.get('matricula'):
                        matricula_entry.delete(0, tk.END)
                        matricula_entry.insert(0, str(user_data.get('matricula', '')))
        
        field_combo.bind("<<ComboboxSelected>>", show_selected_field)
        
        # Nível de acesso com destaque
        access_frame = tk.Frame(edit_frame, bg=self.colors['card'], relief='solid', bd=1, highlightbackground=self.colors['primary'], highlightthickness=2)
        access_frame.pack(fill=tk.X, pady=(5, 10), padx=2)
        
        tk.Label(access_frame, text="Nível de Acesso (Role):", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(10, 5))
        
        tk.Label(access_frame, text="Altere o tipo de usuário para modificar suas permissões no sistema.", 
                font=('Arial', 9, 'italic'), bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', padx=10, pady=(0, 5))
        
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(access_frame, textvariable=role_var, 
                                  values=['aluno', 'professor', 'admin'], state="readonly", width=20, font=('Arial', 11))
        role_combo.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Label para mostrar permissões do role selecionado
        perm_label = tk.Label(access_frame, text="", font=('Arial', 9), 
                             bg=self.colors['card'], fg=self.colors['text'], 
                             wraplength=350, justify='left')
        perm_label.pack(anchor='w', padx=10, pady=(0, 10))
        
        # Label de aviso de alteração
        change_warning = tk.Label(access_frame, text="", font=('Arial', 9, 'bold'), 
                                 bg=self.colors['card'], fg='#FF9800', 
                                 wraplength=350, justify='left')
        change_warning.pack(anchor='w', padx=10, pady=(0, 10))
        
        def update_permissions_info(event=None):
            role = role_var.get()
            permissions = {
                'aluno': 'Ver suas notas e faltas, visualizar atividades da turma, gerenciar anotações',
                'professor': 'Lançar notas, controlar presença, upload de atividades (matérias atribuídas)',
                'admin': 'Acesso total ao sistema, gerenciar usuários e acessos'
            }
            perm_label.config(text=f"Permissões: {permissions.get(role, '')}")
            
            # Verificar se houve mudança
            username = user_var.get()
            if username:
                user_data = self.db.get_user_data(username)
                if user_data and user_data.get('role') != role:
                    change_warning.config(text="ATENÇÃO: Você alterou o nível de acesso! Clique em 'Salvar Alterações' para confirmar.")
                else:
                    change_warning.config(text="")
        
        role_combo.bind("<<ComboboxSelected>>", update_permissions_info)
        
        tk.Label(edit_frame, text="Status:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 0))
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(edit_frame, textvariable=status_var, 
                                    values=['approved', 'pending'], state="readonly", width=20)
        status_combo.pack(anchor='w', pady=(5, 10))
        
        def load_user_data(event=None):
            username = user_var.get()
            if not username:
                return
            
            user_data = self.db.get_user_data(username)
            if user_data:
                role_var.set(user_data.get('role', ''))
                status_var.set(user_data.get('status', 'approved'))
                update_permissions_info()
                # Recarregar campo atual
                show_selected_field()
        
        user_combo.bind("<<ComboboxSelected>>", load_user_data)
        
        # Inicializar com primeiro usuário
        show_selected_field()
        load_user_data()
        
        def save_changes():
            username = user_var.get()
            if not username:
                messagebox.showwarning("Aviso", "Selecione um usuário!")
                return
            
            # Verificar se está mudando o role
            user_data = self.db.get_user_data(username)
            old_role = user_data.get('role', '')
            new_role = role_var.get()
            
            if old_role != new_role:
                confirm_msg = (f"ATENÇÃO: Você está alterando o nível de acesso de '{username}'.\n\n"
                             f"De: {old_role.upper()} → Para: {new_role.upper()}\n\n"
                             f"Esta ação modificará as permissões do usuário no sistema.\n"
                             f"Deseja continuar?")
                if not messagebox.askyesno("Confirmar Alteração de Acesso", confirm_msg, icon='warning'):
                    return
            
            new_data = {
                'role': role_var.get(),
                'status': status_var.get()
            }
            
            # Obter campo selecionado e seu valor
            selected_field = field_var.get()
            
            if selected_field == 'Email' and email_entry:
                new_data['email'] = email_entry.get()
            elif selected_field == 'Senha' and password_entry:
                new_password = password_entry.get()
                if new_password:
                    success_pwd, msg_pwd = self.db.set_password(username, new_password)
                    if not success_pwd:
                        messagebox.showerror("Erro", f"Erro ao atualizar senha: {msg_pwd}")
                        return
            elif selected_field == 'Pergunta Secreta' and secret_question_entry:
                secret_question = secret_question_entry.get()
                if secret_question:
                    # Precisa da resposta também - vamos pedir
                    messagebox.showinfo("Aviso", "Para alterar a pergunta secreta, você também precisa definir uma nova resposta. Selecione 'Resposta Secreta' no menu.")
                    return
            elif selected_field == 'Resposta Secreta' and secret_answer_entry:
                secret_answer = secret_answer_entry.get()
                if secret_answer:
                    # Obter pergunta atual
                    secret_question = user_data.get('secret_question', '')
                    if secret_question:
                        success_secret, msg_secret = self.db.set_secret_question(username, secret_question, secret_answer)
                        if not success_secret:
                            messagebox.showerror("Erro", f"Erro ao atualizar resposta secreta: {msg_secret}")
                            return
                    else:
                        messagebox.showinfo("Aviso", "Usuário não possui pergunta secreta definida. Defina primeiro a pergunta.")
                        return
            elif selected_field == 'Matrícula' and matricula_entry:
                matricula = matricula_entry.get()
                if matricula:
                    if user_data.get('role') != 'aluno':
                        messagebox.showwarning("Aviso", "Apenas usuários com role 'aluno' podem ter matrícula!")
                        return
                    try:
                        new_data['matricula'] = int(matricula)
                    except ValueError:
                        messagebox.showerror("Erro", "Matrícula deve ser um número válido!")
                    return
            
            success, msg = self.db.update_user(username, new_data)
            if success:
                # Atualizar contador se status mudou para/de pending
                old_status = user_data.get('status', 'approved')
                new_status = status_var.get()
                if old_status != new_status:
                    self._refresh_pending_notification()
                else:
                    # Mesmo sem mudança de status, sempre atualizar (caso tenha mudado em outro lugar)
                    self._refresh_pending_notification()
                
                # Mensagem específica para mudança de role
                if old_role != new_role:
                    messagebox.showinfo("Nível de Acesso Alterado", 
                                      f"Nível de acesso de '{username}' alterado com sucesso!\n\n"
                                      f"{old_role.upper()} → {new_role.upper()}\n\n"
                                      f"As novas permissões serão aplicadas no próximo login do usuário.")
                else:
                    messagebox.showinfo("Sucesso", msg)
                load_user_data()  # Recarregar dados
                change_warning.config(text="")  # Limpar aviso
            else:
                messagebox.showerror("Erro", msg)
        
        def delete_user():
            username = user_var.get()
            if not username:
                messagebox.showwarning("Aviso", "Selecione um usuário!")
                return
            
            if messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário '{username}'?\nEsta ação não pode ser desfeita!"):
                if username in self.db.users:
                    del self.db.users[username]
                    self.db.save_users()
                    messagebox.showinfo("Sucesso", "Usuário excluído com sucesso")
                    # Atualizar lista
                    all_users = [u for u in self.db.users.keys() if u != self.username]
                    user_combo['values'] = all_users
                    if all_users:
                        user_combo.set(all_users[0])
                        load_user_data()
                    else:
                        dialog.destroy()
        
        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Frame interno para centralizar botões
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.pack(anchor='center')
        
        # Botão de salvar com destaque
        save_btn = ttk.Button(inner_button_frame, text="Salvar Alterações", command=save_changes,
                             style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(inner_button_frame, text="Atualizar", command=load_user_data, 
                  style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
        
        # Botão de excluir com destaque vermelho
        ttk.Button(inner_button_frame, text="Excluir Usuário", command=delete_user,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Botão Fechar
        close_btn = ttk.Button(inner_button_frame, text="Fechar", command=dialog.destroy, 
                              style='Secondary.TButton')
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Espaçamento extra no final para evitar corte dos botões
        tk.Label(main_frame, text="", bg=self.colors['card']).pack(pady=5)
        
        # Configurar atalhos (ESC fecha)
        _setup_dialog_shortcuts(dialog, cancel_callback=dialog.destroy)

    def associar_alunos_matriculas(self):
        """Interface para admin associar usuários alunos a matrículas"""
        if self.role != 'admin':
            messagebox.showerror("Acesso Negado", "Apenas administradores podem associar alunos.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Associar Alunos a Matrículas")
        dialog.geometry("900x700")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar janela
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f'600x400+{x}+{y}')
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, text="🎓 Associar Alunos a Matrículas", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 20))
        
        # Seleção de usuário aluno
        user_frame = tk.Frame(main_frame, bg=self.colors['card'])
        user_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(user_frame, text="Selecionar Usuário (Aluno):", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        # Lista de usuários alunos
        alunos_users = [u for u, d in self.db.users.items() if d['role'] == 'aluno']
        
        if not alunos_users:
            tk.Label(main_frame, text="Nenhum usuário com role 'aluno' encontrado.", 
                    bg=self.colors['card'], fg=self.colors['text']).pack()
            ttk.Button(main_frame, text="Fechar", command=dialog.destroy, style='Secondary.TButton').pack(pady=10)
            return
        
        user_var = tk.StringVar()
        user_combo = ttk.Combobox(user_frame, textvariable=user_var, values=alunos_users, state="readonly", width=30)
        user_combo.pack(anchor='w', pady=(5, 0))
        if alunos_users:
            user_combo.set(alunos_users[0])
        
        # Campo de matrícula
        mat_frame = tk.Frame(main_frame, bg=self.colors['card'])
        mat_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(mat_frame, text="Matrícula:", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        mat_entry = ttk.Entry(mat_frame, width=30)
        mat_entry.pack(anchor='w', pady=(5, 0))
        
        # Mostrar matrícula atual quando usuário muda
        def update_current_matricula(event=None):
            username = user_var.get()
            if username:
                current_mat = self.db.get_student_matricula(username)
                mat_entry.delete(0, tk.END)
                if current_mat:
                    mat_entry.insert(0, str(current_mat))
        
        user_combo.bind("<<ComboboxSelected>>", update_current_matricula)
        update_current_matricula()
        
        def save_association():
            username = user_var.get()
            matricula = mat_entry.get()
            
            if not username or not matricula:
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            try:
                matricula = int(matricula)
            except ValueError:
                messagebox.showerror("Erro", "Matrícula deve ser um número!")
                return
            
            success, msg = self.db.set_student_matricula(username, matricula)
            if success:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Salvar Associação", command=save_association, style='Dialog.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Fechar", command=dialog.destroy, style='Secondary.TButton').pack(side=tk.RIGHT)
    
    def ver_minhas_notas(self):
        """
        Permite que aluno visualize suas próprias notas em tempo real
        
        Características:
            - Busca dados atualizados do servidor a cada consulta
            - Botão "Atualizar" para recarregar dados sem fechar a janela
            - Exibe NP1, NP2, PIM, Média, Exame e Status
            - Cores visuais baseadas no status (aprovado/reprovado/pendente)
        """
        if self.role != 'aluno':
            show_error(self, "Acesso Negado", "Esta função é exclusiva para alunos.")
            return
        
        # Obter matrícula do aluno logado
        matricula = self.db.get_student_matricula(self.username)
        if not matricula:
            show_error(self, "Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
            return
        
        # Criar janela
        notas_window = tk.Toplevel(self)
        notas_window.title("Minhas Notas")
        notas_window.geometry("550x450")
        notas_window.transient(self)
        notas_window.grab_set()
        _center_window(notas_window)
        
        # Aplicar tema
        try:
            _apply_popup_theme(notas_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(notas_window)
        
        # Frame principal com container para conteúdo dinâmico
        main_frame = tk.Frame(notas_window, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título fixo
        tk.Label(main_frame, text="Minhas Notas", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Container para conteúdo que será atualizado
        content_frame = tk.Frame(main_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        def carregar_notas():
            """Busca notas atualizadas do servidor e atualiza a exibição"""
            # Limpar conteúdo anterior
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            # Buscar aluno completo para obter turma e notas do servidor
            resp_list = self._send_request(f"LIST_TURMAS")
            if not resp_list or "Nenhuma turma" in resp_list:
                show_error(notas_window, "Erro", "Nenhuma turma encontrada.")
                return
            
            # Procurar aluno em todas as turmas
            aluno_info = None
            id_turma = None
            for linha in resp_list.strip().split('\n'):
                if linha:
                    partes = linha.split(', ')
                    tid = partes[0].split(': ')[1]
                    
                    alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                    if alunos_resp and "Nenhum aluno" not in alunos_resp:
                        for aluno_linha in alunos_resp.strip().split('\n'):
                            if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                                id_turma = tid
                                aluno_info = aluno_linha
                                break
                    if aluno_info:
                        break
            
            if not aluno_info:
                show_error(notas_window, "Erro", "Suas informações não foram encontradas.")
                return
            
            # Extrair notas do servidor (TODAS as notas vêm do servidor C)
            partes = aluno_info.split(', ')
            nome = partes[1].split(': ')[1]
            np1 = np2 = pim = media = exame = "0.0"
            for p in partes[2:]:
                if p.startswith('NP1:'): np1 = p.split(': ')[1]
                elif p.startswith('NP2:'): np2 = p.split(': ')[1]
                elif p.startswith('PIM:'): pim = p.split(': ')[1]
                elif p.startswith('Média:'): media = p.split(': ')[1]
                elif p.startswith('Exame:'): exame = p.split(': ')[1]
            
            # Buscar informações da turma
            turma_resp = self._send_request(f"GET_TURMA_DATA|{id_turma}")
            disciplina = "N/A"
            if turma_resp and "ERRO" not in turma_resp:
                disciplina, _ = turma_resp.split('|')
            
            # Exibir informações básicas
            tk.Label(content_frame, text=f"Nome: {nome}", 
                    font=('Arial', 12), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            tk.Label(content_frame, text=f"Matrícula: {matricula}", 
                    font=('Arial', 12), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            tk.Label(content_frame, text=f"Turma: ID {id_turma} - {disciplina}", 
                    font=('Arial', 12), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 15))
            
            # Notas
            notas_display = tk.Frame(content_frame, bg=self.colors['card'], relief='solid', bd=1)
            notas_display.pack(fill=tk.X, pady=10)
            
            tk.Label(notas_display, text=f"NP1: {np1}", font=('Arial', 14, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=15, pady=10)
            tk.Label(notas_display, text=f"NP2: {np2}", font=('Arial', 14, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=15, pady=10)
            tk.Label(notas_display, text=f"PIM: {pim}", font=('Arial', 14, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=15, pady=10)
            
            # Exame
            exame_display = tk.Frame(content_frame, bg=self.colors['card'], relief='solid', bd=1)
            exame_display.pack(fill=tk.X, pady=10)
            
            # Converter exame para float para cálculo de status
            exame_val = float(exame)
            
            tk.Label(exame_display, text=f"Exame: {exame_val:.1f}", font=('Arial', 14, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=15, pady=10)
            
            # Calcular status (converter todas as notas para float)
            media_val = float(media)
            np1_val = float(np1)
            np2_val = float(np2)
            pim_val = float(pim)
            
            # Verificar se há notas atribuídas
            tem_notas = (np1_val > 0 or np2_val > 0 or pim_val > 0)
            
            # Determinar status
            if not tem_notas:
                status = "Pendente Atribuir Notas"
                status_color = '#ffc107'
            elif media_val >= 7.0:
                status = "Aprovado"
                status_color = '#28a745'
            elif media_val < 7.0 and exame_val == 0.0:
                status = "Pendente Exame"
                status_color = '#ffc107'
            elif media_val < 7.0 and exame_val >= 5.0:
                status = "Aprovado (Exame)"
                status_color = '#28a745'
            elif media_val < 7.0 and 0.0 < exame_val < 5.0:
                status = "Reprovado"
                status_color = '#dc3545'
            else:
                status = "Pendente"
                status_color = '#ffc107'
            
            tk.Label(content_frame, text=f"Média Final: {media}", font=('Arial', 16, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(pady=(10, 5))
            tk.Label(content_frame, text=f"Status: {status}", font=('Arial', 14, 'bold'), 
                    bg=self.colors['card'], fg=status_color).pack()
        
        # Carregar dados iniciais
        carregar_notas()
        
        # Botões de ação
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Atualizar", command=carregar_notas, style='Dialog.TButton')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(btn_frame, text="Fechar", command=notas_window.destroy, style='Secondary.TButton')
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos
        _setup_dialog_shortcuts(notas_window, ok_button=refresh_btn, cancel_callback=notas_window.destroy)
    
    def ver_minhas_faltas(self):
        """
        Permite que aluno visualize suas presenças/faltas em tempo real
        
        Características:
            - Busca dados atualizados do servidor
            - Botão "Atualizar" para recarregar sem fechar
            - Exibe lista de presenças por data
            - Cores visuais (verde=presente, vermelho=ausente)
        """
        if self.role != 'aluno':
            show_error(self, "Acesso Negado", "Esta função é exclusiva para alunos.")
            return
        
        matricula = self.db.get_student_matricula(self.username)
        if not matricula:
            show_error(self, "Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
            return
        
        # Procurar aluno em todas as turmas para encontrar sua turma
        resp_list = self._send_request(f"LIST_TURMAS")
        if not resp_list or "Nenhuma turma" in resp_list:
            show_error(self, "Erro", "Nenhuma turma encontrada.")
            return
        
        id_turma = None
        for linha in resp_list.strip().split('\n'):
            if linha:
                partes = linha.split(', ')
                tid = partes[0].split(': ')[1]
                
                alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                if alunos_resp and "Nenhum aluno" not in alunos_resp:
                    for aluno_linha in alunos_resp.strip().split('\n'):
                        if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                            id_turma = tid
                            break
                if id_turma:
                    break
        
        if not id_turma:
            show_error(self, "Erro", "Turma não encontrada.")
            return
        
        # Contar faltas
        faltas = 0
        try:
            for rec in read_presencas_dat(id_turma):
                if rec.get('matricula') == int(matricula) and not rec.get('presente'):
                    faltas += 1
        except Exception:
            pass
        
        # Mostrar resultado com tema aplicado
        show_info(self, "Minhas Faltas", 
                 f"Você possui {faltas} falta(s) registrada(s).\n\n"
                 f"Matrícula: {matricula}\n"
                 f"Turma: ID {id_turma}")
    
    def ver_presencas_por_data(self):
        """
        Permite que aluno visualize suas presenças por data em tempo real
        
        Características:
            - Busca dados atualizados do servidor
            - Botão "Atualizar" para recarregar lista
            - Exibe presenças em formato de tabela por data
            - Cores visuais (verde=presente, vermelho=ausente)
        """
        if self.role != 'aluno':
            show_error(self, "Acesso Negado", "Esta função é exclusiva para alunos.")
            return
        
        matricula = self.db.get_student_matricula(self.username)
        if not matricula:
            show_error(self, "Erro", "Você não possui uma matrícula associada. Entre em contato com o administrador.")
            return
        
        # Encontrar turma do aluno
        resp_list = self._send_request(f"LIST_TURMAS")
        if not resp_list or "Nenhuma turma" in resp_list:
            show_error(self, "Erro", "Nenhuma turma encontrada.")
            return
        
        id_turma = None
        for linha in resp_list.strip().split('\n'):
            if linha:
                partes = linha.split(', ')
                tid = partes[0].split(': ')[1]
                
                alunos_resp = self._send_request(f"LIST_ALUNOS_POR_TURMA|{tid}")
                if alunos_resp and "Nenhum aluno" not in alunos_resp:
                    for aluno_linha in alunos_resp.strip().split('\n'):
                        if aluno_linha and f"Matrícula: {matricula}" in aluno_linha:
                            id_turma = tid
                            break
                if id_turma:
                    break
        
        if not id_turma:
            show_error(self, "Erro", "Turma não encontrada.")
            return
        
        # Criar janela de visualização
        pres_window = tk.Toplevel(self)
        pres_window.title("Minhas Presenças")
        pres_window.geometry("600x500")
        pres_window.transient(self)
        pres_window.grab_set()
        _center_window(pres_window)
        
        # Aplicar tema
        try:
            _apply_popup_theme(pres_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(pres_window)
        
        # Frame principal
        main_frame = tk.Frame(pres_window, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Minhas Presenças", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Lista de presenças
        tree_frame = tk.Frame(main_frame, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Data", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")
        tree.heading("Data", text="Data")
        tree.heading("Status", text="Status")
        tree.column("Data", width=150)
        tree.column("Status", width=150)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar tags de cores
        if getattr(self, 'dark_mode', False):
            tree.tag_configure('presente', background='#1B4D3E', foreground='#B8F4D6')
            tree.tag_configure('ausente', background='#4D1B1B', foreground='#FFB3B3')
        else:
            tree.tag_configure('presente', background='#e8f5e9', foreground='#1B5E20')
            tree.tag_configure('ausente', background='#ffebee', foreground='#C62828')
        
        tree.tag_configure('odd', background=self.colors.get('row_odd'), foreground=self.colors.get('text'))
        tree.tag_configure('even', background=self.colors.get('row_even'), foreground=self.colors.get('text'))
        
        def carregar_presencas():
            """Carrega presenças atualizadas do servidor"""
            # Limpar tree
            tree.delete(*tree.get_children())
            
            try:
                presencas = read_presencas_dat(id_turma)
                minhas_presencas = [p for p in presencas if p.get('matricula') == int(matricula)]
                
                # Ordenar por data
                minhas_presencas.sort(key=lambda x: x.get('date', ''))
                
                for i, pres in enumerate(minhas_presencas):
                    status = "Presente" if pres.get('presente') else "Ausente"
                    tag = 'presente' if status == "Presente" else 'ausente'
                    parity = 'even' if i % 2 == 0 else 'odd'
                    tree.insert("", tk.END, values=(pres.get('date'), status), tags=(parity, tag))
            except Exception as e:
                show_error(pres_window, "Erro", f"Erro ao carregar presenças: {e}")
        
        # Carregar dados iniciais
        carregar_presencas()
        
        # Botões de ação
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Atualizar", command=carregar_presencas, style='Dialog.TButton')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = ttk.Button(btn_frame, text="Fechar", command=pres_window.destroy, style='Secondary.TButton')
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos
        _setup_dialog_shortcuts(pres_window, ok_button=refresh_btn, cancel_callback=pres_window.destroy)
    
    def ver_editar_perfil(self):
        """Interface completa de perfil do usuário com foto e campos adicionais"""
        user_data = self.db.get_user_data(self.username)
        
        dialog = tk.Toplevel(self)
        dialog.title("Meu Perfil")
        
        # Configurar para ocupar altura inteira da tela
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        largura = 600
        altura = screen_height - 90  # Deixa margem para barra de tarefas
        x = (screen_width - largura) // 2
        y = 0
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal com scroll
        main_container = tk.Frame(dialog, bg=self.colors['card'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_container, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        main_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        main_frame.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Conteúdo
        content_frame = tk.Frame(main_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Cabeçalho
        tk.Label(content_frame, text="Meu Perfil", 
                font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Frame para foto de perfil
        foto_frame = tk.Frame(content_frame, bg=self.colors['card'])
        foto_frame.pack(pady=(0, 25))
        
        # Foto de perfil (circular)
        foto_path = user_data.get('foto_perfil')
        foto_label = tk.Label(foto_frame, bg=self.colors['card'])
        
        try:
            if foto_path and os.path.exists(foto_path):
                from PIL import Image, ImageTk, ImageDraw
                img = Image.open(foto_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                
                # Criar máscara circular
                mask = Image.new('L', (80, 80), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 80, 80), fill=255)
                
                # Aplicar máscara
                output = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                photo = ImageTk.PhotoImage(output)
                foto_label.config(image=photo, bg=self.colors['card'], width=120, height=120)
                foto_label.image = photo
            else:
                # Placeholder se não tiver foto
                foto_label.config(text="👤", font=('Arial', 30), 
                                bg=self.colors['border'], fg=self.colors['text_secondary'],
                                width=10, height=5)
        except Exception as e:
            foto_label.config(text="👤", font=('Arial', 30), 
                            bg=self.colors['border'], fg=self.colors['text_secondary'],
                            width=10, height=5)
        
        foto_label.pack()
        
        # Botão para alterar foto
        def alterar_foto():
            arquivo = filedialog.askopenfilename(
                title="Selecionar Foto de Perfil",
                filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos os arquivos", "*.*")]
            )
            if arquivo:
                # Copiar para pasta de perfil
                os.makedirs('uploads/perfil', exist_ok=True)
                extensao = os.path.splitext(arquivo)[1]
                destino = f'uploads/perfil/{self.username}{extensao}'
                
                try:
                    import shutil
                    shutil.copy2(arquivo, destino)
                    
                    # Atualizar no banco
                    self.db.update_user(self.username, {'foto_perfil': destino})
                    
                    # Recarregar imagem
                    from PIL import Image, ImageTk, ImageDraw
                    img = Image.open(destino)
                    img = img.resize((120, 120), Image.Resampling.LANCZOS)
                    
                    mask = Image.new('L', (120, 120), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, 120, 120), fill=255)
                    
                    output = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
                    output.paste(img, (0, 0))
                    output.putalpha(mask)
                    
                    photo = ImageTk.PhotoImage(output)
                    foto_label.config(image=photo, bg=self.colors['card'], text='', width=120, height=120)
                    foto_label.image = photo
                    
                    messagebox.showinfo("Sucesso", "Foto de perfil atualizada!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar foto: {e}")
        
        ttk.Button(foto_frame, text="Alterar Foto", command=alterar_foto, 
                  style='Secondary.TButton').pack(pady=(10, 0))
        
        # Informações básicas (read-only)
        info_frame = tk.LabelFrame(content_frame, text="Informações da Conta", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Arial', 11, 'bold'), padx=15, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Username
        tk.Label(info_frame, text="Usuário:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(info_frame, text=self.username, font=('Arial', 11), 
                bg=self.colors['border'], fg=self.colors['text'], 
                relief='solid', bd=1, padx=8, pady=5).pack(fill=tk.X, pady=(3, 10))
        
        # Role
        role_display = {'aluno': 'Aluno', 'professor': 'Professor', 'admin': 'Administrador'}.get(self.role, self.role)
        tk.Label(info_frame, text="Tipo:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(info_frame, text=role_display, font=('Arial', 11), 
                bg=self.colors['border'], fg=self.colors['text'], 
                relief='solid', bd=1, padx=8, pady=5).pack(fill=tk.X, pady=(3, 10))
        
        # Turno
        turno = user_data.get('turno', 'matutino')
        turno_icone = {'matutino': '', 'vespertino': '', 'noturno': ''}.get(turno, '🕐')
        tk.Label(info_frame, text="Turno:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(info_frame, text=f"{turno_icone} {turno.title()}", font=('Arial', 11), 
                bg=self.colors['border'], fg=self.colors['text'], 
                relief='solid', bd=1, padx=8, pady=5).pack(fill=tk.X, pady=(3, 10))
        
        # Matrícula (se aluno)
        if self.role == 'aluno':
            matricula = user_data.get('matricula', 'Não atribuída')
            tk.Label(info_frame, text="Matrícula:", font=('Arial', 10, 'bold'), 
                    bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            tk.Label(info_frame, text=str(matricula), font=('Arial', 11), 
                    bg=self.colors['border'], fg=self.colors['text'], 
                    relief='solid', bd=1, padx=8, pady=5).pack(fill=tk.X, pady=(3, 10))
        
        # Campos editáveis
        edit_frame = tk.LabelFrame(content_frame, text="Informações Pessoais", 
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   font=('Arial', 11, 'bold'), padx=15, pady=10)
        edit_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Email
        tk.Label(edit_frame, text="Email:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        email_entry = ttk.Entry(edit_frame, font=('Arial', 10))
        email_entry.insert(0, user_data.get('email', '') or '')
        email_entry.pack(fill=tk.X, pady=(3, 12))
        
        # Telefone
        tk.Label(edit_frame, text="Telefone:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        telefone_entry = ttk.Entry(edit_frame, font=('Arial', 10))
        telefone_entry.insert(0, user_data.get('telefone', '') or '')
        telefone_entry.pack(fill=tk.X, pady=(3, 12))
        
        # Data de Nascimento
        tk.Label(edit_frame, text="Data de Nascimento (DD/MM/AAAA):", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        nascimento_entry = ttk.Entry(edit_frame, font=('Arial', 10))
        nascimento_entry.insert(0, user_data.get('data_nascimento', '') or '')
        nascimento_entry.pack(fill=tk.X, pady=(3, 12))
        
        # CPF
        tk.Label(edit_frame, text="CPF:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        cpf_entry = ttk.Entry(edit_frame, font=('Arial', 10))
        cpf_entry.insert(0, user_data.get('cpf', '') or '')
        cpf_entry.pack(fill=tk.X, pady=(3, 12))
        
        # Endereço
        tk.Label(edit_frame, text="Endereço:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        endereco_entry = ttk.Entry(edit_frame, font=('Arial', 10))
        endereco_entry.insert(0, user_data.get('endereco', '') or '')
        endereco_entry.pack(fill=tk.X, pady=(3, 12))
        
        # Bio/Sobre
        tk.Label(edit_frame, text="Sobre mim:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        bio_text = tk.Text(edit_frame, width=45, height=4, font=('Arial', 10),
                          bg=self.colors['input_bg'], fg=self.colors['text'],
                          relief='solid', bd=1)
        bio_text.insert('1.0', user_data.get('bio', ''))
        bio_text.pack(fill=tk.X, pady=(3, 0))
        
        def salvar_perfil():
            """Salva todas as informações do perfil"""
            new_data = {
                'email': email_entry.get(),
                'telefone': telefone_entry.get(),
                'data_nascimento': nascimento_entry.get(),
                'cpf': cpf_entry.get(),
                'endereco': endereco_entry.get(),
                'bio': bio_text.get('1.0', 'end-1c')
            }
            
            # Validar email
            if new_data['email'] and not self.db.validate_email(new_data['email']):
                messagebox.showerror("Erro", "Email inválido!")
                return
            
            # Validar data de nascimento (formato básico)
            if new_data['data_nascimento']:
                if not re.match(r'^\d{2}/\d{2}/\d{4}$', new_data['data_nascimento']):
                    messagebox.showerror("Erro", "Data de nascimento inválida! Use o formato DD/MM/AAAA")
                    return
            
            # Validar CPF (formato básico)
            if new_data['cpf']:
                cpf_numeros = re.sub(r'[^0-9]', '', new_data['cpf'])
                if len(cpf_numeros) != 11:
                    messagebox.showerror("Erro", "CPF inválido! Deve conter 11 dígitos")
                    return
            
            success, msg = self.db.update_user(self.username, new_data)
            if success:
                messagebox.showinfo("Sucesso", "Perfil atualizado com sucesso!")
                dialog.destroy()
            else:
                messagebox.showerror("Erro", msg)
        
        # Botões
        btn_frame = tk.Frame(content_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_btn = ttk.Button(btn_frame, text="Salvar Perfil", command=salvar_perfil, 
                  style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        close_btn = ttk.Button(btn_frame, text="Fechar", command=dialog.destroy, 
                  style='Secondary.TButton')
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos (ESC fecha, Enter salva)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
        
        # Habilitar scroll com mousewheel
        _enable_canvas_scroll(canvas, main_frame)
    
    def editar_meu_email(self):
        """Interface para todos os usuários editarem seu próprio email"""
        user_data = self.db.get_user_data(self.username)
        
        dialog = tk.Toplevel(self)
        dialog.title("Editar Meu Email")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Editar Email", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Frame para email atual
        current_email_frame = tk.Frame(main_frame, bg=self.colors['card'])
        current_email_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(current_email_frame, text="Email atual:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 5))
        
        # Exibir email atual (garantir que seja string)
        display_email = user_data.get('email') or 'Não cadastrado'
        current_email_display = tk.Label(current_email_frame, 
                text=str(display_email), 
                font=('Arial', 11), 
                bg=self.colors['input_bg'], 
                fg=self.colors['text'],
                relief='solid', bd=1, padx=10, pady=8, anchor='w')
        current_email_display.pack(fill=tk.X)
        
        # Frame para novo email
        new_email_frame = tk.Frame(main_frame, bg=self.colors['card'])
        new_email_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(new_email_frame, text="Novo Email:", font=('Arial', 10, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 5))
        
        email_entry = ttk.Entry(new_email_frame, width=40, font=('Arial', 10))
        # Garantir que sempre insira uma string (não None)
        current_email = user_data.get('email') or ''
        if current_email:
            email_entry.insert(0, str(current_email))
        email_entry.pack(fill=tk.X)
        
        def salvar():
            novo_email = email_entry.get().strip()
            if not novo_email:
                show_error(dialog, "Erro", "Email não pode estar vazio!")
                return
            
            if not self.db.validate_email(novo_email):
                show_error(dialog, "Erro", "Email inválido!")
                return
            
            success, msg = self.db.update_user(self.username, {'email': novo_email})
            if success:
                show_info(dialog, "Sucesso", "Email atualizado com sucesso!")
                dialog.destroy()
            else:
                show_error(dialog, "Erro", msg)
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="Salvar", command=salvar, 
                  style='Dialog.TButton')
        save_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn = ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                  style='Secondary.TButton')
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Configurar atalhos (ESC cancela, Enter salva)
        _setup_dialog_shortcuts(dialog, ok_button=save_btn, cancel_callback=dialog.destroy)
        
        # Focar no campo de entrada
        email_entry.focus_set()
    
    def alterar_minha_senha(self):
        """Interface para todos os usuários alterarem sua própria senha"""
        dialog = tk.Toplevel(self)
        dialog.title("Alterar Minha Senha")
        dialog.geometry("450x350")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Alterar Senha", 
                font=('Arial', 14, 'bold'), bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 20))
        
        # Senha atual
        tk.Label(main_frame, text="Senha Atual:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        senha_atual_entry = ttk.Entry(main_frame, width=40, show="*")
        senha_atual_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Nova senha
        tk.Label(main_frame, text="Nova Senha:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        senha_nova_entry = ttk.Entry(main_frame, width=40, show="*")
        senha_nova_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Confirmar nova senha
        tk.Label(main_frame, text="Confirmar Nova Senha:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        senha_confirm_entry = ttk.Entry(main_frame, width=40, show="*")
        senha_confirm_entry.pack(fill=tk.X, pady=(5, 20))
        
        def salvar():
            senha_atual = senha_atual_entry.get()
            senha_nova = senha_nova_entry.get()
            senha_confirm = senha_confirm_entry.get()
            
            if not senha_atual or not senha_nova or not senha_confirm:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
                return
            
            # Verificar senha atual
            if not self.db.verify_password(self.username, senha_atual):
                messagebox.showerror("Erro", "Senha atual incorreta!")
                return
            
            # Verificar se as novas senhas coincidem
            if senha_nova != senha_confirm:
                messagebox.showerror("Erro", "As novas senhas não coincidem!")
                return
            
            # Validar nova senha
            is_valid, msg = self.db.validate_password(senha_nova)
            if not is_valid:
                messagebox.showerror("Erro", msg)
                return
            
            # Salvar nova senha
            success, msg = self.db.set_password(self.username, senha_nova)
            if success:
                messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
                dialog.destroy()
            else:
                messagebox.showerror("Erro", msg)
        
        btn_frame = tk.Frame(main_frame, bg=self.colors['card'])
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="Salvar", command=salvar, 
                  style='Dialog.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy, 
                  style='Secondary.TButton').pack(side=tk.RIGHT, padx=5)

    def gerenciar_acessos_professores(self):
        """Interface para administradores gerenciarem acessos de professores"""
        if self.role != 'admin':
            messagebox.showerror("Erro", "Acesso negado. Apenas administradores podem gerenciar acessos.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Gerenciar Acessos de Professores")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        _center_window(dialog)
        
        # Aplicar tema
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.colors['card'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, text="👥 Gerenciar Acessos de Professores", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 20))
        
        # Frame para seleção de professor
        prof_frame = tk.Frame(main_frame, bg=self.colors['card'])
        prof_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(prof_frame, text="Selecionar Professor:", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        prof_var = tk.StringVar()
        prof_combo = ttk.Combobox(prof_frame, textvariable=prof_var, state="readonly", width=30)
        prof_combo.pack(anchor='w', pady=(5, 0))
        
        # Frame para matérias
        subjects_frame = tk.Frame(main_frame, bg=self.colors['card'])
        subjects_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        tk.Label(subjects_frame, text="Matérias Disponíveis:", 
                font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        # Lista de matérias com checkboxes
        subjects_listbox = tk.Frame(subjects_frame, bg=self.colors['card'])
        subjects_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Scrollbar para a lista
        canvas = tk.Canvas(subjects_listbox, bg=self.colors['card'], highlightthickness=0)
        # <-- MUDANÇA 1: Aplicar o estilo moderno na criação da scrollbar
        scrollbar = ttk.Scrollbar(subjects_listbox, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        # Criar a janela no canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def update_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._manage_scrollbar_visibility(canvas, scrollbar, scrollable_frame)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable_frame.bind("<Configure>", update_scroll)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Variáveis para checkboxes
        subject_vars = {}
        
        def load_professors():
            """Carrega lista de professores"""
            professors = self.db.get_all_professors()
            prof_names = [p['username'] for p in professors]
            prof_combo['values'] = prof_names
            if prof_names:
                prof_combo.set(prof_names[0])
                load_professor_subjects()
        
        def load_turmas():
            """Carrega lista de turmas/matérias"""
            try:
                turmas = self._get_turmas_list()
                return turmas
            except Exception:
                return []
        
        def load_professor_subjects():
            """Carrega matérias do professor selecionado"""
            # Limpar checkboxes existentes
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            subject_vars.clear()
            
            professor = prof_var.get()
            if not professor:
                return
            
            # Obter matérias do professor
            professor_subjects = self.db.get_professor_subjects(professor)
            
            # Obter todas as turmas
            turmas = load_turmas()
            
            if not turmas:
                tk.Label(scrollable_frame, text="Nenhuma turma encontrada", 
                        bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                return
            
            # Criar checkboxes para cada turma
            for t in turmas:
                var = tk.BooleanVar()
                var.set(t['id'] in professor_subjects)
                subject_vars[t['id']] = var
                
                checkbox = tk.Checkbutton(scrollable_frame, 
                                        text=f"ID {t['id']} - {t['nome_disciplina']} ({t['nome_professor']})",
                                        variable=var,
                                        bg=self.colors['card'], fg=self.colors['text'],
                                        activebackground=self.colors['card'], activeforeground=self.colors['text'],
                                        selectcolor=self.colors['input_bg'], 
                                        highlightthickness=0,
                                        font=('Arial', 10))
                checkbox.pack(anchor='w', pady=2)
                dialog.after(50, update_scroll) # 'after' garante que o Tkinter já desenhou os widgets
        
        def save_professor_subjects():
            """Salva matérias do professor"""
            professor = prof_var.get()
            if not professor:
                messagebox.showwarning("Aviso", "Selecione um professor!")
                return
            
            # Obter matérias selecionadas
            selected_subjects = [subject_id for subject_id, var in subject_vars.items() if var.get()]
            
            # Salvar no banco
            success, msg = self.db.set_professor_subjects(professor, selected_subjects)
            if success:
                messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", msg)
        
        # Bind para carregar matérias quando professor muda
        prof_combo.bind("<<ComboboxSelected>>", lambda e: load_professor_subjects())
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Salvar Acessos", command=save_professor_subjects, style='Dialog.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Atualizar", command=load_professor_subjects, style='Dialog.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Fechar", command=dialog.destroy, style='Secondary.TButton').pack(side=tk.RIGHT)
        
        # Configurar scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        # <-- MUDANÇA 2: Adicionar padx para dar espaçamento lateral
        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        
        # Carregar dados iniciais
        load_professors()
    
    def listar_professores(self):
        """Lista todos os professores e suas matérias"""
        if self.role != 'admin':
            messagebox.showerror("Erro", "Acesso negado. Apenas administradores podem listar professores.")
            return
        
        professors = self.db.get_all_professors()
        
        if not professors:
            messagebox.showinfo("Informação", "Nenhum professor cadastrado.")
            return
        
        # Criar janela de listagem
        list_window = tk.Toplevel(self)
        list_window.title("Lista de Professores")
        list_window.geometry("700x500")
        list_window.transient(self)
        list_window.grab_set()
        
        # Centralizar janela
        list_window.update_idletasks()
        x = (list_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (list_window.winfo_screenheight() // 2) - (500 // 2)
        list_window.geometry(f'700x500+{x}+{y}')
        
        # Aplicar tema
        try:
            _apply_popup_theme(list_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(list_window)
        
        # Frame principal
        outer_frame = tk.Frame(list_window, bg=self.colors['card'])
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(outer_frame, text="Lista de Professores", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 15))
        
        # Frame com scrollbar
        canvas = tk.Canvas(outer_frame, bg=self.colors['card'], highlightthickness=0)
        # <-- MUDANÇA 1: Aplicar o estilo moderno
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        
        # Lista de professores
        for i, prof in enumerate(professors):
            prof_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            prof_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Nome e email
            info_frame = tk.Frame(prof_frame, bg=self.colors['card'])
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(info_frame, text=f"{prof['username']}", 
                    font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            if prof['email']:
                tk.Label(info_frame, text=f"{prof['email']}", 
                        font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            # Matérias
            subjects_text = "Matérias: "
            if prof['subjects']:
                subjects_text += ", ".join([f"ID {s}" for s in prof['subjects']])
            else:
                subjects_text += "Nenhuma matéria atribuída"
            
            tk.Label(info_frame, text=subjects_text, 
                    font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        # Configurar scrollbar
        canvas.pack(side="left", fill="both", expand=True, pady=(0, 15))
        # <-- MUDANÇA 2: Adicionar padx para espaçamento
        scrollbar.pack(side="right", fill="y", pady=(0, 15), padx=(5, 0))
        
        # Botão fechar
        ttk.Button(outer_frame, text="✕ Fechar", command=list_window.destroy, style='Secondary.TButton').pack(pady=(15, 0))
    
    def listar_alunos_usuarios(self):
        """Lista todos os alunos com suas informações"""
        if self.role != 'admin':
            messagebox.showerror("Erro", "Acesso negado. Apenas administradores podem listar alunos.")
            return
        
        # Buscar todos os usuários com role 'aluno'
        alunos = []
        for username, data in self.db.users.items():
            if data['role'] == 'aluno':
                matricula = data.get('matricula', 'Não associada')
                alunos.append({
                    'username': username,
                    'email': data.get('email', 'Não cadastrado'),
                    'matricula': matricula,
                    'status': data.get('status', 'approved')
                })
        
        if not alunos:
            messagebox.showinfo("Informação", "Nenhum aluno cadastrado.")
            return
        
        # Criar janela de listagem
        list_window = tk.Toplevel(self)
        list_window.title("Lista de Alunos")
        list_window.geometry("700x500")
        list_window.transient(self)
        list_window.grab_set()
        
        # Centralizar janela
        list_window.update_idletasks()
        x = (list_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (list_window.winfo_screenheight() // 2) - (500 // 2)
        list_window.geometry(f'700x500+{x}+{y}')
        
        # Aplicar tema
        try:
            _apply_popup_theme(list_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(list_window)
        
        # Frame principal
        outer_frame = tk.Frame(list_window, bg=self.colors['card'])
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(outer_frame, text="Lista de Alunos", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 15))
        
        # Frame com scrollbar
        canvas = tk.Canvas(outer_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",  
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Lista de alunos
        for i, aluno in enumerate(alunos):
            aluno_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            aluno_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Informações
            info_frame = tk.Frame(aluno_frame, bg=self.colors['card'])
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(info_frame, text=f"{aluno['username']}", 
                    font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            tk.Label(info_frame, text=f"{aluno['email']}", 
                    font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            tk.Label(info_frame, text=f"Matrícula: {aluno['matricula']}", 
                    font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            # Status
            status_color = '#4CAF50' if aluno['status'] == 'approved' else '#FF9800'
            tk.Label(info_frame, text=f"Status: {aluno['status'].title()}", 
                    font=('Arial', 10, 'bold'), bg=self.colors['card'], fg=status_color).pack(anchor='w')
        
        # Configurar scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão fechar
        ttk.Button(outer_frame, text="Fechar", command=list_window.destroy, style='Secondary.TButton').pack(pady=(15, 0))
    
    def listar_administradores(self):
        """Lista todos os administradores"""
        if self.role != 'admin':
            messagebox.showerror("Erro", "Acesso negado. Apenas administradores podem listar administradores.")
            return
        
        # Buscar todos os usuários com role 'admin'
        admins = []
        for username, data in self.db.users.items():
            if data['role'] == 'admin':
                admins.append({
                    'username': username,
                    'email': data.get('email', 'Não cadastrado'),
                    'status': data.get('status', 'approved')
                })
        
        if not admins:
            messagebox.showinfo("Informação", "Nenhum administrador cadastrado.")
            return
        
        # Criar janela de listagem
        list_window = tk.Toplevel(self)
        list_window.title("Lista de Administradores")
        list_window.geometry("700x400")
        list_window.transient(self)
        list_window.grab_set()
        
        # Centralizar janela
        list_window.update_idletasks()
        x = (list_window.winfo_screenwidth() // 2) - (700 // 2)
        y = (list_window.winfo_screenheight() // 2) - (400 // 2)
        list_window.geometry(f'700x400+{x}+{y}')
        
        # Aplicar tema
        try:
            _apply_popup_theme(list_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(list_window)
        
        # Frame principal
        outer_frame = tk.Frame(list_window, bg=self.colors['card'])
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(outer_frame, text="Lista de Administradores", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 15))
        
        # Frame com scrollbar
        canvas = tk.Canvas(outer_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Lista de administradores
        for i, admin in enumerate(admins):
            admin_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
            admin_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Informações
            info_frame = tk.Frame(admin_frame, bg=self.colors['card'])
            info_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(info_frame, text=f"{admin['username']}", 
                    font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            tk.Label(info_frame, text=f"{admin['email']}", 
                    font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
            
            # Status
            status_color = '#4CAF50' if admin['status'] == 'approved' else '#FF9800'
            tk.Label(info_frame, text=f"Status: {admin['status'].title()}", 
                    font=('Arial', 10, 'bold'), bg=self.colors['card'], fg=status_color).pack(anchor='w')
        
        # Configurar scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão fechar
        ttk.Button(outer_frame, text="Fechar", command=list_window.destroy, style='Secondary.TButton').pack(pady=(15, 0))

    def listar_usuarios_consolidado(self):
        """Lista todos os usuários com filtro por tipo e informações detalhadas"""
        if self.role != 'admin':
            messagebox.showerror("Erro", "Acesso negado. Apenas administradores podem listar usuários.")
            return
        
        # Criar janela de listagem
        list_window = tk.Toplevel(self)
        list_window.title("Lista de Usuários")
        list_window.geometry("900x600")
        list_window.transient(self)
        list_window.grab_set()
        
        # Centralizar janela
        list_window.update_idletasks()
        x = (list_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (list_window.winfo_screenheight() // 2) - (600 // 2)
        list_window.geometry(f'900x600+{x}+{y}')
        
        # Aplicar tema
        try:
            _apply_popup_theme(list_window, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(list_window)
        
        # Frame principal
        outer_frame = tk.Frame(list_window, bg=self.colors['card'])
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(outer_frame, text="Lista de Usuários", 
                              font=('Arial', 16, 'bold'), bg=self.colors['card'], fg=self.colors['primary'])
        title_label.pack(pady=(0, 15))
        
        # Filtro por tipo
        filter_frame = tk.Frame(outer_frame, bg=self.colors['card'])
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(filter_frame, text="Filtrar por Tipo:", font=('Arial', 11, 'bold'), 
                bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT, padx=(0, 10))
        
        filter_var = tk.StringVar(value='Todos')
        filter_combo = ttk.Combobox(filter_frame, textvariable=filter_var, 
                                   values=['Todos', 'Alunos', 'Professores', 'Administradores'], 
                                   state="readonly", width=20)
        filter_combo.pack(side=tk.LEFT)
        
        # Frame com scrollbar para lista de usuários
        list_container_frame = tk.Frame(outer_frame, bg=self.colors['card'])
        # Aplicamos o padding vertical aqui, no container geral
        list_container_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Canvas e Scrollbar (agora dentro do novo container)
        canvas = tk.Canvas(list_container_frame, bg=self.colors['card'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
        # Criar a janela no canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Ajustar largura do scrollable_frame para preencher o canvas
            canvas.itemconfig(canvas_window, width=event.width)
        
        scrollable_frame.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", on_canvas_configure)
        
        def format_time_elapsed(iso_timestamp):
            """Formata tempo decorrido desde um timestamp ISO"""
            if not iso_timestamp:
                return "Nunca"
            try:
                import datetime
                dt = datetime.datetime.fromisoformat(iso_timestamp)
                now = datetime.datetime.now()
                delta = now - dt
                
                if delta.days > 365:
                    years = delta.days // 365
                    return f"Há {years} ano{'s' if years > 1 else ''}"
                elif delta.days > 30:
                    months = delta.days // 30
                    return f"Há {months} mês{'es' if months > 1 else ''}"
                elif delta.days > 0:
                    return f"Há {delta.days} dia{'s' if delta.days > 1 else ''}"
                elif delta.seconds > 3600:
                    hours = delta.seconds // 3600
                    return f"Há {hours} hora{'s' if hours > 1 else ''}"
                elif delta.seconds > 60:
                    minutes = delta.seconds // 60
                    return f"Há {minutes} minuto{'s' if minutes > 1 else ''}"
                else:
                    return "Agora mesmo"
            except:
                return "Desconhecido"
        
        def format_total_time(seconds):
            """Formata tempo total de uso"""
            if not seconds or seconds == 0:
                return "0 minutos"
            
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            
            if hours > 24:
                days = hours // 24
                hours = hours % 24
                return f"{days}d {hours}h {minutes}min"
            elif hours > 0:
                return f"{hours}h {minutes}min"
            else:
                return f"{minutes}min"
        
        def refresh_list():
            # Limpar lista
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # Filtrar usuários baseado no tipo selecionado
            filter_type = filter_var.get()
            role_filter = None
            if filter_type == 'Alunos':
                role_filter = 'aluno'
            elif filter_type == 'Professores':
                role_filter = 'professor'
            elif filter_type == 'Administradores':
                role_filter = 'admin'
            
            # Buscar usuários
            usuarios = []
            for username, data in self.db.users.items():
                if role_filter is None or data.get('role') == role_filter:
                    usuarios.append({
                        'username': username,
                        'email': data.get('email', 'Não cadastrado'),
                        'role': data.get('role', 'Desconhecido'),
                        'status': data.get('status', 'approved'),
                        'created_at': data.get('created_at'),
                        'last_login': data.get('last_login'),
                        'total_time': data.get('total_time', 0),
                        'matricula': data.get('matricula') if data.get('role') == 'aluno' else None
                    })
            
            if not usuarios:
                tk.Label(scrollable_frame, text="Nenhum usuário encontrado com este filtro", 
                        bg=self.colors['card'], fg=self.colors['text']).pack(pady=20)
                return
            
            # Ordenar por data de criação (mais recentes primeiro)
            usuarios.sort(key=lambda u: u.get('created_at') or '', reverse=True)
            
            # Lista de usuários
            for i, user in enumerate(usuarios):
                user_frame = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='solid', bd=1)
                user_frame.pack(fill=tk.X, pady=5, padx=5)
                
                # Informações principais
                info_frame = tk.Frame(user_frame, bg=self.colors['card'])
                info_frame.pack(fill=tk.X, padx=10, pady=10)
                
                # Nome e role
                name_role_frame = tk.Frame(info_frame, bg=self.colors['card'])
                name_role_frame.pack(fill=tk.X, anchor='w')
                
                tk.Label(name_role_frame, text=f"{user['username']}", 
                        font=('Arial', 12, 'bold'), bg=self.colors['card'], fg=self.colors['text']).pack(side=tk.LEFT)
                
                # Badge do role
                role_colors = {
                    'admin': '#F44336',
                    'professor': '#2196F3',
                    'aluno': '#4CAF50'
                }
                role_labels = {
                    'admin': 'Admin',
                    'professor': 'Professor',
                    'aluno': 'Aluno'
                }
                role_bg = role_colors.get(user['role'], '#757575')
                role_label = role_labels.get(user['role'], user['role'].title())
                
                role_badge = tk.Label(name_role_frame, text=role_label, 
                                    font=('Arial', 9, 'bold'), bg=role_bg, fg='white',
                                    padx=8, pady=2)
                role_badge.pack(side=tk.LEFT, padx=(10, 0))
                
                # Status
                if user['status'] == 'pending':
                    status_badge = tk.Label(name_role_frame, text="Pendente", 
                                          font=('Arial', 9, 'bold'), bg='#FF9800', fg='white',
                                          padx=8, pady=2)
                    status_badge.pack(side=tk.LEFT, padx=(5, 0))
                
                # Email
                tk.Label(info_frame, text=f"Email: {user['email']}", 
                        font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                
                # Matrícula (se aluno)
                if user['matricula']:
                    tk.Label(info_frame, text=f"Matrícula: {user['matricula']}", 
                            font=('Arial', 10), bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
                
                # Frame de estatísticas
                stats_frame = tk.Frame(info_frame, bg=self.colors['card'])
                stats_frame.pack(fill=tk.X, pady=(5, 0))
                
                # Data de criação
                created_text = format_time_elapsed(user['created_at'])
                tk.Label(stats_frame, text=f"Criado: {created_text}", 
                        font=('Arial', 9), bg=self.colors['card'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 15))
                
                # Último acesso
                last_login_text = format_time_elapsed(user['last_login'])
                tk.Label(stats_frame, text=f"Último acesso: {last_login_text}", 
                        font=('Arial', 9), bg=self.colors['card'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 15))
                
                # Tempo total de uso
                total_time_text = format_total_time(user['total_time'])
                tk.Label(stats_frame, text=f"Tempo de uso: {total_time_text}", 
                        font=('Arial', 9), bg=self.colors['card'], fg=self.colors['text_secondary']).pack(side=tk.LEFT)
        
        refresh_list()
        
        # Bind para atualizar ao mudar o filtro
        filter_combo.bind("<<ComboboxSelected>>", lambda e: refresh_list())
        
        # Configurar scrollbar
        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        canvas.pack(side="left", fill="both", expand=True)
        
        # Habilitar scroll com o mouse
        _enable_canvas_scroll(canvas, scrollable_frame)
        
        # Botão fechar na parte inferior
        btn_frame = ttk.Frame(outer_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        close_btn = ttk.Button(btn_frame, text="✕ Fechar", command=list_window.destroy, style='Secondary.TButton')
        close_btn.pack(pady=10)
        
        # Configurar atalhos (ESC fecha)
        _setup_dialog_shortcuts(list_window, ok_button=close_btn, cancel_callback=list_window.destroy)

    def gerenciar_anotacoes(self):
        """Sistema de gerenciamento de anotações"""
        dialog = tk.Toplevel(self)
        dialog.configure(bg=self.colors['card'])
        try:
            _apply_popup_theme(dialog, self.colors, self.fonts, getattr(self, 'style', None))
        except Exception:
            pass
        _set_window_icon(dialog)
        dialog.title("Gerenciador de Anotações")
        
        # Configurar para ocupar altura inteira da tela
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        largura = 1200
        altura = screen_height - 90  # Deixa margem para barra de tarefas
        x = (screen_width - largura) // 2
        y = 0
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        # Permitir redimensionamento
        dialog.resizable(True, True)
        dialog.minsize(800, 600)
        
        dialog.transient(self)
        dialog.grab_set()
        
        # Header compacto
        header_frame = ttk.Frame(dialog)
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        title_label = ttk.Label(header_frame, text="Gerenciador de Anotações", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(anchor='w')
        
        # Instruções compactas
        instructions_text = """DICAS: Duplo clique para editar • Exportar para diferentes formatos • Salvas automaticamente"""
        
        instructions_label = ttk.Label(header_frame, text=instructions_text, 
                                     font=('Arial', 9), foreground=self.colors.get('text_secondary', self.colors['text']))
        instructions_label.pack(anchor='w', pady=(5, 0))
        
        # Frame principal com espaçamento otimizado
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Frame esquerdo - Lista de anotações
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Suas Anotações:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Lista de anotações
        notes_list_frame = ttk.Frame(left_frame)
        notes_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para lista de anotações - otimizada para redimensionamento
        columns = ("Título", "Data")
        notes_tree = ttk.Treeview(notes_list_frame, columns=columns, show="headings", height=18)
        notes_tree.heading("Título", text="Título")
        notes_tree.heading("Data", text="Data")
        notes_tree.column("Título", width=250)
        notes_tree.column("Data", width=120)
        notes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para lista
        notes_scrollbar = ttk.Scrollbar(notes_list_frame, orient=tk.VERTICAL, command=notes_tree.yview)
        notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        notes_tree.configure(yscrollcommand=notes_scrollbar.set)
        
        # Frame direito - Editor de anotações
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Editor de Anotações:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Campo de título
        title_frame = ttk.Frame(right_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Título:").pack(anchor='w')
        title_entry = ttk.Entry(title_frame, font=('Arial', 11))
        title_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Editor de texto
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(text_frame, text="Conteúdo:").pack(anchor='w')
        
        # Frame para o editor com scrollbar
        editor_container = ttk.Frame(text_frame)
        editor_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        text_editor = tk.Text(editor_container, wrap=tk.WORD, font=('Arial', 10), height=18,
                             bg=self.colors['input_bg'], fg=self.colors['text'],
                             insertbackground=self.colors['text'],
                             selectbackground=self.colors['primary'],
                             selectforeground=self.colors['card'])
        text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para editor
        text_scrollbar = ttk.Scrollbar(editor_container, orient=tk.VERTICAL, command=text_editor.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_editor.configure(yscrollcommand=text_scrollbar.set)
        
        # Adicionar linhas de caderno
        def configure_notebook_lines():
            """Configura linhas de caderno no editor"""
            try:
                # Configurar espaçamento entre linhas
                text_editor.configure(spacing1=3, spacing2=1, spacing3=3)
                
                # Adicionar tags para linhas
                text_editor.tag_configure("line", background=self.colors.get('row_even', '#F0F0F0'))
                
                # Configurar fonte monoespaçada para melhor alinhamento
                text_editor.configure(font=('Courier New', 10))
            except Exception:
                pass
        
        configure_notebook_lines()
        
        # Botões de ação com layout compacto
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        def carregar_anotacoes():
            """Carrega as anotações salvas"""
            notes_tree.delete(*notes_tree.get_children())
            try:
                if os.path.exists("anotacoes.json"):
                    with open("anotacoes.json", "r", encoding="utf-8") as f:
                        anotacoes = json.load(f)
                        for anotacao in anotacoes:
                            notes_tree.insert("", "end", values=(anotacao["titulo"], anotacao["data"]))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar anotações: {e}")
        
        def salvar_anotacao():
            """Salva uma nova anotação"""
            titulo = title_entry.get().strip()
            conteudo = text_editor.get("1.0", tk.END).strip()
            
            if not titulo or not conteudo:
                messagebox.showwarning("Aviso", "Por favor, preencha título e conteúdo!")
                return
            
            try:
                anotacoes = []
                if os.path.exists("anotacoes.json"):
                    with open("anotacoes.json", "r", encoding="utf-8") as f:
                        anotacoes = json.load(f)
                
                # Verificar se já existe anotação com mesmo título
                for anotacao in anotacoes:
                    if anotacao["titulo"] == titulo:
                        if messagebox.askyesno("Confirmar", f"Já existe uma anotação com o título '{titulo}'. Deseja substituir?"):
                            anotacoes.remove(anotacao)
                        else:
                            return
                
                nova_anotacao = {
                    "titulo": titulo,
                    "conteudo": conteudo,
                    "data": time.strftime("%d/%m/%Y %H:%M")
                }
                anotacoes.append(nova_anotacao)
                
                with open("anotacoes.json", "w", encoding="utf-8") as f:
                    json.dump(anotacoes, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Sucesso", "Anotação salva com sucesso!")
                carregar_anotacoes()
                title_entry.delete(0, tk.END)
                text_editor.delete("1.0", tk.END)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar anotação: {e}")
        
        def editar_anotacao_selecionada():
            """Edita a anotação selecionada no editor"""
            selection = notes_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione uma anotação para editar!")
                return
            
            item = notes_tree.item(selection[0])
            titulo = item["values"][0]
            
            try:
                if os.path.exists("anotacoes.json"):
                    with open("anotacoes.json", "r", encoding="utf-8") as f:
                        anotacoes = json.load(f)
                        for anotacao in anotacoes:
                            if anotacao["titulo"] == titulo:
                                title_entry.delete(0, tk.END)
                                title_entry.insert(0, anotacao["titulo"])
                                text_editor.delete("1.0", tk.END)
                                text_editor.insert("1.0", anotacao["conteudo"])
                                break
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar anotação: {e}")
        
        def excluir_anotacao():
            """Exclui a anotação selecionada"""
            selection = notes_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione uma anotação para excluir!")
                return
            
            item = notes_tree.item(selection[0])
            titulo = item["values"][0]
            
            if messagebox.askyesno("Confirmar", f"Deseja realmente excluir a anotação '{titulo}'?"):
                try:
                    if os.path.exists("anotacoes.json"):
                        with open("anotacoes.json", "r", encoding="utf-8") as f:
                            anotacoes = json.load(f)
                        
                        anotacoes = [a for a in anotacoes if a["titulo"] != titulo]
                        
                        with open("anotacoes.json", "w", encoding="utf-8") as f:
                            json.dump(anotacoes, f, ensure_ascii=False, indent=2)
                        
                        messagebox.showinfo("Sucesso", "Anotação excluída com sucesso!")
                        carregar_anotacoes()
                        title_entry.delete(0, tk.END)
                        text_editor.delete("1.0", tk.END)
                        
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao excluir anotação: {e}")
        
        def exportar_anotacao():
            """Exporta a anotação selecionada para arquivo"""
            selection = notes_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione uma anotação para exportar!")
                return
            
            item = notes_tree.item(selection[0])
            titulo = item["values"][0]
            
            try:
                if os.path.exists("anotacoes.json"):
                    with open("anotacoes.json", "r", encoding="utf-8") as f:
                        anotacoes = json.load(f)
                        anotacao_encontrada = False
                        for anotacao in anotacoes:
                            if anotacao["titulo"] == titulo:
                                anotacao_encontrada = True
                                # Escolher formato de exportação
                                formato = tk.StringVar(value="txt")
                                format_dialog = tk.Toplevel(dialog)
                                format_dialog.configure(bg=self.colors['card'])
                                try:
                                    _apply_popup_theme(format_dialog, self.colors, self.fonts, getattr(self, 'style', None))
                                except Exception:
                                    pass
                                format_dialog.title("Escolher Formato de Exportação")
                                format_dialog.geometry("400x200")
                                format_dialog.transient(dialog)
                                format_dialog.grab_set()
                                
                                # Centralizar o popup
                                format_dialog.update_idletasks()
                                x = (format_dialog.winfo_screenwidth() // 2) - (400 // 2)
                                y = (format_dialog.winfo_screenheight() // 2) - (200 // 2)
                                format_dialog.geometry(f"400x200+{x}+{y}")
                                
                                # Aplicar ícone
                                _set_window_icon(format_dialog)
                                
                                # Frame principal
                                format_frame = ttk.Frame(format_dialog)
                                format_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                                
                                ttk.Label(format_frame, text="Escolha o formato de exportação:", 
                                         font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 10))
                                
                                # Menu suspenso para seleção do formato
                                format_options = [
                                    ("📄 Texto (.txt)", "txt"),
                                    ("📝 Markdown (.md)", "md"),
                                    ("📊 JSON (.json)", "json")
                                ]
                                
                                # Frame para o combobox
                                combo_frame = tk.Frame(format_frame, bg=self.colors['card'])
                                combo_frame.pack(fill=tk.X, pady=(0, 15))
                                
                                # Combobox com tema dark
                                format_combo = ttk.Combobox(combo_frame, textvariable=formato, 
                                                           values=[opt[1] for opt in format_options],
                                                           state="readonly", width=25, font=('Arial', 10))
                                format_combo.pack(anchor='w', pady=5, fill=tk.X)
                                format_combo.set("txt")  # Valor padrão
                                
                                # Configurar estilo do combobox para tema dark
                                try:
                                    style = ttk.Style()
                                    style.configure("TCombobox", 
                                                  fieldbackground=self.colors['input_bg'],
                                                  background=self.colors['input_bg'],
                                                  foreground=self.colors['text'],
                                                  borderwidth=1,
                                                  relief="solid")
                                    style.map("TCombobox",
                                             fieldbackground=[('readonly', self.colors['input_bg'])],
                                             background=[('readonly', self.colors['input_bg'])],
                                             foreground=[('readonly', self.colors['text'])])
                                except Exception:
                                    pass
                                
                                # Label para mostrar a descrição do formato selecionado
                                desc_label = tk.Label(combo_frame, text="Texto (.txt)", 
                                                           bg=self.colors['card'], fg=self.colors['text'],
                                                    font=('Arial', 9), anchor='w')
                                desc_label.pack(anchor='w', pady=(5, 0))
                                
                                # Função para atualizar a descrição quando o formato muda
                                def update_description(event=None):
                                    selected = formato.get()
                                    for desc, value in format_options:
                                        if value == selected:
                                            desc_label.config(text=desc)
                                            break
                                
                                format_combo.bind("<<ComboboxSelected>>", update_description)
                                
                                def exportar():
                                    formato_escolhido = formato.get()
                                    
                                    # Validar se um formato foi selecionado
                                    if not formato_escolhido:
                                        messagebox.showwarning("Aviso", "Por favor, selecione um formato de exportação!")
                                        return
                                    
                                    if formato_escolhido == "txt":
                                        conteudo = f"Título: {anotacao['titulo']}\nData: {anotacao['data']}\n\n{anotacao['conteudo']}"
                                        extensao = ".txt"
                                    elif formato_escolhido == "md":
                                        conteudo = f"# {anotacao['titulo']}\n\n*Data: {anotacao['data']}*\n\n{anotacao['conteudo']}"
                                        extensao = ".md"
                                    elif formato_escolhido == "json":
                                        conteudo = json.dumps(anotacao, ensure_ascii=False, indent=2)
                                        extensao = ".json"
                                    else:
                                        messagebox.showerror("Erro", "Formato de exportação inválido!")
                                        return
                                    
                                    # Salvar arquivo - limpar título para nome de arquivo válido
                                    titulo_limpo = "".join(c for c in anotacao['titulo'] if c.isalnum() or c in (' ', '-', '_')).strip()
                                    if not titulo_limpo:
                                        titulo_limpo = "anotacao"
                                    
                                    filename = filedialog.asksaveasfilename(
                                        defaultextension=extensao,
                                        initialfile=f"{titulo_limpo}{extensao}",
                                        title="Salvar Anotação"
                                    )
                                    
                                    if filename:
                                        try:
                                            with open(filename, "w", encoding="utf-8") as f:
                                                f.write(conteudo)
                                            messagebox.showinfo("Sucesso", f"Anotação exportada para {filename}")
                                            format_dialog.destroy()
                                        except Exception as e:
                                            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
                                
                                # Botões de ação com tema dark corrigido
                                button_frame = tk.Frame(format_frame, bg=self.colors['card'])
                                button_frame.pack(fill=tk.X, pady=(10, 0))
                                
                                export_btn = tk.Button(button_frame, text="📤 Exportar", command=exportar,
                                                     bg=self.colors['primary'], fg=self.colors['card'],
                                                     activebackground=self.colors['primary_hover'], activeforeground=self.colors['card'],
                                                     font=('Arial', 10, 'bold'), relief='flat', padx=15, pady=5)
                                export_btn.pack(side=tk.LEFT, padx=(0, 10))
                                
                                cancel_btn = tk.Button(button_frame, text="❌ Cancelar", command=format_dialog.destroy,
                                                     bg=self.colors['border'], fg=self.colors['text'],
                                                     activebackground=self.colors['hover'], activeforeground=self.colors['text'],
                                                     font=('Arial', 10), relief='flat', padx=15, pady=5)
                                cancel_btn.pack(side=tk.LEFT)
                                break
                        
                        if not anotacao_encontrada:
                            messagebox.showerror("Erro", "Anotação não encontrada!")
                else:
                    messagebox.showerror("Erro", "Arquivo de anotações não encontrado!")
                        
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar anotação: {e}")
        
        # Botões em uma linha compacta para evitar cortes
        ttk.Button(buttons_frame, text="Salvar", command=salvar_anotacao, style='Dialog.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Excluir", command=excluir_anotacao, style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Exportar", command=exportar_anotacao, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Atualizar", command=carregar_anotacoes, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 5))
        
        # Bind duplo clique para editar anotação
        notes_tree.bind("<Double-1>", lambda e: editar_anotacao_selecionada())
        
        # Carregar anotações iniciais
        carregar_anotacoes()

if __name__ == "__main__":
    if os.name!='posix': multiprocessing.freeze_support(); multiprocessing.set_start_method('spawn', True)
    print("[MAIN] Iniciando servidor..."); server_p = multiprocessing.Process(target=run_server, daemon=True); server_p.start(); time.sleep(1.5)
    if not server_p.is_alive(): print("[MAIN-ERRO] Falha ao iniciar o servidor.")
    else: print("[MAIN] Iniciando GUI..."); login=LoginWindow(); login.mainloop()
    if server_p.is_alive(): print("[MAIN] Encerrando servidor..."); server_p.terminate(); server_p.join()
