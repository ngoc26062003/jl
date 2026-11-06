import { onMounted, onUnmounted, ref } from 'vue'

export function useSpeech() {
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  const hasJapaneseVoice = ref(true)
  const playingKey = ref<string | null>(null)
  let voice: SpeechSynthesisVoice | null = null

  function pickVoice() {
    if (!supported) return
    const voices = window.speechSynthesis.getVoices()
    voice = voices.find((v) => v.lang.replace('_', '-').toLowerCase().startsWith('ja')) ?? null
    // danh sách giọng nạp bất đồng bộ: rỗng nghĩa là chưa nạp xong, chưa vội cảnh báo
    hasJapaneseVoice.value = voices.length === 0 ? true : voice !== null
  }

  function speak(text: string, key: string) {
    if (!supported) return
    const synth = window.speechSynthesis
    synth.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'ja-JP'
    u.rate = 0.8
    if (voice) u.voice = voice
    const done = () => {
      if (playingKey.value === key) playingKey.value = null
    }
    u.onstart = () => (playingKey.value = key)
    u.onend = done
    u.onerror = done
    synth.speak(u)
  }

  onMounted(() => {
    pickVoice()
    if (supported) window.speechSynthesis.addEventListener('voiceschanged', pickVoice)
  })
  onUnmounted(() => {
    if (!supported) return
    window.speechSynthesis.removeEventListener('voiceschanged', pickVoice)
    window.speechSynthesis.cancel()
  })

  return { supported, hasJapaneseVoice, playingKey, speak }
}