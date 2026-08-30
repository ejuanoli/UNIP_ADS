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

## 3. Publicar no GitHub Pages

1. Crie um repositório no GitHub e envie esta pasta.
2. Em **Settings → Pages**:
   - Source: **Deploy from a branch**
   - Branch: `main` (ou `master`), pasta `/ (root)`
3. Espere o deploy e abra `https://SEU_USUARIO.github.io/NOME_DO_REPO/`

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
