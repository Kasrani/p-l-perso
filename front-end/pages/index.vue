<template>
  <div class="body mt-6 pt-6 pb-6 mb-6 p-6" style="max-width: 1024px; margin: auto;">
    <img width="142" src="https://i.imgur.com/ctjpoh9.png" />
    <!--
    <h2 style="margin-bottom: 24px; margin-top: 20px; font-size: 24px; margin-bottom: 10px;">Aperçu Financier</h2>
    <p>Transformez vos données en décisions stratégiques éclairées</p>
    -->

    <div class="mb-4 mt-8">


      <div class="flex w-full">
        <USelect class="mr-4 w-32" v-model="selectedPeriod" :options="periods" />
        <USelect class="w-44" v-model="selectedMonth" :options="months" />



        <div class=" flex ml-auto">
          <UTooltip text="Réinitialiser les données" :popper="{ placement: 'left' }">
            <UButton class="mr-4" icon="i-heroicons-trash" variant="outline" @click="deleteMappingResults" />
          </UTooltip>
          <UInput v-model="csvLink" placeholder="Import par URL" class="mr-4 w-40">
            <template #trailing>
              <span class="text-gray-500 dark:text-gray-400 text-xs">CSV</span>
            </template>
          </UInput>
          <UTooltip v-if="csvLink !== ''" text="Importer" :popper="{ placement: 'right' }">
            <UButton class="mr-4" icon="i-heroicons-paper-airplane" @click="fetchMappingResults" />
          </UTooltip>

        </div>
        <div>
          <input type="file" id="fileInput" @change="onFileChange" accept=".csv" style="display: none;" />
          <div>
            <UButton :loading="loading" icon="i-heroicons-arrow-up-on-square" label="Import CSV" size="sm"
              color="primary" variant="outline" @click="triggerFileInput" />
          </div>
        </div>


        <!--
        <UPopover class="ml-4" :popper="{ placement: 'bottom-start' }">
            <UButton icon="i-heroicons-calendar-days-20-solid">
              {{ format(selected.start, 'd MMM, yyy') }} - {{ format(selected.end, 'd MMM, yyy') }}
            </UButton>

            <template #panel="{ close }">
              <div class="flex items-center sm:divide-x divide-gray-200 dark:divide-gray-800">
                <div class="hidden sm:flex flex-col py-4">
                  <UButton v-for="(range, index) in ranges" :key="index" :label="range.label" color="gray"
                    variant="ghost" class="rounded-none px-6"
                    :class="[isRangeSelected(range.duration) ? 'bg-gray-100 dark:bg-gray-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800/50']"
                    truncate @click="selectRange(range.duration)" />
                </div>

                <DatePicker v-model="selected" @close="close" />
              </div>
            </template>
          </UPopover>
          -->
      </div>

    </div>




    <UTabs :items="items" class="w-full">
      <template #mapping="{ item }">
        <UCard class="mt-4" :ui="{
          base: '',
          ring: '',
          divide: 'divide-y divide-gray-200 dark:divide-gray-700',
          header: { padding: 'px-4 py-5' },
          body: { padding: '', base: 'divide-y divide-gray-200 dark:divide-gray-700' },
          footer: { padding: 'p-4' }
        }">
          <div class="flex px-3 py-3.5 border-b border-gray-200 dark:border-gray-700">
            <UInput v-model="searchQuery" placeholder="Rechercher..." icon="i-heroicons-magnifying-glass-20-solid" trailing :loading="loadingSearch" />
            <USelectMenu class="ml-auto" v-model="selectedColumns" :options="columns" multiple placeholder="Columns" />
            
          </div>

          <UTable class="w-full" :ui="{ td: { base: 'max-w-80 truncate' } }" :rows="displayedRows"
            :columns="selectedColumns" :loading="loading"
            :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
            :progress="{ color: 'primary', animation: 'carousel' }">
          
            <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
          </UTable>
          <!-- Number of rows & Pagination -->
          <template #footer>
            <div class="flex flex-wrap justify-between items-center">
              <div>
                <span v-if="totalRows > 0" class="text-sm leading-5">
                  Tous les résultats
                  <span class="font-medium">({{ totalRows * 10 }})</span>
                </span>
              </div>

              <UPagination v-model="page" :page-count="pageCount" :total="totalRows" :ui="{
          wrapper: 'flex items-center gap-1',
          rounded: '!rounded-full min-w-[32px] justify-center',
          default: {
            activeButton: {
              variant: 'outline'
            }
          }
        }" />
            </div>
          </template>
        </UCard>
      </template>
      <template #compteResultats="{ item }">
        <UCard class="mt-4">
          <div class="flex w-full mr-8">
            <div class="flex w-full">
              <div class="header flex w-full">
                <div class="w-full p-0">
                  <UBadge
                    style="width: 100%;padding: 10px;display: block;text-align: center;justify-items: center;justify-items: center;"
                    color="red" size="lg" label="CHARGES" variant="subtle" />
                </div>
              </div>
            </div>

            <div class="flex w-full ml-8">
              <div class="w-full">
                <UBadge
                  style="width: 100%;padding: 10px;display: block;text-align: center;justify-items: center;justify-items: center;"
                  color="green" size="lg" label="PRODUITS" variant="subtle" />
              </div>
            </div>
          </div>
          <div>

          </div>







          <div class="flex mt-4">
            <div class="flex w-full mr-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 truncate' } }"
                :rows="chargesExploitationData" :columns="chargesExploitationColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">

                <template #totalCharges-data="{ row }">
                  <p
                    :style="{ color: row === chargesExploitationData[chargesExploitationData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalCharges) }}
                  </p>
                </template>
                <template #charges-data="{ row }">
                  <p
                    :style="{ color: row === chargesExploitationData[chargesExploitationData.length - 1] ? 'white' : '' }">
                    {{ row.charges }}
                  </p>
                </template>
                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>

              </UTable>
            </div>
            <div class="flex w-full ml-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 w-full truncate' } }"
                :rows="productsExploitationData" :columns="productsExploitationColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">
                <template #totalProducts-data="{ row }">
                  <p
                    :style="{ color: row === productsExploitationData[productsExploitationData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalProducts) }}
                  </p>
                </template>
                <template #products-data="{ row }">
                  <p
                    :style="{ color: row === productsExploitationData[productsExploitationData.length - 1] ? 'white' : '' }">
                    {{ row.products }}
                  </p>
                </template>
                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
              </UTable>
            </div>
          </div>



          <div class="flex mt-4">
            <div class="flex w-full mr-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 w-full truncate' } }"
                :rows="chargesFinancieresData" :columns="chargesFinancieresColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">


                <template #totalCharges-data="{ row }">
                  <p
                    :style="{ color: row === chargesFinancieresData[chargesFinancieresData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalCharges) }}
                  </p>
                </template>
                <template #charges-data="{ row }">
                  <p
                    :style="{ color: row === chargesFinancieresData[chargesFinancieresData.length - 1] ? 'white' : '' }">
                    {{ row.charges }}
                  </p>
                </template>


                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
              </UTable>
            </div>
            <div class="flex w-full ml-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 w-full truncate' } }"
                :rows="productsFinancieresData" :columns="productsFinancieresColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">

                <template #totalProducts-data="{ row }">
                  <p
                    :style="{ color: row === productsFinancieresData[productsFinancieresData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalProducts) }}
                  </p>
                </template>
                <template #products-data="{ row }">
                  <p
                    :style="{ color: row === productsFinancieresData[productsFinancieresData.length - 1] ? 'white' : '' }">
                    {{ row.products }}
                  </p>
                </template>
                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
              </UTable>
            </div>
          </div>


          <div class="flex mt-4">
            <div class="flex w-full mr-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 w-full truncate' } }"
                :rows="chargesExceptionnellesData" :columns="chargesExceptionnellesColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">


                <template #totalCharges-data="{ row }">
                  <p
                    :style="{ color: row === chargesExceptionnellesData[chargesExceptionnellesData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalCharges) }}
                  </p>
                </template>
                <template #charges-data="{ row }">
                  <p
                    :style="{ color: row === chargesExceptionnellesData[chargesExceptionnellesData.length - 1] ? 'white' : '' }">
                    {{ row.charges }}
                  </p>
                </template>


                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
              </UTable>
            </div>
            <div class="flex w-full ml-4">
              <UTable class="w-full custom-table" :ui="{ td: { base: 'max-w-80 w-full truncate' } }"
                :rows="productsExceptionnellesData" :columns="productsExceptionnellesColumns" :loading="loading"
                :loading-state="{ icon: 'i-heroicons-arrow-path-20-solid', label: `Chargement des données... ${progress}%` }"
                :progress="{ color: 'primary', animation: 'carousel' }">

                <template #totalProducts-data="{ row }">
                  <p
                    :style="{ color: row === productsExceptionnellesData[productsExceptionnellesData.length - 1] ? 'white' : '' }">
                    {{ formatDebit(row.totalProducts) }}
                  </p>
                </template>
                <template #products-data="{ row }">
                  <p
                    :style="{ color: row === productsExceptionnellesData[productsExceptionnellesData.length - 1] ? 'white' : '' }">
                    {{ row.products }}
                  </p>
                </template>
                <template #empty-state>
                  <div class="flex flex-col items-center justify-center py-6 gap-3">
                    <span class="italic text-sm">Aucune donnée</span>
                  </div>
                </template>
              </UTable>
            </div>
          </div>


          <div class="mt-2 flex flex-col">

            <div class="flex w-full text-center">
              <div class="header flex w-full">
                <div class="mt-2 w-full flex" style="padding: 0 32px 0 20px; align-items: center;">
                  <div>
                    Total des charges
                  </div>
                  <UBadge style="padding: 10px;display: block;text-align: center;justify-items: center;"
                    class="mb-2 ml-auto" color="red" size="lg" :label="`${formatDebit(totalCharges)}`"
                    variant="subtle" />
                </div>

                <div class="mt-2 w-full flex" style="padding: 0 20px 0 32px; align-items: center;">
                  <div>
                    Total des produits
                  </div>
                  <UBadge style="padding: 10px;display: block;text-align: center;justify-items: center;"
                    class="mb-2 ml-auto" color="green" size="lg" :label="`${formatDebit(totalProducts)}`"
                    variant="subtle" />
                </div>
              </div>

            </div>
          </div>



          <div class="mt-4 flex flex-col">

            <div class="flex w-full text-center">
              <div class="header flex w-full">
                <UCard class="mr-4 w-full">
                  <p>Chiffre d'Affaires</p>
                  <UBadge class="mt-3" size="md" :label="formatDebit(chiffreAffairesData)" variant="subtle" />
                </UCard>
                <UCard class="ml-2 mr-2 w-full">
                  <p>Résultats Net</p>
                  <UBadge class="mt-3" size="md" :label="formatDebit(resultatNet)" variant="subtle" />
                </UCard>
                <UCard class="ml-4 w-full">
                  <p>EBITDA</p>
                  <UBadge class="mt-3" size="md" :label="formatDebit(ebitdaData)" variant="subtle" />

                </UCard>
              </div>

            </div>
          </div>







        </UCard>
      </template>

    </UTabs>
    <UNotifications />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';


const progress = ref(0);

// Connexion au serveur Socket.IO
const socket = io('https://aidviz.onrender.com');

socket.on('connect', () => {
  console.log('Connected to Socket.IO server');
});

socket.on('connect_error', (err) => {
  console.error('Connection error:', err);
});

socket.on('progress', (data) => {
  // console.log('Progress update received:', data);
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});

onMounted(() => {
  // Écouter les mises à jour de progression du serveur
  socket.on('progress', (data) => {
    progress.value = data.progress;
  });
});

onUnmounted(() => {
  // Fermer la connexion lorsque le composant est détruit
  socket.off('progress');
  socket.close();
});



const loading = ref(false);

const csvLink = ref('');


const mappingResults = ref([]);
const chargesExploitationData = ref([]);
const productsExploitationData = ref([]);
const productsFinancieresData = ref([]);
const chargesFinancieresData = ref([]);
const chargesExceptionnellesData = ref([]);
const productsExceptionnellesData = ref([]);


const resultatNet = ref(0);
const totalCharges = ref(0);
const totalProducts = ref(0);

const items = [
  {
    slot: 'compteResultats',
    label: 'Compte de résultats'
  },
  {
    slot: 'mapping',
    label: 'Mapping'
  }
]


const page = ref(1); // Page actuelle
const pageCount = 10; // Nombre de résultats par page
const totalRows = ref(0); // Total des lignes, à mettre à jour lorsque vous chargez les données


const toast = useToast()

const searchQuery = ref('');
const loadingSearch = ref(false);

const displayedRows = computed(() => {
  const startIndex = (page.value - 1) * pageCount;
  
  // Filtrer les données en fonction de l'année et du mois sélectionnés
  const filteredData = mappingResults.value.filter(row => {
    const resultDate = new Date(row.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0'); // Format le mois pour correspondre à votre format de sélection

    return (selectedPeriod.value === 'all' || resultYear === selectedPeriod.value) && 
           (selectedMonth.value === 'all' || resultMonth === selectedMonth.value);
  });

  // Appliquer la recherche si nécessaire
  const searchedData = searchQuery.value ? 
    filteredData.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    ) : filteredData;

  // Retourner les lignes pour la page courante
  return searchedData.slice(startIndex, startIndex + pageCount);
});






const periods = ['2021', '2020', '2019']

const selectedPeriod = ref(periods[0])

const months = [
  { label: 'Tous les mois', value: 'all' },
  { label: 'Janvier', value: '01' },
  { label: 'Février', value: '02' },
  { label: 'Mars', value: '03' },
  { label: 'Avril', value: '04' },
  { label: 'Mai', value: '05' },
  { label: 'Juin', value: '06' },
  { label: 'Juillet', value: '07' },
  { label: 'Août', value: '08' },
  { label: 'Septembre', value: '09' },
  { label: 'Octobre', value: '10' },
  { label: 'Novembre', value: '11' },
  { label: 'Décembre', value: '12' }
];


const selectedMonth = ref(months[0].value);




import { sub, format, isSameDay } from 'date-fns';

const currentYear = new Date().getFullYear();


const ranges = [
  { label: 'Last 7 days', duration: { days: 7 } },
  { label: 'Last 14 days', duration: { days: 14 } },
  { label: 'Last 30 days', duration: { days: 30 } },
  { label: 'Last 3 months', duration: { months: 3 } },
  { label: 'Last 6 months', duration: { months: 6 } },
  { label: 'Last year', duration: { years: 1 } },
  { label: 'All', duration: { years: 7 } },
  { label: 'Toute l\'historique', duration: { start: new Date('1900-01-01'), end: new Date() } },
  { label: '2021', duration: { start: new Date('2021-01-01'), end: new Date('2021-12-31') } },
  { label: '2020', duration: { start: new Date('2020-01-01'), end: new Date('2020-12-31') } },
  { label: '2019', duration: { start: new Date('2019-01-01'), end: new Date('2019-12-31') } }
];

const selected = ref({
  start: new Date('2000-01-01'), // ou une autre année représentant le début de vos données
  end: new Date()
});

function isRangeSelected(duration) {
  return isSameDay(selected.value.start, duration.start && isSameDay(selected.value.end, duration.end));
}

function selectRange(duration) {
  selected.value.start = duration.start;
  selected.value.end = duration.end;
}


const mappinglevel1Data = ref([]);

const sort = ref({
  column: 'count',
  direction: 'desc'
})


const mappingLevel1Columns = [
  { key: 'label', label: 'Catégorie (x)' },
  { key: 'debitSum', label: 'Somme des Débits' },
  { key: 'creditSum', label: 'Somme des Crédit' }
];

const chargesExploitationColumns = [
  { key: 'charges', label: "Charges d'exploitation" },
  { key: 'totalCharges', label: 'Total' },
];
const chargesFinancieresColumns = [
  { key: 'charges', label: "Charges financiéres" },
  { key: 'totalCharges', label: 'Total' },
];
const chargesExceptionnellesColumns = [
  { key: 'charges', label: "Charges exceptionnelles" },
  { key: 'totalCharges', label: 'Total' },
];

const productsExploitationColumns = [
  { key: 'products', label: "Produits d'exploitation" },
  { key: 'totalProducts', label: 'Total' },
];
const productsFinancieresColumns = [
  { key: 'products', label: "Produits financiéres" },
  { key: 'totalProducts', label: 'Total' },
];
const productsExceptionnellesColumns = [
  { key: 'products', label: "Produits exceptionnelles" },
  { key: 'totalProducts', label: 'Total' },
];

const mappingColumns = [
  { key: 'libelleCompte', label: 'Libellé compte' },
  { key: 'mapped_categorie_1', label: 'Mapping' },
  // { key: 'mapped_categorie_2', label: 'Mapping Level 2' },
  // { key: 'mapped_categorie_3', label: 'Mapping Level 3' }
];

// Fonction pour formater les résultats de mapping
const formatMappingResults = (data) => {
  return data.map(result => {
    // Exemple si result est un objet avec des propriétés définies
    const { compte, debit, credit, libelleCompte, mapped_categorie_1, mapped_categorie_2, mapped_categorie_3, mapped_categorie_4 } = result;

    return {
      compte,
      libelleCompte,
      mapped_categorie_1,
      mapped_categorie_2,
      mapped_categorie_3,
      mapped_categorie_4,
      debit,
      credit,
    };
  });
};




const mappingResultsFormatted = ref([]);




// Fonction pour récupérer les résultats de mapping avec fetch
const fetchMappingResults = async () => {

  loading.value = true
  try {
    if (csvLink.value !== "") {
      await submitCSVLink();
    }

    const response = await fetch('https://aidviz.onrender.com/mapping-results');
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des résultats de mapping');
    }
    const data = await response.json();
    mappingResults.value = data;
    mappingResultsFormatted.value = formatMappingResults(data);
    updateMappingLevel1Data(mappingResultsFormatted.value);
    saveMappingResults(data);
    totalRows.value = mappingResults.value.length;
  } catch (error) {
    console.error('Erreur lors de la récupération des résultats de mapping :', error);
  }
};


// Créer ou ouvrir une base de données IndexedDB
const dbName = "MyDatabase";
const storeName = "MappingResults";
const version = 1;

const openDatabase = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(dbName, version);

    request.onerror = (event) => {
      console.error("Database error:", event.target.error);
      reject(event.target.error);
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { autoIncrement: true });
      }
    };

    request.onsuccess = (event) => {
      resolve(event.target.result);
    };
  });
};

// Sauvegarder les résultats de mapping dans IndexedDB
const saveMappingResults = async (data) => {
  try {
    const db = await openDatabase();
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);

    const clearRequest = store.clear();
    clearRequest.onsuccess = () => {
      const addRequest = store.add(data);
      addRequest.onsuccess = () => {
        console.log("Mapping results saved successfully!");
      };
    };

    clearRequest.onerror = (event) => {
      console.error("Error clearing the store:", event.target.error);
    };

    addRequest.onerror = (event) => {
      console.error("Error saving data:", event.target.error);
    };

    db.close();
  } catch (error) {
    console.error("Error working with IndexedDB:", error);
  }
};


// Charger les résultats de mapping depuis IndexedDB
const loadMappingResults = async () => {
  try {
    const db = await openDatabase();
    const transaction = db.transaction([storeName], "readonly");
    const store = transaction.objectStore(storeName);

    const getRequest = store.getAll();
    getRequest.onsuccess = (event) => {
      const data = event.target.result;
      if (data.length > 0) {
        const latestData = data[data.length - 1];
        mappingResults.value = latestData;
        mappingResultsFormatted.value = formatMappingResults(latestData);
        updateMappingLevel1Data(mappingResultsFormatted.value);
        totalRows.value = latestData.length;
      }
      db.close();
    };

    getRequest.onerror = (event) => {
      console.error("Error fetching data:", event.target.error);
    };

    db.close();
  } catch (error) {
    console.error("Error working with IndexedDB:", error);
  }
};


const deleteMappingResults = async () => {
  try {
    const db = await openDatabase();
    const transaction = db.transaction([storeName], "readwrite");
    const store = transaction.objectStore(storeName);

    const deleteRequest = store.clear();

    deleteRequest.onsuccess = () => {
      console.log("Toutes les données de mapping ont été supprimées.");
      toast.add({ title: 'Données supprimées.' })
      mappingResults.value = [];
    };

    deleteRequest.onerror = (event) => {
      console.error("Error deleting data:", event.target.error);
    };

    db.close();
  } catch (error) {
    console.error("Error working with IndexedDB:", error);
  }
};


// Dans votre script Vue
onMounted(() => {
  loadMappingResults();
});




/*
// Fonction pour récupérer les résultats de mapping avec fetch
const fetchMappingResults = async () => {
  try {
    // Envoi du lien CSV et récupération des résultats de mapping
    await submitCSVLink();

    // Une fois que le lien CSV est soumis avec succès, récupérer les résultats de mapping
    const response = await fetch('https://aidviz.onrender.com/mapping-results');
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des résultats de mapping');
    }
    const data = await response.json();
    mappingResults.value = data;
    mappingResultsFormatted.value = formatMappingResults(data);
    updateMappingLevel1Data(mappingResultsFormatted.value);
  } catch (error) {
    console.error('Erreur lors de la récupération des résultats de mapping :', error);
  }
};
*/



const submitCSVLink = async () => {
  try {
    const response = await fetch('https://aidviz.onrender.com/submit-csv-link', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ link: csvLink.value })
    });
    if (!response.ok) {
      throw new Error('Erreur lors de la soumission du lien du fichier CSV');
    }
    console.log('Lien du fichier CSV soumis avec succès');
    toast.add({ title: 'Lien du fichier CSV soumis avec succès' })
  } catch (error) {
    console.error('Erreur lors de la soumission du lien du fichier CSV :', error);
  }
};

const updateMappingLevel1Data = (results) => {
  const counts = {};
  const debitSums = {};
  const creditSums = {};

  results.forEach(result => {
    if (result.mapped_categorie_1 in counts) {
      counts[result.mapped_categorie_1]++;
      if (debitSums[result.mapped_categorie_1]) {
        debitSums[result.mapped_categorie_1] += parseFloat(result.debit);
      } else {
        debitSums[result.mapped_categorie_1] = parseFloat(result.debit);
      }
      if (creditSums[result.mapped_categorie_1]) {
        creditSums[result.mapped_categorie_1] += parseFloat(result.credit);
      } else {
        creditSums[result.mapped_categorie_1] = parseFloat(result.credit);
      }
    } else {
      counts[result.mapped_categorie_1] = 1;
      debitSums[result.mapped_categorie_1] = parseFloat(result.debit);
      creditSums[result.mapped_categorie_1] = parseFloat(result.credit);
    }
  });

  mappinglevel1Data.value = Object.entries(counts).map(([label, count]) => ({
    label,
    count,
    debitSum: debitSums[label] ? formatDebit(debitSums[label]) : "0",
    creditSum: creditSums[label] ? formatDebit(creditSums[label]) : "0"
  }));
};


// Fonction pour formater le montant du débit
const formatDebit = (amount) => {
  const numberAmount = Number(amount);
  return numberAmount.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' });
};


const totalMappingResults = computed(() => mappingResults.value.length);








const listerChargesExploitation = () => {
  const categoriesChargesExploitation = ["Charges opérationnelles", "Impôts et taxes", "Charges de personnel", "Autres charges operationnels"];
  let totalCharges = 0;

  const chargesExploitation = categoriesChargesExploitation.reduce((acc, categorie) => {
    acc[categorie] = 0;
    return acc;
  }, {});

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0'); // Format le mois pour correspondre à votre format de sélection

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {

      if (categoriesChargesExploitation.includes(result.mapped_categorie_1)) {
        const montant = parseFloat(result.debit) - parseFloat(result.credit);
        chargesExploitation[result.mapped_categorie_1] += montant;
        totalCharges += montant;
      }
    }
  });

  chargesExploitation["Total"] = totalCharges;

  chargesExploitationData.value = Object.entries(chargesExploitation).map(([label, totalCharges]) => ({
    charges: label,
    totalCharges: totalCharges.toFixed(2)
  }));
};




watch([mappingResults, selectedPeriod, selectedMonth], listerChargesExploitation);








const listerProductsExploitation = () => {
  const categoriesProductsExploitation = ["Revenue", "Dotation et reprises aux amortissements et aux PRC"];
  let totalProduits = 0;

  const productsExploitation = categoriesProductsExploitation.reduce((acc, categorie) => {
    acc[categorie] = 0;
    return acc;
  }, {});

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      if (categoriesProductsExploitation.includes(result.mapped_categorie_1)) {
        const montant = parseFloat(result.credit) - parseFloat(result.debit);
        productsExploitation[result.mapped_categorie_1] += montant;
        totalProduits += montant;
      }
    }
  });

  productsExploitation["Total"] = totalProduits;

  productsExploitationData.value = Object.entries(productsExploitation).map(([label, totalProducts]) => ({
    products: label,
    totalProducts: totalProducts.toFixed(2)
  }));
};


watch([mappingResults, selectedPeriod, selectedMonth], listerProductsExploitation);






const listerProductsFinancieres = () => {
  let totalProduitsFinanciers = 0;

  const productsFinancieres = {};

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      if (result.mapped_categorie_1 === "Résultat financiers") {
        const montant = parseFloat(result.credit) - parseFloat(result.debit);
        productsFinancieres[result.mapped_categorie_1] = (productsFinancieres[result.mapped_categorie_1] || 0) + montant;
        totalProduitsFinanciers += montant;
      }
    }
  });

  productsFinancieres["Total"] = totalProduitsFinanciers;

  productsFinancieresData.value = Object.entries(productsFinancieres).map(([label, total]) => ({
    products: label,
    totalProducts: total.toFixed(2)
  }));
};


watch([mappingResults, selectedPeriod, selectedMonth], listerProductsFinancieres);




const listerChargesFinancieres = () => {
  let totalChargesFinancieres = 0;

  const chargesFinancieres = {};

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      if (result.mapped_categorie_1 === "Charges financières") {
        const montant = parseFloat(result.debit) - parseFloat(result.credit);
        chargesFinancieres[result.mapped_categorie_1] = (chargesFinancieres[result.mapped_categorie_1] || 0) + montant;
        totalChargesFinancieres += montant;
      }
    }
  });

  chargesFinancieres["Total"] = totalChargesFinancieres;

  chargesFinancieresData.value = Object.entries(chargesFinancieres).map(([label, total]) => ({
    charges: label,
    totalCharges: total.toFixed(2)
  }));
};


watch([mappingResults, selectedPeriod, selectedMonth], listerChargesFinancieres);






const listerProductsExceptionnelles = () => {
  let totalProduitsExceptionnels = 0;

  const productsExceptionnelles = {};

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      if (result.mapped_categorie_1 === "Résultat exceptionnel") {
        const montant = parseFloat(result.credit) - parseFloat(result.debit);
        productsExceptionnelles[result.mapped_categorie_1] = (productsExceptionnelles[result.mapped_categorie_1] || 0) + montant;
        totalProduitsExceptionnels += montant;
      }
    }
  });

  productsExceptionnelles["Total"] = totalProduitsExceptionnels;

  productsExceptionnellesData.value = Object.entries(productsExceptionnelles).map(([label, total]) => ({
    products: label,
    totalProducts: total.toFixed(2)
  }));
};


watch([mappingResults, selectedPeriod, selectedMonth], listerProductsExceptionnelles);




const listerChargesExceptionnelles = () => {
  let totalChargesExceptionnelles = 0;

  const chargesExceptionnelles = {};

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      if (result.mapped_categorie_1 === "Charges exceptionnelles") {
        const montant = parseFloat(result.debit) - parseFloat(result.credit);
        chargesExceptionnelles[result.mapped_categorie_1] = (chargesExceptionnelles[result.mapped_categorie_1] || 0) + montant;
        totalChargesExceptionnelles += montant;
      }
    }
  });

  chargesExceptionnelles["Total"] = totalChargesExceptionnelles;

  chargesExceptionnellesData.value = Object.entries(chargesExceptionnelles).map(([label, total]) => ({
    charges: label,
    totalCharges: total.toFixed(2)
  }));
};


watch([mappingResults, selectedPeriod, selectedMonth], listerChargesExceptionnelles);


// Fonction pour calculer les totaux
const calculerTotaux = () => {
  totalCharges.value = chargesExploitationData.value.reduce((acc, curr) => acc + parseFloat(curr.totalCharges), 0) +
    chargesFinancieresData.value.reduce((acc, curr) => acc + parseFloat(curr.totalCharges), 0) +
    chargesExceptionnellesData.value.reduce((acc, curr) => acc + parseFloat(curr.totalCharges), 0);

  totalProducts.value = productsExploitationData.value.reduce((acc, curr) => acc + parseFloat(curr.totalProducts), 0) +
    productsFinancieresData.value.reduce((acc, curr) => acc + parseFloat(curr.totalProducts), 0) +
    productsExceptionnellesData.value.reduce((acc, curr) => acc + parseFloat(curr.totalProducts), 0);

  resultatNet.value = totalProducts.value - totalCharges.value;
  loading.value = false
};

// Watchers pour recalculer les totaux lorsque les données changent
watch(chargesExploitationData, calculerTotaux);
watch(chargesFinancieresData, calculerTotaux);
watch(chargesExceptionnellesData, calculerTotaux);
watch(productsExploitationData, calculerTotaux);
watch(productsFinancieresData, calculerTotaux);
watch(productsExceptionnellesData, calculerTotaux);




const chiffreAffairesData = ref(0);
const ebitdaData = ref(0);

const calculerChiffreAffairesEtEBITDA = () => {
  let chiffreAffaires = 0;
  let chargesExploitation = 0;
  let produitsFinanciers = 0;
  let produitsExceptionnelles = 0;
  let chargesFinancieres = 0;
  let dotationsAmortissementsProvisions = 0;

  mappingResults.value.forEach(result => {
    const resultDate = new Date(result.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0');

    if (resultYear === selectedPeriod.value && (selectedMonth.value === 'all' || resultMonth === selectedMonth.value)) {
      switch (result.mapped_categorie_1) {
        case "Revenue":
          chiffreAffaires += parseFloat(result.credit) - parseFloat(result.debit);
          break;
        case "Charges opérationnelles":
        case "Autres charges operationnels":
        case "Impôts et taxes":
        case "Charges de personnel":
          chargesExploitation += parseFloat(result.debit) - parseFloat(result.credit);
          break;
        case "Résultat financiers":
          produitsFinanciers += parseFloat(result.credit) - parseFloat(result.debit);
          break;
        case "Résultat exceptionnel":
          produitsExceptionnelles += parseFloat(result.credit) - parseFloat(result.debit);
          break;
        case "Charges financières":
          chargesFinancieres += parseFloat(result.debit) - parseFloat(result.credit);
          break;
        case "Dotation et reprises aux amortissements et aux PRC":
          dotationsAmortissementsProvisions += parseFloat(result.debit) - parseFloat(result.credit);
          break;
      }
    }
  });

  const ebitda = chiffreAffaires - chargesExploitation + produitsFinanciers + produitsExceptionnelles - chargesFinancieres - dotationsAmortissementsProvisions;

  chiffreAffairesData.value = chiffreAffaires;
  ebitdaData.value = ebitda;

  return { chiffreAffaires, ebitda };
};


watch([mappingResults, selectedPeriod, selectedMonth], () => {
  const { chiffreAffaires, ebitda } = calculerChiffreAffairesEtEBITDA();
  chiffreAffairesData.value = chiffreAffaires;
  ebitdaData.value = ebitda;
});




const triggerFileInput = () => {
  document.getElementById('fileInput').click();
};

const onFileChange = async (e) => {
  loading.value = true;
  toast.add({ title: 'Import du fichier en cours' })
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch('https://aidviz.onrender.com/submit-csv-file', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Erreur lors de l’envoi du fichier CSV');
    }
    // Traitez la réponse si nécessaire
    const result = await response.json();
    console.log(result);
    // loading.value = false
    await fetchMappingResults();
  } catch (error) {
    console.error('Erreur lors de l’envoi du fichier CSV:', error);
  }
};




const columns = [{
  key: 'compte',
  label: 'Compte'
}, {
  key: 'libelleCompte',
  label: 'LibelleCompte'
}, {
  key: 'mapped_categorie_1',
  label: 'Level 1'
}, {
  key: 'mapped_categorie_2',
  label: 'Level 2'
}, {
  key: 'mapped_categorie_3',
  label: 'Level 3'
}]

// const selectedColumns = ref([...columns])
// const selectedColumns = ref([columns[1]])
const selectedColumns = ref(columns.slice(0, 3))



const updateDisplayedRowsAndPagination = () => {
  loadingSearch.value = true;
  const filteredData = mappingResults.value.filter(row => {
    const resultDate = new Date(row.date);
    const resultYear = resultDate.getFullYear().toString();
    const resultMonth = (resultDate.getMonth() + 1).toString().padStart(2, '0'); 

    return (selectedPeriod.value === 'all' || resultYear === selectedPeriod.value) && 
           (selectedMonth.value === 'all' || resultMonth === selectedMonth.value);
  });

  const searchedData = searchQuery.value ? 
    filteredData.filter(row => 
      Object.values(row).some(value => 
        String(value).toLowerCase().includes(searchQuery.value.toLowerCase())
      )
    ) : filteredData;

  // Mettre à jour le total des lignes pour la pagination
  totalRows.value = searchedData.length;

  // Définir les lignes affichées pour la page actuelle
  const startIndex = (page.value - 1) * pageCount;
  displayedRows.value = searchedData.slice(startIndex, startIndex + pageCount);
  loadingSearch.value = false;
};

// Appeler cette fonction chaque fois qu'un filtre change
watch([mappingResults, selectedPeriod, selectedMonth, searchQuery], updateDisplayedRowsAndPagination);


</script>

<style>
.body {
  display: flex;
  flex-direction: column;

}

tbody {
  text-align: left !important;
}

.custom-table th:last-child {
  text-align: right;
}

.custom-table td:last-child {
  text-align: right;
}
</style>