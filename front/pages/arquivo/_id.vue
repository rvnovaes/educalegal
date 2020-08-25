<template>
  <div>
  <div v-if="loading">
    <h3 class="text-sm text-black-50"> Carregando...</h3>
  </div>
  <div v-else>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h3 class="h2 text-white d-inline-block mb-0">{{ currentDocument.name }}</h3><br>
          <h4 class="h2 text-white d-inline-block mb-0">{{ currentDocument.status | capitalize }}</h4>
          <p class="text-sm text-white font-weight-bold mb-0">
            {{ currentDocument.interview_name }}
          </p>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div>
        <card body-classes="px-0 pb-1" footer-classes="pb-2">
          <div class="card-body">
            <detalhes-documento-tab :currentDocument="currentDocument">
            </detalhes-documento-tab>
          </div>
        </card>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
import DetalhesDocumentoTab from "@/components/pages/tabs/DetalhesDocumentoTab.Vue";

export default {
  name: "detalhes-documento",
  layout: "DashboardLayout",
  components: {
    DetalhesDocumentoTab
  },
  data() {
    return {
      currentDocument: null,
      doc_uuid: this.$route.params.id,
    };
  },
  computed: {
    loading: function () {
      return !this.currentDocument
    }
  },
  created() {
    this.fetchDocumentDetails(this.doc_uuid)
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
