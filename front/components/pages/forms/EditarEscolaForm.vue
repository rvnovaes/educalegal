<template>
  <card v-if="school">
    <!-- Card header -->
    <h3 slot="header" class="mb-0">Editar {{ school.name }}</h3>

    <!-- Card body -->
    <validation-observer v-slot="{handleSubmit}" ref="formValidator">
      <form class="needs-validation"
            @submit.prevent="handleSubmit(firstFormSubmit)">
        <div class="form-row">
          <div class="col-md-4">
            <base-input label="Nome"
                        name="Nome"
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
                        placeholder="CNPJ/CPF"
                        rules="required"
                        success-message="Parece correto!"
                        :value="school.cnpj"
                        @input="updateCNPJ">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Tipo"
                        name="TIpo"
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
                        placeholder="Telefone"
                        rules="required"
                        :value="school.phone"
                        @input="updatePhone">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Site"
                        name="Site"
                        placeholder="Site"
                        rules="required"
                        :value="school.site"
                        @input="updateSite">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        placeholder="E-mail"
                        rules="required"
                        :value="school.email"
                        @input="updateEmail">
            </base-input>
          </div>
        </div>


        <div class="form-row">
          <div class="col-md-1">
            <base-input label="Zip"
                        name="Zip"
                        placeholder="Zip"
                        rules="required"
                        :value="school.zip"
                        @input="updateZip">
            </base-input>
          </div>

          <div class="col-md-4">
            <base-input label="Logradouro"
                        name="Logradouro"
                        placeholder="Logradouro"
                        rules="required"
                        :value="school.street"
                        @input="updateStreet">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Número"
                        name="Número"
                        placeholder="Número"
                        rules="required"
                        :value="school.street_number"
                        @input="updateStreetNumber">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="Complemento"
                        name="Complemento"
                        placeholder="Complemento"
                        :value="school.unit"
                        @input="updateUnit">
            </base-input>
          </div>
          <div class="col-md-4">
            <base-input label="Bairro"
                        name="Bairro"
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
                        placeholder="Cidade"
                        rules="required"
                        :value="school.city"
                        @input="updateCity">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="UF"
                        name="UF"
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
        <base-button type="success" native-type="submit"><i class="fa fa-check"></i>Salvar</base-button>
        <base-button @click="back()" type="danger"><i class="fa fa-window-close"></i>Voltar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
import Swal from "sweetalert2";

export default {
  props: ["school"],
  components: {},
  data() {
    return {
      selects: {
        legal_natures: [
          {value: "J", label: "Jurídica"},
          {value: "F", label: "Física"},
        ],
        ufs: [
          {value: "AC", label: "AC"},
          {value: "AL", label: "AL"},
          {value: "AP", label: "AP"},
          {value: "AM", label: "AM"},
          {value: "BA", label: "BA"},
          {value: "CE", label: "CE"},
          {value: "DF", label: "DF"},
          {value: "ES", label: "ES"},
          {value: "GO", label: "GO"},
          {value: "MA", label: "MA"},
          {value: "MT", label: "MT"},
          {value: "MS", label: "MS"},
          {value: "MG", label: "MG"},
          {value: "PA", label: "PA"},
          {value: "PB", label: "PB"},
          {value: "PR", label: "PR"},
          {value: "PE", label: "PE"},
          {value: "PI", label: "PI"},
          {value: "RJ", label: "RJ"},
          {value: "RN", label: "RN"},
          {value: "RS", label: "RS"},
          {value: "RO", label: "RO"},
          {value: "RR", label: "RR"},
          {value: "SC", label: "SC"},
          {value: "SP", label: "SP"},
          {value: "SE", label: "SE"},
          {value: "TO", label: "TO"},
        ]
      },
      validated: false,
    };
  },
  // Quando a pagina e recarrecada, o Vuex e totalmente limpado. Por isso, se o objeto schoo estiver vazio,
  // recarregue todas as escolas. Funciona em reload da pagina
  created() {
    if (!this.school) {
      this.$store.dispatch("schools/fetchAllSchools");
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
      const payload = {
        id: this.school.id,
        name: this.school.name,
        legal_name: this.school.legal_name,
        legal_nature: this.school.legal_nature,
        cnpj: this.school.cnpj,
        phone: this.school.phone,
        site: this.school.site,
        email: this.school.email,
        zip: this.school.zip,
        street: this.school.street,
        street_number: this.school.street_number,
        unit: this.school.unit,
        neighborhood: this.school.neighborhood,
        city: this.school.city,
        state: this.school.state
      };
      try {
        this.$axios.patch(`v2/tenant/schools/${this.school.id}`, payload)
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
