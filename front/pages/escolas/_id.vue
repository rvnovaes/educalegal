<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Editar</h6>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <escola-form :school="school"></escola-form>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <representantes-table :school="school"></representantes-table>
          </div>
        </div>
      </div>
    </div>
    <v-tour name="pageTour" :steps="escolaDetalhesSteps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import EscolaForm from "@/components/pages/forms/EscolaForm";
import RepresentantesTable from "~/components/tables/RegularTables/RepresentantesTable";
import tourStepsMixin from "@/components/tourSteps/tourStepsMixin";

export default {
  name: "escola-editar",
  layout: "DashboardLayout",
  mixins: [tourStepsMixin],
  components: {
    RepresentantesTable,
    EscolaForm,
  },
  computed: {
    school() {
      return this.$store.getters["schools/getSchool"](this.$route.params.id);
    }
  }
};
</script>
