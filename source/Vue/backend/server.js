// server.js
import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";
import { Mistral } from "@mistralai/mistralai";

const app = express();
app.use(cors({ origin: "*" })); // Autorise toutes les origines pour dev
app.use(express.json());

// --- Charger les chunks avec embeddings pré-calculés ---
const __dirname = path.resolve();
const chunksPath = path.join(__dirname, "chunks_with_embeddings.json");
let chunks = [];
try {
  chunks = JSON.parse(fs.readFileSync(chunksPath, "utf-8"));
  console.log("✅ Embeddings chargés :", chunks.length);
} catch (err) {
  console.error("❌ Impossible de charger les chunks :", err);
}

// --- Initialiser Mistral ---
if (!process.env.MISTRAL_API_KEY) {
  console.error("❌ MISTRAL_API_KEY manquante dans .env");
  process.exit(1);
}
const mistral = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

// --- Cosine similarity ---
function cosineSimilarity(a, b) {
  const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const normA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const normB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
  return dot / (normA * normB);
}

// --- GET test ---
app.get("/", (req, res) => {
  res.send("🚀 Backend actif ! POST /api/query pour poser une question.");
});

// --- POST chatbot ---
app.post("/api/query", async (req, res) => {
  console.log("Requête reçue :", req.body);
  const { query } = req.body;

  if (!query || !query.trim()) {
    console.log("Paramètre 'query' manquant !");
    return res.status(400).json({ error: "Paramètre 'query' manquant" });
  }

  try {
    // 1️⃣ Générer l'embedding via Mistral
    const embeddingRes = await mistral.embeddings.create({
      model: "mistral-embed",
      inputs: [query.trim()],
    });

    const embedding = embeddingRes.data[0].embedding;

    // 2️⃣ Calculer similarité avec tous les chunks
    const results = chunks.map((chunk) => ({
      text: chunk.text,
      similarity: cosineSimilarity(embedding, chunk.embedding),
    }));

    results.sort((a, b) => b.similarity - a.similarity);

    const best = results[0];
    const threshold = 0.75;

    if (best.similarity >= threshold) {
      res.json({ answer: best.text, score: best.similarity });
    } else {
      res.json({
        answer:
          "🤔 Je n'ai pas trouvé de réponse pertinente.<br>Contacte le support à <a href='mailto:helpdesk@devinci.fr' class='text-blue-600 underline'>helpdesk@devinci.fr</a> ou remplis le <a href='https://monformulaire.com' class='text-blue-600 underline'>formulaire d’assistance</a>.",
        score: best.similarity,
      });
    }
  } catch (err) {
    console.error("Erreur serveur :", err);
    res.status(500).json({ error: "Erreur lors de la recherche sémantique." });
  }
});

// --- Lancer le serveur ---
const PORT = 5000;
app.listen(PORT, () => console.log(`🚀 Backend lancé sur le port ${PORT}`));
