<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0">Criar nova escola</h6>
        </div>
        <div class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <escola-form :school="school">
            </escola-form>
          </div>
        </div>
      </div>
    </div>
    <v-tour name="pageTour" :steps="escolaDetalhesSteps" :options="tourOptions"></v-tour>
  </div>

</template>

<script>
import EscolaForm from "@/components/pages/forms/EscolaForm";
import tourStepsMixin from "@/components/tourSteps/tourStepsMixin";

export default {
  name: "escola-criar",
  layout: "DashboardLayout",
  mixins: [tourStepsMixin],
  components: {
    EscolaForm,
  },
  // passa para o form uma escola vazia com id 0 na prop school
  data() {
    return {
      school: {
        tenant: this.$auth.user.tenant,
        id: 0,
        name: null,
        legal_name: null,
        cnpj: null,
        phone: null,
        site: null,
        email: null,
        zip: null,
        street: null,
        street_number: null,
        unit: null,
        neighborhood: null,
        city: null,
        state: null,
        school_units: [],
        signatories: []
      }
    };
  }
};
</script>
