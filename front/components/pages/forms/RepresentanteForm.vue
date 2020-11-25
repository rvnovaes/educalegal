<template>
  <card v-if="">
    <!-- Card header -->
    <h3 v-if="representative.name" slot="header" class="mb-0">Editar {{ representative.name }}</h3>
    <h3 v-else slot="header" class="mb-0">Representantes são usados nas assinaturas físicas e eletrônicas.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-5">
<!--            para passar um booleano no vuejs deve ser usada a diretiva v-bind, senao ele entende como string-->
<!--            https://stackoverflow.com/questions/50955095/vee-validate-regex-not-working  e necessario usar /  e / para delimitar a regex-->
            <base-input label="Nome"
                        name="Nome"
                        class="representative-nome"
                        placeholder="Nome"
                        success-message="Parece correto!"
                        v-bind:required="true"
                        rules="regex:^['A-zÀ-ÿ-]+(?:\s['A-zÀ-ÿ-]+)+$"
                        :value="representative.name"
                        @input="updateRepresentativeName">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        class="representative-email"
                        placeholder="E-mail"
                        rules="required"
                        type="email"
                        :value="representative.email"
                        @input="updateRepresentativeEmail">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CPF"
                        name="CPF"
                        class="representative-cpf"
                        placeholder="CPF"
                        rules="required"
                        v-mask="'###.###.###-##'"
                        success-message="Parece correto!"
                        :value="representative.cpf"
                        @input="updateRepresentativeCPF">
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
import { isCPF } from 'brazilian-values';
import {mask} from 'vue-the-mask';

export default {
  props: ["representative"],
  components: {},
  directives: {mask},
  data() {
    return {};
  },
  methods: {
    // representative.school e apenas a pk da escola
    updateRepresentativeName(e) {
      this.$store.commit("schools/updateRepresentativeName", {
        schoolId: this.representative.school,
        representativeId: this.representative.id,
        name: e
      });
    },
    updateRepresentativeEmail(e) {
      this.$store.commit("schools/updateRepresentativeEmail", {
        schoolId: this.representative.school,
        representativeId: this.representative.id,
        email: e
      });
    },
    updateRepresentativeCPF(e) {
      this.$store.commit("schools/updateRepresentativeCPF", {
        schoolId: this.representative.school,
        representativeId: this.representative.id,
        cpf: e
      });
    },
    async firstFormSubmit() {
      if (!isCPF(this.representative.cpf)) {
        await Swal.fire({
          title: `CPF ${this.representative.cpf} inválido.`,
          text: 'Deve ser corrigido o CPF do representante.',
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          showCloseButton: true,
          buttonsStyling: false
        });
        return;
      }
      if (this.representative.id !== 0) {
        try {
          const res = await this.$store.dispatch("schools/updateRepresentative", this.representative);
          if (res.status === 200) {
            this.close();
            await Swal.fire({
              title: `Você atualizou ${this.representative.name} com sucesso!`,
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
            title: `Erro ao editar ${this.representative.name}`,
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
          const res = await this.$store.dispatch("schools/createRepresentative", this.representative);
          if (res.status === 201) {
            this.close();
            await Swal.fire({
              title: `Você criou ${this.representative.name} com sucesso!`,
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
            title: `Erro ao criar ${this.representative.name}`,
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
      // Limpa dados do representante vazio (id=0) se os campos nao forem preenchidos
      if (this.representative.name === null || this.representative.email === null || this.representative.cpf === null) {
        this.$store.commit("schools/deleteRepresentative", {school: this.representative.school, id: 0});
      }
      this.$emit("closeRepresentativeForm");
    }
  }
};
</script>
<style>
</style>
