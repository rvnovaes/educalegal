<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0 painel">Painel</h6>
        </div>
        <div class="col-lg-6 col-5 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
      <!-- Card stats -->
      <div class="row">
        <div class="col-xl-3 col-md-6">
          <stats-card class="documentos-gerados"
                      title="Documentos gerados no mês"
                      type="gradient-green"
                      :sub-title="cmDocsCount"
                      icon="fa fa-file">
            <template slot="footer">
              <div v-if="finishedDocDelta >= 0">
                <span class="text-success mr-2 documentos-gerados-mes-anterior"><i
                  class="fa fa-arrow-up"></i> {{ finishedDocDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmDocsCount }})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2 documentos-gerados-mes-anterior"><i
                  class="fa fa-arrow-down"></i> {{ finishedDocDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmDocsCount }})</span>
              </div>
            </template>
          </stats-card>
        </div>

        <div class="col-xl-3 col-md-6">
          <stats-card class="documentos-andamento"
                      title="Documentos em andamento no mês"
                      type="gradient-orange"
                      :sub-title="cmInProgressDocsCount"
                      icon="fa fa-file">
            <template slot="footer">
              <div v-if="inProgressDocDelta >= 0">
                <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> {{ inProgressDocDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmInProgressDocsCount }})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> {{ inProgressDocDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmInProgressDocsCount }})</span>
              </div>
            </template>
          </stats-card>
        </div>

        <div class="col-xl-3 col-md-6">
          <stats-card class="assinaturas"
                      title="Assinaturas Eletrônicas no mês"
                      type="gradient-green"
                      :sub-title="cmSignatureCount"
                      icon="fa fa-signature">

            <template slot="footer">
              <div v-if="signatureDelta >= 0">
                <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> {{ signatureDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmSignatureCount }})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> {{ signatureDelta }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmSignatureCount }})</span>
              </div>
            </template>
          </stats-card>
        </div>

        <div class="col-xl-3 col-md-6">
          <stats-card class="assinaturas-andamento"
                      title="Assinaturas Eletrônicas em andamento no mês"
                      type="gradient-orange"
                      :sub-title="cmInProgressSinatureCount"
                      icon="fa fa-signature">

            <template slot="footer">
              <div v-if="inProgressDocDelta >= 0">
                <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> {{
                    inProgressSignatureDelta
                  }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmInProgressSignatureCount }})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> {{
                    inProgressSignatureDelta
                  }} %</span><span
                class="text-nowrap">Em relação ao mês anterior ({{ lmInProgressSignatureCount }})</span>
              </div>
            </template>
          </stats-card>
        </div>

      </div>
    </base-header>
    <v-tour name="painelTour" :steps="steps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import RouteBreadCrumb from "@/components/argon-core/Breadcrumb/RouteBreadcrumb";
import StatsCard from "@/components/argon-core/Cards/StatsCard";
import Card from "@/components/argon-core/Cards/Card";

export default {
  layout: "DashboardLayout",
  components: {
    RouteBreadCrumb,
    StatsCard,
    Card
  },
  data() {
    return {
      tourOptions: {
        useKeyboardNavigation: true,
        labels: {
          buttonSkip: "Dispensar",
          buttonPrevious: "Anterior",
          buttonNext: "Próximo",
          buttonStop: "Fim"
        }
      },
      steps: [
        {
          target: ".painel",
          header: {
            title: "Painel",
          },
          params: {
            placement: "right"
          },
          content: `No painel você acessa informações gerais sobre o uso do Educa Legal.`
        },
        {
          target: ".documentos-gerados",
          header: {
            title: "Documentos gerados",
          },
          params: {
            placement: "right"
          },
          content: `Aqui você vê quantos documentos sua escola criou no mês.`
        },
        {
          target: ".documentos-gerados-mes-anterior",
          content: `Você compara também com os documentos gerados no mês anterior.`
        },
        {
          target: ".documentos-andamento",
          header: {
            title: "Documentos em andamento",
          },
          content: `São os documentos que ainda estão sendo preenchidos.`
        },
        {
          target: ".assinaturas",
          header: {
            title: "Assinaturas eletrônicas",
          },
          content: `Aqui você vê quantos documentos sua escola enviou para assinatura eletrônica.`
        },
        {
          target: ".assinaturas-andamento",
          header: {
            title: "Assinaturas em andamento",
          },
          content: `Representam os documentos que foram enviados para os destinatários mais ainda não contam com a assinatura de todos. `
        }
      ]
    };
  },
  mounted() {
    this.$store.dispatch("dashboard/fetchDashBoardData");
  },
  methods:{
    tour (){
      this.$tours["painelTour"].start();
    }
  },
  computed: {
    totalDocsCount() {
      return String(this.$store.state.dashboard.totalDocsCount);
    },
    cmDocsCount() {
      return String(this.$store.state.dashboard.cmDocsCount);
    },
    lmDocsCount() {
      return String(this.$store.state.dashboard.lmDocsCount);
    },
    cmInProgressDocsCount() {
      return String(this.$store.state.dashboard.cmInProgressDocsCount);
    },
    lmInProgressDocsCount() {
      return String(this.$store.state.dashboard.lmInProgressDocsCount);
    },
    cmSignatureCount() {
      return String(this.$store.state.dashboard.cmSignatureCount);
    },
    lmSignatureCount() {
      return String(this.$store.state.dashboard.lmSignatureCount);
    },
    cmInProgressSinatureCount() {
      return String(this.$store.state.dashboard.cmInProgressSignatureCount);
    },
    lmInProgressSignatureCount() {
      return String(this.$store.state.dashboard.lmInProgressSignatureCount);
    },
    finishedDocDelta() {
      if (this.lmDocsCount > 0) {
        const variation = (this.cmDocsCount / this.lmDocsCount - 1) * 100;
        return Math.round(variation * 100) / 100;
      } else {
        return 0;
      }
    },
    inProgressDocDelta() {
      if (this.lmInProgressDocsCount > 0) {
        const variation = (this.cmInProgressDocsCount / this.lmInProgressDocsCount - 1) * 100;
        return Math.round(variation * 100) / 100;
      } else {
        return 0;
      }
    },
    signatureDelta() {
      if (this.lmSignatureCount > 0) {
        const variation = (this.cmSignatureCount / this.lmSignatureCount - 1) * 100;
        return Math.round(variation * 100) / 100;
      } else {
        return 0;
      }
    },
    inProgressSignatureDelta() {
      if (this.lmInProgressSignatureCount > 0) {
        const variation = (this.cmInProgressSinatureCount / this.lmInProgressSignatureCount - 1) * 100;
        return Math.round(variation * 100) / 100;
      } else {
        return 0;
      }
    }
  }
};
</script>
<style></style>
