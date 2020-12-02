<template>
  <card v-if="">
    <!-- Card header -->
    <h3 v-if="signatory.name" slot="header" class="mb-0">Editar {{ signatory.name }}</h3>
    <h3 v-else slot="header" class="mb-0">Signatários são usados nas assinaturas físicas e eletrônicas.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-4">
<!--            para passar um booleano no vuejs deve ser usada a diretiva v-bind, senao ele entende como string-->
<!--            https://stackoverflow.com/questions/50955095/vee-validate-regex-not-working  e necessario usar /  e / para delimitar a regex-->
            <base-input label="Nome"
                        name="Nome"
                        class="signatory-nome"
                        placeholder="Nome"
                        success-message="Parece correto!"
                        v-bind:required="true"
                        rules="regex:^['A-zÀ-ÿ-]+(?:\s['A-zÀ-ÿ-]+)+$"
                        :value="signatory.name"
                        @input="updateSignatoryName">
            </base-input>
          </div>
          <div class="col-md-4">
            <base-input label="E-mail"
                        name="E-mail"
                        class="signatory-email"
                        placeholder="E-mail"
                        rules="required"
                        type="email"
                        :value="signatory.email"
                        @input="updateSignatoryEmail">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CPF"
                        name="CPF"
                        class="signatory-cpf"
                        placeholder="CPF"
                        rules="required"
                        v-mask="'###.###.###-##'"
                        success-message="Parece correto!"
                        :value="signatory.cpf"
                        @input="updateSignatoryCPF">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="Tipo"
                        name="Tipo"
                        class="signatory-tipo"
                        placeholder="Tipo "
                        rules="required"
                        success-message="Parece correto!">
              <el-select class="select-danger"
                         placeholder="Tipo"
                         :value="signatory.kind"
                         @input="updateSignatoryKind">
                <el-option v-for="option in selects.kinds"
                           class="select-danger"
                           :value="option.value"
                           :label="option.label"
                           :key="option.label">
                </el-option>
              </el-select>
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
import { signatoryKind } from "@/components/pages/forms/enum";
import { isCPF } from 'brazilian-values';
import {mask} from 'vue-the-mask';

export default {
  props: ["signatory"],
  components: {},
  directives: {mask},
  data() {
    return {
      selects: {
        kinds: signatoryKind
      },
    };
  },
  methods: {
    // signatory.school e apenas a pk da escola
    updateSignatoryName(e) {
      this.$store.commit("schools/updateSignatoryName", {
        schoolId: this.signatory.school,
        signatoryId: this.signatory.id,
        name: e
      });
    },
    updateSignatoryEmail(e) {
      this.$store.commit("schools/updateSignatoryEmail", {
        schoolId: this.signatory.school,
        signatoryId: this.signatory.id,
        email: e
      });
    },
    updateSignatoryCPF(e) {
      this.$store.commit("schools/updateSignatoryCPF", {
        schoolId: this.signatory.school,
        signatoryId: this.signatory.id,
        cpf: e
      });
    },
    updateSignatoryKind(e) {
      this.$store.commit("schools/updateSignatoryKind", {
        schoolId: this.signatory.school,
        signatoryId: this.signatory.id,
        kind: e
      });
    },
    async firstFormSubmit() {
      if (!isCPF(this.signatory.cpf)) {
        await Swal.fire({
          title: `CPF ${this.signatory.cpf} inválido.`,
          text: 'Deve ser corrigido o CPF do signatário.',
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
      if (this.signatory.id !== 0) {
        try {
          const res = await this.$store.dispatch("schools/updateSignatory", this.signatory);
          if (res.status === 200) {
            this.close();
            await Swal.fire({
              title: `Você atualizou ${this.signatory.name} com sucesso!`,
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
            title: `Erro ao editar ${this.signatory.name}`,
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
          const res = await this.$store.dispatch("schools/createSignatory", this.signatory);
          if (res.status === 201) {
            this.close();
            await Swal.fire({
              title: `Você criou ${this.signatory.name} com sucesso!`,
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
            title: `Erro ao criar ${this.signatory.name}`,
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
      // Limpa dados do signatário vazio (id=0) se os campos nao forem preenchidos
      if (this.signatory.name === null || this.signatory.email === null || this.signatory.cpf === null) {
        this.$store.commit("schools/deleteSignatory", {school: this.signatory.school, id: 0});
      }
      this.$emit("closeSignatoryForm");
    }
  }
};
</script>
<style>
</style>
