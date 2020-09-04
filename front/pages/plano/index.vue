<template>
  <div>

    <div class="header pb-6 d-flex align-items-center profile-header">
      <!-- Mask -->
      <span class="mask bg-gradient-default opacity-8"></span>
      <!-- Header container -->
      <div class="container-fluid d-flex align-items-center">
        <div class="row">
          <div class="col-lg-7 col-md-10">
            <h1 class="display-2 text-white">Olá, {{ fullName }}!</h1>
            <p class="text-white mt-0 mb-20">Essa é a página de perfil da sua organização.</p>
<!--            <a href="#!" class="btn btn-neutral">Edit profile</a>-->
          </div>
        </div>
      </div>
    </div>

    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col-xl-4 order-xl-2">
          <!--          <user-card></user-card>-->
          <!--          <progress-track-list></progress-track-list>-->
        </div>
        <div class="col-xl-8 order-xl-1">
          <div class="row">
            <div class="col-lg-6">

              <card gradient="info" class="border-0">
                <div class="row">
                  <div class="col">
                    <h5 class="card-title text-uppercase text-muted mb-0 text-white">Documentos já gerados</h5>
                    <span class="h2 font-weight-bold mb-0 text-white">{{ totalDocs }}</span>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-white text-dark rounded-circle shadow">
                      <i class="fa fa-file"></i>
                    </div>
                  </div>
                </div>
              </card>

            </div>
            <div class="col-lg-6">

              <card gradient="success" class="border-0">
                <div class="row">
                  <div class="col">
                    <h5 class="card-title text-uppercase text-muted mb-0 text-white">Escolas</h5>
                    <span class="h2 font-weight-bold mb-0 text-white">{{ totalSchools }}</span>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-white text-dark rounded-circle shadow">
                      <i class="ni ni-spaceship"></i>
                    </div>
                  </div>
                </div>
              </card>

            </div>
          </div>
          <div class="card-group">
            <card v-if="planUseGed" class="bg-success"><div class="card-header rounded"><span class="text-success font-weight-bold"><i class="fa fa-cloud"></i> GED</span></div></card>
              <card v-else class="bg-light"><div class="card-header rounded"><span class="text-light"><i class="fa fa-cloud" ></i> GED</span></div></card>

            <card v-if="planUseEsignature" class="bg-success"><div class="card-header rounded"><span class="text-success font-weight-bold"><i class="fa fa-signature"></i> Assinatura Eletrônica</span></div></card>
            <card v-else class="bg-light"><div class="card-header rounded" ><span class="text-light"><i class="fa fa-signature" ></i> Assinatura Eletrônica</span></div></card>

            <card v-if="planUseBulkInterview" class="bg-success"><div class="card-header rounded"><span class="text-success font-weight-bold"><i class="fa fa-magic"></i> Geração em Lote</span></div></card>
            <card v-else class="bg-light"><div class="card-header rounded"><span class="text-light"><i class="fa fa-magic" ></i> Geração em Lote</span></div></card>

          </div>
          <div class="card">
            <div class="card-header">
              {{ tenantName }}
            </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item">Plano: {{ planName }}</li>
              <li class="list-group-item">Valor: R$ {{ planValue}}</li>
              <li class="list-group-item">Limite de Documentos: {{ planDocumentLimit }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import EditProfileForm from "~/components/pages/UserProfile/EditProfileForm.vue";
import UserCard from "~/components/pages/UserProfile/UserCard.vue";
import ProgressTrackList from "~/components/widgets/ProgressTrackList.vue";

export default {
  layout: "DashboardLayout",
  components: {

  },
  data() {
    return {};
  },
  computed: {
    fullName: function () {
      return this.$auth.user.first_name + " " + this.$auth.user.last_name;
    },
    tenantName: function () {
      return this.$store.state.tenant.tenantName;
    },
    planName: function () {
      return this.$store.state.tenant.planName;
    },
    planValue: function () {
      return this.$store.state.tenant.planValue;
    },
    planDocumentLimit: function () {
      const limit = this.$store.state.tenant.planDocumentLimit;
      if (limit){
        return limit
      }
      else {
        return "ilimitado"
      }
    },
    planUseGed: function () {
      return  this.$store.state.tenant.planUseGed;
    },
    planUseBulkInterview: function () {
      return this.$store.state.tenant.planUseBulkInterview;
    },
    planUseEsignature: function () {
      return this.$store.state.tenant.planUseEsignature;
    },
    totalDocs: function () {
      return this.$store.state.dashboard.totalDocsCount;
    },
    totalSchools: function () {
      return this.$store.state.schools.schools.length;
    }

  },
  mounted() {
    this.$store.dispatch("tenant/fetchTenantData", this.$auth.user.tenant);
    this.$store.dispatch("dashboard/fetchDashBoardData");
    this.$store.dispatch("schools/fetchAllSchools");
  }
};
</script>
<style>
.profile-header {
  background-size: cover;
  background-position: center top;
  min-height: 500px;
}
</style>
