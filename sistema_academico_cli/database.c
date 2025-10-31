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

// ==============================================================================
// FUNÇÕES INTERNAS DE PERSISTÊNCIA
// ==============================================================================

/**
 * Carrega os dados dos arquivos binários para memória
 * Função é chamada automaticamente antes de qualquer operação
 */
void carregar_dados() {
    if (dados_carregados) return;
    
    // Carregar turmas
    FILE *f_turmas = fopen(TURMAS_DB_FILE, "rb");
    if (f_turmas) {
        fread(&num_turmas, sizeof(int), 1, f_turmas);
        fread(turmas, sizeof(Turma), num_turmas, f_turmas);
        fclose(f_turmas);
        printf("[DB-C] Carregadas %d turmas de %s\n", num_turmas, TURMAS_DB_FILE);
    } else {
        printf("[DB-C] Arquivo %s não encontrado - iniciando vazio\n", TURMAS_DB_FILE);
    }
    
    // Carregar alunos
    FILE *f_alunos = fopen(ALUNOS_DB_FILE, "rb");
    if (f_alunos) {
        fread(&num_alunos, sizeof(int), 1, f_alunos);
        fread(alunos, sizeof(Aluno), num_alunos, f_alunos);
        fclose(f_alunos);
        printf("[DB-C] Carregados %d alunos de %s\n", num_alunos, ALUNOS_DB_FILE);
    } else {
        printf("[DB-C] Arquivo %s não encontrado - iniciando vazio\n", ALUNOS_DB_FILE);
    }
    
    dados_carregados = 1;
}

/**
 * Salva todas as turmas em arquivo binário
 * CRÍTICO: Esta função DEVE ser chamada após qualquer modificação em turmas
 */
void salvar_dados_turmas() {
    FILE* f = fopen(TURMAS_DB_FILE, "wb");
    if (f) {
        fwrite(&num_turmas, sizeof(int), 1, f);
        fwrite(turmas, sizeof(Turma), num_turmas, f);
        fclose(f);
        printf("[DB-C] ✓ Salvas %d turmas em %s\n", num_turmas, TURMAS_DB_FILE);
    } else {
        printf("[DB-C] ✗ ERRO: Não foi possível abrir %s para escrita\n", TURMAS_DB_FILE);
    }
}

/**
 * Salva todos os alunos em arquivo binário
 * CRÍTICO: Esta função DEVE ser chamada após qualquer modificação em alunos
 */
void salvar_dados_alunos() {
    FILE* f = fopen(ALUNOS_DB_FILE, "wb");
    if (f) {
        fwrite(&num_alunos, sizeof(int), 1, f);
        fwrite(alunos, sizeof(Aluno), num_alunos, f);
        fclose(f);
        printf("[DB-C] ✓ Salvos %d alunos em %s\n", num_alunos, ALUNOS_DB_FILE);
    } else {
        printf("[DB-C] ✗ ERRO: Não foi possível abrir %s para escrita\n", ALUNOS_DB_FILE);
    }
}

// ==============================================================================
// FUNÇÕES EXPORTADAS - TURMAS
// ==============================================================================

/**
 * Salva uma nova turma no banco de dados
 * CORREÇÃO: Aceita ponteiro e valida antes de salvar
 */
EXPORT void salvar_turma(const Turma* nova_turma) {
    if (!nova_turma) {
        printf("[DB-C] ✗ ERRO: Ponteiro de turma nulo\n");
        return;
    }
    
    carregar_dados();
    
    if (num_turmas >= MAX_TURMAS) {
        printf("[DB-C] ✗ ERRO: Limite de turmas atingido (%d/%d)\n", num_turmas, MAX_TURMAS);
        return;
    }
    
    // Verificar duplicidade de ID
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == nova_turma->id) {
            printf("[DB-C] ✗ ERRO: Turma com ID %d já existe\n", nova_turma->id);
            return;
        }
    }
    
    turmas[num_turmas++] = *nova_turma;
    salvar_dados_turmas();
    printf("[DB-C] ✓ Turma ID %d salva (Total: %d turmas)\n", nova_turma->id, num_turmas);
}

/**
 * Verifica se uma turma existe pelo ID
 */
EXPORT int turma_existe(int id) {
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id) return 1;
    }
    return 0;
}

/**
 * Lista todas as turmas
 * Retorna: número de turmas copiadas para o array
 */
EXPORT int listar_turmas(Turma* arr, int len) {
    if (!arr) return 0;
    
    carregar_dados();
    int c = (num_turmas < len) ? num_turmas : len;
    if (c > 0) {
        memcpy(arr, turmas, c * sizeof(Turma));
    }
    return c;
}

/**
 * Busca uma turma específica pelo ID
 * Retorna: 1 se encontrou, 0 caso contrário
 */
EXPORT int buscar_turma_por_id(int id, Turma* t) {
    if (!t) return 0;
    
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id) {
            *t = turmas[i];
            return 1;
        }
    }
    return 0;
}

/**
 * Atualiza dados de uma turma existente
 * Retorna: 1 se atualizou, 0 se não encontrou
 */
EXPORT int atualizar_turma(int id, const char* d, const char* p) {
    if (!d || !p) return 0;
    
    carregar_dados();
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id) {
            strncpy(turmas[i].nome_disciplina, d, 99);
            turmas[i].nome_disciplina[99] = '\0';
            strncpy(turmas[i].nome_professor, p, 99);
            turmas[i].nome_professor[99] = '\0';
            salvar_dados_turmas();
            printf("[DB-C] ✓ Turma ID %d atualizada\n", id);
            return 1;
        }
    }
    printf("[DB-C] ✗ Turma ID %d não encontrada\n", id);
    return 0;
}

/**
 * Deleta uma turma e todos os seus alunos
 * Retorna: 1 se deletou, 0 se não encontrou
 */
EXPORT int deletar_turma(int id_turma) {
    carregar_dados();
    int turma_encontrada = 0;
    int alunos_removidos = 0;
    
    // Remover todos os alunos da turma (do fim para o início)
    for (int i = num_alunos - 1; i >= 0; i--) {
        if (alunos[i].id_turma == id_turma) {
            for (int j = i; j < num_alunos - 1; j++) {
                alunos[j] = alunos[j + 1];
            }
            num_alunos--;
            alunos_removidos++;
        }
    }
    
    // Remover a turma
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id_turma) {
            turma_encontrada = 1;
            for (int j = i; j < num_turmas - 1; j++) {
                turmas[j] = turmas[j + 1];
            }
            num_turmas--;
            break;
        }
    }
    
    if (turma_encontrada) {
        salvar_dados_alunos();
        salvar_dados_turmas();
        printf("[DB-C] ✓ Turma ID %d deletada (%d alunos removidos)\n", id_turma, alunos_removidos);
    } else {
        printf("[DB-C] ✗ Turma ID %d não encontrada\n", id_turma);
    }
    
    return turma_encontrada;
}

/**
 * Altera o ID de uma turma (atualiza também todos os alunos)
 * Retorna: 1 se alterou, 0 se não encontrou, -1 se novo ID já existe
 */
EXPORT int alterar_id_turma(int id_antigo, int id_novo) {
    carregar_dados();
    
    if (id_antigo == id_novo) return 1;
    
    // Verificar se novo ID já existe
    if (turma_existe(id_novo)) {
        printf("[DB-C] ✗ Novo ID %d já existe\n", id_novo);
        return -1;
    }
    
    // Procurar turma com ID antigo
    int turma_idx = -1;
    for (int i = 0; i < num_turmas; i++) {
        if (turmas[i].id == id_antigo) {
            turma_idx = i;
            break;
        }
    }
    
    if (turma_idx != -1) {
        // Atualizar ID da turma
        turmas[turma_idx].id = id_novo;
        
        // Atualizar ID em todos os alunos desta turma
        int alunos_atualizados = 0;
        for (int i = 0; i < num_alunos; i++) {
            if (alunos[i].id_turma == id_antigo) {
                alunos[i].id_turma = id_novo;
                alunos_atualizados++;
            }
        }
        
        salvar_dados_turmas();
        salvar_dados_alunos();
        printf("[DB-C] ✓ ID turma alterado: %d → %d (%d alunos atualizados)\n", 
               id_antigo, id_novo, alunos_atualizados);
        return 1;
    }
    
    printf("[DB-C] ✗ Turma com ID %d não encontrada\n", id_antigo);
    return 0;
}

// ==============================================================================
// FUNÇÕES EXPORTADAS - ALUNOS
// ==============================================================================

/**
 * Salva um novo aluno no banco de dados
 * CORREÇÃO: Aceita ponteiro e valida antes de salvar
 */
EXPORT void salvar_aluno(const Aluno* novo_aluno) {
    if (!novo_aluno) {
        printf("[DB-C] ✗ ERRO: Ponteiro de aluno nulo\n");
        return;
    }
    
    carregar_dados();
    
    if (num_alunos >= MAX_ALUNOS) {
        printf("[DB-C] ✗ ERRO: Limite de alunos atingido (%d/%d)\n", num_alunos, MAX_ALUNOS);
        return;
    }
    
    // Verificar duplicidade de matrícula
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == novo_aluno->matricula) {
            printf("[DB-C] ✗ ERRO: Aluno com matrícula %d já existe\n", novo_aluno->matricula);
            return;
        }
    }
    
    alunos[num_alunos++] = *novo_aluno;
    salvar_dados_alunos();
    printf("[DB-C] ✓ Aluno matrícula %d salvo (Total: %d alunos)\n", novo_aluno->matricula, num_alunos);
}

/**
 * Verifica se uma matrícula existe
 */
EXPORT int matricula_existe(int matricula) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) return 1;
    }
    return 0;
}

/**
 * Lista todos os alunos de uma turma específica
 * Retorna: número de alunos encontrados
 */
EXPORT int listar_alunos_por_turma(int id, Aluno* arr, int len) {
    if (!arr) return 0;
    
    carregar_dados();
    int c = 0;
    for (int i = 0; i < num_alunos && c < len; i++) {
        if (alunos[i].id_turma == id) {
            arr[c++] = alunos[i];
        }
    }
    return c;
}

/**
 * Busca um aluno específico pela matrícula
 * Retorna: 1 se encontrou, 0 caso contrário
 */
EXPORT int buscar_aluno_por_matricula(int m, Aluno* a) {
    if (!a) return 0;
    
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == m) {
            *a = alunos[i];
            return 1;
        }
    }
    return 0;
}

/**
 * Atualiza o nome de um aluno
 * Retorna: 1 se atualizou, 0 se não encontrou
 */
EXPORT int atualizar_aluno(int m, const char* n) {
    if (!n) return 0;
    
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == m) {
            strncpy(alunos[i].nome, n, 99);
            alunos[i].nome[99] = '\0';
            salvar_dados_alunos();
            printf("[DB-C] ✓ Aluno matrícula %d atualizado\n", m);
            return 1;
        }
    }
    printf("[DB-C] ✗ Aluno matrícula %d não encontrado\n", m);
    return 0;
}

/**
 * Deleta um aluno do banco de dados
 * Retorna: 1 se deletou, 0 se não encontrou
 */
EXPORT int deletar_aluno(int matricula) {
    carregar_dados();
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            // Shift todos os elementos seguintes
            for (int j = i; j < num_alunos - 1; j++) {
                alunos[j] = alunos[j + 1];
            }
            num_alunos--;
            salvar_dados_alunos();
            printf("[DB-C] ✓ Aluno matrícula %d deletado\n", matricula);
            return 1;
        }
    }
    printf("[DB-C] ✗ Aluno matrícula %d não encontrado\n", matricula);
    return 0;
}

/**
 * Altera a matrícula de um aluno
 * Retorna: 1 se alterou, 0 se não encontrou, -1 se nova matrícula já existe
 */
EXPORT int alterar_matricula_aluno(int matricula_antiga, int matricula_nova) {
    carregar_dados();
    
    if (matricula_antiga == matricula_nova) return 1;
    
    // Verificar se nova matrícula já existe
    if (matricula_existe(matricula_nova)) {
        printf("[DB-C] ✗ Nova matrícula %d já existe\n", matricula_nova);
        return -1;
    }
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula_antiga) {
            alunos[i].matricula = matricula_nova;
            salvar_dados_alunos();
            printf("[DB-C] ✓ Matrícula alterada: %d → %d\n", matricula_antiga, matricula_nova);
            return 1;
        }
    }
    
    printf("[DB-C] ✗ Aluno com matrícula %d não encontrado\n", matricula_antiga);
    return 0;
}

// ==============================================================================
// FUNÇÕES EXPORTADAS - NOTAS (CRÍTICO PARA SINCRONIZAÇÃO)
// ==============================================================================

/**
 * Salva/atualiza as notas de um aluno
 * CORREÇÃO CRÍTICA: Esta função é a FONTE DE VERDADE para notas
 * 
 * Retorna: 1 se salvou, 0 se não encontrou a matrícula
 */
EXPORT int salvar_notas(int matricula, const Notas* novas_notas) {
    if (!novas_notas) {
        printf("[DB-C] ✗ ERRO: Ponteiro de notas nulo\n");
        return 0;
    }
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            // Atualizar notas
            alunos[i].notas = *novas_notas;
            
            // Salvar imediatamente
            salvar_dados_alunos();
            
            printf("[DB-C] ✓ Notas salvas - Matrícula %d: NP1=%.1f, NP2=%.1f, PIM=%.1f, Média=%.1f\n",
                   matricula, novas_notas->np1, novas_notas->np2, novas_notas->pim, novas_notas->media);
            
            return 1;
        }
    }
    
    printf("[DB-C] ✗ ERRO: Matrícula %d não encontrada para salvar notas\n", matricula);
    return 0;
}

/**
 * Busca as notas de um aluno
 * Retorna: 1 se encontrou, 0 caso contrário
 */
EXPORT int buscar_notas(int matricula, Notas* out_notas) {
    if (!out_notas) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            *out_notas = alunos[i].notas;
            printf("[DB-C] ✓ Notas recuperadas - Matrícula %d: NP1=%.1f, NP2=%.1f, PIM=%.1f, Média=%.1f\n",
                   matricula, out_notas->np1, out_notas->np2, out_notas->pim, out_notas->media);
            return 1;
        }
    }
    
    printf("[DB-C] ✗ Notas não encontradas para matrícula %d\n", matricula);
    return 0;
}

// ==============================================================================
// FUNÇÕES EXPORTADAS - PRESENÇAS
// ==============================================================================

/**
 * Adiciona um registro de presença para um aluno
 * Retorna: 1 se adicionou, 0 se falhou
 */
EXPORT int adicionar_presenca(int matricula, const Presenca* presenca) {
    if (!presenca) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            if (alunos[i].num_presencas >= 50) {
                printf("[DB-C] ✗ ERRO: Limite de presenças atingido (50) para matrícula %d\n", matricula);
                return 0;
            }
            
            alunos[i].presencas[alunos[i].num_presencas] = *presenca;
            alunos[i].num_presencas++;
            salvar_dados_alunos();
            printf("[DB-C] ✓ Presença adicionada - Matrícula %d, Data: %s, Presente: %d\n",
                   matricula, presenca->data, presenca->presente);
            return 1;
        }
    }
    
    printf("[DB-C] ✗ Matrícula %d não encontrada para adicionar presença\n", matricula);
    return 0;
}

/**
 * Lista todas as presenças de um aluno
 * Retorna: número de presenças encontradas
 */
EXPORT int listar_presencas(int matricula, Presenca* array_presencas, int max_len) {
    if (!array_presencas) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            int count = (alunos[i].num_presencas < max_len) ? alunos[i].num_presencas : max_len;
            for (int j = 0; j < count; j++) {
                array_presencas[j] = alunos[i].presencas[j];
            }
            return count;
        }
    }
    return 0;
}

/**
 * Busca presença de um aluno em uma data específica
 * Retorna: 1 se encontrou, 0 caso contrário
 */
EXPORT int buscar_presenca_por_data(int matricula, const char* data, Presenca* out_presenca) {
    if (!data || !out_presenca) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            for (int j = 0; j < alunos[i].num_presencas; j++) {
                if (strcmp(alunos[i].presencas[j].data, data) == 0) {
                    *out_presenca = alunos[i].presencas[j];
                    return 1;
                }
            }
        }
    }
    return 0;
}

// ==============================================================================
// FUNÇÕES EXPORTADAS - AVALIAÇÕES
// ==============================================================================

/**
 * Adiciona uma avaliação para um aluno
 * Retorna: 1 se adicionou, 0 se falhou
 */
EXPORT int adicionar_avaliacao(int matricula, const Avaliacao* avaliacao) {
    if (!avaliacao) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            if (alunos[i].num_avaliacoes >= 10) {
                printf("[DB-C] ✗ ERRO: Limite de avaliações atingido (10) para matrícula %d\n", matricula);
                return 0;
            }
            
            alunos[i].avaliacoes[alunos[i].num_avaliacoes] = *avaliacao;
            alunos[i].num_avaliacoes++;
            salvar_dados_alunos();
            printf("[DB-C] ✓ Avaliação adicionada - Matrícula %d, Data: %s, Tipo: %s, Nota: %.1f\n",
                   matricula, avaliacao->data, avaliacao->tipo, avaliacao->nota);
            return 1;
        }
    }
    
    printf("[DB-C] ✗ Matrícula %d não encontrada para adicionar avaliação\n", matricula);
    return 0;
}

/**
 * Lista todas as avaliações de um aluno
 * Retorna: número de avaliações encontradas
 */
EXPORT int listar_avaliacoes(int matricula, Avaliacao* array_avaliacoes, int max_len) {
    if (!array_avaliacoes) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            int count = (alunos[i].num_avaliacoes < max_len) ? alunos[i].num_avaliacoes : max_len;
            for (int j = 0; j < count; j++) {
                array_avaliacoes[j] = alunos[i].avaliacoes[j];
            }
            return count;
        }
    }
    return 0;
}

/**
 * Atualiza uma avaliação existente de um aluno
 * Retorna: 1 se atualizou, 0 se não encontrou
 */
EXPORT int atualizar_avaliacao(int matricula, const char* data, const Avaliacao* nova_avaliacao) {
    if (!data || !nova_avaliacao) return 0;
    
    carregar_dados();
    
    for (int i = 0; i < num_alunos; i++) {
        if (alunos[i].matricula == matricula) {
            for (int j = 0; j < alunos[i].num_avaliacoes; j++) {
                if (strcmp(alunos[i].avaliacoes[j].data, data) == 0) {
                    alunos[i].avaliacoes[j] = *nova_avaliacao;
                    salvar_dados_alunos();
                    printf("[DB-C] ✓ Avaliação atualizada - Matrícula %d, Data: %s\n", matricula, data);
                    return 1;
                }
            }
        }
    }
    
    printf("[DB-C] ✗ Avaliação não encontrada - Matrícula %d, Data: %s\n", matricula, data);
    return 0;
}

// ==============================================================================
// FUNÇÕES DE DEBUG E ESTATÍSTICAS
// ==============================================================================

/**
 * NOVA FUNÇÃO: Retorna estatísticas do banco de dados
 * Útil para debug e monitoramento
 */
EXPORT void imprimir_estatisticas() {
    carregar_dados();
    
    printf("\n");
    printf("╔════════════════════════════════════════╗\n");
    printf("║   ESTATÍSTICAS DO BANCO DE DADOS C     ║\n");
    printf("╠════════════════════════════════════════╣\n");
    printf("║ Turmas:  %3d / %3d (%.1f%%)           ║\n", 
           num_turmas, MAX_TURMAS, (num_turmas * 100.0) / MAX_TURMAS);
    printf("║ Alunos:  %3d / %3d (%.1f%%)           ║\n", 
           num_alunos, MAX_ALUNOS, (num_alunos * 100.0) / MAX_ALUNOS);
    printf("╠════════════════════════════════════════╣\n");
    printf("║ Arquivos:                              ║\n");
    printf("║   %s: %s                    ║\n", 
           TURMAS_DB_FILE, turmas ? "OK" : "ERRO");
    printf("║   %s: %s                    ║\n", 
           ALUNOS_DB_FILE, alunos ? "OK" : "ERRO");
    printf("╚════════════════════════════════════════╝\n");
    printf("\n");
}

/**
 * NOVA FUNÇÃO: Força recarga dos dados do disco
 * Útil quando arquivos são modificados externamente
 */
EXPORT void forcar_recarga() {
    printf("[DB-C] Forçando recarga dos dados...\n");
    dados_carregados = 0;
    num_turmas = 0;
    num_alunos = 0;
    carregar_dados();
    printf("[DB-C] ✓ Recarga completa\n");
}

/**
 * NOVA FUNÇÃO: Limpa todo o banco de dados (USE COM CUIDADO!)
 * Remove todos os dados de memória e dos arquivos
 */
EXPORT int limpar_banco_completo() {
    printf("[DB-C] ⚠ ATENÇÃO: Limpando TODOS os dados!\n");
    
    num_turmas = 0;
    num_alunos = 0;
    
    salvar_dados_turmas();
    salvar_dados_alunos();
    
    printf("[DB-C] ✓ Banco de dados limpo\n");
    return 1;
}