// myapp/static/myapp/js/profile.js
// Завдання 4: локальний JS для сторінки профілю

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("profile-btn");

  if (btn) {
    btn.addEventListener("click", () => {
      alert("Профіль збережено!");
      btn.textContent = "Збережено ✓";
      btn.style.background = "#16a34a";

      setTimeout(() => {
        btn.textContent = "Зберегти профіль";
        btn.style.background = "";
      }, 2000);
    });
  }
});
