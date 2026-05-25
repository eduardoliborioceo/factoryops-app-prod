"use strict";

const _root = () => document.getElementById("roteiros-root");

const URL_CRIAR           = () => _root().dataset.urlCriar;
const URL_EDITAR_TPL      = () => _root().dataset.urlEditarTpl;
const URL_EXCLUIR_TPL     = () => _root().dataset.urlExcluirTpl;
const URL_MODELOS_TPL     = () => _root().dataset.urlModelosTpl;
const URL_VINCULAR_TPL    = () => _root().dataset.urlVincularTpl;
const URL_DESVINCULAR_TPL = () => _root().dataset.urlDesvincularTpl;
const URL_CODIGOS_TPL     = () => _root().dataset.urlCodigosTpl;

const CLIENTES_MODELOS = () => JSON.parse(_root().dataset.clientesModelos || "[]");
const LINHAS_CONFIG    = () => JSON.parse(_root().dataset.linhasConfig    || "{}");

function _url(tpl, id) {
  return tpl.replace("/0/", `/${id}/`).replace("/0", `/${id}`);
}

// ─── Alertas ─────────────────────────────────────────────────────────────────
function mostrarAlerta(tipo, msg) {
  const area = document.getElementById("alertArea");
  if (!area) return;
  const div = document.createElement("div");
  div.className = `alert alert-${tipo} alert-dismissible d-flex align-items-center gap-2 mb-3`;
  div.role = "alert";
  div.innerHTML = `<i class="bi bi-${tipo === "success" ? "check-circle-fill" : "x-circle-fill"} fs-5 flex-shrink-0"></i>
    <div>${msg}</div>
    <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>`;
  area.prepend(div);
  setTimeout(() => div.remove(), 5000);
}

// ─── Filial ───────────────────────────────────────────────────────────────────
function _getFilial() {
  return document.getElementById("roteiroFilial")?.value || "VTE";
}

function onFilialChange() {
  _limparEtapas();
}

// ─── Cores por setor ──────────────────────────────────────────────────────────
const _SETOR_CORES = {
  SMD: "success", PTH: "primary", IM: "warning", PA: "danger"
};

// ─── Etapas (modal criar/editar) ─────────────────────────────────────────────
function adicionarEtapa(setor) {
  const list = document.getElementById("etapasList");
  const existente = list.querySelector(`[data-setor="${setor}"]`);
  if (existente) {
    existente.classList.add("border-warning");
    setTimeout(() => existente.classList.remove("border-warning"), 800);
    return;
  }

  const filial = _getFilial();
  const cor    = _SETOR_CORES[setor] || "secondary";
  const ordem  = list.children.length + 1;

  const linhasDisp = (LINHAS_CONFIG()[filial] || {})[setor] || [];

  const div = document.createElement("div");
  div.className = "mb-2 etapa-item border rounded p-2";
  div.dataset.setor = setor;
  div.style.cssText = "border-color:var(--border) !important;border-radius:8px !important;";

  let linhasHTML = "";
  if (linhasDisp.length > 0) {
    const btns = linhasDisp.map(l =>
      `<button type="button"
               class="btn btn-outline-secondary btn-sm linha-disp-btn"
               style="border-radius:6px;font-size:0.72rem;padding:2px 8px;"
               data-linha="${l.linha}"
               onclick="adicionarLinha(this, '${l.linha.replace(/'/g,"\\'")}')">
         <i class="bi bi-plus-circle me-1"></i>${l.linha}
       </button>`
    ).join("");

    linhasHTML = `
      <div class="mt-2 pt-2" style="border-top:1px dashed var(--border);">
        <div class="fw-semibold mb-1" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-muted);">
          <i class="bi bi-diagram-2 me-1"></i>Linhas / Máquinas (sequência de passagem)
        </div>
        <div class="linhas-disp d-flex flex-wrap gap-1 mb-2">${btns}</div>
        <div class="linhas-selecionadas d-flex flex-wrap align-items-center gap-1"></div>
      </div>`;
  }

  div.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <span class="badge bg-${cor}" style="font-size:0.78rem;min-width:42px;">${setor}</span>
      <span class="text-muted small etapa-ordem">#${ordem}</span>
      <input type="text" class="form-control form-control-sm flex-grow-1 etapa-obs"
             placeholder="Observação (opcional)" style="border-radius:6px;font-size:0.78rem;"
             maxlength="200">
      <button type="button" class="btn btn-outline-danger btn-sm" style="border-radius:6px;padding:2px 6px;"
              onclick="removerEtapa(this)">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>
    ${linhasHTML}
  `;

  list.appendChild(div);
  _atualizarOrdens();
}

function removerEtapa(btn) {
  btn.closest(".etapa-item").remove();
  _atualizarOrdens();
}

function _atualizarOrdens() {
  document.querySelectorAll("#etapasList .etapa-item").forEach(function(item, i) {
    const label = item.querySelector(".etapa-ordem");
    if (label) label.textContent = `#${i + 1}`;
  });
}

// ─── Linhas dentro de uma etapa ───────────────────────────────────────────────
function adicionarLinha(btn, linha) {
  const etapaItem   = btn.closest(".etapa-item");
  const linhasSel   = etapaItem.querySelector(".linhas-selecionadas");
  if (!linhasSel) return;

  if (linhasSel.querySelector(`[data-linha="${linha}"]`)) {
    btn.classList.add("btn-warning");
    setTimeout(() => btn.classList.remove("btn-warning"), 700);
    return;
  }

  const ordem = linhasSel.querySelectorAll("[data-linha]").length + 1;

  const span = document.createElement("span");
  span.className = "d-inline-flex align-items-center gap-1 badge";
  span.dataset.linha = linha;
  span.style.cssText =
    "background:rgba(13,110,253,0.08);color:var(--primary);" +
    "border:1px solid rgba(13,110,253,0.25);border-radius:6px;" +
    "font-size:0.72rem;padding:4px 8px;font-weight:600;";
  span.innerHTML = `
    <span class="linha-ordem" style="opacity:0.6;">${ordem}.</span>
    ${linha}
    <button type="button" onclick="removerLinha(this)"
            style="background:none;border:none;padding:0;margin:0;line-height:1;cursor:pointer;color:inherit;opacity:0.6;"
            aria-label="Remover">
      <i class="bi bi-x-lg" style="font-size:0.6rem;"></i>
    </button>
  `;
  linhasSel.appendChild(span);
  _atualizarOrdemLinhas(linhasSel);
}

function removerLinha(btn) {
  const linhasSel = btn.closest(".linhas-selecionadas");
  btn.closest("[data-linha]").remove();
  _atualizarOrdemLinhas(linhasSel);
}

function _atualizarOrdemLinhas(container) {
  Array.from(container.querySelectorAll("[data-linha]")).forEach(function(el, i) {
    const ordemEl = el.querySelector(".linha-ordem");
    if (ordemEl) ordemEl.textContent = `${i + 1}.`;
  });
}

// ─── Coletar/limpar etapas ────────────────────────────────────────────────────
function _coletarEtapas() {
  return Array.from(document.querySelectorAll("#etapasList .etapa-item")).map(function(item, i) {
    const linhasSel = item.querySelector(".linhas-selecionadas");
    const linhas    = linhasSel
      ? Array.from(linhasSel.querySelectorAll("[data-linha]")).map(function(el, j) {
          return { linha: el.dataset.linha, ordem: j + 1 };
        })
      : [];
    return {
      setor:      item.dataset.setor,
      ordem:      i + 1,
      observacao: item.querySelector(".etapa-obs")?.value.trim() || null,
      linhas,
    };
  });
}

function _limparEtapas() {
  document.getElementById("etapasList").innerHTML = "";
}

function _carregarEtapas(etapas) {
  _limparEtapas();
  (etapas || []).forEach(function(e) {
    adicionarEtapa(e.setor);
    const list   = document.getElementById("etapasList");
    const ultimo = list.lastElementChild;
    if (!ultimo) return;

    if (e.observacao) {
      const obsEl = ultimo.querySelector(".etapa-obs");
      if (obsEl) obsEl.value = e.observacao;
    }

    const linhas = typeof e.linhas === "string" ? JSON.parse(e.linhas) : (e.linhas || []);
    linhas.forEach(function(l) {
      const dispBtn = ultimo.querySelector(`.linhas-disp [data-linha="${l.linha}"]`);
      if (dispBtn) {
        adicionarLinha(dispBtn, l.linha);
      }
    });
  });
}

// ─── Datalist de clientes ─────────────────────────────────────────────────────
function _popularClientesSugestoes() {
  const dl = document.getElementById("clientesSugestoes");
  if (!dl) return;
  dl.innerHTML = "";
  CLIENTES_MODELOS().forEach(function(c) {
    const opt = document.createElement("option");
    opt.value = c;
    dl.appendChild(opt);
  });
}

// ─── Modal Novo ───────────────────────────────────────────────────────────────
function abrirModalNovo() {
  document.getElementById("roteiroId").value       = "";
  document.getElementById("roteiroFilial").value   = "VTE";
  document.getElementById("roteiroNome").value     = "";
  document.getElementById("roteiroCliente").value  = "";
  document.getElementById("roteiroDescricao").value = "";
  _limparEtapas();
  _popularClientesSugestoes();

  document.getElementById("modalRoteiroTitulo").innerHTML =
    '<i class="bi bi-diagram-3 me-2 text-primary"></i>Novo Roteiro';

  bootstrap.Modal.getOrCreateInstance(document.getElementById("modalRoteiro")).show();
}

// ─── Modal Editar ─────────────────────────────────────────────────────────────
function abrirModalEditar(id, roteiro) {
  document.getElementById("roteiroId").value        = id;
  document.getElementById("roteiroFilial").value    = roteiro.filial || "VTE";
  document.getElementById("roteiroNome").value      = roteiro.nome || "";
  document.getElementById("roteiroCliente").value   = roteiro.cliente || "";
  document.getElementById("roteiroDescricao").value = roteiro.descricao || "";
  _popularClientesSugestoes();

  const etapas = typeof roteiro.etapas === "string"
    ? JSON.parse(roteiro.etapas)
    : (roteiro.etapas || []);
  _carregarEtapas(etapas);

  document.getElementById("modalRoteiroTitulo").innerHTML =
    `<i class="bi bi-pencil me-2 text-primary"></i>Editar: ${roteiro.nome}`;

  bootstrap.Modal.getOrCreateInstance(document.getElementById("modalRoteiro")).show();
}

// ─── Salvar (criar ou editar) ─────────────────────────────────────────────────
function salvarRoteiro() {
  const id      = document.getElementById("roteiroId").value;
  const filial  = document.getElementById("roteiroFilial").value;
  const nome    = document.getElementById("roteiroNome").value.trim();
  const cliente = document.getElementById("roteiroCliente").value.trim();
  const descr   = document.getElementById("roteiroDescricao").value.trim();
  const etapas  = _coletarEtapas();

  if (!nome || !cliente) {
    mostrarAlerta("danger", "Nome e cliente são obrigatórios.");
    return;
  }

  const isNovo = !id;
  const url    = isNovo ? URL_CRIAR() : _url(URL_EDITAR_TPL(), id);

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filial, nome, cliente, descricao: descr || null, etapas }),
  })
    .then(r => r.json())
    .then(function(data) {
      if (!data.ok) {
        mostrarAlerta("danger", data.erro || "Erro ao salvar.");
        return;
      }
      bootstrap.Modal.getOrCreateInstance(document.getElementById("modalRoteiro")).hide();
      mostrarAlerta("success", isNovo ? "Roteiro criado com sucesso." : "Roteiro atualizado.");
      setTimeout(() => location.reload(), 900);
    })
    .catch(() => mostrarAlerta("danger", "Erro de comunicação com o servidor."));
}

// ─── Excluir ──────────────────────────────────────────────────────────────────
function excluirRoteiro(id, nome) {
  if (!confirm(`Excluir o roteiro "${nome}"? Todos os modelos vinculados serão desvinculados.`)) return;

  fetch(_url(URL_EXCLUIR_TPL(), id), { method: "POST" })
    .then(r => r.json())
    .then(function(data) {
      if (!data.ok) {
        mostrarAlerta("danger", data.erro || "Erro ao excluir.");
        return;
      }
      const card = document.querySelector(`.roteiro-card[data-id="${id}"]`);
      if (card) card.closest(".col-12").remove();
      mostrarAlerta("success", `Roteiro "${nome}" excluído.`);
    })
    .catch(() => mostrarAlerta("danger", "Erro de comunicação com o servidor."));
}

// ─── Modal Modelos ────────────────────────────────────────────────────────────
function abrirModalModelos(roteiroId, nome, cliente) {
  document.getElementById("modelosRoteiroId").value = roteiroId;
  document.getElementById("modalModelosTitulo").innerHTML =
    `<i class="bi bi-cpu me-2 text-primary"></i>Modelos — ${nome}`;

  _carregarModelosVinculados(roteiroId);

  bootstrap.Modal.getOrCreateInstance(document.getElementById("modalModelos")).show();
}

function _carregarModelosVinculados(roteiroId) {
  const list = document.getElementById("modelosVinculadosList");
  list.innerHTML = `
    <div class="text-center text-muted py-3">
      <div class="spinner-border spinner-border-sm me-2"></div>Carregando…
    </div>`;

  fetch(_url(URL_MODELOS_TPL(), roteiroId))
    .then(r => r.json())
    .then(function(data) {
      if (!data.ok || !data.modelos || data.modelos.length === 0) {
        list.innerHTML = `
          <div class="text-center text-muted py-3" style="font-size:0.82rem;">
            <i class="bi bi-cpu d-block fs-4 mb-2 opacity-25"></i>
            Nenhum modelo vinculado ainda.
          </div>`;
        return;
      }
      list.innerHTML = "";
      data.modelos.forEach(function(m) {
        const row = document.createElement("div");
        row.className = "d-flex align-items-center justify-content-between py-2 px-3 border-bottom";
        row.style.cssText = "border-color:var(--border) !important;font-size:0.82rem;";
        row.innerHTML = `
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-cpu text-muted"></i>
            <span class="fw-semibold">${m.modelo_codigo}</span>
            ${m.setor ? `<span class="badge bg-light text-dark border" style="font-size:0.65rem;">${m.setor}</span>` : ""}
          </div>
          <button class="btn btn-outline-danger btn-sm" style="border-radius:6px;padding:2px 6px;font-size:0.68rem;"
                  onclick="desvincularModelo(${roteiroId}, '${m.modelo_codigo}', this)" title="Desvincular">
            <i class="bi bi-x-lg"></i>
          </button>`;
        list.appendChild(row);
      });
    })
    .catch(() => {
      list.innerHTML = `<div class="text-danger p-3" style="font-size:0.82rem;">Erro ao carregar modelos.</div>`;
    });
}

function vincularModelo() {
  const roteiroId = document.getElementById("modelosRoteiroId").value;
  const codigo    = document.getElementById("novoModeloCodigo").value.trim().toUpperCase();

  if (!codigo) {
    mostrarAlerta("danger", "Informe o código do modelo.");
    return;
  }

  fetch(_url(URL_VINCULAR_TPL(), roteiroId), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo }),
  })
    .then(r => r.json())
    .then(function(data) {
      if (!data.ok) {
        mostrarAlerta("danger", data.erro || "Erro ao vincular.");
        return;
      }
      document.getElementById("novoModeloCodigo").value = "";
      _carregarModelosVinculados(roteiroId);
      _atualizarContadorCard(roteiroId, 1);
    })
    .catch(() => mostrarAlerta("danger", "Erro de comunicação com o servidor."));
}

function desvincularModelo(roteiroId, codigo, btn) {
  if (!confirm(`Desvincular o modelo "${codigo}" deste roteiro?`)) return;

  fetch(_url(URL_DESVINCULAR_TPL(), roteiroId), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ codigo }),
  })
    .then(r => r.json())
    .then(function(data) {
      if (!data.ok) {
        mostrarAlerta("danger", data.erro || "Erro ao desvincular.");
        return;
      }
      btn.closest("div.d-flex").remove();
      _atualizarContadorCard(roteiroId, -1);
    })
    .catch(() => mostrarAlerta("danger", "Erro de comunicação com o servidor."));
}

function _atualizarContadorCard(roteiroId, delta) {
  const container = document.querySelector(`.modelos-count-${roteiroId}`);
  if (!container) return;

  const badge = container.querySelector(".badge");
  if (badge) {
    const match = badge.textContent.trim().match(/^(\d+)/);
    if (match) {
      const novo = Math.max(0, parseInt(match[1]) + delta);
      badge.innerHTML = `<i class="bi bi-cpu me-1"></i>${novo} modelo${novo !== 1 ? "s" : ""}`;
      if (novo === 0) {
        container.innerHTML = '<span class="text-muted fst-italic" style="font-size:0.78rem;">Nenhum modelo vinculado</span>';
      }
    }
  } else if (delta > 0) {
    container.innerHTML = `<span class="badge bg-light text-dark border" style="font-size:0.72rem;">
      <i class="bi bi-cpu me-1"></i>1 modelo
    </span>`;
  }
}
