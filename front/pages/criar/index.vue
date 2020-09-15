<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0 criar">Criar documentos</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Os modelos abaixo são usados para gerar novos contratos e documentos
          </p>
        </div>
        <div v-if="loading" class="col-1">
          <HourGlassSpinner></HourGlassSpinner>
        </div>
        <div v-else class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <entrevistas-table/>
        </div>
      </div>
    </div>
    <v-tour name="pageTour" :steps="criarDocumentosSteps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import {Table, TableColumn, Option} from "element-ui";
import EntrevistasTable from "@/components/tables/RegularTables/EntrevistasTable";
import HourGlassSpinner from "@/components/widgets/HourGlassSpinner";
import tourStepsMixin from "@/components/tourSteps/tourStepsMixin";

export default {
  layout: "DashboardLayout",
  mixins: [tourStepsMixin],
  components: {
    EntrevistasTable,
    HourGlassSpinner,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
  },
  mounted() {
    this.$store.dispatch("schools/fetchAllSchools");
  },
  computed: {
    loading() {
      return this.$store.state.interviews.loading;
      // return true
    }
  }
};
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}
</style>
