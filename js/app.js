(function () {
  "use strict";

  const EXPENSE_CATEGORIES = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Educação",
    "Lazer",
    "Compras",
    "Contas",
    "Outros"
  ];

  const INCOME_CATEGORIES = ["Salário", "Freelance", "Investimentos", "Presente", "Outros"];

  const CATEGORY_ICON = {
    Alimentação: "🍽️",
    Transporte: "🚌",
    Moradia: "🏠",
    Saúde: "💊",
    Educação: "📚",
    Lazer: "🎬",
    Compras: "🛍️",
    Contas: "📄",
    Salário: "💼",
    Freelance: "💻",
    Investimentos: "📈",
    Presente: "🎁",
    Outros: "✨"
  };

  const MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro"
  ];

  const DEMO_STORE = "finora-demo-v1";
  const LIST_PREVIEW = 5;

  const els = {
    loading: document.getElementById("loading"),
    toast: document.getElementById("toast"),
    setup: document.getElementById("view-setup"),
    auth: document.getElementById("view-auth"),
    app: document.getElementById("view-app"),
    formLogin: document.getElementById("form-login"),
    formSignup: document.getElementById("form-signup"),
    authMessage: document.getElementById("auth-message"),
    greeting: document.getElementById("greeting"),
    secSite: document.getElementById("sec-site"),
    secUser: document.getElementById("sec-user"),
    secDb: document.getElementById("sec-db"),
    monthLabel: document.getElementById("month-label"),
    sumBalance: document.getElementById("sum-balance"),
    sumIncome: document.getElementById("sum-income"),
    sumExpense: document.getElementById("sum-expense"),
    sumInsight: document.getElementById("sum-insight"),
    sumIncomeCount: document.getElementById("sum-income-count"),
    sumExpenseCount: document.getElementById("sum-expense-count"),
    txList: document.getElementById("tx-list"),
    txListFull: document.getElementById("tx-list-full"),
    btnTxMore: document.getElementById("btn-tx-more"),
    modalList: document.getElementById("modal-list"),
    breakdown: document.getElementById("category-breakdown"),
    chartFlow: document.getElementById("chart-flow"),
    search: document.getElementById("search"),
    filterType: document.getElementById("filter-type"),
    filterCategory: document.getElementById("filter-category"),
    modal: document.getElementById("modal"),
    confirm: document.getElementById("confirm"),
    formTx: document.getElementById("form-tx"),
    txId: document.getElementById("tx-id"),
    txAmount: document.getElementById("tx-amount"),
    txCategory: document.getElementById("tx-category"),
    txDescription: document.getElementById("tx-description"),
    txDate: document.getElementById("tx-date"),
    modalTitle: document.getElementById("modal-title"),
    btnDeleteTx: document.getElementById("btn-delete-tx"),
    btnSaveTx: document.getElementById("btn-save-tx")
  };

  let supabaseClient = null;
  let currentUser = null;
  let currentName = "";
  let transactions = [];
  let cursor = startOfMonth(new Date());
  let pendingDeleteId = null;
  let toastTimer = null;
  let demoMode = false;
  let dbInfo = { kind: "", label: "Banco" };
  let allUserTransactions = [];

  function isConfigured() {
    const cfg = window.APP_CONFIG || {};
    const url = String(cfg.supabaseUrl || "");
    const key = String(cfg.supabaseAnonKey || "");
    return (
      url.startsWith("https://") &&
      key.length > 40 &&
      !url.includes("COLE_AQUI") &&
      !key.includes("COLE_AQUI")
    );
  }

  function showView(name) {
    if (els.setup) els.setup.classList.toggle("hidden", name !== "setup");
    if (els.auth) els.auth.classList.toggle("hidden", name !== "auth");
    if (els.app) els.app.classList.toggle("hidden", name !== "app");
  }

  function setLoading(on) {
    if (els.loading) els.loading.classList.toggle("hidden", !on);
  }

  function renderSecurity() {
    if (!els.secSite || !els.secUser) return;
    const host = location.hostname;
    const local = host === "localhost" || host === "127.0.0.1";
    if (location.protocol === "https:") {
      els.secSite.textContent = "Dados criptografados";
      els.secSite.className = "sec-badge is-ok";
    } else if (local) {
      els.secSite.textContent = "Dados neste computador";
      els.secSite.className = "sec-badge is-warn";
    } else {
      els.secSite.textContent = "Dados sem criptografia";
      els.secSite.className = "sec-badge is-bad";
    }

    if (demoMode) {
      els.secUser.textContent = "Banco local (demonstração)";
      els.secUser.className = "sec-badge is-warn";
    } else if (currentUser) {
      els.secUser.textContent = "Banco de dados conectado";
      els.secUser.className = "sec-badge is-ok";
    } else {
      els.secUser.textContent = "Banco de dados desconectado";
      els.secUser.className = "sec-badge is-bad";
    }

    if (els.secDb) {
      els.secDb.textContent = dbInfo.label || "Banco";
      els.secDb.className =
        "sec-badge" +
        (dbInfo.kind === "ok" ? " is-ok" : dbInfo.kind === "warn" ? " is-warn" : dbInfo.kind === "bad" ? " is-bad" : "");
    }
  }

  function toast(message) {
    if (!els.toast) return;
    els.toast.textContent = message;
    els.toast.classList.add("is-on");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => els.toast.classList.remove("is-on"), 2800);
  }

  function setAuthMessage(text, isError) {
    els.authMessage.hidden = !text;
    els.authMessage.textContent = text || "";
    els.authMessage.classList.toggle("is-error", Boolean(isError));
  }

  function formatBRL(value) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL"
    }).format(Number(value) || 0);
  }

  function parseBRL(raw) {
    let cleaned = String(raw).trim().replace(/[R$\s]/g, "");
    if (!cleaned) return NaN;
    if (cleaned.includes(",")) cleaned = cleaned.replace(/\./g, "").replace(",", ".");
    const n = Number(cleaned);
    return Number.isFinite(n) ? n : NaN;
  }

  function startOfMonth(date) {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  }

  function monthRange(date) {
    const start = startOfMonth(date);
    const end = new Date(start.getFullYear(), start.getMonth() + 1, 0);
    return {
      start: toISODate(start),
      end: toISODate(end)
    };
  }

  function toISODate(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }

  function parseISODate(iso) {
    const [y, m, d] = String(iso || "").slice(0, 10).split("-").map(Number);
    return new Date(y, m - 1, d);
  }

  function formatShortDate(iso) {
    const date = parseISODate(iso);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleDateString("pt-BR");
  }

  function txDate(t) {
    return String(t && t.occurred_on ? t.occurred_on : "").slice(0, 10);
  }

  function normalizeTx(t) {
    return Object.assign({}, t, {
      occurred_on: txDate(t),
      amount: Number(t.amount)
    });
  }

  function setDbInfo(kind, label) {
    dbInfo = { kind: kind || "", label: label || "Banco" };
  }

  function plural(n, one, many) {
    return `${n} ${n === 1 ? one : many}`;
  }

  function currentType() {
    const checked = document.querySelector('input[name="tx-type"]:checked');
    return checked ? checked.value : "expense";
  }

  function categoriesFor(type) {
    return type === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
  }

  function fillCategories(select, type, selected) {
    const cats = categoriesFor(type);
    select.innerHTML = "";
    cats.forEach((cat) => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      if (cat === selected) opt.selected = true;
      select.appendChild(opt);
    });
  }

  function fillFilterCategories() {
    const previous = els.filterCategory.value || "all";
    els.filterCategory.innerHTML = "";
    const all = document.createElement("option");
    all.value = "all";
    all.textContent = "Todas as categorias";
    els.filterCategory.appendChild(all);
    const used = [...new Set(transactions.map((t) => t.category))].sort();
    used.forEach((cat) => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      els.filterCategory.appendChild(opt);
    });
    els.filterCategory.value = used.includes(previous) ? previous : "all";
  }

  function showAuthTab(tab) {
    document.querySelectorAll("[data-auth-tab]").forEach((btn) => {
      const active = btn.dataset.authTab === tab;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-selected", String(active));
    });
    els.formLogin.classList.toggle("hidden", tab !== "login");
    els.formSignup.classList.toggle("hidden", tab !== "signup");
    setAuthMessage("");
  }

  function normalizeLogin(raw) {
    return String(raw || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, "");
  }

  function isValidLogin(login) {
    return /^[a-z0-9._-]{3,40}$/.test(login);
  }

  function loginToEmail(login) {
    const host = String(window.APP_CONFIG.supabaseUrl || "")
      .replace(/^https?:\/\//, "")
      .split("/")[0];
    return `${login}@${host}`;
  }

  function loginEmails(login) {
    if (String(login).includes("@")) return [login];
    return [...new Set([loginToEmail(login), `${login}@login.finora.app`])];
  }

  async function signInWithLogin(login, password) {
    let lastError = null;
    for (const email of loginEmails(login)) {
      const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
      if (!error) return { data, error: null };
      lastError = error;
    }
    return { data: null, error: lastError };
  }

  function demoDay(day) {
    const now = new Date();
    const last = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    return toISODate(new Date(now.getFullYear(), now.getMonth(), Math.min(day, last)));
  }

  function seedDemo() {
    return {
      profile: { id: "demo-user", name: "Maria" },
      transactions: [
        { id: "d1", user_id: "demo-user", type: "income", amount: 5200, category: "Salário", description: "Salário", occurred_on: demoDay(5), created_at: "" },
        { id: "d2", user_id: "demo-user", type: "income", amount: 480, category: "Freelance", description: "Projeto extra", occurred_on: demoDay(18), created_at: "" },
        { id: "d3", user_id: "demo-user", type: "expense", amount: 186.4, category: "Alimentação", description: "Feira da semana", occurred_on: demoDay(8), created_at: "" },
        { id: "d4", user_id: "demo-user", type: "expense", amount: 89.9, category: "Transporte", description: "Cartão de ônibus", occurred_on: demoDay(9), created_at: "" },
        { id: "d5", user_id: "demo-user", type: "expense", amount: 1450, category: "Moradia", description: "Aluguel", occurred_on: demoDay(3), created_at: "" },
        { id: "d6", user_id: "demo-user", type: "expense", amount: 62.5, category: "Lazer", description: "Cinema", occurred_on: demoDay(21), created_at: "" },
        { id: "d7", user_id: "demo-user", type: "expense", amount: 214.3, category: "Contas", description: "Internet e celular", occurred_on: demoDay(12), created_at: "" }
      ]
    };
  }

  function demoState() {
    try {
      const raw = localStorage.getItem(DEMO_STORE);
      if (raw) return JSON.parse(raw);
    } catch (err) {
      /* ignore */
    }
    const seeded = seedDemo();
    localStorage.setItem(DEMO_STORE, JSON.stringify(seeded));
    return seeded;
  }

  function saveDemo(state) {
    localStorage.setItem(DEMO_STORE, JSON.stringify(state));
  }

  function setDemoChrome(on) {
    demoMode = on;
    const banner = document.getElementById("demo-banner");
    if (banner) banner.classList.toggle("hidden", !on);
    sessionStorage.setItem("finora-demo", on ? "1" : "0");
  }

  async function enterDemo(name) {
    setDemoChrome(true);
    const state = demoState();
    if (name) {
      state.profile.name = name;
      saveDemo(state);
    }
    currentUser = { id: "demo-user", email: "demo@finora.local" };
    currentName = state.profile.name;
    showView("app");
    await fetchMonth();
  }

  async function loadProfile(user) {
    if (demoMode) {
      return demoState().profile.name;
    }

    const { data, error } = await supabaseClient
      .from("profiles")
      .select("name")
      .eq("id", user.id)
      .maybeSingle();

    if (error) throw error;
    if (data?.name) return data.name;

    const fallback = user.user_metadata?.name || String(user.email || "usuario").split("@")[0];
    await supabaseClient.from("profiles").upsert({ id: user.id, name: fallback });
    return fallback;
  }

  async function fetchMonth() {
    const { start, end } = monthRange(cursor);
    if (demoMode) {
      allUserTransactions = demoState().transactions.map(normalizeTx);
      transactions = allUserTransactions
        .filter((t) => t.occurred_on >= start && t.occurred_on <= end)
        .sort((a, b) => (a.occurred_on < b.occurred_on ? 1 : a.occurred_on > b.occurred_on ? -1 : 0));
      setDbInfo("warn", "Banco local");
      renderApp();
      return;
    }

    if (!currentUser || !currentUser.id) {
      throw new Error("Sessão expirada. Entre de novo.");
    }

    let result = await supabaseClient
      .from("transactions")
      .select("*")
      .eq("user_id", currentUser.id)
      .order("occurred_on", { ascending: false });

    if (result.error) {
      result = await supabaseClient.from("transactions").select("*").order("occurred_on", { ascending: false });
    }

    if (result.error) {
      allUserTransactions = [];
      transactions = [];
      const msg = result.error.message || "Não foi possível ler os lançamentos.";
      const lower = msg.toLowerCase();
      if (lower.includes("relation") || lower.includes("schema cache") || lower.includes("does not exist")) {
        setDbInfo("bad", "Falta o schema");
      } else if (lower.includes("permission") || lower.includes("rls") || lower.includes("denied")) {
        setDbInfo("bad", "Sem permissão");
      } else {
        setDbInfo("bad", "Banco: erro");
      }
      renderApp();
      throw new Error(msg);
    }

    allUserTransactions = (result.data || [])
      .map(normalizeTx)
      .filter((t) => !t.user_id || t.user_id === currentUser.id);
    transactions = allUserTransactions
      .filter((t) => t.occurred_on >= start && t.occurred_on <= end)
      .sort((a, b) => {
        if (a.occurred_on !== b.occurred_on) return a.occurred_on < b.occurred_on ? 1 : -1;
        return String(a.created_at || "") < String(b.created_at || "") ? 1 : -1;
      });

    if (!allUserTransactions.length) {
      setDbInfo("ok", "Nenhum lançamento neste mês");
    } else if (!transactions.length) {
      setDbInfo("ok", `${allUserTransactions.length} ${allUserTransactions.length === 1 ? "lançamento no banco" : "lançamentos no banco"}`);
    } else {
      setDbInfo("ok", `${transactions.length} ${transactions.length === 1 ? "lançamento neste mês" : "lançamentos neste mês"}`);
    }
    renderApp();
  }

  async function saveTransaction(payload, id) {
    if (demoMode) {
      const state = demoState();
      if (id) {
        state.transactions = state.transactions.map((t) => (t.id === id ? { ...t, ...payload } : t));
      } else {
        state.transactions.unshift({
          ...payload,
          id: `d${Date.now()}`,
          created_at: new Date().toISOString()
        });
      }
      saveDemo(state);
      return;
    }

    const query = id
      ? supabaseClient.from("transactions").update(payload).eq("id", id).eq("user_id", currentUser.id)
      : supabaseClient.from("transactions").insert(payload);
    const { error } = await query;
    if (error) throw new Error(error.message || error.details || "Erro ao salvar o lançamento.");
  }

  async function removeTransaction(id) {
    if (demoMode) {
      const state = demoState();
      state.transactions = state.transactions.filter((t) => t.id !== id);
      saveDemo(state);
      return;
    }
    const { error } = await supabaseClient
      .from("transactions")
      .delete()
      .eq("id", id)
      .eq("user_id", currentUser.id);
    if (error) throw error;
  }

  function filteredTransactions() {
    const q = els.search.value.trim().toLowerCase();
    const type = els.filterType.value;
    const cat = els.filterCategory.value;
    return transactions.filter((t) => {
      if (type !== "all" && t.type !== type) return false;
      if (cat !== "all" && t.category !== cat) return false;
      if (q && !(t.description || "").toLowerCase().includes(q) && !t.category.toLowerCase().includes(q)) {
        return false;
      }
      return true;
    });
  }

  function renderApp() {
    try {
    els.greeting.textContent = currentName ? `Olá, ${currentName}` : "Olá";
    els.monthLabel.textContent = `${MONTHS[cursor.getMonth()]} ${cursor.getFullYear()}`;
    renderSecurity();

    const incomeItems = transactions.filter((t) => t.type === "income");
    const expenseItems = transactions.filter((t) => t.type === "expense");
    const income = incomeItems.reduce((s, t) => s + Number(t.amount), 0);
    const expense = expenseItems.reduce((s, t) => s + Number(t.amount), 0);
    const balance = income - expense;

    els.sumBalance.textContent = formatBRL(balance);
    els.sumIncome.textContent = formatBRL(income);
    els.sumExpense.textContent = formatBRL(expense);
    els.sumIncomeCount.textContent = plural(incomeItems.length, "lançamento", "lançamentos");
    els.sumExpenseCount.textContent = plural(expenseItems.length, "lançamento", "lançamentos");

    if (income === 0 && expense === 0) {
      els.sumInsight.textContent = allUserTransactions.length
        ? "Não há lançamentos neste mês. Use as setas para ver outros meses."
        : "Comece registrando um lançamento.";
    } else if (balance >= 0) {
      els.sumInsight.textContent = "Você fechou o mês no positivo.";
    } else {
      els.sumInsight.textContent = "As saídas passaram das entradas neste mês.";
    }

    fillFilterCategories();
    renderList();
    renderBreakdown(expenseItems, expense);
    renderCharts(income, expense);
    } catch (err) {
      toast(err.message || "Não foi possível atualizar a tela.");
    }
  }

  function fillTxList(container, items, withDays) {
    container.innerHTML = "";
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = transactions.length
        ? "Nenhum lançamento com esses filtros."
        : allUserTransactions.length
          ? "Nenhum lançamento neste mês."
          : "Nenhum lançamento neste mês.";
      container.appendChild(empty);
      return;
    }

    let lastDay = "";
    items.forEach((t) => {
      const dayKey = txDate(t);
      if (withDays && dayKey !== lastDay) {
        lastDay = dayKey;
        const day = document.createElement("div");
        day.className = "tx-day";
        day.textContent = parseISODate(dayKey).toLocaleDateString("pt-BR", {
          weekday: "long",
          day: "2-digit",
          month: "short"
        });
        container.appendChild(day);
      }

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "tx-item";
      btn.addEventListener("click", () => {
        closeListModal();
        openModal(t);
      });

      const icon = document.createElement("span");
      icon.className = "tx-icon";
      icon.textContent = CATEGORY_ICON[t.category] || "✨";

      const info = document.createElement("span");
      const title = document.createElement("b");
      title.textContent = t.description || t.category;
      const meta = document.createElement("small");
      meta.textContent = t.category;
      info.append(title, meta);

      const right = document.createElement("span");
      right.className = "tx-right";
      const dateEl = document.createElement("small");
      dateEl.className = "tx-date";
      dateEl.textContent = formatShortDate(dayKey);
      const value = document.createElement("strong");
      value.className = t.type === "income" ? "is-income" : "is-expense";
      value.textContent = `${t.type === "income" ? "+" : "−"} ${formatBRL(t.amount)}`;
      right.append(dateEl, value);

      btn.append(icon, info, right);
      container.appendChild(btn);
    });
  }

  function renderList() {
    const items = filteredTransactions();
    fillTxList(els.txList, items.slice(0, LIST_PREVIEW), false);
    if (els.btnTxMore) {
      const extra = items.length - LIST_PREVIEW;
      els.btnTxMore.classList.toggle("hidden", extra <= 0);
      els.btnTxMore.textContent =
        extra > 0 ? `Ver todos os ${items.length} lançamentos` : "Ver todos os lançamentos";
    }
    if (els.modalList && !els.modalList.classList.contains("hidden") && els.txListFull) {
      fillTxList(els.txListFull, items, true);
    }
  }

  function openListModal() {
    if (!els.modalList || !els.txListFull) return;
    fillTxList(els.txListFull, filteredTransactions(), true);
    els.modalList.classList.remove("hidden");
  }

  function closeListModal() {
    if (els.modalList) els.modalList.classList.add("hidden");
  }

  function renderBreakdown(expenseItems, total) {
    els.breakdown.innerHTML = "";
    if (!expenseItems.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "As saídas do mês aparecem aqui.";
      els.breakdown.appendChild(empty);
      return;
    }

    const map = {};
    expenseItems.forEach((t) => {
      map[t.category] = (map[t.category] || 0) + Number(t.amount);
    });

    Object.entries(map)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .forEach(([cat, amount]) => {
        const row = document.createElement("div");
        row.className = "bar-row";
        const meta = document.createElement("div");
        meta.className = "bar-meta";
        const name = document.createElement("span");
        name.textContent = `${CATEGORY_ICON[cat] || ""} ${cat}`.trim();
        const val = document.createElement("span");
        val.textContent = formatBRL(amount);
        meta.append(name, val);
        const track = document.createElement("div");
        track.className = "bar-track";
        const fill = document.createElement("div");
        fill.className = "bar-fill";
        fill.style.width = `${Math.max(6, total ? (amount / total) * 100 : 0)}%`;
        track.appendChild(fill);
        row.append(meta, track);
        els.breakdown.appendChild(row);
      });
  }

  function appendHBar(parent, label, value, max, kind) {
    const row = document.createElement("div");
    row.className = "hbar";
    const name = document.createElement("span");
    name.textContent = label;
    const track = document.createElement("div");
    track.className = "hbar-track";
    const fill = document.createElement("div");
    fill.className = "hbar-fill " + kind;
    const pct = max > 0 ? Math.max(3, (value / max) * 100) : 3;
    fill.style.width = (value > 0 ? pct : 0) + "%";
    track.appendChild(fill);
    const val = document.createElement("strong");
    val.className = kind === "income" ? "is-income" : "is-expense";
    val.textContent = formatBRL(value);
    row.append(name, track, val);
    parent.appendChild(row);
  }

  function renderCharts(income, expense) {
    if (!els.chartFlow) return;
    els.chartFlow.innerHTML = "";

    const used = income > 0 ? (expense / income) * 100 : expense > 0 ? 100 : 0;
    const meter = document.createElement("div");
    meter.className = "meter";
    const track = document.createElement("div");
    track.className = "meter-track";
    const fill = document.createElement("div");
    fill.className = "meter-fill";
    fill.style.width = Math.min(100, used) + "%";
    track.appendChild(fill);
    const note = document.createElement("p");
    if (!income && !expense) {
      note.textContent = "Registre um lançamento para ver o comparativo.";
    } else if (!income) {
      note.textContent = "Há saídas, mas ainda não há entradas neste mês.";
    } else {
      note.textContent = `As saídas representam ${used.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% das entradas.`;
    }
    meter.append(track, note);
    els.chartFlow.appendChild(meter);

    const max = Math.max(income, expense, 1);
    appendHBar(els.chartFlow, "Entradas", income, max, "income");
    appendHBar(els.chartFlow, "Saídas", expense, max, "expense");
  }

  function openModal(tx) {
    els.formTx.reset();
    const isEdit = Boolean(tx);
    els.modalTitle.textContent = isEdit ? "Editar lançamento" : "Novo lançamento";
    els.btnDeleteTx.classList.toggle("hidden", !isEdit);
    els.txId.value = tx?.id || "";
    const type = tx?.type === "income" ? "income" : "expense";
    const typeInput = document.querySelector(`input[name="tx-type"][value="${type}"]`);
    if (typeInput) typeInput.checked = true;
    fillCategories(els.txCategory, type, tx?.category);
    els.txAmount.value = tx ? Number(tx.amount).toFixed(2).replace(".", ",") : "";
    els.txDescription.value = tx?.description || "";
    els.txDate.value = tx ? txDate(tx) : toISODate(new Date());
    els.modal.classList.remove("hidden");
    els.txAmount.focus();
  }

  function closeModal() {
    els.modal.classList.add("hidden");
  }

  async function enterApp(user) {
    currentUser = user;
    currentName =
      (user && user.user_metadata && user.user_metadata.name) ||
      String((user && user.email) || "Usuário").split("@")[0];
    try {
      currentName = await loadProfile(user);
      await safeFetch();
      showView("app");
    } catch (err) {
      toast(err.message || "Não foi possível abrir o painel.");
      showView("app");
    } finally {
      setLoading(false);
    }
  }

  function busy(button, on) {
    if (!button) return;
    button.disabled = on;
  }

  function exportCsv() {
    if (!transactions.length) {
      toast("Não há lançamentos neste mês para exportar.");
      return;
    }
    const header = ["data", "tipo", "categoria", "descricao", "valor"];
    const rows = transactions.map((t) => [
      t.occurred_on,
      t.type === "income" ? "entrada" : "saida",
      t.category,
      `"${String(t.description || "").replace(/"/g, '""')}"`,
      String(t.amount).replace(".", ",")
    ]);
    const csv = [header.join(";"), ...rows.map((r) => r.join(";"))].join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `finora-${cursor.getFullYear()}-${String(cursor.getMonth() + 1).padStart(2, "0")}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function bindEvents() {
    document.querySelectorAll("[data-auth-tab]").forEach((btn) => {
      btn.addEventListener("click", () => showAuthTab(btn.dataset.authTab));
    });

    document.querySelectorAll("[data-toggle-password]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const input = document.getElementById(btn.dataset.togglePassword);
        const hidden = input.type === "password";
        input.type = hidden ? "text" : "password";
        btn.textContent = hidden ? "ocultar" : "ver";
      });
    });

    document.getElementById("btn-demo").addEventListener("click", () => {
      setDemoChrome(true);
      showView("auth");
      showAuthTab("login");
    });

    els.formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      const login = normalizeLogin(document.getElementById("login-user").value);
      if (!isValidLogin(login)) {
        setAuthMessage("Use um login de 3 a 40 caracteres: letras, números, ponto, _ ou -.", true);
        return;
      }
      if (demoMode || !isConfigured()) {
        await enterDemo();
        return;
      }
      const button = document.getElementById("btn-login");
      busy(button, true);
      setAuthMessage("");
      const { error } = await signInWithLogin(login, document.getElementById("login-password").value);
      busy(button, false);
      if (error) setAuthMessage(friendlyAuthError(error), true);
    });

    els.formSignup.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("signup-name").value.trim();
      const login = normalizeLogin(document.getElementById("signup-user").value);
      if (!isValidLogin(login)) {
        setAuthMessage("Use um login de 3 a 40 caracteres: letras, números, ponto, _ ou -.", true);
        return;
      }
      if (demoMode || !isConfigured()) {
        await enterDemo(name || "Maria");
        return;
      }
      const button = document.getElementById("btn-signup");
      busy(button, true);
      setAuthMessage("");
      const password = document.getElementById("signup-password").value;
      const { data, error } = await supabaseClient.auth.signUp({
        email: loginToEmail(login),
        password,
        options: { data: { name, login } }
      });
      busy(button, false);
      if (error) {
        setAuthMessage(friendlyAuthError(error), true);
        return;
      }
      if (data.session) {
        toast("Conta criada.");
        return;
      }
      setAuthMessage("A conta foi criada, mas o login automático está bloqueado. No Supabase: Authentication → Providers → Email → desative Confirm email.");
    });

    document.getElementById("btn-logout").addEventListener("click", async () => {
      currentUser = null;
      transactions = [];
      allUserTransactions = [];
      if (demoMode) {
        showView("auth");
        showAuthTab("login");
        setAuthMessage("Demonstração: entre de novo para continuar olhando o site.");
        return;
      }
      try {
        if (supabaseClient) await supabaseClient.auth.signOut();
      } catch (err) {
        console.error(err);
      }
      showView("auth");
      showAuthTab("login");
    });

    document.getElementById("btn-prev-month").addEventListener("click", async () => {
      cursor = new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1);
      await safeFetch();
    });
    document.getElementById("btn-next-month").addEventListener("click", async () => {
      cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1);
      await safeFetch();
    });
    document.getElementById("btn-this-month").addEventListener("click", async () => {
      cursor = startOfMonth(new Date());
      await safeFetch();
    });

    document.getElementById("btn-new").addEventListener("click", () => openModal(null));
    const fab = document.getElementById("btn-new-fab");
    if (fab) fab.addEventListener("click", () => openModal(null));
    document.getElementById("btn-close-modal").addEventListener("click", closeModal);
    els.modal.addEventListener("click", (e) => {
      if (e.target === els.modal) closeModal();
    });

    document.querySelectorAll('input[name="tx-type"]').forEach((radio) => {
      radio.addEventListener("change", () => fillCategories(els.txCategory, currentType()));
    });

    els.search.addEventListener("input", renderList);
    els.filterType.addEventListener("change", renderList);
    els.filterCategory.addEventListener("change", renderList);
    document.getElementById("btn-export").addEventListener("click", exportCsv);
    if (els.btnTxMore) els.btnTxMore.addEventListener("click", openListModal);
    const btnCloseList = document.getElementById("btn-close-list");
    if (btnCloseList) btnCloseList.addEventListener("click", closeListModal);
    if (els.modalList) {
      els.modalList.addEventListener("click", (e) => {
        if (e.target === els.modalList) closeListModal();
      });
    }

    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape") return;
      els.confirm.classList.add("hidden");
      closeListModal();
      closeModal();
    });

    els.formTx.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!currentUser || !currentUser.id) {
        toast("Sessão expirada. Entre de novo.");
        showView("auth");
        return;
      }
      const amount = parseBRL(els.txAmount.value);
      if (!Number.isFinite(amount) || amount <= 0) {
        toast("Informe um valor válido maior que zero.");
        return;
      }
      if (amount > 9999999999.99) {
        toast("Valor grande demais para salvar.");
        return;
      }
      const type = currentType();
      const category = els.txCategory.value || (type === "income" ? "Salário" : "Outros");
      const occurredOn = els.txDate.value || toISODate(new Date());
      const payload = {
        user_id: currentUser.id,
        type,
        amount,
        category,
        description: els.txDescription.value.trim(),
        occurred_on: occurredOn
      };
      busy(els.btnSaveTx, true);
      try {
        const editingId = els.txId.value;
        await saveTransaction(payload, editingId);
        closeModal();
        toast(editingId ? "Lançamento atualizado." : "Lançamento salvo.");
        await safeFetch();
      } catch (err) {
        const msg = String(err.message || err.details || "Não foi possível salvar.");
        if (msg.includes("relation") || msg.includes("schema cache")) {
          toast("Falta criar as tabelas. Execute sql/schema.sql no SQL Editor do Supabase.");
        } else {
          toast(msg);
        }
      } finally {
        busy(els.btnSaveTx, false);
      }
    });

    els.btnDeleteTx.addEventListener("click", () => {
      pendingDeleteId = els.txId.value;
      els.confirm.classList.remove("hidden");
    });
    document.getElementById("btn-confirm-cancel").addEventListener("click", () => {
      els.confirm.classList.add("hidden");
      pendingDeleteId = null;
    });
    document.getElementById("btn-confirm-ok").addEventListener("click", async () => {
      if (!pendingDeleteId) return;
      try {
        await removeTransaction(pendingDeleteId);
        els.confirm.classList.add("hidden");
        pendingDeleteId = null;
        closeModal();
        toast("Lançamento excluído.");
        await safeFetch();
      } catch (err) {
        toast(err.message || "Não foi possível excluir.");
      }
    });
  }

  async function safeFetch() {
    try {
      await fetchMonth();
    } catch (err) {
      toast(err.message || "Não foi possível carregar os lançamentos.");
    }
  }

  function friendlyAuthError(error) {
    const msg = String(error && error.message ? error.message : "");
    const code = String(error && error.code ? error.code : "");
    const lower = msg.toLowerCase();
    let text = "";

    if (lower.includes("invalid login") || lower.includes("invalid credentials")) {
      text = "Login ou senha incorretos.";
    } else if (lower.includes("already registered") || code === "user_already_exists") {
      text = "Este login já está em uso. Abra a aba Entrar.";
    } else if (lower.includes("leaked") || lower.includes("pwned")) {
      text = "O Supabase recusou esta senha por ser considerada insegura. Escolha outra.";
    } else if (
      lower.includes("error sending") ||
      lower.includes("confirmation email") ||
      lower.includes("email not confirmed")
    ) {
      text =
        "O Supabase tentou enviar um e-mail de confirmação. Em Authentication → Providers → Email, desative Confirm email e tente de novo.";
    } else if (lower.includes("invalid format") || code === "email_address_invalid") {
      text =
        "O Supabase recusou o formato interno do login. Em Authentication → Providers → Email, desative Confirm email e qualquer validação extra de e-mail.";
    } else if (lower.includes("signups not allowed") || lower.includes("signup is disabled")) {
      text = "O cadastro de novas contas está desligado no Supabase.";
    } else if (lower.includes("password") && (lower.includes("least") || lower.includes("6"))) {
      text = "A senha precisa ter pelo menos 6 caracteres.";
    } else {
      text = msg || "Não foi possível concluir.";
    }

    if (msg && text.toLowerCase() !== msg.toLowerCase()) {
      text += " (" + msg + ")";
    }
    return text;
  }

  async function init() {
    try {
      bindEvents();
    } catch (err) {
      console.error(err);
    }

    if (!isConfigured()) {
      setLoading(false);
      if (sessionStorage.getItem("finora-demo") === "1") {
        await enterDemo();
        return;
      }
      showView("setup");
      return;
    }

    if (!window.supabase || !window.supabase.createClient) {
      setLoading(false);
      showView("auth");
      setAuthMessage("Não foi possível carregar o serviço de login. Recarregue a página.", true);
      return;
    }

    try {
      supabaseClient = window.supabase.createClient(
        window.APP_CONFIG.supabaseUrl,
        window.APP_CONFIG.supabaseAnonKey,
        {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: false
          }
        }
      );
    } catch (err) {
      setLoading(false);
      showView("auth");
      setAuthMessage(err.message || "Erro ao conectar no Supabase.", true);
      return;
    }

    let openedFor = "";
    let booted = false;

    async function openSession(user) {
      if (!user) {
        currentUser = null;
        transactions = [];
        allUserTransactions = [];
        showView("auth");
        showAuthTab("login");
        setLoading(false);
        return;
      }
      if (openedFor === user.id && currentUser && currentUser.id === user.id) {
        setLoading(false);
        if (!transactions.length) await safeFetch();
        return;
      }
      openedFor = user.id;
      await enterApp(user);
    }

    async function finishBoot(user) {
      if (booted) return;
      booted = true;
      await openSession(user || null);
    }

    supabaseClient.auth.onAuthStateChange(async (event, session) => {
      if (event === "INITIAL_SESSION") {
        await finishBoot(session && session.user);
        return;
      }
      if (event === "SIGNED_OUT") {
        openedFor = "";
        booted = true;
        await openSession(null);
        return;
      }
      if (event === "TOKEN_REFRESHED" || event === "USER_UPDATED") return;
      if (event === "SIGNED_IN" && session && session.user) {
        booted = true;
        await openSession(session.user);
      }
    });

    async function resolveBootUser() {
      const { data } = await supabaseClient.auth.getSession();
      if (!data || !data.session || !data.session.user) return null;
      const check = await supabaseClient.auth.getUser();
      if (check.error || !check.data || !check.data.user) {
        try {
          await supabaseClient.auth.signOut();
        } catch (err) {
          /* ignore */
        }
        return null;
      }
      return check.data.user;
    }

    setTimeout(function () {
      if (currentUser) {
        setLoading(false);
        return;
      }
      booted = true;
      showView("auth");
      showAuthTab("login");
      setLoading(false);
    }, 5000);

    try {
      const user = await resolveBootUser();
      await finishBoot(user);
    } catch (err) {
      if (!booted && !currentUser) {
        showView("auth");
        showAuthTab("login");
        setAuthMessage(err.message || "Não foi possível verificar a sessão.", true);
      }
    } finally {
      if (!booted && !currentUser) {
        booted = true;
        showView("auth");
        showAuthTab("login");
      }
      setLoading(false);
    }
  }

  window.addEventListener("error", (event) => {
    toast(event.message || "Ocorreu um erro na página.");
  });
  window.addEventListener("unhandledrejection", (event) => {
    const reason = event.reason;
    toast((reason && reason.message) || "Falha ao salvar ou carregar dados.");
  });

  try {
    init();
  } catch (err) {
    showView("auth");
    setLoading(false);
    setAuthMessage((err && err.message) || "Não foi possível iniciar o Finora.", true);
  }
})();
