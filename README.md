# Finora — controle de gastos

Site estático (HTML, CSS e JavaScript) para controle de gastos pessoais. Roda no **GitHub Pages**. Login e dados ficam no **Supabase**, com cada usuário vendo somente os próprios lançamentos.

A autenticação é **somente login e senha**. Não há Google, GitHub, telefone, Magic Link nem recuperação por e-mail.

## 1. Criar o projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com) e crie um projeto.
2. Abra **SQL Editor** → New query.
3. Cole o conteúdo de `sql/schema.sql` e execute.
   Isso cria as tabelas `profiles` e `transactions` e ativa **Row Level Security** (RLS): ninguém acessa dados de outra conta, mesmo conhecendo a chave pública do frontend.
4. Em **Authentication → Providers**:
   - Deixe **Email** ativado (é o provedor usado internamente para login + senha).
   - Desative **Confirm email**.
   - Desative **Magic Link** se aparecer.
   - Deixe **Google, GitHub, Phone** e qualquer outro provedor desligados.
5. Em **Project Settings → API**, copie a URL e a chave **anon public**.

## 2. Colar a URL e a chave anônima

1. No Supabase: **Project Settings → API**.
2. Copie **Project URL** e a chave **anon public** (nunca a `service_role`).
3. Abra `js/config.js` e substitua:

```js
window.APP_CONFIG = {
  supabaseUrl: "https://xxxxxxxx.supabase.co",
  supabaseAnonKey: "eyJhbGciOi..."
};
```

A chave `anon` é pública por desenho. A proteção real são as políticas RLS do `schema.sql`.

## 3. Publicar no GitHub Pages pelo terminal

O site publicado é [https://ejuanoli.github.io/UNIP_ADS/](https://ejuanoli.github.io/UNIP_ADS/).

1. Instale o Git: [https://git-scm.com/download/win](https://git-scm.com/download/win) (marque “Git from the command line”).
2. Abra o **Git Bash** ou o PowerShell **já com o Git no PATH**.
3. Na pasta do projeto:

```bash
cd /c/Projetos/Financeiro
git init
git add .
git commit -m "Atualiza o Finora"
git branch -M main
git remote add origin https://github.com/ejuanoli/UNIP_ADS.git
git push -u origin main
```

Se o `remote` já existir, use só:

```bash
git add .
git commit -m "Atualiza o Finora"
git push
```

Se o GitHub pedir login, use um **Personal Access Token** no lugar da senha: GitHub → Settings → Developer settings → Personal access tokens.

4. Em **Settings → Pages**, a branch deve ser `main` e a pasta `/ (root)`.
5. No Supabase, em **Authentication → URL Configuration**, coloque `https://ejuanoli.github.io/UNIP_ADS/` como Site URL.

## 4. Uso

- **Criar conta** com nome, login e senha.
- **Entrar** só com login e senha.
- Registrar **entradas** e **saídas** com categoria, descrição e data.
- Navegar pelos meses, filtrar, editar, excluir e exportar CSV do mês.

## Segurança

- Apenas a chave **anon** entra no site.
- RLS garante `auth.uid() = user_id` em leitura, criação, edição e exclusão.
- Senhas ficam no Auth do Supabase, não na tabela de lançamentos.
- O site não usa borda lateral colorida nem barra lateral; o layout é centralizado, com fundo creme e verde-sálvia.
