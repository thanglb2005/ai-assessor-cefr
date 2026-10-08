"use strict";
for (const button of document.querySelectorAll("button[data-seek-second]")) {
  button.addEventListener("click", () => {
    const audio = document.querySelector("audio[controls]");
    const seconds = Number(button.dataset.seekSecond);
    if (!audio || !Number.isFinite(seconds) || seconds < 0) return;
    const seek = () => {
      audio.currentTime = seconds;
      audio.play().catch(() => {});
    };
    if (audio.readyState >= 1) seek();
    else { audio.addEventListener("loadedmetadata", seek, {once: true}); audio.load(); }
  });
}
