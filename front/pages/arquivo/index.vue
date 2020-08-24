<template>
  <div class="content">
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">Arquivo</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Documentos já gerados por sua escola
          </p>
        </div>
        <!--        <div class="col-lg-6 col-5 text-right">-->
        <!--          <base-button size="sm" type="neutral">New</base-button>-->
        <!--          <base-button size="sm" type="neutral">Filters</base-button>-->
        <!--        </div>-->
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div>
        <card class="no-border-card" body-classes="px-0 pb-1" footer-classes="pb-2">
          <div>
            <div class="filters col-12 d-flex justify-content-center justify-content-sm-between flex-wrap"
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
                <el-select multiple
                           class="select-primary"
                           placeholder="Escola"
                           v-model="selectedSchools">
                  <el-option
                    class="select-primary"
                    v-for="option in schools"
                    :value="option.value"
                    :label="option.label"
                    :key="option.label">
                  </el-option>
                </el-select>
              </div>


              <div>
                <el-select multiple
                           class="select-primary"
                           placeholder="Status"
                           v-model="selectedStatuses">
                  <el-option
                    class="select-primary"
                    v-for="option in selects.statuses"
                    :value="option.value"
                    :label="option.label"
                    :key="option.label">
                  </el-option>
                </el-select>
              </div>

              <div>
                <base-button @click="applyFilters" type="primary">
                  <i class="fa fa-search"></i> Buscar
                </base-button>
                <base-button @click="cleanFilters" type="danger">
                  <i class="fa fa-trash"></i> Limpar
                </base-button>
              </div>

              <!--              <div>-->

              <!--                <base-input v-model="searchQuery"-->
              <!--                            prepend-icon="fas fa-search"-->
              <!--                            placeholder="Search...">-->
              <!--                </base-input>-->
              <!--              </div>-->
            </div>
            <el-table v-loading="loading"
                      :data="queriedData"
                      row-key="id"
                      header-row-class-name="thead-light"
                      @sort-change="sortChange"
                      @selection-change="selectionChange"
                      style="width: 100%">
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
                Mostrando {{ from + 1 }} a {{ to }} de {{ total }} documentos

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
              @input="updatePagination"
            >
            </base-pagination>
          </div>
        </card>
      </div>
    </div>
  </div
  >
</template>
<script>
import {Table, TableColumn, Select, Option} from "element-ui";
import {BasePagination} from "@/components/argon-core";
import documentPaginationMixin from "~/components/tables/PaginatedTables/documentPaginationMixin";
import Swal from "sweetalert2";
import Fuse from "fuse.js";

export default {
  mixins: [documentPaginationMixin],
  layout: "DashboardLayout",
  components: {
    BasePagination,
    [Select.name]: Select,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
  },
  name: "documents-table",
  data() {
    return {
      propsToSearch: ["name", "interview_name", "school_name", "status"],
      tableColumns: [
        {
          prop: "name",
          label: "Documento",
          minWidth: 140,
          sortable: true
        },
        {
          prop: "interview_name",
          label: "Modelo",
          minWidth: 140,
          sortable: true
        },
        {
          prop: "school_name",
          label: "Escola",
          minWidth: 140,
          sortable: true
        },
        {
          prop: "created_date",
          label: "Criação",
          minWidth: 80,
          sortable: true
        },
        {
          prop: "altered_date",
          label: "Alteração",
          minWidth: 80,
          sortable: true
        },
        {
          prop: "status",
          label: "Status",
          minWidth: 120,
          sortable: true
        },
      ],
      selectedStatuses: null,
      selectedSchools: null,
      selects: {
        statuses: [
          {value: "assinado", label: "assinado"},
          {value: "assinatura recusada/inválida", label: "assinatura recusada/inválida"},
          {value: "completado", label: "completado"},
          {value: "criado", label: "criado"},
          {value: "entregue", label: "entregue"},
          {value: "enviado", label: "enviado"},
          {value: "enviado para assinatura", label: "enviado para assinatura"},
          {value: "enviado por e-mail", label: "enviado por e-mail"},
          {value: "finalizado", label: "finalizado"},
          {value: "inserido no GED", label: "inserido no GED"},
          {value: "inválido", label: "inválido"},
          {value: "rascunho", label: "rascunho"},
          {value: "rascunho - em lote", label: "rascunho - em lote"}
        ],
      },
      // tableData: users,
      selectedRows: [],

    };
  },
  computed: {
    tableData() {
      return this.$store.state.documents.documents;
    },
    schools() {
      return this.$store.state.schools.schools.map(s => ({value: s.id, label: s.name}));
    },
    loading() {
      return this.$store.state.documents.loading;
    }
  },
  created() {
    this.$store.dispatch("schools/fetchAllSchools");
    this.$store.dispatch("documents/fetchPaginatedDocuments", {offset: 0});
    // this.fuseSearch = new Fuse(this.tableData, {
    //   keys: ["name", "school_name", "interview_name", "status"],
    //   threshold: 0.3
    // });
  },
  methods: {
    handleLike(index, row) {
      Swal.fire({
        title: `You liked ${row.name}`,
        buttonsStyling: false,
        type: "success",
        confirmButtonClass: "btn btn-success btn-fill"
      });
    },
    handleEdit(index, row) {
      Swal.fire({
        title: `You want to edit ${row.name}`,
        buttonsStyling: false,
        confirmButtonClass: "btn btn-info btn-fill"
      });
    },
    handleDelete(index, row) {
      Swal.fire({
        title: "Are you sure?",
        text: `You won't be able to revert this!`,
        type: "warning",
        showCancelButton: true,
        confirmButtonClass: "btn btn-success btn-fill",
        cancelButtonClass: "btn btn-danger btn-fill",
        confirmButtonText: "Yes, delete it!",
        buttonsStyling: false
      }).then(result => {
        if (result.value) {
          this.deleteRow(row);
          swal({
            title: "Deleted!",
            text: `You deleted ${row.name}`,
            type: "success",
            confirmButtonClass: "btn btn-success btn-fill",
            buttonsStyling: false
          });
        }
      });
    },
    deleteRow(row) {
      let indexToDelete = this.tableData.findIndex(
        tableRow => tableRow.id === row.id
      );
      if (indexToDelete >= 0) {
        this.tableData.splice(indexToDelete, 1);
      }
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    },
    // Sempre que ocorre um evento  no componente de paginacao base-pagination essa funcao e chamada
    updatePagination(args) {
      console.log("Dispardo evento input no componente de paginacao");
      console.log("Estamos na página: " + args);
      /* demandedDocumens representa quantos docs o componente de tabela precisa conforme o ponto da navegacao. Ou seja,
      se o usuario esta na pagina 2 e escolheu exibir 50 documentos por pagina, precisamos de ter no minimo 100
      documentos ja carregados na aplicacao. Entretanto, somamos 1 à pagina atual para que ele possa carregar  os
      documentos uma página antes de eles serem necessários. No exemplo (usuario na pagina 2 com 50 docs/pagina) o valor
      de demandedDocuments sera (2 + 1) * 50 = 150, o que ira disparar a carga de mais documentos uma pagina antes.
      */
      const demandedDocuments = (this.pagination.currentPage + 1) * this.pagination.perPage;
      console.log("Demanded:" + demandedDocuments);
      const onStore = this.$store.getters["documents/getLoadedDocumentsListCount"];
      console.log("On Store: " + onStore);
      if (demandedDocuments >= onStore) {
        console.log("Precisamos de mais documentos!");
        this.$store.dispatch("documents/fetchPaginatedDocuments", {
          offset: onStore,
          status: this.selectedStatuses,
          school: this.selectedSchools
        });
        // this.fuseSearch = new Fuse(this.tableData, {
        //   keys: ["name", "school_name", "interview_name", "status"],
        //   threshold: 0.3
        // });
      }
    },
    applyFilters() {
      this.$store.commit("documents/cleanDocuments");
      this.$store.dispatch("documents/fetchPaginatedDocuments", {
        offset: 0,
        status: this.selectedStatuses,
        school: this.selectedSchools
      });

    },

    cleanFilters() {
      this.selectedStatuses = null;
      this.selectedSchools = null;
      this.applyFilters();
    }
  },
}
;
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}

.filters {
  margin-bottom: 15px;
}

.el-tag.el-tag--info.el-tag--small.el-tag--light {
  color: #fff;
  background: #5e72e4;
  border-color: #5e72e4;
  box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
}

</style>
