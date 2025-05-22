// Atualiza o ano no rodapé
document.getElementById("footer-year").textContent = new Date().getFullYear();

// Corrige o menu toggle
function toggleMenu() {
  const menu = document.getElementById('mobile-menu');
  menu.classList.toggle('show');
}

function closeMenu() {
  const menu = document.getElementById('mobile-menu');
  menu.classList.remove('show');
}

// Evento do botão
document.getElementById('menu-toggle').addEventListener('click', toggleMenu);
