const form = document.getElementById("form");
const statusBox = document.getElementById("status");
const resultBox = document.getElementById("result");
const preview = document.getElementById("preview");

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

form.photo.addEventListener("change", () => {
  const file = form.photo.files[0];
  if (file) { preview.src = URL.createObjectURL(file); preview.hidden = false; }
});

// Shrink big phone photos before upload (max 1024 px, JPEG). Smaller image = faster AI answer.
async function shrinkImage(file, maxSide = 1024) {
  const img = await createImageBitmap(file);
  const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(img.width * scale);
  canvas.height = Math.round(img.height * scale);
  canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = form.querySelector("button");
  button.disabled = true;
  resultBox.hidden = true;
  statusBox.hidden = false;
  statusBox.innerHTML = "Identifying your plant and writing advice… (can take up to a minute)";
  try {
    const body = new FormData(form);
    try {
      body.set("photo", await shrinkImage(form.photo.files[0]), "photo.jpg");
    } catch (_) { /* if shrinking fails, send the original photo */ }
    const resp = await fetch("/api/analyze", { method: "POST", body });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "Request failed");
    statusBox.hidden = true;
    render(data);
  } catch (err) {
    statusBox.innerHTML = `<p class="error">${esc(err.message)}</p>`;
  } finally {
    button.disabled = false;
  }
});

function render(data) {
  const id = data.identification;
  let html = `<h2>${esc(id.common_name || id.scientific_name)}</h2>
    <p><em>${esc(id.scientific_name)}</em>
    <span class="conf">— ${Math.round(id.confidence * 100)}% confidence, by ${esc(id.provider)}</span></p>`;
  if (data.message) html += `<p class="warn">${esc(data.message)}</p>`;
  const a = data.advice;
  if (a) {
    html += `<span class="tag">${a.method === "rag-llm" ? "AI advice from care database" : "Basic care sheet"}</span>
      <p>${esc(a.summary)}</p>
      <h3>💧 Watering</h3><p>${esc(a.watering)}</p>
      <h3>☀️ Light</h3><p>${esc(a.light)}</p>
      <h3>🌱 Tips</h3><ul>${a.tips.filter(Boolean).map((t) => `<li>${esc(t)}</li>`).join("")}</ul>`;
    if (a.warnings) html += `<h3>⚠️ Warnings</h3><p>${esc(a.warnings)}</p>`;
    html += `<p class="sources"><strong>Sources:</strong> ${a.sources.map(esc).join("; ")}</p>`;
  }
  resultBox.innerHTML = html;
  resultBox.hidden = false;
}
