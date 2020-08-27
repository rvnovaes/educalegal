<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Default</h6>
          <nav aria-label="breadcrumb" class="d-none d-md-inline-block ml-md-4">
            <route-breadcrumb></route-breadcrumb>
          </nav>
        </div>
        <div class="col-lg-6 col-5 text-right">
          <base-button size="sm" type="neutral">New</base-button>
          <base-button size="sm" type="neutral">Filters</base-button>
        </div>
      </div>
      <!-- Card stats -->
      <div class="row">
        <div class="col-xl-3 col-md-6">
          <stats-card title="Documentos gerados"
                      type="gradient-red"
                      sub-title="350"
                      icon="fa fa-file">

            <template slot="footer">
              <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> 3.48%</span>
              <span class="text-nowrap">Em relação ao mês passado</span>
            </template>
          </stats-card>
        </div>
        <div class="col-xl-3 col-md-6">
          <stats-card title="Assinaturas Eletrônicas"
                      type="gradient-orange"
                      sub-title="25"
                      icon="fa fa-signature">

            <template slot="footer">
              <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> 12.18%</span>
              <span class="text-nowrap">Em relação ao mês passado</span>
            </template>
          </stats-card>
        </div>
        <div class="col-xl-3 col-md-6">
          <stats-card title="Chamados"
                      type="gradient-green"
                      sub-title="5"
                      icon="fa fa-user-tie">

            <template slot="footer">
              <span class="text-danger mr-2"><i class="fa fa-arrow-down"></i> 5.72%</span>
              <span class="text-nowrap">Em relação ao mês passado</span>
            </template>
          </stats-card>

        </div>
        <div class="col-xl-3 col-md-6">
          <stats-card title="Escolas"
                      type="gradient-info"
                      sub-title="49,65%"
                      icon="ni ni-hat-3">

            <template slot="footer">
              <span class="text-success mr-2"><i class="fa fa-arrow-up"></i> 54.8%</span>
              <span class="text-nowrap">Em relação ao mês passado</span>
            </template>
          </stats-card>
        </div>
      </div>
    </base-header>
    <card type="frame">
      This is some text within a card body.
    </card>
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
    data() {
      return {}
    },
    methods: {
    },
    created() {
      this.$store.dispatch("interviews/fetchAllInterviews");
      this.$store.dispatch("schools/fetchAllSchools");
      this.$store.dispatch("documents/fetchPaginatedDocuments", {
        offset: 0,
        statusFilter: [],
        schoolFilter: [],
        interviewFilter: [],
        orderByCreatedDate: "descending",
        createdDateRange: null,
      });
    },
    mounted() {
    }
  };
</script>
<style></style>
