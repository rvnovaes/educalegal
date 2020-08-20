<template>
  <card v-if="school">
    <!-- Card header -->
    <h3 slot="header" class="mb-0">Criar {{ school.name }}</h3>

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
                        v-model="school.name">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Razão Social"
                        name="Razão Social"
                        placeholder="Razão Social"
                        rules="required"
                        success-message="Parece correto!"
                        v-model="school.legal_name">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CNPJ/CPF"
                        name="CNPJ/CPF"
                        placeholder="CNPJ/CPF"
                        rules="required"
                        success-message="Parece correto!"
                        v-model="school.cnpj">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Tipo"
                        name="Tipo"
                        placeholder="Tipo "
                        rules="required"
                        success-message="Parece correto!">
                <el-select class="select-danger"
                         placeholder="Tipo"
                         v-model="school.legal_nature">
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
                        v-model="school.phone">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Site"
                        name="Site"
                        placeholder="Site"
                        rules="required"
                        type="url"
                        v-model="school.site">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        placeholder="E-mail"
                        rules="required"
                        type="email"
                        v-model="school.email">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-1">
            <base-input label="Zip"
                        name="Zip"
                        placeholder="Zip"
                        rules="required"
                        v-model="school.zip">
            </base-input>
          </div>

          <div class="col-md-4">
            <base-input label="Logradouro"
                        name="Logradouro"
                        placeholder="Logradouro"
                        rules="required"
                        v-model="school.street">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Número"
                        name="Número"
                        placeholder="Número"
                        rules="required"
                        v-model="school.street_number">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="Complemento"
                        name="Complemento"
                        placeholder="Complemento"
                        v-model="school.unit">
            </base-input>
          </div>
          <div class="col-md-4">
            <base-input label="Bairro"
                        name="Bairro"
                        placeholder="Bairro"
                        rules="required"
                        v-model="school.neighborhood">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-6">
            <base-input label="Cidade"
                        name="Cidade"
                        placeholder="Cidade"
                        rules="required"
                        v-model="school.city">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="UF"
                        name="UF"
                        placeholder="UF"
                        rules="required">
              <el-select class="select-danger"
                         placeholder="UF"
                         v-model="school.state">
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
      school: {
        name: null,
        legal_name: null,
        legal_nature: null,
        cnpj: null,
        phone: null,
        site: null,
        email: null,
        zip: null,
        street: null,
        street_number: null,
        unit: null,
        neighborhood: null,
        city: null,
        state: null,
        school_units: []
      }
    };
  },
  methods: {
    async firstFormSubmit() {
      const payload = {
        tenant: this.$auth.user.tenant,
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
        state: this.school.state,
        school_units: []
      };
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
