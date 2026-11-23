async function playWarningSound() {
  const message = document.getElementById("message");

  message.textContent = "⚠️ 診断番号が違います！";

  const ctx = new AudioContext();
  await ctx.resume();

  document.body.classList.add("scan-error-blink");

  for (let i = 0; i < 3; i++) {
    const osc = ctx.createOscillator();

    osc.frequency.value = 880;
    osc.connect(ctx.destination);

    const startTime = ctx.currentTime + i * 0.7;

    osc.start(startTime);
    osc.stop(startTime + 0.3);
  }

  setTimeout(() => {
    document.body.classList.remove("scan-error-blink");
    message.textContent = "";
    ctx.close();
  }, 3000);
}





if (!item) {
  showWarning(`この案件のシールではありません: ${code}`);
  playWarningSound();
  return;
}





.scan-error-blink {
  animation: scan-error-blink-animation 0.3s infinite;
}

{% endblock %}

{% block style %}
.pick-page { max-width: 1100px; margin: 0 auto; padding-top: 4px; }
.pick-layout {
  display: grid;
  grid-template-columns: minmax(340px, 460px) 1fr;
  gap: 16px;
  align-items: start;
}
.pick-col { min-width: 0; }

@media (max-width: 980px) {
  .pick-layout { grid-template-columns: 1fr; }
}

.reason-panel {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
  margin-top: 12px;
  background: #fff;
}
.reason-title { font-weight: 700; margin-bottom: 10px; font-size: 15px; }
.reason-warning {
  min-height: 20px;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #c0392b;
}
.reason-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 10px; }
.reason-list .reason-item {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 13px 14px;
  cursor: pointer;
  font-size: 15px;
}
.reason-list .reason-item:hover { background: var(--orange-light); }
.reason-list .reason-item.selected { background: var(--orange-light); border-color: var(--orange-dark); }
.reason-list .reason-code { font-weight: 700; margin-right: 8px; color: var(--ink-3); }
.reason-selected { padding: 10px 12px; background: var(--orange-light); border-radius: 8px; margin-bottom: 10px; font-size: 15px; }
.reason-actions { display: flex; gap: 8px; }
.reason-actions .btn { flex: 1; height: 52px; font-size: 15px; }

/* スキャン間違い時の画面点滅 */
.scan-error-blink {
  animation: scan-error-blink-animation 0.3s infinite;
}

@keyframes scan-error-blink-animation {
  0%, 100% {
    background-color: white;
  }
  50% {
    background-color: red;
  }
}
{% endblock %}
