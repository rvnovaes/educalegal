<template>
  <div class="card">
    <div class="border-0 card-header">
      <div class="col-lg-12 col-5 text-right">
          <base-input v-model="searchQuery"
                      label="Pesquisar"
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
        v-bind="column"></el-table-column>
      <el-table-column min-width="100px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleEdit($index, row)"
            class="edit"
            type="success"
            size="sm"
            icon
          >
            <i class="text-white fa fa-plus-circle"></i> Novo Documento
          </base-button>
<!--          <base-button-->
<!--            @click.native="handleDelete($index, row)"-->
<!--            class="remove btn-link"-->
<!--            type="danger"-->
<!--            size="sm"-->
<!--            icon-->
<!--          >-->
<!--            <i class="text-white fa fa-trash"></i>-->
<!--          </base-button>-->
        </div>
      </el-table-column>
    </el-table>
  </div>
</template>
<script>
import Swal from "sweetalert2";
import {Table, TableColumn} from "element-ui";
import interviewSearchMixin from "@/components/tables/PaginatedTables/interviewSearchMixin";
import Fuse from "fuse.js";

export default {
  name: "entrevistas-table",
  mixins: [interviewSearchMixin],
  components: {
    [Table.name]: Table,
    [TableColumn.name]: TableColumn,
  },
  data() {
    return {
      propsToSearch: ['name', 'description'],
      tableColumns: [
        {
          prop: "name",
          label: "Nome",
          minWidth: 240,
          sortable: false
        },
        {
          prop: "description",
          label: "Descrição",
          minWidth: 220,
          sortable: false
        },
        {
          prop: "version",
          label: "Versão",
          minWidth: 80,
          sortable: false
        },
        {
          prop: "date_available",
          label: "Disponibilização",
          minWidth: 100,
          sortable: false
        }
      ],
    };
  },

  created() {
    // Como as entrevistas sao carregadas no VUEX a partir do painel, so e necessario fazer o fetch se a lista de escolas
    // estiver vazia, por exemplo, se for feito um refresh da pagina
    if (this.tableData.length === 0) {
      this.$store.dispatch("interviews/fetchAllInterviews");
    }
  },

  computed: {
    tableData() {
      return this.$store.state.interviews.interviews;
    }
  },
  methods: {
    handleNew() {
      this.$router.push({
        path: "/escolas/criar"
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
    deleteRow(row) {
      try {
        console.log(row);
        this.$store.dispatch("schools/deleteSchool", row);
      } catch (e) {
        Swal.fire({
          title: `Erro ao excluir ${row.name}`,
          text: e,
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          buttonsStyling: false
        });
      }
      // }
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    },
  }
};
</script>
