#include "database.h"
#include <stdio.h>
#include <string.h>

#define MAX_TURMAS 100
#define MAX_ALUNOS 500
#define TURMAS_DB_FILE "turmas.dat"
#define ALUNOS_DB_FILE "alunos.dat"

// Banco de dados em memória
static Turma turmas[MAX_TURMAS];
static int num_turmas = 0;
static Aluno alunos[MAX_ALUNOS];
static int num_alunos = 0;
static int dados_carregados = 0;

// Protótipos de funções internas
void carregar_dados();
void salvar_dados_turmas();
void salvar_dados_alunos();

// Função para carregar os dados dos arquivos binários
void carregar_dados() {
    if (dados_carregados) return;
    FILE *f_turmas = fopen(TURMAS_DB_FILE, "rb");
    if (f_turmas) {
        fread(&num_turmas, sizeof(int), 1, f_turmas);
        fread(turmas, sizeof(Turma), num_turmas, f_turmas);
        fclose(f_turmas);
    }
    FILE *f_alunos = fopen(ALUNOS_DB_FILE, "rb");
    if (f_alunos) {
        fread(&num_alunos, sizeof(int), 1, f_alunos);
        fread(alunos, sizeof(Aluno), num_alunos, f_alunos);
        fclose(f_alunos);
    }
    dados_carregados = 1;
}

// Funções para salvar os dados nos arquivos
void salvar_dados_turmas() {
    FILE* f = fopen(TURMAS_DB_FILE, "wb");
    if (f) {
        fwrite(&num_turmas, sizeof(int), 1, f);
        fwrite(turmas, sizeof(Turma), num_turmas, f);
        fclose(f);
    }
}

void salvar_dados_alunos() {
    FILE* f = fopen(ALUNOS_DB_FILE, "wb");
    if (f) {
        fwrite(&num_alunos, sizeof(int), 1, f);
        fwrite(alunos, sizeof(Aluno), num_alunos, f);
        fclose(f);
    }
}


// --- Implementação das Funções Exportadas ---

// CORRIGIDO: Esta é a versão correta, que aceita um ponteiro.
EXPORT void salvar_turma(const Turma* nova_turma) {
    carregar_dados();
    if (num_turmas < MAX_TURMAS) {
        turmas[num_turmas++] = *nova_turma; // Usa * para obter o valor do ponteiro
        salvar_dados_turmas();
    }
}

// CORRIGIDO: Esta é a versão correta, que aceita um ponteiro.
EXPORT void salvar_aluno(const Aluno* novo_aluno) {
    carregar_dados();
    if (num_alunos < MAX_ALUNOS) {
        alunos[num_alunos++] = *novo_aluno; // Usa * para obter o valor do ponteiro
        salvar_dados_alunos();
    }
}

EXPORT int turma_existe(int id) {
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) if (turmas[i].id == id) return 1;
    return 0;
}

EXPORT int matricula_existe(int matricula) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) if (alunos[i].matricula == matricula) return 1;
    return 0;
}

EXPORT int listar_turmas(Turma* arr, int len) {
    carregar_dados();
    int c = (num_turmas < len) ? num_turmas : len;
    if (c > 0) memcpy(arr, turmas, c * sizeof(Turma));
    return c;
}

EXPORT int listar_alunos_por_turma(int id, Aluno* arr, int len) {
    carregar_dados();
    int c = 0;
    for (int i = 0; i < num_alunos && c < len; i++) if (alunos[i].id_turma == id) arr[c++] = alunos[i];
    return c;
}

EXPORT int buscar_turma_por_id(int id, Turma* t) {
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) if (turmas[i].id == id) { *t = turmas[i]; return 1; }
    return 0;
}

EXPORT int buscar_aluno_por_matricula(int m, Aluno* a) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) if (alunos[i].matricula == m) { *a = alunos[i]; return 1; }
    return 0;
}

EXPORT int atualizar_turma(int id, const char* d, const char* p) {
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id) {
            strncpy(turmas[i].nome_disciplina, d, 99); turmas[i].nome_disciplina[99] = '\0';
            strncpy(turmas[i].nome_professor, p, 99); turmas[i].nome_professor[99] = '\0';
            salvar_dados_turmas();
            return 1;
        }
    }
    return 0;
}

EXPORT int atualizar_aluno(int m, const char* n) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == m) {
            strncpy(alunos[i].nome, n, 99); alunos[i].nome[99] = '\0';
            salvar_dados_alunos();
            return 1;
        }
    }
    return 0;
}

EXPORT int deletar_aluno(int matricula) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            for (int j = i; j < num_alunos - 1; j++) alunos[j] = alunos[j + 1];
            num_alunos--;
            salvar_dados_alunos();
            return 1;
        }
    }
    return 0;
}

EXPORT int deletar_turma(int id_turma) {
    carregar_dados();
    int turma_encontrada = 0;
    for (int i = num_alunos - 1; i >= 0; i--) {
        if (alunos[i].id_turma == id_turma) {
            for (int j = i; j < num_alunos - 1; j++) alunos[j] = alunos[j + 1];
            num_alunos--;
        }
    }
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id_turma) {
            turma_encontrada = 1;
            for (int j = i; j < num_turmas - 1; j++) turmas[j] = turmas[j + 1];
            num_turmas--;
            break;
        }
    }
    if (turma_encontrada) {
        salvar_dados_alunos();
        salvar_dados_turmas();
    }
    return turma_encontrada;
}

EXPORT int alterar_id_turma(int id_antigo, int id_novo) {
    carregar_dados();
    if (id_antigo == id_novo) return 1;
    if (turma_existe(id_novo)) return -1;
    int turma_idx = -1;
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id_antigo) {
            turma_idx = i;
            break;
        }
    }
    if (turma_idx != -1) {
        turmas[turma_idx].id = id_novo;
        for (int i = 0; i < num_alunos; i++) {
            if (alunos[i].id_turma == id_antigo) {
                alunos[i].id_turma = id_novo;
            }
        }
        salvar_dados_turmas();
        salvar_dados_alunos();
        return 1;
    }
    return 0;
}

EXPORT int alterar_matricula_aluno(int matricula_antiga, int matricula_nova) {
    carregar_dados();
    if (matricula_antiga == matricula_nova) return 1;
    if (matricula_existe(matricula_nova)) return -1;
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula_antiga) {
            alunos[i].matricula = matricula_nova;
            salvar_dados_alunos();
            return 1;
        }
    }
    return 0;
}