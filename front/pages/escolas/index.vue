<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Escolas</h6>
          <nav aria-label="breadcrumb" class="d-none d-md-inline-block ml-md-4">
            <route-bread-crumb></route-bread-crumb>
          </nav>
        </div>
        <div class="col-lg-6 col-5 text-right">
          <base-button size="md" type="warning" @click="handleNew">
            <i class="fa fa-plus-circle"></i> Novo</base-button>

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
  </div>
</template>
<script>
import EscolasTable from "~/components/tables/RegularTables/EscolasTable";
import {Table, TableColumn, Option} from "element-ui";
import RouteBreadCrumb from "@/components/argon-core/Breadcrumb/RouteBreadcrumb";

export default {
  layout: "DashboardLayout",
  components: {
    EscolasTable,
    RouteBreadCrumb,
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
