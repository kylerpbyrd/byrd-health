const API_BASE = computeApiBase();
const SLUG_RE = /^sensor\.bbt_(.+)_cycle_day$/;

const MUCUS_OPTIONS = ["None", "Dry", "Sticky", "Creamy", "Egg White", "Watery"];
const OPK_OPTIONS = ["None", "Negative", "Positive", "High", "Peak"];
const FLOW_OPTIONS = ["None", "Spotting", "Light", "Medium", "Heavy"];

const ICONS = {
  header: `<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M15 13V5a3 3 0 0 0-6 0v8a5 5 0 1 0 6 0m-3-9a1 1 0 0 1 1 1v3h-2V5a1 1 0 0 1 1-1Z"/></svg>`,
};

function computeApiBase() {
  try {
    const url = new URL(import.meta.url);
    const path = url.pathname;
    const idx = path.lastIndexOf("/ha-card.js");
    if (idx !== -1) {
      return path.slice(0, idx);
    }
    return "";
  } catch {
    return "";
  }
}

function toTitle(text) {
  if (!text) return "";
  return text.charAt(0).toUpperCase() + text.slice(1);
}

class ByrdHealthEntry extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._config = {};
    this._slug = "";
    this._submitting = false;
    this.attachShadow({ mode: "open" });
  }

  static getConfigElement() {
    return null;
  }

  static getStubConfig() {
    return {};
  }

  setConfig(config) {
    this._config = config;
  }

  set hass(hass) {
    const prevSlug = this._slug;
    if (!this._slug) {
      this._slug = detectSlug(hass);
    }
    this._hass = hass;
    if (prevSlug !== this._slug || !this.shadowRoot || !this.shadowRoot.querySelector(".card")) {
      this._render();
    } else {
      this._updateDisplay();
    }
  }

  getCardSize() {
    return 5;
  }

  _render() {
    if (!this._hass) return;

    while (this.shadowRoot.firstChild) {
      this.shadowRoot.removeChild(this.shadowRoot.firstChild);
    }

    const style = document.createElement("style");
    style.textContent = this._css();
    this.shadowRoot.appendChild(style);

    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = this._template();
    this.shadowRoot.appendChild(card);

    this._wireEvents(card);
    this._updateDisplay();
  }

  _updateDisplay() {
    if (!this._hass || !this._slug || !this.shadowRoot) return;

    const states = this._hass.states || {};

    const header = this.shadowRoot.querySelector(".js-header");
    if (header) {
      const day = getState(states, `sensor.bbt_${this._slug}_cycle_day`);
      const phase = getState(states, `sensor.bbt_${this._slug}_cycle_phase`);
      header.innerHTML = `${ICONS.header} <span>${day} &middot; ${toTitle(phase)}</span>`;
    }

    const tempInput = this.shadowRoot.querySelector(".js-temp");
    if (tempInput) {
      const lastTemp = getState(states, `sensor.bbt_${this._slug}_last_temp`);
      const unit = getAttribute(states, `sensor.bbt_${this._slug}_last_temp`, "unit_of_measurement");
      const unitLabel = this.shadowRoot.querySelector(".js-temp-unit");
      if (unitLabel) unitLabel.textContent = unit || "°F";
      if (!tempInput.value && lastTemp && lastTemp !== "unknown") {
        tempInput.value = lastTemp;
        tempInput.setAttribute("data-last", lastTemp);
      }
    }
  }

  _wireEvents(card) {
    const btn = card.querySelector(".js-submit");
    if (btn) {
      btn.addEventListener("click", () => this._submit());
    }
  }

  async _submit() {
    if (this._submitting) return;
    this._submitting = true;

    const btn = this.shadowRoot.querySelector(".js-submit");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Saving...";
    }

    try {
      const today = new Date().toISOString().slice(0, 10);
      const tempInput = this.shadowRoot.querySelector(".js-temp");
      const tempVal = tempInput ? parseFloat(tempInput.value) : NaN;

      const body = { date: today };

      if (!isNaN(tempVal)) {
        body.temp_value = tempVal;
      }

      const mucus = this.shadowRoot.querySelector(".js-mucus");
      if (mucus && mucus.value) {
        body.cervical_mucus = mucus.value;
      }

      const opk = this.shadowRoot.querySelector(".js-opk");
      if (opk && opk.value) {
        body.opk_result = opk.value;
      }

      const flow = this.shadowRoot.querySelector(".js-flow");
      if (flow && flow.value) {
        body.menstrual_flow = flow.value;
      }

      const url = `${API_BASE}/api/v1/fertility/entries/`;
      const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (resp.ok) {
        this._showToast("Entry logged", "success");
        this._clearForm();
        this._refreshEntities();
      } else {
        const detail = await resp.json().catch(() => ({}));
        const msg = detail.detail || `Error ${resp.status}`;
        this._showToast(msg, "error");
      }
    } catch (err) {
      this._showToast("Network error. Check connection.", "error");
    } finally {
      this._submitting = false;
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Log Entry";
      }
    }
  }

  _clearForm() {
    const temp = this.shadowRoot.querySelector(".js-temp");
    if (temp) {
      temp.value = "";
      temp.removeAttribute("data-last");
    }
    const selects = ["js-mucus", "js-opk", "js-flow"];
    for (const cls of selects) {
      const el = this.shadowRoot.querySelector(`.${cls}`);
      if (el) el.value = "";
    }
  }

  _refreshEntities() {
    if (!this._hass || !this._slug) return;
    const entityIds = [
      `sensor.bbt_${this._slug}_cycle_day`,
      `sensor.bbt_${this._slug}_cycle_phase`,
      `sensor.bbt_${this._slug}_last_temp`,
      `sensor.bbt_${this._slug}_next_period_date`,
      `sensor.bbt_${this._slug}_fertile_window`,
    ];
    if (this._hass.callService) {
      for (const eid of entityIds) {
        try {
          this._hass.callService("homeassistant", "update_entity", { entity_id: eid });
        } catch {}
      }
    }
  }

  _showToast(message, type) {
    const existing = this.shadowRoot.querySelector(".toast");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    this.shadowRoot.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("toast-visible"));

    setTimeout(() => {
      toast.classList.remove("toast-visible");
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  _template() {
    if (!this._slug) {
      return `<div class="no-profile">No Byrd Health profile found. Set up a profile in the Byrd Health add-on first.</div>`;
    }

    return `
      <div class="card-content">
        <div class="card-header js-header">
          ${ICONS.header} <span>-- &middot; --</span>
        </div>

        <div class="card-body">
          <div class="field">
            <label class="field-label">Temperature</label>
            <div class="input-row">
              <input
                type="number"
                class="field-input js-temp"
                step="0.01"
                min="90"
                max="105"
                inputmode="decimal"
                placeholder="--.--"
              />
              <span class="field-suffix js-temp-unit">°F</span>
            </div>
          </div>

          <div class="field">
            <label class="field-label">Mucus</label>
            <select class="field-select js-mucus">
              <option value="">None</option>
              ${MUCUS_OPTIONS.filter((o) => o !== "None").map((o) => `<option value="${o}">${o}</option>`).join("")}
            </select>
          </div>

          <div class="field">
            <label class="field-label">OPK</label>
            <select class="field-select js-opk">
              <option value="">None</option>
              ${OPK_OPTIONS.filter((o) => o !== "None").map((o) => `<option value="${o}">${o}</option>`).join("")}
            </select>
          </div>

          <div class="field">
            <label class="field-label">Flow</label>
            <select class="field-select js-flow">
              <option value="">None</option>
              ${FLOW_OPTIONS.filter((o) => o !== "None").map((o) => `<option value="${o}">${o}</option>`).join("")}
            </select>
          </div>
        </div>

        <button class="submit-btn js-submit">Log Entry</button>
      </div>
    `;
  }

  _css() {
    return `
      :host {
        display: block;
      }

      .card {
        background: var(--card-background-color, #fff);
        border-radius: var(--ha-card-border-radius, 12px);
        box-shadow: var(--ha-card-box-shadow, 0 2px 2px 0 rgba(0, 0, 0, 0.14));
        overflow: hidden;
        font-family: var(--paper-font-common-base_-_font-family, Roboto, sans-serif);
        color: var(--primary-text-color, #212121);
      }

      .no-profile {
        padding: 20px;
        text-align: center;
        color: var(--secondary-text-color, #727272);
        font-size: 14px;
        line-height: 1.5;
      }

      .card-content {
        padding: 16px;
      }

      .card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;
        padding-bottom: 12px;
        margin-bottom: 12px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
        color: var(--primary-color, #03a9f4);
      }

      .card-header svg {
        flex-shrink: 0;
        color: var(--primary-color, #03a9f4);
      }

      .card-body {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .field {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .field-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--secondary-text-color, #727272);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .input-row {
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .field-input {
        flex: 1;
        padding: 10px 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 8px;
        font-size: 18px;
        font-weight: 500;
        font-family: inherit;
        color: var(--primary-text-color, #212121);
        background: var(--input-background-color, transparent);
        outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
        min-width: 0;
      }

      .field-input:focus {
        border-color: var(--primary-color, #03a9f4);
      }

      .field-input::placeholder {
        color: var(--disabled-text-color, #bdbdbd);
        font-weight: 400;
        font-size: 16px;
      }

      .field-suffix {
        font-size: 14px;
        font-weight: 500;
        color: var(--secondary-text-color, #727272);
        white-space: nowrap;
      }

      .field-select {
        padding: 10px 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 8px;
        font-size: 15px;
        font-family: inherit;
        color: var(--primary-text-color, #212121);
        background: var(--input-background-color, transparent);
        outline: none;
        transition: border-color 0.2s;
        cursor: pointer;
        box-sizing: border-box;
        -webkit-appearance: none;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23727272' d='M6 8.825L1.175 4 2.238 2.938 6 6.7 9.763 2.937 10.825 4z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 12px center;
        padding-right: 32px;
      }

      .field-select:focus {
        border-color: var(--primary-color, #03a9f4);
      }

      .submit-btn {
        width: 100%;
        margin-top: 16px;
        padding: 12px;
        border: none;
        border-radius: 10px;
        background: var(--primary-color, #03a9f4);
        color: var(--text-primary-color, #fff);
        font-size: 15px;
        font-weight: 600;
        font-family: inherit;
        cursor: pointer;
        transition: opacity 0.2s;
        letter-spacing: 0.3px;
      }

      .submit-btn:hover {
        opacity: 0.9;
      }

      .submit-btn:active {
        opacity: 0.8;
      }

      .submit-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        font-family: inherit;
        z-index: 999;
        opacity: 0;
        transition: opacity 0.3s, transform 0.3s;
        pointer-events: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }

      .toast-visible {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }

      .toast-success {
        background: var(--success-color, #4caf50);
        color: #fff;
      }

      .toast-error {
        background: var(--error-color, #f44336);
        color: #fff;
      }

      @media (max-width: 360px) {
        .card-content {
          padding: 12px;
        }
        .card-header {
          font-size: 14px;
        }
        .field-input {
          font-size: 16px;
          padding: 8px 10px;
        }
        .submit-btn {
          font-size: 14px;
          padding: 10px;
        }
      }
    `;
  }
}

function detectSlug(hass) {
  if (!hass || !hass.states) return "";
  for (const entityId of Object.keys(hass.states)) {
    const match = entityId.match(SLUG_RE);
    if (match) {
      return match[1];
    }
  }
  return "";
}

function getState(states, entityId) {
  const entity = states[entityId];
  if (!entity) return "";
  return entity.state || "";
}

function getAttribute(states, entityId, attr) {
  const entity = states[entityId];
  if (!entity || !entity.attributes) return "";
  return entity.attributes[attr] || "";
}

customElements.define("byrd-health-entry", ByrdHealthEntry);
