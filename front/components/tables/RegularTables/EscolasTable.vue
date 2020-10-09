<template>
  <div class="card">
    <div class="border-0 card-header">
      <div class="col-lg-12 col-5 text-right">
        <base-button size="md" type="success" @click="handleNew" class="botao-nova-escola">
          <i class="fa fa-plus-circle"></i> Nova Escola
        </base-button>
      </div>
    </div>
<!-- https://stackoverflow.com/questions/47862591/vuejs-error-the-client-side-rendered-virtual-dom-tree-is-not-matching-server-re-->
<!--    https://medium.com/@liutingchun_95744/nuxt-js-best-practices-for-client-side-only-contents-client-only-no-ssr-4843e94d9565-->
    <client-only>
    <el-table class="table-responsive table-flush"
              header-row-class-name="thead-light"
              :data="schools">
      <el-table-column
        v-for="column in tableColumns"
        :key="column.label"
        :class-name="column.tour"
        v-bind="column"></el-table-column>
      <el-table-column min-width="100px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleEdit($index, row)"
            class="edit botao-editar-escola"
            type="primary"
            size="sm"
            icon
          >
            <i class="text-white fa fa-edit"></i>
          </base-button>
          <base-button
            @click.native="handleDelete($index, row)"
            class="remove btn-link botao-apagar-escola"
            type="danger"
            size="sm"
            icon
          >
            <i class="text-white fa fa-trash"></i>
          </base-button>
        </div>
      </el-table-column>
    </el-table>
    </client-only>
  </div>
</template>
<script>
import Swal from "sweetalert2";
import {Table, TableColumn} from "element-ui";

export default {
  name: "escolas-table",
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
          sortable: true,
          tour: "escola-nome"
        },
        {
          prop: "phone",
          label: "Telefone",
          minWidth: 100,
          sortable: true,
          tour: "escola-telefone"
        },
        {
          prop: "email",
          label: "E-mail",
          minWidth: 220,
          sortable: true,
          tour: "escola-email"
        },
        {
          prop: "site",
          label: "Site",
          minWidth: 220,
          sortable: true,
          tour: "escola-site"
        },
        {
          prop: "city",
          label: "Cidade",
          minWidth: 120,
          sortable: true,
          tour: "escola-cidade"
        },
        {
          prop: "state",
          label: "UF",
          minWidth: 60,
          sortable: true,
          tour: "escola-estado"
        },
      ],
      currentPage: 1
    };
  },
  created() {
    this.$store.dispatch("schools/fetchAllSchools");
  },
  computed: {
    // Nao dexa exibir na lista escola vazia, que e usada apenas para a criacao de novas escolas
    schools() {
      return this.$store.state.schools.schools.filter(school => school.id !== 0);
    },
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
    async handleDelete(index, row) {
      const result = await Swal.fire({
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
      });
      console.log(result.value)
      if (result.value) {
        console.log(result.value)
        try {
            const res = await this.$store.dispatch("schools/deleteSchool", row);
            if (res.status === 204) {
              await Swal.fire({
                title: "Excluída!",
                text: `Você excluiu ${row.name}`,
                icon: "success",
                customClass: {
                  confirmButton: "btn btn-success btn-fill",
                },
                showCloseButton: true,
                buttonsStyling: false
              });
            }
            if (res.status === 200) {
              await Swal.fire({
                title: `Não é permitido excluir ${row.name}!`,
                text: res.data,
                icon: "warning",
                customClass: {
                  confirmButton: "btn btn-success btn-fill",
                },
                showCloseButton: true,
                buttonsStyling: false
              });
            }
        } catch (e) {
          await Swal.fire({
            title: `Erro ao excluir ${row.name}`,
            text: e,
            icon: "error",
            customClass: {
              confirmButton: "btn btn-info btn-fill",
            },
            confirmButtonText: "OK",
            showCloseButton: true,
            buttonsStyling: false
          });
        }
      }
    },
    editRow(row) {
      let indexToEdit = row.id;
      this.$router.push({
        path: "/escolas/" + indexToEdit
      });
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    }
  }
};
</script>
