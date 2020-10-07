<template>
  <card v-if="">
    <!-- Card header -->
    <h3 v-if="witness.name" slot="header" class="mb-0">Editar {{ witness.name }}</h3>
    <h3 v-else slot="header" class="mb-0">Testemunhas são usadas nas assinaturas físicas e eletrônicas.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-5">
<!--            para passa um booleano no vuejs deve ser usada a diretiva v-bind, senao ele entende como string-->
<!--            https://stackoverflow.com/questions/50955095/vee-validate-regex-not-working  e necessario usar /  e / para delimitar a regex-->
            <base-input label="Nome"
                        name="Nome"
                        class="witness-nome"
                        placeholder="Nome"
                        success-message="Parece correto!"
                        v-bind:required="true"
                        rules="regex:^['A-zÀ-ÿ-]+(?:\s['A-zÀ-ÿ-]+)+$"
                        :value="witness.name"
                        @input="updateWitnessName">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        class="escola-email"
                        placeholder="E-mail"
                        rules="required"
                        type="email"
                        :value="witness.email"
                        @input="updateWitnessEmail">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CNPJ/CPF"
                        name="CNPJ/CPF"
                        class="escola-cnpj"
                        placeholder="CNPJ/CPF"
                        rules="required"
                        success-message="Parece correto!"
                        :value="witness.cpf"
                        @input="updateWitnessCPF">

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
import ufs from "@/components/pages/forms/ufs";
import legalNatures from "@/components/pages/forms/legalNatures";

export default {
  props: ["witness"],
  components: {},
  data() {
    return {};
  },
  methods: {
    // witness.school e apenas a pk da escola
    updateWitnessName(e) {
      this.$store.commit("schools/updateWitnessName", {
        schoolId: this.witness.school,
        witnessId: this.witness.id,
        name: e
      });
    },
    updateWitnessEmail(e) {
      this.$store.commit("schools/updateWitnessEmail", {
        schoolId: this.witness.school,
        witnessId: this.witness.id,
        email: e
      });
    },
    updateWitnessCPF(e) {
      this.$store.commit("schools/updateWitnessCPF", {
        schoolId: this.witness.school,
        witnessId: this.witness.id,
        cpf: e
      });
    },
    async firstFormSubmit() {
      if (this.witness.id !== 0) {
        try {
          const res = await this.$store.dispatch("schools/updateWitness", this.witness);
          if (res.status === 200) {
            this.close();
            await Swal.fire({
              title: `Você atualizou ${this.witness.name} com sucesso!`,
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
            title: `Erro ao editar ${this.witness.name}`,
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
          const res = await this.$store.dispatch("schools/createWitness", this.witness);
          if (res.status === 201) {
            this.close();
            await Swal.fire({
              title: `Você criou ${this.witness.name} com sucesso!`,
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
            title: `Erro ao criar ${this.witness.name}`,
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
      // Limpa dados da testemunha vazia (id=0) se os campos nao forem preenchidos
      if (this.witness.name === null || this.witness.email === null || this.witness.cpf === null) {
        this.$store.commit("schools/deleteWitness", {school: this.witness.school, id: 0});
      }
      this.$emit("closeWitnessForm");
    }
  }
};
</script>
<style>
</style>
