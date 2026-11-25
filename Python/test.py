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





{% extends "base.html" %}
{% block content %}
<div class="pick-page scan-page--touch">
  <div class="pick-layout">

    <!-- 左：スキャン -->
    <section class="pick-col card">
      <h2 class="sec-title">スキャン</h2>
      <div class="scan-header">
        {% set active_step = "pick" %}
        {% include "_flow_steps.html" %}
        <input type="text" id="seal_id" class="scan-input" autofocus autocomplete="off" placeholder="シールをスキャン">
      </div>

      <div id="pick-warning" class="scan-warning" style="display:none;"></div>

      <button class="btn btn-danger btn-touch" id="exception-btn" style="display:none; width:100%;">
        手動でピックを完了にする
      </button>

      <button class="btn btn-clear" id="clear-btn" style="display:none;">クリア（最初からやり直す）</button>

      <!-- 例外理由パネル -->
      <div id="reason-panel" class="reason-panel" style="display:none;">
        <div class="reason-title">例外完了の理由を選択（バーコードをスキャン）</div>
        <div id="reason-warning" class="reason-warning"></div>
        <input type="text" id="reason-input" class="scan-input" autocomplete="off"
               placeholder="理由バーコードをスキャン (例: EXC01)">
        <div id="reason-list" class="reason-list"></div>
        <div id="reason-selected" class="reason-selected" style="display:none;"></div>
        <div class="reason-actions">
          <button class="btn btn-danger" id="reason-confirm" disabled>この理由でピック完了</button>
          <button class="btn" id="reason-cancel">キャンセル</button>
        </div>
      </div>
    </section>

    <!-- 右：ピック状況 -->
    <section class="pick-col card">
      <h2 class="sec-title">ピック状況</h2>
      <div id="group" class="group-box" style="display:none;"></div>
      <div id="pick-history" class="pick-history" style="display:none;"></div>
      <div id="seal_list" class="seal-list"></div>
    </section>

  </div>
</div>
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
  padding: 13px 14px;   /* タッチで押しやすい高さにする */
  cursor: pointer;
  font-size: 15px;
}
.reason-list .reason-item:hover { background: var(--orange-light); }
.reason-list .reason-item.selected { background: var(--orange-light); border-color: var(--orange-dark); }
.reason-list .reason-code { font-weight: 700; margin-right: 8px; color: var(--ink-3); }
.reason-selected { padding: 10px 12px; background: var(--orange-light); border-radius: 8px; margin-bottom: 10px; font-size: 15px; }
.reason-actions { display: flex; gap: 8px; }
.reason-actions .btn { flex: 1; height: 52px; font-size: 15px; }


  /* 警告時の画面点滅 */
@keyframes warningFlash {
  0%, 100% {
    background-color: transparent;
  }

  50% {
    background-color: rgba(255, 0, 0, 0.25);
  }
}

body.warning-flash {
  animation: warningFlash 0.4s ease-in-out 3;
}


{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/pickHistory.js') }}"></script>
<script src="{{ url_for('static', filename='js/scanWarning.js') }}"></script>
<script>
document.addEventListener('DOMContentLoaded', function () {
  // 作業台番号は base.html が読み込み時点で sessionStorage に保存済み。
  const station = sessionStorage.getItem('station');

  // テストモード：trueならテスト用、falseなら本番用
  const TEST_MODE = true;

  // 最初の操作で音声を準備する
document.addEventListener('pointerdown', prepareWarningAudio, {
    once: true
});

document.addEventListener('keydown', prepareWarningAudio, {
    once: true
});


  const input        = document.getElementById('seal_id');
  const sealList     = document.getElementById('seal_list');
  const groupDiv     = document.getElementById('group');
  const historyDiv   = document.getElementById('pick-history');
  const exceptionBtn = document.getElementById('exception-btn');

  const reasonPanel    = document.getElementById('reason-panel');
  const reasonInput    = document.getElementById('reason-input');
  const reasonListDiv  = document.getElementById('reason-list');
  const reasonSelected = document.getElementById('reason-selected');
  const reasonConfirm  = document.getElementById('reason-confirm');
  const reasonCancel   = document.getElementById('reason-cancel');
  const clearBtn       = document.getElementById('clear-btn');
  const warningDiv     = document.getElementById('pick-warning');
  const reasonWarning  = document.getElementById('reason-warning');

  function showReasonWarning(msg) { reasonWarning.textContent = msg || ''; }

  const { show: showWarning, clear: clearWarning } = ScanWarning.create(warningDiv, input);

  let currentGroup    = null;
  let reasons         = [];   // [{barcode, label}]
  let selectedReason  = null; // {barcode, label}

  input.focus();

  /* ── クリア（やり直し） ── */
  clearBtn.addEventListener('click', resetScreen);
  function resetScreen() {
    currentGroup = null;
    clearWarning();
    groupDiv.style.display = 'none';
    groupDiv.innerHTML = '';
    historyDiv.style.display = 'none';
    historyDiv.innerHTML = '';
    sealList.innerHTML = '';
    exceptionBtn.style.display = 'none';
    reasonPanel.style.display = 'none';
    clearBtn.style.display = 'none';
    input.value = '';
    input.focus();
  }

  /* ── 例外理由の読み込み ── */
    // テストモードでは理由リストを読み込まない
  if (!TEST_MODE) {
    fetch('/api/pick_exception_reasons')
      .then(r => r.json())
      .then(data => {
        reasons = data;
        reasonListDiv.innerHTML = '';

        reasons.forEach(rsn => {
          const div = document.createElement('div');
          div.className = 'reason-item';
          div.dataset.barcode = rsn.barcode;
          div.innerHTML = `<span class="reason-code">${rsn.barcode}</span>${rsn.label}`;
          div.addEventListener('click', () => selectReason(rsn));
          reasonListDiv.appendChild(div);
        });
      })
      .catch(err => console.error('理由リスト取得失敗', err));
  }

  /* ── 理由バーコードのスキャン（フォーカス離脱で確定） ── */
  // Tabキーによる確定の場合だけ、確定後にフォーカスを戻す（ボタンクリック等の
  // 他要因によるblurでは奪い返さない。でないとフォーカスの奪い合いが起きる）。
  let reasonTabConfirm = false;
  reasonInput.addEventListener('blur', function () {
    showReasonWarning('');
    const code = reasonInput.value.trim();
    reasonInput.value = '';
    if (!code) { if (reasonTabConfirm) reasonInput.focus(); reasonTabConfirm = false; return; }
    const rsn = reasons.find(r => r.barcode === code);
    if (!rsn) { showReasonWarning(`未知の理由バーコードです：${code}`); reasonInput.focus(); reasonTabConfirm = false; return; }
    selectReason(rsn);
    if (reasonTabConfirm) reasonInput.focus();
    reasonTabConfirm = false;
  });
  // Tabキーでページ外にフォーカスが逃げないよう、明示的にblurさせて確定する
  reasonInput.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    e.preventDefault();
    reasonTabConfirm = true;
    reasonInput.blur();
  });

  /* ── フォーカス離脱（Blur）で確定 ── */
  // 同上の理由で、Tabキーによる確定の場合だけ確定後にフォーカスを戻す。
  let scanTabConfirm = false;
  input.addEventListener('blur', function () {
    // 旧システムのバーコードには中間にスペースが混入しているため、
    // trim だけでなく全てのスペースを除去してから比較・送信する。
    const code = input.value.replace(/\s+/g, '');
    input.value = '';
    if (!code) { if (scanTabConfirm) input.focus(); scanTabConfirm = false; return; }
    if (!currentGroup) loadGroup(code);
    else markItemAsScanned(code);
    if (scanTabConfirm) input.focus();
    scanTabConfirm = false;
  });
  // Tabキーでページ外にフォーカスが逃げないよう、明示的にblurさせて確定する
  input.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    e.preventDefault();
    scanTabConfirm = true;
    input.blur();
  });

  /* ── 初回スキャン：グループ取得 ── */
  function loadGroup(code) {
    groupDiv.style.display = 'block';
    groupDiv.textContent = '読み込み中…';

    fetch(`/api/seal_records?name=${encodeURIComponent(code)}`)
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => {
        if (data.error) {
          groupDiv.textContent = data.error;
          return;
        }
        currentGroup = {
          id:               data.group.id,
          diagnosis_number: data.group.diagnosis_number,
          items:            data.items.map(i => ({ name: i.name, label: i.label, checked: false }))
        };
        renderGroup();
        PickHistory.render(historyDiv, currentGroup.id);
        exceptionBtn.style.display = '';
        clearBtn.style.display = '';
        markItemAsScanned(code);
      })
      .catch(err => {
        groupDiv.textContent = 'データ取得に失敗しました';
        console.error(err);
      });
  }

  /* ── スキャン処理（ローカルのみ） ── */
  function markItemAsScanned(code) {
    if (!currentGroup) return;
    const item = currentGroup.items.find(i => i.name === code);
        if (!item) {
    showWarningEffect();

    showWarning(`この案件のシールではありません: ${code}`);

    return;
}
    clearWarning();
    item.checked = true;
    renderGroup();
    if (currentGroup.items.every(i => i.checked)) completeGroup();
  }


  // =========================
// 警告音・画面点滅
// =========================

// 音声を管理
let warningAudioContext = null;

// 音声を準備する
async function prepareWarningAudio() {
    const AudioContextClass =
        window.AudioContext || window.webkitAudioContext;

    if (!AudioContextClass) return;

    if (!warningAudioContext) {
        warningAudioContext = new AudioContextClass();
    }

    if (warningAudioContext.state === 'suspended') {
        await warningAudioContext.resume();
    }
}

// 警告音を3回鳴らす
// 警告音を3回鳴らす
// 警告音を3回鳴らす
// 低音ブザー警告音
async function playWarningSound() {
    await prepareWarningAudio();

    if (!warningAudioContext) return;

    const audioContext = warningAudioContext;
    const now = audioContext.currentTime + 0.02;

    for (let i = 0; i < 3; i++) {
        const startTime = now + i * 0.55;

        const oscillator = audioContext.createOscillator();
        const gain = audioContext.createGain();

        // 低いブザー音
        oscillator.type = 'square';
        oscillator.frequency.setValueAtTime(90, startTime);
        oscillator.frequency.setValueAtTime(70, startTime + 0.3);

        // 音量
        gain.gain.setValueAtTime(0.01, startTime);
        gain.gain.linearRampToValueAtTime(0.5, startTime + 0.03);
        gain.gain.setValueAtTime(0.5, startTime + 0.3);
        gain.gain.linearRampToValueAtTime(0.01, startTime + 0.4);

        oscillator.connect(gain);
        gain.connect(audioContext.destination);

        oscillator.start(startTime);
        oscillator.stop(startTime + 0.42);
    }
}
// 音声と画面点滅を同時に開始
function showWarningEffect() {
    playWarningSound();

    document.body.classList.remove('warning-flash');
    void document.body.offsetWidth;
    document.body.classList.add('warning-flash');

    setTimeout(() => {
        document.body.classList.remove('warning-flash');
    }, 1300);
}

  /* ── 描画 ── */
  function renderGroup() {
    const total   = currentGroup.items.length;
    const scanned = currentGroup.items.filter(i => i.checked).length;
    groupDiv.style.display = 'block';
    groupDiv.innerHTML = `
      ${currentGroup.diagnosis_number}
      <div class="group-meta">${scanned} / ${total} スキャン済み</div>
    `;
    sealList.innerHTML = '';
    currentGroup.items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'seal-item' + (item.checked ? ' checked' : '');
      div.innerHTML = `<span class="seal-icon">${item.checked ? '✓' : '○'}</span><span class="seal-label">${item.label}</span><span class="seal-code">${item.name}</span>`;
      sealList.appendChild(div);
    });
  }

  /* ── ピック結果を送信（reasonBarcode 省略なら通常完了、指定すれば例外完了） ── */
  function pushPickRecord(reasonBarcode) {


        if (TEST_MODE) {
      console.log('テストモード：データベースへの記録をスキップしました');
      return Promise.resolve({});
    }


    const checkedCodes = currentGroup.items.filter(i => i.checked).map(i => i.name);
    return fetch('/api/push_pick_record', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        group_id: currentGroup.id,
        checked_codes: checkedCodes,
        reason_barcode: reasonBarcode,
        // station は文字列のまま送る（数値化すると "棚A" 等が NaN→null になり記録漏れする）
        station: station || null
      })
    }).then(r => r.json());
  }

  /* ── 通常完了 ── */
  function completeGroup() {
    pushPickRecord().then(d => { if (!d.error) showCompleted(); });
  }

  /* ── 例外完了：理由パネルを開く ── */
  exceptionBtn.addEventListener('click', () => {
    if (!currentGroup) return;
    showReasonWarning('');
    selectedReason = null;
    reasonConfirm.disabled = true;
    reasonSelected.style.display = 'none';
    reasonListDiv.querySelectorAll('.reason-item').forEach(el => el.classList.remove('selected'));
    reasonPanel.style.display = 'block';
    exceptionBtn.style.display = 'none';
    reasonInput.focus();
  });

  reasonCancel.addEventListener('click', () => {
    showReasonWarning('');
    reasonPanel.style.display = 'none';
    if (currentGroup) exceptionBtn.style.display = '';
    input.focus();
  });

  /* ── 理由確定 → 例外完了を送信 ── */
  reasonConfirm.addEventListener('click', () => {
    if (!currentGroup || !selectedReason) return;
    pushPickRecord(selectedReason.barcode)
      .then(d => {
        if (d.error) { showReasonWarning(`エラー: ${d.error}`); return; }
        reasonPanel.style.display = 'none';
        showCompleted();
      })
      .catch(err => { console.error(err); showReasonWarning('例外完了の記録に失敗しました'); });
  });

  /* ── 完了表示 ── */
  function showCompleted() {
    exceptionBtn.style.display = 'none';
    clearBtn.style.display = 'none';
    groupDiv.classList.add('completed');
    groupDiv.textContent = 'ピック完了';
    setTimeout(() => {
      groupDiv.classList.remove('completed');
      groupDiv.style.display = 'none';
      historyDiv.style.display = 'none';
      historyDiv.innerHTML = '';
      sealList.innerHTML = '';
      currentGroup = null;
    }, 2000);
  }



// テストモード用の仮データ
if (TEST_MODE) {
    currentGroup = {
        id: 'TEST001',
        diagnosis_number: 'テスト案件001',
        items: [
            {
                name: 'TEST-001',
                label: 'テスト用シール1',
                checked: false
            },
            {
                name: 'TEST-002',
                label: 'テスト用シール2',
                checked: false
            }
        ]
    };

    renderGroup();

    exceptionBtn.style.display = 'none';
    clearBtn.style.display = 'none';
}


});
</script>
{% endblock %}
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
