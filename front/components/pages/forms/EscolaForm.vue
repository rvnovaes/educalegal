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
                          success-message="Parece correto!"
                          :value="school.legal_nature"
                          @input="updateLegalNature">
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
                        v-model="school.phone">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="Site"
                        name="Site"
                        placeholder="Site"
                        rules="required"
                        v-model="school.site">
            </base-input>
          </div>
          <div class="col-md-5">
            <base-input label="E-mail"
                        name="E-mail"
                        placeholder="E-mail"
                        rules="required"
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
                        :value="school.city"
                        @input="updateCity">
            </base-input>
          </div>
          <div class="col-md-1">
            <base-input label="UF"
                        name="UF"
                        placeholder="UF"
                        rules="required"
                        :value="school.state"
                        @input="updateUF">
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
import Swal from 'sweetalert2';

  export default {
    props: ['school'],
    components: {},
    data() {
      return {

        validated: false,
      }
    },

    // Quando a pagina e recarrecada, o Vuex e totalmente limpado. Por isso, se o objeto schoo estiver vazio,
    // recarregue todas as escolas. Funciona em reload da pagina
    created() {
      if(!this.school){
        this.$store.dispatch('schools/fetchAllSchools')
      }
    },

    methods: {
      updateName (e) {
        this.$store.commit('schools/updateName', {id: this.school.id, name: e})
      },
      updateLegalName (e) {
        this.$store.commit('schools/updateLegalName', {id: this.school.id, legal_name: e})
      },
      updateCNPJ (e) {
        this.$store.commit('schools/updateCNPJ', {id: this.school.id, cnpj: e})
      },
      updateLegalNature (e) {
        this.$store.commit('schools/updateLegalNature', {id: this.school.id, legal_nature: e})
      },
      updateCity (e) {
        this.$store.commit('schools/updateCity', {id: this.school.id, city: e})
      },
      updateUF (e) {
        this.$store.commit('schools/updateUF', {id: this.school.id, state: e})
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
          }
        try {
          this.$axios.patch(`v2/tenant/schools/${this.school.id}`, payload)
          .then((data) => {
            Swal.fire({
              title: `Você atualizou ${this.school.name} com sucesso!`,
              buttonsStyling: false,
              icon: 'success',
              customClass: {
                confirmButton: 'btn btn-success btn-fill',
              }
            });
          })
        } catch (e) {
          await Swal.fire({
            title: `Erro ao editar ${this.school.name}`,
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
          path: '/escolas'
        })
      }
    }
  }
</script>
<style>
</style>
