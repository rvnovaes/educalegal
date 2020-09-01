<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0">Modelos</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Modelos são usados para gerar novos contratos e documentos
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
      <div class="row">
        <div class="col">
          <entrevistas-table/>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import {Table, TableColumn, Option} from "element-ui";
import EntrevistasTable from "@/components/tables/RegularTables/EntrevistasTable";
import HourGlassSpinner from "@/components/widgets/HourGlassSpinner";

export default {
  layout: "DashboardLayout",
  components: {
    EntrevistasTable,
    HourGlassSpinner,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
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
