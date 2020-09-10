<template>
  <div class="content">
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0 arquivo">Arquivo</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Documentos já gerados por sua escola
          </p>
        </div>
        <div v-if="loading" class="col-1">
          <HourGlassSpinner></HourGlassSpinner>
        </div>
        <div v-else class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div>
        <card class="no-border-card" body-classes="px-0 pb-1" footer-classes="pb-2">
          <div>
            <div class="col-12 d-flex  justify-content-sm-between flex-wrap"
            >

              <div class="col2">

                <base-input label="Data de criação"
                            addon-left-icon="ni ni-calendar-grid-58">
                  <flat-pickr slot-scope="{focus, blur}"
                              @on-open="focus"
                              @on-close="blur"
                              :config="{allowInput: true, mode: 'range'}"
                              class="form-control datepicker"
                              v-model="createdDateRange">
                  </flat-pickr>
                </base-input>
              </div>
              <div class="col-4">
                <base-input label="Modelo de Documento">
                  <el-select multiple
                             class="select-primary"
                             placeholder="Modelo"
                             v-model="selectedInterviews">
                    <el-option
                      class="select-primary"
                      v-for="option in interviews"
                      :value="option.value"
                      :label="option.label"
                      :key="option.label">
                    </el-option>
                  </el-select>
                </base-input>
              </div>

              <div class="col-2">
                <base-input label="Escola">
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
                </base-input>

              </div>

              <div class="col-2">
                <base-input label="Status">
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
                </base-input>
              </div>

              <div class="col-2">
                <base-input label="Paginação">
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
                </base-input>
              </div>


            </div>

            <div class="col-12 d-flex justify-content-end  flex-wrap filter-buttons "
            >

              <div id="filter-buttons">
                <base-button @click="applyFilters" type="primary">
                  <i class="fa fa-search"></i> Buscar
                </base-button>
                <base-button @click="cleanFilters" type="warning">
                  <i class="fa fa-sync"></i> Limpar
                </base-button>
              </div>


            </div>
            <el-table :data="paginatedData"
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
              <el-table-column min-width="80px" align="right" label="Detalhes">
                <div slot-scope="{$index, row}" class="d-flex">
                  <!--                  <base-button-->
                  <!--                    @click.native="handleLike($index, row)"-->
                  <!--                    class="like btn-link"-->
                  <!--                    type="info"-->
                  <!--                    size="sm"-->
                  <!--                    icon-->
                  <!--                  >-->
                  <!--                    <i class="text-white ni ni-like-2"></i>-->
                  <!--                  </base-button>-->
                  <base-button
                    @click.native="handleEdit($index, row)"
                    class="edit"
                    type="primary"
                    size="sm"
                    icon
                  >
                    <i class="text-white fa fa-edit"></i>
                  </base-button>
                  <!--                  <base-button-->
                  <!--                    @click.native="handleDelete($index, row)"-->
                  <!--                    class="remove btn-link"-->
                  <!--                    type="danger"-->
                  <!--                    size="sm"-->
                  <!--                    icon-->
                  <!--                  >-->
                  <!--                    <i class="text-white ni ni-fat-remove"></i>-->
                  <!--                  </base-button>-->
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
    <v-tour name="arquivoTour" :steps="steps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import {Table, TableColumn, Select, Option} from "element-ui";
import {BasePagination} from "@/components/argon-core";
import documentPaginationMixin from "~/components/tables/PaginatedTables/documentPaginationMixin";
import Swal from "sweetalert2";
// Set the locale:
// https://github.com/ankurk91/vue-flatpickr-component/issues/49
import flatpickr from "flatpickr";
import {Portuguese} from "flatpickr/dist/l10n/pt";

flatpickr.localize(Portuguese);
flatpickr.setDefaults({
    dateFormat: "d/m/Y"
  }
);
import flatPickr from "vue-flatpickr-component";

import "flatpickr/dist/flatpickr.css";
import HourGlassSpinner from "@/components/widgets/HourGlassSpinner";

export default {
  mixins: [documentPaginationMixin],
  layout: "DashboardLayout",
  components: {
    HourGlassSpinner,
    BasePagination,
    flatPickr,
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
          prop: "created_date",
          label: "Criação",
          minWidth: 100,
          sortable: false
        },
        {
          prop: "name",
          label: "Documento",
          minWidth: 220,
          sortable: false
        },
        {
          prop: "interview_name",
          label: "Modelo",
          minWidth: 240,
          sortable: false
        },
        {
          prop: "school_name",
          label: "Escola",
          minWidth: 140,
          sortable: false
        },
        {
          prop: "status",
          label: "Status",
          minWidth: 120,
          sortable: false
        },
        {
          prop: "altered_date",
          label: "Alteração",
          minWidth: 100,
          sortable: false
        },
      ],
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
      selectedRows: [],
      orderByCreatedDate: "descending",
      createdDateRange: null,
      selectedStatuses: [],
      selectedInterviews: [],
      selectedSchools: [],
      tourOptions: {
        useKeyboardNavigation: true,
        debug: true,
        labels: {
          buttonSkip: "Dispensar",
          buttonPrevious: "Anterior",
          buttonNext: "Próximo",
          buttonStop: "Fim"
        }
      },
      steps: [
        {
          target: ".arquivo",
          header: {
            title: "Arquivo",
          },
          content: `No arquivo você acessa e pesquisa todos os documentos já gerados por sua escola`,
          params: {
            placement: "right",
            enableScrolling: false
          }
        },
        //Aqui tivemos que usar o target como classe, pq so conseguimos passar para a coluna (que e outro componente) a classe
        {
          target: ".nome-entrevista",
          content: `Esse é o nome pelo qual o tipo de documento ou contrato é identificado na plataforma. Sempre use esse nome ao se referir ao documento. A busca procura por palavras no nome.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".descricao-entrevista",
          content: `Aqui você encontra informações úteis sobre quando e como usar o documento. A pesquisa desta página também procura por palavras na descrição. `,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".versao-entrevista",
          content: `Estamos sempre trabalhando em atualizações dos documentos em virtude de novas leis e de melhores práticas jurídicas e de gestão.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".disponibilizacao-entrevista",
          content: `Essa é a data na qual a versão do documento foi disponibilizada para uso na plataforma.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".edit",
          content: `Clique nesse botão para criar o documento.`,
          params: {
            placement: "top",
            highlight: false,
            enableScrolling: false
          }
        },
      ]
    };
  },
  computed: {
    tableData() {
      return this.$store.state.documents.documents;
    },
    schools() {
      return this.$store.state.schools.schools.map(s => ({value: s.id, label: s.name}));
    },
    interviews() {
      return this.$store.state.interviews.interviews.map(interview => ({value: interview.id, label: interview.name}));
    },
    loading() {
      return this.$store.state.documents.loading;
      // return true
    }
  },
  created() {
    // Como as escolas sao carregadas no VUEX a partir do painel, so e necessario fazer o fetch se a lista de escolas
    // estiver vazia, por exemplo, se for feito um refresh da pagina. Esse componete precisa das escolas e das entrevistas
    // para os filtros respectivos. Os primeiros 50 documentos tambem ja sao carregados no painel e aqui apenas em caso
    // de refresh
    if (this.schools.length === 0) {
      this.$store.dispatch("schools/fetchAllSchools");
    }
    if (this.interviews.length === 0) {
      this.$store.dispatch("interviews/fetchAllInterviews");
    }
    if (this.tableData.length === 0) {
      this.$store.dispatch("documents/fetchPaginatedDocuments", {
        offset: 0,
        statusFilter: [],
        schoolFilter: [],
        interviewFilter: [],
        orderByCreatedDate: "descending",
        createdDateRange: null,
      });
    }
    ;
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
      console.log(index);
      console.log(row);
      this.$router.push({
        path: "/arquivo/" + row.doc_uuid
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
          Swal.fire({
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
    sortChange({prop, order}) {
      let orderByCreatedDate = "descending";
      if (prop === "created_date") {
        console.log(prop);
        console.log(order);
        if (order === "ascending") {
          orderByCreatedDate = order;
        }
      }
      this.orderByCreatedDate = orderByCreatedDate;
      this.updatePagination("Modificada ordenacao de data");
      this.$store.dispatch("documents/fetchPaginatedDocuments", {offset: 0, createdDateOrdering: order});
    },
    // Sempre que ocorre um evento  no componente de paginacao base-pagination essa funcao e chamada
    updatePagination(args) {
      // console.log("Disparado evento input no componente de paginacao");
      console.log("Estamos na página: " + args);
      /* demandedDocumens representa quantos docs o componente de tabela precisa conforme o ponto da navegacao. Ou seja,
      se o usuario esta na pagina 2 e escolheu exibir 50 documentos por pagina, precisamos de ter no minimo 100
      documentos ja carregados na aplicacao. Entretanto, somamos 1 à pagina atual para que ele possa carregar  os
      documentos uma página antes de eles serem necessários. No exemplo (usuario na pagina 2 com 50 docs/pagina) o valor
      de demandedDocuments sera (2 + 1) * 50 = 150, o que ira disparar a carga de mais documentos uma pagina antes.
      */
      // let clearDocumentsList = false
      // // console.log("this.selectedStatuses.length")
      // // console.log(this.selectedStatuses.length)
      // // console.log("this.$store.state.documents.statusFilter.length")
      // // console.log(this.$store.state.documents.statusFilter.length)
      // if (this.selectedStatuses.length !== this.$store.state.documents.statusFilter.length){
      //   clearDocumentsList = true
      // }
      // console.log("clearDocumentsList")
      // console.log(clearDocumentsList)
      const demandedDocuments = (this.pagination.currentPage + 1) * this.pagination.perPage;
      // console.log("Demanded:" + demandedDocuments);
      const onStore = this.$store.getters["documents/getLoadedDocumentsListCount"];
      // console.log("On Store: " + onStore);
      if (demandedDocuments >= onStore) {
        console.log("Precisamos de mais documentos!");
        this.$store.dispatch("documents/fetchPaginatedDocuments", {
          offset: onStore,
          statusFilter: this.selectedStatuses,
          schoolFilter: this.selectedSchools,
          interviewFilter: this.selectedInterviews,
          orderByCreatedDate: this.orderByCreatedDate,
          createdDateRange: this.createdDateRange
        });
      }
    },
    async applyFilters() {
      this.$store.commit("documents/cleanDocuments");
      await this.$store.dispatch("documents/fetchPaginatedDocuments", {
        offset: 0,
        statusFilter: this.selectedStatuses,
        schoolFilter: this.selectedSchools,
        interviewFilter: this.selectedInterviews,
        orderByCreatedDate: this.orderByCreatedDate,
        createdDateRange: this.createdDateRange
      });
    },
    cleanFilters() {
      this.createdDateRange = null;
      this.selectedInterviews = [];
      this.selectedStatuses = [];
      this.selectedSchools = [];
      this.createdDateRange = null;
      this.applyFilters();
    },
    tour() {
      this.$tours["arquivoTour"].start();
    }
  },
}
;
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}

#filter-buttons {
  margin-bottom: 30px;
  margin-right: 15px;
}

.el-tag.el-tag--info.el-tag--small.el-tag--light {
  color: #fff;
  background: #5e72e4;
  border-color: #5e72e4;
  box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
}

</style>
