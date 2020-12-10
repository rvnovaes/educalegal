<template>
  <card v-if="">
    <!-- Card header -->
    <h3 v-if="grade.name" slot="header" class="mb-0">Editar {{ grade.name }}</h3>
    <h3 v-else slot="header" class="mb-0">As séries escolares são usadas no preenchimento do contrato.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-12">
            <base-input label="Nome"
                        name="Nome"
                        class="grade-nome"
                        placeholder="Nome"
                        success-message="Parece correto!"
                        v-bind:required="true"
                        :value="grade.name"
                        @input="updateGradeName">
            </base-input>
          </div>
        </div>
        <base-button type="success" native-type="submit"><i class="fa fa-check salvar-escola"></i>Salvar</base-button>
        <base-button @click="close()" type="warning"><i class="ni ni-bold-left"></i>Fechar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
import Swal from "sweetalert2";

export default {
  props: ["grade"],
  components: {},
  data() {
    return {
    };
  },
  methods: {
    updateGradeName(e) {
      this.$store.commit("schools/updateGradeName", {
        schoolId: this.grade.school,
        gradeId: this.grade.id,
        name: e
      });
    },
    async firstFormSubmit() {
      if (this.grade.id !== 0) {
        try {
          const res = await this.$store.dispatch("schools/updateGrade", this.grade);
          if (res.status === 200) {
            this.close();
            await Swal.fire({
              title: `Você atualizou ${this.grade.name} com sucesso!`,
              buttonsStyling: false,
              icon: "success",
              showCloseButton: true,
              customClass: {
                confirmButton: "btn btn-success btn-fill",
              }
            });
          }
        } catch (e) {
          await Swal.fire({
            title: `Erro ao editar ${this.grade.name}`,
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
      } else
        try {
          const res = await this.$store.dispatch("schools/createGrade", this.grade);
          if (res.status === 201) {
            this.close();
            await Swal.fire({
              title: `Você criou ${this.grade.name} com sucesso!`,
              buttonsStyling: false,
              icon: "success",
              showCloseButton: true,
              customClass: {
                confirmButton: "btn btn-success btn-fill",
              }
            });
          }
        } catch (e) {
          await Swal.fire({
            title: `Erro ao criar ${this.grade.name}`,
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
    },
    close: function () {
      // Limpa dados da serie vazia (id=0) se os campos nao forem preenchidos
      if (this.grade.name === null) {
        this.$store.commit("schools/deleteGrade", {school: this.grade.school, id: 0});
      }
      this.$emit("closeGradeForm");
    }
  }
};
</script>
<style>
</style>
