<template>
  <div class="card">

    <div class="border-0 card-header">
      <h3 class="mb-0">Representantes</h3>
      <div class="col-lg-12 col-5 text-right">
        <base-button size="md" type="success" @click="handleNew" class="botao-nova-escola">
          <i class="fa fa-plus-circle"></i> Novo Representante
        </base-button>
      </div>
    </div>
    <el-table class="table-responsive table-flush"
              header-row-class-name="thead-light"
              :data="representatives">
      <el-table-column
        v-for="column in tableColumns"
        :key="column.label"
        :class-name="column.tour"
        v-bind="column"></el-table-column>
      <el-table-column min-width="100px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleEdit($index, row)"
            class="edit botao-editar-representante"
            type="primary"
            size="sm"
            icon>
            <i class="text-white fa fa-edit"></i>
          </base-button>
          <base-button
            @click.native="handleDelete($index, row)"
            class="remove btn-link botao-apagar-representante"
            type="danger"
            size="sm"
            icon>
            <i class="text-white fa fa-trash"></i>
          </base-button>
        </div>
      </el-table-column>
    </el-table>
    <representante-form v-if="currentRepresentative" :representative="currentRepresentative" @closeRepresentativeForm="currentRepresentative = null"></representante-form>
  </div>
</template>
<script>
import Swal from "sweetalert2";
import RepresentanteForm from "@/components/pages/forms/RepresentanteForm";
import {Table, TableColumn} from "element-ui";

export default {
  name: "representantes-table",
  props: ["school"],
  components: {
    RepresentanteForm,
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
          tour: "representante-nome"
        },
        {
          prop: "email",
          label: "E-mail",
          minWidth: 220,
          sortable: true,
          tour: "representante-email"
        },
        {
          prop: "cpf",
          label: "CPF",
          minWidth: 220,
          sortable: true,
          tour: "representante-cpf"
        },
        {
          prop: "kind",
          label: "Tipo",
          minWidth: 220,
          sortable: true,
          tour: "representante-kind"
        },
      ],
      currentRepresentative: null
    };
  },
  computed: {
    representatives() {
      return this.$store.getters["schools/getRepresentatives"](this.school.id)
    },
  },
  methods: {
    handleNew() {
      let newRepresentative = {
        id: 0,
        tenant: this.school.tenant,
        school: this.school.id,
        name: null,
        email: null,
        kind: null,
        cpf: null
      }
      // insere o representante vazio no store dentro da lista da escola
      this.$store.commit("schools/addRepresentative", {schoolId: this.school.id, newRepresentative: newRepresentative})
      // altera a currentRepresentative para o representante vazio que acabou de ser adicionada para abrir o form vazio de representante
      this.currentRepresentative = this.$store.state.schools.schools.find(school => school.id === Number(this.school.id)).representatives.find(representative => representative.id === 0)
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
            const res = await this.$store.dispatch("schools/deleteRepresentative", row);
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
      this.currentRepresentative = this.$store.getters["schools/getRepresentative"](this.school.id, indexToEdit)
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    }
  }
};
</script>
