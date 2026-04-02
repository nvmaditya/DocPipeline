import OpenAI from "openai";

const openai = new OpenAI({
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
});

export function chunkText(text: string, chunkSize = 500, overlap = 50): string[] {
  const words = text.split(/\s+/);
  const chunks: string[] = [];

  for (let i = 0; i < words.length; i += chunkSize - overlap) {
    const chunk = words.slice(i, i + chunkSize).join(" ");
    if (chunk.trim()) {
      chunks.push(chunk.trim());
    }
    if (i + chunkSize >= words.length) break;
  }

  return chunks;
}

export function extractTextFromBuffer(buffer: Buffer, mimeType: string): string {
  if (
    mimeType === "text/plain" ||
    mimeType === "text/markdown" ||
    mimeType === "text/csv"
  ) {
    return buffer.toString("utf-8");
  }
  return buffer.toString("utf-8");
}

export function simpleTermFrequency(text: string): Map<string, number> {
  const words = text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2);

  const freq = new Map<string, number>();
  for (const word of words) {
    freq.set(word, (freq.get(word) ?? 0) + 1);
  }
  return freq;
}

export function cosineSimilarityBM25(query: string, text: string): number {
  const queryWords = query
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2);

  const textFreq = simpleTermFrequency(text);
  const totalWords = Array.from(textFreq.values()).reduce((a, b) => a + b, 0);

  let score = 0;
  const k1 = 1.5;
  const b = 0.75;
  const avgdl = 300;

  for (const qWord of queryWords) {
    const tf = textFreq.get(qWord) ?? 0;
    if (tf > 0) {
      const numerator = tf * (k1 + 1);
      const denominator = tf + k1 * (1 - b + b * (totalWords / avgdl));
      score += numerator / denominator;
    }
  }

  return score;
}

export async function generateAnswer(
  question: string,
  contexts: Array<{ content: string; documentName: string }>
): Promise<string> {
  const contextText = contexts
    .map((c, i) => `[Source ${i + 1}: ${c.documentName}]\n${c.content}`)
    .join("\n\n---\n\n");

  const response = await openai.chat.completions.create({
    model: "gpt-5.2",
    max_completion_tokens: 8192,
    messages: [
      {
        role: "system",
        content:
          "You are a helpful document intelligence assistant. Answer the user's question based ONLY on the provided document excerpts. If the answer cannot be found in the documents, say so clearly. Be concise and accurate. Cite which sources you used.",
      },
      {
        role: "user",
        content: `Question: ${question}\n\nDocument excerpts:\n\n${contextText}`,
      },
    ],
  });

  return response.choices[0]?.message?.content ?? "Unable to generate answer.";
}
