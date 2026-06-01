/**
 * Contract service landing — client interactions
 */
(function () {
  "use strict";

  function resolveFormSubmitEmail() {
    const meta = document.querySelector('meta[name="formsubmit-email"]');
    return meta?.content?.trim() || "rodionova61@bk.ru";
  }

  const FORMSUBMIT_EMAIL = resolveFormSubmitEmail();
  const FORMSUBMIT_URL = `https://formsubmit.co/ajax/${encodeURIComponent(FORMSUBMIT_EMAIL)}`;

  const REGION_LABELS = {
    moscow: "Москва и МО",
    spb: "Санкт-Петербург и ЛО",
    central: "Центральный ФО",
    south: "Южный ФО",
    north: "Северо-Западный ФО",
    volga: "Приволжский ФО",
    ural: "Уральский ФО",
    siberia: "Сибирский ФО",
    "far-east": "Дальневосточный ФО",
    other: "Другой",
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  /* ——— Mobile navigation ——— */
  function initNav() {
    const toggle = $("#nav-toggle");
    const menu = $("#nav-menu");
    const nav = $("#site-nav");
    const header = $(".site-header");
    const backdrop = $("#nav-backdrop");

    if (!toggle || !menu) return;

    const setMenuOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      nav?.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      if (backdrop) {
        backdrop.hidden = !open;
        backdrop.classList.toggle("is-visible", open);
      }
    };

    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      setMenuOpen(!open);
    });

    backdrop?.addEventListener("click", () => setMenuOpen(false));

    menu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setMenuOpen(false));
    });

    window.addEventListener("scroll", () => {
      header?.classList.toggle("is-scrolled", window.scrollY > 24);
    }, { passive: true });

    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setMenuOpen(false);
    });
  }

  /* ——— Scroll reveal ——— */
  function initReveal() {
    const items = $$("[data-animate]");
    if (!items.length || !("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
    );

    items.forEach((el) => observer.observe(el));
  }

  /* ——— Counter animation ——— */
  function initCounters() {
    const counters = $$("[data-counter]");
    if (!counters.length) return;

    const animate = (el) => {
      const target = Number(el.getAttribute("data-counter")) || 0;
      const duration = 1600;
      const start = performance.now();

      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(target * eased);
        if (progress < 1) requestAnimationFrame(tick);
      };

      requestAnimationFrame(tick);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animate(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    counters.forEach((el) => observer.observe(el));
  }

  /* ——— Phone mask ——— */
  function formatPhone(value) {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    let normalized = digits;
    if (normalized.startsWith("8")) normalized = "7" + normalized.slice(1);
    if (!normalized.startsWith("7") && normalized.length) normalized = "7" + normalized;

    const parts = [
      normalized.slice(0, 1),
      normalized.slice(1, 4),
      normalized.slice(4, 7),
      normalized.slice(7, 9),
      normalized.slice(9, 11),
    ];

    if (!parts[0]) return "";
    let out = "+7";
    if (parts[1]) out += ` (${parts[1]}`;
    if (parts[1]?.length === 3) out += ")";
    if (parts[2]) out += ` ${parts[2]}`;
    if (parts[3]) out += `-${parts[3]}`;
    if (parts[4]) out += `-${parts[4]}`;
    return out;
  }

  function initPhoneMask() {
    const phone = $("#phone");
    if (!phone) return;

    phone.addEventListener("input", () => {
      phone.value = formatPhone(phone.value);
    });
  }

  /* ——— Form validation ——— */
  const validators = {
    name(value) {
      const trimmed = value.trim();
      if (trimmed.length < 5) return "Введите полное ФИО (минимум 5 символов)";
      if (!/^[\p{L}\s\-]+$/u.test(trimmed)) return "ФИО может содержать только буквы, пробелы и дефис";
      const parts = trimmed.split(/\s+/).filter(Boolean);
      if (parts.length < 2) return "Укажите фамилию и имя";
      return "";
    },
    phone(value) {
      const digits = value.replace(/\D/g, "");
      if (digits.length < 11) return "Введите корректный номер телефона";
      return "";
    },
    age(value) {
      const n = Number(value);
      if (!Number.isInteger(n) || n < 18 || n > 63) return "Возраст должен быть от 18 до 63 лет";
      return "";
    },
    region(value) {
      if (!value) return "Выберите регион";
      return "";
    },
    consent(checked) {
      if (!checked) return "Необходимо согласие на обработку данных";
      return "";
    },
  };

  function showFieldError(name, message) {
    const input = $(`#${name}`) || $(`[name="${name}"]`);
    const errorEl = $(`.form__error[data-for="${name}"]`);
    if (input) input.classList.toggle("is-invalid", Boolean(message));
    if (errorEl) errorEl.textContent = message || "";
  }

  function validateForm(form) {
    let valid = true;
    const data = new FormData(form);

    Object.keys(validators).forEach((field) => {
      let message = "";
      if (field === "consent") {
        message = validators.consent($("#consent")?.checked);
      } else {
        message = validators[field](data.get(field)?.toString() || "");
      }
      showFieldError(field, message);
      if (message) valid = false;
    });

    return valid;
  }

  function showToast(message) {
    const toast = $("#toast");
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    toast.classList.add("is-visible");
    setTimeout(() => {
      toast.classList.remove("is-visible");
      setTimeout(() => { toast.hidden = true; }, 400);
    }, 4000);
  }

  function setFormStatus(message, type) {
    const status = $("#form-status");
    if (!status) return;
    status.textContent = message;
    status.className = "form__status";
    if (type) status.classList.add(`is-${type}`);
  }

  function buildFormSubmitBody(payload, form) {
    return {
      _subject: `Заявка: ${payload.name} — ${payload.phone}`,
      _template: "table",
      _captcha: "false",
      _honey: form._honey?.value || "",
      "ФИО": payload.name,
      "Телефон": payload.phone,
      "Возраст": String(payload.age),
      "Регион": REGION_LABELS[payload.region] || payload.region,
      "Комментарий": payload.comment || "—",
    };
  }

  function isFormSubmitSuccess(body) {
    return body?.success === true || body?.success === "true";
  }

  async function submitForm(form) {
    const btn = $("#submit-btn");
    const payload = {
      name: form.name.value.trim(),
      phone: form.phone.value.trim(),
      age: Number(form.age.value),
      region: form.region.value,
      comment: form.comment.value.trim(),
      consent: form.consent.checked,
    };

    btn.disabled = true;
    btn.textContent = "Отправка…";
    setFormStatus("", "");

    try {
      const res = await fetch(FORMSUBMIT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(buildFormSubmitBody(payload, form)),
      });

      const body = await res.json().catch(() => ({}));

      if (!res.ok || !isFormSubmitSuccess(body)) {
        const errMsg =
          body.message ||
          "Не удалось отправить заявку. Позвоните +7 906 310-16-33 или повторите позже.";
        setFormStatus(errMsg, "error");
        showToast(errMsg);
        return;
      }

      form.reset();
      $$(".form__error").forEach((el) => { el.textContent = ""; });
      $$(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
      setFormStatus("Заявка принята! Мы свяжемся с вами в течение 24 часов.", "success");
      showToast("Заявка успешно отправлена");
    } catch {
      const fallback =
        "Ошибка сети. Позвоните по телефону +7 906 310-16-33 или повторите позже.";
      setFormStatus(fallback, "error");
      showToast("Ошибка сети");
    } finally {
      btn.disabled = false;
      btn.textContent = "Отправить заявку";
    }
  }

  function initForm() {
    const form = $("#apply-form");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!validateForm(form)) {
        setFormStatus("Исправьте ошибки в форме", "error");
        return;
      }
      submitForm(form);
    });

    form.querySelectorAll("input, select, textarea").forEach((el) => {
      el.addEventListener("blur", () => {
        const name = el.name;
        if (validators[name]) {
          const msg = validators[name](el.type === "checkbox" ? el.checked : el.value);
          showFieldError(name, msg);
        }
      });
    });
  }

  /* ——— Active section in nav ——— */
  function initScrollSpy() {
    const links = $$("[data-nav]");
    const sections = links
      .map((a) => document.querySelector(a.getAttribute("href")))
      .filter(Boolean);

    if (!sections.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = entry.target.id;
          links.forEach((link) => {
            link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
          });
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
    );

    sections.forEach((section) => observer.observe(section));
  }

  function init() {
    initNav();
    initScrollSpy();
    initReveal();
    initCounters();
    initPhoneMask();
    initForm();
    $(".site-header")?.classList.toggle("is-scrolled", window.scrollY > 24);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
