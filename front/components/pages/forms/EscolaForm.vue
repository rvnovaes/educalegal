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
        <base-button @click="back()" type="danger"><i class="fa fa-window-close"></i>Voltar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
import updateSchool from '@/queries/updateSchool.graphql'
import Swal from 'sweetalert2';

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
        try {
          const result = await this.$apollo.mutate({
            mutation: updateSchool,
            variables: {
              id: this.model.id,
              name: this.model.name,
              legalName: this.model.legalName,
              legalNature: this.model.legalNature,
              cnpj: this.model.cnpj,
              phone: this.model.phone,
              site: this.model.site,
              email: this.model.email,
              zip: this.model.zip,
              street: this.model.street,
              streetNumber: this.model.streetNumber,
              unit: this.model.unit,
              neighborhood: this.model.neighborhood,
              city: this.model.city,
              state: this.model.state
            },
          }).then((data) => {
            Swal.fire({
              title: `Você atualizou ${this.model.name} com sucesso!`,
              buttonsStyling: false,
              icon: 'success',
              customClass: {
                confirmButton: 'btn btn-success btn-fill',
              }
            });
          })
        } catch (e) {
          await Swal.fire({
            title: `Erro ao editar ${this.model.name}`,
            text: e,
            icon: 'error',
            customClass: {
              confirmButton: 'btn btn-info btn-fill',
            },
            confirmButtonText: 'OK',
            buttonsStyling: false
          });
        }
      },
      back: function () {
        this.$router.push({
          path: '/escolas/listar'
        })
      }
    }
  }
</script>
<style>
</style>
