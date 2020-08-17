<template>
  <div class="content">
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Escolas</h6>
          <nav aria-label="breadcrumb" class="d-none d-md-inline-block ml-md-4">
            <route-bread-crumb></route-bread-crumb>
          </nav>
        </div>
        <div class="col-lg-6 col-5 text-right">
          <base-button size="sm" type="neutral">New</base-button>
          <base-button size="sm" type="neutral">Filters</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div>
        <card class="no-border-card" body-classes="px-0 pb-1" footer-classes="pb-2">
          <template slot="header">
            <h3 class="mb-0">Escolas</h3>
            <p class="text-sm mb-0">
              Os dados das escolas são usados para a geração dos contratos e documentos.
            </p>
          </template>
          <div>
            <div class="col-12 d-flex justify-content-center justify-content-sm-between flex-wrap"
            >
              <el-select
                class="select-primary pagination-select"
                v-model="pagination.perPage"
                placeholder="Per page"
              >
                <el-option
                  class="select-primary"
                  v-for="item in pagination.perPageOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                >
                </el-option>
              </el-select>

              <div>
                <base-input v-model="searchQuery"
                            prepend-icon="fas fa-search"
                            placeholder="Buscar...">
                </base-input>
              </div>
            </div>
            <el-table :data="queriedData"
                      row-key="id"
                      header-row-class-name="thead-light"
                      @sort-change="sortChange"
                      @selection-change="selectionChange">
              <el-table-column
                v-for="column in tableColumns"
                :key="column.label"
                v-bind="column"
              >
              </el-table-column>
              <el-table-column min-width="180px" align="right" label="Actions">
                <div slot-scope="{$index, row}" class="d-flex">
                  <base-button
                    @click.native="handleLike($index, row)"
                    class="like btn-link"
                    type="info"
                    size="sm"
                    icon
                  >
                    <i class="text-white ni ni-like-2"></i>
                  </base-button>
                  <base-button
                    @click.native="handleEdit($index, row)"
                    class="edit"
                    type="warning"
                    size="sm"
                    icon
                  >
                    <i class="text-white ni ni-ruler-pencil"></i>
                  </base-button>
                  <base-button
                    @click.native="handleDelete($index, row)"
                    class="remove btn-link"
                    type="danger"
                    size="sm"
                    icon
                  >
                    <i class="text-white ni ni-fat-remove"></i>
                  </base-button>
                </div>
              </el-table-column>
            </el-table>
          </div>
          <div
            slot="footer"
            class="col-12 d-flex justify-content-center justify-content-sm-between flex-wrap"
          >
            <div class="">
              <p class="card-category">
                Showing {{ from + 1 }} to {{ to }} of {{ total }} entries

                <span v-if="selectedRows.length">
                  &nbsp; &nbsp; {{ selectedRows.length }} rows selected
                </span>
              </p>

            </div>
            <base-pagination
              class="pagination-no-border"
              v-model="pagination.currentPage"
              :per-page="pagination.perPage"
              :total="total"
            >
            </base-pagination>
          </div>
        </card>
      </div>
    </div>
  </div>
</template>
<script>
import {Table, TableColumn, Select, Option} from "element-ui";
import RouteBreadCrumb from "@/components/argon-core/Breadcrumb/RouteBreadcrumb";
import {BasePagination} from "@/components/argon-core";
import clientPaginationMixin from "@/components/tables/PaginatedTables/clientPaginationMixin";
import Swal from "sweetalert2";
// import allSchools from "@/queries/allSchools.graphql";
// import deleteSchool from "@/queries/deleteSchool.graphql";

export default {
  mixins: [clientPaginationMixin],
  layout: "DashboardLayout",
  components: {
    BasePagination,
    RouteBreadCrumb,
    [Select.name]: Select,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
  },
  data() {
    return {
      propsToSearch: ["name", "legal_name", "city", "state"],
      tableColumns: [
        {
          type: "selection"
        },
        {
          prop: "name",
          label: "Nome",
          minWidth: 160,
          sortable: true
        },
        {
          prop: "legal_name",
          label: "Razão Social",
          minWidth: 220,
          sortable: true
        },
        {
          prop: "city",
          label: "Cidade",
          minWidth: 135,
          sortable: true
        },
        {
          prop: "state",
          label: "Estado",
          minWidth: 100,
          sortable: true
        },
      ],
      tableData: [],
      selectedRows: []
    };
  },
  methods: {
    handleLike(index, row) {
      Swal.fire({
        title: `Você marcou ${row.name} como favorita`,
        buttonsStyling: false,
        icon: "success",
        customClass: {
          confirmButton: "btn btn-success btn-fill",
        },
      });
    },
    handleEdit(index, row) {
      this.editRow(row);
    },
    handleDelete(index, row) {
      Swal.fire({
        title: `Tem certeza que quer excluir ${row.name}?`,
        text: `Não é possível desfazer essa ação!`,
        icon: "warning",
        showCancelButton: true,
        customClass: {
          confirmButton: "btn btn-success btn-fill",
          cancelButton: "btn btn-danger btn-fill"
        },
        confirmButtonText: "Sim, excluir!",
        cancelButtonText: "Cancelar",
        buttonsStyling: false
      }).then(result => {
        if (result.value) {
          this.deleteRow(row);
          Swal.fire({
            title: "Excluída!",
            text: `Você excluiu ${row.name}`,
            icon: "success",
            customClass: {
              confirmButton: "btn btn-success btn-fill",
            },
            buttonsStyling: false
          });
        }
      });
    },
    editRow(row) {
      let indexToEdit = row.id;
      this.$router.push({
        path: "/escolas/" + indexToEdit
      });
    },
    async deleteRow(row) {
      let indexToDelete = this.tableData.findIndex(
        tableRow => tableRow.id === row.id
      );
      if (indexToDelete >= 0) {
        // try {
        //   const result = await this.$apollo.mutate({
        //     mutation: deleteSchool,
        //     variables: {
        //       id: row.id
        //     }
        //   }).then((data) => {
        //     console.log(data);
        //     this.tableData.splice(indexToDelete, 1);
        //   });
        // } catch (e) {
        //   await Swal.fire({
        //     title: `Erro ao excluir ${row.name}`,
        //     text: e,
        //     icon: 'error',
        //     customClass: {
        //       confirmButton: 'btn btn-info btn-fill',
        //     },
        //     confirmButtonText: 'OK',
        //     buttonsStyling: false
        //   });
        //
        // }
      }
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    },
  },
  async asyncData({ $axios }){
    return $axios.$get('http://localhost:8001/v2/tenant/schools').then((response) => {
      console.log(response)
      return {tableData: response.results}
    })
  }
};
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}
</style>
