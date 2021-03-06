<template>
  <div class="card">
    <div class="border-0 card-header">
      <div class="col-lg-12 col-5 text-right">
        <base-input input-classes="busca-modelos"
                    v-model="searchQuery"
                    prepend-icon="fas fa-search"
                    placeholder="Pesquise por qualquer termo...">
        </base-input>

      </div>
    </div>

    <el-table class="table-responsive table-flush"
              header-row-class-name="thead-light"
              :data="queriedData">
      <el-table-column
        v-for="column in tableColumns"
        :key="column.label"
        :class-name="column.tour"
        v-bind="column"></el-table-column>
      <el-table-column min-width="100px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleNew($index, row)"
            class="edit"
            type="success"
            size="sm"
            icon
          >
            <i class="text-white fa fa-plus-circle"></i> Criar
          </base-button>
          <!--          <base-button-->
        </div>
      </el-table-column>
    </el-table>
  </div>
</template>
<script>
import {Table, TableColumn} from "element-ui";
import interviewSearchMixin from "@/components/tables/PaginatedTables/interviewSearchMixin";
import Swal from "sweetalert2";


export default {
  name: "entrevistas-table",
  mixins: [interviewSearchMixin],
  components: {
    [Table.name]: Table,
    [TableColumn.name]: TableColumn,
  },
  data() {
    return {
      propsToSearch: ["name", "description"],
      tableColumns: [
        {
          prop: "name",
          label: "Nome",
          minWidth: 240,
          sortable: false,
          tour: "nome-entrevista"
        },
        {
          prop: "description",
          label: "Descrição",
          minWidth: 220,
          sortable: false,
          tour: "descricao-entrevista"
        },
        {
          prop: "version",
          label: "Versão",
          minWidth: 80,
          sortable: false,
          tour: "versao-entrevista"
        },
        {
          prop: "date_available",
          label: "Disponibilização",
          minWidth: 100,
          sortable: false,
          tour: "disponibilizacao-entrevista"
        }
      ],
    };
  },

  created() {
      this.$store.dispatch("interviews/fetchAllInterviews");
  },

  computed: {
    tableData() {
      return this.$store.state.interviews.interviews;
    }
  },
  methods: {
    handleNew(index, row) {
      this.reachedDocumentLimit().then((reachedLimit) => {
        if (!reachedLimit) {
          this.editRow(row);
        }
      });
    },
    reachedDocumentLimit: async function () {
      try {
        const res = await this.$axios.get("/v2/create_documents/documents_limit");
        if (res.status === 200) {
          const reachedLimit = res.data.reached_limit;
          if (reachedLimit) {
            await Swal.fire({
              title: "Faça um upgrade do seu plano!",
              html: "Foi atingido o limite mensal de geração de 10 documentos para o plano contratado.<br/><br/>" +
                "Entre em contato conosco e faça um upgrade de seu plano.",
              icon: "info",
              showCloseButton: true,
              confirmButtonText: 'Entrar em contato',
              customClass: {
                confirmButton: "btn btn-info",
              },
              buttonsStyling: false,
            }).then(function () {
              window.open('https://www.educalegal.com.br/contato/', '_blank');
            })
          }
          return reachedLimit;
        }
      } catch (e) {
        await Swal.fire({
          title: "Erro ao obter o limite de documentos",
          text: e,
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          showCloseButton: true,
          buttonsStyling: false
        });
        return true;
      }
    },
    async editRow(row) {
      const urlParams = new URLSearchParams(row.interview_link);
      const payload = {
        name: "---",
        status: "rascunho",
        description: "Documento em elaboração...",
        tenant: urlParams.get("tid"),
        interview: urlParams.get("intid")
      };
      try {
        const res = await this.$axios.post("/v2/documents/", payload);
        console.log(res);
        if (res.status === 201) {
          const doc_uuid = res.data.doc_uuid;
          const destination_link = row.interview_link  + "&doc_uuid=" + doc_uuid;
          let win = window.open(destination_link, "_blank");
          win.focus();
        }
      }
      catch (e){
        let errorMessage = ''
        if (e.response.data){
          errorMessage = e.response.data
        }
        else {
          errorMessage = e.toString()
        }
        await Swal.fire({
          title: 'Erro ao gerar o documento',
          text: errorMessage,
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          showCloseButton: true,
          buttonsStyling: false
        });
      }
    },
  }
};
</script>
