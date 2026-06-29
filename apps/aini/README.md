# Aini App Prototype

这是 Aini 的首版轻量移动端 UI 原型，使用纯 HTML/CSS/JavaScript 编写，方便在没有 Flutter/React Native/HarmonyOS SDK 的环境中先验证产品交互、视觉风格和本地状态逻辑。

## 已覆盖

- Aini 品牌与移动端主界面。
- 本地聊天 UI。
- 语音唤醒、蓝牙、主动关怀状态开关。
- AI 情绪值面板。
- 本地记忆蒸馏示意。
- 权限入口：位置、摄像头、手表健康数据、文件。
- 本地模型 API 设置抽屉。
- Android / iOS / HarmonyOS 支持提示。

## 运行

```bash
python3 -m http.server 4173 -d apps/aini
```

然后访问 `http://localhost:4173`。

## 后续移动端落地

建议将当前 UI 与状态逻辑迁移到跨平台移动框架，并保留平台原生适配层：

- Android：权限、音频、蓝牙、Health Connect、Keystore。
- iOS：权限、音频、蓝牙、HealthKit、Keychain。
- HarmonyOS：权限、音频、蓝牙、Health Service/运动健康生态、鸿蒙系统安全区。
