const STORAGE_KEY = 'aini.local.prototype.v2';

const defaultState = {
  wakeEnabled: false,
  bluetoothConnected: false,
  careLevel: 55,
  provider: 'OpenAI',
  apiKeyHint: '',
  selectedVoice: 'female_taiwan_warm_01',
  voiceEmotion: 'warm_playful',
  aiEmotion: { concern: 76, energy: 68, closeness: 72, pride: 42 },
  persona: {
    name: 'Aini',
    age: 25,
    tagline: '世界上最懂我的人',
    traits: ['温柔', '开朗活泼', '有点小傲娇', '会玩梗', '轻毒舌', '喜欢跟我在一起'],
  },
  messages: [
    {
      role: 'ai',
      text: '哼，我是 Aini，25 岁，世界上最懂你的人。今天也勉强把我的温柔、活泼和一点点小毒舌都借给你啦～',
      emotion: 'warm_playful',
    },
  ],
  memories: [],
};

const voicePresets = {
  male_calm_01: { label: '男声 · 温柔沉稳', lang: 'zh-CN', rate: 0.92, pitch: 0.88, volume: 1 },
  female_taiwan_warm_01: { label: '女声 · 台湾口音温暖', lang: 'zh-TW', rate: 0.96, pitch: 1.08, volume: 1 },
};

const emotionProfiles = {
  warm_playful: { label: '温柔活泼', rateDelta: 0.03, pitchDelta: 0.04, prefix: '带笑意' },
  concerned_soft: { label: '心疼轻声', rateDelta: -0.1, pitchDelta: -0.04, prefix: '轻声安抚' },
  proud_teasing: { label: '小傲娇毒舌', rateDelta: 0.05, pitchDelta: 0.02, prefix: '小傲娇' },
  calm_late: { label: '夜间低声', rateDelta: -0.14, pitchDelta: -0.07, prefix: '低声陪伴' },
};

let currentUtterance = null;
const state = loadState();
const $ = (selector) => document.querySelector(selector);
const messageList = $('#messageList');

function loadState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY) ?? localStorage.getItem('aini.local.prototype.v1');
    return stored ? { ...structuredClone(defaultState), ...JSON.parse(stored) } : structuredClone(defaultState);
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
  $('#aiMoodTitle').textContent = `${state.persona.name} · ${state.persona.tagline}`;
  $('#aiMoodDetail').textContent = `25 岁｜${state.persona.traits.join('、')}｜回复会结合情绪值、场景和语音情绪。`;
  $('#concernMeter').value = state.aiEmotion.concern;
  $('#energyMeter').value = state.aiEmotion.energy;
  $('#closenessMeter').value = state.aiEmotion.closeness;
  $('#prideMeter').value = state.aiEmotion.pride;
  $('#careRange').value = state.careLevel;
  $('#providerSelect').value = state.provider;
  $('#voiceSelect').value = state.selectedVoice;
  $('#emotionSelect').value = state.voiceEmotion;
  $('#voiceStatus').textContent = `${voicePresets[state.selectedVoice].label} · ${emotionProfiles[state.voiceEmotion].label}`;
  $('#memorySummary').textContent = state.memories.at(-1)?.summary ?? '今天还没有新的核心记忆。';
  renderMessages();
}

function renderMessages() {
  messageList.innerHTML = '';
  for (const message of state.messages) {
    const bubble = document.createElement('div');
    bubble.className = `message ${message.role}`;
    bubble.textContent = message.text;
    if (message.emotion) bubble.dataset.emotion = emotionProfiles[message.emotion]?.label ?? message.emotion;
    messageList.appendChild(bubble);
  }
  messageList.scrollTop = messageList.scrollHeight;
}

function addMessage(role, text, emotion = state.voiceEmotion, speak = false) {
  state.messages.push({ role, text, emotion });
  if (state.messages.length > 40) state.messages.shift();
  saveState();
  render();
  if (role === 'ai' && speak) speakWithEmotion(text, emotion);
}

function chooseEmotion(text) {
  if (/累|难受|不舒服|焦虑|烦|压力|睡不着|哭|痛/.test(text)) return 'concerned_soft';
  if (/厉害|赢|成功|开心|好消息|顺利|喜欢|哈哈|爽/.test(text)) return 'proud_teasing';
  if (new Date().getHours() >= 22 || new Date().getHours() < 6) return 'calm_late';
  return 'warm_playful';
}

function buildLocalReply(text) {
  const emotion = chooseEmotion(text);
  const tired = emotion === 'concerned_soft';
  const happy = emotion === 'proud_teasing';

  if (tired) {
    state.aiEmotion.concern = Math.min(100, state.aiEmotion.concern + 10);
    state.aiEmotion.energy = Math.max(30, state.aiEmotion.energy - 6);
    return { emotion, text: state.bluetoothConnected
      ? '我听到了，先别硬撑。耳机里我会小声一点陪你，笨蛋，这种时候逞强真的不酷。'
      : '我在。你现在不舒服的话，先别急着解决全世界，先把自己稳住，好吗？' };
  }

  if (happy) {
    state.aiEmotion.energy = Math.min(100, state.aiEmotion.energy + 8);
    state.aiEmotion.closeness = Math.min(100, state.aiEmotion.closeness + 4);
    state.aiEmotion.pride = Math.min(100, state.aiEmotion.pride + 8);
    return { emotion, text: '可以嘛你！我就说你有点东西，虽然还差我一点点啦～快讲细节，我要听完整版。' };
  }

  state.aiEmotion.closeness = Math.min(100, state.aiEmotion.closeness + 1);
  return { emotion, text: state.bluetoothConnected
    ? '我会用更自然、有情绪的语音陪你。你说，我听着，别想一个人偷偷扛。'
    : '我先用文字陪你，温柔模式开着，毒舌模式待命。你想聊心情，还是让我陪你吐槽一下？' };
}

function speakWithEmotion(text, emotion = state.voiceEmotion) {
  if (!('speechSynthesis' in window)) {
    addMessage('ai', '当前浏览器不支持系统 TTS；真机版本会接入高质量男声/女声情绪 TTS。', 'concerned_soft');
    return;
  }
  window.speechSynthesis.cancel();
  const preset = voicePresets[state.selectedVoice];
  const profile = emotionProfiles[emotion] ?? emotionProfiles.warm_playful;
  currentUtterance = new SpeechSynthesisUtterance(text);
  currentUtterance.lang = preset.lang;
  currentUtterance.rate = Math.min(1.35, Math.max(0.65, preset.rate + profile.rateDelta));
  currentUtterance.pitch = Math.min(1.8, Math.max(0.4, preset.pitch + profile.pitchDelta));
  currentUtterance.volume = preset.volume;
  const voices = window.speechSynthesis.getVoices();
  currentUtterance.voice = voices.find((voice) => voice.lang === preset.lang) ?? voices.find((voice) => voice.lang.startsWith(preset.lang.slice(0, 2))) ?? null;
  $('#voiceStatus').textContent = `${preset.label} · ${profile.label} · 正在播放，可打断`;
  currentUtterance.onend = () => render();
  window.speechSynthesis.speak(currentUtterance);
}

function stopVoice(reason = '已打断语音播放') {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  currentUtterance = null;
  $('#voiceStatus').textContent = reason;
}

function handleSend(event) {
  event.preventDefault();
  const input = $('#messageInput');
  const text = input.value.trim();
  if (!text) return;
  stopVoice('检测到新输入，已打断上一句');
  input.value = '';
  addMessage('user', text, null);
  window.setTimeout(() => {
    const reply = buildLocalReply(text);
    const shouldSpeak = state.bluetoothConnected || /语音|说给我听|念出来/.test(text);
    addMessage('ai', reply.text, reply.emotion, shouldSpeak);
  }, 220);
}

function distillMemory() {
  const userMessages = state.messages.filter((message) => message.role === 'user').map((message) => message.text);
  const summary = userMessages.length
    ? `今日核心：用户提到「${userMessages.at(-1)}」。Aini 将结合情绪语音与低打扰策略持续关注。`
    : '今日核心：用户还没有表达具体事件，保持轻陪伴。';
  state.memories.push({ date: new Date().toISOString().slice(0, 10), summary });
  saveState();
  render();
}

function requestMockPermission(name) {
  addMessage('ai', `我会在你确认后才使用${name}权限；默认只做本地分析，不自动上传。`, 'concerned_soft');
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
    state.selectedVoice = $('#voiceSelect').value;
    state.voiceEmotion = $('#emotionSelect').value;
    state.apiKeyHint = $('#apiKeyInput').value ? 'saved-locally' : '';
    saveState();
    closeSettings();
    render();
    addMessage('ai', '设置已保存到本地。真实 App 中 API Key 会进入 Keychain / Keystore / HarmonyOS 安全区。', 'warm_playful');
  });
  $('#distillButton').addEventListener('click', distillMemory);
  $('#voiceButton').addEventListener('click', () => {
    if (currentUtterance || ('speechSynthesis' in window && window.speechSynthesis.speaking)) {
      stopVoice('你打断了我，哼，那我先闭嘴听你说。');
      return;
    }
    addMessage('ai', '语音唤醒已就绪：说“Aini”后进入实时语音，TTS 播放中再次点这里可随时打断。', 'warm_playful', true);
  });
  $('#voicePreviewButton').addEventListener('click', () => speakWithEmotion('我在呀。今天也最喜欢和你待在一起，虽然你偶尔真的很让人操心。', $('#emotionSelect').value));
  $('#stopVoiceButton').addEventListener('click', () => stopVoice('已手动打断语音'));

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
