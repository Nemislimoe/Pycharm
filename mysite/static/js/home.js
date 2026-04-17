// static/js/home.js
// Локальний JS — лише для головної сторінки
console.log("Головна сторінка завантажена");

document.addEventListener("DOMContentLoaded", () => {
  const hero = document.querySelector(".hero");
  if (hero) {
    hero.style.transition = "opacity .5s";
    hero.style.opacity = "0";
    requestAnimationFrame(() => { hero.style.opacity = "1"; });
  }
});
