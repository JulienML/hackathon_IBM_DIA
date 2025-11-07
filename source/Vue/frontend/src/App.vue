<template>
  <div class="app-container">
    <!-- Colonne gauche : Questions fréquentes -->
    <div class="sidebar">
      <h2 class="sidebar-title">💡 Questions fréquentes</h2>
      <button
        v-for="(q, i) in faqQuestions"
        :key="i"
        class="faq-btn"
        @click="askFAQ(q)"
      >
        {{ q }}
      </button>
    </div>

    <!-- Contenu principal -->
    <div class="main-content">
      <!-- Logo -->
      <div class="header">
        <img src="/new.png" alt="Logo école" class="logo" />
      </div>

      <!-- Zone du chat -->
      <div class="chat-container">
        <div class="chat-title">🤖 HelpCenter AI – PLV</div>

        <div ref="chatContainer" class="messages">
          <transition-group name="fade" tag="div">
            <div
              v-for="(item, index) in history"
              :key="index"
              :class="['message', item.type]"
            >
              <div class="bubble" v-html="formatMessage(item.message)"></div>
            </div>
          </transition-group>

          <div v-if="loading" class="message bot">
            <div class="bubble typing">
              <span class="dot" v-for="i in 3" :key="i"></span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <input
            v-model="question"
            @keyup.enter="sendQuestion"
            type="text"
            placeholder="Pose ta question ici..."
          />
          <button @click="sendQuestion" :disabled="loading || !question.trim()">Envoyer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      question: "",
      history: [],
      loading: false,
      faqQuestions: [
        "Quel niveau de langue pour valider son diplôme ?",
        "Combien d'absences je peux avoir par semestre ?",
        "Quand puis-je affecter mes points bonus ?"
      ],
    };
  },
  methods: {
    async sendQuestion(qOverride = null) {
      let q = "";

      if (typeof qOverride === "string") {
        q = qOverride.trim();
      } else {
        q = this.question.trim();
      }

      if (!q) return;

      this.history.push({ type: "user", message: q });
      this.loading = true;
      this.question = "";

      try {
        const res = await axios.post("http://localhost:5000/api/query", { query: q });
        let answer = res.data.answer || "🤔 Je n’ai pas trouvé de réponse pertinente.";

        // Nettoyage
        answer = this.cleanResponse(answer);

        await this.fakeTyping(answer);
      } catch (err) {
        console.error("Erreur Axios :", err);
        this.history.push({
          type: "bot",
          message: "⚠️ Erreur de connexion au serveur. Vérifie qu'il est lancé.",
        });
      } finally {
        this.loading = false;
      }
    },

    async fakeTyping(text) {
      let current = "";
      for (let char of text) {
        current += char;
        this.history = this.history.filter(h => h.type !== "bot-temp");
        this.history.push({ type: "bot-temp", message: current });
        await new Promise(r => setTimeout(r, 5));
      }
      this.history = this.history.filter(h => h.type !== "bot-temp");
      this.history.push({ type: "bot", message: text });

      this.$nextTick(() => {
        const container = this.$refs.chatContainer;
        container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
      });
    },

    formatMessage(msg) {
      msg = msg.replace(/\|\s*Thématique\s*:.*$/i, "").trim();
      msg = msg.replace(/question\s*:\s*/i, "<strong class='highlight'>Question :</strong><br>");
      msg = msg.replace(/réponse\s*:\s*/i, "<br><strong class='highlight'>Réponse :</strong><br>");
      return msg;
    },

    cleanResponse(text) {
      return text
        .replace(/\|/g, "")
        .replace(/\?.*?(true|false)(;|$)/g, "")
        .replace(/https?:\/\/[^\s]+/g, (url) => `<a href="${url}" target="_blank" class="link">${url}</a>`)
        .trim();
    },

    async askFAQ(q) {
      await this.sendQuestion(q);
    },
  },
};
</script>

<style scoped>
/* --- Styles inchangés (comme dans ta version précédente) --- */
.app-container { display: flex; height: 100vh; background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #164e63); background-size: 400% 400%; animation: gradientShift 15s ease infinite; color: #fff; font-family: "Inter", sans-serif; }
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.sidebar { width: 280px; padding: 40px 30px; display: flex; flex-direction: column; justify-content: center; border-right: 1px solid rgba(56, 189, 248, 0.3); background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(10px); }
.sidebar-title { font-size: 1.1rem; color: #38bdf8; font-weight: 600; margin-bottom: 20px; }
.faq-btn { text-align: left; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.4); color: #e2e8f0; font-size: 0.9rem; padding: 12px 14px; border-radius: 10px; margin-bottom: 12px; cursor: pointer; transition: 0.3s; }
.faq-btn:hover { background: rgba(56, 189, 248, 0.3); color: white; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
.main-content { flex: 1; display: flex; align-items: center; justify-content: center; position: relative; }
.header { position: absolute; top: 5%; right: 10%; text-align: right; }
.logo { width: 110px; margin-bottom: 8px; filter: drop-shadow(0 0 12px rgba(34, 211, 238, 0.6)); }
.chat-container { width: 520px; height: 70vh; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 20px; backdrop-filter: blur(16px); box-shadow: 0 0 25px rgba(0, 255, 255, 0.1); display: flex; flex-direction: column; justify-content: space-between; padding: 20px 24px; }
.chat-title { text-align: center; font-weight: bold; color: #22d3ee; margin-bottom: 8px; font-size: 1rem; }
.messages { flex: 1; overflow-y: auto; padding-right: 4px; }
.message { display: flex; margin-bottom: 10px; }
.message.user { justify-content: flex-end; }
.message.bot { justify-content: flex-start; }
.bubble { padding: 12px 16px; border-radius: 18px; max-width: 75%; word-break: break-word; font-size: 0.9rem; line-height: 1.5; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2); animation: fadeIn 0.4s ease; }
.user .bubble { background: linear-gradient(135deg, #22d3ee, #0891b2); color: white; border-bottom-right-radius: 4px; }
.bot .bubble { background: rgba(51, 65, 85, 0.8); color: #f1f5f9; border-bottom-left-radius: 4px; }
.link { color: #38bdf8; text-decoration: underline; word-break: break-all; }
.link:hover { color: #67e8f9; }
.input-area { display: flex; align-items: center; gap: 8px; border-top: 1px solid rgba(56, 189, 248, 0.3); padding-top: 10px; }
.input-area input { flex: 1; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.5); border-radius: 10px; padding: 12px; color: white; }
.input-area input:focus { outline: none; border-color: #22d3ee; box-shadow: 0 0 10px rgba(34, 211, 238, 0.4); }
.input-area button { background: #22d3ee; color: white; font-weight: 600; border: none; border-radius: 10px; padding: 12px 20px; cursor: pointer; transition: 0.3s; }
.input-area button:hover { background: #06b6d4; box-shadow: 0 0 15px rgba(34, 211, 238, 0.5); }
.input-area button:disabled { opacity: 0.6; cursor: not-allowed; }
.typing { display: flex; gap: 6px; align-items: center; }
.dot { width: 8px; height: 8px; background: #22d3ee; border-radius: 50%; animation: bounce 1.2s infinite ease-in-out; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); opacity: 0.3; } 40% { transform: translateY(-5px); opacity: 1; } }
.highlight { color: #22d3ee; font-weight: 600; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
</style>
