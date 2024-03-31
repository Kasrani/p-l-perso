<template>
  <div>
    <div v-if="uploadMessage === '' && !responseMessage">
      <input type="file" @change="onFileChange" accept=".csv" style="display: none" ref="fileInput" />
      <div @click="clickFileInput" style="padding: 60px" class="border-2 border-dashed border-indigo-500/75 rounded-lg p-14 mt-6 flex flex-col items-center">
        <img width="100" src="https://cdn-icons-png.flaticon.com/512/8242/8242984.png" />
        <h4 class="mt-4">Sélectionner un fichier CSV à importer</h4>
      </div>
    </div>
    <div style="max-width: 500px" v-if="uploadMessage">{{ uploadMessage }}</div>

    <button @click="fetchEmbeddings">Obtenir les Embeddings</button>
    <pre v-if="embeddings">{{ embeddings }}</pre>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const responseMessage = ref('');
const uploadMessage = ref('');
const selectedFile = ref(null);
const fileInput = ref(null);
const embeddings = ref('');

const fetchEmbeddings = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/get-embeddings');
    if (response.ok) {
      const embeddings = await response.json();
      console.log('Embeddings reçus du serveur:', embeddings);
      uploadMessage.value = embeddings
    } else {
      console.error('Erreur lors de la récupération des embeddings');
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des embeddings:', error);
  }
};

const onFileChange = async (event) => {
  selectedFile.value = event.target.files[0];
  
  if (selectedFile.value) {
    uploadMessage.value = "Nous analysons votre document et nous préparons les résultats. Veuillez patienter quelques secondes.";
    await sendFileToServer();
  }
};

const sendFileToServer = async () => {
  if (!selectedFile.value) return;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await fetch('http://127.0.0.1:5000/test', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      console.log('Réponse du serveur :', result);
      responseMessage.value = result.message;
      uploadMessage.value = "";
    } else {
      console.error('Erreur lors de l’envoi du fichier');
      uploadMessage.value = "Erreur lors de l'envoi du fichier.";
    }
  } catch (error) {
    console.error('Erreur lors de l’envoi du fichier:', error);
    uploadMessage.value = "Erreur lors de l'envoi du fichier.";
  }
};

const clickFileInput = () => {
  fileInput.value.click();
};
</script>

<style>
/* Votre CSS personnalisé ici */
</style>
