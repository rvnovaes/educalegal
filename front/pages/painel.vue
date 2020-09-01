<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Painel</h6>
          <nav aria-label="breadcrumb" class="d-none d-md-inline-block ml-md-4">
            <route-breadcrumb></route-breadcrumb>
          </nav>
        </div>
<!--        <div class="col-lg-6 col-5 text-right">-->
<!--          <base-button size="sm" type="neutral">New</base-button>-->
<!--          <base-button size="sm" type="neutral">Filters</base-button>-->
<!--        </div>-->
      </div>
      <!-- Card stats -->
      <div class="row">
        <div class="col-xl-3 col-md-6">
          <stats-card title="Documentos gerados"
                      type="gradient-red"
                      :sub-title="currentMonthDocumentCount"
                      icon="fa fa-file">
            <template slot="footer">
              <div v-if="documentDelta >= 0">
                <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> {{ documentDelta }} %</span><span class="text-nowrap">Em relação ao mês passado ({{ lastMonthDocumentCount}})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> {{ documentDelta }} %</span><span class="text-nowrap">Em relação ao mês passado ({{ lastMonthDocumentCount}})</span>
              </div>
            </template>
          </stats-card>
        </div>
        <div class="col-xl-3 col-md-6">
          <stats-card title="Assinaturas Eletrônicas"
                      type="gradient-orange"
                      :sub-title="currentMonthSignatureCount"
                      icon="fa fa-signature">

            <template slot="footer">
              <div v-if="signatureDelta >= 0">
                <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> {{ signatureDelta }} %</span><span class="text-nowrap">Em relação ao mês passado ({{ lastMonthSignatureCount}})</span>
              </div>
              <div v-else>
                <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> {{ signatureDelta }} %</span><span class="text-nowrap">Em relação ao mês passado ({{ lastMonthSignatureCount}})</span>
              </div>
            </template>
          </stats-card>
        </div>
<!--        <div class="col-xl-3 col-md-6">-->
<!--          <stats-card title="Chamados"-->
<!--                      type="gradient-green"-->
<!--                      sub-title="5"-->
<!--                      icon="fa fa-user-tie">-->

<!--            <template slot="footer">-->
<!--              <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> 5.72%</span>-->
<!--              <span class="text-nowrap">Em relação ao mês passado</span>-->
<!--            </template>-->
<!--          </stats-card>-->

<!--        </div>-->
<!--        <div class="col-xl-3 col-md-6">-->
<!--          <stats-card title="Escolas"-->
<!--                      type="gradient-info"-->
<!--                      sub-title="49,65%"-->
<!--                      icon="ni ni-hat-3">-->

<!--            <template slot="footer">-->
<!--              <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> 54.8%</span>-->
<!--              <span class="text-nowrap">Em relação ao mês passado</span>-->
<!--            </template>-->
<!--          </stats-card>-->
<!--        </div>-->
      </div>
    </base-header>
<!--    <card type="frame">-->
<!--      This is some text within a card body.-->
<!--    </card>-->
  </div>

</template>
<script>
  import RouteBreadCrumb from '@/components/argon-core/Breadcrumb/RouteBreadcrumb';
  import StatsCard from '@/components/argon-core/Cards/StatsCard';
  import Card from '@/components/argon-core/Cards/Card'
  export default {
    layout: 'DashboardLayout',
    components: {
      RouteBreadCrumb,
      StatsCard,
      Card
    },
    created() {
      this.$store.dispatch("dashboard/fetchDashBoardData")
    },
    computed:{
      currentMonthDocumentCount () {
        return String(this.$store.state.dashboard.currentMonthDocumentCount)
      },
      lastMonthDocumentCount() {
        return this.$store.state.dashboard.lastMonthDocumentCount
      },
      currentMonthSignatureCount () {
        return String(this.$store.state.dashboard.currentMonthSignatureCount)
      },
      lastMonthSignatureCount() {
        return this.$store.state.dashboard.lastMonthSignatureCount
      },
      documentDelta(){
        const variation = (this.currentMonthDocumentCount / this.lastMonthDocumentCount - 1) * 100
        return Math.round(variation * 100) / 100
      },
      signatureDelta(){
        const variation = (this.currentMonthSignatureCount / this.lastMonthSignatureCount - 1) * 100
        return Math.round(variation * 100) / 100
      }
    }

  };
</script>
<style></style>
