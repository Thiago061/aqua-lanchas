function formatDateLabel(date) {
  return new Intl.DateTimeFormat('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' }).format(date);
}

function renderCalendar(mode) {
  const target = document.querySelector('#calendar');
  const dataEl = document.querySelector('#reservas-data');
  if (!target || !dataEl) return;

  const reservas = JSON.parse(dataEl.textContent);
  const today = new Date();
  let totalDays = 7;
  if (mode === 'dia') totalDays = 1;
  if (mode === 'mes') totalDays = 30;

  const days = Array.from({ length: totalDays }, (_, index) => {
    const d = new Date(today);
    d.setDate(today.getDate() + index);
    return d;
  });

  target.innerHTML = `<div class="calendar-grid">${days.map(day => {
    const iso = day.toISOString().slice(0, 10);
    const eventos = reservas.filter(item => item.start.slice(0, 10) === iso);
    return `<div class="calendar-day">
      <strong>${formatDateLabel(day)}</strong>
      ${eventos.map(evento => `<a class="calendar-event" href="${evento.url}">${evento.start.slice(11, 16)} ${evento.title}<br><small>${evento.status}</small></a>`).join('') || '<span class="text-muted">Livre</span>'}
    </div>`;
  }).join('')}</div>`;
}

document.addEventListener('DOMContentLoaded', () => {
  renderCalendar('semana');
  document.querySelectorAll('[data-calendar-mode]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-calendar-mode]').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      renderCalendar(button.dataset.calendarMode);
    });
  });

  const reservaForm = document.querySelector('form');
  if (!reservaForm) return;
  const lancha = document.querySelector('[name="lancha"]');
  const data = document.querySelector('[name="data"]');
  const inicio = document.querySelector('[name="horario_inicio"]');
  const fim = document.querySelector('[name="horario_fim"]');
  if (!lancha || !data || !inicio || !fim) return;

  const aviso = document.createElement('div');
  aviso.className = 'mt-2 fw-semibold';
  fim.parentElement.appendChild(aviso);

  async function checarDisponibilidade() {
    if (!lancha.value || !data.value || !inicio.value || !fim.value) return;
    const params = new URLSearchParams({ lancha: lancha.value, data: data.value, inicio: inicio.value, fim: fim.value });
    const resposta = await fetch(`/api/disponibilidade/?${params}`);
    const json = await resposta.json();
    aviso.textContent = json.disponivel ? 'Horário disponível.' : 'Existe conflito para este horário.';
    aviso.className = json.disponivel ? 'mt-2 fw-semibold text-success' : 'mt-2 fw-semibold text-danger';
  }

  [lancha, data, inicio, fim].forEach(input => input.addEventListener('change', checarDisponibilidade));
});
