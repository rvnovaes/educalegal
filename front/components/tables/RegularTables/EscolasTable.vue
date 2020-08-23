<template>
  <div class="card">
    <div class="border-0 card-header">
<!--      <h3 class="mb-0">Escolas</h3>-->
    </div>

    <el-table class="table-responsive table-flush"
              header-row-class-name="thead-light"
              :data="schools">
      <el-table-column
        v-for="column in tableColumns"
        :key="column.label"
        v-bind="column"></el-table-column>
      <el-table-column min-width="180px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleEdit($index, row)"
            class="edit"
            type="primary"
            size="sm"
            icon
          >
            <i class="text-white fa fa-edit"></i>
<!--            <i class="text-white ni ni-ruler-pencil"></i>-->
          </base-button>
          <base-button
            @click.native="handleDelete($index, row)"
            class="remove btn-link"
            type="danger"
            size="sm"
            icon
          >
            <i class="text-white fa fa-trash"></i>
          </base-button>
        </div>
      </el-table-column>
    </el-table>
  </div>
</template>
<script>
import Swal from "sweetalert2";
import { Table, TableColumn} from 'element-ui'
export default {
  name: 'escolas-table',
  components: {
    [Table.name]: Table,
    [TableColumn.name]: TableColumn,
  },
  data() {
    return {
      tableColumns: [
        {
          prop: "name",
          label: "Nome",
          minWidth: 140,
          sortable: true
        },
        {
          prop: "phone",
          label: "Telefone",
          minWidth: 100,
          sortable: true
        },
        {
          prop: "email",
          label: "E-mail",
          minWidth: 220,
          sortable: true
        },
        {
          prop: "site",
          label: "Site",
          minWidth: 220,
          sortable: true
        },
        {
          prop: "city",
          label: "Cidade",
          minWidth: 120,
          sortable: true
        },
        {
          prop: "state",
          label: "UF",
          minWidth: 60,
          sortable: true
        },
      ],

      currentPage: 1
    };
  },

  created() {
    this.$store.dispatch("schools/fetchAllSchools");
  },

  computed: {
    schools () {
      return this.$store.state.schools.schools;
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
          console.log(row)
          this.$store.dispatch("schools/deleteSchool", row)
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
}
</script>
