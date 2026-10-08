"use strict";
const form = document.querySelector("form[data-recorder]");
if (form) {
  const start = document.getElementById("record-start");
  const stop = document.getElementById("record-stop");
  const notice = document.getElementById("record-notice");
  const preview = document.getElementById("record-preview");
  const file = document.getElementById("audio");
  const progress = document.getElementById("upload-progress");
  const submit = form.querySelector("button[type=submit]");
  let recorder, stream, recorded, previewURL, timer, ticker;
  const cleanup = () => {
    clearTimeout(timer); clearInterval(ticker);
    if (stream) stream.getTracks().forEach(track => track.stop());
    start.disabled = false; stop.disabled = true;
  };
  const available = form.dataset.recordingEnabled === "true" && navigator.mediaDevices?.getUserMedia && window.MediaRecorder;
  start.disabled = !available;
  if (!available) notice.textContent = "Trình duyệt chưa hỗ trợ ghi âm. Bạn vẫn có thể chọn tệp.";
  start.addEventListener("click", async () => {
    start.disabled = true;
    try {
      stream = await navigator.mediaDevices.getUserMedia({audio: true});
      const mime = ["audio/webm;codecs=opus", "audio/mp4"].find(type => MediaRecorder.isTypeSupported(type));
      if (!mime) throw new Error("unsupported");
      recorder = new MediaRecorder(stream, {mimeType: mime});
      const parts = [];
      let bytes = 0;
      recorded = null;
      recorder.addEventListener("dataavailable", event => {
        parts.push(event.data); bytes += event.data.size;
        if (bytes > Number(form.dataset.maxBytes) && recorder.state === "recording") recorder.stop();
      });
      recorder.addEventListener("stop", () => {
        const blob = new Blob(parts, {type: mime});
        recorded = new File([blob], mime.startsWith("audio/webm") ? "recording.webm" : "recording.mp4", {type: mime});
        if (previewURL) URL.revokeObjectURL(previewURL);
        previewURL = URL.createObjectURL(blob); preview.src = previewURL; preview.hidden = false;
        file.required = false; file.value = "";
        notice.textContent = "Đã ghi âm. Nghe lại trước khi nộp; bấm ghi lại nếu muốn thay thế.";
        cleanup();
      });
      recorder.addEventListener("error", () => { notice.textContent = "Không thể ghi âm. Hãy chọn tệp."; cleanup(); });
      recorder.start(1000); stop.disabled = false;
      const begun = Date.now();
      const maximum = Math.min(Number(form.dataset.maxSeconds), 300);
      ticker = setInterval(() => { notice.textContent = `Đang ghi: ${Math.floor((Date.now() - begun) / 1000)} / ${maximum} giây`; }, 250);
      timer = setTimeout(() => { if (recorder.state === "recording") recorder.stop(); }, maximum * 1000);
    } catch (_) {
      notice.textContent = "Không thể bật micro. Kiểm tra quyền trình duyệt hoặc chọn tệp âm thanh.";
      cleanup();
    }
  });
  stop.addEventListener("click", () => { if (recorder?.state === "recording") recorder.stop(); });
  file.addEventListener("change", () => { recorded = null; file.required = true; preview.hidden = true; });
  form.addEventListener("submit", event => {
    event.preventDefault();
    if (recorder?.state === "recording") { notice.textContent = "Dừng ghi âm trước khi nộp."; return; }
    const audio = recorded || file.files[0];
    if (!audio) { notice.textContent = "Ghi âm hoặc chọn tệp trước khi nộp."; return; }
    if (audio.size > Number(form.dataset.maxBytes)) { notice.textContent = "Tệp vượt giới hạn dung lượng."; return; }
    const payload = new FormData(form); payload.set("audio", audio);
    submit.disabled = true; progress.hidden = false; notice.textContent = "Đang gửi bài…";
    const request = new XMLHttpRequest();
    request.open("POST", "/api/student/responses");
    request.upload.addEventListener("progress", event => { if (event.lengthComputable) progress.value = 100 * event.loaded / event.total; });
    request.addEventListener("load", () => {
      try {
        const response = JSON.parse(request.responseText);
        if (request.status === 201 && response.response_id) {
          window.location.assign("/student/responses/" + encodeURIComponent(response.response_id)); return;
        }
        notice.textContent = "Không thể nộp bài: " + (response.error || "hãy kiểm tra dữ liệu và đăng nhập.");
      } catch (_) { notice.textContent = "Không thể nộp bài. Hãy thử lại."; }
      submit.disabled = false;
    });
    request.addEventListener("error", () => { notice.textContent = "Kết nối bị gián đoạn. Kiểm tra lịch sử bài trước khi gửi lại."; submit.disabled = false; });
    request.send(payload);
  });
  window.addEventListener("pagehide", () => { cleanup(); if (previewURL) URL.revokeObjectURL(previewURL); });
}
