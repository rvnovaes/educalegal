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
        :class-name="column.ots"
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
          ots: "nome-entrevista"
        },
        {
          prop: "description",
          label: "Descrição",
          minWidth: 220,
          sortable: false,
          ots: "descricao-entrevista"
        },
        {
          prop: "version",
          label: "Versão",
          minWidth: 80,
          sortable: false,
          ots: "versao-entrevista"
        },
        {
          prop: "date_available",
          label: "Disponibilização",
          minWidth: 100,
          sortable: false,
          ots: "disponibilizacao-entrevista"
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
      this.editRow(row);
    },
    async editRow(row) {
      console.log(row);
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
      catch (error){
        await Swal.fire({
          title: error.response.data['message'],
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          buttonsStyling: false
        });
      }
    },
  }
};
</script>
