const STORAGE_KEY = 'aini.local.prototype.v1';

const defaultState = {
  wakeEnabled: false,
  bluetoothConnected: false,
  careLevel: 55,
  provider: 'OpenAI',
  apiKeyHint: '',
  aiEmotion: { concern: 76, energy: 58, closeness: 64 },
  messages: [
    {
      role: 'ai',
      text: '我会尽量在本地轻轻运行，不打扰你。你可以先告诉我今天的心情，或者配置你的模型 API。',
    },
  ],
  memories: [],
};

const state = loadState();
const $ = (selector) => document.querySelector(selector);
const messageList = $('#messageList');

function loadState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? { ...defaultState, ...JSON.parse(stored) } : structuredClone(defaultState);
  } catch {
    return structuredClone(defaultState);
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function render() {
  $('#wakeStatus').textContent = state.wakeEnabled ? '唤醒开启' : '唤醒关闭';
  $('#bluetoothStatus').textContent = state.bluetoothConnected ? '蓝牙已连' : '无蓝牙';
  $('#careStatus').textContent = state.careLevel > 70 ? '关怀高' : state.careLevel < 30 ? '关怀低' : '关怀普通';
  $('#sceneLabel').textContent = `本地运行 · ${state.bluetoothConnected ? '蓝牙耳机已连接' : '未连接蓝牙'} · ${state.provider}`;
  $('#concernMeter').value = state.aiEmotion.concern;
  $('#energyMeter').value = state.aiEmotion.energy;
  $('#closenessMeter').value = state.aiEmotion.closeness;
  $('#careRange').value = state.careLevel;
  $('#providerSelect').value = state.provider;
  $('#memorySummary').textContent = state.memories.at(-1)?.summary ?? '今天还没有新的核心记忆。';
  renderMessages();
}

function renderMessages() {
  messageList.innerHTML = '';
  for (const message of state.messages) {
    const bubble = document.createElement('div');
    bubble.className = `message ${message.role}`;
    bubble.textContent = message.text;
    messageList.appendChild(bubble);
  }
  messageList.scrollTop = messageList.scrollHeight;
}

function addMessage(role, text) {
  state.messages.push({ role, text });
  if (state.messages.length > 40) state.messages.shift();
  saveState();
  render();
}

function buildLocalReply(text) {
  const tired = /累|难受|不舒服|焦虑|烦|压力|睡不着/.test(text);
  const happy = /开心|好消息|顺利|喜欢|哈哈/.test(text);

  if (tired) {
    state.aiEmotion.concern = Math.min(100, state.aiEmotion.concern + 8);
    state.aiEmotion.energy = Math.max(35, state.aiEmotion.energy - 4);
    return state.bluetoothConnected
      ? '我听到了，你现在可能有点撑着。先慢一点，我会用短语音陪你，不说太多。'
      : '我在。你现在不舒服的话，我们先不用急着解决问题，先把状态稳下来。';
  }

  if (happy) {
    state.aiEmotion.energy = Math.min(100, state.aiEmotion.energy + 8);
    state.aiEmotion.closeness = Math.min(100, state.aiEmotion.closeness + 3);
    return '听起来这是个让人放松的好消息呀。我有点替你开心，想听你多讲一点。';
  }

  return state.bluetoothConnected
    ? '我会默认用更自然的语音陪你。如果你不方便听，也可以随时切回文本。'
    : '我会先用文字陪你，尽量轻一点、不打扰。你想让我更温柔，还是更理性一点？';
}

function handleSend(event) {
  event.preventDefault();
  const input = $('#messageInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMessage('user', text);
  window.setTimeout(() => addMessage('ai', buildLocalReply(text)), 220);
}

function distillMemory() {
  const userMessages = state.messages.filter((message) => message.role === 'user').map((message) => message.text);
  const summary = userMessages.length
    ? `今日核心：用户提到「${userMessages.at(-1)}」。Aini 将以低打扰方式持续关注情绪变化。`
    : '今日核心：用户还没有表达具体事件，保持轻陪伴。';
  state.memories.push({ date: new Date().toISOString().slice(0, 10), summary });
  saveState();
  render();
}

function requestMockPermission(name) {
  addMessage('ai', `我会在你确认后才使用${name}权限；默认只做本地分析，不自动上传。`);
}

function openSettings() {
  $('#settingsDrawer').classList.add('open');
  $('#settingsDrawer').setAttribute('aria-hidden', 'false');
}

function closeSettings() {
  $('#settingsDrawer').classList.remove('open');
  $('#settingsDrawer').setAttribute('aria-hidden', 'true');
}

function bindEvents() {
  $('#chatForm').addEventListener('submit', handleSend);
  $('#settingsButton').addEventListener('click', openSettings);
  $('#closeSettings').addEventListener('click', closeSettings);
  $('#saveSettings').addEventListener('click', () => {
    state.provider = $('#providerSelect').value;
    state.careLevel = Number($('#careRange').value);
    state.apiKeyHint = $('#apiKeyInput').value ? 'saved-locally' : '';
    saveState();
    closeSettings();
    render();
    addMessage('ai', '设置已保存到本地。真实 App 中 API Key 会进入 Keychain / Keystore / HarmonyOS 安全区。');
  });
  $('#distillButton').addEventListener('click', distillMemory);
  $('#voiceButton').addEventListener('click', () => addMessage('ai', '语音原型：这里会接入端侧唤醒词、VAD、流式 ASR 和可打断 TTS。'));

  document.querySelectorAll('.quick-card').forEach((button) => {
    button.addEventListener('click', () => {
      const action = button.dataset.action;
      if (action === 'toggleWake') state.wakeEnabled = !state.wakeEnabled;
      if (action === 'toggleBluetooth') state.bluetoothConnected = !state.bluetoothConnected;
      if (action === 'toggleCare') state.careLevel = state.careLevel > 70 ? 20 : state.careLevel < 30 ? 55 : 85;
      saveState();
      render();
    });
  });

  document.querySelectorAll('[data-permission]').forEach((button) => {
    button.addEventListener('click', () => requestMockPermission(button.dataset.permission));
  });
}

bindEvents();
render();
