<template>
  <card v-if="school">
    <!-- Card header -->
    <h3 v-if="school.name" slot="header" class="mb-0">Editar {{ school.name }}</h3>
    <h3 v-else slot="header" class="mb-0">Preencha corretamente todos os campos. Os dados serão usados nos contratos e
      documentos.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-5">
            <base-input label="Nome"
                        name="Nome"
                        class="escola-nome"
                        placeholder="Nome"
                        success-message="Parece correto!"
                        rules="required"
                        :value="school.name"
                        @input="updateName">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Razão Social"
                        name="Razão Social"
                        class="escola-razao"
                        placeholder="Razão Social"
                        rules="required"
                        success-message="Parece correto!"
                        :value="school.legal_name"
                        @input="updateLegalName">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CNPJ"
                        name="CNPJ"
                        class="escola-cnpj"
                        placeholder="CNPJ"
                        rules="required"
                        v-mask="'##.###.###/####-##'"
                        success-message="Parece correto!"
                        :value="school.cnpj"
                        @input="updateCNPJ">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-2">
            <base-input label="Telefone"
                        name="Telefone"
                        class="escola-telefone"
                        placeholder="Telefone"
                        rules="required"
                        :value="school.phone"
                        @input="updatePhone">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Site"
                        name="Site"
                        class="escola-site"
                        placeholder="https://www.minha-escola.com.br"
                        type="url"
                        :value="school.site"
                        @input="updateSite">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        class="escola-email"
                        placeholder="E-mail"
                        rules="required"
                        type="email"
                        :value="school.email"
                        @input="updateEmail">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-1">
            <base-input label="Cep"
                        name="Cep"
                        class="escola-cep"
                        placeholder="Cep"
                        rules="required"
                        :value="school.zip"
                        @input="updateZip">
            </base-input>
          </div>

          <div class="col-md-4">
            <base-input label="Logradouro"
                        name="Logradouro"
                        class="escola-logradouro"
                        placeholder="Logradouro"
                        rules="required"
                        :value="school.street"
                        @input="updateStreet">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Número"
                        name="Número"
                        class="escola-numero"
                        placeholder="Número"
                        rules="required"
                        :value="school.street_number"
                        @input="updateStreetNumber">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="Complemento"
                        name="Complemento"
                        class="escola-complemento"
                        placeholder="Complemento"
                        :value="school.unit"
                        @input="updateUnit">
            </base-input>
          </div>
          <div class="col-md-4">
            <base-input label="Bairro"
                        name="Bairro"
                        class="escola-bairro"
                        placeholder="Bairro"
                        rules="required"
                        :value="school.neighborhood"
                        @input="updateNeighborhood">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-6">
            <base-input label="Cidade"
                        name="Cidade"
                        class-escola="cidade"
                        placeholder="Cidade"
                        rules="required"
                        :value="school.city"
                        @input="updateCity">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="UF"
                        name="UF"
                        class="escola-estado"
                        placeholder="UF"
                        rules="required"
                        @input="updateUF">
              <el-select class="select-danger"
                         placeholder="UF"
                         :value="school.state"
                         @input="updateUF">
                <el-option v-for="option in selects.ufs"
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
        <base-button @click="back()" type="warning"><i class="ni ni-bold-left"></i>Voltar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
import Swal from "sweetalert2";
import ufs from "@/components/pages/forms/ufs";
import {isCNPJ} from 'brazilian-values';
import {mask} from 'vue-the-mask';

export default {
  props: ["school"],
  components: {},
  directives: {mask},
  data() {
    return {
      selects: {
        ufs: ufs
      },
      validated: false,
    };
  },
  created() {
    if (this.school.id === 0) {
      // Procura se existe escola vazia no store
      let newSchool = this.$store.state.schools.schools.filter(school => school.id === 0);
      // Se ja houver escola vazia, nao cria outra
      if (newSchool.length === 0) {
        this.$store.commit("schools/addSchool", this.school);
      }
    }
  },
  methods: {
    updateName(e) {
      this.$store.commit("schools/updateName", {id: this.school.id, name: e});
    },
    updateLegalName(e) {
      this.$store.commit("schools/updateLegalName", {id: this.school.id, legal_name: e});
    },
    updateCNPJ(e) {
      this.$store.commit("schools/updateCNPJ", {id: this.school.id, cnpj: e});
    },
    updatePhone(e) {
      this.$store.commit("schools/updatePhone", {id: this.school.id, phone: e});
    },
    updateSite(e) {
      this.$store.commit("schools/updateSite", {id: this.school.id, site: e});
    },
    updateEmail(e) {
      this.$store.commit("schools/updateEmail", {id: this.school.id, email: e});
    },
    updateZip(e) {
      this.$store.commit("schools/updateZip", {id: this.school.id, zip: e});
    },
    updateStreet(e) {
      this.$store.commit("schools/updateStreet", {id: this.school.id, street: e});
    },
    updateStreetNumber(e) {
      this.$store.commit("schools/updateStreetNumber", {id: this.school.id, street_number: e});
    },
    updateUnit(e) {
      this.$store.commit("schools/updateUnit", {id: this.school.id, unit: e});
    },
    updateNeighborhood(e) {
      this.$store.commit("schools/updateNeighborhood", {id: this.school.id, neighborhood: e});
    },
    updateCity(e) {
      this.$store.commit("schools/updateCity", {id: this.school.id, city: e});
    },
    updateUF(e) {
      this.$store.commit("schools/updateUF", {id: this.school.id, state: e});
    },
    async firstFormSubmit() {
      if (!isCNPJ(this.school.cnpj)) {
        await Swal.fire({
          title: `CNPJ ${this.school.cnpj} inválido.`,
          text: 'Deve ser corrigido o CNPJ da esola.',
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
      if (this.school.id !== 0) {
        try {
          const res = await this.$store.dispatch("schools/updateSchool", this.school);
          if (res.status === 200) {
            await Swal.fire({
              title: `Você atualizou ${this.school.name} com sucesso!`,
              buttonsStyling: false,
              icon: "success",
              showCloseButton: true,
              customClass: {
                confirmButton: "btn btn-success btn-fill",
              }
            });
          }
        } catch (e) {
          let errorMessage = e.response.data ? e.response.data : e.toString();
          await Swal.fire({
            title: `Erro ao editar ${this.school.name}`,
            text: errorMessage,
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
          const res = await this.$store.dispatch("schools/createSchool", this.school);
          if (res.status === 201) {
            await Swal.fire({
              title: `Você criou ${this.school.name} com sucesso!`,
              buttonsStyling: false,
              icon: "success",
              showCloseButton: true,
              customClass: {
                confirmButton: "btn btn-success btn-fill",
              }
            });
            // recarrega a escola que foi criada
            await this.$router.push({path: "/escolas/" + res.data.id});
          }
        } catch (e) {
          await Swal.fire({
            title: `Erro ao criar ${this.school.name}`,
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
    back: function () {
      this.$router.push({
        path: "/escolas"
      });
    }
  }
};
</script>
<style>
</style>
