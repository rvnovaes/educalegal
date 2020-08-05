<template>
  <card>
    <!-- Card header -->
    <h3 slot="header" class="mb-0">Custom styles</h3>

    <!-- Card body -->
    <div class="row">
      <div class="col-lg-8">
        <p class="mb-0">
          Para uma mensagem bacanosa
          For custom form validation messages, you’ll need to provide error messages to your
          <code>&lt;base-input&gt;</code> components. This disables the browser default feedback tooltips, but still
          provides access to the form
          validation APIs in JavaScript.
          <br/><br/>
          When attempting to submit, you’ll see the<code>.is-valid</code> and <code>.is-invalid</code> classes applied
          to your form controls.
        </p>
      </div>
    </div>
    <hr>
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

          <div class="col-md-8">
            <base-input label="Razão Social"
                        name="Razão Social"
                        placeholder="Razão Social"
                        rules="required"
                        success-message="Parece correto!"
                        v-model="model.legalName">
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
          <div class="col-md-3">
            <base-input label="Zip"
                        name="Zip"
                        placeholder="Zip"
                        rules="required"
                        v-model="model.zip">
            </base-input>
          </div>
        </div>
        <base-button type="primary" native-type="submit">Gravar</base-button>
      </form>
    </validation-observer>
  </card>
</template>
<script>
  export default {
    props: ['name', 'legalName', 'city', 'state', 'zip'],
    components: {},
    data() {
      return {
        validated: false,
        model: {
          name: this.name,
          legalName: this.legalName,
          city: this.city,
          state: this.state,
          zip: this.zip,
        }
      }
    },
    methods: {
      async firstFormSubmit() {
        // Form submit here
      },
    }
  }
</script>
<style>
</style>
