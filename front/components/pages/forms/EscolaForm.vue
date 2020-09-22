<template>
  <card v-if="school">
    <!-- Card header -->
    <h3 v-if="school.name" slot="header" class="mb-0">Editar {{ school.name }}</h3>
    <h3 v-else slot="header" class="mb-0">Preencha corretamente todos os campos. Os dados serão usados nos contratos e documentos.</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-4">
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
            <base-input label="CNPJ/CPF"
                        name="CNPJ/CPF"
                        class="escola-cnpj"
                        placeholder="CNPJ/CPF"
                        rules="required"
                        success-message="Parece correto!"
                        :value="school.cnpj"
                        @input="updateCNPJ">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Tipo"
                        name="Tipo"
                        class="escola-tipo"
                        placeholder="Tipo "
                        rules="required"
                        success-message="Parece correto!">
              <el-select class="select-danger"
                         placeholder="Tipo"
                         :value="school.legal_nature"
                         @input="updateLegalNature">
                <el-option v-for="option in selects.legal_natures"
                           class="select-danger"
                           :value="option.value"
                           :label="option.label"
                           :key="option.label">
                </el-option>
              </el-select>
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
                        placeholder="Site"
                        rules="required"
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
        <base-button @click="back()" type="warning"><i class="ni ni-bold-left voltar"></i>Voltar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
import Swal from "sweetalert2";
import ufs from "@/components/pages/forms/ufs";
import legalNatures from "@/components/pages/forms/legalNatures";

export default {
  props: ["school"],
  components: {},
  data() {
    return {
      selects: {
        legal_natures: legalNatures,
        ufs: ufs
      },
      validated: false,
    };
  },
  // Se o id da escola for 0, cria escola vazia no store
  created() {
    if (this.school.id === 0){
      this.$store.commit("schools/addSchool", this.school)
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
    updateLegalNature(e) {
        this.$store.commit("schools/updateLegalNature", {id: this.school.id, legal_nature: e});
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

      let payload = this.$store.getters["schools/getSchool"](this.school.id)
      console.log(payload)
      if (payload.id) {
        try {
          this.$axios.patch(`v2/schools/${this.school.id}`, payload)
            .then((data) => {
              Swal.fire({
                title: `Você atualizou ${this.school.name} com sucesso!`,
                buttonsStyling: false,
                icon: "success",
                customClass: {
                  confirmButton: "btn btn-success btn-fill",
                }
              });
              this.back();
            });
        } catch (e) {
          await Swal.fire({
            title: `Erro ao editar ${this.school.name}`,
            text: e,
            icon: "error",
            customClass: {
              confirmButton: "btn btn-info btn-fill",
            },
            confirmButtonText: "OK",
            buttonsStyling: false
          });
        }
      } else
        try {
          await this.$store.dispatch("schools/createSchool", payload)
            .then((data) => {
              Swal.fire({
                title: `Você criou ${this.school.name} com sucesso!`,
                buttonsStyling: false,
                icon: "success",
                customClass: {
                  confirmButton: "btn btn-success btn-fill",
                }
              });
              this.back();
            });
        } catch (e) {
          await Swal.fire({
            title: `Erro ao criar ${this.school.name}`,
            text: e,
            icon: "error",
            customClass: {
              confirmButton: "btn btn-info btn-fill",
            },
            confirmButtonText: "OK",
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
