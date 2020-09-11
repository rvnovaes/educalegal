<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0 escolas">Escolas</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Os dados cadastrados em cada escola são usados no preenchimento dos documentos
          </p>
        </div>
        <div class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <escolas-table/>
        </div>
      </div>
    </div>
    <v-tour name="pageTour" :steps="escolaSteps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import EscolasTable from "~/components/tables/RegularTables/EscolasTable";
import {Table, TableColumn, Option} from "element-ui";
import schoolAlertMixin from "@/components/pages/schoolAlertMixin";
import tourStepsMixin from "@/components/tourSteps/tourStepsMixin";

export default {
  layout: "DashboardLayout",
  mixins: [schoolAlertMixin, tourStepsMixin],
  components: {
    EscolasTable,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
  },
  methods: {
    handleNew() {
      this.$router.push({
        path: "/escolas/criar"
      });
    },
  }
};
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}
</style>
