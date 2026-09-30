/**
 * MN DUBBER WEB PRO - Core Client Logic
 * Handles Video Upload, Real-Time Progress, Voice Auditions & PWA
 */

// Application State
const state = {
  selectedFile: null,
  uploadedFileId: null,
  currentTaskId: null,
  activeTab: 'studioTab',
  voices: [],
  serverIp: 'localhost',
  serverPort: 8000,
  ws: null,
  selectedLogoFile: null,
  uploadedLogoFileId: null,
  rawLogoDataUrl: null,
  logoPosition: 'top-right',
  logoX: 80,
  logoY: 5,
  blurY: 83,
  blurHeight: 13,
  blurX: 5,
  blurWidth: 90,
  customTextX: 35,
  customTextY: 5,
  isDemoPreview: false,
  currentTikTokData: null
};

// DOM Elements
const elements = {
  // Tabs
  navBtns: document.querySelectorAll('.nav-btn'),
  tabPanes: document.querySelectorAll('.tab-pane'),

  // Upload Zone
  dropZone: document.getElementById('dropZone'),
  videoFileInput: document.getElementById('videoFileInput'),
  browseFileBtn: document.getElementById('browseFileBtn'),
  dropZonePrompt: document.getElementById('dropZonePrompt'),
  filePreviewCard: document.getElementById('filePreviewCard'),
  sourceVideoPlayer: document.getElementById('sourceVideoPlayer'),
  previewFileName: document.getElementById('previewFileName'),
  previewFileSize: document.getElementById('previewFileSize'),
  removeFileBtn: document.getElementById('removeFileBtn'),

  // Upload Progress
  uploadProgressBarContainer: document.getElementById('uploadProgressBarContainer'),
  uploadProgressBar: document.getElementById('uploadProgressBar'),
  uploadStatusText: document.getElementById('uploadStatusText'),
  uploadPercentText: document.getElementById('uploadPercentText'),

  // Dubbing Settings
  voiceSelect: document.getElementById('voiceSelect'),
  testVoiceBtn: document.getElementById('testVoiceBtn'),
  rateSlider: document.getElementById('rateSlider'),
  rateValLabel: document.getElementById('rateValLabel'),
  pitchSlider: document.getElementById('pitchSlider'),
  pitchValLabel: document.getElementById('pitchValLabel'),
  bgMusicSlider: document.getElementById('bgMusicSlider'),
  bgMusicValLabel: document.getElementById('bgMusicValLabel'),
  dubVolSlider: document.getElementById('dubVolSlider'),
  dubVolValLabel: document.getElementById('dubVolValLabel'),
  startDubBtn: document.getElementById('startDubBtn'),

  // Processing View
  processingCard: document.getElementById('processingCard'),
  processStepTitle: document.getElementById('processStepTitle'),
  processStepDesc: document.getElementById('processStepDesc'),
  processPercentBadge: document.getElementById('processPercentBadge'),
  dubProgressBar: document.getElementById('dubProgressBar'),
  nodes: [
    document.getElementById('node1'),
    document.getElementById('node2'),
    document.getElementById('node3'),
    document.getElementById('node4'),
    document.getElementById('node5')
  ],

  // Result View
  resultCard: document.getElementById('resultCard'),
  resultVideoPlayer: document.getElementById('resultVideoPlayer'),
  downloadVideoBtn: document.getElementById('downloadVideoBtn'),
  downloadAudioBtn: document.getElementById('downloadAudioBtn'),
  downloadSrtBtn: document.getElementById('downloadSrtBtn'),
  dubAgainBtn: document.getElementById('dubAgainBtn'),

  // Voice Studio
  voiceTestText: document.getElementById('voiceTestText'),
  voiceTestSelect: document.getElementById('voiceTestSelect'),
  playVoiceTestBtn: document.getElementById('playVoiceTestBtn'),
  voiceTestAudioPlayer: document.getElementById('voiceTestAudioPlayer'),
  voiceCardsContainer: document.getElementById('voiceCardsContainer'),

  // Settings
  serverIpBadge: document.getElementById('serverIpBadge'),
  displayMobileUrl: document.getElementById('displayMobileUrl'),
  copyUrlBtn: document.getElementById('copyUrlBtn'),
  geminiKeyInput: document.getElementById('geminiKeyInput'),
  saveSettingsBtn: document.getElementById('saveSettingsBtn'),
  saveStatusMsg: document.getElementById('saveStatusMsg'),
  mobileShareBtn: document.getElementById('mobileShareBtn'),
  mobileShareModal: document.getElementById('mobileShareModal'),
  closeMobileModalBtn: document.getElementById('closeMobileModalBtn'),
  mobileQrImg: document.getElementById('mobileQrImg'),
  onlineLinkBox: document.getElementById('onlineLinkBox'),
  onlineUrlInput: document.getElementById('onlineUrlInput'),
  copyOnlineUrlBtn: document.getElementById('copyOnlineUrlBtn'),
  wifiUrlInput: document.getElementById('wifiUrlInput'),
  copyWifiUrlBtn: document.getElementById('copyWifiUrlBtn'),
  toastContainer: document.getElementById('toastContainer'),

  // Video Overlays (Logo, Blur, Custom Text)
  logoEnabledToggle: document.getElementById('logoEnabledToggle'),
  logoStatusBadge: document.getElementById('logoStatusBadge'),
  logoControlsPanel: document.getElementById('logoControlsPanel'),
  logoFileInput: document.getElementById('logoFileInput'),
  browseLogoBtn: document.getElementById('browseLogoBtn'),
  useAppLogoBtn: document.getElementById('useAppLogoBtn'),
  selectedLogoName: document.getElementById('selectedLogoName'),
  logoCornerButtons: document.querySelectorAll('#logoCornerButtons .corner-btn'),
  logoSizeSlider: document.getElementById('logoSizeSlider'),
  logoSizeVal: document.getElementById('logoSizeVal'),
  logoOpacitySlider: document.getElementById('logoOpacitySlider'),
  logoOpacityVal: document.getElementById('logoOpacityVal'),
  logoRemoveBgToggle: document.getElementById('logoRemoveBgToggle'),
  logoChromaColorPicker: document.getElementById('logoChromaColorPicker'),

  blurEnabledToggle: document.getElementById('blurEnabledToggle'),
  blurStatusBadge: document.getElementById('blurStatusBadge'),
  blurControlsPanel: document.getElementById('blurControlsPanel'),
  blurYSlider: document.getElementById('blurYSlider'),
  blurYVal: document.getElementById('blurYVal'),
  blurHeightSlider: document.getElementById('blurHeightSlider'),
  blurHeightVal: document.getElementById('blurHeightVal'),
  blurStrengthSlider: document.getElementById('blurStrengthSlider'),
  blurStrengthVal: document.getElementById('blurStrengthVal'),
  blurDarknessSlider: document.getElementById('blurDarknessSlider'),
  blurDarknessVal: document.getElementById('blurDarknessVal'),

  customTextEnabledToggle: document.getElementById('customTextEnabledToggle'),
  customTextStatusBadge: document.getElementById('customTextStatusBadge'),
  customTextControlsPanel: document.getElementById('customTextControlsPanel'),
  customTextInput: document.getElementById('customTextInput'),
  customTextPositionSelect: document.getElementById('customTextPositionSelect'),
  customTextSizeSlider: document.getElementById('customTextSizeSlider'),
  customTextSizeVal: document.getElementById('customTextSizeVal'),
  customTextBgToggle: document.getElementById('customTextBgToggle'),
  customTextColorPicker: document.getElementById('customTextColorPicker'),

  // Draggable Stage Elements
  videoPreviewWrapper: document.getElementById('videoPreviewWrapper'),
  videoStageBox: document.getElementById('videoStageBox'),
  chromaPresetBtns: document.querySelectorAll('.chroma-preset-btn'),
  videoPlaceholderCanvas: document.getElementById('videoPlaceholderCanvas'),
  overlayStage: document.getElementById('overlayStage'),
  previewBlurBox: document.getElementById('previewBlurBox'),
  blurResizeTopHandle: document.getElementById('blurResizeTopHandle'),
  blurResizeBottomHandle: document.getElementById('blurResizeBottomHandle'),
  previewCustomText: document.getElementById('previewCustomText'),
  previewCustomTextContent: document.getElementById('previewCustomTextContent'),
  previewLogo: document.getElementById('previewLogo'),
  previewLogoImg: document.getElementById('previewLogoImg'),
  previewLogoPlaceholder: document.getElementById('previewLogoPlaceholder'),
  scrollToPreviewBtn: document.getElementById('scrollToPreviewBtn'),

  // TikTok Downloader
  tiktokUrlInput: document.getElementById('tiktokUrlInput'),
  tiktokPasteBtn: document.getElementById('tiktokPasteBtn'),
  tiktokClearBtn: document.getElementById('tiktokClearBtn'),
  tiktokFetchBtn: document.getElementById('tiktokFetchBtn'),
  tiktokFetchSpinner: document.getElementById('tiktokFetchSpinner'),
  tiktokFetchIcon: document.getElementById('tiktokFetchIcon'),
  tiktokFetchText: document.getElementById('tiktokFetchText'),
  tiktokQuickDubBtn: document.getElementById('tiktokQuickDubBtn'),
  tiktokQuickDubSpinner: document.getElementById('tiktokQuickDubSpinner'),
  tiktokQuickDubText: document.getElementById('tiktokQuickDubText'),
  tiktokLoadingState: document.getElementById('tiktokLoadingState'),
  tiktokLoadingTitle: document.getElementById('tiktokLoadingTitle'),
  tiktokLoadingSubtitle: document.getElementById('tiktokLoadingSubtitle'),
  tiktokResultCard: document.getElementById('tiktokResultCard'),
  tiktokCoverImg: document.getElementById('tiktokCoverImg'),
  tiktokDurationBadge: document.getElementById('tiktokDurationBadge'),
  tiktokPlayPreviewBtn: document.getElementById('tiktokPlayPreviewBtn'),
  tiktokPreviewVideo: document.getElementById('tiktokPreviewVideo'),
  tiktokVideoTitle: document.getElementById('tiktokVideoTitle'),
  tiktokAuthorAvatar: document.getElementById('tiktokAuthorAvatar'),
  tiktokAuthorName: document.getElementById('tiktokAuthorName'),
  tiktokDurationTag: document.getElementById('tiktokDurationTag'),
  tiktokQualityTag: document.getElementById('tiktokQualityTag'),
  tiktokSizeTag: document.getElementById('tiktokSizeTag'),
  tiktokSendToDubBtn: document.getElementById('tiktokSendToDubBtn'),
  tiktokDirectDownloadBtn: document.getElementById('tiktokDirectDownloadBtn')
};

// =========================================================================
// Initialization
// =========================================================================
document.addEventListener('DOMContentLoaded', async () => {
  initTabs();
  initSliders();
  initVocalCutOptions();
  initVideoTools();
  initFileUpload();
  initVoiceAudition();
  initSettings();
  initTikTokDownloader();
  initMobileModalHandlers();
  registerPWA();

  // Load server info and voices
  await fetchServerInfo();
  await loadVoices();
});

// Toast notification helper
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  elements.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// =========================================================================
// Tabs Navigation
// =========================================================================
function initTabs() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      if (!targetTab) return;
      
      document.querySelectorAll('.nav-btn').forEach(b => {
        if (b.getAttribute('data-tab') === targetTab) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
      });

      elements.tabPanes.forEach(pane => {
        if (pane.id === targetTab) {
          pane.classList.remove('hidden');
        } else {
          pane.classList.add('hidden');
        }
      });
      state.activeTab = targetTab;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  elements.mobileShareBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    openMobileModal();
  });
}

function openMobileModal() {
  if (!elements.mobileShareModal) return;

  const wifiUrl = `http://${state.serverIp || window.location.hostname}:${state.serverPort || 8000}`;
  if (elements.wifiUrlInput) elements.wifiUrlInput.value = wifiUrl;

  const activeUrl = state.publicUrl || wifiUrl;
  if (state.publicUrl && elements.onlineLinkBox) {
    elements.onlineLinkBox.classList.remove('hidden');
    if (elements.onlineUrlInput) elements.onlineUrlInput.value = state.publicUrl;
  } else if (elements.onlineLinkBox) {
    elements.onlineLinkBox.classList.add('hidden');
  }

  // Generate QR code for instant camera scanning on phones
  if (elements.mobileQrImg) {
    elements.mobileQrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${encodeURIComponent(activeUrl)}`;
  }

  elements.mobileShareModal.classList.remove('hidden');
}

function initMobileModalHandlers() {
  elements.closeMobileModalBtn?.addEventListener('click', () => {
    elements.mobileShareModal?.classList.add('hidden');
  });

  elements.mobileShareModal?.addEventListener('click', (e) => {
    if (e.target === elements.mobileShareModal) {
      elements.mobileShareModal.classList.add('hidden');
    }
  });

  elements.copyOnlineUrlBtn?.addEventListener('click', async () => {
    const val = elements.onlineUrlInput?.value;
    if (!val) return;
    try {
      await navigator.clipboard.writeText(val);
      showToast("📋 បាន Copy Link Online រួចរាល់!", "success");
    } catch {
      elements.onlineUrlInput?.select();
      document.execCommand('copy');
      showToast("📋 បាន Copy Link Online រួចរាល់!", "success");
    }
  });

  elements.copyWifiUrlBtn?.addEventListener('click', async () => {
    const val = elements.wifiUrlInput?.value;
    if (!val) return;
    try {
      await navigator.clipboard.writeText(val);
      showToast("📋 បាន Copy Link Wi-Fi រួចរាល់!", "success");
    } catch {
      elements.wifiUrlInput?.select();
      document.execCommand('copy');
      showToast("📋 បាន Copy Link Wi-Fi រួចរាល់!", "success");
    }
  });
}

// =========================================================================
// Server Info, Mobile IP & Online Cloudflare Tunnel
// =========================================================================
async function fetchServerInfo() {
  try {
    const res = await fetch('/api/info');
    if (res.ok) {
      const data = await res.json();
      state.serverIp = data.localIp || window.location.hostname;
      state.serverPort = data.port || window.location.port || 8000;
      state.publicUrl = data.publicUrl || null;
      
      const fullUrl = `http://${state.serverIp}:${state.serverPort}`;
      if (state.publicUrl) {
        elements.serverIpBadge.innerHTML = `<span class="status-dot-pulse"></span> 🌐 Mobile Online`;
      } else {
        elements.serverIpBadge.textContent = `📱 ${state.serverIp}:${state.serverPort}`;
      }
      if (elements.displayMobileUrl) {
        elements.displayMobileUrl.textContent = state.publicUrl || fullUrl;
      }
    }
  } catch (err) {
    console.warn('Could not fetch server info:', err);
    if (elements.displayMobileUrl) {
      elements.displayMobileUrl.textContent = window.location.origin;
    }
  }
}

// =========================================================================
// Voices Catalog & Population
// =========================================================================
async function loadVoices() {
  try {
    const res = await fetch('/api/voices');
    if (res.ok) {
      const data = await res.json();
      state.voices = data.voices || [];
      populateVoiceSelectors(state.voices);
      renderVoiceCards(state.voices);
    }
  } catch (err) {
    console.warn('Failed to load voices from server:', err);
  }
}

function populateVoiceSelectors(voices) {
  elements.voiceSelect.innerHTML = '';
  elements.voiceTestSelect.innerHTML = '';

  voices.forEach(v => {
    const opt1 = document.createElement('option');
    opt1.value = v.id;
    opt1.textContent = `${v.name} (${v.lang})`;
    if (v.default) opt1.selected = true;
    elements.voiceSelect.appendChild(opt1);

    const opt2 = document.createElement('option');
    opt2.value = v.id;
    opt2.textContent = `${v.name} (${v.lang})`;
    if (v.default) opt2.selected = true;
    elements.voiceTestSelect.appendChild(opt2);
  });
}

function renderVoiceCards(voices) {
  elements.voiceCardsContainer.innerHTML = '';

  voices.forEach(v => {
    const card = document.createElement('div');
    card.className = 'voice-card';
    card.innerHTML = `
      <div class="voice-meta">
        <span class="voice-name">${v.name}</span>
        <span class="voice-lang">${v.lang} • ${v.gender}</span>
      </div>
      <button type="button" class="btn-play-voice" data-voice="${v.id}" data-sample="${encodeURIComponent(v.sample || 'សួស្តី')}">
        ▶ ស្តាប់គំរូ
      </button>
    `;

    card.querySelector('.btn-play-voice').addEventListener('click', (e) => {
      const voiceId = e.currentTarget.getAttribute('data-voice');
      const sampleText = decodeURIComponent(e.currentTarget.getAttribute('data-sample'));
      playVoiceSample(sampleText, voiceId);
    });

    elements.voiceCardsContainer.appendChild(card);
  });
}

// =========================================================================
// Sliders & Live Labels
// =========================================================================
function initSliders() {
  elements.rateSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value, 10);
    elements.rateValLabel.textContent = val === 0 ? 'ធម្មតា (+0%)' : (val > 0 ? `+${val}%` : `${val}%`);
  });

  elements.pitchSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value, 10);
    elements.pitchValLabel.textContent = val === 0 ? 'ធម្មតា (+0Hz)' : (val > 0 ? `+${val}Hz` : `${val}Hz`);
  });

  elements.bgMusicSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    const pct = Math.round(val * 100);
    elements.bgMusicValLabel.textContent = val === 0 ? '0% (បិទ)' : `${pct}%`;
  });

  elements.dubVolSlider.addEventListener('input', (e) => {
    const pct = Math.round(parseFloat(e.target.value) * 100);
    elements.dubVolValLabel.textContent = `${pct}%`;
  });
}

function initVocalCutOptions() {
  const vocalRadios = document.querySelectorAll('input[name="vocalCutMode"]');
  vocalRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.value === 'clean-voice') {
        elements.bgMusicSlider.value = 0;
        elements.bgMusicValLabel.textContent = '0% (បិទ)';
      } else if (parseFloat(elements.bgMusicSlider.value) === 0) {
        elements.bgMusicSlider.value = 0.15;
        elements.bgMusicValLabel.textContent = '15%';
      }
    });
  });
}

// =========================================================================
// Interactive Draggable Overlays Engine & Studio Video Tools
// =========================================================================
function activateDemoPreviewIfEmpty() {
  if (!state.selectedFile && elements.filePreviewCard) {
    elements.dropZonePrompt.classList.add('hidden');
    elements.filePreviewCard.classList.remove('hidden');
    elements.videoPlaceholderCanvas?.classList.remove('hidden');
    elements.sourceVideoPlayer.style.display = 'none';
    state.isDemoPreview = true;
  }
}

function makeDraggable(element, { onDrag, onDragStart, onDragEnd, boundsContainer }) {
  if (!element) return;
  let isDragging = false;
  let startPointerX = 0;
  let startPointerY = 0;
  let startElemLeft = 0;
  let startElemTop = 0;

  function onPointerDown(e) {
    if (e.target.classList.contains('overlay-drag-handle-top') || 
        e.target.classList.contains('overlay-drag-handle-bottom')) {
      return;
    }
    isDragging = true;
    element.classList.add('dragging');

    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    startPointerX = clientX;
    startPointerY = clientY;

    startElemLeft = element.offsetLeft;
    startElemTop = element.offsetTop;

    if (onDragStart) onDragStart();
    e.preventDefault();
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;

    const deltaX = clientX - startPointerX;
    const deltaY = clientY - startPointerY;

    const container = boundsContainer();
    if (!container) return;
    const containerW = container.clientWidth || 1;
    const containerH = container.clientHeight || 1;

    let newLeft = startElemLeft + deltaX;
    let newTop = startElemTop + deltaY;

    const elemW = element.offsetWidth;
    const elemH = element.offsetHeight;
    newLeft = Math.max(0, Math.min(newLeft, containerW - elemW));
    newTop = Math.max(0, Math.min(newTop, containerH - elemH));

    const xPercent = (newLeft / containerW) * 100;
    const yPercent = (newTop / containerH) * 100;

    element.style.left = `${xPercent}%`;
    element.style.top = `${yPercent}%`;
    element.style.right = 'auto';
    element.style.bottom = 'auto';
    element.style.transform = 'none';

    if (onDrag) onDrag({ xPercent, yPercent, newLeft, newTop });
  }

  function onPointerUp() {
    if (!isDragging) return;
    isDragging = false;
    element.classList.remove('dragging');
    if (onDragEnd) onDragEnd();
  }

  element.addEventListener('mousedown', onPointerDown);
  element.addEventListener('touchstart', onPointerDown, { passive: false });

  window.addEventListener('mousemove', onPointerMove);
  window.addEventListener('touchmove', onPointerMove, { passive: false });

  window.addEventListener('mouseup', onPointerUp);
  window.addEventListener('touchend', onPointerUp);
}

function makeVerticalResizable(handle, { onResize, boundsContainer, direction }) {
  if (!handle) return;
  let isResizing = false;
  let startY = 0;
  let startHeight = 0;
  let startTop = 0;

  function onPointerDown(e) {
    e.stopPropagation();
    isResizing = true;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    startY = clientY;
    startHeight = elements.previewBlurBox.offsetHeight;
    startTop = elements.previewBlurBox.offsetTop;
    e.preventDefault();
  }

  function onPointerMove(e) {
    if (!isResizing) return;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    const deltaY = clientY - startY;
    const container = boundsContainer();
    if (!container) return;
    const containerH = container.clientHeight || 1;

    if (direction === 'bottom') {
      let newH = startHeight + deltaY;
      newH = Math.max(20, Math.min(newH, containerH - startTop));
      const hPercent = (newH / containerH) * 100;
      elements.previewBlurBox.style.height = `${hPercent}%`;
      if (onResize) onResize({ hPercent });
    } else if (direction === 'top') {
      let newTop = startTop + deltaY;
      let newH = startHeight - deltaY;
      if (newTop >= 0 && newH >= 20) {
        elements.previewBlurBox.style.top = `${(newTop / containerH) * 100}%`;
        elements.previewBlurBox.style.height = `${(newH / containerH) * 100}%`;
        if (onResize) onResize({ yPercent: (newTop / containerH) * 100, hPercent: (newH / containerH) * 100 });
      }
    }
  }

  function onPointerUp() {
    isResizing = false;
  }

  handle.addEventListener('mousedown', onPointerDown);
  handle.addEventListener('touchstart', onPointerDown, { passive: false });
  window.addEventListener('mousemove', onPointerMove);
  window.addEventListener('touchmove', onPointerMove, { passive: false });
  window.addEventListener('mouseup', onPointerUp);
  window.addEventListener('touchend', onPointerUp);
}

function dataUrlToBlob(dataUrl) {
  return new Promise((resolve) => {
    const parts = dataUrl.split(',');
    const mime = parts[0].match(/:(.*?);/)[1];
    const bstr = atob(parts[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    resolve(new Blob([u8arr], { type: mime }));
  });
}

function detectGreenScreenFromDataUrl(dataUrl) {
  return new Promise((resolve) => {
    if (!dataUrl) return resolve(null);
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        canvas.width = Math.min(200, img.naturalWidth || img.width || 100);
        canvas.height = Math.min(200, img.naturalHeight || img.height || 100);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const w = canvas.width;
        const h = canvas.height;

        // Sample corner points (top-left, top-right, bottom-left, bottom-right)
        const corners = [
          ctx.getImageData(4, 4, 1, 1).data,
          ctx.getImageData(w - 5, 4, 1, 1).data,
          ctx.getImageData(4, h - 5, 1, 1).data,
          ctx.getImageData(w - 5, h - 5, 1, 1).data
        ];

        let greenHits = 0;
        let sumR = 0, sumG = 0, sumB = 0;
        for (const c of corners) {
          const r = c[0], g = c[1], b = c[2], a = c[3];
          if (a > 100 && g > 110 && g > r * 1.3 && g > b * 1.3) {
            greenHits++;
            sumR += r; sumG += g; sumB += b;
          }
        }

        if (greenHits >= 2) {
          const avgR = Math.round(sumR / greenHits);
          const avgG = Math.round(sumG / greenHits);
          const avgB = Math.round(sumB / greenHits);
          const toHex = (n) => n.toString(16).padStart(2, '0');
          return resolve(`#${toHex(avgR)}${toHex(avgG)}${toHex(avgB)}`);
        }
      } catch (e) {
        console.warn("detectGreenScreen error:", e);
      }
      resolve(null);
    };
    img.onerror = () => resolve(null);
    img.src = dataUrl;
  });
}

function processChromaKey(dataUrl, colorHex) {
  return new Promise((resolve) => {
    if (!dataUrl) return resolve('');
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.naturalWidth || img.width || 200;
      canvas.height = img.naturalHeight || img.height || 200;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);

      if (elements.logoRemoveBgToggle && elements.logoRemoveBgToggle.checked) {
        const hex = (colorHex || '#00FF00').replace('#', '');
        const kr = parseInt(hex.substring(0, 2), 16) || 0;
        const kg = parseInt(hex.substring(2, 4), 16) || 255;
        const kb = parseInt(hex.substring(4, 6), 16) || 0;

        const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const d = imgData.data;
        const isGreenKey = (kr < 85 && kg > 150 && kb < 85);

        for (let i = 0; i < d.length; i += 4) {
          const r = d[i], g = d[i+1], b = d[i+2];
          // Euclidean color distance
          const diff = Math.sqrt((r - kr)**2 + (g - kg)**2 + (b - kb)**2);
          
          // Green screen spill detection (catches variations and edges)
          const isGreenSpill = isGreenKey && (g > 95) && (g > r * 1.25) && (g > b * 1.25);

          if (diff < 95 || isGreenSpill) {
            d[i+3] = 0;
          } else if (diff < 140) {
            d[i+3] = Math.round(255 * ((diff - 95) / 45));
          }
        }
        ctx.putImageData(imgData, 0, 0);
      }
      resolve(canvas.toDataURL('image/png'));
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

function initVideoTools() {
  const getContainer = () => elements.overlayStage || elements.videoStageBox || elements.videoPreviewWrapper;

  // Auto-adapt exact video stage dimensions (no black bars!)
  function syncVideoStageDimensions() {
    const video = elements.sourceVideoPlayer;
    if (!video || !elements.videoStageBox) return;
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (vw && vh) {
      const wrapperW = elements.videoPreviewWrapper?.clientWidth || 360;
      const maxH = Math.min(480, Math.round(window.innerHeight * 0.55));
      const aspect = vw / vh;

      let renderH = maxH;
      let renderW = renderH * aspect;
      if (renderW > wrapperW) {
        renderW = wrapperW;
        renderH = renderW / aspect;
      }
      elements.videoStageBox.style.width = `${Math.round(renderW)}px`;
      elements.videoStageBox.style.height = `${Math.round(renderH)}px`;
    }
  }

  elements.sourceVideoPlayer?.addEventListener('loadedmetadata', syncVideoStageDimensions);
  elements.sourceVideoPlayer?.addEventListener('canplay', syncVideoStageDimensions);
  elements.sourceVideoPlayer?.addEventListener('play', syncVideoStageDimensions);
  window.addEventListener('resize', syncVideoStageDimensions);

  // Jump to preview button
  elements.scrollToPreviewBtn?.addEventListener('click', () => {
    activateDemoPreviewIfEmpty();
    syncVideoStageDimensions();
    elements.filePreviewCard?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (elements.videoPreviewWrapper) {
      elements.videoPreviewWrapper.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
      elements.videoPreviewWrapper.style.borderColor = '#38bdf8';
      elements.videoPreviewWrapper.style.boxShadow = '0 0 25px rgba(56, 189, 248, 0.7)';
      setTimeout(() => {
        elements.videoPreviewWrapper.style.borderColor = '';
        elements.videoPreviewWrapper.style.boxShadow = '';
      }, 1200);
    }
  });

  // Chroma color presets (Green, Black, White, Blue)
  elements.chromaPresetBtns?.forEach(btn => {
    btn.addEventListener('click', async () => {
      const color = btn.getAttribute('data-color') || '#00FF00';
      if (elements.logoChromaColorPicker) elements.logoChromaColorPicker.value = color;
      if (state.rawLogoDataUrl && elements.logoRemoveBgToggle?.checked) {
        const processedUrl = await processChromaKey(state.rawLogoDataUrl, color);
        if (elements.previewLogoImg) elements.previewLogoImg.src = processedUrl;
      }
    });
  });

  // ---------------------------------------------------------
  // 1. Logo Overlay Setup
  // ---------------------------------------------------------
  function applyLogoPresetCorner(pos) {
    state.logoPosition = pos;
    elements.logoCornerButtons?.forEach(b => {
      const isCur = b.getAttribute('data-pos') === pos;
      b.style.background = isCur ? '#3b82f6' : '';
      b.style.color = isCur ? '#ffffff' : '';
    });

    if (pos === 'top-left') {
      state.logoX = 5;
      state.logoY = 5;
    } else if (pos === 'bottom-right') {
      state.logoX = 80;
      state.logoY = 78;
    } else if (pos === 'bottom-left') {
      state.logoX = 5;
      state.logoY = 78;
    } else {
      // top-right
      state.logoX = 80;
      state.logoY = 5;
    }
    if (elements.previewLogo) {
      elements.previewLogo.style.left = `${state.logoX}%`;
      elements.previewLogo.style.top = `${state.logoY}%`;
      elements.previewLogo.style.right = 'auto';
      elements.previewLogo.style.bottom = 'auto';
    }
  }

  // Initial logo styles
  if (elements.previewLogo) {
    elements.previewLogo.style.left = `${state.logoX}%`;
    elements.previewLogo.style.top = `${state.logoY}%`;
    elements.previewLogo.style.width = `${elements.logoSizeSlider ? elements.logoSizeSlider.value : 14}%`;
    elements.previewLogo.style.opacity = `${(elements.logoOpacitySlider ? elements.logoOpacitySlider.value : 90) / 100}`;
  }

  elements.logoEnabledToggle?.addEventListener('change', (e) => {
    const on = e.target.checked;
    if (elements.logoControlsPanel) elements.logoControlsPanel.style.display = on ? 'block' : 'none';
    if (elements.logoStatusBadge) {
      elements.logoStatusBadge.textContent = on ? 'បើក' : 'បិទ';
      elements.logoStatusBadge.style.color = on ? '#38bdf8' : '#94a3b8';
    }

    if (on) {
      elements.previewLogo?.classList.remove('hidden');
      activateDemoPreviewIfEmpty();
    } else {
      elements.previewLogo?.classList.add('hidden');
    }
  });

  elements.browseLogoBtn?.addEventListener('click', () => {
    elements.logoFileInput?.click();
  });

  elements.logoFileInput?.addEventListener('change', async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const f = e.target.files[0];
      state.selectedLogoFile = f;
      if (elements.selectedLogoName) elements.selectedLogoName.textContent = f.name;

      const reader = new FileReader();
      reader.onload = async (re) => {
        state.rawLogoDataUrl = re.target.result;

        // Auto-detect green screen from image corners
        const detectedGreen = await detectGreenScreenFromDataUrl(state.rawLogoDataUrl);
        if (detectedGreen) {
          if (elements.logoRemoveBgToggle) elements.logoRemoveBgToggle.checked = true;
          if (elements.logoChromaColorPicker) elements.logoChromaColorPicker.value = detectedGreen;
          showToast("✨ បានរកឃើញ Green Screen ដោយស្វ័យប្រវត្តិ និងបានលុប Background រួចរាល់!", "success");
        }

        const processedUrl = await processChromaKey(
          state.rawLogoDataUrl,
          elements.logoChromaColorPicker?.value || '#00FF00'
        );
        if (elements.previewLogoImg) {
          elements.previewLogoImg.src = processedUrl;
          elements.previewLogoImg.classList.remove('hidden');
        }
        elements.previewLogoPlaceholder?.classList.add('hidden');

        // Convert the transparent image to PNG file for server upload
        try {
          const blob = await dataUrlToBlob(processedUrl);
          const uploadFileObj = new File([blob], f.name.replace(/\.[^.]+$/, '') + '_clean.png', { type: 'image/png' });
          state.selectedLogoFile = uploadFileObj;
          state.uploadedLogoFileId = await uploadFileWithProgress(uploadFileObj);
          showToast("Logo ត្រូវបាន Upload ជោគជ័យ!", "success");
        } catch (err) {
          console.warn("Transparent upload error:", err);
          state.uploadedLogoFileId = await uploadFileWithProgress(f);
        }
      };
      reader.readAsDataURL(f);
    }
  });

  // Quick Action: Use App Logo
  elements.useAppLogoBtn?.addEventListener('click', async () => {
    try {
      showToast("កំពុងទាញយក Logo កម្មវិធី MN DUBBER PRO...", "info");
      const res = await fetch('/icons/logo_transparent.png');
      if (!res.ok) throw new Error("Could not load app logo");
      const blob = await res.blob();
      const fileObj = new File([blob], 'mn_dubber_logo.png', { type: 'image/png' });
      state.selectedLogoFile = fileObj;
      if (elements.selectedLogoName) elements.selectedLogoName.textContent = 'MN Dubber Pro Logo';

      const logoUrl = '/icons/logo_transparent.png';
      state.rawLogoDataUrl = logoUrl;
      if (elements.previewLogoImg) {
        elements.previewLogoImg.src = logoUrl;
        elements.previewLogoImg.classList.remove('hidden');
      }
      elements.previewLogoPlaceholder?.classList.add('hidden');

      // Auto enable logo panel and preview
      if (elements.logoEnabledToggle) elements.logoEnabledToggle.checked = true;
      if (elements.logoControlsPanel) elements.logoControlsPanel.style.display = 'block';
      if (elements.logoStatusBadge) {
        elements.logoStatusBadge.textContent = 'បើក';
        elements.logoStatusBadge.style.color = '#38bdf8';
      }
      elements.previewLogo?.classList.remove('hidden');
      activateDemoPreviewIfEmpty();

      state.uploadedLogoFileId = await uploadFileWithProgress(fileObj);
      showToast("✨ បានកំណត់ Logo កម្មវិធី MN DUBBER PRO រួចរាល់!", "success");
    } catch (err) {
      console.error("Use app logo error:", err);
      showToast("មិនអាចកំណត់ Logo កម្មវិធីបានទេ: " + err.message, "error");
    }
  });

  elements.logoCornerButtons?.forEach(btn => {
    btn.addEventListener('click', () => {
      const pos = btn.getAttribute('data-pos') || 'top-right';
      applyLogoPresetCorner(pos);
    });
  });

  elements.logoSizeSlider?.addEventListener('input', (e) => {
    if (elements.logoSizeVal) elements.logoSizeVal.textContent = `${e.target.value}%`;
    if (elements.previewLogo) {
      elements.previewLogo.style.width = `${e.target.value}%`;
    }
  });

  elements.logoOpacitySlider?.addEventListener('input', (e) => {
    if (elements.logoOpacityVal) elements.logoOpacityVal.textContent = `${e.target.value}%`;
    if (elements.previewLogo) {
      elements.previewLogo.style.opacity = `${e.target.value / 100}`;
    }
  });

  elements.logoRemoveBgToggle?.addEventListener('change', async () => {
    if (state.rawLogoDataUrl) {
      const processedUrl = await processChromaKey(
        state.rawLogoDataUrl,
        elements.logoChromaColorPicker?.value || '#00FF00'
      );
      if (elements.previewLogoImg) {
        elements.previewLogoImg.src = processedUrl;
      }
    }
  });

  elements.logoChromaColorPicker?.addEventListener('input', async (e) => {
    if (state.rawLogoDataUrl && elements.logoRemoveBgToggle?.checked) {
      const processedUrl = await processChromaKey(state.rawLogoDataUrl, e.target.value);
      if (elements.previewLogoImg) {
        elements.previewLogoImg.src = processedUrl;
      }
    }
  });

  // Make Logo Draggable
  makeDraggable(elements.previewLogo, {
    boundsContainer: getContainer,
    onDrag: ({ xPercent, yPercent }) => {
      state.logoX = Math.round(xPercent);
      state.logoY = Math.round(yPercent);
      elements.logoCornerButtons?.forEach(b => {
        b.style.background = '';
        b.style.color = '';
      });
    }
  });

  // ---------------------------------------------------------
  // 2. Blur Subtitle Box Setup
  // ---------------------------------------------------------
  if (elements.previewBlurBox) {
    elements.previewBlurBox.style.top = `${state.blurY}%`;
    elements.previewBlurBox.style.height = `${state.blurHeight}%`;
    elements.previewBlurBox.style.backdropFilter = `blur(${elements.blurStrengthSlider ? elements.blurStrengthSlider.value : 15}px)`;
    elements.previewBlurBox.style.webkitBackdropFilter = `blur(${elements.blurStrengthSlider ? elements.blurStrengthSlider.value : 15}px)`;
    elements.previewBlurBox.style.background = `rgba(0, 0, 0, ${(elements.blurDarknessSlider ? elements.blurDarknessSlider.value : 40) / 100})`;
  }

  elements.blurEnabledToggle?.addEventListener('change', (e) => {
    const on = e.target.checked;
    if (elements.blurControlsPanel) elements.blurControlsPanel.style.display = on ? 'block' : 'none';
    if (elements.blurStatusBadge) {
      elements.blurStatusBadge.textContent = on ? 'បើក' : 'បិទ';
      elements.blurStatusBadge.style.color = on ? '#38bdf8' : '#94a3b8';
    }

    if (on) {
      elements.previewBlurBox?.classList.remove('hidden');
      activateDemoPreviewIfEmpty();
    } else {
      elements.previewBlurBox?.classList.add('hidden');
    }
  });

  elements.blurYSlider?.addEventListener('input', (e) => {
    state.blurY = parseInt(e.target.value, 10);
    if (elements.blurYVal) elements.blurYVal.textContent = `${state.blurY}%`;
    if (elements.previewBlurBox) {
      elements.previewBlurBox.style.top = `${state.blurY}%`;
    }
  });

  elements.blurHeightSlider?.addEventListener('input', (e) => {
    state.blurHeight = parseInt(e.target.value, 10);
    if (elements.blurHeightVal) elements.blurHeightVal.textContent = `${state.blurHeight}%`;
    if (elements.previewBlurBox) {
      elements.previewBlurBox.style.height = `${state.blurHeight}%`;
    }
  });

  elements.blurStrengthSlider?.addEventListener('input', (e) => {
    if (elements.blurStrengthVal) elements.blurStrengthVal.textContent = `${e.target.value}`;
    if (elements.previewBlurBox) {
      elements.previewBlurBox.style.backdropFilter = `blur(${e.target.value}px)`;
      elements.previewBlurBox.style.webkitBackdropFilter = `blur(${e.target.value}px)`;
    }
  });

  elements.blurDarknessSlider?.addEventListener('input', (e) => {
    if (elements.blurDarknessVal) elements.blurDarknessVal.textContent = `${e.target.value}%`;
    if (elements.previewBlurBox) {
      elements.previewBlurBox.style.background = `rgba(0, 0, 0, ${e.target.value / 100})`;
    }
  });

  // Make Blur Box Draggable (Vertically and Horizontally)
  makeDraggable(elements.previewBlurBox, {
    boundsContainer: getContainer,
    onDrag: ({ xPercent, yPercent }) => {
      state.blurY = Math.round(yPercent);
      state.blurX = Math.round(xPercent);
      if (elements.blurYSlider) elements.blurYSlider.value = state.blurY;
      if (elements.blurYVal) elements.blurYVal.textContent = `${state.blurY}%`;
    }
  });

  // Make Blur Box Resizable with Handles
  makeVerticalResizable(elements.blurResizeBottomHandle, {
    boundsContainer: getContainer,
    direction: 'bottom',
    onResize: ({ hPercent }) => {
      state.blurHeight = Math.round(hPercent);
      if (elements.blurHeightSlider) elements.blurHeightSlider.value = state.blurHeight;
      if (elements.blurHeightVal) elements.blurHeightVal.textContent = `${state.blurHeight}%`;
    }
  });

  makeVerticalResizable(elements.blurResizeTopHandle, {
    boundsContainer: getContainer,
    direction: 'top',
    onResize: ({ yPercent, hPercent }) => {
      if (yPercent != null) {
        state.blurY = Math.round(yPercent);
        if (elements.blurYSlider) elements.blurYSlider.value = state.blurY;
        if (elements.blurYVal) elements.blurYVal.textContent = `${state.blurY}%`;
      }
      if (hPercent != null) {
        state.blurHeight = Math.round(hPercent);
        if (elements.blurHeightSlider) elements.blurHeightSlider.value = state.blurHeight;
        if (elements.blurHeightVal) elements.blurHeightVal.textContent = `${state.blurHeight}%`;
      }
    }
  });

  // ---------------------------------------------------------
  // 3. Custom Text Banner Setup
  // ---------------------------------------------------------
  function applyCustomTextPresetPosition(pos) {
    if (pos === 'top-left') {
      state.customTextX = 5;
      state.customTextY = 5;
    } else if (pos === 'top-right') {
      state.customTextX = 65;
      state.customTextY = 5;
    } else if (pos === 'bottom-center') {
      state.customTextX = 35;
      state.customTextY = 88;
    } else if (pos === 'bottom-left') {
      state.customTextX = 5;
      state.customTextY = 88;
    } else if (pos === 'bottom-right') {
      state.customTextX = 65;
      state.customTextY = 88;
    } else {
      // top-center
      state.customTextX = 35;
      state.customTextY = 5;
    }
    if (elements.previewCustomText) {
      elements.previewCustomText.style.left = `${state.customTextX}%`;
      elements.previewCustomText.style.top = `${state.customTextY}%`;
      elements.previewCustomText.style.right = 'auto';
      elements.previewCustomText.style.bottom = 'auto';
    }
  }

  // Initial text styles
  if (elements.previewCustomText) {
    elements.previewCustomText.style.left = `${state.customTextX}%`;
    elements.previewCustomText.style.top = `${state.customTextY}%`;
    if (elements.previewCustomTextContent) {
      elements.previewCustomTextContent.textContent = elements.customTextInput?.value || 'សម្រាយរឿង';
      elements.previewCustomTextContent.style.fontSize = `${(elements.customTextSizeSlider ? elements.customTextSizeSlider.value : 26) * 0.7}px`;
      elements.previewCustomTextContent.style.color = elements.customTextColorPicker ? elements.customTextColorPicker.value : '#FFFFFF';
    }
    elements.previewCustomText.style.background = elements.customTextBgToggle?.checked ? 'rgba(0,0,0,0.65)' : 'transparent';
  }

  elements.customTextEnabledToggle?.addEventListener('change', (e) => {
    const on = e.target.checked;
    if (elements.customTextControlsPanel) elements.customTextControlsPanel.style.display = on ? 'block' : 'none';
    if (elements.customTextStatusBadge) {
      elements.customTextStatusBadge.textContent = on ? 'បើក' : 'បិទ';
      elements.customTextStatusBadge.style.color = on ? '#38bdf8' : '#94a3b8';
    }

    if (on) {
      elements.previewCustomText?.classList.remove('hidden');
      activateDemoPreviewIfEmpty();
    } else {
      elements.previewCustomText?.classList.add('hidden');
    }
  });

  elements.customTextInput?.addEventListener('input', (e) => {
    if (elements.previewCustomTextContent) {
      elements.previewCustomTextContent.textContent = e.target.value.trim() || 'សម្រាយរឿង';
    }
  });

  elements.customTextPositionSelect?.addEventListener('change', (e) => {
    applyCustomTextPresetPosition(e.target.value);
  });

  elements.customTextSizeSlider?.addEventListener('input', (e) => {
    if (elements.customTextSizeVal) elements.customTextSizeVal.textContent = `${e.target.value}px`;
    if (elements.previewCustomTextContent) {
      elements.previewCustomTextContent.style.fontSize = `${e.target.value * 0.7}px`;
    }
  });

  elements.customTextColorPicker?.addEventListener('input', (e) => {
    if (elements.previewCustomTextContent) {
      elements.previewCustomTextContent.style.color = e.target.value;
    }
  });

  elements.customTextBgToggle?.addEventListener('change', (e) => {
    if (elements.previewCustomText) {
      elements.previewCustomText.style.background = e.target.checked ? 'rgba(0,0,0,0.65)' : 'transparent';
      elements.previewCustomText.style.border = e.target.checked ? '2px dashed rgba(16, 185, 129, 0.9)' : '2px dashed rgba(255, 255, 255, 0.4)';
    }
  });

  // Make Custom Text Draggable
  makeDraggable(elements.previewCustomText, {
    boundsContainer: getContainer,
    onDrag: ({ xPercent, yPercent }) => {
      state.customTextX = Math.round(xPercent);
      state.customTextY = Math.round(yPercent);
    }
  });
}

// =========================================================================
// File Upload & Preview
// =========================================================================
function initFileUpload() {
  const dropZone = elements.dropZone;
  const fileInput = elements.videoFileInput;

  elements.browseFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropZone.addEventListener('click', () => {
    if (!state.selectedFile) {
      fileInput.click();
    }
  });

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleSelectedFile(fileInput.files[0]);
    }
  });

  elements.removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileSelection();
  });

  elements.dubAgainBtn.addEventListener('click', () => {
    resetFileSelection();
    elements.resultCard.classList.add('hidden');
    elements.processingCard.classList.add('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  elements.startDubBtn.addEventListener('click', () => {
    if (!state.selectedFile) {
      showToast('សូមជ្រើសរើសវីដេអូជាមុនសិន!', 'info');
      elements.videoFileInput.click();
      return;
    }
    startDubbingProcess();
  });
}

let preUploadPromise = null;

function startBackgroundPreUpload(file) {
  if (!file) return;
  state.uploadedFileId = null;
  const badge = document.getElementById('previewUploadBadge');
  if (badge) {
    badge.textContent = '☁️ កំពុង Upload... 0%';
    badge.style.display = 'inline-block';
    badge.style.color = '#38bdf8';
    badge.style.background = 'rgba(56, 189, 248, 0.15)';
  }

  preUploadPromise = uploadFileWithProgress(file, (pct) => {
    if (badge && !state.uploadedFileId) {
      badge.textContent = `☁️ កំពុង Upload... ${pct}%`;
    }
  }).then((fileId) => {
    state.uploadedFileId = fileId;
    if (badge) {
      badge.textContent = '✅ Upload រួចរាល់';
      badge.style.color = '#4ade80';
      badge.style.background = 'rgba(34, 197, 94, 0.15)';
    }
    return fileId;
  }).catch((err) => {
    console.warn("Background upload notice:", err);
    if (badge) {
      badge.textContent = '⚠️ នឹង Upload ពេលចុច Dubbing';
      badge.style.color = '#f59e0b';
      badge.style.background = 'rgba(245, 158, 11, 0.15)';
    }
    return null;
  });
}

function handleSelectedFile(file) {
  state.selectedFile = file;
  state.uploadedFileId = null;
  state.isDemoPreview = false;

  elements.previewFileName.textContent = file.name;
  elements.previewFileSize.textContent = formatBytes(file.size);

  const fileUrl = URL.createObjectURL(file);
  elements.sourceVideoPlayer.src = fileUrl;
  elements.sourceVideoPlayer.style.display = 'block';
  elements.videoPlaceholderCanvas?.classList.add('hidden');

  elements.dropZonePrompt.classList.add('hidden');
  elements.filePreviewCard.classList.remove('hidden');
  elements.startDubBtn.disabled = false;

  showToast(`បានជ្រើសរើសឯកសារ: ${file.name}`, 'success');

  // Immediately upload in background so user has 0s upload wait time when clicking Dub!
  startBackgroundPreUpload(file);
}

function resetFileSelection() {
  state.selectedFile = null;
  state.uploadedFileId = null;
  preUploadPromise = null;
  const badge = document.getElementById('previewUploadBadge');
  if (badge) badge.style.display = 'none';

  elements.videoFileInput.value = '';
  elements.sourceVideoPlayer.pause();
  elements.sourceVideoPlayer.src = '';

  const anyOverlay = (elements.logoEnabledToggle?.checked) || 
                     (elements.blurEnabledToggle?.checked) || 
                     (elements.customTextEnabledToggle?.checked);

  if (anyOverlay) {
    elements.videoPlaceholderCanvas?.classList.remove('hidden');
    elements.sourceVideoPlayer.style.display = 'none';
    elements.dropZonePrompt.classList.add('hidden');
    elements.filePreviewCard.classList.remove('hidden');
    state.isDemoPreview = true;
  } else {
    elements.dropZonePrompt.classList.remove('hidden');
    elements.filePreviewCard.classList.add('hidden');
    state.isDemoPreview = false;
  }

  elements.startDubBtn.disabled = true;
  if (elements.uploadProgressBarContainer) {
    elements.uploadProgressBarContainer.classList.add('hidden');
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function postJson(url, data) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            resolve(JSON.parse(xhr.responseText));
          } catch (e) {
            reject(new Error("Invalid server response"));
          }
        } else {
          let errText = "Server error " + xhr.status;
          try {
            const errJson = JSON.parse(xhr.responseText);
            if (errJson.detail) errText = errJson.detail;
          } catch (_) {}
          reject(new Error(errText));
        }
      }
    };
    xhr.onerror = () => reject(new Error("Network connection error"));
    xhr.send(JSON.stringify(data));
  });
}

// =========================================================================
// Exact Overlay Percentage Calculator (100% matched to Video Dimensions)
// =========================================================================
function getExactOverlayPercentages() {
  const stage = elements.overlayStage || elements.videoStageBox;
  if (!stage) return null;

  const stageRect = stage.getBoundingClientRect();
  const stageW = stageRect.width || stage.clientWidth || 1;
  const stageH = stageRect.height || stage.clientHeight || 1;

  // 1. Blur Subtitle Box
  const blurEl = elements.previewBlurBox;
  let blurX = 5.0, blurY = 83.0, blurW = 90.0, blurH = 13.0;
  if (blurEl && !blurEl.classList.contains('hidden')) {
    const r = blurEl.getBoundingClientRect();
    blurX = Math.max(0, Math.min(99, ((r.left - stageRect.left) / stageW) * 100));
    blurY = Math.max(0, Math.min(99, ((r.top - stageRect.top) / stageH) * 100));
    blurW = Math.max(2, Math.min(100 - blurX, (r.width / stageW) * 100));
    blurH = Math.max(1, Math.min(100 - blurY, (r.height / stageH) * 100));
  } else {
    if (state.blurY != null) blurY = state.blurY;
    if (state.blurX != null) blurX = state.blurX;
    if (state.blurHeight != null) blurH = state.blurHeight;
  }

  // 2. Logo
  const logoEl = elements.previewLogo;
  let logoX = 80.0, logoY = 5.0, logoW = 14.0;
  if (logoEl && !logoEl.classList.contains('hidden')) {
    const r = logoEl.getBoundingClientRect();
    logoX = Math.max(0, Math.min(98, ((r.left - stageRect.left) / stageW) * 100));
    logoY = Math.max(0, Math.min(98, ((r.top - stageRect.top) / stageH) * 100));
    logoW = Math.max(3, Math.min(80, (r.width / stageW) * 100));
  } else {
    if (state.logoX != null) logoX = state.logoX;
    if (state.logoY != null) logoY = state.logoY;
    logoW = parseFloat(elements.logoSizeSlider?.value || 14);
  }

  // 3. Custom Text Banner
  const textEl = elements.previewCustomText;
  let textX = 35.0, textY = 5.0;
  let fontPercent = 5.5; // default ~5.5% of height
  if (textEl && !textEl.classList.contains('hidden')) {
    const r = textEl.getBoundingClientRect();
    textX = Math.max(0, Math.min(98, ((r.left - stageRect.left) / stageW) * 100));
    textY = Math.max(0, Math.min(98, ((r.top - stageRect.top) / stageH) * 100));

    // Calculate actual rendered font size in pixels and express as % of video stage height
    if (elements.previewCustomTextContent) {
      const computedFontPx = parseFloat(window.getComputedStyle(elements.previewCustomTextContent).fontSize) || 18;
      fontPercent = (computedFontPx / stageH) * 100;
      fontPercent = Math.max(3.0, Math.min(15.0, fontPercent));
    }
  } else {
    if (state.customTextX != null) textX = state.customTextX;
    if (state.customTextY != null) textY = state.customTextY;
    const sliderVal = parseFloat(elements.customTextSizeSlider?.value || 26);
    fontPercent = (sliderVal / 26.0) * 5.5;
  }

  return {
    blur: {
      x: Number(blurX.toFixed(2)),
      y: Number(blurY.toFixed(2)),
      w: Number(blurW.toFixed(2)),
      h: Number(blurH.toFixed(2))
    },
    logo: {
      x: Number(logoX.toFixed(2)),
      y: Number(logoY.toFixed(2)),
      w: Number(logoW.toFixed(2))
    },
    text: {
      x: Number(textX.toFixed(2)),
      y: Number(textY.toFixed(2)),
      fontSizePercent: Number(fontPercent.toFixed(2))
    }
  };
}

// =========================================================================
// Dubbing Execution & Progress
// =========================================================================
async function startDubbingProcess() {
  if (!state.selectedFile) return;

  elements.startDubBtn.disabled = true;
  elements.resultCard.classList.add('hidden');
  elements.processingCard.classList.remove('hidden');

  try {
    // 1. Ensure Video is Uploaded (Zero wait if pre-uploaded in background!)
    let fileId = state.uploadedFileId;
    if (!fileId) {
      updateProgress(5, "កំពុង Upload វីដេអូឡើង Server...", "Preparing file upload...");
      if (preUploadPromise) {
        fileId = await preUploadPromise;
      }
      if (!fileId) {
        fileId = await uploadFileWithProgress(state.selectedFile, (pct) => {
          const mappedPct = Math.min(15, Math.max(5, Math.round(pct * 0.15)));
          updateProgress(mappedPct, `កំពុង Upload វីដេអូ (${pct}%)`, "Uploading video to server...");
        });
        state.uploadedFileId = fileId;
      }
    }

    // 2. Start Dubbing Job
    const voiceMode = document.querySelector('input[name="voiceMode"]:checked')?.value || 'auto';
    const vocalCutMode = document.querySelector('input[name="vocalCutMode"]:checked')?.value || 'smart-duck';
    const geminiKey = localStorage.getItem('mn_gemini_api_key') || '';

    // If logo enabled and file selected but not yet uploaded
    if (elements.logoEnabledToggle?.checked && state.selectedLogoFile && !state.uploadedLogoFileId) {
      updateProgress(10, "កំពុង Upload Logo...", "Uploading watermark image...");
      try {
        state.uploadedLogoFileId = await uploadFileWithProgress(state.selectedLogoFile);
      } catch (e) {
        console.warn("Logo upload failed, continuing without logo", e);
      }
    }

    // Read exact on-screen video frame percentage coordinates
    const overlayCoords = getExactOverlayPercentages();

    const payload = {
      fileId: fileId,
      voiceId: elements.voiceSelect.value,
      voiceMode: voiceMode,
      vocalCutMode: vocalCutMode,
      bgMusicVolume: parseFloat(elements.bgMusicSlider.value),
      dubVolume: parseFloat(elements.dubVolSlider.value),
      rate: parseInt(elements.rateSlider.value, 10),
      pitch: parseInt(elements.pitchSlider.value, 10),
      geminiApiKey: geminiKey || null,

      // Logo Overlay (Exact % coordinates matching preview video)
      logoEnabled: elements.logoEnabledToggle ? elements.logoEnabledToggle.checked : false,
      logoFileId: state.uploadedLogoFileId,
      logoPosition: state.logoPosition || 'top-right',
      logoX: overlayCoords ? overlayCoords.logo.x : (state.logoX != null ? state.logoX : null),
      logoY: overlayCoords ? overlayCoords.logo.y : (state.logoY != null ? state.logoY : null),
      logoSize: overlayCoords ? overlayCoords.logo.w : parseInt(elements.logoSizeSlider ? elements.logoSizeSlider.value : 14, 10),
      logoOpacity: parseInt(elements.logoOpacitySlider ? elements.logoOpacitySlider.value : 90, 10),
      logoRemoveBg: elements.logoRemoveBgToggle ? elements.logoRemoveBgToggle.checked : false,
      logoChromaColor: elements.logoChromaColorPicker ? elements.logoChromaColorPicker.value : "#00FF00",

      // Blur Subtitle Box (Exact % coordinates and dimensions matching preview video)
      blurEnabled: elements.blurEnabledToggle ? elements.blurEnabledToggle.checked : false,
      blurY: overlayCoords ? overlayCoords.blur.y : parseFloat(elements.blurYSlider ? elements.blurYSlider.value : 83),
      blurHeight: overlayCoords ? overlayCoords.blur.h : parseFloat(elements.blurHeightSlider ? elements.blurHeightSlider.value : 13),
      blurWidth: overlayCoords ? overlayCoords.blur.w : (state.blurWidth || 90),
      blurX: overlayCoords ? overlayCoords.blur.x : (state.blurX != null ? state.blurX : null),
      blurStrength: parseInt(elements.blurStrengthSlider ? elements.blurStrengthSlider.value : 15, 10),
      blurDarkness: parseInt(elements.blurDarknessSlider ? elements.blurDarknessSlider.value : 40, 10),

      // Custom Text Banner (Exact % coordinates and proportional font size)
      customTextEnabled: elements.customTextEnabledToggle ? elements.customTextEnabledToggle.checked : false,
      customText: elements.customTextInput ? elements.customTextInput.value.trim() : "",
      customTextPosition: elements.customTextPositionSelect ? elements.customTextPositionSelect.value : "top-center",
      customTextX: overlayCoords ? overlayCoords.text.x : (state.customTextX != null ? state.customTextX : null),
      customTextY: overlayCoords ? overlayCoords.text.y : (state.customTextY != null ? state.customTextY : null),
      customTextSize: parseInt(elements.customTextSizeSlider ? elements.customTextSizeSlider.value : 26, 10),
      customTextFontSizePercent: overlayCoords ? overlayCoords.text.fontSizePercent : null,
      customTextColor: elements.customTextColorPicker ? elements.customTextColorPicker.value : "#FFFFFF",
      customTextBg: elements.customTextBgToggle ? elements.customTextBgToggle.checked : true
    };

    updateProgress(15, "កំពុងចាប់ផ្តើម AI Pipeline...", "Sending job to server...");

    const dubData = await postJson('/api/dub', payload);
    state.currentTaskId = dubData.taskId;

    // 3. Start Polling Progress (100% reliable across iOS Safari & Android)
    startPollingTask(dubData.taskId);

  } catch (err) {
    console.error('Dubbing error:', err);
    showToast(`បញ្ហា: ${err.message}`, 'error');
    elements.startDubBtn.disabled = false;
    elements.processStepTitle.textContent = "មានបញ្ហា (Error)";
    elements.processStepDesc.textContent = err.message;
  }
}

function uploadFileWithProgress(file, onProgress) {
  return new Promise((resolve, reject) => {
    if (elements.uploadProgressBarContainer) {
      elements.uploadProgressBarContainer.classList.remove('hidden');
      if (elements.uploadProgressBar) elements.uploadProgressBar.style.width = '0%';
    }

    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('file', file);

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        if (elements.uploadProgressBar) elements.uploadProgressBar.style.width = `${pct}%`;
        if (elements.uploadPercentText) elements.uploadPercentText.textContent = `${pct}%`;
        if (onProgress) onProgress(pct);
      }
    });

    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const res = JSON.parse(xhr.responseText);
            if (elements.uploadProgressBarContainer) {
              elements.uploadProgressBarContainer.classList.add('hidden');
            }
            resolve(res.fileId);
          } catch (e) {
            reject(new Error('Invalid upload response'));
          }
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    };

    xhr.onerror = () => reject(new Error('Network error during upload'));
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
  });
}

function startPollingTask(taskId) {
  let consecutiveErrors = 0;
  
  const pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/task/${taskId}?_t=${Date.now()}`);
      if (res.ok) {
        consecutiveErrors = 0;
        const data = await res.json();
        handleProgressUpdate(data);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollTimer);
        }
      } else {
        consecutiveErrors++;
      }
    } catch (e) {
      consecutiveErrors++;
      // Only fail if disconnected for more than 15 consecutive attempts (15+ seconds)
      if (consecutiveErrors > 15) {
        clearInterval(pollTimer);
        elements.processStepTitle.textContent = "មានបញ្ហាតភ្ជាប់ (Connection Lost)";
        elements.processStepDesc.textContent = "បាត់បង់ការតភ្ជាប់ទៅកាន់ Server សូមពិនិត្យមើល Wi-Fi";
        elements.startDubBtn.disabled = false;
      }
    }
  }, 1000);
}

function handleProgressUpdate(data) {
  const pct = data.percent || 0;
  const step = data.step || "កំពុងដំណើរការ...";
  const details = data.details || "";

  updateProgress(pct, step, details);

  if (data.status === 'completed' || pct >= 100) {
    onDubbingCompleted(data.result);
  } else if (data.status === 'failed') {
    elements.processStepTitle.textContent = "មានបញ្ហា (Failed)";
    elements.processStepDesc.textContent = data.error || "Unknown error";
    elements.startDubBtn.disabled = false;
    showToast(`Dubbing failed: ${data.error}`, 'error');
  }
}

function updateProgress(percent, step, details) {
  elements.dubProgressBar.style.width = `${percent}%`;
  elements.processPercentBadge.textContent = `${percent}%`;
  elements.processStepTitle.textContent = step;
  elements.processStepDesc.textContent = details;

  // Update step nodes
  const nodePcts = [10, 30, 60, 80, 95];
  elements.nodes.forEach((node, i) => {
    if (percent >= nodePcts[i]) {
      node.classList.add('completed');
      node.classList.remove('active');
    } else if (i === 0 || percent >= nodePcts[i - 1]) {
      node.classList.add('active');
      node.classList.remove('completed');
    } else {
      node.classList.remove('active', 'completed');
    }
  });
}

function onDubbingCompleted(result) {
  elements.processingCard.classList.add('hidden');
  elements.resultCard.classList.remove('hidden');
  elements.startDubBtn.disabled = false;

  const videoUrl = result?.videoUrl || `/api/download/${state.currentTaskId}/video`;
  const audioUrl = result?.audioUrl || `/api/download/${state.currentTaskId}/audio`;
  const srtUrl = result?.srtUrl || `/api/download/${state.currentTaskId}/srt`;

  elements.resultVideoPlayer.src = videoUrl;
  elements.downloadVideoBtn.href = videoUrl;
  elements.downloadAudioBtn.href = audioUrl;
  elements.downloadSrtBtn.href = srtUrl;

  showToast("🎉 ការ Dubbing ទទួលបានជោគជ័យ ១០០%!", "success");
}

// =========================================================================
// Voice Audition / Preview
// =========================================================================
function initVoiceAudition() {
  // Test from main controls
  elements.testVoiceBtn.addEventListener('click', () => {
    const voiceId = elements.voiceSelect.value;
    const sample = "សួស្តី! នេះគឺជាសំឡេងពិសិដ្ឋ បង្កើតដោយបញ្ញាសិប្បនិម្មិត AI Dubber។";
    playVoiceSample(sample, voiceId);
  });

  // Test from Voice Studio Tab
  elements.playVoiceTestBtn.addEventListener('click', () => {
    const text = elements.voiceTestText.value.trim();
    const voiceId = elements.voiceTestSelect.value;
    if (!text) {
      showToast("សូមបញ្ចូលអត្ថបទដើម្បីស្តាប់", "error");
      return;
    }
    playVoiceSample(text, voiceId);
  });
}

async function playVoiceSample(text, voiceId) {
  const btnIcon = elements.playVoiceBtnIcon;
  const btnText = elements.playVoiceBtnText;

  if (btnText) btnText.textContent = "កំពុងរៀបចំ...";

  try {
    const rate = parseInt(elements.rateSlider.value, 10);
    const pitch = parseInt(elements.pitchSlider.value, 10);

    const res = await fetch('/api/preview-voice', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice: voiceId, rate, pitch })
    });

    if (!res.ok) throw new Error("Could not synthesize preview.");

    const blob = await res.blob();
    const audioUrl = URL.createObjectURL(blob);
    
    elements.voiceTestAudioPlayer.src = audioUrl;
    elements.voiceTestAudioPlayer.play();

    showToast("🔊 កំពុងចាក់សំឡេង...", "info");
  } catch (err) {
    showToast(`បញ្ហាសំឡេង: ${err.message}`, "error");
  } finally {
    if (btnText) btnText.textContent = "ស្តាប់សម្លេង";
  }
}

// =========================================================================
// Settings & Mobile Link Copy
// =========================================================================
function initSettings() {
  // Load saved API Key
  const savedKey = localStorage.getItem('mn_gemini_api_key') || '';
  elements.geminiKeyInput.value = savedKey;

  elements.saveSettingsBtn.addEventListener('click', () => {
    const key = elements.geminiKeyInput.value.trim();
    localStorage.setItem('mn_gemini_api_key', key);
    elements.saveStatusMsg.textContent = "✓ បានរក្សាទុកជោគជ័យ!";
    setTimeout(() => { elements.saveStatusMsg.textContent = ""; }, 3000);
    showToast("ការកំណត់ត្រូវបានរក្សាទុក!", "success");
  });

  // Copy Mobile URL
  elements.copyUrlBtn.addEventListener('click', () => {
    const url = elements.displayMobileUrl.textContent;
    navigator.clipboard.writeText(url).then(() => {
      elements.copyUrlBtn.textContent = "ចម្លងរួច (Copied!)";
      setTimeout(() => { elements.copyUrlBtn.textContent = "ចម្លង (Copy)"; }, 2000);
      showToast("បានចម្លង Link សម្រាប់ទូរស័ព្ទ!", "success");
    });
  });
}

// =========================================================================
// Progressive Web App (PWA) Registration
// =========================================================================
function registerPWA() {
  if ('serviceWorker' in navigator) {
    if (window.location.protocol === 'https:' || window.location.hostname === 'localhost') {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
      });
    } else {
      navigator.serviceWorker.getRegistrations().then(registrations => {
        for (let r of registrations) r.unregister();
      }).catch(() => {});
    }
  }
}

// =========================================================================
// TikTok Video Downloader & Auto-Dub Integration
// =========================================================================
function initTikTokDownloader() {
  const urlInput = elements.tiktokUrlInput;
  const pasteBtn = elements.tiktokPasteBtn;
  const clearBtn = elements.tiktokClearBtn;
  const fetchBtn = elements.tiktokFetchBtn;
  const quickDubBtn = elements.tiktokQuickDubBtn;
  const loadingState = elements.tiktokLoadingState;
  const resultCard = elements.tiktokResultCard;
  const sendToDubBtn = elements.tiktokSendToDubBtn;
  const directDownloadBtn = elements.tiktokDirectDownloadBtn;
  const playPreviewBtn = elements.tiktokPlayPreviewBtn;
  const previewVideo = elements.tiktokPreviewVideo;
  const coverImg = elements.tiktokCoverImg;

  if (!urlInput) return;

  function toggleClearButton() {
    if (urlInput.value.trim().length > 0) {
      clearBtn?.classList.remove('hidden');
    } else {
      clearBtn?.classList.add('hidden');
    }
  }

  urlInput.addEventListener('input', toggleClearButton);

  clearBtn?.addEventListener('click', () => {
    urlInput.value = '';
    toggleClearButton();
    resultCard?.classList.add('hidden');
    loadingState?.classList.add('hidden');
    state.currentTikTokData = null;
    if (previewVideo) {
      previewVideo.pause();
      previewVideo.src = '';
      previewVideo.classList.add('hidden');
    }
    coverImg?.classList.remove('hidden');
    playPreviewBtn?.classList.remove('hidden');
    urlInput.focus();
  });

  pasteBtn?.addEventListener('click', async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const clipText = await navigator.clipboard.readText();
        if (clipText) {
          urlInput.value = clipText.trim();
          toggleClearButton();
          showToast("បានបិទភ្ជាប់ Link រួចរាល់!", "success");
          handleFetchTikTok(false);
          return;
        }
      }
      urlInput.focus();
      showToast("សូមចុចបិទភ្ជាប់ (Paste) ក្នុងប្រអប់", "info");
    } catch (err) {
      urlInput.focus();
      showToast("សូមចុចបិទភ្ជាប់ (Paste) ដោយផ្ទាល់", "info");
    }
  });

  fetchBtn?.addEventListener('click', () => {
    handleFetchTikTok(false);
  });

  quickDubBtn?.addEventListener('click', () => {
    handleFetchTikTok(true);
  });

  playPreviewBtn?.addEventListener('click', () => {
    const data = state.currentTikTokData;
    if (!data) return;
    let playSrc = '';
    if (data.fileId) {
      playSrc = `/uploads/${data.fileId}`;
    } else if (data.playUrl) {
      playSrc = `/api/tiktok/stream?url=${encodeURIComponent(data.playUrl)}`;
    }
    if (playSrc) {
      coverImg?.classList.add('hidden');
      playPreviewBtn?.classList.add('hidden');
      previewVideo.src = playSrc;
      previewVideo.classList.remove('hidden');
      previewVideo.play().catch(() => {});
    }
  });

  async function handleFetchTikTok(autoDubAfterDownload = false) {
    const rawUrl = urlInput.value.trim();
    if (!rawUrl) {
      showToast("សូមបញ្ចូល Link វីដេអូ TikTok!", "error");
      urlInput.focus();
      return;
    }

    // Set UI loading state
    loadingState?.classList.remove('hidden');
    resultCard?.classList.add('hidden');
    if (autoDubAfterDownload) {
      elements.tiktokQuickDubSpinner?.classList.remove('hidden');
      quickDubBtn.disabled = true;
      elements.tiktokLoadingTitle.textContent = "កំពុងទាញយកវីដេអូ និងរៀបចំសម្រាប់ Dubbing...";
      elements.tiktokLoadingSubtitle.textContent = "កំពុងទាញយកឯកសារកម្រិត HD No-Watermark មកកាន់ Studio...";
    } else {
      elements.tiktokFetchSpinner?.classList.remove('hidden');
      elements.tiktokFetchIcon?.classList.add('hidden');
      fetchBtn.disabled = true;
      elements.tiktokLoadingTitle.textContent = "កំពុងទាញយកព័ត៌មានវីដេអូពី TikTok...";
      elements.tiktokLoadingSubtitle.textContent = "កំពុងស្វែងរកកម្រិត HD No-Watermark...";
    }

    try {
      if (autoDubAfterDownload) {
        // Direct download flow
        const dlRes = await postJson('/api/tiktok/download', { url: rawUrl });
        if (!dlRes || !dlRes.fileId) {
          throw new Error("Download failed");
        }
        state.currentTikTokData = dlRes;
        await sendTikTokToDubStudio(dlRes);
      } else {
        // Info fetch flow
        const infoRes = await postJson('/api/tiktok/info', { url: rawUrl });
        if (!infoRes || !infoRes.info) {
          throw new Error("Could not retrieve video info");
        }
        const info = infoRes.info;
        state.currentTikTokData = info;
        renderTikTokResult(info);
      }
    } catch (err) {
      console.error("TikTok fetch error:", err);
      showToast(err.message || "មិនអាចទាញយកវីដេអូ TikTok នេះបានទេ។ សូមពិនិត្យ Link ម្តងទៀត!", "error");
    } finally {
      loadingState?.classList.add('hidden');
      elements.tiktokFetchSpinner?.classList.add('hidden');
      elements.tiktokFetchIcon?.classList.remove('hidden');
      elements.tiktokQuickDubSpinner?.classList.add('hidden');
      fetchBtn.disabled = false;
      quickDubBtn.disabled = false;
    }
  }

  function renderTikTokResult(info) {
    if (!info) return;

    elements.tiktokVideoTitle.textContent = info.title || 'TikTok Video';
    elements.tiktokAuthorName.textContent = info.author || 'TikTok Creator';
    if (info.avatar && elements.tiktokAuthorAvatar) {
      elements.tiktokAuthorAvatar.src = info.avatar;
    }
    if (info.cover && elements.tiktokCoverImg) {
      elements.tiktokCoverImg.src = info.cover;
    }

    const durationSec = info.duration || 0;
    if (durationSec > 0) {
      const mins = Math.floor(durationSec / 60);
      const secs = durationSec % 60;
      const durStr = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
      if (elements.tiktokDurationBadge) elements.tiktokDurationBadge.textContent = durStr;
      if (elements.tiktokDurationTag) elements.tiktokDurationTag.textContent = `⏱️ ${durStr}`;
    } else {
      if (elements.tiktokDurationBadge) elements.tiktokDurationBadge.textContent = 'Drama / HD';
      if (elements.tiktokDurationTag) elements.tiktokDurationTag.textContent = '🎬 TikTok Drama / Episode';
    }

    // Reset video player state
    if (previewVideo) {
      previewVideo.pause();
      previewVideo.src = '';
      previewVideo.classList.add('hidden');
    }
    coverImg?.classList.remove('hidden');
    playPreviewBtn?.classList.remove('hidden');

    // Setup direct download button
    if (info.playUrl && directDownloadBtn) {
      directDownloadBtn.href = `/api/tiktok/stream?url=${encodeURIComponent(info.playUrl)}`;
      directDownloadBtn.setAttribute('download', `${(info.title || 'tiktok_video').replace(/[^\w\s-]/g, '').trim() || 'tiktok'}.mp4`);
      directDownloadBtn.target = "_blank";
    }

    resultCard?.classList.remove('hidden');
    resultCard?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  sendToDubBtn?.addEventListener('click', async () => {
    const rawUrl = urlInput.value.trim();
    if (!rawUrl) return;

    sendToDubBtn.disabled = true;
    sendToDubBtn.innerHTML = `<span class="btn-spinner"></span> កំពុងទាញយកចូល Studio...`;

    try {
      const dlRes = await postJson('/api/tiktok/download', { url: rawUrl });
      if (!dlRes || !dlRes.fileId) {
        throw new Error("Download failed");
      }
      state.currentTikTokData = dlRes;
      await sendTikTokToDubStudio(dlRes);
    } catch (err) {
      console.error("Send to dub error:", err);
      showToast(err.message || "មិនអាចទាញយកវីដេអូបានទេ", "error");
    } finally {
      sendToDubBtn.disabled = false;
      sendToDubBtn.innerHTML = `<span class="btn-icon">🎬</span><span class="btn-label-bold">យកទៅ Dub ភាសាខ្មែរភ្លាមៗ (Send to Dub Studio)</span>`;
    }
  });

  async function sendTikTokToDubStudio(dlData) {
    showToast("កំពុងរៀបចំវីដេអូក្នុង Dub Studio...", "info");
    try {
      const videoRes = await fetch(`/uploads/${dlData.fileId}`);
      if (!videoRes.ok) {
        throw new Error("Could not access downloaded video file");
      }
      const blob = await videoRes.blob();
      const videoFile = new File([blob], dlData.filename || 'tiktok_video.mp4', { type: 'video/mp4' });

      // Load into Dub Studio
      handleSelectedFile(videoFile);
      state.uploadedFileId = dlData.fileId;

      // Switch to Dub Studio tab
      const studioTabBtn = document.querySelector('.nav-btn[data-tab="studioTab"]');
      if (studioTabBtn) studioTabBtn.click();

      // Update download button on result card for local copy
      if (directDownloadBtn && dlData.fileId) {
        directDownloadBtn.href = `/api/tiktok/download-file/${dlData.fileId}?name=${encodeURIComponent(dlData.title || 'tiktok_video')}`;
        directDownloadBtn.removeAttribute('target');
      }

      showToast("🎉 វីដេអូ TikTok ត្រូវបានដាក់ចូល Dub Studio រួចរាល់!", "success");
    } catch (err) {
      console.error("Error sending to Dub Studio:", err);
      showToast("មានបញ្ហាក្នុងការដាក់ចូល Dub Studio: " + err.message, "error");
    }
  }
}
