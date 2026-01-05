const form = document.getElementById("contact-form");
const statusText = document.getElementById("form-status");
const submitBtn = document.getElementById("submit-btn");

// ---------------- FORMULARIO ----------------
form.addEventListener("submit", async function (event) {
  event.preventDefault();

  statusText.textContent = "Enviando...";
  statusText.className = "form-status loading";
  submitBtn.disabled = true;

  const formData = new FormData(form);

  const data = {
    nombre: formData.get("nombre"),
    email: formData.get("email"),
    mensaje: formData.get("mensaje")
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/lead", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.mensaje || "Error al enviar");
    }

    statusText.textContent =
      "Solicitud enviada correctamente. Te contactaremos pronto.";
    statusText.className = "form-status success";

    form.reset();
  } catch (error) {
    statusText.textContent =
      "Ocurrió un error al enviar el formulario. Intenta nuevamente.";
    statusText.className = "form-status error";
  } finally {
    submitBtn.disabled = false;
  }
});

// ---------------- CTA SCROLL ----------------
const ctaHero = document.getElementById("cta-btn");
const ctaFooter = document.getElementById("cta-btn-footer");
const contactSection = document.getElementById("contact-section");

function scrollToForm() {
  contactSection.scrollIntoView({ behavior: "smooth" });
}

ctaHero.addEventListener("click", scrollToForm);
ctaFooter.addEventListener("click", scrollToForm);
