<template>
  <card>
    <!-- Card header -->
    <h3 slot="header" class="mb-0">Editar {{ model.name }}</h3>

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
                        v-model="model.name">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Razão Social"
                        name="Razão Social"
                        placeholder="Razão Social"
                        rules="required"
                        success-message="Parece correto!"
                        v-model="model.legalName">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="CNPJ/CPF"
                        name="CNPJ/CPF"
                        placeholder="CNPJ/CPF"
                        rules="required"
                        success-message="Parece correto!"
                        v-model="model.cnpj">
            </base-input>
          </div>
            <div class="col-md-1">
              <base-input label="Tipo"
                          name="TIpo"
                          placeholder="Tipo "
                          rules="required"
                          success-message="Parece correto!"
                          v-model="model.legalNature">
<!--                <select class="form-control">-->
<!--                  <option>J</option>-->
<!--                  <option>F</option>-->
<!--                </select>-->
              </base-input>

          </div>
        </div>
        <div class="form-row">
          <div class="col-md-2">
            <base-input label="Telefone"
                        name="Telefone"
                        placeholder="Telefone"
                        rules="required"
                        v-model="model.phone">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Site"
                        name="Site"
                        placeholder="Site"
                        rules="required"
                        v-model="model.site">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        placeholder="E-mail"
                        rules="required"
                        v-model="model.email">
            </base-input>
          </div>
        </div>


        <div class="form-row">
          <div class="col-md-1">
            <base-input label="Zip"
                        name="Zip"
                        placeholder="Zip"
                        rules="required"
                        v-model="model.zip">
            </base-input>
          </div>

          <div class="col-md-4">
            <base-input label="Logradouro"
                        name="Logradouro"
                        placeholder="Logradouro"
                        rules="required"
                        v-model="model.street">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="Número"
                        name="Número"
                        placeholder="Número"
                        rules="required"
                        v-model="model.streetNumber">
            </base-input>
          </div>
          <div class="col-md-2">
            <base-input label="Complemento"
                        name="Complemento"
                        placeholder="Complemento"
                        v-model="model.unit">
            </base-input>
          </div>
          <div class="col-md-4">
            <base-input label="Bairro"
                        name="Bairro"
                        placeholder="Bairro"
                        rules="required"
                        v-model="model.neighborhood">
            </base-input>
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-6">
            <base-input label="Cidade"
                        name="Cidade"
                        placeholder="Cidade"
                        rules="required"
                        v-model="model.city">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="UF"
                        name="UF"
                        placeholder="UF"
                        rules="required"
                        v-model="model.state">
            </base-input>
          </div>
        </div>
        <base-button type="success" native-type="submit"><i class="fa fa-check"></i>Salvar</base-button>
        <base-button @click="cancel()" type="danger"><i class="fa fa-window-close"></i>Cancelar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
// import updateSchool from '~/queries/updateSchool'
import updateSchool from '~/queries/updateSchoolSimple'

  export default {
    props: ['id', 'name', 'legalName', 'legalNature', 'cnpj', 'phone', 'site', 'email', 'zip', 'street', 'streetNumber', 'unit', 'neighborhood', 'city', 'state', 'zip'],
    components: {},
    data() {
      return {
        validated: false,
        model: {
          id: this.id,
          name: this.name,
          legalName: this.legalName,
          legalNature: this.legalNature,
          cnpj: this.cnpj,
          phone: this.phone,
          site: this.site,
          email: this.email,
          zip: this.zip,
          street: this.street,
          streetNumber: this.streetNumber,
          unit: this.unit,
          neighborhood: this.neighborhood,
          city: this.city,
          state: this.state,
        }
      }
    },
    watch: {
      id: function (newVal, oldVal){
        this.model.id = newVal
      },
      name: function (newVal, oldVal){
        this.model.name = newVal
      },
      legalName: function (newVal, oldVal){
        this.model.legalName = newVal
      },
      legalNature: function (newVal, oldVal){
        this.model.legalNature = newVal
      },
      cnpj: function (newVal, oldVal){
        this.model.cnpj = newVal
      },
      phone: function (newVal, oldVal){
        this.model.phone = newVal
      },
      site: function (newVal, oldVal){
        this.model.site = newVal
      },
      email: function (newVal, oldVal){
        this.model.email = newVal
      },
      zip: function (newVal, oldVal){
        this.model.zip = newVal
      },
      street: function (newVal, oldVal){
        this.model.street = newVal
      },
      streetNumber: function (newVal, oldVal){
        this.model.streetNumber = newVal
      },
      unit: function (newVal, oldVal){
        this.model.unit = newVal
      },
      neighborhood: function (newVal, oldVal){
        this.model.neighborhood = newVal
      },
      city: function (newVal, oldVal){
        this.model.city = newVal
      },
      state: function (newVal, oldVal){
        this.model.state = newVal
      },

    },
    methods: {
      async firstFormSubmit() {
        console.log("FORM SUBMIT");
        const id = this.model.id;
        console.log(id);
        const name = this.model.name;
        console.log(name);
        const result = await this.$apollo.mutate({
          mutation: updateSchool,
          variables: {
            id: id,
            name: name,
            // legalName: legalName,
            // legalNature: legalNature,
            // cnpj: cnpj,
            // phone: phone,
            // site: site,
            // email: email,
            // zip: zip,
            // street: street,
            // streetNumber: this.mode.streetNumber,
            // unit: unit,
            // neighborhood: neighborhood,
            // city: city,
            // state: state,
          },
        })
      },
      cancel: function () {
        this.$router.push({
          path: '/escolas/listar'
        })
      }
    }
  }
</script>
<style>
</style>
