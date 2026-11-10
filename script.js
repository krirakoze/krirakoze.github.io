const filters = document.querySelectorAll('[data-filter]');
filters.forEach(button => button.addEventListener('click', () => {
  const selected = button.dataset.filter;
  filters.forEach(item => { const active = item === button; item.classList.toggle('active', active); item.setAttribute('aria-pressed', String(active)); });
  document.querySelectorAll('.project-card').forEach(card => { card.hidden = selected !== 'All' && card.dataset.category !== selected; });
}));
const timing = document.querySelector('#timing-toggle');
if (timing) timing.addEventListener('change', () => {
  const reversed = timing.checked;
  document.querySelector('#lowest-balance').textContent = reversed ? '$150' : '$650';
  document.querySelector('#scenario-note').textContent = reversed ? 'Rent first: the balance falls to $150 before the $500 paycheck arrives. The ending balance remains $650.' : 'Payment order changes the lowest balance, even when the ending balance stays the same.';
  const points = reversed ? [1650,1500,1250,150,650] : [1650,1500,1250,1750,650];
  const coords = points.map((value,i) => [12+i*87, 10+(1900-value)*.087]);
  const svg = document.querySelector('.mini-chart');
  svg.querySelector('path').setAttribute('d', coords.map(([x,y],i) => `${i?'L':'M'}${x} ${y}`).join(' '));
  svg.querySelectorAll('circle').forEach((circle,i) => {circle.setAttribute('cx', coords[i][0]);circle.setAttribute('cy',coords[i][1]);});
  svg.setAttribute('viewBox','0 0 380 170');
  svg.setAttribute('aria-label', `Fictional checking balances: ${points.join(', ')} dollars`);
});
