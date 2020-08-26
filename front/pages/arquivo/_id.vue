<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-11 col-11">
          <h3 v-if="currentDocument" class="h2 text-white d-inline-block mb-0">{{ currentDocument.name }}</h3>
          <h3 v-else class="h2 text-white d-inline-block mb-0">Carregando...</h3><br>
          <h4 v-if="currentDocument" class="h2 text-white d-inline-block mb-0">{{ currentDocument.status | capitalize }}</h4>
          <p v-if="currentDocument" class="text-sm text-white font-weight-bold mb-0">
            {{ currentDocument.interview_name }}
          </p>
        </div>
        <div v-if="loading" class="col-1">
          <div>
            <HourGlassSpinner></HourGlassSpinner>
          </div>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div>
        <card body-classes="px-0 pb-1" footer-classes="pb-2">
          <div class="card-body">
            <detalhes-documento-tab v-if="currentDocument" :currentDocument="currentDocument">
            </detalhes-documento-tab>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>

<script>
import DetalhesDocumentoTab from "@/components/pages/tabs/DetalhesDocumentoTab.Vue";
import HourGlassSpinner from "@/components/widgets/HourGlassSpinner";

export default {
  name: "detalhes-documento",
  layout: "DashboardLayout",
  components: {
    DetalhesDocumentoTab,
    HourGlassSpinner
  },
  data() {
    return {
      currentDocument: null,
    };
  },
  computed: {
    loading: function () {
      return !this.currentDocument
    }
  },
  created() {
    this.fetchDocumentDetails(this.$route.params.id,)
  },
  methods: {
    async fetchDocumentDetails(doc_uuid) {
      const res = await this.$axios.get("/v2/documents/" + doc_uuid);
      console.log(res);
      if (res.status === 200) {
        this.currentDocument = res.data
      }
    }
  }
};
</script>
