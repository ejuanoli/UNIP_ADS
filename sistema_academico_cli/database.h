#ifndef DATABASE_H
#define DATABASE_H

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

// Estruturas
typedef struct {
    int id;
    char nome_disciplina[100];
    char nome_professor[100];
} Turma;

typedef struct {
    float nota;
    char comentario[500];
    char data[11];  // formato DD/MM/YYYY
} Avaliacao;

typedef struct {
    char data[11];  // formato DD/MM/YYYY
    int presente;
} Presenca;

typedef struct {
    float np1;
    float np2;
    float pim;
    float media;
} Notas;

typedef struct {
    int id_turma;
    int matricula;
    char nome[100];
    Notas notas;
    Avaliacao avaliacoes[10];  // máximo de 10 avaliações por aluno
    Presenca presencas[50];    // máximo de 50 aulas por disciplina
    int num_avaliacoes;
    int num_presencas;
} Aluno;

// Protótipos das Funções

// CORRIGIDO: salvar_turma e salvar_aluno agora aceitam ponteiros (const Turma*)
EXPORT void salvar_turma(const Turma* nova_turma);
EXPORT void salvar_aluno(const Aluno* novo_aluno);

// (O resto das funções já usava o padrão correto ou tipos primitivos)
EXPORT int turma_existe(int id);
EXPORT int matricula_existe(int matricula);
EXPORT int listar_turmas(Turma* array_turmas, int max_len);
EXPORT int listar_alunos_por_turma(int id_turma, Aluno* array_alunos, int max_len);
EXPORT int buscar_turma_por_id(int id, Turma* out_turma);
EXPORT int buscar_aluno_por_matricula(int matricula, Aluno* out_aluno);
EXPORT int atualizar_turma(int id_turma, const char* nova_disciplina, const char* novo_professor);
EXPORT int atualizar_aluno(int matricula, const char* novo_nome);
EXPORT int alterar_id_turma(int id_antigo, int id_novo);
EXPORT int alterar_matricula_aluno(int matricula_antiga, int matricula_nova);
EXPORT int deletar_turma(int id_turma);
EXPORT int deletar_aluno(int matricula);

// Novas funções para notas
EXPORT int salvar_notas(int matricula, const Notas* notas);
EXPORT int buscar_notas(int matricula, Notas* out_notas);

// Novas funções para presenças
EXPORT int adicionar_presenca(int matricula, const Presenca* presenca);
EXPORT int listar_presencas(int matricula, Presenca* array_presencas, int max_len);
EXPORT int buscar_presenca_por_data(int matricula, const char* data, Presenca* out_presenca);

// Novas funções para avaliações
EXPORT int adicionar_avaliacao(int matricula, const Avaliacao* avaliacao);
EXPORT int listar_avaliacoes(int matricula, Avaliacao* array_avaliacoes, int max_len);
EXPORT int atualizar_avaliacao(int matricula, const char* data, const Avaliacao* nova_avaliacao);

#endif // DATABASE_H