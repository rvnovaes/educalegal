<template>
  <div class="card">
    <div class="border-0 card-header">
      <h3 class="mb-0">Séries</h3>
      <div class="col-lg-12 col-5 text-right">
        <base-button size="md" type="success" @click="handleNew" class="botao-nova-escola">
          <i class="fa fa-plus-circle"></i> Nova Série
        </base-button>
      </div>
    </div>
    <el-table class="table-responsive table-flush"
              header-row-class-name="thead-light"
              :data="grades">
      <el-table-column
        v-for="column in tableColumns"
        :key="column.label"
        :class-name="column.tour"
        v-bind="column"></el-table-column>
      <el-table-column min-width="100px" align="right" label="Ações">
        <div slot-scope="{$index, row}" class="d-flex">
          <base-button
            @click.native="handleEdit($index, row)"
            class="edit botao-editar-serie"
            type="primary"
            size="sm"
            icon>
            <i class="text-white fa fa-edit"></i>
          </base-button>
          <base-button
            @click.native="handleDelete($index, row)"
            class="remove btn-link botao-apagar-serie"
            type="danger"
            size="sm"
            icon>
            <i class="text-white fa fa-trash"></i>
          </base-button>
        </div>
      </el-table-column>
    </el-table>
    <serie-form v-if="currentGrade" :grade="currentGrade" @closeGradeForm="currentGrade = null"></serie-form>
  </div>
</template>
<script>
import Swal from "sweetalert2";
import {Table, TableColumn} from "element-ui";
import SerieForm from "@/components/pages/forms/SerieForm";

export default {
  name: "series-table",
  props: ["school"],
  components: {
    SerieForm,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn,
  },
  data() {
    return {
      tableColumns: [
        {
          prop: "name",
          label: "Nome",
          minWidth: 500,
          sortable: true,
          tour: "serie-nome"
        },
      ],
      currentGrade: null
    };
  },
  computed: {
    grades() {
      return this.$store.getters["schools/getGrades"](this.school.id)
    },
  },
  methods: {
    handleNew() {
      let newGrade = {
        id: 0,
        tenant: this.school.tenant,
        school: this.school.id,
        name: null
      }
      // insere a serie vazia no store dentro da lista da escola
      this.$store.commit("schools/addGrade", {schoolId: this.school.id, newGrade: newGrade})
      // altera a currentGrade para a serie vazia que acabou de ser adicionada para abrir o form vazio de serie
      this.currentGrade = this.$store.state.schools.schools.find(school => school.id === Number(this.school.id)).grades.find(grade => grade.id === 0)
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
            const res = await this.$store.dispatch("schools/deleteGrade", row);
            if (res.status === 204) {
              await Swal.fire({
                title: "Exclusão!",
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
      this.currentGrade = this.$store.getters["schools/getGrade"](this.school.id, indexToEdit)
    },
    selectionChange(selectedRows) {
      this.selectedRows = selectedRows;
    }
  }
};
</script>
