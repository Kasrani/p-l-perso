import { defineEventHandler } from "h3";
import OpenAI from "openai/index.mjs";

const openai = new OpenAI(process.env.OPENAI_API_KEY);

export default defineEventHandler(async (event) => {
  try {
    let body = "";
    event.req.on("data", (chunk) => {
      body += chunk.toString();
    });
    await new Promise((resolve) => event.req.on("end", resolve));

    let parsedData;
    try {
      parsedData = JSON.parse(body);
    } catch (e) {
      console.log(e);
    }

    const response = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: "text-embedding-3-large",
        input: parsedData
      })
    });

    const data = await response.json();

    
    const embedding = data.data[0].embedding;
    console.log(embedding);
    
    
    return { message: embedding };
  } catch (error) {
    console.error("Erreur !", error);
    return { message: "Fichier trop volumineux !" };
  }
});
